import pandas as pd
import numpy as np
import geopandas as gpd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

print("=== 포천시 상권 분석 데이터 생성 ===")

# 1. 유동인구 데이터 불러오기
print("1. 유동인구 데이터 로딩...")
floating = pd.read_csv('../01_data_analysis/데이터_전처리후/4_유동인구(202201-202505)/gyeonggido_population_concat_2024.csv')
floating_pc = floating[floating['CTY_NM'] == '포천시'].copy()

# 월별, 읍면동별 유동인구 집계
cnt_cols = [col for col in floating_pc.columns if '_CNT' in col]
floating_pc['유동인구'] = floating_pc[cnt_cols].sum(axis=1)

floating_month = floating_pc.groupby(['ADMI_CD', 'YEAR', 'MONTH'])['유동인구'].sum().reset_index()
floating_month['연월'] = floating_month['YEAR'].astype(str) + '-' + floating_month['MONTH'].astype(str).str.zfill(2)
floating_month = floating_month.rename(columns={'ADMI_CD': 'EMD_CD'})
floating_month['EMD_CD'] = floating_month['EMD_CD'].astype(str)

# 2. 공간정보 결합
print("2. 공간정보 결합...")
gdf = gpd.read_file('../01_data_analysis/LSMD_ADM_SECT_UMD_경기/LSMD_ADM_SECT_UMD_41_202506.shp', encoding='cp949')
pocheon_gdf = gdf[gdf['EMD_CD'].astype(str).str.startswith('41650')].copy()
pocheon_gdf['EMD_CD'] = pocheon_gdf['EMD_CD'].astype(str)
pocheon_gdf['lat'] = pocheon_gdf.centroid.y
pocheon_gdf['lon'] = pocheon_gdf.centroid.x

# 유동인구와 공간정보 결합
df_spatial = floating_month.merge(
    pocheon_gdf[['EMD_CD', 'geometry', 'lat', 'lon', 'EMD_NM']], 
    on='EMD_CD', how='left'
)

# 3. 매출 데이터 불러오기 및 결합
print("3. 매출 데이터 로딩...")
sales_retail = pd.read_csv('../01_data_analysis/데이터_전처리후/5_매출현황/지역별_도소매별_평균매출액_현황.csv')
sales_service = pd.read_csv('../01_data_analysis/데이터_전처리후/5_매출현황/지역별_서비스별_평균매출액_현황.csv')
sales_food = pd.read_csv('../01_data_analysis/데이터_전처리후/5_매출현황/지역별_외식별_평균매출액_현황.csv')

# 경기도 데이터만 추출
retail_gg = sales_retail[sales_retail['areaNm'] == '경기'].copy()
service_gg = sales_service[sales_service['areaNm'] == '경기'].copy()
food_gg = sales_food[sales_food['areaNm'] == '경기'].copy()

# 매출액을 숫자로 변환
for df in [retail_gg, service_gg, food_gg]:
    df['arUnitAvrgSlsAmt'] = pd.to_numeric(df['arUnitAvrgSlsAmt'], errors='coerce')

# 4. 매출 데이터를 월별로 확장
print("4. 매출 데이터 월별 확장...")
def expand_yearly_to_monthly(df, year_col='yr', value_col='arUnitAvrgSlsAmt'):
    """연도별 데이터를 월별로 확장 (선형 보간)"""
    expanded_data = []
    
    for induty in df['indutyMlsfcNm'].unique():
        sub_df = df[df['indutyMlsfcNm'] == induty].sort_values(year_col)
        
        for i in range(len(sub_df) - 1):
            year1, year2 = sub_df.iloc[i][year_col], sub_df.iloc[i+1][year_col]
            value1, value2 = sub_df.iloc[i][value_col], sub_df.iloc[i+1][value_col]
            
            # 연도 간 선형 보간으로 월별 값 생성
            for year in range(year1, year2 + 1):
                for month in range(1, 13):
                    if year == year1 and month < 7:  # 첫 해는 7월부터
                        continue
                    if year == year2 and month > 6:  # 마지막 해는 6월까지만
                        continue
                    
                    # 선형 보간
                    if year == year1:
                        ratio = (month - 6) / 6  # 7월=0, 12월=1
                        interpolated_value = value1 + (value2 - value1) * ratio
                    elif year == year2:
                        ratio = month / 6  # 1월=0, 6월=1
                        interpolated_value = value1 + (value2 - value1) * ratio
                    else:
                        # 중간 연도는 선형 보간
                        year_ratio = (year - year1) / (year2 - year1)
                        interpolated_value = value1 + (value2 - value1) * year_ratio
                    
                    expanded_data.append({
                        'year': year,
                        'month': month,
                        'indutyMlsfcNm': induty,
                        'arUnitAvrgSlsAmt': interpolated_value
                    })
    
    return pd.DataFrame(expanded_data)

# 매출 데이터 월별 확장
retail_monthly = expand_yearly_to_monthly(retail_gg)
service_monthly = expand_yearly_to_monthly(service_gg)
food_monthly = expand_yearly_to_monthly(food_gg)

# 5. 매출 데이터 결합
print("5. 매출 데이터 결합...")
df_spatial['year'] = df_spatial['연월'].str[:4].astype(int)
df_spatial['month'] = df_spatial['연월'].str[5:7].astype(int)

def pivot_sales_data(df, prefix):
    """매출 데이터를 피벗하여 업종별 컬럼으로 변환"""
    pivoted = df.pivot_table(
        index=['year', 'month'], 
        columns='indutyMlsfcNm', 
        values='arUnitAvrgSlsAmt',
        aggfunc='mean'
    ).reset_index()
    
    # 컬럼명에 prefix 추가
    pivoted.columns = [f"{prefix}_{col}" if col not in ['year', 'month'] else col 
                      for col in pivoted.columns]
    return pivoted

retail_pivot = pivot_sales_data(retail_monthly, 'retail')
service_pivot = pivot_sales_data(service_monthly, 'service')
food_pivot = pivot_sales_data(food_monthly, 'food')

# 매출 데이터와 유동인구 데이터 결합
df_combined = df_spatial.merge(retail_pivot, on=['year', 'month'], how='left')
df_combined = df_combined.merge(service_pivot, on=['year', 'month'], how='left')
df_combined = df_combined.merge(food_pivot, on=['year', 'month'], how='left')

# 6. 예측 모델 생성
print("6. 예측 모델 생성...")
# 피벗 테이블 생성
pivot_data = df_combined.pivot_table(
    index='EMD_CD', 
    columns='연월', 
    values='유동인구', 
    fill_value=0
)

# 시계열 예측을 위한 데이터 준비
X = pivot_data.values[:, :-1]  # 마지막 달 제외
y = pivot_data.values[:, -1]   # 마지막 달을 타겟으로

# Random Forest 모델 학습
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# 예측
predictions = rf_model.predict(X)

# 7. 대시보드용 데이터 생성
print("7. 대시보드용 데이터 생성...")
# 예측 결과를 데이터프레임에 추가
prediction_df = pd.DataFrame({
    'EMD_CD': pivot_data.index,
    '실제유동인구': y,
    '예측유동인구': predictions
})

# 최종 데이터 생성
dashboard_data = df_combined.merge(prediction_df, on='EMD_CD', how='left')

# 필요한 컬럼만 선택하고 정리
final_columns = [
    'EMD_CD', 'EMD_NM', '연월', 'YEAR', 'MONTH', '유동인구', 
    '실제유동인구', '예측유동인구', 'lat', 'lon'
]

# 매출 관련 컬럼 추가
sales_columns = [col for col in dashboard_data.columns if any(x in col for x in ['retail_', 'service_', 'food_'])]
final_columns.extend(sales_columns)

dashboard_final = dashboard_data[final_columns].copy()

# NaN 값 처리
dashboard_final = dashboard_final.fillna(0)

# 8. CSV 파일로 저장
print("8. CSV 파일 저장...")
dashboard_final.to_csv('상권_분석_데이터.csv', index=False, encoding='utf-8-sig')

print(f"=== 완료 ===")
print(f"생성된 데이터: {dashboard_final.shape}")
print(f"파일 저장: 상권_분석_데이터.csv")
print(f"컬럼 수: {len(dashboard_final.columns)}")
print(f"행 수: {len(dashboard_final)}")
print(f"읍면동 수: {len(dashboard_final['EMD_CD'].unique())}")

# 9. 요약 통계 출력
print("\n=== 요약 통계 ===")
print(f"평균 유동인구: {dashboard_final['유동인구'].mean():,.0f}명")
print(f"평균 예측 유동인구: {dashboard_final['예측유동인구'].mean():,.0f}명")
print(f"예측 정확도 (R²): {rf_model.score(X, y):.3f}")

# 10. 시각화 예시
print("\n=== 시각화 생성 ===")
plt.figure(figsize=(10, 6))
plt.scatter(dashboard_final['실제유동인구'], dashboard_final['예측유동인구'], alpha=0.6)
plt.plot([dashboard_final['실제유동인구'].min(), dashboard_final['실제유동인구'].max()],
         [dashboard_final['실제유동인구'].min(), dashboard_final['실제유동인구'].max()],
         'r--', label='Perfect Prediction')
plt.xlabel('실제 유동인구')
plt.ylabel('예측 유동인구')
plt.title('포천시 유동인구 예측 vs 실제')
plt.legend()
plt.tight_layout()
plt.savefig('prediction_accuracy.png', dpi=300, bbox_inches='tight')
plt.show()

print("시각화 파일 저장: prediction_accuracy.png") 