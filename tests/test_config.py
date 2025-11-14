"""config.py 모듈 테스트
"""

import importlib
import logging
import unittest
from unittest.mock import patch

logging.disable(logging.CRITICAL)


class TestConfig(unittest.TestCase):
    """config.py 모듈 테스트"""

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    def setUp(self):
        if "security_chatbot.config" in importlib.sys.modules:
            del importlib.sys.modules["security_chatbot.config"]
        self.config = None

    def _reload_config_module(self):
        self.config = importlib.import_module("security_chatbot.config")

    @patch("os.getenv")
    def test_log_level_default(self, mock_getenv):
        """LOG_LEVEL 기본값 테스트"""
        mock_getenv.side_effect = lambda key, default: {
            "LOG_LEVEL": default,
            "GEMINI_API_KEY": "",
            "GEMINI_MODEL_NAME": "gemini-2.0-flash-exp",
            "API_TIMEOUT_SECONDS": "60",
        }.get(key, default)

        self._reload_config_module()
        self.assertEqual(self.config.LOG_LEVEL, "INFO")

    @patch("os.getenv")
    def test_gemini_api_key_present(self, mock_getenv):
        """GEMINI_API_KEY 설정 테스트"""
        mock_getenv.side_effect = lambda key, default: {
            "LOG_LEVEL": "INFO",
            "GEMINI_API_KEY": "TEST_API_KEY_123",
            "GEMINI_MODEL_NAME": "gemini-2.0-flash-exp",
            "API_TIMEOUT_SECONDS": "60",
        }.get(key, default)

        self._reload_config_module()
        self.assertEqual(self.config.GEMINI_API_KEY, "TEST_API_KEY_123")

    def test_default_store_display_name(self):
        """DEFAULT_STORE_DISPLAY_NAME 테스트"""
        self._reload_config_module()
        self.assertEqual(self.config.DEFAULT_STORE_DISPLAY_NAME, "MyRAGFileSearchStore")


if __name__ == "__main__":
    unittest.main()
