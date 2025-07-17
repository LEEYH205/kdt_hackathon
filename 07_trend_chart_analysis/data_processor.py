"""
트렌드 차트 분석을 위한 데이터 전처리 및 통합 모듈
"""

import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class TrendDataProcessor:
    def __init__(self):
        self.data_path = "../01_data_analysis/데이터_전처리후"
        self.output_path = "data"
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_path, exist_ok=True)
        
        print("=== 트렌드 차트 데이터 프로세서 초기화 ===")
    
    def load_floating_population_data(self):
        """유동인구 데이터 로딩"""
        print("1. 유동인구 데이터 로딩...")
        
        # 포천시 전용 데이터 파일 사용
        file_path = os.path.join("../01_data_analysis/data", "pocheon_population_2024.csv")
        
        try:
            df = pd.read_csv(file_path)
            
            print(f"   - 포천시 데이터: {len(df):,}행")
            print(f"   - 기간: {df['YEAR'].min()}년 {df['MONTH'].min()}월 ~ {df['YEAR'].max()}년 {df['MONTH'].max()}월")
            print(f"   - 지역: {df['ADMI_NM'].nunique()}개 행정동")
            
            return df
            
        except Exception as e:
            print(f"   - 오류: {e}")
            return None
    
    def process_floating_population(self, df):
        """유동인구 데이터 전처리"""
        print("2. 유동인구 데이터 전처리...")
        
        if df is None:
            return None
        
        # 유동인구 컬럼 추출 (CNT로 끝나는 컬럼들)
        cnt_cols = [col for col in df.columns if col.endswith('_CNT')]
        
        # 유동인구 합계 계산
        df['유동인구'] = df[cnt_cols].sum(axis=1)
        
        # 월별, 읍면동별 집계
        df['연월'] = df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str).str.zfill(2)
        
        # 읍면동별 월별 유동인구 집계
        floating_monthly = df.groupby(['ADMI_CD', 'ADMI_NM', 'YEAR', 'MONTH', '연월'])['유동인구'].sum().reset_index()
        
        print(f"   - 처리된 데이터: {len(floating_monthly):,}행")
        print(f"   - 기간: {floating_monthly['연월'].min()} ~ {floating_monthly['연월'].max()}")
        
        return floating_monthly
    
    def load_sales_data(self):
        """매출 데이터 로딩"""
        print("3. 매출 데이터 로딩...")
        
        sales_data = {}
        
        # 업종별 매출 데이터 파일
        sales_files = {
            '도소매': '지역별_도소매별_평균매출액_현황.csv',
            '서비스': '지역별_서비스별_평균매출액_현황.csv',
            '외식': '지역별_외식별_평균매출액_현황.csv'
        }
        
        for category, filename in sales_files.items():
            file_path = os.path.join(self.data_path, "5_매출현황", filename)
            
            try:
                df = pd.read_csv(file_path)
                # 경기도 데이터만 필터링
                df_gg = df[df['areaNm'] == '경기'].copy()
                sales_data[category] = df_gg
                
                print(f"   - {category}: {len(df_gg):,}행")
                
            except Exception as e:
                print(f"   - {category} 오류: {e}")
                sales_data[category] = None
        
        return sales_data
    
    def process_sales_data(self, sales_data):
        """매출 데이터 전처리"""
        print("4. 매출 데이터 전처리...")
        
        processed_sales = {}
        
        for category, df in sales_data.items():
            if df is not None:
                # 매출액을 숫자로 변환
                df['arUnitAvrgSlsAmt'] = pd.to_numeric(df['arUnitAvrgSlsAmt'], errors='coerce')
                
                # 연도별, 업종별 평균 매출 계산
                sales_summary = df.groupby(['yr', 'indutyMlsfcNm'])['arUnitAvrgSlsAmt'].mean().reset_index()
                sales_summary['category'] = category
                
                processed_sales[category] = sales_summary
                
                print(f"   - {category}: {len(sales_summary):,}행")
        
        return processed_sales
    
    def load_franchise_data(self):
        """가맹점수 데이터 로딩"""
        print("5. 가맹점수 데이터 로딩...")
        
        franchise_data = {}
        
        # 업종별 가맹점수 데이터 파일
        franchise_files = {
            '도소매': '지역별_도소매별_가맹점수_현황.csv',
            '서비스': '지역별_서비스별_가맹점수_현황.csv',
            '외식': '지역별_외식별_가맹점수_현황.csv'
        }
        
        for category, filename in franchise_files.items():
            file_path = os.path.join(self.data_path, "9_가맹점수현황", filename)
            
            try:
                df = pd.read_csv(file_path)
                franchise_data[category] = df
                
                print(f"   - {category}: {len(df):,}행")
                
            except Exception as e:
                print(f"   - {category} 오류: {e}")
                franchise_data[category] = None
        
        return franchise_data
    
    def process_franchise_data(self, franchise_data):
        """가맹점수 데이터 전처리"""
        print("6. 가맹점수 데이터 전처리...")
        
        processed_franchise = {}
        
        for category, df in franchise_data.items():
            if df is not None:
                # 가맹점수를 숫자로 변환
                df['frcsCnt'] = pd.to_numeric(df['frcsCnt'], errors='coerce')
                
                # 연도별, 업종별 가맹점수 집계
                franchise_summary = df.groupby(['yr', 'indutyMlsfcNm'])['frcsCnt'].sum().reset_index()
                franchise_summary['category'] = category
                
                processed_franchise[category] = franchise_summary
                
                print(f"   - {category}: {len(franchise_summary):,}행")
        
        return processed_franchise
    
    def load_card_data(self):
        """카드데이터 로딩 (샘플)"""
        print("7. 카드데이터 로딩 (샘플)...")
        
        file_path = os.path.join(self.data_path, "6_카드데이터", "카드데이터_병합_202401_조인됨.csv")
        
        try:
            # 대용량 파일이므로 샘플만 읽기
            sample_size = 100000
            df_sample = pd.read_csv(file_path, nrows=sample_size)
            
            # 포천시 데이터만 필터링 (cty_rgn_nm이 '포천시'인 경우)
            df_pocheon = df_sample[df_sample['cty_rgn_nm'] == '포천시'].copy()
            
            print(f"   - 샘플 데이터: {len(df_sample):,}행")
            print(f"   - 포천시 샘플: {len(df_pocheon):,}행")
            
            return df_pocheon
            
        except Exception as e:
            print(f"   - 오류: {e}")
            return None
    
    def process_card_data(self, df):
        """카드데이터 전처리"""
        print("8. 카드데이터 전처리...")
        
        if df is None:
            return None
        
        # 시간대별, 업종별 소비 패턴 분석
        card_summary = df.groupby(['hour', 'card_tpbuz_nm_1', 'card_tpbuz_nm_2']).agg({
            'amt': 'sum',
            'cnt': 'sum'
        }).reset_index()
        
        print(f"   - 처리된 데이터: {len(card_summary):,}행")
        
        return card_summary
    
    def integrate_data(self, floating_data, sales_data, franchise_data, card_data):
        """모든 데이터 통합"""
        print("9. 데이터 통합...")
        
        # 기본 데이터프레임 생성 (유동인구 기준)
        integrated_df = floating_data.copy()
        
        # 매출 데이터 통합
        if sales_data:
            all_sales = []
            for category, df in sales_data.items():
                if df is not None:
                    all_sales.append(df)
            
            if all_sales:
                sales_combined = pd.concat(all_sales, ignore_index=True)
                # 연도별 매출 요약
                sales_summary = sales_combined.groupby('yr')['arUnitAvrgSlsAmt'].mean().reset_index()
                sales_summary.columns = ['YEAR', '평균매출']
                
                # 유동인구 데이터와 연도별로 결합
                integrated_df = integrated_df.merge(sales_summary, on='YEAR', how='left')
        
        # 가맹점수 데이터 통합
        if franchise_data:
            all_franchise = []
            for category, df in franchise_data.items():
                if df is not None:
                    all_franchise.append(df)
            
            if all_franchise:
                franchise_combined = pd.concat(all_franchise, ignore_index=True)
                # 연도별 가맹점수 요약
                franchise_summary = franchise_combined.groupby('yr')['frcsCnt'].sum().reset_index()
                franchise_summary.columns = ['YEAR', '총가맹점수']
                
                # 유동인구 데이터와 연도별로 결합
                integrated_df = integrated_df.merge(franchise_summary, on='YEAR', how='left')
        
        print(f"   - 통합된 데이터: {len(integrated_df):,}행")
        print(f"   - 컬럼 수: {len(integrated_df.columns)}개")
        
        return integrated_df
    
    def calculate_trend_metrics(self, df):
        """트렌드 지표 계산"""
        print("10. 트렌드 지표 계산...")
        
        # 읍면동별로 그룹화하여 지표 계산
        trend_metrics = []
        
        for emd_cd in df['ADMI_CD'].unique():
            emd_data = df[df['ADMI_CD'] == emd_cd].sort_values('연월')
            
            if len(emd_data) < 2:
                continue
            
            # 성장률 계산
            emd_data['유동인구_전월대비'] = emd_data['유동인구'].pct_change() * 100
            emd_data['유동인구_전년대비'] = emd_data.groupby('MONTH')['유동인구'].pct_change(12) * 100
            
            # 변동성 계산
            emd_data['유동인구_변동성'] = emd_data['유동인구'].rolling(window=3, min_periods=1).std()
            
            # 트렌드 방향 (선형 회귀 기울기)
            x = np.arange(len(emd_data))
            y = emd_data['유동인구'].values
            slope = np.polyfit(x, y, 1)[0]
            
            # 최신 데이터
            latest = emd_data.iloc[-1]
            
            trend_metrics.append({
                'ADMI_CD': emd_cd,
                'ADMI_NM': latest['ADMI_NM'],
                '최신_유동인구': latest['유동인구'],
                '평균_유동인구': emd_data['유동인구'].mean(),
                '최대_유동인구': emd_data['유동인구'].max(),
                '최소_유동인구': emd_data['유동인구'].min(),
                '변동성': emd_data['유동인구_변동성'].mean(),
                '트렌드_기울기': slope,
                '성장률_3개월': emd_data['유동인구_전월대비'].tail(3).mean(),
                '성장률_12개월': emd_data['유동인구_전년대비'].tail(12).mean()
            })
        
        trend_df = pd.DataFrame(trend_metrics)
        
        print(f"   - 계산된 지표: {len(trend_df):,}행")
        
        return trend_df
    
    def save_data(self, integrated_df, trend_df, card_data):
        """데이터 저장"""
        print("11. 데이터 저장...")
        
        # 통합 데이터 저장
        integrated_path = os.path.join(self.output_path, "processed_data.csv")
        integrated_df.to_csv(integrated_path, index=False, encoding='utf-8-sig')
        print(f"   - 통합 데이터 저장: {integrated_path}")
        
        # 트렌드 지표 저장
        trend_path = os.path.join(self.output_path, "trend_analysis.csv")
        trend_df.to_csv(trend_path, index=False, encoding='utf-8-sig')
        print(f"   - 트렌드 지표 저장: {trend_path}")
        
        # 카드데이터 저장
        if card_data is not None:
            card_path = os.path.join(self.output_path, "card_analysis.csv")
            card_data.to_csv(card_path, index=False, encoding='utf-8-sig')
            print(f"   - 카드데이터 저장: {card_path}")
        
        print("   - 모든 데이터 저장 완료!")
    
    def run(self):
        """전체 데이터 처리 파이프라인 실행"""
        print("=== 트렌드 차트 데이터 처리 시작 ===")
        
        # 1. 유동인구 데이터 처리
        floating_raw = self.load_floating_population_data()
        floating_processed = self.process_floating_population(floating_raw)
        
        # 2. 매출 데이터 처리
        sales_raw = self.load_sales_data()
        sales_processed = self.process_sales_data(sales_raw)
        
        # 3. 가맹점수 데이터 처리
        franchise_raw = self.load_franchise_data()
        franchise_processed = self.process_franchise_data(franchise_raw)
        
        # 4. 카드데이터 처리
        card_raw = self.load_card_data()
        card_processed = self.process_card_data(card_raw)
        
        # 5. 데이터 통합
        integrated_data = self.integrate_data(floating_processed, sales_processed, franchise_processed, card_processed)
        
        # 6. 트렌드 지표 계산
        trend_metrics = self.calculate_trend_metrics(integrated_data)
        
        # 7. 데이터 저장
        self.save_data(integrated_data, trend_metrics, card_processed)
        
        print("=== 데이터 처리 완료 ===")
        
        return integrated_data, trend_metrics, card_processed

if __name__ == "__main__":
    processor = TrendDataProcessor()
    integrated_data, trend_metrics, card_data = processor.run()
    
    print("\n=== 처리 결과 요약 ===")
    print(f"통합 데이터: {len(integrated_data):,}행")
    print(f"트렌드 지표: {len(trend_metrics):,}행")
    if card_data is not None:
        print(f"카드데이터: {len(card_data):,}행") 