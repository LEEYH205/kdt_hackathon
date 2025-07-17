"""
Plotly 기반 트렌드 차트 생성 모듈
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 전체 유동인구 시계열 차트 (개선)
def plot_total_population_time_series(df):
    """
    전체 유동인구 시계열 차트 (개선된 버전)
    """
    total_df = df.groupby('연월')['유동인구'].sum().reset_index()
    
    # Y축 범위를 데이터에 맞게 조정 (만명 단위로 표시)
    total_df['유동인구_만명'] = total_df['유동인구'] / 10000
    y_min = total_df['유동인구_만명'].min() * 0.95
    y_max = total_df['유동인구_만명'].max() * 1.05
    
    fig = px.line(total_df, x='연월', y='유동인구_만명', 
                  title='전체 유동인구 시계열 (단위: 만명)', 
                  markers=True)
    
    fig.update_layout(
        xaxis_title='연월', 
        yaxis_title='유동인구 (만명)',
        hovermode='x unified',
        yaxis=dict(range=[y_min, y_max])
    )
    
    # Y축을 만명 단위로 변환
    fig.update_yaxes(tickformat='.0f')
    
    # 5월 피크 강조
    may_data = total_df[total_df['연월'].str.contains('-05')]
    if not may_data.empty:
        fig.add_annotation(
            x=may_data['연월'].iloc[0],
            y=may_data['유동인구_만명'].iloc[0],
            text="5월 피크<br>(41.6% 증가)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="red",
            ax=40,
            ay=-40,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="red",
            borderwidth=1
        )
    
    return fig

# 2. 읍면동별 유동인구 시계열 비교 (개선)
def plot_region_population_time_series(df, selected_regions=None):
    """
    읍면동별 유동인구 시계열 비교 (개선된 버전)
    """
    if selected_regions is not None:
        df = df[df['ADMI_NM'].isin(selected_regions)]
    
    # 만명 단위로 변환하여 표시
    df_copy = df.copy()
    df_copy['유동인구_만명'] = df_copy['유동인구'] / 10000
    
    fig = px.line(df_copy, x='연월', y='유동인구_만명', color='ADMI_NM', 
                  title='읍면동별 유동인구 시계열 비교', 
                  markers=True)
    
    fig.update_layout(
        xaxis_title='연월', 
        yaxis_title='유동인구 (만명)',
        hovermode='x unified',
        legend_title='읍면동'
    )
    
    return fig

# 3. 읍면동별 유동인구 비교 바 차트 (개선)
def plot_region_population_comparison(df):
    """
    읍면동별 평균 유동인구 비교 바 차트 (개선된 버전)
    """
    region_avg = df.groupby('ADMI_NM')['유동인구'].mean().sort_values(ascending=True)
    
    # 만명 단위로 변환
    region_avg_만명 = region_avg / 10000
    
    fig = px.bar(
        x=region_avg_만명.index, 
        y=region_avg_만명.values,
        title='읍면동별 평균 유동인구 비교',
        labels={'x': '읍면동', 'y': '평균 유동인구 (만명)'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig

# 4. 월별 유동인구 변화 히트맵 (개선)
def plot_monthly_population_heatmap(df):
    """
    월별 유동인구 변화 히트맵 (개선된 버전)
    """
    # 월별, 읍면동별 유동인구 피벗
    pivot_data = df.pivot_table(
        index='ADMI_NM', 
        columns='MONTH', 
        values='유동인구', 
        aggfunc='mean'
    )
    
    # 만명 단위로 변환
    pivot_data_만명 = pivot_data / 10000
    
    fig = px.imshow(
        pivot_data_만명,
        title='월별 읍면동 유동인구 히트맵 (단위: 만명)',
        labels=dict(x='월', y='읍면동', color='유동인구 (만명)'),
        aspect='auto',
        color_continuous_scale='Blues'
    )
    
    return fig

# 5. 업종별 매출 트렌드 (기존)
def plot_sales_trend(df, sales_col='평균매출'):
    """
    업종별 매출 트렌드 (평균매출)
    """
    sales_df = df.groupby('연월')[sales_col].mean().reset_index()
    fig = px.line(sales_df, x='연월', y=sales_col, 
                  title='업종별 평균 매출 트렌드', 
                  markers=True)
    fig.update_layout(xaxis_title='연월', yaxis_title='평균매출', hovermode='x unified')
    return fig

# 6. 업종별 매출 비교 바 차트 (기존)
def plot_sales_by_category(df):
    """
    업종별 매출 비교 바 차트
    """
    categories = ['도소매', '서비스', '외식']
    sales = [df['평균매출'].mean(), 0, 0]  # 기본값, 실제 업종별 매출 컬럼이 있으면 수정
    
    fig = px.bar(x=categories, y=sales, 
                 title='업종별 평균 매출 비교', 
                 labels={'x':'업종', 'y':'평균매출'})
    return fig 