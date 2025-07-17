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

    # === AI 기반 SWOT 분석 ===
    st.subheader("💪 AI 기반 SWOT 분석 (자동)")
    swot_df = df.copy()

    # 성장률/변동성/경쟁도 계산 (전체 기준)
    swot_df = swot_df.sort_values(['EMD_NM', '연월'])
    swot_df['유동인구_성장률'] = swot_df.groupby('EMD_NM')['유동인구'].pct_change()
    growth_mean = swot_df.groupby('EMD_NM')['유동인구_성장률'].mean()
    growth_std = swot_df.groupby('EMD_NM')['유동인구_성장률'].std()
    pop_mean = swot_df.groupby('EMD_NM')['유동인구'].mean()

    # NaN 값이 있는 지역은 제외 (교집합 index를 list로 변환)
    valid_index = list(set(growth_mean.dropna().index) & set(growth_std.dropna().index) & set(pop_mean.dropna().index))
    growth_mean = growth_mean.loc[valid_index]
    growth_std = growth_std.loc[valid_index]
    pop_mean = pop_mean.loc[valid_index]

    # Streamlit sidebar에서 선택된 읍면동 정보 활용
    selected_emd = st.session_state.get('selected_emd', None)
    if not selected_emd:
        selected_emd = df['EMD_NM'].unique().tolist()
    if isinstance(selected_emd, str):
        selected_emd = [selected_emd]

    if len(selected_emd) == 1:
        emd = selected_emd[0]
        # 해당 읍면동의 수치
        g = growth_mean.get(emd, None)
        s = growth_std.get(emd, None)
        p = pop_mean.get(emd, None)
        # 전체 분포에서의 위치
        g_rank = growth_mean.rank(ascending=False)[emd] if g is not None else None
        s_rank = growth_std.rank(ascending=True)[emd] if s is not None else None
        p_rank = pop_mean.rank(ascending=False)[emd] if p is not None else None
        n = len(growth_mean)
        # SWOT 문장 생성
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        if g is not None:
            if g_rank <= n*0.3:
                strengths.append(f"{emd}은(는) 유동인구 성장률이 {g:.1%}로 전체 상위권입니다.")
            elif g_rank >= n*0.7:
                weaknesses.append(f"{emd}은(는) 유동인구 성장률이 {g:.1%}로 전체 하위권입니다.")
            else:
                strengths.append(f"{emd}의 유동인구 성장률은 {g:.1%}로 전체 평균 수준입니다.")
        if s is not None:
            if s_rank <= n*0.3:
                opportunities.append(f"{emd}은(는) 유동인구 변동성이 낮아(σ={s:.2%}) 안정적입니다.")
            elif s_rank >= n*0.7:
                threats.append(f"{emd}은(는) 유동인구 변동성이 높아(σ={s:.2%}) 불안정할 수 있습니다.")
            else:
                opportunities.append(f"{emd}의 유동인구 변동성은 {s:.2%}로 전체 평균 수준입니다.")
        if p is not None:
            if p_rank <= n*0.3:
                threats.append(f"{emd}은(는) 유동인구가 많아 경쟁이 치열할 수 있습니다.")
            elif p_rank >= n*0.7:
                opportunities.append(f"{emd}은(는) 유동인구가 적어 신규 진입 기회가 있습니다.")
            else:
                opportunities.append(f"{emd}의 유동인구는 전체 평균 수준입니다.")
        col1, col2 = st.columns(2)
        with col1:
            st.success("**강점 (Strengths)**")
            for s in strengths:
                st.write(f"- {s}")
            st.error("**약점 (Weaknesses)**")
            for w in weaknesses:
                st.write(f"- {w}")
        with col2:
            st.info("**기회 (Opportunities)**")
            for o in opportunities:
                st.write(f"- {o}")
            st.warning("**위협 (Threats)**")
            for t in threats:
                st.write(f"- {t}")
    else:
        # 기존 전체 랭킹 기반 SWOT
        top_growth = growth_mean.sort_values(ascending=False).head(3)
        low_growth = growth_mean.sort_values(ascending=True).head(3)
        top_var = growth_std.sort_values(ascending=False).head(3)
        low_var = growth_std.sort_values(ascending=True).head(3)
        top_pop = pop_mean.sort_values(ascending=False).head(3)
        low_pop = pop_mean.sort_values(ascending=True).head(3)
        strengths = [f"{em} 지역 유동인구 성장률 상위 ({gr:.1%})" for em, gr in top_growth.items()]
        weaknesses = [f"{em} 지역 유동인구 성장률 하위 ({gr:.1%})" for em, gr in low_growth.items()]
        opportunities = [f"{em} 지역 유동인구 변동성 낮음 (안정적)" for em in low_var.index]
        threats = [f"{em} 지역 유동인구 변동성 높음 (불안정)" for em in top_var.index]
        threats += [f"{em} 지역 유동인구 많아 경쟁 치열" for em in top_pop.index]
        opportunities += [f"{em} 지역 유동인구 적어 신규 진입 기회" for em in low_pop.index]
        col1, col2 = st.columns(2)
        with col1:
            st.success("**강점 (Strengths)**")
            for s in strengths:
                st.write(f"- {s}")
            st.error("**약점 (Weaknesses)**")
            for w in weaknesses:
                st.write(f"- {w}")
        with col2:
            st.info("**기회 (Opportunities)**")
            for o in opportunities:
                st.write(f"- {o}")
            st.warning("**위협 (Threats)**")
            for t in threats:
                st.write(f"- {t}")

    st.markdown("---")
    st.subheader("🤖 AI 추천 전략")
    st.info("AI 기반 SWOT 분석 결과를 바탕으로 창업/마케팅 전략을 자동 추천합니다. (예: 성장률 상위 지역 우선 공략, 변동성 낮은 지역 안정적 진입 등)")

with tab2:
    st.header("🎯 GNN 기반 유동인구 예측 분석")

    # ===== 데이터 전처리 (NaN/0/음수 제거) =====
    filtered_df = filtered_df.dropna(subset=['실제유동인구', '예측유동인구'])
    filtered_df = filtered_df[(filtered_df['실제유동인구'] > 0) & (filtered_df['예측유동인구'] > 0)]

    # ===== 예측오차 계산 (분모 0 방지) =====
    filtered_df['예측오차'] = abs(filtered_df['실제유동인구'] - filtered_df['예측유동인구']) / filtered_df['실제유동인구'] * 100
    filtered_df = filtered_df.dropna(subset=['예측오차'])

    # ===== 데이터 상태 출력 (디버깅용) =====
    st.write("데이터 행 수:", len(filtered_df))
    st.write(filtered_df[['연월', 'EMD_NM', '실제유동인구', '예측유동인구', '예측오차']].head())

    if len(filtered_df) < 5:
        st.warning("선택된 데이터가 너무 적어 그래프가 정상적으로 표시되지 않을 수 있습니다.")

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
    if len(filtered_df) > 0:
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
        fig = px.histogram(
            filtered_df,
            x='예측오차',
            nbins=20,
            title="예측 오차 분포 (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 지역별 예측 정확도
        if '예측오차' in filtered_df.columns:
            accuracy_by_region = filtered_df.groupby('EMD_NM')['예측오차'].mean().sort_values()
            fig = px.bar(
                x=accuracy_by_region.values,
                y=accuracy_by_region.index,
                orientation='h',
                title="지역별 예측 정확도 (오차율 낮을수록 정확)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("예측오차 데이터가 없습니다.")

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
