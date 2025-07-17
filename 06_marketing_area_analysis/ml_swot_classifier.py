import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# 1. 데이터 로딩
print("=== 머신러닝 기반 SWOT 자동화 ===")
df = pd.read_csv('상권_분석_데이터.csv')

# 2. Feature 엔지니어링 (읍면동별 성장률, 변동성, 평균 유동인구)
df = df.sort_values(['EMD_NM', '연월'])
df['성장률'] = df.groupby('EMD_NM')['유동인구'].pct_change()
df['변동성'] = df.groupby('EMD_NM')['유동인구'].rolling(window=3, min_periods=1).std().reset_index(0, drop=True)
df['평균유동인구'] = df.groupby('EMD_NM')['유동인구'].transform('mean')

# 3. 규칙 기반 SWOT 라벨링 (예시)
def swot_rule(row, g_rank, v_rank, p_rank, n):
    # 성장률 상위 30%: 강점, 하위 30%: 약점
    # 변동성 하위 30%: 기회, 상위 30%: 위협
    if g_rank <= n*0.3:
        return '강점'
    elif g_rank >= n*0.7:
        return '약점'
    elif v_rank <= n*0.3:
        return '기회'
    elif v_rank >= n*0.7:
        return '위협'
    else:
        return '기타'

# 읍면동별 마지막 달만 사용 (최신 데이터)
latest_df = df.sort_values(['EMD_NM', '연월']).groupby('EMD_NM').tail(1).reset_index(drop=True)
n = len(latest_df)
latest_df['g_rank'] = latest_df['성장률'].rank(ascending=False)
latest_df['v_rank'] = latest_df['변동성'].rank(ascending=True)
latest_df['p_rank'] = latest_df['평균유동인구'].rank(ascending=False)
latest_df['swot_label'] = latest_df.apply(lambda row: swot_rule(row, row['g_rank'], row['v_rank'], row['p_rank'], n), axis=1)

# 4. 머신러닝 분류 데이터셋 준비
feature_cols = ['성장률', '변동성', '평균유동인구']
X = latest_df[feature_cols].fillna(0)
y = latest_df['swot_label']

label_counts = y.value_counts()
valid_labels = label_counts[label_counts >= 2].index
X = X[y.isin(valid_labels)]
y = y[y.isin(valid_labels)]

# 5. 학습/테스트 분할 및 모델 학습
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 6. 예측 및 평가
y_pred = clf.predict(X_test)
print("\n=== 분류 성능 ===")
print(classification_report(y_test, y_pred))
print(f"정확도: {accuracy_score(y_test, y_pred):.3f}")

valid_idx = y.index
latest_df_valid = latest_df.loc[valid_idx].reset_index(drop=True)

# 7. 전체 데이터 예측 및 저장
latest_df_valid['swot_pred'] = clf.predict(X)
latest_df_valid[['EMD_NM', '성장률', '변동성', '평균유동인구', 'swot_label', 'swot_pred']].to_csv('swot_ml_result.csv', index=False, encoding='utf-8-sig')
print("\n예측 결과 저장: swot_ml_result.csv")

# 8. 예측 예시 출력
print("\n=== 예측 예시 ===")
print(latest_df_valid[['EMD_NM', 'swot_label', 'swot_pred']].head()) 