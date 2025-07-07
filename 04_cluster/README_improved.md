# 🚀 개선된 아이디어 유사도 측정 시스템

창업 아이디어의 의미적 유사도를 측정하고, 사용자 피드백(좋아요/싫어요)을 반영한 지능형 추천 시스템입니다.

## ✨ 주요 개선사항

### 1. **사용자 피드백 반영**
- 좋아요/싫어요 비율을 기반으로 한 인기도 점수 계산
- 유사도와 인기도를 결합한 최종 점수 산출
- 인기도 가중치 조절 가능 (기본값: 20%)

### 2. **향상된 텍스트 전처리**
- URL 자동 제거
- 특수문자 필터링 개선
- 한글/영문/숫자만 유지하는 정교한 정규식

### 3. **확장된 API 기능**
- 통계 정보 제공
- 아이디어 목록 조회 및 정렬
- 특정 아이디어 상세 조회
- 모델 저장/로드 기능

### 4. **객체지향적 설계**
- `IdeaSimilarityEngine` 클래스로 캡슐화
- 모듈화된 함수 구조
- 에러 처리 강화

## 📁 파일 구조

```
04_cluster/
├── data/
│   ├── ideas_sample.csv          # 기존 10개 아이디어
│   └── ideas_sample_100.csv      # 새로운 100개 아이디어 (좋아요/싫어요 포함)
│   └── ideas_sample_1000.csv     # 새로운 1000개 아이디어 (좋아요/싫어요 포함)
├── pipeline_mvp.py               # 기존 파이프라인
├── pipeline_mvp_improved.py      # 🆕 개선된 파이프라인
├── api_server.py                 # 기존 API 서버
├── api_server_improved.py        # 🆕 개선된 API 서버
├── test_improved.py              # 🆕 테스트 스크립트
└── README_improved.md            # 🆕 이 파일
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
pip install fastapi uvicorn sentence-transformers faiss-cpu scikit-learn joblib requests
```

### 2. 서버 실행
```bash
cd kdt_hackathon/04_cluster
python api_server_improved.py
```

### 3. 웹 UI 실행
```bash
streamlit run web_interface.py
```

### 4. 테스트 실행
```bash
python test_improved.py
```

## 🔧 API 사용법

### 기본 엔드포인트

#### 1. **헬스 체크**
```bash
GET /health
```

#### 2. **통계 정보**
```bash
GET /statistics
```

#### 3. **유사 아이디어 검색**
```bash
POST /search
{
    "query": "로봇 바리스타 카페",
    "top_k": 10,
    "use_popularity": true,
    "min_similarity": 0.3
}
```

#### 4. **새로운 아이디어 추가**
```bash
POST /add-idea
{
    "idea_id": "new_001",
    "title": "AI 반려동물 훈련사",
    "body": "인공지능을 활용한 반려동물 행동 분석 서비스",
    "좋아요": 25,
    "싫어요": 5
}
```

#### 5. **아이디어 목록 조회**
```bash
GET /ideas?limit=20&sort_by=popularity_score
```

#### 6. **특정 아이디어 조회**
```bash
GET /ideas/idea_001
```

## 📊 인기도 점수 계산 방식

### 공식
```
인기도 점수 = 좋아요 / (좋아요 + 싫어요)
```

### 예시
- 좋아요: 30, 싫어요: 10 → 인기도: 0.75
- 좋아요: 0, 싫어요: 0 → 인기도: 0.5 (중립)
- 좋아요: 5, 싫어요: 45 → 인기도: 0.1

### 최종 점수 계산
```
최종점수 = 유사도 × (1 - 인기도가중치) + 정규화된인기도 × 인기도가중치
```

## 🎯 사용 예시

### Python 클라이언트
```python
import requests

# 서버 상태 확인
response = requests.get("http://localhost:8000/health")
print(response.json())

# 유사 아이디어 검색
search_data = {
    "query": "친환경 카페",
    "top_k": 5,
    "use_popularity": True,
    "min_similarity": 0.3
}

response = requests.post("http://localhost:8000/search", json=search_data)
results = response.json()

for idea in results["results"]:
    print(f"제목: {idea['title']}")
    print(f"유사도: {idea['similarity_score']:.3f}")
    print(f"최종점수: {idea['final_score']:.3f}")
    print(f"좋아요: {idea['likes']}, 싫어요: {idea['dislikes']}")
    print()
```

### cURL 예시
```bash
# 유사 아이디어 검색
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "VR 게임 센터",
       "top_k": 5,
       "use_popularity": true,
       "min_similarity": 0.3
     }'

# 통계 정보 조회
curl "http://localhost:8000/statistics"
```

## 🔍 성능 특징

### 검색 성능
- **FAISS**: 밀리초 단위 고속 검색
- **Sentence Transformers**: 의미적 유사도 측정
- **한국어 최적화**: `jhgan/ko-sbert-sts` 모델 사용

### 확장성
- **실시간 추가**: 새 아이디어 즉시 검색 가능
- **모델 저장**: 학습된 모델 상태 저장/로드
- **배치 처리**: 대량 데이터 처리 지원

## 📈 데이터셋 통계

### ideas_sample_100.csv
- **총 아이디어 수**: 100개
- **평균 좋아요**: ~25개
- **평균 싫어요**: ~20개
- **카테고리**: 카페, 반려동물, VR/AR, 친환경, 헬스케어 등

### 인기도 분포
- **최고 인기도**: VR 체험형 게임 센터 (0.73)
- **최저 인기도**: 도심 곤충 사육 체험관 (0.52)
- **평균 인기도**: 0.55

## 🚀 향후 개선 방향

### 1. **고급 기능**
- [ ] 카테고리별 필터링
- [ ] 시계열 인기도 변화 추적
- [ ] 협업 필터링 추가

### 2. **성능 최적화**
- [ ] 벡터 압축 (PQ, SQ)
- [ ] GPU 가속 지원
- [ ] 캐싱 레이어 추가

### 3. **사용자 경험**
- [ ] 웹 인터페이스
- [ ] 실시간 추천
- [ ] 개인화 설정

## 🐛 문제 해결

### 일반적인 오류

#### 1. **모델 로딩 실패**
```bash
# 의존성 재설치
pip install --upgrade sentence-transformers
```

#### 2. **메모리 부족**
```bash
# 배치 크기 조정
# pipeline_mvp_improved.py에서 BATCH_SIZE 수정
```

#### 3. **API 연결 실패**
```bash
# 서버 상태 확인
curl http://localhost:8000/health
```

## 📝 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**개발자**: AI Study Team  
**버전**: 2.0.0  
**최종 업데이트**: 2024년 12월 