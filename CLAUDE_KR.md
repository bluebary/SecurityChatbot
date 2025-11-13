# CLAUDE_KR.md

이 파일은 이 저장소의 코드 작업 시 Claude Code (claude.ai/code)에 대한 지침을 제공합니다.

## 프로젝트 개요

SecurityChatbot은 Google Gemini File Search API를 사용하는 AI 기반 RAG (Retrieval-Augmented Generation) 보안 챗봇입니다.

**라이선스**: MIT License (Copyright 2025 bluebary)

**개발 상태**: 활발한 개발 중 - 초기 설정 단계

## 기술 스택

- **Python 3.10**: 주요 개발 언어
- **uv**: 빠르고 안정적인 Python 패키지 설치 및 의존성 관리 도구
- **Streamlit**: 사용자 친화적인 웹 기반 UI 프레임워크
- **Google Gemini File Search API**: 문서 인덱싱 및 검색을 위한 관리형 RAG 시스템
- **python-dotenv**: `.env` 파일에서 환경 변수 관리

## 개발 워크플로우

이 프로젝트는 **Gemini-Claude 협업 워크플로우**를 따릅니다:

### 코드 구현
1. **Gemini** (`mcp__zen__chat` 도구 사용): 초기 코드 초안 생성
2. **Claude**: 코드 검토, 개선 및 향상
3. **Claude**: Write/Edit 도구를 사용하여 최종 코드를 파일에 작성

[TODO.md](TODO.md)에 **[Gemini → Claude]**로 표시된 모든 코드 항목은 이 워크플로우를 따릅니다.

### 문서 작성
**모든 문서는 Claude가 작성합니다**. 여기에는 다음이 포함됩니다:
- README.md
- 아키텍처 문서 (docs/)
- 코드 주석 및 Docstring
- API 문서
- 사용자 가이드

### mcp__zen__chat 사용법

Gemini에 코드 요청 시:
- 명확한 요구사항과 컨텍스트 제공
- 생성할 파일/모듈 명시
- 관련 기술 제약사항 포함
- 필요시 기존 코드 패턴 참조

**참고**: Gemini에게 문서 작성을 요청하지 마세요 - Claude가 모든 문서 작업을 처리합니다.

## 개발 진행 상황

**현재 단계**: 1단계 - 프로젝트 설정

자세한 구현 체크리스트(10단계, 약 60개 항목)는 [TODO.md](TODO.md)를 참조하세요.

**진행 요약**:
- ✅ TODO.md 생성 완료
- ✅ CLAUDE.md 업데이트 완료
- ⏳ 프로젝트 초기화 진행 중

## 파일 형식 지원

**지원되는 문서 형식**:
- PDF (application/pdf)
- TXT (text/plain)
- Markdown (text/markdown)
- HWP (application/x-hwp)
- HWPX (application/x-hwp-v5)

**제한사항**:
- 최대 파일 크기: 파일당 100MB
- 파일은 Gemini File Search API에 의해 자동으로 처리 및 인덱싱됩니다 (수동 전처리 불필요)

## 프로젝트 아키텍처

### RAG 파이프라인 아키텍처

```
사용자 입력 (쿼리 / 파일 업로드)
        ↓
  Streamlit UI
        ↓
        ├─ 파일 업로드 플로우 ─────────────────────────┐
        │       ↓                                      │
        │  문서 유효성 검증                              │
        │       ↓                                      │
        │  Gemini File Search Store에 업로드          │
        │  (자동 청킹 및 인덱싱)                         │
        │       ↓                                      │
        │  인덱싱된 지식 베이스                          │
        │                                              │
        ├─ 쿼리 플로우 ────────────────────────────────┘
        │       ↓
        │  RAG 쿼리 핸들러
        │       ↓
        │  Gemini File Search API
        │  (검색: 시맨틱 검색)
        │       ↓
        │  Gemini Pro LLM
        │  (생성: 검색된 컨텍스트와 함께)
        │       ↓
        │  응답 + 인용
        │       ↓
  Streamlit UI (표시)
```

### 디렉토리 구조

```
SecurityChatbot/
├── .env                          # 환경 변수 (gitignored)
├── .env.example                  # 환경 변수 템플릿
├── .gitignore                    # Git 제외 규칙
├── .python-version               # Python 버전 (3.10)
├── pyproject.toml                # 프로젝트 메타데이터 및 의존성
├── uv.lock                       # 의존성 락파일
├── README.md                     # 사용자 가이드
├── LICENSE                       # MIT 라이선스
├── CLAUDE.md                     # 이 파일 (영문)
├── CLAUDE_KR.md                  # 이 파일 (한글)
├── TODO.md                       # 구현 체크리스트
│
├── src/
│   └── security_chatbot/         # 메인 애플리케이션 패키지
│       ├── __init__.py
│       ├── main.py               # Streamlit 앱 진입점
│       ├── config.py             # 설정 및 환경 변수 관리
│       │
│       ├── rag/                  # RAG 파이프라인 모듈
│       │   ├── __init__.py
│       │   ├── document_manager.py   # 파일 업로드 및 검증
│       │   ├── store_manager.py      # File Search Store 작업
│       │   └── query_handler.py      # RAG 쿼리 처리
│       │
│       ├── chat/                 # 채팅 인터페이스 모듈
│       │   ├── __init__.py
│       │   ├── session.py        # 세션 상태 관리
│       │   └── ui_components.py  # 재사용 가능한 UI 컴포넌트
│       │
│       └── utils/                # 유틸리티 모듈
│           ├── __init__.py
│           └── api_client.py     # Gemini API 클라이언트 래퍼
│
├── data/
│   └── documents/                # 업로드된 문서 (gitignored)
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_api_client.py
│   ├── test_store_manager.py
│   ├── test_document_manager.py
│   ├── test_query_handler.py
│   └── test_integration.py       # 엔드투엔드 테스트
│
└── docs/
    └── architecture.md           # 상세 아키텍처 문서 (선택사항)
```

### 모듈 역할

- **main.py**: Streamlit 애플리케이션 진입점, UI 레이아웃 조율
- **config.py**: 환경 변수 로드, 설정 상수 정의
- **api_client.py**: Gemini API 클라이언트 초기화 및 관리
- **store_manager.py**: File Search Store 생성, 조회, 검색, 삭제
- **document_manager.py**: 문서 검증, File Search Store 업로드, 인덱싱 모니터링
- **query_handler.py**: RAG 파이프라인을 사용한 사용자 쿼리 처리, 응답 포맷팅
- **session.py**: Streamlit 세션 상태 관리 (채팅 기록, 스토어 정보)
- **ui_components.py**: 재사용 가능한 Streamlit UI 컴포넌트 (채팅 메시지, 파일 업로더)

## 개발 환경 설정

### 사전 요구사항

1. **uv 설치**:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # 또는 pip 사용
   pip install uv

   # 또는 pipx 사용
   pipx install uv
   ```

2. **Python 3.10 확인**:
   ```bash
   python3.10 --version
   ```

### 초기 설정

1. **저장소 클론**:
   ```bash
   git clone <repository-url>
   cd SecurityChatbot
   ```

2. **의존성 설치**:
   ```bash
   uv sync
   ```
   이 명령은 `pyproject.toml`에 정의된 모든 의존성을 설치합니다.

3. **환경 변수 설정**:
   ```bash
   cp .env.example .env
   ```
   `.env` 파일을 편집하여 Gemini API 키를 추가하세요:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Gemini API 키 발급**:
   - https://ai.google.dev/ 방문
   - 로그인 후 API 키 메뉴로 이동
   - 새 API 키 생성
   - `.env` 파일에 복사

## 주요 명령어

### 개발

```bash
# 의존성 설치/동기화
uv sync

# Streamlit 개발 서버 실행
uv run streamlit run src/security_chatbot/main.py

# 코드 변경 시 자동 재실행
uv run streamlit run src/security_chatbot/main.py --server.runOnSave=true
```

### 테스트

```bash
# 모든 테스트 실행
uv run pytest

# 커버리지 리포트와 함께 실행
uv run pytest --cov=src/security_chatbot --cov-report=html

# 특정 테스트 파일 실행
uv run pytest tests/test_document_manager.py

# 상세 출력으로 실행
uv run pytest -v
```

### 코드 품질

```bash
# Black으로 코드 포맷팅
uv run black src/ tests/

# Ruff로 코드 린팅
uv run ruff check src/ tests/

# 린팅 이슈 자동 수정
uv run ruff check --fix src/ tests/

# 타입 체크 (mypy 추가 시)
uv run mypy src/
```

### 패키지 관리

```bash
# 새 의존성 추가
uv add <package-name>

# 개발 의존성 추가
uv add --dev <package-name>

# 모든 의존성 업데이트
uv lock --upgrade

# 의존성 제거
uv remove <package-name>
```

## 보안 모범 사례

- **`.env` 파일 커밋 금지** - 민감한 API 키 포함
- **`.env.example` 사용** - 필수 환경 변수 템플릿 제공
- **파일 업로드 검증** - 처리 전 파일 크기 및 형식 확인
- **API 오류 처리** - 사용자에게 내부 오류 노출 방지
- **Rate Limit 처리** - 지수 백오프를 사용한 재시도 로직 구현
- **입력값 검증** - 사용자 쿼리 검증 및 새니타이징

## 문제 해결

### 일반적인 문제

1. **API 키 오류**:
   - `.env`에 `GEMINI_API_KEY`가 설정되어 있는지 확인
   - https://ai.google.dev/ 에서 API 키 유효성 확인

2. **Import 오류**:
   - `uv sync`를 실행하여 모든 의존성이 설치되었는지 확인
   - Python 버전이 3.10인지 확인

3. **Streamlit을 찾을 수 없음**:
   - `uv run` 접두사 사용: `uv run streamlit run ...`
   - 또는 수동으로 venv 활성화 후 streamlit 실행

## 다음 단계

전체 구현 로드맵은 [TODO.md](TODO.md)를 참조하세요.
