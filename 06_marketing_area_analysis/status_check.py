#!/usr/bin/env python3
"""
포천시 상권 분석 시스템 상태 확인
"""

import pandas as pd
import numpy as np
import requests
import time

def check_system_status():
    print("=== 포천시 상권 AI 분석 시스템 상태 확인 ===\n")
    
    # 1. 데이터 파일 확인
    print("1. 📊 데이터 파일 확인...")
    try:
        df = pd.read_csv('상권_분석_데이터.csv')
        print(f"   ✅ 데이터 로딩 성공: {df.shape[0]}행, {df.shape[1]}컬럼")
        print(f"   📅 분석 기간: {df['연월'].min()} ~ {df['연월'].max()}")
        print(f"   🏘️  분석 지역: {len(df['EMD_NM'].unique())}개 읍면동")
    except Exception as e:
        print(f"   ❌ 데이터 로딩 실패: {e}")
        return False
    
    # 2. Streamlit 앱 상태 확인
    print("\n2. 🌐 Streamlit 앱 상태 확인...")
    try:
        response = requests.get('http://localhost:8501', timeout=5)
        if response.status_code == 200:
            print("   ✅ Streamlit 앱 정상 실행 중")
            print("   🌍 접속 URL: http://localhost:8501")
        else:
            print(f"   ⚠️  Streamlit 앱 응답: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Streamlit 앱 연결 실패 - 앱이 실행되지 않았을 수 있습니다")
    except Exception as e:
        print(f"   ❌ 확인 실패: {e}")
    
    # 3. 데이터 품질 확인
    print("\n3. 🔍 데이터 품질 확인...")
    missing_values = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    print(f"   📊 결측값: {missing_values}개")
    print(f"   🔄 중복행: {duplicate_rows}개")
    
    if missing_values == 0 and duplicate_rows == 0:
        print("   ✅ 데이터 품질 양호")
    else:
        print("   ⚠️  데이터 품질 개선 필요")
    
    # 4. 예측 모델 성능 확인
    print("\n4. 🤖 예측 모델 성능 확인...")
    if '예측오차' in df.columns:
        avg_error = df['예측오차'].mean()
        accuracy = 100 - avg_error
        print(f"   📈 평균 예측 오차: {avg_error:.2f}%")
        print(f"   🎯 예측 정확도: {accuracy:.1f}%")
        
        if accuracy > 80:
            print("   ✅ 모델 성능 양호")
        else:
            print("   ⚠️  모델 성능 개선 필요")
    else:
        print("   ⚠️  예측 모델 데이터 없음")
    
    # 5. 시스템 요약
    print("\n" + "="*50)
    print("📋 시스템 요약")
    print("="*50)
    print(f"📊 데이터: {df.shape[0]}행, {df.shape[1]}컬럼")
    print(f"🏘️  지역: {len(df['EMD_NM'].unique())}개 읍면동")
    print(f"📅 기간: {df['연월'].min()} ~ {df['연월'].max()}")
    print(f"🌐 대시보드: http://localhost:8501")
    print(f"📁 작업 디렉토리: {__file__.replace('/status_check.py', '')}")
    
    print("\n✅ 시스템 상태 확인 완료!")
    return True

if __name__ == "__main__":
    check_system_status() 