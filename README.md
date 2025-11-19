# SecurityChatbot

🔐 **Google Gemini File Search API를 활용한 AI 기반 RAG 보안 챗봇**

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.2-FF4B4B.svg)](https://streamlit.io/)

---

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [프로젝트 현황](#-프로젝트-현황)
- [시작하기](#-시작하기)
  - [사전 요구사항](#사전-요구사항)
  - [설치 방법](#설치-방법)
  - [환경 설정](#환경-설정)
- [사용 방법](#-사용-방법)
- [지원 파일 형식](#-지원-파일-형식)
- [프로젝트 구조](#-프로젝트-구조)
- [개발 가이드](#-개발-가이드)
- [문제 해결](#-문제-해결)
- [라이선스](#-라이선스)

---

## 🎯 프로젝트 개요

SecurityChatbot은 **Google Gemini File Search API**를 활용하여 보안 관련 문서를 학습하고, 사용자의 질문에 정확하게 답변하는 **RAG(Retrieval-Augmented Generation)** 기반 챗봇입니다.

보안 정책, 가이드라인, 매뉴얼 등의 문서를 업로드하면 자동으로 인덱싱되며, 사용자는 자연어로 질문하여 관련 정보를 빠르게 검색하고 학습할 수 있습니다.

### 왜 SecurityChatbot인가?

- **보안 문서 중앙화**: 흩어진 보안 문서를 하나의 시스템에 통합
- **빠른 정보 검색**: 키워드 검색이 아닌 의미 기반 검색으로 정확한 답변 제공
- **출처 제공**: 모든 답변에 참조 문서 출처를 함께 제공하여 신뢰성 확보
- **사용 편의성**: 웹 기반 UI로 누구나 쉽게 사용 가능

---

## ✨ 주요 기능

### 1. 다양한 문서 형식 지원
- **PDF**, **TXT**, **Markdown**, **HWP**, **HWPX** 파일 업로드 지원
- 파일당 최대 **100MB** 크기 제한
- 배치 업로드로 여러 파일 동시 처리

### 2. 자동 문서 인덱싱
- Google Gemini File Search API를 통한 자동 청킹 및 인덱싱
- 업로드 진행률 실시간 표시
- 문서 메타데이터 관리 (파일명, 크기, 업로드 날짜)

### 3. RAG 기반 질의응답
- **의미 기반 검색(Semantic Search)**으로 관련 문서 자동 검색
- **Gemini Pro** 모델을 활용한 정확한 답변 생성
- **출처 정보(Citations)** 제공으로 답변 신뢰성 확보

### 4. 사용자 친화적 UI
- Streamlit 기반의 직관적인 웹 인터페이스
- 실시간 채팅 히스토리 관리
- 블루/퍼플 테마의 세련된 디자인

### 5. 고급 문서 관리
- 파일명으로 문서 검색/필터링
- 개별 문서 또는 전체 문서 삭제
- 업로드된 문서 목록 및 상세 정보 표시

### 6. 채팅 내보내기
- **JSON** 형식: 구조화된 데이터로 내보내기 (타임스탬프, 출처 포함)
- **TXT** 형식: 사람이 읽기 쉬운 텍스트 형식으로 내보내기

### 7. 강력한 에러 핸들링
- API Rate Limit 자동 재시도 (Exponential Backoff)
- 사용자 친화적 에러 메시지 및 해결 방법 제공
- 입력값 검증 (빈 문자열, 최대 길이 제한)

### 8. 개선된 로깅 시스템
- **파일 로깅**: 모든 로그를 `logs/` 디렉토리에 자동 저장
  - `app.log`: 모든 레벨의 로그 (DEBUG 이상)
  - `error.log`: 에러만 기록 (ERROR 이상)
- **로그 로테이션**: 파일 크기 기반 자동 로테이션 (10MB, 최대 5개 백업)
- **상세한 로그 포맷**: 파일명, 함수명, 라인 번호 포함
- **환경 변수 제어**: 로그 레벨, 파일 로깅 활성화/비활성화 등 설정 가능

---

## 🛠 기술 스택

| 카테고리 | 기술 |
|---------|------|
| **언어** | Python 3.10 |
| **패키지 관리** | uv (Fast Python package installer) |
| **웹 프레임워크** | Streamlit 1.40.2 |
| **AI/ML** | Google Gemini File Search API, Gemini Pro |
| **개발 도구** | pytest, black, ruff, pytest-cov |
| **기타** | python-dotenv (환경 변수 관리) |

---

## 📊 프로젝트 현황

### 개발 완료도

- **전체 진행률**: 97% (58/60 항목 완료)
- **완료된 Phase**: Phase 1~9 (9/10)
- **현재 Phase**: Phase 10 (문서화 및 배포 준비)

### 테스트 현황

- **총 테스트 수**: 44개
- **테스트 통과율**: 100%
- **코드 커버리지**: 34% (목표 30% 초과 달성)

### 주요 모듈별 테스트

| 모듈 | 테스트 수 | 상태 |
|------|----------|------|
| `config.py` | 3개 | ✅ 통과 |
| `api_client.py` | 3개 | ✅ 통과 |
| `store_manager.py` | 12개 | ✅ 통과 |
| `document_manager.py` | 18개 | ✅ 통과 |
| `query_handler.py` | 3개 | ✅ 통과 |
| 통합 테스트 | 1개 | ✅ 통과 |

### 코드 품질

- **포맷팅**: Black으로 전체 코드 포맷팅 완료 (15개 파일)
- **린팅**: Ruff로 191개 오류 자동 수정 완료
- **에러 핸들링**: 전역 에러 핸들러 및 재시도 로직 구현

### 아키텍처

RAG 파이프라인의 상세 아키텍처는 [docs/architecture.md](docs/architecture.md)를 참조하세요.

---

## 🚀 시작하기

### 사전 요구사항

- **Python 3.10** 이상
- **Google Gemini API Key** ([발급 방법](#gemini-api-key-발급))
- **uv** (권장) 또는 pip

### 설치 방법

#### 1. 저장소 클론

```bash
git clone https://github.com/[YOUR_USERNAME]/SecurityChatbot.git
cd SecurityChatbot
```

> **Note**: `[YOUR_USERNAME]`을 실제 GitHub 사용자명으로 변경하세요.

#### 2. uv 설치 (권장)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**또는 pip 사용:**
```bash
pip install uv
```

**또는 pipx 사용:**
```bash
pipx install uv
```

#### 3. 의존성 설치

```bash
uv sync
```

이 명령어는 `pyproject.toml`에 정의된 모든 의존성을 자동으로 설치합니다.

### 환경 설정

#### 1. 환경 변수 파일 생성

```bash
cp .env.example .env
```

#### 2. Gemini API Key 발급

1. [Google AI Studio](https://ai.google.dev/) 방문
2. 로그인 후 **Get API Key** 클릭
3. API 키 생성 및 복사

#### 3. `.env` 파일 편집

```bash
# .env 파일에 발급받은 API 키 입력
GEMINI_API_KEY=your_gemini_api_key_here

# 선택사항: 로깅 설정
LOG_LEVEL=INFO                  # 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
FILE_LOGGING_ENABLED=true       # 파일 로깅 활성화 여부
LOG_MAX_BYTES=10485760          # 로그 파일 최대 크기 (10MB)
LOG_BACKUP_COUNT=5              # 백업 파일 개수
```

⚠️ **주의**: `.env` 파일은 절대 Git에 커밋하지 마세요! (`.gitignore`에 포함되어 있습니다)

---

## 📖 사용 방법

### 1. 애플리케이션 실행

```bash
uv run streamlit run src/security_chatbot/main.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱에 접속할 수 있습니다.

### 2. 문서 업로드

1. 좌측 사이드바에서 **"보안 문서 업로드"** 섹션을 찾습니다.
2. **"파일 선택"** 버튼을 클릭하여 문서를 선택합니다. (여러 파일 동시 선택 가능)
3. **"업로드 시작"** 버튼을 클릭합니다.
4. 업로드 진행률을 확인하고, 완료되면 문서 목록에 표시됩니다.

### 3. 질문하기

1. 메인 화면 하단의 채팅 입력창에 질문을 입력합니다.
2. 엔터를 누르면 AI가 업로드된 문서를 기반으로 답변을 생성합니다.
3. 답변 하단에 **출처 정보(Citations)**가 표시되어 어떤 문서를 참고했는지 확인할 수 있습니다.

**질문 예시**:
- "OAuth 2.0의 주요 보안 취약점은 무엇인가요?"
- "SQL Injection 공격을 방지하는 방법을 알려주세요."
- "OWASP Top 10에서 가장 위험한 취약점은 무엇인가요?"
- "보안 정책에서 비밀번호 복잡도 요구사항이 어떻게 되나요?"
- "XSS 공격과 CSRF 공격의 차이점은 무엇인가요?"

### 4. 문서 관리

- **문서 검색**: 사이드바의 검색창에 파일명을 입력하여 필터링
- **문서 삭제**: 각 문서 옆의 🗑️ 버튼을 클릭하여 개별 삭제
- **전체 삭제**: "모든 문서 삭제" 버튼으로 전체 문서 삭제

### 5. 채팅 내보내기

1. 사이드바에서 **"채팅 내보내기"** 섹션을 찾습니다.
2. **JSON** 또는 **TXT** 형식을 선택합니다.
3. 다운로드 버튼을 클릭하여 채팅 기록을 저장합니다.

### 6. 채팅 초기화

- 사이드바의 **"대화 기록 초기화"** 버튼을 클릭하면 현재 채팅 세션을 초기화합니다.

---

## 📁 지원 파일 형식

| 파일 형식 | MIME Type | 확장자 | 최대 크기 |
|----------|-----------|--------|----------|
| PDF | application/pdf | `.pdf` | 100MB |
| 텍스트 | text/plain | `.txt` | 100MB |
| Markdown | text/markdown | `.md` | 100MB |
| HWP | application/x-hwp | `.hwp` | 100MB |
| HWPX | application/x-hwp-v5 | `.hwpx` | 100MB |

---

## 🗂 프로젝트 구조

```
SecurityChatbot/
├── .env                          # 환경 변수 (gitignored)
├── .env.example                  # 환경 변수 템플릿
├── .gitignore                    # Git 무시 파일
├── .python-version               # Python 버전 (3.10)
├── pyproject.toml                # 프로젝트 메타데이터 및 의존성
├── uv.lock                       # 의존성 잠금 파일
├── README.md                     # 이 파일
├── LICENSE                       # MIT 라이선스
├── CLAUDE.md                     # Claude Code 개발 가이드
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
│           ├── api_client.py     # Gemini API 클라이언트 래퍼
│           └── error_handler.py  # 에러 핸들링
│
├── data/
│   └── documents/                # 업로드된 문서 (gitignored)
│
├── logs/                         # 로그 파일 (gitignored)
│   ├── app.log                   # 전체 로그
│   └── error.log                 # 에러 로그만
│
├── tests/                        # 테스트 파일
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_api_client.py
│   ├── test_store_manager.py
│   ├── test_document_manager.py
│   ├── test_query_handler.py
│   └── test_integration.py
│
└── docs/
    └── architecture.md           # 아키텍처 상세 문서
```

---

## 👨‍💻 개발 가이드

### 개발 환경 설정

```bash
# 의존성 동기화
uv sync

# 개발 서버 실행 (자동 리로드)
uv run streamlit run src/security_chatbot/main.py --server.runOnSave=true
```

### 테스트 실행

```bash
# 전체 테스트 실행
uv run pytest

# 커버리지 포함
uv run pytest --cov=src/security_chatbot --cov-report=html

# 특정 테스트 파일 실행
uv run pytest tests/test_query_handler.py

# verbose 모드
uv run pytest -v
```

### 코드 품질

```bash
# 코드 포맷팅 (Black)
uv run black src/ tests/

# 린팅 (Ruff)
uv run ruff check src/ tests/

# 자동 수정
uv run ruff check --fix src/ tests/
```

### 패키지 관리

```bash
# 새 패키지 추가
uv add <package-name>

# 개발 의존성 추가
uv add --dev <package-name>

# 패키지 제거
uv remove <package-name>

# 의존성 업데이트
uv lock --upgrade
```

---

## 🔧 문제 해결

### 1. API 키 오류

**증상**: `ConfigurationError: API 키가 설정되지 않았습니다`

**해결 방법**:
```bash
# .env 파일이 존재하는지 확인
ls -la .env

# .env 파일에 API 키가 올바르게 설정되어 있는지 확인
cat .env

# API 키가 없다면 .env.example을 복사하여 생성
cp .env.example .env

# .env 파일에 발급받은 API 키 입력
nano .env  # 또는 vim, code 등 편집기 사용
```

### 2. 파일 업로드 실패

**증상**: `FileUploadError: 파일 업로드에 실패했습니다`

**원인 및 해결 방법**:
- **파일 크기 초과**: 100MB 이하로 제한됩니다. 파일을 분할하거나 압축해주세요.
- **지원되지 않는 형식**: PDF, TXT, MD, HWP, HWPX만 지원됩니다.
- **네트워크 오류**: 인터넷 연결을 확인하고 다시 시도해주세요.

### 3. 모듈을 찾을 수 없음 (Import Error)

**증상**: `ModuleNotFoundError: No module named 'streamlit'`

**해결 방법**:
```bash
# 의존성 재설치
uv sync

# 또는 uv run 명령어 사용
uv run streamlit run src/security_chatbot/main.py
```

### 4. Streamlit이 실행되지 않음

**증상**: `streamlit: command not found`

**해결 방법**:
```bash
# uv run 명령어 사용 (권장)
uv run streamlit run src/security_chatbot/main.py

# 또는 가상환경 활성화 후 실행
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate  # Windows
streamlit run src/security_chatbot/main.py
```

### 5. API Rate Limit 오류

**증상**: `429 Resource Exhausted: Quota exceeded`

**해결 방법**:
- 앱이 자동으로 3회까지 재시도합니다 (1초, 2초, 4초 간격).
- 잠시 기다렸다가 다시 시도해주세요.
- 무료 플랜의 경우 하루 요청 수 제한이 있을 수 있습니다.

### 6. 채팅 응답이 느림

**원인**: Gemini API의 응답 속도는 네트워크 및 문서 개수에 따라 달라집니다.

**해결 방법**:
- 관련 없는 문서는 삭제하여 검색 범위를 줄입니다.
- 짧고 명확한 질문을 작성합니다.

### 7. 로그 파일 확인 및 디버깅

**로그 파일 위치**: `logs/app.log`, `logs/error.log`

**실시간 로그 모니터링**:
```bash
# 전체 로그 실시간 확인
tail -f logs/app.log

# 에러 로그만 확인
tail -f logs/error.log

# 특정 키워드 검색
grep "ERROR" logs/app.log
```

**로그 레벨 변경**:
```bash
# .env 파일에서 설정
LOG_LEVEL=DEBUG  # 더 상세한 로그 출력
```

**로그 비활성화** (성능 향상):
```bash
# .env 파일에서 설정
FILE_LOGGING_ENABLED=false
```

---

## 📝 라이선스

이 프로젝트는 **MIT License**로 제공됩니다.

```
MIT License

Copyright (c) 2025 bluebary

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

전체 라이선스 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 감사의 말

- **Google Gemini API**: RAG 시스템의 핵심 기능 제공
- **Streamlit**: 빠르고 쉬운 웹 UI 구축
- **uv**: 빠르고 안정적인 Python 패키지 관리

---

## 📧 문의 및 기여

버그 리포트, 기능 제안, 기여는 언제든지 환영합니다!

### 기여 방법

1. 이 저장소를 포크합니다.
2. 새로운 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

### 버그 리포트 및 기능 제안

- **GitHub Repository**: `https://github.com/[YOUR_USERNAME]/SecurityChatbot`
  > **Note**: 실제 저장소를 생성한 후 위 URL을 업데이트해주세요.

프로젝트 개선을 위한 여러분의 참여를 기다립니다!

---

**Made with ❤️ by bluebary**
