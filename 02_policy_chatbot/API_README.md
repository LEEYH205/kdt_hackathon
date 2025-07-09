# 🏛️ 정책 챗봇 API 사용 가이드

정책 챗봇의 REST API를 사용하여 정책 검색 및 추천 서비스를 활용할 수 있습니다.

## 📋 목차

1. [개요](#개요)
2. [설치 및 실행](#설치-및-실행)
3. [API 엔드포인트](#api-엔드포인트)
4. [사용 예시](#사용-예시)
5. [클라이언트 라이브러리](#클라이언트-라이브러리)
6. [에러 처리](#에러-처리)
7. [성능 최적화](#성능-최적화)
8. [문제 해결](#문제-해결)

## 🎯 개요

정책 챗봇 API는 FastAPI 기반의 RESTful API로, 다음과 같은 기능을 제공합니다:

- **정책 검색**: 자연어 쿼리로 관련 정책 검색
- **필터링**: 지역, 지원대상, 지원분야별 필터링
- **정책 요약**: 검색 결과를 요약하여 제공
- **메타데이터**: 사용 가능한 지역 목록 등

### 🔧 기술 스택

- **백엔드**: FastAPI, Uvicorn
- **AI/ML**: Sentence Transformers, FAISS
- **데이터 처리**: Pandas, NumPy
- **문서화**: Swagger UI, ReDoc

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
# 프로젝트 디렉토리로 이동
cd kdt_hackathon/02_policy_chatbot

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터 준비

API 서버 실행 전에 정책 데이터가 필요합니다:

```bash
# 데이터 파일 확인
ls data/
# gyeonggi_smallbiz_policies_2000_소상공인,경기_20250705.csv 파일이 있어야 함
```

### 3. API 서버 실행

#### 기본 실행
```bash
python run_api.py
```

#### 개발 모드 (권장)
```bash
python run_api.py --reload
```

#### 다른 포트로 실행
```bash
python run_api.py --port 8080
```

#### 모든 옵션 보기
```bash
python run_api.py --help
```

### 4. 서버 상태 확인

서버가 정상적으로 실행되면 다음 URL에서 접근 가능합니다:

- **API 서버**: http://localhost:8000
- **Swagger 문서**: http://localhost:8000/docs
- **ReDoc 문서**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health

## 🌐 API 엔드포인트

### 기본 정보

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **인증**: 현재 인증 불필요

### 1. 헬스 체크

서버 상태와 모델 로드 상태를 확인합니다.

```http
GET /health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "data_count": 951
}
```

### 2. 정책 검색 (POST)

상세한 필터와 가중치를 사용한 정책 검색

```http
POST /search
Content-Type: application/json

{
  "query": "중소기업 기술지원",
  "top_k": 5,
  "similarity_threshold": 0.0,
  "region_filter": "포천시",
  "target_filter": "중소기업",
  "field_filter": "기술개발",
  "region_weight": 0.3,
  "target_weight": 0.2,
  "field_weight": 0.2
}
```

**요청 파라미터:**
- `query` (필수): 검색 쿼리
- `top_k` (선택): 반환할 결과 수 (기본값: 5, 최대: 20)
- `similarity_threshold` (선택): 유사도 임계값 (0.0~1.0, 기본값: 0.0)
- `region_filter` (선택): 지역 필터 (예: "포천시", "경기도")
- `target_filter` (선택): 지원대상 필터 (예: "중소기업", "소상공인")
- `field_filter` (선택): 지원분야 필터 (예: "기술개발", "창업")
- `region_weight` (선택): 지역 가중치 (0.0~1.0, 기본값: 0.3)
- `target_weight` (선택): 지원대상 가중치 (0.0~1.0, 기본값: 0.2)
- `field_weight` (선택): 지원분야 가중치 (0.0~1.0, 기본값: 0.2)

**응답 예시:**
```json
{
  "query": "중소기업 기술지원",
  "total_results": 3,
  "results": [
    {
      "title": "2025년 스마트물류 기술사업화 협업플랫폼 구축사업",
      "body": "블록체인을 접목한 커피, 스마트 물류, ICT 분야...",
      "target": "중소기업",
      "organization": "과학기술정보통신부",
      "field_major": "기술",
      "field_minor": "기술사업화/이전/지도",
      "executing_org": "부산테크노파크",
      "contact": "부산테크노파크 지산학DX단 블록체인센터 051-923-8313",
      "period": "20250617 ~ 20250707",
      "application_method": "이메일 접수 (lcw@btp.or.kr)",
      "similarity_score": 0.668
    }
  ],
  "filters_applied": {
    "region_filter": "포천시",
    "target_filter": "중소기업",
    "field_filter": "기술개발",
    "similarity_threshold": 0.0,
    "weights": {
      "region_weight": 0.3,
      "target_weight": 0.2,
      "field_weight": 0.2
    }
  }
}
```

### 3. 정책 검색 (GET)

간단한 파라미터로 정책 검색

```http
GET /search/simple?query=기술지원&top_k=3&region=포천시
```

**쿼리 파라미터:**
- `query` (필수): 검색 쿼리
- `top_k` (선택): 반환할 결과 수 (기본값: 5)
- `region` (선택): 지역 필터

### 4. 정책 요약

검색 결과를 요약하여 반환

```http
POST /summary
Content-Type: application/json

{
  "query": "청년 지원"
}
```

**응답 예시:**
```json
{
  "query": "청년 지원",
  "summary": "'청년 지원'와 관련된 정책을 찾았습니다:\n\n📋 2025년 2차 장애인 창업점포 지원사업...\n🎯 지원대상: 장애인기업\n🏢 소관기관: 중소벤처기업부\n📅 신청기간: 20250625 ~ 20250717\n📊 유사도 점수: 0.612\n--------------------------------------------------"
}
```

### 5. 지역 목록

사용 가능한 지역 목록과 계층 구조 반환

```http
GET /regions
```

**응답 예시:**
```json
{
  "regions": ["포천시", "가평군", "양평군", "여주시", "이천시", ...],
  "total_count": 71,
  "hierarchy": {
    "포천시": ["포천시", "경기도", "전국"],
    "가평군": ["가평군", "경기도", "전국"],
    "강남구": ["강남구", "서울특별시", "전국"],
    "경기도": ["경기도", "전국"],
    "전국": ["전국"]
  }
}
```

### 6. API 정보

API 기본 정보 반환

```http
GET /
```

**응답 예시:**
```json
{
  "message": "정책 챗봇 API에 오신 것을 환영합니다!",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

## 💻 사용 예시

### 1. curl 명령어

#### 헬스 체크
```bash
curl http://localhost:8000/health
```

#### 간단한 검색
```bash
curl "http://localhost:8000/search/simple?query=기술지원&top_k=3"
```

#### 상세 검색
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "창업 지원",
    "top_k": 5,
    "region_filter": "포천시",
    "similarity_threshold": 0.1
  }'
```

#### 정책 요약
```bash
curl -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{"query": "청년 지원"}'
```

#### 지역 목록
```bash
curl http://localhost:8000/regions
```

### 2. Python requests

```python
import requests
import json

# API 기본 URL
BASE_URL = "http://localhost:8000"

# 헬스 체크
response = requests.get(f"{BASE_URL}/health")
print(f"서버 상태: {response.json()['status']}")

# 정책 검색
search_data = {
    "query": "중소기업 기술지원",
    "top_k": 3,
    "region_filter": "포천시"
}

response = requests.post(f"{BASE_URL}/search", json=search_data)
results = response.json()

print(f"검색 결과: {results['total_results']}개")
for result in results['results']:
    print(f"- {result['title']}")
    print(f"  유사도: {result['similarity_score']:.3f}")
```

### 3. JavaScript (fetch)

```javascript
// 헬스 체크
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log('서버 상태:', data.status));

// 정책 검색
const searchData = {
  query: "중소기업 기술지원",
  top_k: 3,
  region_filter: "포천시"
};

fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(searchData)
})
.then(response => response.json())
.then(data => {
  console.log(`검색 결과: ${data.total_results}개`);
  data.results.forEach(result => {
    console.log(`- ${result.title}`);
    console.log(`  유사도: ${result.similarity_score.toFixed(3)}`);
  });
});
```

## 📚 클라이언트 라이브러리

### Python 클라이언트

프로젝트에 포함된 Python 클라이언트를 사용할 수 있습니다:

```python
from api_client import PolicyChatbotAPI

# API 클라이언트 초기화
api = PolicyChatbotAPI("http://localhost:8000")

# 헬스 체크
health = api.health_check()
print(f"서버 상태: {health['status']}")

# 정책 검색
results = api.search_policies(
    query="중소기업 기술지원",
    top_k=5,
    region_filter="포천시"
)

# 결과 출력
for result in results['results']:
    print(f"제목: {result['title']}")
    print(f"유사도: {result['similarity_score']:.3f}")
```

### 클라이언트 테스트

```bash
# 자동 테스트
python api_client.py

# 대화형 테스트
python api_client.py interactive
```

## ⚠️ 에러 처리

### HTTP 상태 코드

- `200 OK`: 요청 성공
- `400 Bad Request`: 잘못된 요청 (파라미터 오류)
- `500 Internal Server Error`: 서버 내부 오류
- `503 Service Unavailable`: 서비스 사용 불가 (모델 로드 실패)

### 에러 응답 형식

```json
{
  "detail": "에러 메시지"
}
```

### 일반적인 에러

#### 1. 모델 로드 실패
```json
{
  "detail": "챗봇이 초기화되지 않았습니다."
}
```

**해결 방법:**
- 서버 재시작
- 데이터 파일 확인
- 의존성 재설치

#### 2. 잘못된 파라미터
```json
{
  "detail": "검색 중 오류가 발생했습니다: 잘못된 파라미터"
}
```

**해결 방법:**
- 요청 파라미터 형식 확인
- 필수 파라미터 누락 확인

#### 3. 검색 결과 없음
```json
{
  "query": "존재하지 않는 검색어",
  "total_results": 0,
  "results": [],
  "filters_applied": {...}
}
```

**해결 방법:**
- 검색어 변경
- 필터 조건 완화
- 유사도 임계값 조정

## 🚀 성능 최적화

### 1. 검색 성능 향상

#### 적절한 top_k 값 사용
```python
# 너무 많은 결과 요청 방지
results = api.search_policies(query="검색어", top_k=10)  # 권장: 5-10
```

#### 유사도 임계값 활용
```python
# 낮은 유사도 결과 필터링
results = api.search_policies(
    query="검색어",
    similarity_threshold=0.3  # 0.3 이상만 반환
)
```

### 2. 필터링 최적화

#### 지역 계층 구조 활용
```python
# 포천시 검색 시 경기도, 전국 정책도 포함
results = api.search_policies(
    query="검색어",
    region_filter="포천시"  # 자동으로 상위 지역 포함
)
```

#### 가중치 조정
```python
# 지역 우선 검색
results = api.search_policies(
    query="검색어",
    region_weight=0.5,    # 지역 가중치 증가
    target_weight=0.2,
    field_weight=0.1
)
```

### 3. 요청 최적화

#### 배치 처리
```python
# 여러 검색어를 한 번에 처리
queries = ["기술지원", "창업지원", "청년지원"]
results = []

for query in queries:
    result = api.search_policies(query=query, top_k=3)
    results.append(result)
```

#### 캐싱 활용
```python
import functools

# 동일한 쿼리 결과 캐싱
@functools.lru_cache(maxsize=100)
def cached_search(query, top_k=5):
    return api.search_policies(query=query, top_k=top_k)
```

## 🔧 문제 해결

### 1. 서버 시작 실패

#### 포트 충돌
```bash
# 다른 포트 사용
python run_api.py --port 8080

# 또는 기존 프로세스 종료
lsof -ti:8000 | xargs kill -9
```

#### 의존성 문제
```bash
# 가상환경 재생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 모델 로드 실패

#### 메모리 부족
```bash
# 시스템 메모리 확인
free -h  # Linux
top       # macOS

# 다른 모델 사용
# policy_chatbot.py에서 model_name 변경
```

#### 네트워크 문제
```bash
# 인터넷 연결 확인
ping google.com

# 프록시 설정 (필요시)
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

### 3. 검색 성능 문제

#### 느린 응답
```python
# 배치 크기 조정
# policy_chatbot.py에서 batch_size 조정

# 인덱스 최적화
# FAISS 인덱스 타입 변경 고려
```

#### 메모리 사용량 높음
```python
# top_k 값 줄이기
results = api.search_policies(query="검색어", top_k=3)

# 불필요한 필드 제외
# 응답에서 필요한 필드만 사용
```

### 4. 로그 확인

#### 서버 로그
```bash
# 상세 로그로 실행
python run_api.py --log-level debug
```

#### 클라이언트 로그
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# API 클라이언트 사용
api = PolicyChatbotAPI()
```

## 📊 모니터링

### 1. 성능 지표

- **응답 시간**: 평균 0.1-0.5초
- **처리량**: 초당 10-50 요청
- **메모리 사용량**: 약 2-4GB
- **정확도**: 유사도 점수 0.7+ 기준

### 2. 헬스 체크

```bash
# 주기적 헬스 체크
while true; do
  curl -s http://localhost:8000/health | jq .
  sleep 30
done
```

### 3. 로그 모니터링

```bash
# 실시간 로그 확인
tail -f api_server.log

# 에러 로그 필터링
grep "ERROR" api_server.log
```

## 🤝 기여하기

### 1. 이슈 리포트

문제가 발생하면 다음 정보와 함께 이슈를 등록해주세요:

- API 엔드포인트
- 요청 파라미터
- 에러 메시지
- 예상 동작
- 실제 동작

### 2. 기능 제안

새로운 기능 제안 시 다음을 포함해주세요:

- 기능 설명
- 사용 사례
- 구현 방법
- 기대 효과

### 3. 코드 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 지원

### 문서

- **API 문서**: http://localhost:8000/docs
- **ReDoc 문서**: http://localhost:8000/redoc
- **프로젝트 README**: README_policy_chatbot.md

### 연락처

- **이슈 트래커**: GitHub Issues
- **문의**: 팀 내부 커뮤니케이션 채널

---

**🏛️ 정책 챗봇 API로 원하는 정책을 쉽게 찾아보세요!** 🚀 