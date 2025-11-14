"""api_client.py 모듈 테스트
"""

import logging
import unittest
from unittest.mock import MagicMock, patch

logging.disable(logging.CRITICAL)

API_CLIENT_MODULE = "security_chatbot.utils.api_client"

from security_chatbot.utils.api_client import GeminiClientManager


class TestGeminiClientManager(unittest.TestCase):
    """GeminiClientManager 클래스 테스트"""

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    def setUp(self):
        GeminiClientManager._client = None

    def tearDown(self):
        GeminiClientManager._client = None

    @patch(f"{API_CLIENT_MODULE}.GEMINI_API_KEY", "fake_api_key")
    @patch(f"{API_CLIENT_MODULE}.genai")
    def test_get_client_success(self, mock_genai):
        """API 키가 있을 때 클라이언트 초기화 테스트"""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        client = GeminiClientManager.get_client()

        mock_genai.Client.assert_called_once_with(api_key="fake_api_key")
        self.assertEqual(client, mock_client)

    @patch(f"{API_CLIENT_MODULE}.GEMINI_API_KEY", "")
    def test_get_client_no_api_key(self):
        """API 키가 없을 때 ValueError 발생 테스트"""
        with self.assertRaises(ValueError):
            GeminiClientManager.get_client()

    @patch(f"{API_CLIENT_MODULE}.GeminiClientManager.get_client")
    def test_verify_connection_success(self, mock_get_client):
        """연결 성공 테스트"""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.file_search_stores.list.return_value = []

        result = GeminiClientManager.verify_connection()

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
