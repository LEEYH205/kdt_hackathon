#!/usr/bin/env python3
"""
유사도 임계값 조절 테스트 스크립트
"""

from policy_chatbot import PolicyChatbot

def test_similarity_thresholds():
    """다양한 유사도 임계값으로 검색 테스트"""
    print("🔍 유사도 임계값 조절 테스트")
    print("=" * 50)
    
    # 챗봇 초기화
    chatbot = PolicyChatbot()
    
    # 테스트 쿼리
    test_query = "중소기업 기술지원"
    
    # 다양한 임계값으로 테스트
    thresholds = [0.0, 0.3, 0.5, 0.7, 0.8]
    
    for threshold in thresholds:
        print(f"\n📊 유사도 임계값: {threshold}")
        print("-" * 30)
        
        results = chatbot.search_policies(test_query, top_k=10, similarity_threshold=threshold)
        
        if results:
            print(f"✅ {len(results)}개 결과 (임계값 {threshold} 이상)")
            for i, result in enumerate(results[:3], 1):  # 상위 3개만 표시
                print(f"  {i}. {result['title'][:50]}... (유사도: {result['similarity_score']:.3f})")
        else:
            print(f"❌ 결과 없음 (임계값 {threshold} 이상)")
    
    print("\n" + "=" * 50)
    print("💡 유사도 임계값 가이드:")
    print("• 0.0: 모든 결과 표시")
    print("• 0.3: 약간 관련된 결과만")
    print("• 0.5: 중간 정도 관련된 결과만")
    print("• 0.7: 높은 관련성 결과만")
    print("• 0.8: 매우 높은 관련성 결과만")

def test_specific_threshold():
    """특정 임계값으로 상세 테스트"""
    print("\n🎯 특정 임계값 상세 테스트")
    print("=" * 50)
    
    chatbot = PolicyChatbot()
    test_queries = ["AI 기술", "창업 지원", "수출 진출"]
    
    for query in test_queries:
        print(f"\n🔍 검색어: '{query}'")
        print("-" * 30)
        
        # 임계값 0.5로 테스트
        results = chatbot.search_policies(query, top_k=5, similarity_threshold=0.5)
        
        if results:
            print(f"✅ {len(results)}개 결과 (임계값 0.5 이상)")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']}")
                print(f"     🎯 {result['target']} | 📊 유사도: {result['similarity_score']:.3f}")
                print()
        else:
            print("❌ 임계값 0.5 이상인 결과가 없습니다.")

if __name__ == "__main__":
    test_similarity_thresholds()
    test_specific_threshold() 