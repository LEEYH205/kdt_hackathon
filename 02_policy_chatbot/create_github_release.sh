#!/bin/bash

# GitHub Releases 자동 생성 스크립트
# 패키지를 GitHub Releases에 업로드합니다.

set -e

# 설정
REPO_OWNER="your-username"
REPO_NAME="policy-chatbot-api"
VERSION="1.0.0"
TAG_NAME="v$VERSION"

echo "🚀 GitHub Releases 생성 시작..."

# 1. 패키지 빌드
echo "📦 패키지 빌드 중..."
./deploy_package.sh

# 2. 최신 배포 폴더 찾기
DEPLOY_DIR=$(ls -td deploy_package_* | head -1)
if [ -z "$DEPLOY_DIR" ]; then
    echo "❌ 배포 폴더를 찾을 수 없습니다."
    exit 1
fi

echo "📁 배포 폴더: $DEPLOY_DIR"

# 3. GitHub CLI 설치 확인
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI가 설치되어 있지 않습니다."
    echo "설치 방법: https://cli.github.com/"
    exit 1
fi

# 4. GitHub 로그인 확인
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub에 로그인되어 있지 않습니다."
    echo "gh auth login 명령어로 로그인하세요."
    exit 1
fi

# 5. 태그 생성
echo "🏷️ 태그 생성 중..."
git tag -a $TAG_NAME -m "Release $TAG_NAME"
git push origin $TAG_NAME

# 6. Release 생성
echo "📤 Release 생성 중..."
gh release create $TAG_NAME \
    --title "Policy Chatbot API v$VERSION" \
    --notes "## 🎉 Policy Chatbot API v$VERSION

### 새로운 기능
- 🚀 완전한 API 패키지 배포
- 📦 팀원용 자동 설치 스크립트
- 🔧 Windows/Linux/Mac 지원
- 📚 상세한 사용 가이드

### 설치 방법
1. \`policy_chatbot_api-$VERSION-py3-none-any.whl\` 파일 다운로드
2. \`install.sh\` (Linux/Mac) 또는 \`install.bat\` (Windows) 실행
3. \`policy-api --port 8000\` 명령어로 서버 실행

### API 사용
- API 문서: http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/health
- 간단 검색: http://localhost:8000/search/simple?query=창업지원

### 지원
문제가 발생하면 이슈를 생성해주세요." \
    --repo $REPO_OWNER/$REPO_NAME

# 7. 파일 업로드
echo "📁 파일 업로드 중..."
gh release upload $TAG_NAME \
    "$DEPLOY_DIR/policy_chatbot_api-$VERSION-py3-none-any.whl" \
    "$DEPLOY_DIR/install.sh" \
    "$DEPLOY_DIR/install.bat" \
    "$DEPLOY_DIR/README.md" \
    --repo $REPO_OWNER/$REPO_NAME

# 8. 배포 폴더 압축
echo "🗜️ 배포 폴더 압축 중..."
cd $DEPLOY_DIR
zip -r "../policy_chatbot_api_$VERSION.zip" .
cd ..

# 9. 압축 파일 업로드
echo "📦 압축 파일 업로드 중..."
gh release upload $TAG_NAME \
    "policy_chatbot_api_$VERSION.zip" \
    --repo $REPO_OWNER/$REPO_NAME

echo "🎉 GitHub Release 생성 완료!"
echo ""
echo "🔗 Release URL: https://github.com/$REPO_OWNER/$REPO_NAME/releases/tag/$TAG_NAME"
echo ""
echo "📋 팀원 설치 방법:"
echo "1. GitHub Releases에서 파일 다운로드"
echo "2. 압축 해제 후 install.sh 또는 install.bat 실행"
echo "3. policy-api 명령어로 서버 실행" 