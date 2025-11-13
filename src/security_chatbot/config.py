"""
SecurityChatbot Configuration

Load environment variables and define application-wide configuration constants.
"""

import os
import logging
from typing import Final

# 로깅 설정
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO").upper()

# 기본 로깅 설정
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Gemini API 설정
GEMINI_API_KEY: Final[str] = os.getenv("GEMINI_API_KEY", "")

# 환경 변수 검증
if not GEMINI_API_KEY:
    logging.warning("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. API 호출에 실패할 수 있습니다.")

# 기타 설정 (필요에 따라 추가)
DEFAULT_STORE_DISPLAY_NAME: Final[str] = "MyRAGFileSearchStore"
