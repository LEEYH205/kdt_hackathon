#!/usr/bin/env python3
"""
정책 챗봇 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from policy_chatbot import PolicyChatbot
import time

def test_chatbot():
    """챗봇 테스트"""
    print("🏛️ 정책 챗봇 테스트 시작")
    print("=" * 50)
    
    try:
        # 챗봇 초기화
        print("1. 챗봇 초기화 중...")
        start_time = time.time()
        chatbot = PolicyChatbot()
        init_time = time.time() - start_time
        print(f"✅ 초기화 완료 (소요시간: {init_time:.2f}초)")
        
        # 테스트 쿼리들
        test_queries = [
            "중소기업 기술지원",
            "창업 지원",
            "수출 진출",
            "청년 지원",
            "AI 기술 개발",
            "소상공인 지원",
            "연구개발 지원",
            "블록체인",
            "바이오 기술",
            "환경 친화적"
        ]
        
        print(f"\n2. 검색 테스트 ({len(test_queries)}개 쿼리)")
        print("-" * 30)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 테스트 {i}: '{query}'")
            
            start_time = time.time()
            results = chatbot.search_policies(query, top_k=3)
            search_time = time.time() - start_time
            
            if results:
                print(f"✅ {len(results)}개 결과 찾음 (소요시간: {search_time:.3f}초)")
                for j, result in enumerate(results, 1):
                    print(f"  {j}. {result['title'][:50]}... (유사도: {result['similarity_score']:.3f})")
            else:
                print(f"❌ 결과 없음 (소요시간: {search_time:.3f}초)")
        
        # 요약 테스트
        print(f"\n3. 요약 테스트")
        print("-" * 30)
        
        summary_query = "중소기업 기술지원"
        start_time = time.time()
        summary = chatbot.get_policy_summary(summary_query)
        summary_time = time.time() - start_time
        
        print(f"📋 '{summary_query}' 요약 (소요시간: {summary_time:.3f}초)")
        print(summary[:200] + "..." if len(summary) > 200 else summary)
        
        # 모델 저장 테스트
        print(f"\n4. 모델 저장 테스트")
        print("-" * 30)
        
        start_time = time.time()
        chatbot.save_model("test_model.pkl")
        save_time = time.time() - start_time
        print(f"✅ 모델 저장 완료 (소요시간: {save_time:.3f}초)")
        
        # 통계 정보
        print(f"\n5. 데이터 통계")
        print("-" * 30)
        
        data = chatbot.data
        print(f"📊 총 정책 수: {len(data)}개")
        print(f"📊 지원대상 종류: {data['지원대상'].nunique()}개")
        print(f"📊 소관기관 종류: {data['소관기관'].nunique()}개")
        print(f"📊 지원분야 종류: {data['지원분야(대)'].nunique()}개")
        
        print("\n🎯 지원대상별 분포 (상위 5개):")
        target_counts = data['지원대상'].value_counts().head(5)
        for target, count in target_counts.items():
            print(f"  • {target}: {count}개")
        
        print("\n🏷️ 지원분야별 분포 (상위 5개):")
        field_counts = data['지원분야(대)'].value_counts().head(5)
        for field, count in field_counts.items():
            print(f"  • {field}: {count}개")
        
        print("\n✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

def interactive_test():
    """대화형 테스트"""
    print("🏛️ 정책 챗봇 대화형 테스트")
    print("=" * 50)
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("-" * 30)
    
    try:
        chatbot = PolicyChatbot()
        print("✅ 챗봇이 준비되었습니다!")
        
        while True:
            query = input("\n🔍 검색어를 입력하세요: ").strip()
            
            if query.lower() in ['quit', 'exit', '종료']:
                print("👋 테스트를 종료합니다.")
                break
            
            if not query:
                print("❌ 검색어를 입력해주세요.")
                continue
            
            print("🔍 검색 중...")
            results = chatbot.search_policies(query, top_k=3)
            
            if results:
                print(f"\n✅ '{query}'에 대한 {len(results)}개의 정책을 찾았습니다!")
                for i, result in enumerate(results, 1):
                    print(f"\n📋 {i}. {result['title']}")
                    print(f"   🎯 지원대상: {result['target']}")
                    print(f"   🏢 소관기관: {result['organization']}")
                    print(f"   📅 신청기간: {result['period']}")
                    print(f"   📊 유사도: {result['similarity_score']:.3f}")
                    print(f"   📞 문의처: {result['contact']}")
                    print("-" * 40)
            else:
                print(f"😔 '{query}'에 대한 관련 정책을 찾을 수 없습니다.")
    
    except KeyboardInterrupt:
        print("\n👋 테스트를 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="정책 챗봇 테스트")
    parser.add_argument("--interactive", "-i", action="store_true", help="대화형 테스트 모드")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_test()
    else:
        test_chatbot() 