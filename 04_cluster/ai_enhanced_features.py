# AI 기반 고도화 기능들
import pandas as pd
import numpy as np
import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import warnings
warnings.filterwarnings('ignore')

# NLTK 데이터 다운로드 (최초 실행 시)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class AIEnhancedIdeaAnalyzer:
    """AI 기반 아이디어 분석 및 생성 시스템"""
    
    def __init__(self, csv_path="./data/ideas_sample_1000.csv"):
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path).fillna("")
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # 분석 결과 저장
        self.sentiment_scores = {}
        self.trend_analysis = {}
        self.keyword_analysis = {}
        
        # 초기 분석 수행
        self._perform_initial_analysis()
    
    def _perform_initial_analysis(self):
        """초기 분석 수행"""
        print("AI 기반 분석을 수행 중...")
        
        # 감정 분석
        self._analyze_sentiments()
        
        # 키워드 분석
        self._analyze_keywords()
        
        # 트렌드 분석
        self._analyze_trends()
        
        print("AI 분석 완료!")
    
    def _analyze_sentiments(self):
        """감정 분석 수행"""
        for idx, row in self.df.iterrows():
            text = f"{row['title']} {row['body']}"
            
            # VADER 감정 분석
            sentiment_scores = self.sia.polarity_scores(text)
            
            # TextBlob 감정 분석 (보조)
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            
            self.sentiment_scores[row['idea_id']] = {
                'vader_compound': sentiment_scores['compound'],
                'vader_positive': sentiment_scores['pos'],
                'vader_negative': sentiment_scores['neg'],
                'vader_neutral': sentiment_scores['neu'],
                'textblob_polarity': textblob_polarity,
                'overall_sentiment': self._classify_sentiment(sentiment_scores['compound'])
            }
    
    def _classify_sentiment(self, compound_score: float) -> str:
        """감정 점수를 분류"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_keywords(self):
        """키워드 분석 수행"""
        all_text = ' '.join(self.df['title'].tolist() + self.df['body'].tolist())
        
        # 토큰화 및 정제
        tokens = word_tokenize(all_text.lower())
        tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
        
        # 빈도 분석
        from collections import Counter
        word_freq = Counter(tokens)
        
        # 상위 키워드 추출
        self.keyword_analysis = {
            'top_keywords': word_freq.most_common(20),
            'total_unique_words': len(set(tokens)),
            'most_common_bigrams': self._extract_bigrams(tokens)
        }
    
    def _extract_bigrams(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """바이그램 추출"""
        bigrams = []
        for i in range(len(tokens) - 1):
            bigrams.append((tokens[i], tokens[i + 1]))
        
        from collections import Counter
        bigram_freq = Counter(bigrams)
        return bigram_freq.most_common(10)
    
    def _analyze_trends(self):
        """트렌드 분석 수행"""
        # 카테고리별 인기도 트렌드
        categories = self._extract_categories()
        category_trends = {}
        
        for category in categories:
            category_ideas = self.df[self.df['title'].str.contains(category, case=False, na=False)]
            if len(category_ideas) > 0:
                avg_popularity = category_ideas['좋아요'].sum() / (category_ideas['좋아요'].sum() + category_ideas['싫어요'].sum())
                category_trends[category] = {
                    'count': len(category_ideas),
                    'avg_popularity': avg_popularity,
                    'trend_score': avg_popularity * len(category_ideas)  # 인기도 * 빈도
                }
        
        self.trend_analysis = {
            'category_trends': category_trends,
            'popularity_distribution': self._analyze_popularity_distribution(),
            'sentiment_trends': self._analyze_sentiment_trends()
        }
    
    def _extract_categories(self) -> List[str]:
        """카테고리 추출"""
        categories = ['카페', '반려동물', 'VR', 'AR', '친환경', '헬스', '의료', '교육', 'AI', '로봇', '스마트']
        return categories
    
    def _analyze_popularity_distribution(self) -> Dict:
        """인기도 분포 분석"""
        popularity_scores = []
        for _, row in self.df.iterrows():
            total = row['좋아요'] + row['싫어요']
            if total > 0:
                popularity_scores.append(row['좋아요'] / total)
        
        return {
            'mean': np.mean(popularity_scores),
            'std': np.std(popularity_scores),
            'percentiles': {
                '25%': np.percentile(popularity_scores, 25),
                '50%': np.percentile(popularity_scores, 50),
                '75%': np.percentile(popularity_scores, 75)
            }
        }
    
    def _analyze_sentiment_trends(self) -> Dict:
        """감정 트렌드 분석"""
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for sentiment_data in self.sentiment_scores.values():
            sentiment_counts[sentiment_data['overall_sentiment']] += 1
        
        return sentiment_counts
    
    def generate_idea_suggestions(self, category: Optional[str] = None, 
                                sentiment: Optional[str] = None,
                                num_suggestions: int = 5) -> List[Dict]:
        """AI 기반 아이디어 제안 생성"""
        
        # 필터링 조건
        filtered_df = self.df.copy()
        
        if category:
            filtered_df = filtered_df[filtered_df['title'].str.contains(category, case=False, na=False)]
        
        if sentiment:
            sentiment_ids = [
                idea_id for idea_id, data in self.sentiment_scores.items()
                if data['overall_sentiment'] == sentiment
            ]
            filtered_df = filtered_df[filtered_df['idea_id'].isin(sentiment_ids)]
        
        # 점수 계산 및 정렬
        suggestions = []
        for _, row in filtered_df.iterrows():
            idea_id = row['idea_id']
            
            # 종합 점수 계산
            popularity_score = row['좋아요'] / (row['좋아요'] + row['싫어요']) if (row['좋아요'] + row['싫어요']) > 0 else 0.5
            sentiment_score = self.sentiment_scores[idea_id]['vader_compound']
            
            # 가중 평균 점수
            final_score = 0.7 * popularity_score + 0.3 * sentiment_score
            
            suggestions.append({
                'idea_id': idea_id,
                'title': row['title'],
                'body': row['body'],
                'popularity_score': popularity_score,
                'sentiment_score': sentiment_score,
                'final_score': final_score,
                'sentiment': self.sentiment_scores[idea_id]['overall_sentiment']
            })
        
        # 점수순 정렬 및 상위 결과 반환
        suggestions.sort(key=lambda x: x['final_score'], reverse=True)
        return suggestions[:num_suggestions]
    
    def predict_idea_success(self, title: str, body: str) -> Dict:
        """아이디어 성공 가능성 예측"""
        
        # 텍스트 분석
        text = f"{title} {body}"
        
        # 감정 분석
        sentiment_scores = self.sia.polarity_scores(text)
        
        # 키워드 분석
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
        
        # 트렌드 키워드 매칭
        trend_keywords = [kw for kw, _ in self.keyword_analysis['top_keywords'][:10]]
        trend_matches = sum(1 for token in tokens if token in trend_keywords)
        trend_score = trend_matches / len(tokens) if tokens else 0
        
        # 카테고리 매칭
        categories = self._extract_categories()
        category_matches = []
        for category in categories:
            if category.lower() in text.lower():
                category_matches.append(category)
        
        # 성공 가능성 점수 계산
        sentiment_weight = 0.3
        trend_weight = 0.4
        category_weight = 0.3
        
        sentiment_score = (sentiment_scores['compound'] + 1) / 2  # 0~1 범위로 정규화
        category_score = len(category_matches) / len(categories) if categories else 0
        
        success_probability = (
            sentiment_score * sentiment_weight +
            trend_score * trend_weight +
            category_score * category_weight
        )
        
        return {
            'success_probability': success_probability,
            'sentiment_analysis': {
                'compound': sentiment_scores['compound'],
                'positive': sentiment_scores['pos'],
                'negative': sentiment_scores['neg'],
                'neutral': sentiment_scores['neu']
            },
            'trend_analysis': {
                'trend_score': trend_score,
                'trend_keywords_matched': trend_matches,
                'category_matches': category_matches
            },
            'recommendations': self._generate_recommendations(sentiment_scores, trend_score, category_matches)
        }
    
    def _generate_recommendations(self, sentiment_scores: Dict, trend_score: float, 
                                category_matches: List[str]) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 감정 기반 권장사항
        if sentiment_scores['compound'] < 0:
            recommendations.append("더 긍정적인 톤으로 아이디어를 표현해보세요.")
        
        if sentiment_scores['compound'] > 0.5:
            recommendations.append("긍정적인 감정이 잘 표현되어 있습니다!")
        
        # 트렌드 기반 권장사항
        if trend_score < 0.1:
            recommendations.append("현재 트렌드 키워드를 더 활용해보세요.")
        else:
            recommendations.append("트렌드 키워드가 잘 활용되고 있습니다.")
        
        # 카테고리 기반 권장사항
        if not category_matches:
            recommendations.append("명확한 카테고리를 제시해보세요.")
        else:
            recommendations.append(f"'{', '.join(category_matches)}' 카테고리에 적합한 아이디어입니다.")
        
        return recommendations
    
    def get_market_insights(self) -> Dict:
        """시장 인사이트 제공"""
        
        # 카테고리별 분석
        category_insights = {}
        for category in self._extract_categories():
            category_ideas = self.df[self.df['title'].str.contains(category, case=False, na=False)]
            if len(category_ideas) > 0:
                avg_likes = category_ideas['좋아요'].mean()
                avg_dislikes = category_ideas['싫어요'].mean()
                total_ideas = len(category_ideas)
                
                category_insights[category] = {
                    'total_ideas': total_ideas,
                    'avg_likes': avg_likes,
                    'avg_dislikes': avg_dislikes,
                    'engagement_rate': (avg_likes + avg_dislikes) / total_ideas if total_ideas > 0 else 0,
                    'sentiment_distribution': self._get_category_sentiment_distribution(category_ideas)
                }
        
        # 전체 시장 트렌드
        overall_trends = {
            'most_popular_categories': sorted(
                category_insights.items(), 
                key=lambda x: x[1]['avg_likes'], 
                reverse=True
            )[:5],
            'emerging_categories': self._identify_emerging_categories(),
            'sentiment_overview': self._analyze_sentiment_trends(),
            'keyword_trends': self.keyword_analysis['top_keywords'][:10]
        }
        
        return {
            'category_insights': category_insights,
            'overall_trends': overall_trends,
            'recommendations': self._generate_market_recommendations(category_insights)
        }
    
    def _get_category_sentiment_distribution(self, category_ideas: pd.DataFrame) -> Dict:
        """카테고리별 감정 분포"""
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for _, row in category_ideas.iterrows():
            idea_id = row['idea_id']
            if idea_id in self.sentiment_scores:
                sentiment = self.sentiment_scores[idea_id]['overall_sentiment']
                sentiment_counts[sentiment] += 1
        
        return sentiment_counts
    
    def _identify_emerging_categories(self) -> List[str]:
        """신흥 카테고리 식별"""
        # 간단한 구현: 낮은 빈도지만 높은 인기도를 가진 카테고리
        emerging = []
        categories = self._extract_categories()
        
        for category in categories:
            category_ideas = self.df[self.df['title'].str.contains(category, case=False, na=False)]
            if len(category_ideas) > 0:
                avg_popularity = category_ideas['좋아요'].sum() / (category_ideas['좋아요'].sum() + category_ideas['싫어요'].sum())
                if len(category_ideas) < 5 and avg_popularity > 0.6:  # 적은 수지만 높은 인기도
                    emerging.append(category)
        
        return emerging
    
    def _generate_market_recommendations(self, category_insights: Dict) -> List[str]:
        """시장 기반 권장사항 생성"""
        recommendations = []
        
        # 가장 인기있는 카테고리
        most_popular = max(category_insights.items(), key=lambda x: x[1]['avg_likes'])
        recommendations.append(f"'{most_popular[0]}' 카테고리가 가장 높은 관심을 받고 있습니다.")
        
        # 신흥 카테고리
        emerging = self._identify_emerging_categories()
        if emerging:
            recommendations.append(f"'{', '.join(emerging)}' 카테고리가 신흥 트렌드로 부상하고 있습니다.")
        
        # 감정 분석 기반
        sentiment_trends = self._analyze_sentiment_trends()
        if sentiment_trends['positive'] > sentiment_trends['negative']:
            recommendations.append("전반적으로 긍정적인 아이디어들이 선호되고 있습니다.")
        else:
            recommendations.append("더 긍정적인 접근 방식이 필요할 수 있습니다.")
        
        return recommendations
    
    def export_ai_analysis_report(self) -> Dict:
        """AI 분석 리포트 생성"""
        return {
            'sentiment_analysis': {
                'overall_sentiment_distribution': self._analyze_sentiment_trends(),
                'sentiment_scores': self.sentiment_scores
            },
            'keyword_analysis': self.keyword_analysis,
            'trend_analysis': self.trend_analysis,
            'market_insights': self.get_market_insights(),
            'top_suggestions': self.generate_idea_suggestions(num_suggestions=10),
            'analysis_summary': {
                'total_ideas_analyzed': len(self.df),
                'positive_sentiment_ratio': sum(1 for data in self.sentiment_scores.values() if data['overall_sentiment'] == 'positive') / len(self.sentiment_scores),
                'average_popularity': self.df['좋아요'].sum() / (self.df['좋아요'].sum() + self.df['싫어요'].sum()),
                'most_trending_keywords': [kw for kw, _ in self.keyword_analysis['top_keywords'][:5]]
            }
        }

# 사용 예시
if __name__ == "__main__":
    # AI 분석기 초기화
    analyzer = AIEnhancedIdeaAnalyzer()
    
    # 아이디어 제안 생성
    print("=== AI 기반 아이디어 제안 ===")
    suggestions = analyzer.generate_idea_suggestions(category="AI", sentiment="positive", num_suggestions=3)
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion['title']}")
        print(f"   점수: {suggestion['final_score']:.3f}")
        print(f"   감정: {suggestion['sentiment']}")
        print()
    
    # 성공 가능성 예측
    print("=== 아이디어 성공 가능성 예측 ===")
    test_idea = {
        'title': "AI 기반 반려동물 건강 모니터링 서비스",
        'body': "스마트 센서와 AI를 활용하여 반려동물의 건강 상태를 실시간으로 모니터링하고 이상 징후를 조기에 발견하는 서비스입니다."
    }
    
    prediction = analyzer.predict_idea_success(test_idea['title'], test_idea['body'])
    print(f"성공 가능성: {prediction['success_probability']:.2%}")
    print(f"권장사항: {prediction['recommendations']}")
    
    # 시장 인사이트
    print("\n=== 시장 인사이트 ===")
    insights = analyzer.get_market_insights()
    print(f"가장 인기있는 카테고리: {insights['overall_trends']['most_popular_categories'][0][0]}")
    print(f"신흥 카테고리: {insights['overall_trends']['emerging_categories']}")
    print(f"권장사항: {insights['recommendations']}")
    
    # 분석 리포트
    print("\n=== AI 분석 리포트 요약 ===")
    report = analyzer.export_ai_analysis_report()
    summary = report['analysis_summary']
    print(f"분석된 아이디어 수: {summary['total_ideas_analyzed']}")
    print(f"긍정적 감정 비율: {summary['positive_sentiment_ratio']:.2%}")
    print(f"평균 인기도: {summary['average_popularity']:.3f}")
    print(f"트렌드 키워드: {summary['most_trending_keywords']}") 