"""
Gemini API 연결 테스트 스크립트

이 스크립트는 Gemini API 연결과 File Search Store API를 테스트합니다.
실행 전에 .env 파일에 GEMINI_API_KEY를 설정해야 합니다.

사용법:
    uv run python test_connection.py
"""

import sys
from security_chatbot.utils.api_client import GeminiClientManager
from security_chatbot.rag.store_manager import FileSearchStoreManager


def test_api_connection():
    """Gemini API 연결 테스트"""
    print("=" * 60)
    print("Gemini API 연결 테스트")
    print("=" * 60)

    try:
        # 1. API 클라이언트 초기화
        print("\n[1/3] Gemini API 클라이언트 초기화 중...")
        client = GeminiClientManager.get_client()
        print("✅ 클라이언트 초기화 성공")

        # 2. 연결 검증
        print("\n[2/3] API 연결 검증 중...")
        is_connected = GeminiClientManager.verify_connection()
        if is_connected:
            print("✅ API 연결 검증 성공")
        else:
            print("❌ API 연결 검증 실패")
            return False

        # 3. File Search Store 목록 조회 테스트
        print("\n[3/3] File Search Store 목록 조회 테스트 중...")
        manager = FileSearchStoreManager()
        stores = manager.list_stores()
        print(f"✅ File Search Store 목록 조회 성공 (총 {len(stores)}개의 스토어)")

        if stores:
            print("\n현재 존재하는 File Search Store:")
            for i, store in enumerate(stores, 1):
                print(f"  {i}. {store.display_name} (ID: {store.name})")
        else:
            print("  (스토어가 없습니다)")

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        return True

    except ValueError as e:
        print(f"\n❌ 환경 설정 오류: {e}")
        print("\n해결 방법:")
        print("1. .env 파일을 생성하고 GEMINI_API_KEY를 설정하세요.")
        print("2. 또는 환경 변수로 export GEMINI_API_KEY=your_api_key를 실행하세요.")
        return False
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        print(f"\n오류 타입: {type(e).__name__}")
        return False


def main():
    """메인 함수"""
    success = test_api_connection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
