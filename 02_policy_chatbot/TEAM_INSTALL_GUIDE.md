# Policy Chatbot API - 팀원용 설치 가이드

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 방법](#설치-방법)
3. [API 서버 실행](#api-서버-실행)
4. [API 사용법](#api-사용법)
5. [문제 해결](#문제-해결)
6. [예제 코드](#예제-코드)

---

## 🖥️ 시스템 요구사항

### 필수 소프트웨어
- **Python 3.8 이상**
- **pip** (Python 패키지 관리자)
- **curl** (API 테스트용, 선택사항)

### 지원 운영체제
- ✅ Windows 10/11
- ✅ macOS 10.15 이상
- ✅ Ubuntu 18.04 이상
- ✅ CentOS 7 이상

---

## 📦 설치 방법

### 방법 1: 자동 설치 (권장)

#### Linux/Mac 사용자
```bash
# 1. 파일 다운로드 및 압축 해제
unzip policy_chatbot_api_1.0.0.zip

# 2. 설치 스크립트 실행
chmod +x install.sh
./install.sh
```

#### Windows 사용자
```cmd
# 1. 파일 다운로드 및 압축 해제
# Windows 탐색기에서 압축 해제

# 2. 설치 스크립트 실행
install.bat
```

### 방법 2: 수동 설치

```bash
# 1. 기존 설치 제거 (있다면)
pip uninstall policy-chatbot-api -y

# 2. 패키지 설치
pip install policy_chatbot_api-1.0.0-py3-none-any.whl

# 3. 설치 확인
policy-api --help
```

---

## 🚀 API 서버 실행

### 기본 실행
```bash
policy-api --port 8000
```

### 옵션 설정
```bash
# 특정 포트로 실행
policy-api --port 8080

# 모든 IP에서 접근 허용
policy-api --host 0.0.0.0 --port 8000

# 자동 리로드 모드 (개발용)
policy-api --port 8000 --reload
```

### 백그라운드 실행 (Linux/Mac)
```bash
# 백그라운드 실행
nohup policy-api --port 8000 > api.log 2>&1 &

# 프로세스 확인
ps aux | grep policy-api

# 로그 확인
tail -f api.log
```

---

## 🔌 API 사용법

### 1. API 문서 확인
브라우저에서 `http://localhost:8000/docs` 접속

### 2. 헬스 체크
```bash
curl http://localhost:8000/health
```

### 3. 기본 검색 (GET 요청)
```bash
# 간단한 검색
curl "http://localhost:8000/search/simple?query=창업지원&top_k=5"

# 지역 필터 적용
curl "http://localhost:8000/search/simple?query=창업지원&region=포천시&top_k=3"
```

### 4. 상세 검색 (POST 요청)
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "포천시 중소기업 기술지원",
    "top_k": 5,
    "region_filter": "포천시",
    "target_filter": "중소기업",
    "field_filter": "기술개발"
  }'
```

### 5. 정책 요약
```bash
curl -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{"query": "중소기업 기술지원"}'
```

### 6. 지역 목록 조회
```bash
curl http://localhost:8000/regions
```

---

## 🔧 문제 해결

### 포트 충돌
```bash
# 다른 포트 사용
policy-api --port 8001

# 또는 기존 프로세스 종료
lsof -ti:8000 | xargs kill -9
```

### 설치 오류
```bash
# 완전 재설치
pip uninstall policy-chatbot-api -y
pip install --force-reinstall policy_chatbot_api-1.0.0-py3-none-any.whl
```

### 권한 오류 (Linux/Mac)
```bash
# 실행 권한 부여
chmod +x install.sh
chmod +x policy-api
```

### Python 버전 문제
```bash
# Python 버전 확인
python3 --version

# pip 버전 확인
pip --version
```

---

## 💻 예제 코드

### Python 예제
```python
import requests
import json

# API 기본 URL
BASE_URL = "http://localhost:8000"

# 1. 헬스 체크
response = requests.get(f"{BASE_URL}/health")
print("서버 상태:", response.json())

# 2. 간단 검색
params = {
    "query": "창업 지원",
    "top_k": 5,
    "region": "포천시"
}
response = requests.get(f"{BASE_URL}/search/simple", params=params)
results = response.json()
print(f"검색 결과: {results['total_results']}개")

# 3. 상세 검색
search_data = {
    "query": "포천시 중소기업 기술지원",
    "top_k": 3,
    "region_filter": "포천시",
    "target_filter": "중소기업"
}
response = requests.post(f"{BASE_URL}/search", json=search_data)
results = response.json()

# 결과 출력
for i, policy in enumerate(results['results'], 1):
    print(f"\n{i}. {policy['title']}")
    print(f"   기관: {policy['organization']}")
    print(f"   대상: {policy['target']}")
    print(f"   유사도: {policy['similarity_score']:.3f}")

# 4. 정책 요약
summary_data = {"query": "중소기업 기술지원"}
response = requests.post(f"{BASE_URL}/summary", json=summary_data)
summary = response.json()
print(f"\n요약: {summary['summary']}")
```

### JavaScript 예제
```javascript
// 1. 간단 검색
async function searchPolicies(query, topK = 5) {
    const response = await fetch(
        `http://localhost:8000/search/simple?query=${encodeURIComponent(query)}&top_k=${topK}`
    );
    return await response.json();
}

// 2. 상세 검색
async function detailedSearch(searchData) {
    const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchData)
    });
    return await response.json();
}

// 3. 사용 예제
searchPolicies('창업 지원', 3)
    .then(results => {
        console.log('검색 결과:', results);
        results.results.forEach((policy, index) => {
            console.log(`${index + 1}. ${policy.title}`);
        });
    })
    .catch(error => console.error('오류:', error));
```

### Excel VBA 예제
```vba
Sub CallPolicyAPI()
    Dim http As Object
    Dim url As String
    Dim response As String
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' API 호출
    url = "http://localhost:8000/search/simple?query=창업지원&top_k=5"
    http.Open "GET", url, False
    http.send
    
    response = http.responseText
    
    ' 결과를 셀에 출력
    Range("A1").Value = response
    
    Set http = Nothing
End Sub
```

---

## 📞 지원 및 문의

### 문제 발생 시
1. **로그 확인**: `api.log` 파일 확인
2. **헬스 체크**: `curl http://localhost:8000/health`
3. **재시작**: 서버 재시작 후 재시도
4. **팀 리더 문의**: 위 방법으로 해결되지 않을 경우

### 유용한 명령어
```bash
# 서버 상태 확인
curl http://localhost:8000/health

# 프로세스 확인
ps aux | grep policy-api

# 포트 사용 확인
lsof -i :8000

# 로그 실시간 확인
tail -f api.log
```

---

## 📚 추가 리소스

- **API 문서**: http://localhost:8000/docs
- **ReDoc 문서**: http://localhost:8000/redoc
- **GitHub 저장소**: [팀 저장소 링크]
- **이슈 리포트**: [GitHub Issues 링크]

---

**🎉 설치가 완료되었습니다! 이제 Policy Chatbot API를 사용할 수 있습니다.** 