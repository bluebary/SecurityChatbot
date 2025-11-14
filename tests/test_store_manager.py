"""store_manager.py 모듈 테스트
"""

import logging
import unittest
from unittest.mock import MagicMock, patch

from google import genai
from google.api_core.exceptions import (
    AlreadyExists,
    InvalidArgument,
    NotFound,
    PermissionDenied,
)
from google.genai import types

# 테스트 대상 모듈 임포트
from security_chatbot.rag.store_manager import FileSearchStoreManager

# 로깅 레벨 설정 (테스트 시 불필요한 로그 출력 방지)
logging.disable(logging.CRITICAL)


class TestFileSearchStoreManager(unittest.TestCase):

    def setUp(self):
        """각 테스트 실행 전 Mock 클라이언트 설정"""
        self.mock_client = MagicMock(spec=genai.Client)
        self.mock_file_search_stores = MagicMock()
        self.mock_client.file_search_stores = self.mock_file_search_stores

        # GeminiClientManager.get_client가 mock_client를 반환하도록 패치
        patcher = patch(
            "security_chatbot.utils.api_client.GeminiClientManager.get_client",
            return_value=self.mock_client,
        )
        self.addCleanup(patcher.stop)
        patcher.start()

        self.manager = FileSearchStoreManager()

    def test_create_store_success(self):
        """스토어 생성 성공 테스트"""
        mock_store_name = "fileSearchStores/test-store-123"
        mock_display_name = "My Test Store"
        mock_created_store = types.FileSearchStore(
            name=mock_store_name, display_name=mock_display_name
        )

        self.mock_file_search_stores.create.return_value = mock_created_store

        store = self.manager.create_store(display_name=mock_display_name)

        self.assertIsNotNone(store)
        self.assertEqual(store.name, mock_store_name)
        self.assertEqual(store.display_name, mock_display_name)
        self.mock_file_search_stores.create.assert_called_once_with(
            config={"display_name": mock_display_name}
        )

    def test_create_store_already_exists(self):
        """스토어 생성 시 이미 존재하는 경우 테스트"""
        self.mock_file_search_stores.create.side_effect = AlreadyExists(
            "Store already exists."
        )

        store = self.manager.create_store(display_name="Existing Store")

        self.assertIsNone(store)
        self.mock_file_search_stores.create.assert_called_once()

    def test_create_store_api_error(self):
        """스토어 생성 시 API 오류 발생 테스트"""
        self.mock_file_search_stores.create.side_effect = InvalidArgument(
            "Invalid display name."
        )

        store = self.manager.create_store(display_name="Invalid Name!")

        self.assertIsNone(store)
        self.mock_file_search_stores.create.assert_called_once()

    def test_get_store_success(self):
        """스토어 조회 성공 테스트"""
        mock_store_name = "fileSearchStores/test-store-123"
        mock_display_name = "My Test Store"
        mock_retrieved_store = types.FileSearchStore(
            name=mock_store_name, display_name=mock_display_name
        )

        self.mock_file_search_stores.get.return_value = mock_retrieved_store

        store = self.manager.get_store(store_name=mock_store_name)

        self.assertIsNotNone(store)
        self.assertEqual(store.name, mock_store_name)
        self.assertEqual(store.display_name, mock_display_name)
        self.mock_file_search_stores.get.assert_called_once_with(name=mock_store_name)

    def test_get_store_not_found(self):
        """스토어 조회 시 찾을 수 없는 경우 테스트"""
        self.mock_file_search_stores.get.side_effect = NotFound("Store not found.")

        store = self.manager.get_store(store_name="fileSearchStores/non-existent")

        self.assertIsNone(store)
        self.mock_file_search_stores.get.assert_called_once()

    def test_get_store_api_error(self):
        """스토어 조회 시 API 오류 발생 테스트"""
        self.mock_file_search_stores.get.side_effect = PermissionDenied(
            "Permission denied."
        )

        store = self.manager.get_store(store_name="fileSearchStores/forbidden")

        self.assertIsNone(store)
        self.mock_file_search_stores.get.assert_called_once()

    def test_list_stores_success_empty(self):
        """스토어 목록 조회 성공 (빈 목록) 테스트"""
        self.mock_file_search_stores.list.return_value = iter([])

        stores = self.manager.list_stores()

        self.assertIsInstance(stores, list)
        self.assertEqual(len(stores), 0)
        self.mock_file_search_stores.list.assert_called_once()

    def test_list_stores_success_with_items(self):
        """스토어 목록 조회 성공 (항목 포함) 테스트"""
        mock_store_1 = types.FileSearchStore(
            name="fileSearchStores/s1", display_name="Store 1"
        )
        mock_store_2 = types.FileSearchStore(
            name="fileSearchStores/s2", display_name="Store 2"
        )
        self.mock_file_search_stores.list.return_value = iter(
            [mock_store_1, mock_store_2]
        )

        stores = self.manager.list_stores()

        self.assertIsInstance(stores, list)
        self.assertEqual(len(stores), 2)
        self.assertEqual(stores[0].name, "fileSearchStores/s1")
        self.assertEqual(stores[1].display_name, "Store 2")
        self.mock_file_search_stores.list.assert_called_once()

    def test_list_stores_api_error(self):
        """스토어 목록 조회 시 API 오류 발생 테스트"""
        self.mock_file_search_stores.list.side_effect = PermissionDenied(
            "Access denied."
        )

        stores = self.manager.list_stores()

        self.assertIsInstance(stores, list)
        self.assertEqual(len(stores), 0)
        self.mock_file_search_stores.list.assert_called_once()

    def test_delete_store_success(self):
        """스토어 삭제 성공 테스트"""
        mock_store_name = "fileSearchStores/test-store-to-delete"
        self.mock_file_search_stores.delete.return_value = (
            None  # delete는 반환값이 없음
        )

        result = self.manager.delete_store(store_name=mock_store_name)

        self.assertTrue(result)
        self.mock_file_search_stores.delete.assert_called_once_with(
            name=mock_store_name
        )

    def test_delete_store_not_found(self):
        """스토어 삭제 시 찾을 수 없는 경우 테스트"""
        self.mock_file_search_stores.delete.side_effect = NotFound(
            "Store not found for deletion."
        )

        result = self.manager.delete_store(
            store_name="fileSearchStores/non-existent-to-delete"
        )

        self.assertFalse(result)
        self.mock_file_search_stores.delete.assert_called_once()

    def test_delete_store_api_error(self):
        """스토어 삭제 시 API 오류 발생 테스트"""
        self.mock_file_search_stores.delete.side_effect = PermissionDenied(
            "Cannot delete this store."
        )

        result = self.manager.delete_store(
            store_name="fileSearchStores/forbidden-to-delete"
        )

        self.assertFalse(result)
        self.mock_file_search_stores.delete.assert_called_once()


if __name__ == "__main__":
    unittest.main()
