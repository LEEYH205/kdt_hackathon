#!/usr/bin/env python3
"""
정책 챗봇 실행 스크립트
"""

import sys
import os
import argparse
import subprocess

def check_dependencies():
    """의존성 확인"""
    required_packages = [
        'pandas', 'numpy', 'sentence_transformers', 
        'faiss', 'streamlit', 'gradio'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 다음 패키지들이 설치되지 않았습니다:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n다음 명령어로 설치하세요:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_data_file():
    """데이터 파일 확인"""
    data_path = "data/bizinfo.csv"
    if not os.path.exists(data_path):
        print(f"❌ 데이터 파일을 찾을 수 없습니다: {data_path}")
        return False
    return True

def run_streamlit():
    """Streamlit 앱 실행"""
    print("🚀 Streamlit 앱을 시작합니다...")
    print("📱 브라우저에서 http://localhost:8501 을 열어주세요")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)
    
    try:
        subprocess.run(["streamlit", "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 앱을 종료합니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit 실행 실패: {e}")

def run_gradio():
    """Gradio 앱 실행"""
    print("🚀 Gradio 앱을 시작합니다...")
    print("📱 브라우저에서 http://localhost:7860 을 열어주세요")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)
    
    try:
        subprocess.run(["python", "gradio_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 앱을 종료합니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Gradio 실행 실패: {e}")

def run_test():
    """테스트 실행"""
    print("🧪 테스트를 실행합니다...")
    print("-" * 50)
    
    try:
        subprocess.run(["python", "test_chatbot.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 테스트 실행 실패: {e}")

def run_interactive_test():
    """대화형 테스트 실행"""
    print("💬 대화형 테스트를 시작합니다...")
    print("-" * 50)
    
    try:
        subprocess.run(["python", "test_chatbot.py", "--interactive"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 대화형 테스트 실행 실패: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="🏛️ 정책 챗봇 실행 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python run_chatbot.py streamlit    # Streamlit 웹 앱 실행
  python run_chatbot.py gradio       # Gradio 웹 앱 실행
  python run_chatbot.py test         # 테스트 실행
  python run_chatbot.py interactive  # 대화형 테스트 실행
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['streamlit', 'gradio', 'test', 'interactive'],
        help='실행 모드 선택'
    )
    
    parser.add_argument(
        '--skip-check',
        action='store_true',
        help='의존성 및 데이터 파일 확인 건너뛰기'
    )
    
    args = parser.parse_args()
    
    # 헤더 출력
    print("🏛️ 정책 챗봇")
    print("=" * 50)
    
    # 의존성 및 데이터 확인
    if not args.skip_check:
        print("🔍 시스템 확인 중...")
        
        if not check_dependencies():
            sys.exit(1)
        
        if not check_data_file():
            sys.exit(1)
        
        print("✅ 모든 확인 완료!")
        print()
    
    # 모드별 실행
    if args.mode == 'streamlit':
        run_streamlit()
    elif args.mode == 'gradio':
        run_gradio()
    elif args.mode == 'test':
        run_test()
    elif args.mode == 'interactive':
        run_interactive_test()

if __name__ == "__main__":
    main() 