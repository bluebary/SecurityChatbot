# SecurityChatbot Project TODO List

**프로젝트 개요:**
- Python 3.10, uv, Streamlit 기반
- Google Gemini File Search API를 사용한 RAG 보안 챗봇
- 지원 파일 형식: PDF, TXT, Markdown, HWP, HWPX

**개발 워크플로우:** 모든 코드는 Gemini가 초안 작성 → Claude가 검토 및 수정

---

## phase 1. 프로젝트 초기 설정 (예상 소요 시간: 0.5일)

- [ ] uv 설치 확인 (`uv --version`)
- [ ] Python 3.10으로 프로젝트 초기화 (`uv init`)
- [ ] `.python-version` 파일 생성 (3.10 명시)
- [ ] **[Gemini → Claude]** `pyproject.toml` 작성 (프로젝트 메타데이터 및 의존성)
- [ ] **[Gemini → Claude]** `.gitignore` 생성 (.env, data/documents/, __pycache__, .pytest_cache 등)
- [ ] **[Gemini → Claude]** `.env.example` 생성 (GEMINI_API_KEY 템플릿)
- [ ] 디렉토리 구조 생성 (src/security_chatbot/, tests/, data/documents/, docs/)
- [ ] 초기 의존성 설치 (`uv add google-genai streamlit python-dotenv`)
- [ ] 개발 의존성 설치 (`uv add --dev pytest pytest-cov black ruff`)
- [ ] Git 저장소 초기화 및 초기 커밋

## phase 2. Gemini API 통합 기본 구조 (예상 소요 시간: 1일)

- [ ] **[Gemini → Claude]** `src/security_chatbot/config.py` 작성
  - 환경 변수 로드 (dotenv)
  - 설정 상수 정의 (API 키, 모델명, 청킹 설정 등)
- [ ] **[Gemini → Claude]** `src/security_chatbot/utils/api_client.py` 작성
  - Gemini Client 초기화 함수
  - API 연결 검증 함수
- [ ] **[Gemini → Claude]** `src/security_chatbot/rag/store_manager.py` 작성
  - File Search Store 생성 함수
  - File Search Store 조회/목록 함수
  - File Search Store 삭제 함수
- [ ] **[Gemini → Claude]** `tests/test_store_manager.py` 작성
- [ ] 실제 API 키로 연결 테스트 실행

## phase 3. 문서 업로드 및 인덱싱 (예상 소요 시간: 1.5일)

- [ ] **[Gemini → Claude]** `src/security_chatbot/rag/document_manager.py` 작성
  - 파일 유효성 검증 함수 (파일 형식, 크기 제한 100MB)
  - 단일 파일 업로드 함수 (File Search Store에 직접 업로드)
  - 배치 파일 업로드 함수
  - Operation 폴링 및 인덱싱 완료 대기 함수(Option으로 사용)
  - 청킹 설정 적용 (max_tokens_per_chunk, overlap)
- [ ] 에러 핸들링 추가
  - 파일 크기 초과
  - 지원되지 않는 파일 형식
  - API 오류
- [ ] 재시도 로직 구현 (exponential backoff)
- [ ] **[Gemini → Claude]** `tests/test_document_manager.py` 작성
- [ ] 파일 형식별 업로드 테스트 (PDF, TXT, MD, HWP, HWPX)

## phase 4. Streamlit UI 기본 구조 (예상 소요 시간: 1일)

- [ ] **[Gemini → Claude]** `src/security_chatbot/chat/session.py` 작성
  - 세션 상태 초기화 함수
  - 세션 상태 관리 유틸리티
- [ ] **[Gemini → Claude]** `src/security_chatbot/main.py` 작성 (Part 1: 기본 레이아웃)
  - Streamlit 페이지 설정 (st.set_page_config)
  - 앱 타이틀 및 설명
  - 기본 레이아웃 구조
- [ ] **[Gemini → Claude]** 사이드바 문서 업로드 UI 구현
  - st.file_uploader (multiple files 지원)
  - 업로드 버튼
  - 업로드 진행 상황 표시 (st.spinner, st.progress)
  - 업로드된 문서 목록 표시
- [ ] 로컬 테스트 실행 (`uv run streamlit run src/security_chatbot/main.py`)
- [ ] UI/UX 개선 (레이아웃, 색상, 아이콘)

## phase 5. 채팅 인터페이스 구현 (예상 소요 시간: 1.5일)

- [ ] **[Gemini → Claude]** `src/security_chatbot/chat/ui_components.py` 작성
  - 채팅 메시지 표시 컴포넌트
  - 채팅 입력 처리 함수
  - 채팅 히스토리 렌더링 함수
- [ ] **[Gemini → Claude]** `main.py`에 채팅 UI 통합
  - 세션 상태 관리 (messages 리스트)
  - 채팅 히스토리 표시 (st.chat_message)
  - 사용자 입력 처리 (st.chat_input)
- [ ] 기본 에코 봇 구현 (Gemini 연동 전 테스트용)
- [ ] 채팅 초기화 버튼 추가 (사이드바)
- [ ] 메시지 타임스탬프 표시
- [ ] 긴 대화 기록 스크롤 처리

## phase 6. RAG 쿼리 처리 구현 (예상 소요 시간: 2일)

- [ ] **[Gemini → Claude]** `src/security_chatbot/rag/query_handler.py` 작성
  - Gemini File Search 쿼리 함수 (generate_content with tools)
  - 보안 특화 시스템 프롬프트 작성
  - Grounding metadata 파싱 함수
  - 응답 포맷팅 함수
- [ ] **[Gemini → Claude]** `main.py`에 쿼리 핸들러 통합
  - 사용자 쿼리를 query_handler로 전달
  - 응답 수신 및 표시
- [ ] 응답에 출처 정보 표시 (grounding metadata 활용)
- [ ] 스트리밍 응답 구현 (선택 사항)
- [ ] 쿼리 전처리 로직 (공백 제거, 포맷팅)
- [ ] **[Gemini → Claude]** `tests/test_query_handler.py` 작성
- [ ] E2E 테스트 (샘플 보안 PDF 업로드 및 질의)

## phase 7. 고급 기능 추가 (예상 소요 시간: 1.5일)

- [ ] **[Gemini → Claude]** 배치 문서 업로드 UI 개선
  - 여러 파일 동시 선택 및 업로드
  - 업로드 진행률 표시 (각 파일별)
- [ ] **[Gemini → Claude]** 문서 메타데이터 관리
  - 업로드 날짜, 파일명, 파일 크기 표시
  - 메타데이터를 세션 상태에 저장
- [ ] **[Gemini → Claude]** 문서 삭제 기능
  - 사이드바에 문서 목록 및 삭제 버튼
  - File Search Store에서 파일 삭제
- [ ] **[Gemini → Claude]** 문서 검색/필터링 기능
- [ ] **[Gemini → Claude]** 채팅 내보내기 기능 (JSON, TXT)

## phase 8. 에러 핸들링 및 사용성 개선 (예상 소요 시간: 1.5일)

- [ ] **[Gemini → Claude]** 전역 에러 핸들러 추가
- [ ] **[Gemini → Claude]** 사용자 친화적 에러 메시지
  - API 키 누락
  - 네트워크 오류
  - 파일 업로드 실패
  - 인덱싱 실패
  - 쿼리 실패
- [ ] **[Gemini → Claude]** API Rate Limit 처리
  - 재시도 로직
  - 사용자에게 대기 안내
- [ ] 로딩 상태 시각화 개선 (스피너, 진행률 바)
- [ ] 사용자 입력 검증 (빈 쿼리, 특수 문자)
- [ ] **[Gemini → Claude]** 로깅 시스템 구현 (디버깅용)
- [ ] 전체 사용자 플로우 테스트

## phase 9. 테스트 및 품질 보증 (예상 소요 시간: 1.5일)

- [ ] **[Gemini → Claude]** `pyproject.toml`에 pytest 설정 추가
- [ ] **[Gemini → Claude]** 단위 테스트 작성
  - test_config.py
  - test_api_client.py
  - test_store_manager.py
  - test_document_manager.py
  - test_query_handler.py
- [ ] **[Gemini → Claude]** 통합 테스트 작성 (`tests/test_integration.py`)
  - 문서 업로드 → 쿼리 → 응답 전체 플로우
- [ ] 테스트 실행 및 커버리지 확인 (`uv run pytest --cov`)
- [ ] 코드 포맷팅 (`uv run black src/ tests/`)
- [ ] 린팅 (`uv run ruff check src/ tests/`)
- [ ] 보안 취약점 점검 (API 키 노출, 입력값 검증)
- [ ] 성능 테스트 (대용량 파일, 다중 쿼리)
- [ ] 코드 리뷰 및 리팩토링

## phase 10. 문서화 및 배포 준비 (예상 소요 시간: 1.5일)

**참고**: 모든 문서는 Claude가 직접 작성합니다 (Gemini 사용하지 않음)

- [ ] **[Claude]** `README.md` 완성
  - 프로젝트 개요 및 주요 기능
  - 설치 방법 (uv 사용)
  - 환경 설정 (.env 파일 설정)
  - 실행 방법
  - 사용 예시 (스크린샷 포함)
  - 문제 해결 가이드
- [ ] **[Claude]** `CLAUDE.md` 최종 업데이트
  - 완성된 프로젝트 구조
  - 개발 워크플로우 설명
  - 주요 명령어
  - TODO.md 참조 링크
- [ ] **[Claude]** 코드 내 Docstring 작성 (모든 함수/클래스)
- [ ] **[Claude]** `docs/architecture.md` 작성 (선택 사항)
  - RAG 파이프라인 다이어그램
  - 모듈별 상세 설명
- [ ] 샘플 보안 문서 준비 (`data/documents/samples/`)
- [ ] **[Claude]** 배포 가이드 작성
  - Streamlit Cloud 배포
  - Docker 컨테이너화 (Dockerfile)
  - 환경 변수 설정 가이드

---

## 진행 상황 요약

- **총 Todo 항목**: 약 60개
- **예상 총 소요 시간**: 10-14일
- **완료된 항목**: 0/60
- **현재 단계**: 1단계 (프로젝트 초기 설정)
