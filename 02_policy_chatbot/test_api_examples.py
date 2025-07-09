#!/usr/bin/env python3
"""
정책 챗봇 API 사용 예시 스크립트

이 스크립트는 API의 다양한 사용 방법을 보여줍니다.
팀원들이 API를 어떻게 사용할 수 있는지 참고하세요.
"""

import requests
import json
import time
from typing import Dict, Any, List

class PolicyAPIExamples:
    """정책 챗봇 API 사용 예시 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def print_section(self, title: str):
        """섹션 제목 출력"""
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print(f"{'='*60}")
    
    def print_result(self, title: str, result: Any):
        """결과 출력"""
        print(f"\n🔍 {title}")
        print("-" * 40)
        if isinstance(result, dict):
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result)
    
    def test_health_check(self):
        """헬스 체크 테스트"""
        self.print_section("1. 헬스 체크")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            result = response.json()
            
            self.print_result("서버 상태", result)
            
            if result['status'] == 'healthy':
                print("✅ 서버가 정상적으로 실행 중입니다!")
                print(f"   📊 데이터 개수: {result['data_count']}개")
            else:
                print("❌ 서버에 문제가 있습니다.")
                
        except Exception as e:
            print(f"❌ 헬스 체크 실패: {e}")
    
    def test_simple_search(self):
        """간단한 검색 테스트"""
        self.print_section("2. 간단한 검색")
        
        # 다양한 검색어로 테스트
        test_queries = [
            "기술지원",
            "창업 지원", 
            "청년 지원",
            "중소기업",
            "AI 개발"
        ]
        
        for query in test_queries:
            try:
                params = {"query": query, "top_k": 2}
                response = self.session.get(f"{self.base_url}/search/simple", params=params)
                response.raise_for_status()
                result = response.json()
                
                self.print_result(f"검색어: '{query}'", {
                    "total_results": result['total_results'],
                    "results": [
                        {
                            "title": r['title'][:50] + "...",
                            "organization": r['organization'],
                            "similarity_score": round(r['similarity_score'], 3)
                        }
                        for r in result['results']
                    ]
                })
                
            except Exception as e:
                print(f"❌ 검색 실패 ('{query}'): {e}")
    
    def test_detailed_search(self):
        """상세 검색 테스트"""
        self.print_section("3. 상세 검색 (필터링)")
        
        # 다양한 필터 조합 테스트
        test_cases = [
            {
                "name": "포천시 기술지원",
                "data": {
                    "query": "기술지원",
                    "top_k": 3,
                    "region_filter": "포천시",
                    "similarity_threshold": 0.1
                }
            },
            {
                "name": "중소기업 창업지원",
                "data": {
                    "query": "창업 지원",
                    "top_k": 3,
                    "target_filter": "중소기업",
                    "field_filter": "창업"
                }
            },
            {
                "name": "청년 지원 (높은 유사도)",
                "data": {
                    "query": "청년 지원",
                    "top_k": 3,
                    "similarity_threshold": 0.5
                }
            }
        ]
        
        for case in test_cases:
            try:
                response = self.session.post(f"{self.base_url}/search", json=case["data"])
                response.raise_for_status()
                result = response.json()
                
                self.print_result(f"케이스: {case['name']}", {
                    "query": result['query'],
                    "total_results": result['total_results'],
                    "filters_applied": result['filters_applied'],
                    "results": [
                        {
                            "title": r['title'][:50] + "...",
                            "target": r['target'][:30] + "...",
                            "organization": r['organization'],
                            "similarity_score": round(r['similarity_score'], 3)
                        }
                        for r in result['results']
                    ]
                })
                
            except Exception as e:
                print(f"❌ 상세 검색 실패 ({case['name']}): {e}")
    
    def test_policy_summary(self):
        """정책 요약 테스트"""
        self.print_section("4. 정책 요약")
        
        test_queries = ["기술지원", "창업 지원", "청년 지원"]
        
        for query in test_queries:
            try:
                payload = {"query": query}
                response = self.session.post(f"{self.base_url}/summary", json=payload)
                response.raise_for_status()
                result = response.json()
                
                self.print_result(f"요약: '{query}'", {
                    "query": result['query'],
                    "summary_length": len(result['summary']),
                    "summary_preview": result['summary'][:200] + "..."
                })
                
            except Exception as e:
                print(f"❌ 요약 실패 ('{query}'): {e}")
    
    def test_regions(self):
        """지역 목록 테스트"""
        self.print_section("5. 지역 목록")
        
        try:
            response = self.session.get(f"{self.base_url}/regions")
            response.raise_for_status()
            result = response.json()
            
            self.print_result("지역 정보", {
                "total_count": result['total_count'],
                "sample_regions": result['regions'][:10],
                "hierarchy_examples": {
                    "포천시": result['hierarchy']['포천시'],
                    "강남구": result['hierarchy']['강남구'],
                    "경기도": result['hierarchy']['경기도']
                }
            })
            
        except Exception as e:
            print(f"❌ 지역 목록 조회 실패: {e}")
    
    def test_performance(self):
        """성능 테스트"""
        self.print_section("6. 성능 테스트")
        
        # 응답 시간 측정
        test_queries = ["기술지원", "창업", "청년", "중소기업", "AI"]
        response_times = []
        
        for query in test_queries:
            try:
                start_time = time.time()
                
                params = {"query": query, "top_k": 3}
                response = self.session.get(f"{self.base_url}/search/simple", params=params)
                response.raise_for_status()
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms
                response_times.append(response_time)
                
                print(f"   '{query}': {response_time:.1f}ms")
                
            except Exception as e:
                print(f"   '{query}': 실패 ({e})")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"\n📊 평균 응답 시간: {avg_time:.1f}ms")
            print(f"   최소: {min(response_times):.1f}ms")
            print(f"   최대: {max(response_times):.1f}ms")
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        self.print_section("7. 에러 처리 테스트")
        
        # 잘못된 요청 테스트
        error_cases = [
            {
                "name": "빈 쿼리",
                "method": "GET",
                "url": f"{self.base_url}/search/simple",
                "params": {"query": ""}
            },
            {
                "name": "잘못된 JSON",
                "method": "POST", 
                "url": f"{self.base_url}/search",
                "json": {"invalid": "data"}
            },
            {
                "name": "존재하지 않는 엔드포인트",
                "method": "GET",
                "url": f"{self.base_url}/nonexistent"
            }
        ]
        
        for case in error_cases:
            try:
                if case["method"] == "GET":
                    response = self.session.get(case["url"], params=case.get("params", {}))
                else:
                    response = self.session.post(case["url"], json=case.get("json", {}))
                
                self.print_result(f"에러 케이스: {case['name']}", {
                    "status_code": response.status_code,
                    "response": response.json() if response.content else "No content"
                })
                
            except Exception as e:
                self.print_result(f"에러 케이스: {case['name']}", f"예외 발생: {e}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 정책 챗봇 API 사용 예시 테스트 시작")
        print(f"📍 API 서버: {self.base_url}")
        print(f"⏰ 시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. 헬스 체크
            self.test_health_check()
            
            # 2. 간단한 검색
            self.test_simple_search()
            
            # 3. 상세 검색
            self.test_detailed_search()
            
            # 4. 정책 요약
            self.test_policy_summary()
            
            # 5. 지역 목록
            self.test_regions()
            
            # 6. 성능 테스트
            self.test_performance()
            
            # 7. 에러 처리
            self.test_error_handling()
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 테스트가 중단되었습니다.")
        except Exception as e:
            print(f"\n\n❌ 테스트 실행 중 오류 발생: {e}")
        
        print(f"\n✅ 테스트 완료: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="정책 챗봇 API 사용 예시")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="API 서버 URL (기본값: http://localhost:8000)"
    )
    parser.add_argument(
        "--test", 
        choices=["health", "search", "summary", "regions", "performance", "errors", "all"],
        default="all",
        help="실행할 테스트 (기본값: all)"
    )
    
    args = parser.parse_args()
    
    # API 예시 객체 생성
    examples = PolicyAPIExamples(args.url)
    
    # 선택된 테스트 실행
    if args.test == "all":
        examples.run_all_tests()
    elif args.test == "health":
        examples.test_health_check()
    elif args.test == "search":
        examples.test_simple_search()
        examples.test_detailed_search()
    elif args.test == "summary":
        examples.test_policy_summary()
    elif args.test == "regions":
        examples.test_regions()
    elif args.test == "performance":
        examples.test_performance()
    elif args.test == "errors":
        examples.test_error_handling()

if __name__ == "__main__":
    main() 