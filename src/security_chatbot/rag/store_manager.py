"""Google Gemini File Search Store management module

Provides FileSearchStoreManager class to handle File Search Store operations
including create, retrieve, list, and delete.
"""

import logging

from google import genai
from google.api_core.exceptions import (
    AlreadyExists,
    GoogleAPIError,
    InvalidArgument,
    NotFound,
    PermissionDenied,
)
from google.genai import types

from security_chatbot.config import DEFAULT_STORE_DISPLAY_NAME
from security_chatbot.utils.api_client import GeminiClientManager

logger = logging.getLogger(__name__)


class FileSearchStoreManager:
    """Google Gemini File Search Store의 생성, 조회, 목록 조회, 삭제를 관리하는 클래스입니다.
    """

    def __init__(self, client: genai.Client | None = None):
        """FileSearchStoreManager의 생성자입니다.

        Args:
            client (Optional[genai.Client]): 초기화된 Gemini API 클라이언트.
                                             제공되지 않으면 GeminiClientManager를 통해 새로 가져옵니다.

        """
        self.client = client if client else GeminiClientManager.get_client()
        if not self.client:
            raise ValueError("Gemini API 클라이언트를 초기화할 수 없습니다.")
        logger.info("FileSearchStoreManager가 초기화되었습니다.")

    def create_store(
        self, display_name: str = DEFAULT_STORE_DISPLAY_NAME
    ) -> types.FileSearchStore | None:
        """새로운 File Search Store를 생성합니다.

        Args:
            display_name (str): 생성할 스토어의 표시 이름.

        Returns:
            Optional[types.FileSearchStore]: 생성된 File Search Store 객체 또는 생성 실패 시 None.

        """
        logger.info(f"File Search Store 생성 시도: display_name='{display_name}'")
        try:
            store = self.client.file_search_stores.create(
                config={"display_name": display_name}
            )
            logger.info(
                f"File Search Store 생성 성공: name='{store.name}', display_name='{display_name}'"
            )
            return store
        except AlreadyExists:
            logger.warning(
                f"File Search Store 생성 실패: '{display_name}' 이름의 스토어가 이미 존재합니다."
            )
            return None
        except (InvalidArgument, PermissionDenied, GoogleAPIError) as e:
            logger.error(
                f"File Search Store 생성 중 API 오류 발생 (display_name='{display_name}'): {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"File Search Store 생성 중 알 수 없는 오류 발생 (display_name='{display_name}'): {e}"
            )
            return None

    def get_store(self, store_name: str) -> types.FileSearchStore | None:
        """지정된 이름의 File Search Store를 조회합니다.

        Args:
            store_name (str): 조회할 File Search Store의 전체 리소스 이름 (예: "fileSearchStores/store-id").

        Returns:
            Optional[types.FileSearchStore]: 조회된 File Search Store 객체 또는 찾을 수 없거나 실패 시 None.

        """
        logger.info(f"File Search Store 조회 시도: name='{store_name}'")
        try:
            store = self.client.file_search_stores.get(name=store_name)
            logger.info(
                f"File Search Store 조회 성공: name='{store.name}', display_name='{store.display_name}'"
            )
            return store
        except NotFound:
            logger.warning(
                f"File Search Store 조회 실패: '{store_name}'을(를) 찾을 수 없습니다."
            )
            return None
        except (InvalidArgument, PermissionDenied, GoogleAPIError) as e:
            logger.error(
                f"File Search Store 조회 중 API 오류 발생 (name='{store_name}'): {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"File Search Store 조회 중 알 수 없는 오류 발생 (name='{store_name}'): {e}"
            )
            return None

    def list_stores(self) -> list[types.FileSearchStore]:
        """모든 File Search Store 목록을 조회합니다.

        Returns:
            List[types.FileSearchStore]: File Search Store 객체 목록. 오류 발생 시 빈 리스트 반환.

        """
        logger.info("File Search Store 목록 조회 시도.")
        try:
            stores = list(self.client.file_search_stores.list())
            logger.info(
                f"File Search Store 목록 조회 성공. 총 {len(stores)}개의 스토어 발견."
            )
            return stores
        except (PermissionDenied, GoogleAPIError) as e:
            logger.error(f"File Search Store 목록 조회 중 API 오류 발생: {e}")
            return []
        except Exception as e:
            logger.error(f"File Search Store 목록 조회 중 알 수 없는 오류 발생: {e}")
            return []

    def delete_store(self, store_name: str) -> bool:
        """지정된 이름의 File Search Store를 삭제합니다.

        Args:
            store_name (str): 삭제할 File Search Store의 전체 리소스 이름 (예: "fileSearchStores/store-id").

        Returns:
            bool: 삭제 성공 시 True, 실패 시 False.

        """
        logger.info(f"File Search Store 삭제 시도: name='{store_name}'")
        try:
            self.client.file_search_stores.delete(name=store_name)
            logger.info(f"File Search Store 삭제 성공: name='{store_name}'")
            return True
        except NotFound:
            logger.warning(
                f"File Search Store 삭제 실패: '{store_name}'을(를) 찾을 수 없습니다."
            )
            return False
        except (InvalidArgument, PermissionDenied, GoogleAPIError) as e:
            logger.error(
                f"File Search Store 삭제 중 API 오류 발생 (name='{store_name}'): {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"File Search Store 삭제 중 알 수 없는 오류 발생 (name='{store_name}'): {e}"
            )
            return False

    def delete_corpus_file(self, corpus_file_resource_name: str) -> bool:
        """지정된 File Search Store에서 개별 코퍼스 파일(corpus file)을 삭제합니다.

        Args:
            corpus_file_resource_name (str): 삭제할 코퍼스 파일의 전체 리소스 이름
                                              (예: "fileSearchStores/store-id/corpusFiles/file-id")

        Returns:
            bool: 삭제 성공 시 True, 실패 시 False.

        """
        logger.info(
            f"코퍼스 파일 삭제 시도: corpus_file_resource_name='{corpus_file_resource_name}'"
        )
        try:
            self.client.file_search_stores.delete_corpus_file(
                name=corpus_file_resource_name
            )
            logger.info(
                f"코퍼스 파일 삭제 성공: corpus_file_resource_name='{corpus_file_resource_name}'"
            )
            return True
        except NotFound:
            logger.warning(
                f"코퍼스 파일 삭제 실패: '{corpus_file_resource_name}'을(를) 찾을 수 없습니다. 이미 삭제되었거나 존재하지 않습니다."
            )
            return False
        except PermissionDenied:
            logger.error(
                f"코퍼스 파일 삭제 실패: '{corpus_file_resource_name}'에 대한 권한이 없습니다."
            )
            return False
        except (InvalidArgument, GoogleAPIError) as e:
            logger.error(
                f"코퍼스 파일 삭제 중 API 오류 발생 (corpus_file_resource_name='{corpus_file_resource_name}'): {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"코퍼스 파일 삭제 중 알 수 없는 오류 발생 (corpus_file_resource_name='{corpus_file_resource_name}'): {e}"
            )
            return False
