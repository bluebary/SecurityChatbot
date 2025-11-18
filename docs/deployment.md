# SecurityChatbot 배포 가이드

이 문서는 SecurityChatbot을 다양한 환경에 배포하는 방법을 설명합니다.

## 목차

1. [Streamlit Cloud 배포](#1-streamlit-cloud-배포)
2. [Docker 컨테이너 배포](#2-docker-컨테이너-배포)
3. [로컬 프로덕션 배포](#3-로컬-프로덕션-배포)
4. [환경 변수 관리](#4-환경-변수-관리)
5. [문제 해결](#5-문제-해결)

---

## 1. Streamlit Cloud 배포

Streamlit Cloud는 Streamlit 앱을 무료로 호스팅할 수 있는 서비스입니다.

### 1.1 사전 준비

1. **GitHub 저장소 생성**
   ```bash
   # 로컬 저장소를 GitHub에 푸시
   git remote add origin https://github.com/[YOUR_USERNAME]/SecurityChatbot.git
   git branch -M main
   git push -u origin main
   ```

2. **Streamlit Cloud 계정 생성**
   - https://streamlit.io/cloud 방문
   - GitHub 계정으로 로그인

### 1.2 배포 단계

1. **Streamlit Cloud 대시보드 접속**
   - https://share.streamlit.io/ 로 이동
   - "New app" 버튼 클릭

2. **저장소 및 브랜치 선택**
   - **Repository**: `[YOUR_USERNAME]/SecurityChatbot`
   - **Branch**: `main`
   - **Main file path**: `src/security_chatbot/main.py`

3. **환경 변수 설정**
   - "Advanced settings" 클릭
   - "Secrets" 섹션에 다음 내용 추가:
   ```toml
   # .streamlit/secrets.toml 형식
   GEMINI_API_KEY = "your_gemini_api_key_here"
   GEMINI_MODEL_NAME = "gemini-2.0-flash-exp"
   ```

4. **Python 버전 지정** (선택 사항)
   - "Python version"에서 `3.10` 선택

5. **배포 시작**
   - "Deploy!" 버튼 클릭
   - 앱이 빌드되고 배포되기까지 몇 분 소요

### 1.3 배포 후 확인

- 배포가 완료되면 앱 URL이 생성됩니다 (예: `https://your-app-name.streamlit.app`)
- 브라우저에서 URL 접속하여 정상 동작 확인

### 1.4 Streamlit Cloud 업데이트

```bash
# 로컬에서 변경 사항 커밋 및 푸시
git add .
git commit -m "Update SecurityChatbot"
git push origin main
```

- GitHub에 푸시하면 Streamlit Cloud가 자동으로 재배포합니다.

### 1.5 주의사항

- **파일 크기 제한**: Streamlit Cloud는 파일 크기 제한이 있을 수 있습니다.
- **리소스 제한**: 무료 플랜은 CPU 및 메모리 제한이 있습니다.
- **환경 변수**: `.env` 파일 대신 Streamlit Cloud Secrets를 사용해야 합니다.

---

## 2. Docker 컨테이너 배포

Docker를 사용하면 일관된 환경에서 앱을 배포할 수 있습니다.

### 2.1 Dockerfile 생성

프로젝트 루트에 `Dockerfile`을 생성합니다:

```dockerfile
# SecurityChatbot Dockerfile

# Python 3.10 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# Python 버전 파일 복사
COPY .python-version ./

# 의존성 설치
RUN uv sync --frozen

# 소스 코드 복사
COPY src/ ./src/
COPY .env.example ./.env.example

# Streamlit 설정 디렉토리 생성
RUN mkdir -p .streamlit

# Streamlit 설정 파일 생성 (선택 사항)
RUN echo '\
[server]\n\
headless = true\n\
port = 8501\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
' > .streamlit/config.toml

# 포트 노출
EXPOSE 8501

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Streamlit 앱 실행
CMD ["uv", "run", "streamlit", "run", "src/security_chatbot/main.py", "--server.address=0.0.0.0"]
```

### 2.2 .dockerignore 생성

불필요한 파일을 Docker 이미지에서 제외합니다:

```
# .dockerignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.pytest_cache/
.coverage
htmlcov/
*.egg-info/

# 가상환경
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 환경 변수
.env

# 데이터
data/documents/

# Git
.git/
.gitignore

# 문서
docs/
README.md
TODO.md
CLAUDE.md

# 테스트
tests/
```

### 2.3 Docker 이미지 빌드

```bash
# Docker 이미지 빌드
docker build -t security-chatbot:latest .

# 빌드 확인
docker images | grep security-chatbot
```

### 2.4 Docker 컨테이너 실행

#### 2.4.1 환경 변수 파일 사용

먼저 `.env` 파일을 생성합니다:

```bash
# .env 파일
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-2.0-flash-exp
```

Docker 컨테이너 실행:

```bash
# .env 파일을 사용하여 컨테이너 실행
docker run -d \
  --name security-chatbot \
  -p 8501:8501 \
  --env-file .env \
  security-chatbot:latest

# 컨테이너 로그 확인
docker logs -f security-chatbot

# 브라우저에서 http://localhost:8501 접속
```

#### 2.4.2 환경 변수 직접 전달

```bash
docker run -d \
  --name security-chatbot \
  -p 8501:8501 \
  -e GEMINI_API_KEY="your_gemini_api_key_here" \
  -e GEMINI_MODEL_NAME="gemini-2.0-flash-exp" \
  security-chatbot:latest
```

### 2.5 Docker Compose 사용

`docker-compose.yml` 파일을 생성합니다:

```yaml
version: '3.8'

services:
  security-chatbot:
    build: .
    container_name: security-chatbot
    ports:
      - "8501:8501"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    volumes:
      # 선택 사항: 로그 파일 영구 저장
      - ./logs:/app/logs
```

Docker Compose로 실행:

```bash
# 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 중지
docker-compose down

# 컨테이너 재시작
docker-compose restart
```

### 2.6 Docker 이미지 배포

#### Docker Hub에 푸시

```bash
# Docker Hub 로그인
docker login

# 이미지 태그
docker tag security-chatbot:latest [YOUR_DOCKERHUB_USERNAME]/security-chatbot:latest

# 이미지 푸시
docker push [YOUR_DOCKERHUB_USERNAME]/security-chatbot:latest
```

#### 다른 서버에서 이미지 pull 및 실행

```bash
# Docker 이미지 pull
docker pull [YOUR_DOCKERHUB_USERNAME]/security-chatbot:latest

# 컨테이너 실행
docker run -d \
  --name security-chatbot \
  -p 8501:8501 \
  --env-file .env \
  [YOUR_DOCKERHUB_USERNAME]/security-chatbot:latest
```

---

## 3. 로컬 프로덕션 배포

로컬 서버 또는 VPS에 직접 배포하는 방법입니다.

### 3.1 시스템 요구사항

- **OS**: Ubuntu 20.04 LTS 이상 (권장)
- **Python**: 3.10 이상
- **메모리**: 최소 2GB RAM
- **디스크**: 최소 5GB 여유 공간

### 3.2 배포 단계

#### 3.2.1 서버 준비

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 3.10 설치 확인
python3.10 --version

# 필수 패키지 설치
sudo apt install -y git curl build-essential
```

#### 3.2.2 프로젝트 클론

```bash
# 프로젝트 디렉토리 생성
mkdir -p /opt/security-chatbot
cd /opt/security-chatbot

# Git 저장소 클론
git clone https://github.com/[YOUR_USERNAME]/SecurityChatbot.git .
```

#### 3.2.3 uv 설치

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# PATH 설정
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# uv 설치 확인
uv --version
```

#### 3.2.4 의존성 설치

```bash
# 의존성 설치
uv sync
```

#### 3.2.5 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (nano 또는 vim 사용)
nano .env

# API 키 입력
# GEMINI_API_KEY=your_gemini_api_key_here
```

#### 3.2.6 Systemd 서비스 설정

`/etc/systemd/system/security-chatbot.service` 파일 생성:

```ini
[Unit]
Description=SecurityChatbot Streamlit Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/security-chatbot
Environment="PATH=/home/www-data/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/www-data/.cargo/bin/uv run streamlit run src/security_chatbot/main.py --server.address=0.0.0.0 --server.port=8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 시작:

```bash
# Systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable security-chatbot

# 서비스 시작
sudo systemctl start security-chatbot

# 서비스 상태 확인
sudo systemctl status security-chatbot

# 로그 확인
sudo journalctl -u security-chatbot -f
```

### 3.3 Nginx 리버스 프록시 설정 (선택 사항)

HTTPS 및 도메인을 사용하려면 Nginx를 리버스 프록시로 설정합니다.

#### 3.3.1 Nginx 설치

```bash
sudo apt install -y nginx
```

#### 3.3.2 Nginx 설정

`/etc/nginx/sites-available/security-chatbot` 파일 생성:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 실제 도메인으로 변경

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 지원
        proxy_read_timeout 86400;
    }
}
```

설정 활성화:

```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/security-chatbot /etc/nginx/sites-enabled/

# Nginx 설정 검증
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

#### 3.3.3 SSL/TLS 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com

# 인증서 자동 갱신 설정 확인
sudo certbot renew --dry-run
```

---

## 4. 환경 변수 관리

### 4.1 필수 환경 변수

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `GEMINI_API_KEY` | Google Gemini API 키 | - | ✅ |
| `GEMINI_MODEL_NAME` | 사용할 Gemini 모델 | `gemini-2.0-flash-exp` | ❌ |
| `API_TIMEOUT_SECONDS` | API 타임아웃 (초) | `60` | ❌ |
| `LOG_LEVEL` | 로그 레벨 | `INFO` | ❌ |
| `DEFAULT_STORE_DISPLAY_NAME` | 기본 Store 이름 | `MyRAGFileSearchStore` | ❌ |

### 4.2 환경별 설정

#### 개발 환경 (.env.development)

```bash
GEMINI_API_KEY=your_dev_api_key
GEMINI_MODEL_NAME=gemini-2.0-flash-exp
LOG_LEVEL=DEBUG
```

#### 프로덕션 환경 (.env.production)

```bash
GEMINI_API_KEY=your_prod_api_key
GEMINI_MODEL_NAME=gemini-2.0-flash-exp
LOG_LEVEL=INFO
API_TIMEOUT_SECONDS=120
```

### 4.3 환경 변수 로드

```bash
# 개발 환경
export $(cat .env.development | xargs)

# 프로덕션 환경
export $(cat .env.production | xargs)
```

---

## 5. 문제 해결

### 5.1 Streamlit Cloud 관련

#### 문제: 앱이 시작되지 않음

**원인**: 환경 변수 미설정 또는 파일 경로 오류

**해결**:
1. Streamlit Cloud Secrets에 `GEMINI_API_KEY`가 올바르게 설정되었는지 확인
2. Main file path가 `src/security_chatbot/main.py`인지 확인
3. 로그를 확인하여 구체적인 오류 메시지 확인

#### 문제: 앱이 느리거나 메모리 부족

**원인**: 무료 플랜의 리소스 제한

**해결**:
- Streamlit Cloud Pro 플랜으로 업그레이드
- 또는 Docker/VPS로 배포

### 5.2 Docker 관련

#### 문제: Docker 이미지 빌드 실패

**원인**: 의존성 설치 실패 또는 네트워크 오류

**해결**:
```bash
# 캐시 없이 다시 빌드
docker build --no-cache -t security-chatbot:latest .
```

#### 문제: 컨테이너 실행 후 접속 불가

**원인**: 포트 충돌 또는 방화벽 설정

**해결**:
```bash
# 포트 사용 중인지 확인
sudo netstat -tulpn | grep 8501

# 다른 포트로 실행
docker run -d -p 8080:8501 --env-file .env security-chatbot:latest
```

### 5.3 로컬 프로덕션 배포 관련

#### 문제: Systemd 서비스가 시작되지 않음

**원인**: 권한 문제 또는 경로 오류

**해결**:
```bash
# 서비스 로그 확인
sudo journalctl -u security-chatbot -n 50 --no-pager

# 권한 확인
sudo chown -R www-data:www-data /opt/security-chatbot

# 서비스 재시작
sudo systemctl restart security-chatbot
```

#### 문제: Nginx 502 Bad Gateway

**원인**: Streamlit 앱이 실행 중이지 않음

**해결**:
```bash
# Streamlit 앱 상태 확인
sudo systemctl status security-chatbot

# 앱 재시작
sudo systemctl restart security-chatbot

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 6. 모니터링 및 로그 관리

### 6.1 로그 수집

#### Docker

```bash
# 컨테이너 로그 확인
docker logs -f security-chatbot

# 로그를 파일로 저장
docker logs security-chatbot > app.log 2>&1
```

#### Systemd

```bash
# 실시간 로그 확인
sudo journalctl -u security-chatbot -f

# 최근 100줄 로그 확인
sudo journalctl -u security-chatbot -n 100
```

### 6.2 성능 모니터링

#### Docker Stats

```bash
# 컨테이너 리소스 사용량 확인
docker stats security-chatbot
```

#### Systemd + htop

```bash
# CPU 및 메모리 사용량 확인
htop
```

---

## 7. 보안 권장사항

### 7.1 API 키 보호

- 환경 변수 또는 시크릿 관리 도구 사용
- `.env` 파일을 절대 Git에 커밋하지 않음
- 정기적으로 API 키 순환 (Rotation)

### 7.2 네트워크 보안

- HTTPS 사용 (Let's Encrypt 등)
- 방화벽 설정 (UFW, iptables)
- 불필요한 포트 차단

### 7.3 접근 제어

- Nginx 기본 인증 설정
- IP 화이트리스트
- OAuth 2.0 또는 SSO 통합 (향후 개선)

---

## 8. 자동화 및 CI/CD

### 8.1 GitHub Actions (예시)

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t security-chatbot:latest .

      - name: Push to Docker Hub
        env:
          DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
        run: |
          echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
          docker tag security-chatbot:latest $DOCKER_USERNAME/security-chatbot:latest
          docker push $DOCKER_USERNAME/security-chatbot:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/security-chatbot
            docker-compose pull
            docker-compose up -d
```

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-01-18
**작성자**: Claude Code
