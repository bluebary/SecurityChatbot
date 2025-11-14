"""document_manager.py 모듈 테스트
"""

import logging
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from google import genai
from google.api_core.exceptions import (
    GoogleAPIError,
    InvalidArgument,
    NotFound,
    ServiceUnavailable,
)
from google.genai import types

from security_chatbot.rag.document_manager import (
    MAX_FILE_SIZE_BYTES,
    DocumentManager,
)

logging.disable(logging.CRITICAL)


class TestDocumentManager(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock(spec=genai.Client)
        self.mock_files = MagicMock()
        self.mock_file_search_stores = MagicMock()
        self.mock_operations = MagicMock()

        self.mock_client.files = self.mock_files
        self.mock_client.file_search_stores = self.mock_file_search_stores
        self.mock_client.operations = self.mock_operations

        patcher = patch(
            "security_chatbot.utils.api_client.GeminiClientManager.get_client",
            return_value=self.mock_client,
        )
        self.addCleanup(patcher.stop)
        patcher.start()

        self.store_name = "fileSearchStores/test-store-123"
        self.manager = DocumentManager(store_name=self.store_name)

        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: self._cleanup_temp_dir())

    def _cleanup_temp_dir(self):
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_temp_file(self, filename: str, size: int = 1024) -> str:
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, "wb") as f:
            f.write(b"X" * size)
        return file_path

    def test_init_success(self):
        self.assertEqual(self.manager.store_name, self.store_name)
        self.assertEqual(self.manager.max_tokens_per_chunk, 200)
        self.assertEqual(self.manager.overlap_tokens, 20)

    def test_init_with_custom_chunking(self):
        manager = DocumentManager(
            store_name=self.store_name, max_tokens_per_chunk=500, overlap_tokens=50
        )
        self.assertEqual(manager.max_tokens_per_chunk, 500)
        self.assertEqual(manager.overlap_tokens, 50)

    def test_init_with_excessive_chunk_size(self):
        manager = DocumentManager(store_name=self.store_name, max_tokens_per_chunk=3000)
        self.assertEqual(manager.max_tokens_per_chunk, 2043)

    def test_init_empty_store_name(self):
        with self.assertRaises(ValueError):
            DocumentManager(store_name="")

    def test_validate_file_success_pdf(self):
        file_path = self._create_temp_file("test.pdf", 1024)
        result = self.manager.validate_file(file_path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["file_size"], 1024)
        self.assertEqual(result["mime_type"], "application/pdf")
        self.assertEqual(result["file_name"], "test.pdf")

    def test_validate_file_success_txt(self):
        file_path = self._create_temp_file("test.txt", 2048)
        result = self.manager.validate_file(file_path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["mime_type"], "text/plain")

    def test_validate_file_not_exists(self):
        with self.assertRaises(ValueError) as ctx:
            self.manager.validate_file("/non/existent/file.pdf")
        self.assertIn("찾을 수 없습니다", str(ctx.exception))

    def test_validate_file_size_exceeded(self):
        file_path = self._create_temp_file("large.pdf", MAX_FILE_SIZE_BYTES + 1)
        with self.assertRaises(ValueError) as ctx:
            self.manager.validate_file(file_path)
        self.assertIn("크기가 제한을 초과", str(ctx.exception))

    def test_validate_file_unsupported_format(self):
        file_path = self._create_temp_file("test.exe", 1024)
        with self.assertRaises(ValueError) as ctx:
            self.manager.validate_file(file_path)
        self.assertIn("지원되지 않는 파일 형식", str(ctx.exception))

    def test_upload_file_success(self):
        file_path = self._create_temp_file("test.pdf", 1024)
        mock_uploaded_file = types.File(
            name="files/test-file-123", display_name="test.pdf"
        )
        mock_corpus_file = MagicMock(name="corpus_files/test-corpus-123")
        mock_corpus_file.name = "corpus_files/test-corpus-123"
        self.mock_files.upload.return_value = mock_uploaded_file
        self.mock_file_search_stores.create_corpus_file.return_value = mock_corpus_file
        result = self.manager.upload_file(file_path)
        self.assertIsNotNone(result)
        self.assertIn("file", result)
        self.assertEqual(result["file"].name, "files/test-file-123")

    def test_upload_file_validation_error(self):
        with self.assertRaises(ValueError):
            self.manager.upload_file("/non/existent/file.pdf")

    def test_upload_file_api_error(self):
        file_path = self._create_temp_file("test.pdf", 1024)
        self.mock_files.upload.side_effect = InvalidArgument("Invalid file")
        with self.assertRaises(GoogleAPIError):
            self.manager.upload_file(file_path)

    def test_upload_files_batch_success(self):
        file1 = self._create_temp_file("test1.pdf", 1024)
        file2 = self._create_temp_file("test2.txt", 2048)
        mock_uploaded_file = types.File(name="files/test-file", display_name="test")
        self.mock_files.upload.return_value = mock_uploaded_file
        self.mock_file_search_stores.create_corpus_file.return_value = MagicMock()
        results = self.manager.upload_files_batch([file1, file2])
        self.assertEqual(results["total"], 2)
        self.assertEqual(len(results["success"]), 2)
        self.assertEqual(len(results["failed"]), 0)

    def test_upload_files_batch_partial_failure(self):
        file1 = self._create_temp_file("test1.pdf", 1024)
        file2 = self._create_temp_file("test2.txt", 2048)
        mock_uploaded_file = types.File(name="files/test-file", display_name="test")

        def upload_side_effect(*args, **kwargs):
            if self.mock_files.upload.call_count == 1:
                return mock_uploaded_file
            else:
                raise InvalidArgument("Upload failed")

        self.mock_files.upload.side_effect = upload_side_effect
        self.mock_file_search_stores.create_corpus_file.return_value = MagicMock()
        results = self.manager.upload_files_batch([file1, file2])
        self.assertEqual(results["total"], 2)
        self.assertEqual(len(results["success"]), 1)
        self.assertEqual(len(results["failed"]), 1)

    def test_retry_with_backoff_success_first_try(self):
        mock_func = MagicMock(return_value="success")
        result = self.manager._retry_with_backoff(mock_func, "arg1", kwarg1="value1")
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 1)

    @patch("time.sleep")
    def test_retry_with_backoff_success_after_retry(self, mock_sleep):
        mock_func = MagicMock()
        mock_func.side_effect = [ServiceUnavailable("Service unavailable"), "success"]
        result = self.manager._retry_with_backoff(mock_func)
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)

    @patch("time.sleep")
    def test_retry_with_backoff_max_retries_exceeded(self, mock_sleep):
        mock_func = MagicMock()
        mock_func.side_effect = ServiceUnavailable("Service unavailable")
        with self.assertRaises(ServiceUnavailable):
            self.manager._retry_with_backoff(mock_func)
        self.assertEqual(mock_func.call_count, 3)

    def test_retry_with_backoff_non_retryable_error(self):
        mock_func = MagicMock()
        mock_func.side_effect = InvalidArgument("Invalid argument")
        with self.assertRaises(InvalidArgument):
            self.manager._retry_with_backoff(mock_func)
        self.assertEqual(mock_func.call_count, 1)

    def test_wait_for_indexing_success(self):
        operation_name = "operations/test-operation-123"
        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.error = None
        self.mock_operations.get.return_value = mock_operation
        result = self.manager.wait_for_indexing(
            operation_name, timeout=10, poll_interval=1
        )
        self.assertTrue(result)

    @patch("time.sleep")
    def test_wait_for_indexing_timeout(self, mock_sleep):
        operation_name = "operations/test-operation-123"
        mock_operation = MagicMock()
        mock_operation.done = False
        self.mock_operations.get.return_value = mock_operation
        result = self.manager.wait_for_indexing(
            operation_name, timeout=5, poll_interval=2
        )
        self.assertFalse(result)

    def test_wait_for_indexing_error(self):
        operation_name = "operations/test-operation-123"
        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.error = "Indexing failed"
        self.mock_operations.get.return_value = mock_operation
        result = self.manager.wait_for_indexing(operation_name)
        self.assertFalse(result)

    def test_wait_for_indexing_not_found(self):
        operation_name = "operations/non-existent"
        self.mock_operations.get.side_effect = NotFound("Operation not found")
        result = self.manager.wait_for_indexing(operation_name)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
