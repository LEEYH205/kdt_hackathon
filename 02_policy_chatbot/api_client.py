import requests
import json
from typing import Dict, Any, Optional
import time

class PolicyChatbotAPI:
    """정책 챗봇 API 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """서버 상태 확인"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def search_policies(self, 
                       query: str,
                       top_k: int = 5,
                       similarity_threshold: float = 0.0,
                       region_filter: Optional[str] = None,
                       target_filter: Optional[str] = None,
                       field_filter: Optional[str] = None,
                       region_weight: float = 0.3,
                       target_weight: float = 0.2,
                       field_weight: float = 0.2) -> Dict[str, Any]:
        """정책 검색 (POST 요청)"""
        try:
            payload = {
                "query": query,
                "top_k": top_k,
                "similarity_threshold": similarity_threshold,
                "region_filter": region_filter,
                "target_filter": target_filter,
                "field_filter": field_filter,
                "region_weight": region_weight,
                "target_weight": target_weight,
                "field_weight": field_weight
            }
            
            response = self.session.post(f"{self.base_url}/search", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def simple_search(self, 
                     query: str,
                     top_k: int = 5,
                     region: Optional[str] = None) -> Dict[str, Any]:
        """간단한 정책 검색 (GET 요청)"""
        try:
            params = {
                "query": query,
                "top_k": top_k
            }
            if region:
                params["region"] = region
            
            response = self.session.get(f"{self.base_url}/search/simple", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_policy_summary(self, query: str) -> Dict[str, Any]:
        """정책 요약"""
        try:
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/summary", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_available_regions(self) -> Dict[str, Any]:
        """사용 가능한 지역 목록"""
        try:
            response = self.session.get(f"{self.base_url}/regions")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

def test_api():
    """API 테스트 함수"""
    api = PolicyChatbotAPI()
    
    print("🚀 정책 챗봇 API 테스트 시작")
    print("=" * 50)
    
    # 1. 헬스 체크
    print("1. 헬스 체크...")
    health = api.health_check()
    if "error" in health:
        print(f"❌ 헬스 체크 실패: {health['error']}")
        return
    else:
        print(f"✅ 서버 상태: {health['status']}")
        print(f"   모델 로드: {health['model_loaded']}")
        print(f"   데이터 개수: {health['data_count']}")
    
    print()
    
    # 2. 지역 목록 조회
    print("2. 지역 목록 조회...")
    regions = api.get_available_regions()
    if "error" in regions:
        print(f"❌ 지역 목록 조회 실패: {regions['error']}")
    else:
        print(f"✅ 사용 가능한 지역: {regions['total_count']}개")
        print(f"   예시: {regions['regions'][:5]}")
    
    print()
    
    # 3. 간단한 검색 테스트
    print("3. 간단한 검색 테스트...")
    simple_result = api.simple_search("중소기업 기술지원", top_k=3)
    if "error" in simple_result:
        print(f"❌ 간단 검색 실패: {simple_result['error']}")
    else:
        print(f"✅ 검색 결과: {simple_result['total_results']}개")
        for i, result in enumerate(simple_result['results'][:2], 1):
            print(f"   {i}. {result['title'][:50]}...")
            print(f"      유사도: {result['similarity_score']:.3f}")
    
    print()
    
    # 4. 상세 검색 테스트
    print("4. 상세 검색 테스트...")
    detailed_result = api.search_policies(
        query="창업 지원",
        top_k=3,
        region_filter="포천시",
        similarity_threshold=0.1
    )
    if "error" in detailed_result:
        print(f"❌ 상세 검색 실패: {detailed_result['error']}")
    else:
        print(f"✅ 검색 결과: {detailed_result['total_results']}개")
        print(f"   적용된 필터: {detailed_result['filters_applied']}")
        for i, result in enumerate(detailed_result['results'][:2], 1):
            print(f"   {i}. {result['title'][:50]}...")
            print(f"      소관기관: {result['organization']}")
            print(f"      유사도: {result['similarity_score']:.3f}")
    
    print()
    
    # 5. 요약 테스트
    print("5. 정책 요약 테스트...")
    summary_result = api.get_policy_summary("청년 지원")
    if "error" in summary_result:
        print(f"❌ 요약 실패: {summary_result['error']}")
    else:
        print(f"✅ 요약 완료")
        print(f"   쿼리: {summary_result['query']}")
        print(f"   요약 길이: {len(summary_result['summary'])}자")
        print(f"   요약 미리보기: {summary_result['summary'][:200]}...")

def interactive_test():
    """대화형 API 테스트"""
    api = PolicyChatbotAPI()
    
    print("🎯 대화형 정책 챗봇 API 테스트")
    print("=" * 50)
    
    while True:
        print("\n옵션을 선택하세요:")
        print("1. 헬스 체크")
        print("2. 간단 검색")
        print("3. 상세 검색")
        print("4. 정책 요약")
        print("5. 지역 목록")
        print("0. 종료")
        
        choice = input("\n선택 (0-5): ").strip()
        
        if choice == "0":
            print("👋 테스트를 종료합니다.")
            break
        
        elif choice == "1":
            health = api.health_check()
            if "error" in health:
                print(f"❌ 오류: {health['error']}")
            else:
                print(f"✅ 상태: {health['status']}")
                print(f"   모델: {'로드됨' if health['model_loaded'] else '로드되지 않음'}")
                print(f"   데이터: {health['data_count']}개")
        
        elif choice == "2":
            query = input("검색어: ").strip()
            if not query:
                print("❌ 검색어를 입력해주세요.")
                continue
            
            top_k = input("결과 수 (기본값: 5): ").strip()
            top_k = int(top_k) if top_k.isdigit() else 5
            
            region = input("지역 필터 (선택사항): ").strip()
            region = region if region else None
            
            result = api.simple_search(query, top_k, region)
            if "error" in result:
                print(f"❌ 오류: {result['error']}")
            else:
                print(f"✅ 결과: {result['total_results']}개")
                for i, policy in enumerate(result['results'], 1):
                    print(f"\n{i}. {policy['title']}")
                    print(f"   소관기관: {policy['organization']}")
                    print(f"   지원대상: {policy['target'][:50]}...")
                    print(f"   유사도: {policy['similarity_score']:.3f}")
        
        elif choice == "3":
            query = input("검색어: ").strip()
            if not query:
                print("❌ 검색어를 입력해주세요.")
                continue
            
            top_k = input("결과 수 (기본값: 5): ").strip()
            top_k = int(top_k) if top_k.isdigit() else 5
            
            threshold = input("유사도 임계값 (기본값: 0.0): ").strip()
            threshold = float(threshold) if threshold else 0.0
            
            region = input("지역 필터 (선택사항): ").strip()
            region = region if region else None
            
            target = input("지원대상 필터 (선택사항): ").strip()
            target = target if target else None
            
            field = input("지원분야 필터 (선택사항): ").strip()
            field = field if field else None
            
            result = api.search_policies(
                query=query,
                top_k=top_k,
                similarity_threshold=threshold,
                region_filter=region,
                target_filter=target,
                field_filter=field
            )
            
            if "error" in result:
                print(f"❌ 오류: {result['error']}")
            else:
                print(f"✅ 결과: {result['total_results']}개")
                print(f"   적용된 필터: {result['filters_applied']}")
                for i, policy in enumerate(result['results'], 1):
                    print(f"\n{i}. {policy['title']}")
                    print(f"   소관기관: {policy['organization']}")
                    print(f"   지원대상: {policy['target'][:50]}...")
                    print(f"   지원분야: {policy['field_major']}")
                    print(f"   유사도: {policy['similarity_score']:.3f}")
        
        elif choice == "4":
            query = input("요약할 쿼리: ").strip()
            if not query:
                print("❌ 쿼리를 입력해주세요.")
                continue
            
            result = api.get_policy_summary(query)
            if "error" in result:
                print(f"❌ 오류: {result['error']}")
            else:
                print(f"✅ 요약 완료")
                print(f"쿼리: {result['query']}")
                print("\n" + "="*50)
                print(result['summary'])
        
        elif choice == "5":
            result = api.get_available_regions()
            if "error" in result:
                print(f"❌ 오류: {result['error']}")
            else:
                print(f"✅ 사용 가능한 지역: {result['total_count']}개")
                print("\n지역 목록:")
                for i, region in enumerate(result['regions'], 1):
                    print(f"   {i:2d}. {region}")
        
        else:
            print("❌ 잘못된 선택입니다. 0-5 중에서 선택해주세요.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        test_api() 