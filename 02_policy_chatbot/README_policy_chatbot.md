# 🏛️ 정책 챗봇 (Policy Chatbot)

AI 기반 정책 검색 시스템으로, 사용자가 자연어로 원하는 정책을 쉽게 찾을 수 있습니다.
경기도 및 전국의 다양한 정책 정보를 자연어로 검색할 수 있는 AI 기반 정책 챗봇입니다.
Sentence Transformers 임베딩 + FAISS 벡터 검색을 활용하여,
사용자가 원하는 정책을 쉽고 빠르게 찾을 수 있습니다.

## 📋 주요 기능

- **🔍 자연어 검색**: 키워드나 문장으로 정책 검색
- **📊 유사도 기반 매칭**: Sentence Transformers를 활용한 정확한 검색
- **📱 웹 인터페이스**: Streamlit과 Gradio를 통한 사용자 친화적 UI
- **🌐 REST API**: FastAPI 기반 RESTful API 서비스
- **📈 통계 분석**: 정책 데이터 분석 및 시각화
- **💾 모델 저장/로드**: 학습된 모델의 저장 및 재사용

- **정책 데이터 크롤링 및 CSV 저장**
- **정책 임베딩 생성 및 FAISS 인덱스 구축**
- **자연어 검색 (Streamlit/Gradio/CLI/API)**
- **지역명, 지원대상, 지원분야 등 다양한 필터 및 가중치 설정**
- **지역 계층 구조(예: 포천시 → 경기도 → 전국) 기반 검색**
- **정책명/본문에 특정 지역명 포함 여부까지 정밀 필터링**

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 데이터 준비

`data/bizinfo.csv` 파일이 필요합니다. 파일 구조:
```csv
title(공고명),body_text(공고내용),지원대상,소관기관,지원분야(대),지원분야(중),사업수행기관,문의처,신청기간,사업신청방법설명
```

### 3. 실행 방법

#### A. Streamlit 웹 앱 (권장)
```bash
streamlit run streamlit_app.py
```

#### B. Gradio 웹 앱
```bash
python gradio_app.py
```

#### C. 명령줄 테스트
```bash
# 기본 테스트
python test_chatbot.py

# 대화형 테스트
python test_chatbot.py --interactive
```

#### D. Python 코드에서 직접 사용
```python
from policy_chatbot import PolicyChatbot

# 챗봇 초기화
chatbot = PolicyChatbot()

# 정책 검색
results = chatbot.search_policies("중소기업 기술지원", top_k=5)

# 결과 출력
for result in results:
    print(f"제목: {result['title']}")
    print(f"지원대상: {result['target']}")
    print(f"유사도: {result['similarity_score']:.3f}")
    print("-" * 30)
```

#### E. REST API 서버
```bash
# API 서버 실행
python run_api.py

# 또는 개발 모드로 실행
python run_api.py --reload

# 다른 포트로 실행
python run_api.py --port 8080
```

#### F. API 클라이언트 테스트
```bash
# 자동 테스트
python api_client.py

# 대화형 테스트
python api_client.py interactive
```

## 🏗️ 시스템 구조

```
kdt_hackathon/
├── policy_chatbot.py          # 핵심 챗봇 클래스
├── streamlit_app.py           # Streamlit 웹 인터페이스
├── gradio_app.py              # Gradio 웹 인터페이스
├── api_server.py              # FastAPI REST 서버
├── api_client.py              # API 클라이언트 테스트
├── run_api.py                 # API 서버 실행 스크립트
├── test_chatbot.py            # 테스트 스크립트
├── requirements.txt           # 의존성 목록
├── data/
│   └── bizinfo.csv           # 정책 데이터
└── README_policy_chatbot.md   # 이 파일
```

## 🔧 기술 스택

- **AI/ML**: Sentence Transformers, FAISS
- **웹 프레임워크**: Streamlit, Gradio, FastAPI
- **데이터 처리**: Pandas, NumPy
- **검색 엔진**: FAISS (Facebook AI Similarity Search)
- **API**: FastAPI, Uvicorn, Pydantic
- **언어**: Python 3.8+

## 📊 주요 기능 상세

### 1. 정책 검색
- 자연어 쿼리를 벡터로 변환
- FAISS를 통한 고속 유사도 검색
- 유사도 점수 기반 결과 정렬

### 2. 텍스트 전처리
- 특수문자 제거 및 정규화
- 다국어 지원 (한국어/영어)
- 결측값 처리

### 3. 웹 인터페이스
- 직관적인 검색 인터페이스
- 실시간 결과 표시
- 검색 히스토리 관리
- 필터링 옵션

### 4. 통계 분석
- 지원대상별 분포
- 소관기관별 분포
- 지원분야별 분포
- 시각화 차트

### 5. REST API
- FastAPI 기반 RESTful API
- 자동 문서화 (Swagger/ReDoc)
- JSON 기반 요청/응답
- CORS 지원
- 헬스 체크 엔드포인트

## 🎯 사용 예시

### 검색 예시
```
입력: "중소기업 기술지원"
출력: 
- 친환경 히트펌프 및 소재ㆍ부품 중소기업 기술지원사업
- 2025년 2차 블록체인 기반 AI 융합 응용서비스 개발 자금 지원사업
- 2025년 시험인증산업경쟁력 및 신뢰성제고사업

입력: "창업 지원"
출력:
- 2025년 산학협력 우수기업 선정 계획
- [경기] 의정부시 2025년 혁신도시 스타트업 챌린지
- 2025년 연구개발특구 과기특성화대 기술창업투자 경진대회
```

### API 사용 예시
```python
# 챗봇 초기화
chatbot = PolicyChatbot()

# 정책 검색
results = chatbot.search_policies("AI 기술 개발", top_k=3)

# 정책 요약
summary = chatbot.get_policy_summary("중소기업 지원")

# 모델 저장
chatbot.save_model("my_model.pkl")

# 모델 로드
chatbot.load_model("my_model.pkl")
```

### REST API 사용 예시

#### 1. 헬스 체크
```bash
curl http://localhost:8000/health
```

#### 2. 간단한 검색 (GET)
```bash
curl "http://localhost:8000/search/simple?query=중소기업%20기술지원&top_k=3"
```

#### 3. 상세 검색 (POST)
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

#### 4. 정책 요약
```bash
curl -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{"query": "청년 지원"}'
```

#### 5. 지역 목록 조회
```bash
curl http://localhost:8000/regions
```

#### 6. Python 클라이언트 사용
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

## 🌐 API 엔드포인트

### 기본 정보
- **Base URL**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc 문서**: `http://localhost:8000/redoc`

### 엔드포인트 목록

#### 1. 헬스 체크
- **GET** `/health`
- **설명**: 서버 상태 및 모델 로드 상태 확인
- **응답**: `HealthResponse`

#### 2. 정책 검색 (POST)
- **POST** `/search`
- **설명**: 상세한 필터와 가중치를 사용한 정책 검색
- **요청**: `SearchRequest`
- **응답**: `SearchResponse`

#### 3. 정책 검색 (GET)
- **GET** `/search/simple`
- **설명**: 간단한 파라미터로 정책 검색
- **쿼리 파라미터**: `query`, `top_k`, `region`
- **응답**: `SearchResponse`

#### 4. 정책 요약
- **POST** `/summary`
- **설명**: 검색 결과를 요약하여 반환
- **요청**: `SummaryRequest`
- **응답**: `SummaryResponse`

#### 5. 지역 목록
- **GET** `/regions`
- **설명**: 사용 가능한 지역 목록 반환
- **응답**: 지역 목록 및 계층 구조

#### 6. 루트
- **GET** `/`
- **설명**: API 기본 정보
- **응답**: API 버전 및 문서 링크

### 데이터 모델

#### SearchRequest
```json
{
  "query": "string",
  "top_k": 5,
  "similarity_threshold": 0.0,
  "region_filter": "string",
  "target_filter": "string",
  "field_filter": "string",
  "region_weight": 0.3,
  "target_weight": 0.2,
  "field_weight": 0.2
}
```

#### SearchResponse
```json
{
  "query": "string",
  "total_results": 5,
  "results": [
    {
      "title": "string",
      "body": "string",
      "target": "string",
      "organization": "string",
      "field_major": "string",
      "field_minor": "string",
      "executing_org": "string",
      "contact": "string",
      "period": "string",
      "application_method": "string",
      "similarity_score": 0.85
    }
  ],
  "filters_applied": {
    "region_filter": "string",
    "target_filter": "string",
    "field_filter": "string",
    "similarity_threshold": 0.0,
    "weights": {
      "region_weight": 0.3,
      "target_weight": 0.2,
      "field_weight": 0.2
    }
  }
}
```

## ⚙️ 설정 옵션

### 모델 설정
```python
# 다른 임베딩 모델 사용
chatbot = PolicyChatbot(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

### 검색 설정
```python
# 검색 결과 수 조정
results = chatbot.search_policies("검색어", top_k=10)

# 유사도 임계값 설정 (필요시)
filtered_results = [r for r in results if r['similarity_score'] > 0.5]
```

## 🔍 검색 성능 최적화

### 1. 쿼리 최적화
- 구체적인 키워드 사용
- 관련 용어 포함
- 문맥을 고려한 검색어

### 2. 모델 튜닝
- 한국어 특화 모델 사용
- 도메인 특화 파인튜닝
- 앙상블 모델 적용

### 3. 인덱스 최적화
- FAISS 인덱스 타입 선택
- 벡터 차원 최적화
- 메모리 사용량 조정

## 🐛 문제 해결

### 일반적인 문제들

1. **모델 로딩 실패**
   ```bash
   # 인터넷 연결 확인
   # 캐시 삭제 후 재시도
   rm -rf ~/.cache/huggingface/
   ```

2. **메모리 부족**
   ```python
   # 배치 크기 조정
   chatbot.model.encode(texts, batch_size=32)
   ```

3. **검색 결과 없음**
   - 검색어 변경
   - 유사도 임계값 조정
   - 데이터 품질 확인

## 📈 성능 지표

- **검색 속도**: 평균 0.1-0.5초
- **정확도**: 유사도 점수 0.7+ 기준
- **메모리 사용량**: 약 2-4GB
- **지원 언어**: 한국어, 영어

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

문제가 있거나 개선 사항이 있으시면 이슈를 등록해주세요.

---

**🏛️ 정책 챗봇으로 원하는 정책을 쉽게 찾아보세요!** 