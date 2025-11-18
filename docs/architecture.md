# SecurityChatbot 아키텍처 문서

## 목차

- [개요](#개요)
- [시스템 아키텍처](#시스템-아키텍처)
- [RAG 파이프라인](#rag-파이프라인)
- [모듈 상세 설명](#모듈-상세-설명)
- [데이터 플로우](#데이터-플로우)
- [에러 핸들링 전략](#에러-핸들링-전략)
- [보안 고려사항](#보안-고려사항)

---

## 개요

SecurityChatbot은 **Google Gemini File Search API**를 활용한 RAG(Retrieval-Augmented Generation) 기반 보안 챗봇입니다. 사용자는 보안 문서를 업로드하고, 자연어 질문을 통해 관련 정보를 검색하고 AI 기반 답변을 받을 수 있습니다.

### 핵심 기술

- **Streamlit**: 웹 기반 UI 프레임워크
- **Google Gemini API**: File Search API (RAG), Gemini Pro (LLM)
- **Python 3.10**: 주요 개발 언어
- **uv**: 패키지 관리

---

## 시스템 아키텍처

### 전체 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자 (User)                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI (main.py)                   │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  문서 업로드   │  │  채팅 인터페이스  │  │  문서 관리      │ │
│  │  (Sidebar)     │  │  (Main Area)     │  │  (Sidebar)      │ │
│  └────────────────┘  └──────────────────┘  └─────────────────┘ │
└───────────────┬─────────────┬─────────────────┬─────────────────┘
                │             │                 │
                │             │                 │
┌───────────────▼─────────────▼─────────────────▼─────────────────┐
│               비즈니스 로직 계층 (Python Modules)                 │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │session.py    │  │ui_components │  │config.py     │          │
│  │(세션 관리)   │  │(UI 컴포넌트) │  │(설정 관리)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              RAG Pipeline (rag/ 모듈)                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │document_     │  │store_        │  │query_        │    │ │
│  │  │manager.py    │  │manager.py    │  │handler.py    │    │ │
│  │  │(문서 업로드) │  │(스토어 관리) │  │(쿼리 처리)   │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          유틸리티 모듈 (utils/)                            │ │
│  │  ┌──────────────┐  ┌──────────────────────────────────┐  │ │
│  │  │api_client.py │  │error_handler.py                  │  │ │
│  │  │(API 클라이언트│  │(에러 핸들링 & 재시도)            │  │ │
│  │  └──────────────┘  └──────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬───────────────────────────────────-─┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               Google Gemini API (외부 서비스)                    │
│                                                                  │
│  ┌────────────────────────┐  ┌────────────────────────────┐    │
│  │  File Search API       │  │  Gemini Pro API            │    │
│  │  (문서 인덱싱 & 검색)   │  │  (답변 생성)               │    │
│  └────────────────────────┘  └────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 계층 구조

1. **프레젠테이션 계층 (Presentation Layer)**
   - Streamlit UI (main.py)
   - 사용자 입력 수집 및 결과 표시

2. **비즈니스 로직 계층 (Business Logic Layer)**
   - 세션 관리 (session.py)
   - RAG 파이프라인 (rag/)
   - 유틸리티 (utils/)

3. **외부 서비스 계층 (External Service Layer)**
   - Google Gemini API
   - File Search Store
   - Gemini Pro LLM

---

## RAG 파이프라인

### RAG 파이프라인 플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                        1. 문서 업로드 플로우                     │
└─────────────────────────────────────────────────────────────────┘

  사용자 파일 선택
         │
         ▼
  ┌─────────────────┐
  │ File Uploader   │ (main.py)
  │ (Streamlit)     │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ File Validation │ (document_manager.py)
  │ - 파일 형식     │
  │ - 파일 크기     │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Store Creation/Retrieval    │ (store_manager.py)
  │ - create_store()            │
  │ - get_store()               │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ File Upload to Gemini       │ (document_manager.py)
  │ - upload_file()             │
  │ - Chunking Config 적용      │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Automatic Indexing          │ (Gemini File Search API)
  │ - 청킹 (Chunking)           │
  │ - 임베딩 (Embedding)        │
  │ - 벡터 저장 (Vector Store)  │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Store Metadata in Session   │ (session.py)
  │ - 파일명, 크기, 날짜        │
  │ - corpus_file_resource_name │
  └─────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                        2. 쿼리 처리 플로우                       │
└─────────────────────────────────────────────────────────────────┘

  사용자 질문 입력
         │
         ▼
  ┌─────────────────┐
  │ Chat Input      │ (ui_components.py)
  │ - 입력 검증     │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Query Handler               │ (query_handler.py)
  │ - query_with_rag()          │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Gemini API Call             │
  │ - File Search Tool 설정     │
  │ - System Prompt 적용        │
  │ - Temperature: 0.2          │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Semantic Search             │ (Gemini File Search API)
  │ - 쿼리 임베딩               │
  │ - 유사도 검색               │
  │ - 관련 청크 검색            │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Answer Generation           │ (Gemini Pro LLM)
  │ - 검색된 컨텍스트 활용      │
  │ - 답변 생성                 │
  │ - Grounding Metadata 포함   │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Response Formatting         │ (query_handler.py)
  │ - 텍스트 추출               │
  │ - Citations 파싱            │
  │ - 에러 처리                 │
  └────────┬────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ Display to User             │ (ui_components.py)
  │ - 답변 표시                 │
  │ - 출처 표시                 │
  │ - 타임스탬프 표시           │
  └─────────────────────────────┘
```

### RAG 파이프라인 주요 특징

1. **자동 청킹 (Automatic Chunking)**
   - Google Gemini File Search API가 자동으로 문서를 청크로 분할
   - 설정 가능한 파라미터:
     - `max_tokens_per_chunk`: 최대 토큰 수 (기본값: 200, 최대: 2043)
     - `max_overlap_tokens`: 청크 간 오버랩 토큰 수 (기본값: 20)

2. **의미 기반 검색 (Semantic Search)**
   - 사용자 질문을 임베딩하여 벡터로 변환
   - 문서 청크와의 코사인 유사도 계산
   - 관련성 높은 청크를 자동으로 검색

3. **Grounding with Citations**
   - 생성된 답변에 출처 정보 자동 포함
   - 사용자는 어떤 문서를 참조했는지 확인 가능

4. **보안 특화 프롬프트**
   - 시스템 프롬프트를 통해 보안 도메인에 특화된 답변 생성
   - 추측하지 않고 문서 기반으로만 답변

---

## 모듈 상세 설명

### 1. main.py (Streamlit 앱 진입점)

**역할**:
- Streamlit 페이지 설정
- UI 레이아웃 구성 (사이드바, 메인 영역)
- 문서 업로드 및 관리 UI
- 채팅 인터페이스 통합

**주요 함수**:
- `main()`: 앱 진입점
- `_handle_document_upload()`: 문서 업로드 프로세스 처리
- `_display_uploaded_documents()`: 업로드된 문서 목록 표시
- `_handle_individual_document_deletion()`: 개별 문서 삭제
- `_handle_delete_all_documents()`: 전체 문서 삭제

### 2. config.py (설정 관리)

**역할**:
- 환경 변수 로드 (`.env` 파일)
- 애플리케이션 전역 상수 정의
- 로깅 설정

**주요 상수**:
- `GEMINI_API_KEY`: Gemini API 키
- `GEMINI_MODEL_NAME`: 사용할 모델명 (기본값: gemini-2.0-flash-exp)
- `API_TIMEOUT_SECONDS`: API 타임아웃 시간
- `DEFAULT_STORE_DISPLAY_NAME`: 기본 스토어 이름

### 3. session.py (세션 상태 관리)

**역할**:
- Streamlit 세션 상태 초기화 및 관리
- 채팅 메시지 히스토리 저장
- File Search Store 정보 관리
- 업로드된 문서 메타데이터 관리

**주요 함수**:
- `initialize_session_state()`: 세션 상태 초기화
- `add_chat_message()`: 채팅 메시지 추가
- `get_chat_messages()`: 채팅 메시지 조회
- `add_uploaded_file_metadata()`: 업로드된 파일 메타데이터 추가
- `set_rag_engine_active_status()`: RAG 엔진 상태 설정

### 4. ui_components.py (UI 컴포넌트)

**역할**:
- 재사용 가능한 UI 컴포넌트 제공
- 채팅 메시지 표시
- 사용자 입력 처리 및 검증

**주요 함수**:
- `display_message()`: 단일 채팅 메시지 표시
- `render_chat_history()`: 전체 채팅 히스토리 렌더링
- `process_chat_input()`: 사용자 입력 처리 및 RAG 쿼리 실행

### 5. rag/store_manager.py (File Search Store 관리)

**역할**:
- Google Gemini File Search Store 생성, 조회, 삭제
- 코퍼스 파일(corpus file) 삭제

**주요 메서드**:
- `create_store()`: 새로운 File Search Store 생성
- `get_store()`: Store 조회
- `list_stores()`: 모든 Store 목록 조회
- `delete_store()`: Store 삭제
- `delete_corpus_file()`: 개별 코퍼스 파일 삭제

### 6. rag/document_manager.py (문서 업로드 관리)

**역할**:
- 파일 유효성 검증 (형식, 크기)
- 파일 업로드 및 File Search Store에 추가
- 청킹 설정 적용
- 배치 업로드 지원

**주요 메서드**:
- `validate_file()`: 파일 유효성 검증
- `upload_file()`: 단일 파일 업로드
- `upload_files_batch()`: 배치 파일 업로드
- `wait_for_indexing()`: 인덱싱 완료 대기 (선택적)

**지원 파일 형식**:
- PDF (`application/pdf`)
- TXT (`text/plain`)
- Markdown (`text/markdown`)
- HWP (`application/x-hwp`)
- HWPX (`application/x-hwp-v5`)

**제약사항**:
- 최대 파일 크기: 100MB

### 7. rag/query_handler.py (쿼리 처리)

**역할**:
- RAG 기반 쿼리 실행
- Gemini File Search API 호출
- 응답 포맷팅 및 출처 파싱

**주요 함수**:
- `query_with_rag()`: RAG 쿼리 실행 및 응답 반환
- `parse_grounding_metadata()`: Grounding metadata에서 출처 추출
- `format_response()`: 응답 포맷팅

**시스템 프롬프트**:
```python
SECURITY_SYSTEM_PROMPT = """
당신은 보안 전문 챗봇입니다. 제공된 보안 문서, 위협 인텔리전스 데이터, 보안 정책 등을 분석하여
사용자 질문에 정확하고 심층적인 답변을 제공해야 합니다.

1. 보안 관련 질문에만 집중하여 답변하세요.
2. 출처 문서의 내용을 기반으로 답변을 생성하고, 추측하거나 없는 정보를 만들어내지 마세요.
3. 위협 분석, 취약점 평가, 보안 정책 해석, 규정 준수 관련 질문에 특히 강점을 보이세요.
4. 답변은 명확하고 간결하며, 필요한 경우 기술적인 세부 정보를 포함하세요.
5. 가능한 경우, 답변의 근거가 되는 출처를 명확히 제시하세요.
6. 한국어로 답변하세요.
"""
```

### 8. utils/api_client.py (API 클라이언트 관리)

**역할**:
- Gemini API 클라이언트 초기화 및 관리
- 싱글톤 패턴으로 클라이언트 재사용
- 연결 검증

**주요 클래스**:
- `GeminiClientManager`: API 클라이언트 관리 클래스
  - `get_client()`: 클라이언트 인스턴스 반환
  - `verify_connection()`: 연결 검증

### 9. utils/error_handler.py (에러 핸들링)

**역할**:
- 전역 에러 핸들러
- 사용자 친화적 에러 메시지 제공
- Exponential backoff 재시도 로직

**사용자 정의 예외**:
- `FileUploadError`: 파일 업로드 오류
- `IndexingError`: 문서 인덱싱 오류
- `QueryError`: RAG 쿼리 오류
- `ConfigurationError`: 설정 오류 (API 키 누락 등)

**주요 클래스**:
- `ErrorHandler`: 에러 핸들링 클래스
  - `handle_error()`: 에러 처리 및 로깅
  - `retry_with_backoff()`: Exponential backoff 재시도
  - `get_user_friendly_message()`: 사용자 친화적 메시지 반환

**재시도 전략**:
- 최대 재시도 횟수: 3회
- 대기 시간: 1초, 2초, 4초 (Exponential backoff)
- 재시도 대상 예외: `ResourceExhausted`, `GoogleAPIError`

---

## 데이터 플로우

### 문서 업로드 데이터 플로우

```
1. 사용자 파일 선택
   ↓
2. Streamlit file_uploader가 파일을 메모리에 로드
   ↓
3. main.py의 _handle_document_upload()가 호출됨
   ↓
4. 임시 파일로 저장 (tempfile.NamedTemporaryFile)
   ↓
5. DocumentManager.validate_file()로 검증
   ↓
6. FileSearchStoreManager.create_store() 또는 get_store()
   ↓
7. DocumentManager.upload_file()
   ├─ client.files.upload() → Gemini API에 파일 업로드
   └─ client.file_search_stores.create_corpus_file() → Store에 추가
   ↓
8. corpus_file_name (리소스 이름) 반환
   ↓
9. session.add_uploaded_file_metadata()로 메타데이터 저장
   ↓
10. session.set_rag_engine_active_status(True)
   ↓
11. UI 업데이트 (st.rerun())
```

### 쿼리 처리 데이터 플로우

```
1. 사용자가 채팅 입력창에 질문 입력
   ↓
2. ui_components.process_chat_input()가 호출됨
   ↓
3. 입력 검증 (빈 문자열, 최대 길이)
   ↓
4. session.add_chat_message(role="user", content=user_input)
   ↓
5. query_handler.query_with_rag(query, store_name) 호출
   ↓
6. Gemini API 호출
   ├─ File Search Tool 설정
   ├─ System Prompt 적용
   └─ client.models.generate_content()
   ↓
7. Gemini File Search API가 관련 문서 검색
   ↓
8. Gemini Pro LLM이 답변 생성
   ↓
9. query_handler.parse_grounding_metadata()로 출처 추출
   ↓
10. query_handler.format_response()로 응답 포맷팅
   ↓
11. session.add_chat_message(role="assistant", content=response, citations=citations)
   ↓
12. UI에 응답 표시 (st.chat_message)
```

---

## 에러 핸들링 전략

### 1. 계층별 에러 핸들링

**API 계층 (utils/api_client.py)**:
- API 키 누락: `ValueError` 발생
- API 인증 실패: `GoogleAPIError` 발생
- 연결 검증 실패: `False` 반환

**비즈니스 로직 계층 (rag/)**:
- 파일 검증 실패: `ValueError` 발생
- 파일 업로드 실패: `GoogleAPIError` 발생
- 쿼리 실패: `QueryError` 발생

**프레젠테이션 계층 (main.py, ui_components.py)**:
- 모든 예외를 `error_handler.handle_error()`로 전달
- 심각도에 따라 `st.error()`, `st.warning()`, `st.info()` 호출

### 2. 재시도 전략

**Exponential Backoff**:
```python
# 1회 시도: 실패 시 1초 대기
# 2회 시도: 실패 시 2초 대기
# 3회 시도: 실패 시 4초 대기 (최대 재시도 횟수 도달)
```

**재시도 대상 오류**:
- `ResourceExhausted`: API Rate Limit 초과
- `InternalServerError`: 서버 내부 오류
- `ServiceUnavailable`: 서비스 일시 중단

**재시도하지 않는 오류**:
- `PermissionDenied`: 권한 부족
- `InvalidArgument`: 잘못된 인자
- `NotFound`: 리소스 없음

### 3. 사용자 친화적 메시지

모든 에러는 다음 정보를 포함합니다:
- **메시지**: 사용자가 이해할 수 있는 한국어 설명
- **심각도**: CRITICAL, ERROR, WARNING, INFO
- **해결 방법**: 사용자가 취할 수 있는 조치

예시:
```python
{
    "message": "Google API 호출 한도를 초과했습니다.",
    "severity": "WARNING",
    "solution": "잠시 후 다시 시도해주세요. 반복될 경우 API 사용량 한도를 확인하거나 증액을 요청해야 할 수 있습니다."
}
```

---

## 보안 고려사항

### 1. API 키 보호

- `.env` 파일에 API 키 저장
- `.gitignore`에 `.env` 추가하여 버전 관리에서 제외
- 환경 변수가 설정되지 않은 경우 경고 로그 출력

### 2. 입력 검증

**파일 업로드**:
- 지원되는 파일 형식만 허용 (PDF, TXT, MD, HWP, HWPX)
- 최대 파일 크기 제한 (100MB)
- 파일 존재 및 유효성 검증

**사용자 입력**:
- 빈 문자열 거부
- 최대 입력 길이 제한 (2000자)
- 공백만 있는 입력 거부

### 3. 에러 메시지

- 내부 오류 세부 정보를 사용자에게 노출하지 않음
- 로그에만 상세한 스택 트레이스 기록
- 사용자에게는 일반화된 에러 메시지 표시

### 4. 세션 상태 관리

- 각 사용자의 세션 상태를 독립적으로 관리
- 세션 간 데이터 공유 없음
- 민감한 정보는 세션 상태에 저장하지 않음 (API 키 등)

### 5. HTTPS 사용

- Streamlit Cloud 또는 프로덕션 배포 시 HTTPS 사용 권장
- 네트워크 통신 암호화

---

## 확장 가능성

### 1. 멀티 스토어 지원

현재는 하나의 File Search Store만 지원하지만, 다음과 같이 확장 가능:
- 사용자별 독립적인 Store 생성
- 프로젝트별 Store 분리
- Store 전환 UI 추가

### 2. 고급 검색 기능

- 필터링 옵션 추가 (날짜, 파일 형식, 태그)
- 검색 결과 정렬 옵션
- 전문 검색 (Full-text Search) 지원

### 3. 사용자 인증

- OAuth 2.0 또는 SAML 통합
- 역할 기반 접근 제어 (RBAC)
- 감사 로그 (Audit Log)

### 4. 배치 처리

- 백그라운드 작업 큐 (Celery, RQ)
- 대용량 파일 업로드 최적화
- 인덱싱 진행률 추적

### 5. 다국어 지원

- i18n (국제화) 지원
- 다국어 문서 처리
- 언어별 시스템 프롬프트

---

## 참고 자료

- [Google Gemini API Documentation](https://ai.google.dev/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [RAG (Retrieval-Augmented Generation) 개념](https://arxiv.org/abs/2005.11401)
- [SecurityChatbot GitHub Repository](https://github.com/yourusername/SecurityChatbot)

---

## 테스트 및 품질 보증

### 테스트 현황

- **총 테스트 수**: 44개
- **테스트 통과율**: 100%
- **코드 커버리지**: 34% (목표 30% 초과 달성)

### 테스트 구성

| 테스트 파일 | 테스트 수 | 설명 |
|------------|----------|------|
| `test_config.py` | 3 | 환경 변수 및 설정 테스트 |
| `test_api_client.py` | 3 | Gemini API 클라이언트 테스트 |
| `test_store_manager.py` | 12 | File Search Store 관리 테스트 |
| `test_document_manager.py` | 18 | 문서 업로드 및 유효성 검증 테스트 |
| `test_query_handler.py` | 3 | RAG 쿼리 처리 테스트 |
| `test_integration.py` | 1 | E2E 통합 테스트 |

### 코드 품질

- **포맷팅**: Black으로 전체 코드 포맷팅 완료 (15개 파일)
- **린팅**: Ruff로 191개 오류 자동 수정 완료
- **에러 핸들링**: 전역 에러 핸들러 및 재시도 로직 구현
- **Docstring**: 모든 주요 함수 및 클래스에 상세한 문서화 완료

---

**최종 업데이트**: 2025-01-18
**버전**: 1.1
**작성자**: Claude Code
