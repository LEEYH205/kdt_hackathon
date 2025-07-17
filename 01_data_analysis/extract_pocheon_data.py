import pandas as pd
import numpy as np
from datetime import datetime

def extract_pocheon_data():
    """
    포천시 유동인구 데이터를 읽어서 요청된 형식으로 변환
    """
    # 원본 데이터 읽기
    print("포천시 유동인구 데이터를 읽는 중...")
    df = pd.read_csv('data/경기도 포천시 유동인구 수.CSV')
    
    print(f"원본 데이터 shape: {df.shape}")
    print(f"컬럼명: {df.columns.tolist()}")
    
    # 데이터 전처리
    # CRTR_YMD를 날짜로 변환
    df['CRTR_YMD'] = pd.to_datetime(df['CRTR_YMD'], format='%Y%m%d')
    df['YEAR'] = df['CRTR_YMD'].dt.year
    df['MONTH'] = df['CRTR_YMD'].dt.month
    df['DAY'] = df['CRTR_YMD'].dt.day
    
    # TMZN_CD를 시간대로 변환 (0-23)
    df['TIME_CD'] = df['TMZN_CD']
    
    # 성별을 FORN_GB로 변환 (MALE -> M, FEMALE -> F)
    df['FORN_GB'] = df['SEX_DV'].map({'MALE': 'M', 'FEMALE': 'F'})
    
    # 연령대별 컬럼 생성
    age_mapping = {
        0: '10', 1: '15', 2: '20', 3: '25', 4: '30', 
        5: '35', 6: '40', 7: '45', 8: '50', 9: '55', 
        10: '60', 11: '65', 12: '70'
    }
    
    # 연령대별 인구수 컬럼 생성
    for age_code, age_str in age_mapping.items():
        # 남성
        male_mask = (df['AGRDE_CLS'] == age_code) & (df['SEX_DV'] == 'MALE')
        df[f'M_{age_str}_CNT'] = np.where(male_mask, df['REVISN_AMBLT_PUL_CNT'], 0)
        
        # 여성
        female_mask = (df['AGRDE_CLS'] == age_code) & (df['SEX_DV'] == 'FEMALE')
        df[f'F_{age_str}_CNT'] = np.where(female_mask, df['REVISN_AMBLT_PUL_CNT'], 0)
    
    # 요청된 형식으로 컬럼 선택 및 정렬
    result_columns = [
        'SGG_CD', 'SGG_NM', 'TMZN_CD', 'FORN_GB',
        'M_10_CNT', 'M_15_CNT', 'M_20_CNT', 'M_25_CNT', 'M_30_CNT', 
        'M_35_CNT', 'M_40_CNT', 'M_45_CNT', 'M_50_CNT', 'M_55_CNT', 
        'M_60_CNT', 'M_65_CNT', 'M_70_CNT',
        'F_10_CNT', 'F_15_CNT', 'F_20_CNT', 'F_25_CNT', 'F_30_CNT', 
        'F_35_CNT', 'F_40_CNT', 'F_45_CNT', 'F_50_CNT', 'F_55_CNT', 
        'F_60_CNT', 'F_65_CNT', 'F_70_CNT',
        'YEAR', 'MONTH', 'DAY'
    ]
    
    # 컬럼명 매핑
    column_mapping = {
        'SGG_CD': 'ADMI_CD',
        'SGG_NM': 'ADMI_NM',
        'TMZN_CD': 'TIME_CD'
    }
    
    # 결과 데이터프레임 생성
    result_df = df[result_columns].copy()
    result_df = result_df.rename(columns=column_mapping)
    
    # CTY_NM 컬럼 추가 (경기도)
    result_df['CTY_NM'] = '경기도'
    
    # 컬럼 순서 재정렬
    final_columns = [
        'ADMI_CD', 'CTY_NM', 'ADMI_NM', 'TIME_CD', 'FORN_GB',
        'M_10_CNT', 'M_15_CNT', 'M_20_CNT', 'M_25_CNT', 'M_30_CNT', 
        'M_35_CNT', 'M_40_CNT', 'M_45_CNT', 'M_50_CNT', 'M_55_CNT', 
        'M_60_CNT', 'M_65_CNT', 'M_70_CNT',
        'F_10_CNT', 'F_15_CNT', 'F_20_CNT', 'F_25_CNT', 'F_30_CNT', 
        'F_35_CNT', 'F_40_CNT', 'F_45_CNT', 'F_50_CNT', 'F_55_CNT', 
        'F_60_CNT', 'F_65_CNT', 'F_70_CNT',
        'YEAR', 'MONTH', 'DAY'
    ]
    
    result_df = result_df[final_columns]
    
    # 중복 제거 및 정렬
    result_df = result_df.drop_duplicates().sort_values(['YEAR', 'MONTH', 'DAY', 'TIME_CD'])
    
    print(f"변환된 데이터 shape: {result_df.shape}")
    print(f"최종 컬럼: {result_df.columns.tolist()}")
    
    # 결과 저장
    output_file = 'data/pocheon_floating_population.csv'
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"포천시 유동인구 데이터가 {output_file}에 저장되었습니다.")
    
    # 데이터 샘플 출력
    print("\n데이터 샘플:")
    print(result_df.head())
    
    # 기본 통계
    print(f"\n기본 통계:")
    print(f"총 레코드 수: {len(result_df)}")
    print(f"기간: {result_df['YEAR'].min()}년 {result_df['MONTH'].min()}월 ~ {result_df['YEAR'].max()}년 {result_df['MONTH'].max()}월")
    print(f"시간대: {result_df['TIME_CD'].min()}시 ~ {result_df['TIME_CD'].max()}시")
    
    return result_df

if __name__ == "__main__":
    extract_pocheon_data() 