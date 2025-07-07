#!/usr/bin/env python3
"""
개선된 아이디어 유사도 측정 시스템 테스트 스크립트
"""

import requests
import json
import time
from typing import Dict, Any

# API 기본 URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """헬스 체크 테스트"""
    print("=== 헬스 체크 테스트 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_statistics():
    """통계 정보 테스트"""
    print("\n=== 통계 정보 테스트 ===")
    try:
        response = requests.get(f"{BASE_URL}/statistics")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"총 아이디어 수: {stats['total_ideas']}")
            print(f"평균 좋아요: {stats['avg_likes']:.2f}")
            print(f"평균 싫어요: {stats['avg_dislikes']:.2f}")
            print(f"가장 인기있는 아이디어: {stats['most_popular']}")
            print(f"가장 인기없는 아이디어: {stats['least_popular']}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search_similar_ideas():
    """유사 아이디어 검색 테스트"""
    print("\n=== 유사 아이디어 검색 테스트 ===")
    
    test_queries = [
        "로봇 바리스타 카페",
        "반려동물 미용실",
        "VR 게임 센터",
        "친환경 리필 스토어",
        "모바일 헬스 진료"
    ]
    
    for query in test_queries:
        print(f"\n검색어: '{query}'")
        try:
            payload = {
                "query": query,
                "top_k": 5,
                "use_popularity": True,
                "min_similarity": 0.3
            }
            
            response = requests.post(f"{BASE_URL}/search", json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"검색된 결과 수: {result['total_found']}")
                
                for i, idea in enumerate(result['results'][:3], 1):
                    print(f"  {i}. {idea['title']}")
                    print(f"     유사도: {idea['similarity_score']:.3f}")
                    print(f"     최종점수: {idea['final_score']:.3f}")
                    print(f"     좋아요: {idea['likes']}, 싫어요: {idea['dislikes']}")
            
            time.sleep(0.5)  # API 호출 간격
            
        except Exception as e:
            print(f"Error: {e}")

def test_add_new_idea():
    """새로운 아이디어 추가 테스트"""
    print("\n=== 새로운 아이디어 추가 테스트 ===")
    
    test_ideas = [
        {
            "idea_id": "test_001",
            "title": "AI 반려동물 훈련사",
            "body": "인공지능을 활용한 반려동물 행동 분석 및 맞춤형 훈련 서비스",
            "좋아요": 25,
            "싫어요": 5
        },
        {
            "idea_id": "test_002", 
            "title": "스마트 도시농장 구독 서비스",
            "body": "IoT 센서가 장착된 미니 농장을 구독으로 제공하여 도시에서도 신선한 채소를 재배할 수 있는 서비스",
            "좋아요": 15,
            "싫어요": 8
        }
    ]
    
    for idea in test_ideas:
        print(f"\n새 아이디어: '{idea['title']}'")
        try:
            response = requests.post(f"{BASE_URL}/add-idea", json=idea)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"메시지: {result['message']}")
                print(f"유사 아이디어 수: {len(result['similar_ideas'])}")
                
                for i, similar in enumerate(result['similar_ideas'][:3], 1):
                    print(f"  {i}. {similar['title']} (유사도: {similar['similarity_score']:.3f})")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}")

def test_get_ideas():
    """아이디어 목록 조회 테스트"""
    print("\n=== 아이디어 목록 조회 테스트 ===")
    
    try:
        # 인기도 순으로 정렬
        response = requests.get(f"{BASE_URL}/ideas?limit=10&sort_by=popularity_score")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"총 아이디어 수: {result['total']}")
            print(f"반환된 아이디어 수: {len(result['ideas'])}")
            
            print("\n인기도 상위 5개 아이디어:")
            for i, idea in enumerate(result['ideas'][:5], 1):
                print(f"  {i}. {idea['title']}")
                print(f"     좋아요: {idea['좋아요']}, 싫어요: {idea['싫어요']}")
                print(f"     인기도 점수: {idea.get('popularity_score', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_get_idea_by_id():
    """특정 아이디어 조회 테스트"""
    print("\n=== 특정 아이디어 조회 테스트 ===")
    
    test_ids = ["idea_001", "idea_005", "idea_010"]
    
    for idea_id in test_ids:
        print(f"\n아이디어 ID: {idea_id}")
        try:
            response = requests.get(f"{BASE_URL}/ideas/{idea_id}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                idea = response.json()
                print(f"제목: {idea['title']}")
                print(f"좋아요: {idea['좋아요']}, 싫어요: {idea['싫어요']}")
            elif response.status_code == 404:
                print("아이디어를 찾을 수 없습니다.")
            
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Error: {e}")

def test_search_without_popularity():
    """인기도 점수 없이 검색 테스트"""
    print("\n=== 인기도 점수 없이 검색 테스트 ===")
    
    try:
        payload = {
            "query": "카페",
            "top_k": 5,
            "use_popularity": False,
            "min_similarity": 0.3
        }
        
        response = requests.post(f"{BASE_URL}/search", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"검색어: '{result['query']}'")
            print(f"검색된 결과 수: {result['total_found']}")
            
            print("\n순수 유사도 기반 결과:")
            for i, idea in enumerate(result['results'][:3], 1):
                print(f"  {i}. {idea['title']}")
                print(f"     순수 유사도: {idea['similarity_score']:.3f}")
                print(f"     최종점수: {idea['final_score']:.3f}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 개선된 아이디어 유사도 측정 시스템 테스트 시작")
    print("=" * 60)
    
    # 서버가 실행 중인지 확인
    if not test_health_check():
        print("❌ 서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.")
        print("   python api_server_improved.py")
        return
    
    print("✅ 서버가 정상적으로 실행 중입니다.")
    
    # 각종 테스트 실행
    test_statistics()
    test_search_similar_ideas()
    test_add_new_idea()
    test_get_ideas()
    test_get_idea_by_id()
    test_search_without_popularity()
    
    print("\n" + "=" * 60)
    print("🎉 모든 테스트가 완료되었습니다!")

if __name__ == "__main__":
    main() 