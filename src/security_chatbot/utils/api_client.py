"""
Gemini API client initialization and connection validation module
"""

import os
import logging
from typing import Optional

from google import genai
from google.api_core.exceptions import GoogleAPIError

from security_chatbot.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


class GeminiClientManager:
    """
    Google Gemini API 클라이언트를 초기화하고 관리하는 클래스입니다.
    API 키를 사용하여 클라이언트를 생성하고, 연결 상태를 검증합니다.
    """
    _client: Optional[genai.Client] = None

    @classmethod
    def get_client(cls) -> genai.Client:
        """
        Gemini API 클라이언트 인스턴스를 반환합니다.
        클라이언트가 아직 초기화되지 않았다면, GEMINI_API_KEY를 사용하여 초기화합니다.

        Returns:
            genai.Client: 초기화된 Gemini API 클라이언트 인스턴스.

        Raises:
            ValueError: GEMINI_API_KEY가 설정되지 않았을 경우 발생합니다.
            GoogleAPIError: 클라이언트 초기화 중 오류가 발생했을 경우 발생합니다.
        """
        if cls._client is None:
            if not GEMINI_API_KEY:
                logger.error("GEMINI_API_KEY가 설정되지 않아 Gemini API 클라이언트를 초기화할 수 없습니다.")
                raise ValueError("GEMINI_API_KEY 환경 변수를 설정해야 합니다.")
            try:
                cls._client = genai.Client(api_key=GEMINI_API_KEY)
                logger.info("Gemini API 클라이언트가 성공적으로 초기화되었습니다.")
            except GoogleAPIError as e:
                logger.error(f"Gemini API 인증 오류: {e}")
                raise GoogleAPIError(f"API 키 인증에 실패했습니다: {e}") from e
            except Exception as e:
                logger.error(f"Gemini API 클라이언트 초기화 중 알 수 없는 오류 발생: {e}")
                raise Exception(f"클라이언트 초기화 실패: {e}") from e
        return cls._client

    @classmethod
    def verify_connection(cls) -> bool:
        """
        Gemini API 클라이언트의 연결 상태를 검증합니다.
        실제 API 호출을 통해 연결 유효성을 확인합니다.

        Returns:
            bool: 연결이 유효하면 True, 그렇지 않으면 False.
        """
        try:
            client = cls.get_client()
            # 가벼운 API 호출을 통해 연결 검증
            # File Search Store 목록 조회로 연결 확인
            _ = list(client.file_search_stores.list())
            logger.info("Gemini API 연결이 성공적으로 검증되었습니다.")
            return True
        except (ValueError, GoogleAPIError) as e:
            logger.error(f"Gemini API 연결 검증 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"알 수 없는 오류로 Gemini API 연결 검증 실패: {e}")
            return False
