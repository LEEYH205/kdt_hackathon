# 고도화된 아이디어 유사도 측정 시스템
import pandas as pd
import numpy as np
import faiss
import re
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import redis
import asyncio
from collections import defaultdict

class AdvancedIdeaEngine:
    """고도화된 아이디어 유사도 측정 엔진"""
    
    def __init__(self, csv_path="./data/ideas_sample_1000.csv", use_db=True):
        self.csv_path = csv_path
        self.use_db = use_db
        self.embedder = SentenceTransformer("jhgan/ko-sbert-sts")
        self.scaler = MinMaxScaler()
        self.clusterer = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.redis_client = None
        self.db_conn = None
        
        # 초기화
        self._initialize_database()
        self._initialize_redis()
        self._load_data()
        self._initialize_models()
    
    def _initialize_database(self):
        """SQLite 데이터베이스 초기화"""
        if not self.use_db:
            return
            
        self.db_conn = sqlite3.connect('./data/ideas.db', check_same_thread=False)
        cursor = self.db_conn.cursor()
        
        # 아이디어 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ideas (
                idea_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT,
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT,
                tags TEXT,
                embedding BLOB
            )
        ''')
        
        # 사용자 상호작용 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                idea_id TEXT,
                interaction_type TEXT, -- 'like', 'dislike', 'view', 'share'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (idea_id) REFERENCES ideas (idea_id)
            )
        ''')
        
        # 클러스터 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clusters (
                cluster_id INTEGER PRIMARY KEY,
                cluster_name TEXT,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db_conn.commit()
    
    def _initialize_redis(self):
        """Redis 캐시 초기화"""
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()
            print("Redis 연결 성공")
        except:
            print("Redis 연결 실패 - 캐시 기능 비활성화")
            self.redis_client = None
    
    def _load_data(self):
        """데이터 로딩 (CSV 또는 DB)"""
        if self.use_db and self.db_conn:
            # DB에서 데이터 로드
            self.df = pd.read_sql_query("SELECT * FROM ideas", self.db_conn)
            if self.df.empty:
                # DB가 비어있으면 CSV에서 로드하고 DB에 저장
                self.df = pd.read_csv(self.csv_path).fillna("")
                self._save_to_database()
        else:
            # CSV에서 직접 로드
            self.df = pd.read_csv(self.csv_path).fillna("")
        
        # 기본 전처리
        self.df["clean"] = self.df["title"] + " " + self.df["body"]
        self.df["clean"] = self.df["clean"].apply(self._clean_text)
        
        # 인기도 점수 계산
        self.df["popularity_score"] = self.df.apply(
            lambda x: self._calculate_popularity_score(x["좋아요"], x["싫어요"]), axis=1
        )
        
        # 인기도 점수 정규화
        self.df["popularity_normalized"] = self.scaler.fit_transform(
            self.df[["popularity_score"]].values
        ).flatten()
    
    def _save_to_database(self):
        """데이터프레임을 DB에 저장"""
        if not self.use_db or not self.db_conn:
            return
            
        for _, row in self.df.iterrows():
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO ideas 
                (idea_id, title, body, likes, dislikes, category, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['idea_id'],
                row['title'],
                row['body'],
                row['좋아요'],
                row['싫어요'],
                self._extract_category(row['title']),
                self._extract_tags(row['title'], row['body'])
            ))
        
        self.db_conn.commit()
    
    def _initialize_models(self):
        """모델 초기화 (임베딩, 클러스터링, TF-IDF)"""
        print("고도화된 모델 초기화 중...")
        
        # 임베딩 생성
        self.emb = self.embedder.encode(
            self.df["clean"].tolist(), 
            normalize_embeddings=True
        ).astype("float32")
        
        # FAISS 인덱스 생성
        d = self.emb.shape[1]
        self.index = faiss.IndexFlatIP(d)
        self.index.add(self.emb)
        
        # HDBSCAN 클러스터링
        self._perform_clustering()
        
        # TF-IDF 벡터라이저 학습
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df["clean"])
        
        print(f"초기화 완료: {len(self.df)}개 아이디어, {len(np.unique(self.df['cluster']))}개 클러스터")
    
    def _perform_clustering(self):
        """HDBSCAN 클러스터링 수행"""
        min_cluster_size = max(2, int(0.1 * len(self.df)))
        
        self.clusterer = HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=1,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        
        self.df['cluster'] = self.clusterer.fit_predict(self.emb)
        
        # 클러스터 이름 생성
        self._generate_cluster_names()
    
    def _generate_cluster_names(self):
        """클러스터별 이름 자동 생성"""
        cluster_names = {}
        
        for cluster_id in np.unique(self.df['cluster']):
            if cluster_id == -1:
                cluster_names[cluster_id] = "노이즈"
                continue
                
            cluster_data = self.df[self.df['cluster'] == cluster_id]
            
            # TF-IDF로 주요 키워드 추출
            cluster_texts = cluster_data['clean'].tolist()
            tfidf_matrix = self.tfidf_vectorizer.transform(cluster_texts)
            
            # 상위 키워드 추출
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_sums = np.array(tfidf_matrix.sum(axis=0)).flatten()
            top_indices = tfidf_sums.argsort()[-3:][::-1]
            keywords = [feature_names[i] for i in top_indices]
            
            cluster_names[cluster_id] = f"{keywords[0]}_{len(cluster_data)}개"
        
        self.cluster_names = cluster_names
        self.df['cluster_name'] = self.df['cluster'].map(cluster_names)
    
    def _clean_text(self, txt: str) -> str:
        """향상된 텍스트 전처리"""
        txt = re.sub(r"http\S+|www\S+", " ", txt)
        txt = re.sub(r"[^\w가-힣\s]", " ", txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        return txt.lower()
    
    def _calculate_popularity_score(self, likes: int, dislikes: int) -> float:
        """개선된 인기도 점수 계산 (시간 가중치 포함)"""
        total = likes + dislikes
        if total == 0:
            return 0.5
        
        # 기본 점수
        base_score = likes / total
        
        # 시간 가중치 (최근 활동에 더 높은 가중치)
        # 실제 구현에서는 created_at 필드 사용
        time_weight = 1.0
        
        return base_score * time_weight
    
    def _extract_category(self, title: str) -> str:
        """제목에서 카테고리 자동 추출"""
        category_keywords = {
            '카페': ['카페', '커피', '음료', '디저트'],
            '반려동물': ['반려동물', '펫', '강아지', '고양이'],
            'VR/AR': ['VR', 'AR', '가상현실', '증강현실'],
            '친환경': ['친환경', '제로웨이스트', '리필', '재활용'],
            '헬스케어': ['헬스', '의료', '진료', '건강'],
            '교육': ['교육', '학습', '스터디', '강의'],
            '기술': ['AI', '로봇', '스마트', 'IoT']
        }
        
        title_lower = title.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return '기타'
    
    def _extract_tags(self, title: str, body: str) -> str:
        """제목과 본문에서 태그 추출"""
        text = f"{title} {body}".lower()
        
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        keywords = []
        common_words = ['서비스', '카페', '스토어', '센터', '플랫폼', '앱', '시스템']
        
        for word in common_words:
            if word in text:
                keywords.append(word)
        
        return ','.join(keywords[:5])  # 최대 5개 태그
    
    def find_similar_ideas_advanced(self, query: str, user_id: Optional[str] = None,
                                   top_k: int = 10, use_popularity: bool = True,
                                   min_similarity: float = 0.3, 
                                   category_filter: Optional[str] = None,
                                   cluster_filter: Optional[int] = None) -> List[Dict]:
        """고도화된 유사 아이디어 검색"""
        
        # 캐시 확인
        cache_key = f"search:{hash(query)}:{user_id}:{top_k}:{use_popularity}:{category_filter}"
        if self.redis_client:
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
        
        # 기본 검색
        clean_query = self._clean_text(query)
        query_vec = self.embedder.encode([clean_query], normalize_embeddings=True).astype("float32")
        
        # FAISS 검색
        D, I = self.index.search(query_vec, top_k * 3)  # 더 많은 후보
        
        results = []
        for idx, score in zip(I[0], D[0]):
            if score < min_similarity:
                continue
                
            row = self.df.iloc[idx]
            
            # 필터링
            if category_filter and row.get('category') != category_filter:
                continue
            if cluster_filter is not None and row['cluster'] != cluster_filter:
                continue
            
            # 개인화 점수 계산
            personalization_score = 0.0
            if user_id:
                personalization_score = self._calculate_personalization_score(user_id, row['idea_id'])
            
            # 최종 점수 계산
            final_score = score
            if use_popularity:
                popularity_weight = 0.15  # 인기도 가중치 (15%)
                personalization_weight = 0.05  # 개인화 가중치 (5%)
                final_score = (score * (1 - popularity_weight - personalization_weight) + 
                             row["popularity_normalized"] * popularity_weight +
                             personalization_score * personalization_weight)
            
            results.append({
                "idea_id": row["idea_id"],
                "title": row["title"],
                "body": row["body"][:150] + "..." if len(row["body"]) > 150 else row["body"],
                "similarity_score": round(float(score), 3),
                "final_score": round(float(final_score), 3),
                "likes": row["좋아요"],
                "dislikes": row["싫어요"],
                "popularity_score": round(float(row["popularity_score"]), 3),
                "category": row.get('category', '기타'),
                "cluster_name": row.get('cluster_name', '노이즈'),
                "tags": row.get('tags', '').split(',') if row.get('tags') else [],
                "personalization_score": round(float(personalization_score), 3)
            })
            
            if len(results) >= top_k:
                break
        
        # 최종 점수로 정렬
        results.sort(key=lambda x: x["final_score"], reverse=True)
        
        # 캐시 저장
        if self.redis_client:
            self.redis_client.setex(cache_key, 300, json.dumps(results))  # 5분 캐시
        
        return results
    
    def _calculate_personalization_score(self, user_id: str, idea_id: str) -> float:
        """사용자 개인화 점수 계산"""
        if not self.use_db or not self.db_conn:
            return 0.0
        
        cursor = self.db_conn.cursor()
        
        # 사용자의 과거 상호작용 분석
        cursor.execute('''
            SELECT interaction_type, COUNT(*) as count
            FROM user_interactions 
            WHERE user_id = ? AND idea_id = ?
            GROUP BY interaction_type
        ''', (user_id, idea_id))
        
        interactions = dict(cursor.fetchall())
        
        # 점수 계산
        score = 0.0
        if 'like' in interactions:
            score += interactions['like'] * 0.3
        if 'dislike' in interactions:
            score -= interactions['dislike'] * 0.3
        if 'view' in interactions:
            score += interactions['view'] * 0.1
        if 'share' in interactions:
            score += interactions['share'] * 0.2
        
        return min(max(score, 0.0), 1.0)  # 0~1 범위로 제한
    
    def add_user_interaction(self, user_id: str, idea_id: str, interaction_type: str):
        """사용자 상호작용 기록"""
        if not self.use_db or not self.db_conn:
            return
        
        cursor = self.db_conn.cursor()
        cursor.execute('''
            INSERT INTO user_interactions (user_id, idea_id, interaction_type)
            VALUES (?, ?, ?)
        ''', (user_id, idea_id, interaction_type))
        
        # 아이디어의 좋아요/싫어요 업데이트
        if interaction_type in ['like', 'dislike']:
            field = 'likes' if interaction_type == 'like' else 'dislikes'
            cursor.execute(f'''
                UPDATE ideas SET {field} = {field} + 1, updated_at = CURRENT_TIMESTAMP
                WHERE idea_id = ?
            ''', (idea_id,))
        
        self.db_conn.commit()
        
        # 캐시 무효화
        if self.redis_client:
            self.redis_client.flushdb()
    
    def get_cluster_analysis(self) -> Dict:
        """클러스터 분석 결과"""
        cluster_stats = {}
        
        for cluster_id in np.unique(self.df['cluster']):
            cluster_data = self.df[self.df['cluster'] == cluster_id]
            
            cluster_stats[cluster_id] = {
                'name': self.cluster_names.get(cluster_id, '노이즈'),
                'size': len(cluster_data),
                'avg_popularity': cluster_data['popularity_score'].mean(),
                'top_ideas': cluster_data.nlargest(3, 'popularity_score')[['title', 'popularity_score']].to_dict('records'),
                'categories': cluster_data['category'].value_counts().to_dict() if 'category' in cluster_data.columns else {}
            }
        
        return cluster_stats
    
    def get_trending_ideas(self, days: int = 7) -> List[Dict]:
        """트렌딩 아이디어 (최근 활동 기준)"""
        if not self.use_db or not self.db_conn:
            # DB가 없으면 인기도 기준으로 반환
            return self.df.nlargest(10, 'popularity_score')[['idea_id', 'title', 'popularity_score']].to_dict('records')
        
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT i.idea_id, i.title, COUNT(ui.id) as recent_activity
            FROM ideas i
            LEFT JOIN user_interactions ui ON i.idea_id = ui.idea_id
            WHERE ui.created_at >= datetime('now', '-{} days')
            GROUP BY i.idea_id, i.title
            ORDER BY recent_activity DESC
            LIMIT 10
        '''.format(days))
        
        return [{'idea_id': row[0], 'title': row[1], 'activity_count': row[2]} 
                for row in cursor.fetchall()]
    
    def get_recommendations_for_user(self, user_id: str, top_k: int = 10) -> List[Dict]:
        """사용자별 개인화 추천"""
        if not self.use_db or not self.db_conn:
            return []
        
        # 사용자의 과거 상호작용 분석
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT i.category, COUNT(*) as interaction_count
            FROM user_interactions ui
            JOIN ideas i ON ui.idea_id = i.idea_id
            WHERE ui.user_id = ? AND ui.interaction_type IN ('like', 'view')
            GROUP BY i.category
            ORDER BY interaction_count DESC
        ''', (user_id,))
        
        user_preferences = dict(cursor.fetchall())
        
        if not user_preferences:
            # 선호도가 없으면 인기도 기준 추천
            return self.df.nlargest(top_k, 'popularity_score')[['idea_id', 'title', 'popularity_score']].to_dict('records')
        
        # 선호 카테고리 기반 추천
        preferred_category = max(user_preferences.keys(), key=user_preferences.get)
        
        category_ideas = self.df[self.df.get('category', '기타') == preferred_category]
        if len(category_ideas) < top_k:
            # 카테고리 아이디어가 부족하면 전체에서 보충
            remaining = top_k - len(category_ideas)
            other_ideas = self.df[self.df.get('category', '기타') != preferred_category].nlargest(remaining, 'popularity_score')
            category_ideas = pd.concat([category_ideas, other_ideas])
        
        return category_ideas.nlargest(top_k, 'popularity_score')[['idea_id', 'title', 'popularity_score']].to_dict('records')
    
    def export_analytics_report(self) -> Dict:
        """분석 리포트 생성"""
        return {
            'total_ideas': len(self.df),
            'total_clusters': len(np.unique(self.df['cluster'])),
            'popularity_stats': {
                'mean': self.df['popularity_score'].mean(),
                'std': self.df['popularity_score'].std(),
                'min': self.df['popularity_score'].min(),
                'max': self.df['popularity_score'].max()
            },
            'cluster_analysis': self.get_cluster_analysis(),
            'category_distribution': self.df.get('category', pd.Series(['기타'] * len(self.df))).value_counts().to_dict(),
            'trending_ideas': self.get_trending_ideas(),
            'top_ideas_by_popularity': self.df.nlargest(10, 'popularity_score')[['idea_id', 'title', 'popularity_score']].to_dict('records')
        }

# 사용 예시
if __name__ == "__main__":
    # 고도화된 엔진 초기화
    engine = AdvancedIdeaEngine(use_db=False)  # DB 없이 테스트
    
    # 고도화된 검색 테스트
    results = engine.find_similar_ideas_advanced(
        query="AI 반려동물 훈련 서비스",
        user_id="user123",
        top_k=5,
        category_filter="반려동물"
    )
    
    print("=== 고도화된 검색 결과 ===")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   유사도: {result['similarity_score']}, 최종점수: {result['final_score']}")
        print(f"   카테고리: {result['category']}, 클러스터: {result['cluster_name']}")
        print()
    
    # 클러스터 분석
    cluster_analysis = engine.get_cluster_analysis()
    print("=== 클러스터 분석 ===")
    for cluster_id, stats in cluster_analysis.items():
        print(f"클러스터 {cluster_id} ({stats['name']}): {stats['size']}개 아이디어")
    
    # 분석 리포트
    report = engine.export_analytics_report()
    print(f"\n=== 분석 리포트 ===")
    print(f"총 아이디어: {report['total_ideas']}개")
    print(f"총 클러스터: {report['total_clusters']}개")
    print(f"평균 인기도: {report['popularity_stats']['mean']:.3f}") 