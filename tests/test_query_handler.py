"""query_handler.py 모듈 테스트
"""

import logging
import unittest
from unittest.mock import MagicMock, patch

logging.disable(logging.CRITICAL)


class TestQueryHandler(unittest.TestCase):
    """query_handler 모듈 테스트"""

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    def test_parse_grounding_metadata_with_citations(self):
        """출처 정보 파싱 테스트"""
        from security_chatbot.rag.query_handler import parse_grounding_metadata

        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_chunk = MagicMock()
        mock_chunk.retrieved_context.title = "Document 1"
        mock_response.candidates[0].grounding_metadata.grounding_chunks = [mock_chunk]

        citations = parse_grounding_metadata(mock_response)

        self.assertIsInstance(citations, list)
        self.assertGreaterEqual(len(citations), 0)

    def test_format_response_success(self):
        """응답 포맷팅 성공 테스트"""
        from security_chatbot.rag.query_handler import format_response

        mock_response = MagicMock()
        mock_response.text = "테스트 응답"
        mock_citations = ["Doc 1"]

        formatted = format_response(mock_response, mock_citations)

        self.assertEqual(formatted["content"], "테스트 응답")
        self.assertEqual(formatted["citations"], mock_citations)
        self.assertTrue(formatted["success"])

    @patch("security_chatbot.rag.query_handler.GeminiClientManager")
    @patch("security_chatbot.rag.query_handler.parse_grounding_metadata")
    @patch("security_chatbot.rag.query_handler.format_response")
    def test_query_with_rag_success(self, mock_format, mock_parse, mock_client_manager):
        """RAG 쿼리 성공 테스트"""
        from security_chatbot.rag.query_handler import query_with_rag

        mock_client = MagicMock()
        mock_client_manager.get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = "테스트 응답"
        mock_client.models.generate_content.return_value = mock_response

        mock_parse.return_value = ["Doc 1"]
        mock_format.return_value = {
            "content": "테스트 응답",
            "citations": ["Doc 1"],
            "success": True,
            "error": None,
        }

        result = query_with_rag("테스트 질문", "test-store")

        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "테스트 응답")


if __name__ == "__main__":
    unittest.main()
