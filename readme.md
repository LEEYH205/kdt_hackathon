# kdt_hackathon

## 프로젝트 개요
- **아이디어 추천/유사도 검색**을 위한 한국어 문장 임베딩 + FAISS 기반 실시간 검색/추천 API
- 입력된 창업/비즈니스 아이디어와 유사한 기존 아이디어를 빠르게 찾아줍니다.

---

## 주요 파일 설명
- `pipeline_mvp.py` : 데이터 전처리, 임베딩, FAISS 인덱스, 실시간 아이디어 추가 및 유사도 검색 함수 정의
- `api_server.py`   : FastAPI 기반 REST API 서버 (POST /submit)
- `data/ideas_sample.csv` : 샘플 아이디어 데이터 (idea_id, title, body)
- `test.ipynb`      : 전체 파이프라인 및 함수 테스트용 Jupyter 노트북

---

## 사용 모델
- [jhgan/ko-sbert-sts](https://huggingface.co/jhgan/ko-sbert-sts) (한국어 SBERT 문장 임베딩)

---

## 실행 방법

### 1. 의존성 설치 (conda 환경 추천)
```bash
pip install sentence-transformers faiss-cpu fastapi pydantic uvicorn
```

### 2. API 서버 실행
```bash
python -m uvicorn api_server:app --reload --port 8000
```
- 서버가 실행되면 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)에서 Swagger UI로 테스트 가능

### 3. API 사용 예시
- **POST /submit**
- 입력(JSON):
```json
{
  "idea_id": "idea_011",
  "title": "전통 카페를 열고 싶어요",
  "body": "한옥 분위기의 커피 전문점 창업을 고민 중입니다."
}
```
- 출력(JSON):
```json
{
  "similar": [
    {
      "idea_id": "idea_001",
      "title": "로봇 바리스타 카페",
      "body": "무인 로봇 팔이 주문과 커피 제조를 담당해 24시간 운영하는 스마트 카페 아이디어.",
      "score": 0.91
    }
  ]
}
```
- `score`는 입력 아이디어와 기존 아이디어 간의 코사인 유사도(0~1)

---

## 참고/특징
- 아이디어 추가 시 실시간으로 FAISS 인덱스와 데이터프레임이 갱신됨
- 0.7 이상 유사도인 아이디어만 반환 (필요시 threshold 조정 가능)
- HDBSCAN 등 클러스터링/탐색적 분석은 test.ipynb 참고

---

## 문의/기여
- pull request, issue, discussion 환영합니다!

## todo
- 실제 데이터 투입 → 군집 재빌드 자동화 → 창업 리포트 PDF