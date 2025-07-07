# Streamlit 웹 인터페이스
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="아이디어 유사도 측정 시스템",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .idea-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        color: #222222 !important;
        opacity: 1 !important;
    }
    .idea-card h3, .idea-card p, .idea-card span {
        color: #222222 !important;
        opacity: 1 !important;
    }
    .similarity-score {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# API 기본 URL
API_BASE_URL = "http://localhost:8000"

def check_api_connection():
    """API 연결 상태 확인"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_statistics():
    """통계 정보 가져오기"""
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def search_ideas(query, top_k=10, use_popularity=True, min_similarity=0.3):
    """아이디어 검색"""
    try:
        payload = {
            "query": query,
            "top_k": top_k,
            "use_popularity": use_popularity,
            "min_similarity": min_similarity
        }
        response = requests.post(f"{API_BASE_URL}/search", json=payload)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def add_idea(idea_data):
    """새 아이디어 추가"""
    try:
        response = requests.post(f"{API_BASE_URL}/add-idea", json=idea_data)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_all_ideas(limit=50, sort_by="popularity_score"):
    """모든 아이디어 가져오기"""
    try:
        response = requests.get(f"{API_BASE_URL}/ideas?limit={limit}&sort_by={sort_by}")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# 메인 앱
def main():
    st.markdown('<h1 class="main-header">🚀 아이디어 유사도 측정 시스템</h1>', unsafe_allow_html=True)
    
    # API 연결 상태 확인
    if not check_api_connection():
        st.error("❌ API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        st.info("서버 실행 방법: `python api_server_improved.py`")
        return
    
    st.success("✅ API 서버에 성공적으로 연결되었습니다!")
    
    # 사이드바
    st.sidebar.title("🔧 설정")
    page = st.sidebar.selectbox(
        "페이지 선택",
        ["🏠 대시보드", "🔍 아이디어 검색", "➕ 새 아이디어 추가", "📊 분석 리포트", "📋 아이디어 목록"]
    )
    
    if page == "🏠 대시보드":
        show_dashboard()
    elif page == "🔍 아이디어 검색":
        show_search_page()
    elif page == "➕ 새 아이디어 추가":
        show_add_idea_page()
    elif page == "📊 분석 리포트":
        show_analytics_page()
    elif page == "📋 아이디어 목록":
        show_ideas_list_page()

def show_dashboard():
    """대시보드 페이지"""
    st.header("📊 대시보드")
    
    # 통계 정보
    stats = get_statistics()
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 아이디어 수", stats['total_ideas'])
        
        with col2:
            st.metric("평균 좋아요", f"{stats['avg_likes']:.1f}")
        
        with col3:
            st.metric("평균 싫어요", f"{stats['avg_dislikes']:.1f}")
        
        with col4:
            st.metric("가장 인기있는", stats['most_popular'][:20] + "...")
        
        # 인기도 분포 차트
        st.subheader("📈 인기도 분포")
        
        # 샘플 데이터로 차트 생성 (실제로는 API에서 가져와야 함)
        ideas_data = get_all_ideas(limit=100)
        if ideas_data and 'ideas' in ideas_data:
            df = pd.DataFrame(ideas_data['ideas'])
            
            # 인기도 점수 계산
            df['popularity_score'] = df['좋아요'] / (df['좋아요'] + df['싫어요']).replace(0, 1)
            
            # 히스토그램
            fig = px.histogram(
                df, 
                x='popularity_score',
                nbins=20,
                title="아이디어 인기도 분포",
                labels={'popularity_score': '인기도 점수', 'count': '아이디어 수'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # 상위 10개 아이디어
            st.subheader("🏆 인기도 상위 10개 아이디어")
            top_ideas = df.nlargest(10, 'popularity_score')
            
            for i, (_, idea) in enumerate(top_ideas.iterrows(), 1):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{i}. {idea['title']}**")
                    with col2:
                        st.write(f"👍 {idea['좋아요']}")
                    with col3:
                        st.write(f"👎 {idea['싫어요']}")
                    st.progress(idea['popularity_score'])
                    st.divider()

def show_search_page():
    """검색 페이지"""
    st.header("🔍 아이디어 검색")
    
    # 검색 폼
    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input("검색할 아이디어를 입력하세요", placeholder="예: AI 반려동물 훈련 서비스")
        
        with col2:
            top_k = st.number_input("결과 수", min_value=1, max_value=20, value=10)
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            use_popularity = st.checkbox("인기도 점수 반영", value=True)
        
        with col4:
            min_similarity = st.slider("최소 유사도", 0.0, 1.0, 0.3, 0.1)
        
        with col5:
            submitted = st.form_submit_button("🔍 검색", use_container_width=True)
    
    if submitted and query:
        with st.spinner("검색 중..."):
            results = search_ideas(query, top_k, use_popularity, min_similarity)
        
        if results and 'results' in results:
            st.success(f"✅ '{query}'에 대한 {len(results['results'])}개 결과를 찾았습니다!")
            
            # 검색 결과 표시
            for i, idea in enumerate(results['results'], 1):
                with st.container():
                    st.markdown(f"""
                    <div class="idea-card">
                        <h3>{i}. {idea['title']}</h3>
                        <p>{idea['body']}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="similarity-score">유사도: {idea['similarity_score']:.3f}</span>
                            <span>👍 {idea['likes']} | 👎 {idea['dislikes']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("검색 중 오류가 발생했습니다.")

def show_add_idea_page():
    """새 아이디어 추가 페이지"""
    st.header("➕ 새 아이디어 추가")
    
    with st.form("add_idea_form"):
        # 유사 아이디어 결과 개수 선택
        similar_count = st.selectbox("유사 아이디어 결과 개수", [3, 5, 10, 20], index=1)
        title = st.text_input("제목", placeholder="아이디어 제목을 입력하세요")
        body = st.text_area("상세 내용", placeholder="아이디어에 대한 상세한 설명을 입력하세요", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            likes = st.number_input("좋아요 수", min_value=0, value=0)
        with col2:
            dislikes = st.number_input("싫어요 수", min_value=0, value=0)
        
        submitted = st.form_submit_button("➕ 아이디어 추가", use_container_width=True)
    
    if submitted and title:
        # 아이디어 ID 자동 생성: 현재 아이디어 개수 + 1
        ideas_data = get_all_ideas(limit=1000)
        if ideas_data and 'ideas' in ideas_data:
            last_id_num = 0
            for idea in ideas_data['ideas']:
                if 'idea_id' in idea and idea['idea_id'].startswith('idea_'):
                    try:
                        num = int(idea['idea_id'].split('_')[-1])
                        if num > last_id_num:
                            last_id_num = num
                    except:
                        pass
            new_idea_id = f"idea_{last_id_num+1}"
        else:
            new_idea_id = "idea_1"
        idea_data = {
            "idea_id": new_idea_id,
            "title": title,
            "body": body,
            "좋아요": likes,
            "싫어요": dislikes
        }
        
        with st.spinner("아이디어를 추가하는 중..."):
            result = add_idea(idea_data)
        
        if result:
            st.success("✅ 아이디어가 성공적으로 추가되었습니다!")
            
            # 유사 아이디어 표시 (셀렉트박스에서 선택한 개수만큼)
            if 'similar_ideas' in result and result['similar_ideas']:
                st.subheader("🔍 유사한 아이디어들")
                for i, similar in enumerate(result['similar_ideas'][:similar_count], 1):
                    # 유사도 근거: 본문 일부(최대 60자)
                    body_snippet = similar.get('body', '')[:60] + ("..." if len(similar.get('body', '')) > 60 else "")
                    st.markdown(f"""
                    **{i}. [{similar.get('idea_id', '')}] {similar.get('title', '')}**  
                    - 유사도: `{similar.get('similarity_score', similar.get('score', 0)):.3f}`  
                    - 근거: {body_snippet}
                    """)
        else:
            st.error("아이디어 추가 중 오류가 발생했습니다.")

def show_analytics_page():
    """분석 리포트 페이지"""
    st.header("📊 분석 리포트")
    
    # 통계 정보
    stats = get_statistics()
    if not stats:
        st.error("통계 정보를 가져올 수 없습니다.")
        return
    
    # 기본 통계
    st.subheader("📈 기본 통계")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("총 아이디어 수", stats['total_ideas'])
        st.metric("평균 좋아요", f"{stats['avg_likes']:.1f}")
    
    with col2:
        st.metric("평균 싫어요", f"{stats['avg_dislikes']:.1f}")
        st.metric("인기도 범위", f"{stats['popularity_range']['min']:.2f} ~ {stats['popularity_range']['max']:.2f}")
    
    # 아이디어 목록으로 차트 생성
    ideas_data = get_all_ideas(limit=100)
    if ideas_data and 'ideas' in ideas_data:
        df = pd.DataFrame(ideas_data['ideas'])
        df['popularity_score'] = df['좋아요'] / (df['좋아요'] + df['싫어요']).replace(0, 1)
        
        # 좋아요 vs 싫어요 산점도
        st.subheader("📊 좋아요 vs 싫어요 분포")
        fig = px.scatter(
            df,
            x='좋아요',
            y='싫어요',
            size='popularity_score',
            hover_data=['title'],
            title="좋아요 vs 싫어요 산점도 (크기는 인기도 점수)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 카테고리별 분석 (가상 데이터)
        st.subheader("🏷️ 카테고리별 분석")
        
        # 카테고리 추출 (간단한 키워드 기반)
        def extract_category(title):
            title_lower = title.lower()
            if any(word in title_lower for word in ['카페', '커피']):
                return '카페'
            elif any(word in title_lower for word in ['반려동물', '펫']):
                return '반려동물'
            elif any(word in title_lower for word in ['VR', 'AR', '게임']):
                return 'VR/AR'
            elif any(word in title_lower for word in ['친환경', '리필']):
                return '친환경'
            elif any(word in title_lower for word in ['헬스', '의료']):
                return '헬스케어'
            else:
                return '기타'
        
        df['category'] = df['title'].apply(extract_category)
        
        # 카테고리별 통계
        category_stats = df.groupby('category').agg({
            'popularity_score': ['mean', 'count'],
            '좋아요': 'sum',
            '싫어요': 'sum'
        }).round(3)
        
        st.dataframe(category_stats, use_container_width=True)
        
        # 카테고리별 인기도 차트 (멀티 인덱스 → 단일 인덱스 변환)
        category_stats_reset = category_stats.reset_index()
        category_stats_reset.columns = [
            'category',
            'popularity_score_mean',
            'popularity_score_count',
            'likes_sum',
            'dislikes_sum'
        ]
        fig = px.bar(
            category_stats_reset,
            x='category',
            y='popularity_score_mean',
            title="카테고리별 평균 인기도",
            labels={'popularity_score_mean': '평균 인기도', 'category': '카테고리'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_ideas_list_page():
    """아이디어 목록 페이지"""
    st.header("📋 아이디어 목록")
    
    # 필터링 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_by = st.selectbox(
            "정렬 기준",
            ["popularity_score", "좋아요", "싫어요", "title"],
            format_func=lambda x: {
                "popularity_score": "인기도 점수",
                "좋아요": "좋아요 수",
                "싫어요": "싫어요 수",
                "title": "제목"
            }[x]
        )
    
    with col2:
        limit = st.slider("표시할 아이디어 수", 10, 100, 50)
    
    with col3:
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()
    
    # 아이디어 목록 가져오기
    ideas_data = get_all_ideas(limit=limit, sort_by=sort_by)
    
    if ideas_data and 'ideas' in ideas_data:
        df = pd.DataFrame(ideas_data['ideas'])
        
        # 검색 필터
        search_term = st.text_input("🔍 제목으로 검색", placeholder="검색어를 입력하세요")
        if search_term:
            df = df[df['title'].str.contains(search_term, case=False, na=False)]
        
        # 아이디어 목록 표시
        for i, (_, idea) in enumerate(df.iterrows(), 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                
                with col1:
                    st.write(f"**{i}. {idea['title']}**")
                    if pd.notna(idea.get('body')):
                        st.write(idea['body'][:100] + "..." if len(idea['body']) > 100 else idea['body'])
                
                with col2:
                    st.write(f"👍 {idea['좋아요']}")
                
                with col3:
                    st.write(f"👎 {idea['싫어요']}")
                
                with col4:
                    if 'popularity_score' in idea:
                        st.write(f"⭐ {idea['popularity_score']:.2f}")
                
                st.divider()
    else:
        st.error("아이디어 목록을 가져올 수 없습니다.")

if __name__ == "__main__":
    main() 