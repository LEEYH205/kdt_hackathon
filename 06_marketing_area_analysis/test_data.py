#!/usr/bin/env python3
"""
포천시 상권 분석 데이터 테스트 스크립트
데이터 로딩 및 기본 통계 확인
"""

import pandas as pd
import numpy as np

def test_data():
    print("=== 포천시 상권 분석 데이터 테스트 ===")
    
    try:
        # 데이터 로딩
        df = pd.read_csv('상권_분석_데이터.csv')
        print(f"✅ 데이터 로딩 성공: {df.shape[0]}행, {df.shape[1]}컬럼")
        
        # 기본 정보
        print(f"\n📊 기본 정보:")
        print(f"- 분석 기간: {df['연월'].min()} ~ {df['연월'].max()}")
        print(f"- 분석 지역: {len(df['EMD_NM'].unique())}개 읍면동")
        print(f"- 데이터 포인트: {len(df)}개")
        
        # 유동인구 통계
        print(f"\n👥 유동인구 통계:")
        print(f"- 평균 유동인구: {df['유동인구'].mean():,.0f}명")
        print(f"- 최대 유동인구: {df['유동인구'].max():,.0f}명")
        print(f"- 최소 유동인구: {df['유동인구'].min():,.0f}명")
        
        # 예측 모델 성능
        print(f"\n🤖 예측 모델 성능:")
        if '실제유동인구' in df.columns and '예측유동인구' in df.columns:
            # 예측 오차 계산
            df['예측오차'] = abs(df['실제유동인구'] - df['예측유동인구']) / df['실제유동인구'] * 100
            print(f"- 평균 예측 오차: {df['예측오차'].mean():.2f}%")
            print(f"- 예측 정확도: {100 - df['예측오차'].mean():.1f}%")
        
        # 매출 데이터 확인
        sales_columns = [col for col in df.columns if any(x in col for x in ['retail_', 'service_', 'food_'])]
        print(f"\n💰 매출 데이터:")
        print(f"- 매출 관련 컬럼: {len(sales_columns)}개")
        print(f"- 도소매 업종: {len([col for col in sales_columns if 'retail_' in col])}개")
        print(f"- 서비스 업종: {len([col for col in sales_columns if 'service_' in col])}개")
        print(f"- 외식 업종: {len([col for col in sales_columns if 'food_' in col])}개")
        
        # 지역별 분석
        print(f"\n🗺️ 지역별 분석:")
        emd_stats = df.groupby('EMD_NM')['유동인구'].agg(['mean', 'std']).round(0)
        print("지역별 평균 유동인구 (상위 5개):")
        print(emd_stats.sort_values('mean', ascending=False).head())
        
        # 데이터 품질 확인
        print(f"\n🔍 데이터 품질:")
        print(f"- 결측값: {df.isnull().sum().sum()}개")
        print(f"- 중복값: {df.duplicated().sum()}개")
        
        # 컬럼 목록
        print(f"\n📋 주요 컬럼:")
        main_columns = ['EMD_CD', 'EMD_NM', '연월', '유동인구', '실제유동인구', '예측유동인구', 'lat', 'lon']
        for col in main_columns:
            if col in df.columns:
                print(f"- {col}: {df[col].dtype}")
        
        print(f"\n✅ 데이터 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_data() 