"""RAG 파이프라인 통합 테스트
"""

import logging
import unittest
from unittest.mock import MagicMock, patch

import pytest

logging.disable(logging.CRITICAL)


@pytest.mark.integration
class TestRAGIntegration(unittest.TestCase):
    """RAG 파이프라인 통합 테스트"""

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    def setUp(self):
        self.test_store_name = "fileSearchStores/test-store-123"

    @patch("security_chatbot.rag.query_handler.GeminiClientManager")
    @patch("security_chatbot.rag.store_manager.GeminiClientManager")
    def test_full_rag_pipeline(self, mock_store_client, mock_query_client):
        """전체 RAG 파이프라인 테스트"""
        from security_chatbot.rag.query_handler import query_with_rag
        from security_chatbot.rag.store_manager import FileSearchStoreManager

        # Store 생성
        mock_client = MagicMock()
        mock_store_client.get_client.return_value = mock_client

        mock_store = MagicMock()
        mock_store.name = self.test_store_name
        mock_client.file_search_stores.create.return_value = mock_store

        store_manager = FileSearchStoreManager()
        created_store = store_manager.create_store(display_name="Test Store")

        self.assertIsNotNone(created_store)

        # RAG 쿼리
        mock_query_client.get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = "테스트 응답"
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].grounding_metadata.grounding_chunks = []
        mock_client.models.generate_content.return_value = mock_response

        result = query_with_rag("테스트 질문", self.test_store_name)

        self.assertTrue(result["success"])

        # Store 삭제
        mock_client.file_search_stores.delete.return_value = None
        delete_result = store_manager.delete_store(self.test_store_name)

        self.assertTrue(delete_result)


if __name__ == "__main__":
    unittest.main()
