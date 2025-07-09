# 🚀 정책 챗봇 API 빠른 시작 가이드

5분 만에 정책 챗봇 API를 시작하세요!

## 📋 목차

1. [빠른 설치](#빠른-설치)
2. [서버 실행](#서버-실행)
3. [기본 사용법](#기본-사용법)
4. [테스트](#테스트)
5. [다음 단계](#다음-단계)

## ⚡ 빠른 설치

### 1. 의존성 설치
```bash
cd kdt_hackathon/02_policy_chatbot
pip install -r requirements.txt
```

### 2. 데이터 확인
```bash
ls data/
# gyeonggi_smallbiz_policies_2000_소상공인,경기_20250705.csv 파일이 있어야 함
```

## 🏃 서버 실행

### 개발 모드로 실행 (권장)
```bash
python run_api.py --reload
```

### 기본 실행
```bash
python run_api.py
```

### 다른 포트로 실행
```bash
python run_api.py --port 8080
```

## 🎯 기본 사용법

### 1. 서버 상태 확인
```bash
curl http://localhost:8000/health
```

### 2. 간단한 검색
```bash
curl "http://localhost:8000/search/simple?query=기술지원&top_k=3"
```

### 3. 상세 검색
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "창업 지원",
    "top_k": 5,
    "region_filter": "포천시"
  }'
```

### 4. 정책 요약
```bash
curl -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{"query": "청년 지원"}'
```

### 5. 지역 목록
```bash
curl http://localhost:8000/regions
```

## 🧪 테스트

### 자동 테스트 실행
```bash
python test_api_examples.py
```

### 특정 테스트만 실행
```bash
# 헬스 체크만
python test_api_examples.py --test health

# 검색 테스트만
python test_api_examples.py --test search

# 성능 테스트만
python test_api_examples.py --test performance
```

### 대화형 테스트
```bash
python api_client.py interactive
```

## 📚 Python 클라이언트 사용

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

## 🌐 웹 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 주요 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/health` | GET | 서버 상태 확인 |
| `/search/simple` | GET | 간단한 검색 |
| `/search` | POST | 상세 검색 |
| `/summary` | POST | 정책 요약 |
| `/regions` | GET | 지역 목록 |
| `/` | GET | API 정보 |

## 📊 응답 예시

### 검색 응답
```json
{
  "query": "기술지원",
  "total_results": 3,
  "results": [
    {
      "title": "2025년 스마트물류 기술사업화 협업플랫폼 구축사업",
      "body": "블록체인을 접목한 커피, 스마트 물류...",
      "target": "중소기업",
      "organization": "과학기술정보통신부",
      "similarity_score": 0.668
    }
  ]
}
```

### 헬스 체크 응답
```json
{
  "status": "healthy",
  "model_loaded": true,
  "data_count": 951
}
```

## ⚠️ 문제 해결

### 서버가 시작되지 않는 경우
```bash
# 포트 충돌 확인
lsof -ti:8000 | xargs kill -9

# 다른 포트 사용
python run_api.py --port 8080
```

### 모델 로드 실패
```bash
# 의존성 재설치
pip install -r requirements.txt

# 데이터 파일 확인
ls data/
```

### 검색 결과가 없는 경우
- 검색어 변경
- 필터 조건 완화
- 유사도 임계값 조정

## 📈 성능 지표

- **응답 시간**: 평균 40ms
- **처리량**: 초당 10-50 요청
- **메모리 사용량**: 약 2-4GB
- **정확도**: 유사도 점수 0.7+ 기준

## 🎯 다음 단계

1. **상세 문서 읽기**: [API_README.md](API_README.md)
2. **프로젝트 문서**: [README_policy_chatbot.md](README_policy_chatbot.md)
3. **웹 인터페이스**: `streamlit run streamlit_app.py`
4. **Gradio 인터페이스**: `python gradio_app.py`

## 🆘 도움말

- **API 문서**: http://localhost:8000/docs
- **상세 가이드**: [API_README.md](API_README.md)
- **이슈 리포트**: 팀 내부 커뮤니케이션 채널

---

**🏛️ 이제 정책 챗봇 API를 사용해보세요!** 🚀 