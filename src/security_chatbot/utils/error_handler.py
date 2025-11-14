"""
SecurityChatbot Error Handler

전역 에러 핸들러 및 재시도 로직을 제공합니다.
"""

import logging
import time
from functools import wraps
from typing import Callable, Any, Dict, Tuple, Type

from google.api_core.exceptions import (
    GoogleAPIError,
    ResourceExhausted,
    PermissionDenied,
    InvalidArgument,
    NotFound
)

# --- 1. 사용자 정의 에러 타입 정의 ---
class FileUploadError(Exception):
    """파일 업로드 중 발생한 오류를 위한 사용자 정의 예외."""
    pass


class IndexingError(Exception):
    """문서 인덱싱 중 발생한 오류를 위한 사용자 정의 예외."""
    pass


class QueryError(Exception):
    """RAG 쿼리 처리 중 발생한 오류를 위한 사용자 정의 예외."""
    pass


class ConfigurationError(Exception):
    """API 키 누락 등 설정 관련 오류를 위한 사용자 정의 예외."""
    pass


# --- 2. 로깅 설정 (config.py 참조) ---
# config.py에서 로깅이 설정되어 있다고 가정하고, 해당 로거를 가져옵니다.
logger = logging.getLogger(__name__)


# --- 3. 전역 에러 핸들러 클래스 구현 ---
class ErrorHandler:
    """
    전역 에러 핸들러 클래스.
    다양한 에러 타입을 처리하고 사용자 친화적인 메시지를 제공하며, 에러 로깅을 수행합니다.
    """

    # 3.1. 사용자 친화적 에러 메시지 매핑
    # 각 에러 타입별로 한국어 사용자 친화적 메시지, 심각도, 해결 방법 제공
    ERROR_MESSAGES: Dict[Type[Exception], Dict[str, str]] = {
        # Google API 관련 오류
        GoogleAPIError: {
            "message": "Google API 통신 중 알 수 없는 오류가 발생했습니다.",
            "severity": "ERROR",
            "solution": "네트워크 연결을 확인하거나, API 키가 올바른지 확인해주세요. 문제가 지속되면 관리자에게 문의하세요."
        },
        ResourceExhausted: {
            "message": "Google API 호출 한도를 초과했습니다.",
            "severity": "WARNING",
            "solution": "잠시 후 다시 시도해주세요. 반복될 경우 API 사용량 한도를 확인하거나 증액을 요청해야 할 수 있습니다."
        },
        PermissionDenied: {
            "message": "Google API 접근 권한이 없습니다.",
            "severity": "CRITICAL",
            "solution": "API 키의 권한 설정을 확인하거나, 올바른 프로젝트에 연결되었는지 확인해주세요."
        },
        InvalidArgument: {
            "message": "Google API 요청 파라미터가 잘못되었습니다.",
            "severity": "ERROR",
            "solution": "내부 로직에 문제가 있을 수 있습니다. 개발팀에 문의하여 이 문제를 보고해주세요."
        },
        NotFound: {
            "message": "요청한 Google API 리소스를 찾을 수 없습니다.",
            "severity": "ERROR",
            "solution": "대상 리소스가 존재하지 않거나, 잘못된 ID를 사용했을 수 있습니다. 개발팀에 문의해주세요."
        },
        # 파일 업로드 관련 오류
        FileUploadError: {
            "message": "파일 업로드 중 오류가 발생했습니다.",
            "severity": "ERROR",
            "solution": "파일 크기나 형식을 확인해주세요. 지원되는 파일 형식은 PDF, TXT, Markdown, HWP, HWPX입니다. 최대 파일 크기는 100MB입니다."
        },
        # 인덱싱 실패 오류
        IndexingError: {
            "message": "문서 인덱싱 중 오류가 발생했습니다.",
            "severity": "ERROR",
            "solution": "업로드된 문서의 내용에 문제가 있거나, 인덱싱 시스템에 일시적인 오류가 발생했을 수 있습니다. 잠시 후 다시 시도해주세요."
        },
        # 쿼리 실패 오류
        QueryError: {
            "message": "질의 처리 중 오류가 발생했습니다.",
            "severity": "ERROR",
            "solution": "질의 내용을 다시 확인하거나, 시스템에 일시적인 오류가 발생했을 수 있습니다. 잠시 후 다시 시도해주세요."
        },
        # 설정 관련 오류
        ConfigurationError: {
            "message": "애플리케이션 설정 오류가 발생했습니다.",
            "severity": "CRITICAL",
            "solution": "API 키 또는 환경 변수 설정이 올바른지 확인해주세요. .env 파일에 GEMINI_API_KEY가 설정되어 있는지 확인하세요."
        },
        # 기타 예상치 못한 오류 (Catch-all)
        Exception: {
            "message": "예상치 못한 오류가 발생했습니다.",
            "severity": "CRITICAL",
            "solution": "서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도하거나 관리자에게 문의해주세요."
        }
    }

    def __init__(self):
        """
        ErrorHandler 클래스를 초기화합니다.
        현재는 인스턴스별 상태가 필요하지 않아 특별한 초기화 로직이 없습니다.
        """
        pass

    def get_user_friendly_message(self, exception: Exception) -> Dict[str, str]:
        """
        주어진 예외 객체에 대한 사용자 친화적인 메시지, 심각도, 해결 방법을 반환합니다.
        예외의 MRO(Method Resolution Order)를 따라 가장 구체적인 매핑을 찾습니다.

        Args:
            exception: 발생한 예외 객체.

        Returns:
            사용자 친화적인 메시지, 심각도, 해결 방법을 담은 딕셔너리.
        """
        for exc_type in type(exception).__mro__:
            if exc_type in self.ERROR_MESSAGES:
                return self.ERROR_MESSAGES[exc_type]
        # 매핑된 예외가 없는 경우, 일반 Exception 메시지를 반환합니다.
        return self.ERROR_MESSAGES[Exception]

    def log_error(self, exception: Exception, context: str, severity: str = "ERROR") -> None:
        """
        에러를 로깅 시스템에 기록합니다.
        스택 트레이스와 컨텍스트 정보를 포함합니다.

        Args:
            exception: 발생한 예외 객체.
            context: 에러가 발생한 컨텍스트 (예: "파일 업로드", "API 호출").
            severity: 에러의 심각도 (CRITICAL, ERROR, WARNING, INFO).
        """
        log_message = f"Context: {context} | Exception Type: {type(exception).__name__} | Message: {exception}"
        if severity == "CRITICAL":
            logger.critical(log_message, exc_info=True)
        elif severity == "ERROR":
            logger.error(log_message, exc_info=True)
        elif severity == "WARNING":
            logger.warning(log_message, exc_info=True)
        elif severity == "INFO":
            logger.info(log_message, exc_info=False)  # INFO 레벨은 일반적으로 스택 트레이스를 포함하지 않습니다.
        else:
            logger.error(f"Unknown severity level '{severity}'. Logging as ERROR. {log_message}", exc_info=True)

    def handle_error(self, exception: Exception, context: str) -> Dict[str, str]:
        """
        예외를 처리하고 사용자에게 표시할 메시지를 반환하며, 에러를 로깅합니다.

        Args:
            exception: 발생한 예외 객체.
            context: 에러가 발생한 컨텍스트 (예: "파일 업로드", "API 호출").

        Returns:
            사용자에게 표시할 메시지, 심각도, 해결 방법을 담은 딕셔너리.
            이 딕셔너리는 Streamlit의 st.error, st.warning 등에 활용될 수 있습니다.
        """
        error_info = self.get_user_friendly_message(exception)
        severity = error_info["severity"]

        self.log_error(exception, context, severity)

        return error_info

    def retry_with_backoff(
        self,
        func: Callable[..., Any],
        max_retries: int = 3,
        retry_exceptions: Tuple[Type[Exception], ...] = (ResourceExhausted, GoogleAPIError),
        on_retry_callback: Callable[[int, float, Exception], None] = None
    ) -> Callable[..., Any]:
        """
        Exponential backoff을 사용하여 함수 실행을 재시도하는 데코레이터입니다.
        주로 API Rate Limit 또는 일시적인 네트워크 오류 처리에 사용됩니다.

        Args:
            func: 재시도할 함수.
            max_retries: 최대 재시도 횟수 (기본값: 3회).
            retry_exceptions: 재시도할 예외 타입 튜플 (기본값: ResourceExhausted, GoogleAPIError).
            on_retry_callback: 재시도 시 호출될 콜백 함수.
                                (현재 재시도 횟수, 대기 시간, 발생한 예외)를 인자로 받습니다.
                                Streamlit 메시지 표시 등에 활용될 수 있습니다.

        Returns:
            데코레이터가 적용된 함수.
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    if attempt == max_retries:
                        # 모든 재시도 실패 시 마지막 예외를 다시 발생시킵니다.
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_retries} attempts due to {type(e).__name__}.",
                            exc_info=True
                        )
                        raise

                    wait_time = 2 ** (attempt - 1)  # 1, 2, 4 초
                    logger.warning(
                        f"Attempt {attempt}/{max_retries} for '{func.__name__}' failed: {type(e).__name__}. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    if on_retry_callback:
                        on_retry_callback(attempt, wait_time, e)

                    time.sleep(wait_time)
                except Exception as e:
                    # 재시도 가능한 예외가 아닌 경우 즉시 로깅하고 다시 발생시킵니다.
                    logger.error(
                        f"Function '{func.__name__}' encountered a non-retryable error: {type(e).__name__}.",
                        exc_info=True
                    )
                    raise
            # 이 부분은 모든 재시도가 실패하고 예외가 다시 발생하면 도달하지 않아야 합니다.
            # 하지만 코드의 견고성을 위해 추가합니다.
            raise RuntimeError(f"Function '{func.__name__}' failed unexpectedly after all retries.")

        return wrapper


# 전역적으로 사용할 ErrorHandler 인스턴스를 생성합니다.
error_handler = ErrorHandler()
