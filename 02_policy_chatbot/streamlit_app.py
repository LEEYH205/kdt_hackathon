import streamlit as st
import pandas as pd
from policy_chatbot import PolicyChatbot
import time

# 페이지 설정
st.set_page_config(
    page_title="정책 챗봇",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .policy-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .similarity-score {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        display: inline-block;
        font-weight: bold;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .stButton > button {
        border-radius: 20px;
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_chatbot():
    """챗봇 로드 (캐싱)"""
    try:
        chatbot = PolicyChatbot()
        return chatbot
    except Exception as e:
        st.error(f"챗봇 로드 실패: {e}")
        return None

def main():
    # 헤더
    st.markdown('<h1 class="main-header">🏛️ 정책 챗봇</h1>', unsafe_allow_html=True)
    st.markdown("### 💡 원하는 정책을 자연어로 검색해보세요!")
    
    # 사이드바
    with st.sidebar:
        st.header("🔧 설정")
        top_k = st.slider("검색 결과 수", min_value=1, max_value=10, value=5)
        similarity_threshold = st.slider("유사도 임계값 (높을수록 정확한 결과만)", 0.0, 1.0, 0.0, 0.05)
        
        st.subheader("📊 필터")
        # 지역명을 텍스트 입력창으로 변경 (하위분류 포함)
        region_filter = st.text_input("지역명 (예: 포천시 → 포천시+경기도+전국 정책 검색)", placeholder="전체 검색시 비워두세요")
        if not region_filter:
            region_filter = None
        target_options = ["중소기업", "소상공인", "창업벤처"]
        target_filter = st.selectbox("지원대상", ["(전체)"] + target_options)
        field_options = ["기술", "경영", "수출", "창업", "내수"]
        field_filter = st.selectbox("지원분야", ["(전체)"] + field_options)

        st.subheader("⚖️ 필터 가중치 설정")
        target_weight = st.slider("지원대상 가중치", 0.0, 1.0, 0.2, 0.05)
        field_weight = st.slider("지원분야 가중치", 0.0, 1.0, 0.2, 0.05)
        
        # 통계 정보
        st.subheader("📈 통계")
        if 'chatbot' in st.session_state and st.session_state.chatbot:
            total_policies = len(st.session_state.chatbot.data)
            st.metric("총 정책 수", total_policies)
            
            # 지원대상별 통계
            target_counts = st.session_state.chatbot.data['지원대상'].value_counts()
            st.write("**지원대상별 분포**")
            for target, count in target_counts.head(5).items():
                st.write(f"• {target}: {count}개")
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 검색 입력
        query = st.text_input(
            "🔍 정책 검색",
            placeholder="예: 중소기업 기술지원, 창업 지원, 수출 진출 등",
            help="원하는 정책을 자연어로 입력하세요"
        )
        
        # 검색 버튼
        search_button = st.button("🔍 검색", use_container_width=True)
        
        # 예시 쿼리
        st.markdown("**💡 검색 예시:**")
        example_queries = [
            "중소기업 기술지원",
            "창업 지원",
            "수출 진출",
            "청년 지원",
            "AI 기술 개발",
            "소상공인 지원",
            "연구개발 지원"
        ]
        
        cols = st.columns(3)
        for i, example in enumerate(example_queries):
            with cols[i % 3]:
                if st.button(example, key=f"example_{i}"):
                    st.session_state.query = example
                    st.rerun()
    
    with col2:
        st.markdown("### 📋 최근 검색")
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
        
        for i, (query_text, timestamp) in enumerate(st.session_state.search_history[-5:]):
            if st.button(f"🔍 {query_text[:20]}...", key=f"history_{i}"):
                st.session_state.query = query_text
                st.rerun()
    
    # 검색 실행
    if search_button or ('query' in st.session_state and st.session_state.query):
        if 'chatbot' not in st.session_state:
            with st.spinner("챗봇을 로딩 중입니다..."):
                st.session_state.chatbot = load_chatbot()
        
        if st.session_state.chatbot:
            search_query = st.session_state.query if 'query' in st.session_state else query
            
            if search_query:
                # 검색 히스토리에 추가
                if 'search_history' not in st.session_state:
                    st.session_state.search_history = []
                
                current_time = time.strftime("%H:%M")
                st.session_state.search_history.append((search_query, current_time))
                
                # 검색 실행
                with st.spinner("정책을 검색 중입니다..."):
                    results = st.session_state.chatbot.search_policies(
                        search_query,
                        top_k=top_k,
                        similarity_threshold=similarity_threshold,
                        region_filter=region_filter if region_filter != "(전체)" else None,
                        target_filter=target_filter if target_filter != "(전체)" else None,
                        field_filter=field_filter if field_filter != "(전체)" else None,
                        target_weight=target_weight,
                        field_weight=field_weight
                    )
                
                # 결과 표시
                if results:
                    st.success(f"✅ '{search_query}'에 대한 {len(results)}개의 정책을 찾았습니다!")
                    
                    for i, result in enumerate(results):
                        with st.expander(f"📋 {result['title']}", expanded=i==0):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**🎯 지원대상:** {result['target']}")
                                st.markdown(f"**🏢 소관기관:** {result['organization']}")
                                st.markdown(f"**📅 신청기간:** {result['period']}")
                                st.markdown(f"**📞 문의처:** {result['contact']}")
                                
                                # 공고내용
                                if result['body']:
                                    st.markdown("**📝 공고내용:**")
                                    st.text_area(
                                        "내용",
                                        value=result['body'][:500] + "..." if len(result['body']) > 500 else result['body'],
                                        height=100,
                                        key=f"body_{i}",
                                        disabled=True
                                    )
                                
                                # 신청방법
                                if result['application_method']:
                                    st.markdown("**📋 신청방법:**")
                                    st.text_area(
                                        "방법",
                                        value=result['application_method'],
                                        height=80,
                                        key=f"method_{i}",
                                        disabled=True
                                    )
                            
                            with col2:
                                st.markdown(f"<div class='similarity-score'>유사도: {result['similarity_score']:.3f}</div>", 
                                           unsafe_allow_html=True)
                                st.markdown(f"**🏷️ 분야:** {result['field_major']} > {result['field_minor']}")
                                st.markdown(f"**🏛️ 수행기관:** {result['executing_org']}")
                                
                                # 상세 정보 버튼
                                if st.button("📊 상세정보", key=f"detail_{i}"):
                                    st.json(result)
                else:
                    st.warning("😔 관련 정책을 찾을 수 없습니다. 다른 키워드로 검색해보세요.")
                    
                    # 추천 검색어
                    st.markdown("**💡 추천 검색어:**")
                    recommendations = ["중소기업", "창업", "기술지원", "수출", "청년"]
                    for rec in recommendations:
                        if st.button(rec, key=f"rec_{rec}"):
                            st.session_state.query = rec
                            st.rerun()
        else:
            st.error("챗봇을 로드할 수 없습니다. 데이터 파일을 확인해주세요.")
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏛️ 정책 챗봇 | AI 기반 정책 검색 시스템</p>
        <p>자연어로 원하는 정책을 쉽게 찾아보세요!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 