"""SecurityChatbot Configuration

Load environment variables and define application-wide configuration constants.
"""

import logging
import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

# .env 파일 로드 (프로젝트 루트 디렉토리에서)
# config.py는 src/security_chatbot/ 안에 있으므로, 루트는 2단계 위
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 로깅 설정
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO").upper()
FILE_LOGGING_ENABLED: Final[bool] = os.getenv("FILE_LOGGING_ENABLED", "true").lower() == "true"
LOG_DIR: Final[Path] = Path(__file__).parent.parent.parent / "logs"
LOG_MAX_BYTES: Final[int] = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
LOG_BACKUP_COUNT: Final[int] = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# 로그 디렉토리 생성
if FILE_LOGGING_ENABLED:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

# 개선된 로그 포맷 (파일명, 함수명, 라인 번호 포함)
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
SIMPLE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 핸들러 설정
handlers = []

# 1. 콘솔 핸들러 (항상 활성화)
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(logging.Formatter(SIMPLE_FORMAT))
handlers.append(console_handler)

# 2. 파일 핸들러 (환경 변수로 제어)
if FILE_LOGGING_ENABLED:
    from logging.handlers import RotatingFileHandler

    # 모든 로그를 기록하는 파일 핸들러
    app_log_file = LOG_DIR / "app.log"
    app_file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    app_file_handler.setLevel(logging.DEBUG)
    app_file_handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
    handlers.append(app_file_handler)

    # 에러만 기록하는 파일 핸들러
    error_log_file = LOG_DIR / "error.log"
    error_file_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
    handlers.append(error_file_handler)

# 기본 로깅 설정 적용
logging.basicConfig(
    level=logging.DEBUG,  # 루트 로거는 DEBUG로 설정하고, 핸들러에서 레벨 제어
    format=DETAILED_FORMAT,
    handlers=handlers,
)

# 루트 로거 레벨 설정
logging.getLogger().setLevel(LOG_LEVEL)

# Gemini API 설정
GEMINI_API_KEY: Final[str] = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME: Final[str] = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")
API_TIMEOUT_SECONDS: Final[int] = int(os.getenv("API_TIMEOUT_SECONDS", "60"))

# 환경 변수 검증
if not GEMINI_API_KEY:
    logging.warning(
        "GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. API 호출에 실패할 수 있습니다."
    )

# 기타 설정 (필요에 따라 추가)
DEFAULT_STORE_DISPLAY_NAME: Final[str] = "MyRAGFileSearchStore"
