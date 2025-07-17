"""
트렌드 분석 로직 모듈
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

class TrendAnalyzer:
    def __init__(self):
        self.data_path = "data"
        print("=== 트렌드 분석기 초기화 ===")
    
    def load_data(self):
        """데이터 로딩"""
        print("데이터 로딩 중...")
        
        try:
            # 처리된 데이터 로딩
            self.processed_data = pd.read_csv(f"{self.data_path}/processed_data.csv")
            self.trend_metrics = pd.read_csv(f"{self.data_path}/trend_analysis.csv")
            
            # 카드데이터는 선택적으로 로딩
            try:
                self.card_data = pd.read_csv(f"{self.data_path}/card_analysis.csv")
                if len(self.card_data) == 0:
                    self.card_data = None
            except:
                self.card_data = None
            
            print(f"   - 처리된 데이터: {len(self.processed_data):,}행")
            print(f"   - 트렌드 지표: {len(self.trend_metrics):,}행")
            if self.card_data is not None:
                print(f"   - 카드데이터: {len(self.card_data):,}행")
            
            return True
            
        except Exception as e:
            print(f"   - 데이터 로딩 오류: {e}")
            return False
    
    def analyze_trend_direction(self, data, value_col='유동인구', time_col='연월'):
        """트렌드 방향 분석"""
        # 시간 순서로 정렬
        data = data.sort_values(time_col)
        
        # 선형 회귀로 트렌드 분석
        X = np.arange(len(data)).reshape(-1, 1)
        y = data[value_col].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        slope = model.coef_[0]
        r2 = r2_score(y, model.predict(X))
        
        # 트렌드 방향 판단
        if slope > 0:
            direction = "상승"
        elif slope < 0:
            direction = "하락"
        else:
            direction = "안정"
        
        return {
            'slope': slope,
            'r2': r2,
            'direction': direction,
            'trend_strength': abs(slope)
        }
    
    def calculate_growth_rates(self, data, value_col='유동인구', time_col='연월'):
        """성장률 계산"""
        data = data.sort_values(time_col)
        
        # 전월 대비 성장률
        data['전월대비_성장률'] = data[value_col].pct_change() * 100
        
        # 전년 대비 성장률 (12개월 전과 비교)
        data['전년대비_성장률'] = data.groupby('MONTH')[value_col].pct_change(12) * 100
        
        # 연평균 성장률 (CAGR)
        if len(data) > 1:
            first_value = data[value_col].iloc[0]
            last_value = data[value_col].iloc[-1]
            periods = len(data)
            cagr = ((last_value / first_value) ** (1 / periods) - 1) * 100
        else:
            cagr = 0
        
        return {
            '전월대비_평균': data['전월대비_성장률'].mean(),
            '전년대비_평균': data['전년대비_성장률'].mean(),
            'CAGR': cagr,
            '최근_3개월_평균': data['전월대비_성장률'].tail(3).mean(),
            '최근_6개월_평균': data['전월대비_성장률'].tail(6).mean()
        }
    
    def analyze_seasonality(self, data, value_col='유동인구', time_col='연월'):
        """계절성 분석"""
        data = data.sort_values(time_col)
        
        # 월별 평균 계산
        monthly_avg = data.groupby('MONTH')[value_col].mean()
        
        # 전체 평균 대비 월별 비율
        overall_avg = data[value_col].mean()
        seasonal_ratio = monthly_avg / overall_avg
        
        # 계절성 강도 (표준편차)
        seasonal_strength = seasonal_ratio.std()
        
        # 피크 월과 저점 월 찾기
        peak_month = seasonal_ratio.idxmax()
        trough_month = seasonal_ratio.idxmin()
        
        return {
            'seasonal_strength': seasonal_strength,
            'peak_month': peak_month,
            'trough_month': trough_month,
            'seasonal_ratio': seasonal_ratio.to_dict()
        }
    
    def analyze_volatility(self, data, value_col='유동인구', time_col='연월'):
        """변동성 분석"""
        data = data.sort_values(time_col)
        
        # 이동 표준편차
        data['이동_표준편차'] = data[value_col].rolling(window=3, min_periods=1).std()
        
        # 변동계수
        cv = data[value_col].std() / data[value_col].mean()
        
        # 최대값과 최소값
        max_val = data[value_col].max()
        min_val = data[value_col].min()
        range_val = max_val - min_val
        
        return {
            '변동계수': cv,
            '최대값': max_val,
            '최소값': min_val,
            '범위': range_val,
            '평균_이동_표준편차': data['이동_표준편차'].mean()
        }
    
    def detect_anomalies(self, data, value_col='유동인구', threshold=2):
        """이상치 탐지"""
        data = data.sort_values('연월')
        
        # 이동평균과 표준편차 계산
        data['이동평균'] = data[value_col].rolling(window=3, min_periods=1).mean()
        data['이동_표준편차'] = data[value_col].rolling(window=3, min_periods=1).std()
        
        # Z-score 계산
        data['z_score'] = (data[value_col] - data['이동평균']) / data['이동_표준편차']
        
        # 이상치 탐지
        anomalies = data[abs(data['z_score']) > threshold].copy()
        
        return anomalies
    
    def generate_trend_summary(self, region_data, region_name):
        """지역별 트렌드 요약 생성"""
        if len(region_data) < 2:
            return None
        
        # 트렌드 방향 분석
        trend_info = self.analyze_trend_direction(region_data)
        
        # 성장률 분석
        growth_info = self.calculate_growth_rates(region_data)
        
        # 계절성 분석
        seasonal_info = self.analyze_seasonality(region_data)
        
        # 변동성 분석
        volatility_info = self.analyze_volatility(region_data)
        
        # 이상치 탐지
        anomalies = self.detect_anomalies(region_data)
        
        summary = {
            '지역명': region_name,
            '분석_기간': f"{region_data['연월'].min()} ~ {region_data['연월'].max()}",
            '데이터_포인트': len(region_data),
            '트렌드_방향': trend_info['direction'],
            '트렌드_강도': trend_info['trend_strength'],
            'R²': trend_info['r2'],
            'CAGR': growth_info['CAGR'],
            '최근_3개월_성장률': growth_info['최근_3개월_평균'],
            '계절성_강도': seasonal_info['seasonal_strength'],
            '피크_월': seasonal_info['peak_month'],
            '저점_월': seasonal_info['trough_month'],
            '변동계수': volatility_info['변동계수'],
            '이상치_개수': len(anomalies)
        }
        
        return summary
    
    def analyze_all_regions(self):
        """모든 지역 트렌드 분석"""
        print("모든 지역 트렌드 분석 중...")
        
        summaries = []
        
        for region_cd in self.processed_data['ADMI_CD'].unique():
            region_data = self.processed_data[self.processed_data['ADMI_CD'] == region_cd].copy()
            region_name = region_data['ADMI_NM'].iloc[0]
            
            summary = self.generate_trend_summary(region_data, region_name)
            if summary:
                summaries.append(summary)
        
        self.region_summaries = pd.DataFrame(summaries)
        
        print(f"   - 분석 완료: {len(summaries)}개 지역")
        
        return self.region_summaries
    
    def get_top_performers(self, metric='CAGR', top_n=5):
        """상위 성과 지역 조회"""
        if not hasattr(self, 'region_summaries'):
            self.analyze_all_regions()
        
        # 성장률 기준 상위 지역
        top_growth = self.region_summaries.nlargest(top_n, metric)
        
        # 안정성 기준 상위 지역 (변동계수 낮은 순)
        top_stable = self.region_summaries.nsmallest(top_n, '변동계수')
        
        return {
            '성장률_상위': top_growth,
            '안정성_상위': top_stable
        }
    
    def get_trend_insights(self):
        """트렌드 인사이트 생성"""
        if not hasattr(self, 'region_summaries'):
            self.analyze_all_regions()
        
        insights = []
        
        # 전체 트렌드 분석
        total_data = self.processed_data.groupby('연월')['유동인구'].sum().reset_index()
        # 연월에서 월 추출
        total_data['MONTH'] = total_data['연월'].str[5:7].astype(int)
        overall_trend = self.analyze_trend_direction(total_data)
        
        if overall_trend['direction'] == '상승':
            insights.append("📈 전체적으로 유동인구가 증가하는 추세를 보이고 있습니다.")
        elif overall_trend['direction'] == '하락':
            insights.append("📉 전체적으로 유동인구가 감소하는 추세를 보이고 있습니다.")
        else:
            insights.append("➡️ 전체적으로 유동인구가 안정적인 수준을 유지하고 있습니다.")
        
        # 상위 성과 지역 분석
        top_performers = self.get_top_performers()
        top_growth = top_performers['성장률_상위']
        
        if len(top_growth) > 0:
            best_region = top_growth.iloc[0]
            insights.append(f"🏆 {best_region['지역명']}이(가) 가장 높은 성장률({best_region['CAGR']:.1f}%)을 보이고 있습니다.")
        
        # 계절성 분석
        seasonal_analysis = self.analyze_seasonality(total_data)
        if seasonal_analysis['seasonal_strength'] > 0.1:
            insights.append(f"🌤️ {seasonal_analysis['peak_month']}월에 유동인구가 가장 많고, {seasonal_analysis['trough_month']}월에 가장 적습니다.")
        
        # 변동성 분석
        volatility_analysis = self.analyze_volatility(total_data)
        if volatility_analysis['변동계수'] > 0.2:
            insights.append("📊 유동인구 변동성이 상당히 높아 계절적 요인이나 특별한 이벤트의 영향을 받고 있습니다.")
        
        return insights
    
    def run_analysis(self):
        """전체 분석 실행"""
        print("=== 트렌드 분석 시작 ===")
        
        # 1. 데이터 로딩
        if not self.load_data():
            return None
        
        # 2. 지역별 분석
        region_summaries = self.analyze_all_regions()
        
        # 3. 인사이트 생성
        insights = self.get_trend_insights()
        
        # 4. 결과 저장
        region_summaries.to_csv(f"{self.data_path}/region_trend_summary.csv", index=False, encoding='utf-8-sig')
        
        print("=== 트렌드 분석 완료 ===")
        print("\n=== 주요 인사이트 ===")
        for insight in insights:
            print(f"• {insight}")
        
        return {
            'region_summaries': region_summaries,
            'insights': insights
        }

if __name__ == "__main__":
    analyzer = TrendAnalyzer()
    results = analyzer.run_analysis() 