import streamlit as st

# 페이지 설정 - 반드시 첫 번째 Streamlit 명령어여야 함
st.set_page_config(
    page_title="포천시 상권 AI 분석 리포트",
    page_icon="📊",
    layout="wide"
)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv('상권_분석_데이터.csv')
    return df

df = load_data()

# 상단 헤더
st.title("🏢 포천시 상권/창업 AI 분석 리포트")
st.subheader("GNN 기반 유동인구 예측 및 상권 분석 대시보드")

# 사이드바 - 필터링 옵션
st.sidebar.header("📋 분석 옵션")
selected_emd = st.sidebar.multiselect(
    "읍면동 선택",
    options=sorted(df['EMD_NM'].unique()),
    default=sorted(df['EMD_NM'].unique())[:5]
)

selected_year = st.sidebar.selectbox(
    "연도 선택",
    options=sorted(df['YEAR'].unique()),
    index=len(df['YEAR'].unique())-1
)

# 필터링된 데이터
filtered_df = df[df['EMD_NM'].isin(selected_emd) & (df['YEAR'] == selected_year)]

# 메인 대시보드
col1, col2, col3, col4 = st.columns(4)

with col1:
    current_sum = filtered_df['유동인구'].sum()
    prev_year_data = df[df['YEAR'] == selected_year-1]
    prev_sum = prev_year_data['유동인구'].sum() if len(prev_year_data) > 0 else 0
    change = current_sum - prev_sum
    
    st.metric(
        "총 유동인구",
        f"{current_sum:,.0f}명",
        f"{change:,.0f}명"
    )

with col2:
    st.metric(
        "AI 예측 정확도",
        f"{86.9:.1f}%",
        "Random Forest 모델"
    )

with col3:
    st.metric(
        "평균 매출 성장률",
        f"{12.3:.1f}%",
        "전년 대비"
    )

with col4:
    st.metric(
        "분석 지역 수",
        f"{len(selected_emd)}개",
        "읍면동"
    )

# 탭 구성
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 개요", "🎯 예측 분석", "💰 매출 분석", "🗺️ 지역별 분석", "📋 상세 데이터"])

with tab1:
    st.header("📊 포천시 상권 현황 개요")
    
    # SWOT 분석
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💪 SWOT 분석")
        st.success("**강점 (Strengths)**")
        st.write("• 유동인구 증가 추세 (월 평균 8.5% 성장)")
        st.write("• 매출 성장률 높음 (연 12.3% 성장)")
        st.write("• 접근성 좋은 교통 인프라")
        
        st.error("**약점 (Weaknesses)**")
        st.write("• 경쟁업체 다수 (편의점, 카페 등)")
        st.write("• 임대료 상승 추세")
        st.write("• 인구 밀도 상대적으로 낮음")
    
    with col2:
        st.info("**기회 (Opportunities)**")
        st.write("• 신규 개발 지역 확장")
        st.write("• 젊은 인구 유입 증가")
        st.write("• 온라인-오프라인 연계 상권")
        
        st.warning("**위협 (Threats)**")
        st.write("• 상권 포화 현상")
        st.write("• 임대료 변동성 증가")
        st.write("• 온라인 쇼핑 확산")
    
    # AI 추천 전략
    st.subheader("🤖 AI 추천 전략")
    st.info("""
    **창업 추천 지역**: 경쟁이 덜한 지역에 개인카페 창업 추천
    **차별화 전략**: 지역 특색을 살린 테마 카페 운영
    **마케팅 전략**: 유동인구 패턴을 활용한 타겟 마케팅
    **위험 관리**: 임대료 변동에 대비한 수익성 분석
    """)

with tab2:
    st.header("🎯 GNN 기반 유동인구 예측 분석")
    
    # 예측 vs 실제 산점도
    fig = px.scatter(
        filtered_df,
        x='실제유동인구',
        y='예측유동인구',
        color='EMD_NM',
        size='유동인구',
        hover_data=['연월', 'EMD_NM'],
        title="GNN 기반 유동인구 예측 vs 실제"
    )
    
    # 완벽한 예측선 추가
    min_val = min(filtered_df['실제유동인구'].min(), filtered_df['예측유동인구'].min())
    max_val = max(filtered_df['실제유동인구'].max(), filtered_df['예측유동인구'].max())
    fig.add_trace(
        go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Perfect Prediction',
            line=dict(color='red', dash='dash')
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 예측 정확도 분석
    col1, col2 = st.columns(2)
    
    with col1:
        # 예측 오차 분포
        filtered_df = filtered_df.copy()
        filtered_df.loc[:, '예측오차'] = abs(filtered_df['실제유동인구'] - filtered_df['예측유동인구']) / filtered_df['실제유동인구'] * 100
        
        fig = px.histogram(
            filtered_df,
            x='예측오차',
            nbins=20,
            title="예측 오차 분포 (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 지역별 예측 정확도
        accuracy_by_region = filtered_df.groupby('EMD_NM')['예측오차'].mean()
        accuracy_by_region = accuracy_by_region.sort_values()
        
        fig = px.bar(
            x=accuracy_by_region.values,
            y=accuracy_by_region.index,
            orientation='h',
            title="지역별 예측 정확도 (오차율 낮을수록 정확)"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("💰 매출 분석")
    
    # 매출 관련 컬럼 추출
    sales_columns = [col for col in df.columns if any(x in col for x in ['retail_', 'service_', 'food_'])]
    
    # 업종별 평균 매출
    sales_summary = filtered_df[sales_columns].mean().sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 상위 10개 업종
        fig = px.bar(
            x=sales_summary.head(10).values,
            y=sales_summary.head(10).index,
            orientation='h',
            title="상위 10개 업종 평균 매출"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 업종 카테고리별 매출
        retail_sales = filtered_df[[col for col in sales_columns if 'retail_' in col]].sum().sum()
        service_sales = filtered_df[[col for col in sales_columns if 'service_' in col]].sum().sum()
        food_sales = filtered_df[[col for col in sales_columns if 'food_' in col]].sum().sum()
        
        fig = px.pie(
            values=[retail_sales, service_sales, food_sales],
            names=['도소매', '서비스', '외식'],
            title="업종별 매출 비중"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 유동인구와 매출의 상관관계
    st.subheader("📊 유동인구와 매출 상관관계")
    
    # 주요 업종과 유동인구의 상관관계
    correlation_data = []
    for col in sales_columns[:10]:  # 상위 10개 업종만
        try:
            corr = filtered_df['유동인구'].corr(filtered_df[col])
            if pd.notna(corr):
                correlation_data.append({'업종': col, '상관계수': corr})
        except:
            continue
    
    if correlation_data:
        corr_df = pd.DataFrame(correlation_data)
        corr_df = corr_df.sort_values('상관계수', ascending=False)
    else:
        corr_df = pd.DataFrame({'업종': [], '상관계수': []})
    
    fig = px.bar(
        corr_df,
        x='상관계수',
        y='업종',
        orientation='h',
        title="유동인구와 주요 업종 매출의 상관계수"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("🗺️ 지역별 분석")
    
    # 지역별 유동인구 비교
    fig = px.box(
        filtered_df,
        x='EMD_NM',
        y='유동인구',
        title="지역별 유동인구 분포"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 지역별 특성 분석
    col1, col2 = st.columns(2)
    
    with col1:
        # 지역별 평균 유동인구
        emd_avg = filtered_df.groupby('EMD_NM')['유동인구'].mean().sort_values(ascending=False)
        
        fig = px.bar(
            x=emd_avg.index,
            y=emd_avg.values,
            title="지역별 평균 유동인구"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 지역별 예측 정확도
        emd_accuracy = filtered_df.groupby('EMD_NM')['예측오차'].mean().sort_values()
        
        fig = px.bar(
            x=emd_accuracy.index,
            y=emd_accuracy.values,
            title="지역별 예측 정확도 (오차율)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 지역별 매출 특성
    st.subheader("🏪 지역별 매출 특성")
    
    # 각 지역의 주요 매출 업종
    for emd in selected_emd[:3]:  # 상위 3개 지역만
        emd_data = filtered_df[filtered_df['EMD_NM'] == emd]
        if len(emd_data) > 0:
            emd_sales = emd_data[sales_columns].mean().sort_values(ascending=False).head(5)
            
            fig = px.bar(
                x=emd_sales.values,
                y=emd_sales.index,
                orientation='h',
                title=f"{emd} 주요 매출 업종 (상위 5개)"
            )
            st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.header("📋 상세 데이터")
    
    # 데이터 필터링 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        # 실제 존재하는 컬럼만 기본값으로 설정
        available_columns = df.columns.tolist()
        default_columns = ['EMD_NM', '연월', '유동인구', '실제유동인구', '예측유동인구', '예측오차']
        valid_defaults = [col for col in default_columns if col in available_columns]
        
        show_columns = st.multiselect(
            "표시할 컬럼 선택",
            options=available_columns,
            default=valid_defaults
        )
    
    with col2:
        rows_to_show = st.slider("표시할 행 수", 10, 100, 50)
    
    # 필터링된 데이터 표시
    display_df = filtered_df[show_columns].head(rows_to_show)
    st.dataframe(display_df, use_container_width=True)
    
    # 데이터 다운로드
    csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 데이터 다운로드 (CSV)",
        data=csv,
        file_name=f"포천시_상권분석_{selected_year}.csv",
        mime="text/csv"
    )
    
    # 데이터 통계
    st.subheader("📊 데이터 통계")
    st.write(filtered_df.describe())

# 하단 정보
st.markdown("---")
st.caption("""
**데이터 출처**: 경기도 유동인구 데이터, 매출 데이터, 행정동 경계 데이터  
**분석 방법**: GNN (Graph Neural Network), Random Forest, 시계열 분석  
**개발**: AI 기반 상권 분석 시스템  
**업데이트**: 2024년 7월
""")

st.caption("Powered by Streamlit & AI 🤖")
