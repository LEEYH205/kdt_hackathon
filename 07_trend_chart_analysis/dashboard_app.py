import streamlit as st
import pandas as pd
from chart_generator import (
    plot_total_population_time_series,
    plot_region_population_time_series,
    plot_region_population_comparison,
    plot_monthly_population_heatmap,
    plot_sales_trend,
    plot_sales_by_category
)

st.set_page_config(
    page_title="경기도 상권 트렌드 차트 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📊 경기도 상권 트렌드 차트 대시보드")
st.caption("유동인구, 매출, 가맹점수 등 시계열/업종별 변화 시각화")

# 데이터 로딩
data_path = "data/processed_data.csv"
df = pd.read_csv(data_path)

# 사이드바: 읍면동 선택
df_regions = sorted(df['ADMI_NM'].unique())
selected_regions = st.sidebar.multiselect(
    "읍면동 선택 (비교)",
    options=df_regions,
    default=df_regions[:5]  # 기본값을 5개로 증가
)

# 탭 구성 (확장)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "전체 유동인구 시계열",
    "읍면동별 유동인구 비교",
    "읍면동별 평균 유동인구",
    "월별 유동인구 히트맵",
    "업종별 매출 트렌드",
    "업종별 매출 비교"
])

with tab1:
    st.subheader("전체 유동인구 시계열 (개선된 버전)")
    st.info("💡 5월에 유동인구가 41.6% 증가하는 뚜렷한 피크 현상이 나타납니다. Y축이 만명 단위로 조정되어 변화가 더 명확하게 보입니다.")
    fig = plot_total_population_time_series(df)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("읍면동별 유동인구 시계열 비교 (개선된 버전)")
    st.info("💡 만명 단위로 표시되어 지역별 차이가 더 명확하게 보입니다. 소흘읍이 가장 높은 유동인구를 보이고 있습니다.")
    fig = plot_region_population_time_series(df, selected_regions)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("읍면동별 평균 유동인구 비교 (개선된 버전)")
    st.info("💡 소흘읍이 가장 큰 유동인구를 보유하고 있습니다. X축이 유동인구 순으로 정렬되어 있어 지역별 차이를 쉽게 비교할 수 있습니다.")
    fig = plot_region_population_comparison(df)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("월별 읍면동 유동인구 히트맵 (개선된 버전)")
    st.info("💡 5월에 모든 지역에서 유동인구가 증가하는 패턴을 확인할 수 있습니다. 색상 강도로 월별 변화를 한눈에 볼 수 있습니다.")
    fig = plot_monthly_population_heatmap(df)
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("업종별 평균 매출 트렌드")
    st.warning("⚠️ 현재 매출 데이터는 업종별 구분이 제한적입니다. 모든 지역이 동일한 매출 값을 가지고 있어 의미있는 분석이 어렵습니다.")
    fig = plot_sales_trend(df)
    st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("업종별 평균 매출 비교")
    st.warning("⚠️ 업종별 매출 데이터 개선이 필요합니다. 현재는 도소매 업종만 데이터가 있으며, 서비스와 외식 업종 데이터가 부족합니다.")
    fig = plot_sales_by_category(df)
    st.plotly_chart(fig, use_container_width=True)

# 주요 인사이트 섹션 추가
st.markdown("---")
st.subheader("✅ 주요 인사이트")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "5월 유동인구 증가율",
        "41.6%",
        "다른 월 평균 대비"
    )

with col2:
    st.metric(
        "최대 유동인구 지역",
        "소흘읍",
        "858만명 (평균)"
    )

with col3:
    st.metric(
        "분석 기간",
        "2024.01~10",
        "10개월"
    )

st.markdown("---")
st.caption("데이터 출처: 경기도 상권 데이터 | Powered by Streamlit & Plotly") 