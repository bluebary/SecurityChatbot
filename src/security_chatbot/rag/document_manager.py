"""Document upload and indexing management module for Google Gemini File Search API

Handles file validation, upload to File Search Store, batch operations,
and indexing management with chunking configuration.
"""

import logging
import time
from pathlib import Path
from typing import Any

from google import genai
from google.api_core.exceptions import (
    GoogleAPIError,
    InternalServerError,
    InvalidArgument,
    NotFound,
    PermissionDenied,
    ResourceExhausted,
    ServiceUnavailable,
)

from security_chatbot.utils.api_client import GeminiClientManager

logger = logging.getLogger(__name__)

# 파일 형식 지원
SUPPORTED_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".hwp": "application/x-hwp",
    ".hwpx": "application/x-hwp-v5",
}

# 파일 크기 제한 (100MB)
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024

# 재시도 설정
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0
MAX_RETRY_DELAY = 32.0

# 청킹 설정 기본값
DEFAULT_MAX_TOKENS_PER_CHUNK = 200
DEFAULT_OVERLAP_TOKENS = 20


class DocumentManager:
    """Google Gemini File Search Store에 문서를 업로드하고 관리하는 클래스

    파일 유효성 검증, 단일/배치 업로드, 청킹 설정, 재시도 로직을 제공합니다.
    """

    def __init__(
        self,
        store_name: str,
        client: genai.Client | None = None,
        max_tokens_per_chunk: int = DEFAULT_MAX_TOKENS_PER_CHUNK,
        overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
    ):
        """DocumentManager 초기화

        Args:
            store_name: File Search Store의 전체 리소스 이름
            client: 초기화된 Gemini API 클라이언트. None이면 새로 생성
            max_tokens_per_chunk: 청크당 최대 토큰 수 (기본값: 200, 최대: 2043)
            overlap_tokens: 청크 간 오버랩 토큰 수 (기본값: 20)

        Raises:
            ValueError: client를 초기화할 수 없거나 store_name이 비어있는 경우

        """
        if not store_name:
            raise ValueError("store_name은 비어있을 수 없습니다.")

        self.store_name = store_name
        self.client = client if client else GeminiClientManager.get_client()

        if not self.client:
            raise ValueError("Gemini API 클라이언트를 초기화할 수 없습니다.")

        if max_tokens_per_chunk > 2043:
            logger.warning(
                f"max_tokens_per_chunk({max_tokens_per_chunk})가 최대값(2043)을 초과하여 2043으로 조정됩니다."
            )
            max_tokens_per_chunk = 2043

        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.overlap_tokens = overlap_tokens

        logger.info(
            f"DocumentManager 초기화 완료: store={store_name}, "
            f"chunk_size={max_tokens_per_chunk}, overlap={overlap_tokens}"
        )

    def validate_file(self, file_path: str) -> dict[str, Any]:
        """파일 유효성 검증 (파일 형식, 크기)

        Args:
            file_path: 검증할 파일의 경로

        Returns:
            검증 결과 딕셔너리 (valid, file_size, mime_type, file_name)

        Raises:
            ValueError: 파일이 존재하지 않거나, 크기가 초과하거나, 지원되지 않는 형식인 경우

        """
        path = Path(file_path)

        if not path.exists():
            raise ValueError(f"파일을 찾을 수 없습니다: {file_path}")

        if not path.is_file():
            raise ValueError(f"올바른 파일이 아닙니다: {file_path}")

        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"파일 크기가 제한을 초과했습니다: {file_size / (1024*1024):.2f}MB > "
                f"{MAX_FILE_SIZE_BYTES / (1024*1024):.0f}MB"
            )

        file_ext = path.suffix.lower()
        mime_type = SUPPORTED_MIME_TYPES.get(file_ext)

        if not mime_type:
            supported = ", ".join(SUPPORTED_MIME_TYPES.keys())
            raise ValueError(
                f"지원되지 않는 파일 형식입니다: {file_ext}\n" f"지원 형식: {supported}"
            )

        logger.info(
            f"파일 검증 성공: {path.name} " f"({file_size / 1024:.2f}KB, {mime_type})"
        )

        return {
            "valid": True,
            "file_size": file_size,
            "mime_type": mime_type,
            "file_name": path.name,
        }

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Exponential backoff을 사용한 재시도 로직

        Args:
            func: 실행할 함수
            *args: 함수에 전달할 위치 인자
            **kwargs: 함수에 전달할 키워드 인자

        Returns:
            함수 실행 결과

        Raises:
            마지막 시도에서 발생한 예외

        """
        delay = INITIAL_RETRY_DELAY
        last_exception = None

        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except (InternalServerError, ServiceUnavailable, ResourceExhausted) as e:
                last_exception = e
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"API 호출 실패 (시도 {attempt + 1}/{MAX_RETRIES}): {e}. "
                        f"{delay:.1f}초 후 재시도..."
                    )
                    time.sleep(delay)
                    delay = min(delay * 2, MAX_RETRY_DELAY)
                else:
                    logger.error(f"최대 재시도 횟수 도달. 실패: {e}")
            except Exception as e:
                logger.error(f"재시도 불가능한 에러 발생: {e}")
                raise

        raise last_exception

    def upload_file(
        self, file_path: str, display_name: str | None = None
    ) -> dict[str, Any] | None:
        """단일 파일을 File Search Store에 업로드

        Args:
            file_path: 업로드할 파일의 경로
            display_name: 파일의 표시 이름 (기본값: 파일명)

        Returns:
            업로드된 파일 정보 딕셔너리 (file, corpus_file) 또는 실패 시 None
            - file: 업로드된 File 객체
            - corpus_file: Store에 추가된 CorpusFile 객체
            - corpus_file_name: CorpusFile의 리소스 이름 (삭제 시 사용)

        Raises:
            ValueError: 파일 유효성 검증 실패
            GoogleAPIError: API 호출 실패

        """
        validation = self.validate_file(file_path)

        file_name = validation["file_name"]
        display_name = display_name or file_name

        logger.info(f"파일 업로드 시작: {file_name} -> {self.store_name}")

        try:
            chunking_config = {
                "white_space_config": {
                    "max_tokens_per_chunk": self.max_tokens_per_chunk,
                    "max_overlap_tokens": self.overlap_tokens,
                }
            }

            def _upload():
                with open(file_path, "rb") as f:
                    return self.client.files.upload(
                        file=f,
                        config={
                            "display_name": display_name,
                            "mime_type": validation["mime_type"],
                        },
                    )

            uploaded_file = self._retry_with_backoff(_upload)

            def _add_to_store():
                return self.client.file_search_stores.import_file(
                    file_search_store_name=self.store_name,
                    file_name=uploaded_file.name,
                    config={"chunking_config": chunking_config},
                )

            corpus_file = self._retry_with_backoff(_add_to_store)

            logger.info(
                f"파일 업로드 성공: {file_name} "
                f"(file={uploaded_file.name}, corpus_file={corpus_file.name})"
            )

            return {
                "file": uploaded_file,
                "corpus_file": corpus_file,
                "corpus_file_name": corpus_file.name,
            }

        except ValueError as e:
            logger.error(f"파일 검증 실패: {e}")
            raise
        except (InvalidArgument, PermissionDenied) as e:
            logger.error(f"API 권한 또는 인자 오류: {e}")
            raise GoogleAPIError(f"파일 업로드 실패: {e}") from e
        except GoogleAPIError as e:
            logger.error(f"파일 업로드 중 API 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"파일 업로드 중 알 수 없는 오류: {e}")
            raise

    def upload_files_batch(self, file_paths: list[str]) -> dict[str, Any]:
        """여러 파일을 배치로 업로드

        Args:
            file_paths: 업로드할 파일 경로 리스트

        Returns:
            업로드 결과 딕셔너리 (success, failed, total)
            - success: 성공한 파일 정보 리스트 (각 항목은 upload_file의 반환값)

        """
        logger.info(f"배치 업로드 시작: {len(file_paths)}개 파일")

        results = {"success": [], "failed": [], "total": len(file_paths)}

        for file_path in file_paths:
            try:
                upload_result = self.upload_file(file_path)
                if upload_result:
                    results["success"].append(upload_result)
            except Exception as e:
                logger.warning(f"파일 업로드 실패: {file_path} - {e}")
                results["failed"].append({"file_path": file_path, "error": str(e)})

        logger.info(
            f"배치 업로드 완료: "
            f"성공 {len(results['success'])}/{results['total']}, "
            f"실패 {len(results['failed'])}"
        )

        return results

    def wait_for_indexing(
        self, operation_name: str, timeout: int = 300, poll_interval: int = 5
    ) -> bool:
        """Operation 폴링을 통해 인덱싱 완료 대기 (Optional)

        Args:
            operation_name: 대기할 Operation의 리소스 이름
            timeout: 최대 대기 시간 (초, 기본값: 300)
            poll_interval: 폴링 간격 (초, 기본값: 5)

        Returns:
            인덱싱 완료 시 True, 타임아웃 또는 실패 시 False

        """
        logger.info(f"인덱싱 완료 대기 시작: {operation_name}")

        elapsed = 0
        while elapsed < timeout:
            try:
                operation = self.client.operations.get(name=operation_name)

                if operation.done:
                    if operation.error:
                        logger.error(f"인덱싱 실패: {operation.error}")
                        return False
                    logger.info(f"인덱싱 완료: {operation_name}")
                    return True

                logger.debug(f"인덱싱 진행 중... (경과: {elapsed}초)")
                time.sleep(poll_interval)
                elapsed += poll_interval

            except NotFound:
                logger.warning(f"Operation을 찾을 수 없습니다: {operation_name}")
                return False
            except GoogleAPIError as e:
                logger.error(f"Operation 조회 중 API 오류: {e}")
                return False

        logger.warning(f"인덱싱 대기 타임아웃: {timeout}초 경과")
        return False
