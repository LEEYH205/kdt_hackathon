#!/bin/bash

# Policy Chatbot API 패키지 배포 스크립트
# 팀원들이 코드 없이 API만 사용할 수 있도록 wheel 파일을 생성합니다.

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 Policy Chatbot API 패키지 배포 시작..."

# 1. 기존 빌드 파일 정리
echo "📁 기존 빌드 파일 정리 중..."
rm -rf build/ dist/ *.egg-info/
rm -f *.whl *.tar.gz

# 2. 패키지 빌드
echo "🔨 패키지 빌드 중..."
python setup.py sdist bdist_wheel

# 3. 빌드 결과 확인
echo "✅ 빌드 결과 확인 중..."
ls -la dist/

# 4. 패키지 테스트 설치
echo "🧪 패키지 테스트 설치 중..."
pip uninstall policy-chatbot-api -y 2>/dev/null || true
pip install dist/policy_chatbot_api-*.whl

# 5. API 서버 테스트
echo "🔍 API 서버 테스트 중..."
timeout 10s policy-api --port 8001 &
SERVER_PID=$!
sleep 5

# 헬스 체크
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ API 서버 정상 동작 확인"
else
    echo "❌ API 서버 테스트 실패"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

# 서버 종료
kill $SERVER_PID 2>/dev/null || true

# 6. 배포 파일 생성
echo "📦 배포 파일 생성 중..."
DEPLOY_DIR="deploy_package_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEPLOY_DIR

# wheel 파일 복사
cp dist/policy_chatbot_api-*.whl $DEPLOY_DIR/

# 설치 스크립트 생성
cat > $DEPLOY_DIR/install.sh << 'EOF'
#!/bin/bash
# Policy Chatbot API 설치 스크립트

echo "🚀 Policy Chatbot API 설치 시작..."

# Python 환경 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    exit 1
fi

# pip 확인
if ! command -v pip &> /dev/null; then
    echo "❌ pip가 설치되어 있지 않습니다."
    exit 1
fi

# 기존 설치 제거
echo "🧹 기존 설치 제거 중..."
pip uninstall policy-chatbot-api -y 2>/dev/null || true

# 패키지 설치
echo "📦 패키지 설치 중..."
pip install policy_chatbot_api-*.whl

# 설치 확인
if command -v policy-api &> /dev/null; then
    echo "✅ 설치 완료!"
    echo ""
    echo "🎉 사용 방법:"
    echo "1. API 서버 실행: policy-api --port 8000"
    echo "2. 브라우저에서 확인: http://localhost:8000/docs"
    echo "3. API 테스트: curl http://localhost:8000/health"
else
    echo "❌ 설치 실패"
    exit 1
fi
EOF

chmod +x $DEPLOY_DIR/install.sh

# Windows용 설치 스크립트 생성
cat > $DEPLOY_DIR/install.bat << 'EOF'
@echo off
REM Policy Chatbot API 설치 스크립트 (Windows)

echo 🚀 Policy Chatbot API 설치 시작...

REM Python 환경 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

REM pip 확인
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip가 설치되어 있지 않습니다.
    pause
    exit /b 1
)

REM 기존 설치 제거
echo 🧹 기존 설치 제거 중...
pip uninstall policy-chatbot-api -y >nul 2>&1

REM 패키지 설치
echo 📦 패키지 설치 중...
pip install policy_chatbot_api-*.whl

REM 설치 확인
where policy-api >nul 2>&1
if errorlevel 1 (
    echo ❌ 설치 실패
    pause
    exit /b 1
) else (
    echo ✅ 설치 완료!
    echo.
    echo 🎉 사용 방법:
    echo 1. API 서버 실행: policy-api --port 8000
    echo 2. 브라우저에서 확인: http://localhost:8000/docs
    echo 3. API 테스트: curl http://localhost:8000/health
)

pause
EOF

# README 파일 생성
cat > $DEPLOY_DIR/README.md << 'EOF'
# Policy Chatbot API - 팀원용 설치 가이드

## 🚀 빠른 시작

### 1. 설치
```bash
# Linux/Mac
chmod +x install.sh
./install.sh

# Windows
install.bat
```

### 2. API 서버 실행
```bash
policy-api --port 8000
```

### 3. API 사용
- **API 문서**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health
- **간단 검색**: http://localhost:8000/search/simple?query=창업지원

## 📋 API 엔드포인트

### 기본 검색
```bash
curl "http://localhost:8000/search/simple?query=창업지원&top_k=5"
```

### 상세 검색
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "포천시 창업 지원",
    "top_k": 5,
    "region_filter": "포천시"
  }'
```

### 정책 요약
```bash
curl -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{"query": "중소기업 기술지원"}'
```

## 🔧 문제 해결

### 포트 충돌 시
```bash
policy-api --port 8001
```

### 설치 오류 시
```bash
pip uninstall policy-chatbot-api -y
pip install --force-reinstall policy_chatbot_api-*.whl
```

## 📞 지원
문제가 발생하면 팀 리더에게 문의하세요.
EOF

# 7. 배포 완료
echo "🎉 배포 완료!"
echo ""
echo "📁 배포 폴더: $DEPLOY_DIR"
echo "📦 포함된 파일:"
ls -la $DEPLOY_DIR/
echo ""
echo "📋 팀원 배포 방법:"
echo "1. $DEPLOY_DIR 폴더를 압축하여 팀원들에게 공유"
echo "2. 팀원들은 압축 해제 후 install.sh 또는 install.bat 실행"
echo "3. policy-api 명령어로 서버 실행"
echo ""
echo "🔗 Git 배포 방법:"
echo "git add $DEPLOY_DIR/"
echo "git commit -m 'Add package deployment files'"
echo "git push origin main" 