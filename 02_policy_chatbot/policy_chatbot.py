import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from typing import List, Dict, Tuple
import re

class PolicyChatbot:
    def __init__(self, csv_path: str = "bizinfo.csv", model_name: str = "sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens"):
        """
        정책 챗봇 초기화
        
        Args:
            csv_path: 정책 데이터 CSV 파일 경로
            model_name: 임베딩 모델명
        """
        self.csv_path = csv_path
        self.model_name = model_name
        self.data = None
        self.embeddings = None
        self.index = None
        self.model = None
        
        # 데이터 로드 및 모델 초기화
        self._load_data()
        self._initialize_model()
        self._create_embeddings()
        
    def _load_data(self):
        """CSV 데이터 로드 및 전처리"""
        try:
            self.data = pd.read_csv(self.csv_path)
            print(f"데이터 로드 완료: {len(self.data)}개 정책")
            
            # 결측값 처리
            self.data = self.data.fillna("")
            
            # 텍스트 전처리
            self.data['processed_text'] = self.data.apply(self._preprocess_text, axis=1)
            
        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            raise
    
    def _preprocess_text(self, row: pd.Series) -> str:
        """텍스트 전처리"""
        # 주요 필드들을 결합하여 검색용 텍스트 생성
        fields = [
            str(row['title(공고명)']),
            str(row['body text (공고내용)']),
            str(row['지원대상']),
            str(row['소관기관']),
            str(row['지원분야(대)']),
            str(row['지원분야(중)']),
            str(row['사업수행기관']),
            str(row['문의처']),
            str(row['신청기간']),
            str(row['사업신청방법설명'])
        ]
        
        # 텍스트 결합 및 정리
        combined_text = " ".join(fields)
        
        # 특수문자 제거 및 공백 정리
        combined_text = re.sub(r'[^\w\s가-힣]', ' ', combined_text)
        combined_text = re.sub(r'\s+', ' ', combined_text).strip()
        
        return combined_text
    
    def _initialize_model(self):
        """임베딩 모델 초기화"""
        try:
            print("임베딩 모델 로딩 중...")
            self.model = SentenceTransformer(self.model_name)
            print("모델 로딩 완료")
        except Exception as e:
            print(f"모델 로딩 실패: {e}")
            # 한국어에 특화된 모델로 대체
            self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    
    def _create_embeddings(self):
        """텍스트 임베딩 생성 및 FAISS 인덱스 구축"""
        try:
            print("임베딩 생성 중...")
            
            # 텍스트 임베딩 생성
            texts = self.data['processed_text'].tolist()
            self.embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # FAISS 인덱스 구축
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
            
            # 정규화 (cosine similarity를 위해)
            faiss.normalize_L2(self.embeddings)
            self.index.add(self.embeddings.astype('float32'))
            
            print(f"임베딩 생성 완료: {len(self.embeddings)}개 벡터")
            
        except Exception as e:
            print(f"임베딩 생성 실패: {e}")
            raise
    
    def search_policies(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        정책 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 리스트
        """
        try:
            # 쿼리 전처리
            processed_query = re.sub(r'[^\w\s가-힣]', ' ', query)
            processed_query = re.sub(r'\s+', ' ', processed_query).strip()
            
            # 쿼리 임베딩 생성
            query_embedding = self.model.encode([processed_query])
            faiss.normalize_L2(query_embedding)
            
            # 유사도 검색
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # 결과 포맷팅
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.data):
                    row = self.data.iloc[idx]
                    result = {
                        'rank': i + 1,
                        'similarity_score': float(score),
                        'title': row['title(공고명)'],
                        'body': row['body text (공고내용)'],
                        'target': row['지원대상'],
                        'organization': row['소관기관'],
                        'field_major': row['지원분야(대)'],
                        'field_minor': row['지원분야(중)'],
                        'executing_org': row['사업수행기관'],
                        'contact': row['문의처'],
                        'period': row['신청기간'],
                        'application_method': row['사업신청방법설명']
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"검색 실패: {e}")
            return []
    
    def get_policy_summary(self, query: str) -> str:
        """정책 요약 정보 생성"""
        results = self.search_policies(query, top_k=3)
        
        if not results:
            return "관련 정책을 찾을 수 없습니다."
        
        summary = f"'{query}'와 관련된 정책을 찾았습니다:\n\n"
        
        for result in results:
            summary += f"📋 {result['title']}\n"
            summary += f"🎯 지원대상: {result['target']}\n"
            summary += f"🏢 소관기관: {result['organization']}\n"
            summary += f"📅 신청기간: {result['period']}\n"
            summary += f"📞 문의처: {result['contact']}\n"
            summary += f"📝 신청방법: {result['application_method'][:100]}...\n"
            summary += f"📊 유사도 점수: {result['similarity_score']:.3f}\n"
            summary += "-" * 50 + "\n"
        
        return summary
    
    def save_model(self, path: str = "policy_chatbot_model.pkl"):
        """모델 저장"""
        try:
            model_data = {
                'data': self.data,
                'embeddings': self.embeddings,
                'index': self.index,
                'model_name': self.model_name
            }
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            print(f"모델 저장 완료: {path}")
            
        except Exception as e:
            print(f"모델 저장 실패: {e}")
    
    def load_model(self, path: str = "policy_chatbot_model.pkl"):
        """모델 로드"""
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.data = model_data['data']
            self.embeddings = model_data['embeddings']
            self.index = model_data['index']
            self.model_name = model_data['model_name']
            
            # 모델 재초기화
            self._initialize_model()
            
            print(f"모델 로드 완료: {path}")
            
        except Exception as e:
            print(f"모델 로드 실패: {e}")

# 사용 예시
if __name__ == "__main__":
    # 챗봇 초기화
    chatbot = PolicyChatbot()
    
    # 테스트 검색
    test_queries = [
        "중소기업 기술지원",
        "창업 지원",
        "수출 진출",
        "청년 지원",
        "AI 기술 개발"
    ]
    
    for query in test_queries:
        print(f"\n🔍 검색어: {query}")
        print("=" * 50)
        results = chatbot.search_policies(query, top_k=3)
        
        for result in results:
            print(f"📋 {result['title']}")
            print(f"🎯 {result['target']} | 📊 유사도: {result['similarity_score']:.3f}")
            print("-" * 30) 