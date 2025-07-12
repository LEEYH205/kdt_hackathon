# Policy Chatbot API

한국 지역 정책 검색을 위한 RESTful API 패키지입니다.

## 🚀 빠른 시작

### 설치

```bash
# Git에서 직접 설치
pip install git+https://github.com/your-team/policy-chatbot-api.git

# 또는 로컬에서 설치
git clone https://github.com/your-team/policy-chatbot-api.git
cd policy-chatbot-api
pip install -e .
```

### API 서버 실행

```bash
# 기본 포트(8000)로 실행
policy-api

# 특정 포트로 실행
policy-api --port 8080

# 특정 호스트로 실행
policy-api --host 0.0.0.0 --port 8000
```

### API 사용 예시

```python
import requests

# 정책 검색
response = requests.get("http://localhost:8000/search/simple", 
                       params={"query": "창업 지원", "top_k": 5})
results = response.json()

# 상세 검색
response = requests.post("http://localhost:8000/search/detailed", 
                        json={
                            "query": "포천시 창업 지원",
                            "top_k": 3,
                            "region_filter": "포천시"
                        })
results = response.json()

# 정책 요약
response = requests.get("http://localhost:8000/summary", 
                       params={"query": "소상공인 지원"})
summary = response.json()
```

## 📋 API 엔드포인트

### 1. 헬스 체크
- **GET** `/health`
- 서버 상태 및 모델 정보 확인

### 2. 간단 검색
- **GET** `/search/simple`
- **파라미터**: `query`, `top_k` (선택)

### 3. 상세 검색
- **POST** `/search/detailed`
- **파라미터**: `query`, `top_k`, `region_filter`, `target_filter`, `field_filter`

### 4. 정책 요약
- **GET** `/summary`
- **파라미터**: `query`

### 5. 지역 목록
- **GET** `/regions`
- 지원되는 지역 목록 조회

## 🔧 설정

환경 변수로 설정 가능:
- `POLICY_API_HOST`: 서버 호스트 (기본값: 0.0.0.0)
- `POLICY_API_PORT`: 서버 포트 (기본값: 8000)

## 📦 패키지 구조

```
policy-chatbot-api/
├── policy_chatbot_api/
│   ├── __init__.py
│   ├── api_server.py      # FastAPI 서버
│   ├── policy_chatbot.py  # 핵심 검색 로직
│   ├── config.py          # 설정 관리
│   └── data/              # 정책 데이터
├── setup.py
├── requirements.txt
└── README.md
```

## 🤝 팀원 사용법

### 1. 설치
```bash
pip install git+https://github.com/your-team/policy-chatbot-api.git
```

### 2. 서버 실행
```bash
policy-api --port 8000
```

### 3. API 호출
```python
import requests

# 예시: 창업 지원 정책 검색
url = "http://localhost:8000/search/simple"
params = {"query": "창업 지원", "top_k": 5}

response = requests.get(url, params=params)
policies = response.json()

for policy in policies:
    print(f"제목: {policy['title']}")
    print(f"소관기관: {policy['organization']}")
    print(f"지원대상: {policy['target']}")
    print("---")
```

## 📞 지원

문제가 있거나 질문이 있으시면 팀 리더에게 문의하세요.

## 📄 라이선스

MIT License 