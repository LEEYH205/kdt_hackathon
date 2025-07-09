#!/usr/bin/env python3
"""
정책 챗봇 API 서버 실행 스크립트
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="정책 챗봇 API 서버 실행")
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="서버 호스트 (기본값: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="서버 포트 (기본값: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="개발 모드 (자동 재시작)"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="워커 프로세스 수 (기본값: 1)"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["debug", "info", "warning", "error"],
        help="로그 레벨 (기본값: info)"
    )
    
    args = parser.parse_args()
    
    # 현재 디렉토리를 프로젝트 루트로 설정
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 정책 챗봇 API 서버 시작")
    print(f"📍 호스트: {args.host}")
    print(f"🔌 포트: {args.port}")
    print(f"🔄 자동 재시작: {'활성화' if args.reload else '비활성화'}")
    print(f"👥 워커 수: {args.workers}")
    print(f"📝 로그 레벨: {args.log_level}")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "api_server:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 서버를 종료합니다.")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 