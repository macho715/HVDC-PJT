#!/usr/bin/env python3
"""
HVDC Project Full Stack 실행 스크립트
백엔드 API 서버와 프론트엔드 개발 서버를 동시에 실행
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class FullStackRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = False
        
    def start_backend(self):
        """백엔드 API 서버 시작"""
        print("🚀 백엔드 API 서버 시작 중...")
        backend_dir = Path(__file__).parent / "src" / "backend"
        
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✅ 백엔드 서버가 포트 8000에서 실행 중입니다")
            print("📖 API 문서: http://localhost:8000/docs")
        except Exception as e:
            print(f"❌ 백엔드 서버 시작 실패: {e}")
            return False
        return True
    
    def start_frontend(self):
        """프론트엔드 개발 서버 시작"""
        print("🌐 프론트엔드 개발 서버 시작 중...")
        frontend_dir = Path(__file__).parent / "src" / "frontend"
        
        try:
            # npm 의존성 설치 확인
            if not (frontend_dir / "node_modules").exists():
                print("📦 npm 의존성 설치 중...")
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            
            self.frontend_process = subprocess.Popen(
                ["npm", "start"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✅ 프론트엔드 서버가 포트 3000에서 실행 중입니다")
            print("🌍 웹 앱: http://localhost:3000")
        except Exception as e:
            print(f"❌ 프론트엔드 서버 시작 실패: {e}")
            return False
        return True
    
    def start_services(self):
        """모든 서비스 시작"""
        print("🎯 HVDC Full Stack 시스템 시작 중...")
        
        # 백엔드 시작
        if not self.start_backend():
            return False
        
        # 백엔드가 완전히 시작될 때까지 대기
        time.sleep(3)
        
        # 프론트엔드 시작
        if not self.start_frontend():
            self.stop_backend()
            return False
        
        self.running = True
        print("\n🎉 HVDC Full Stack 시스템이 성공적으로 시작되었습니다!")
        print("\n📋 접속 정보:")
        print("   🌐 웹 애플리케이션: http://localhost:3000")
        print("   🔌 API 서버: http://localhost:8000")
        print("   📖 API 문서: http://localhost:8000/docs")
        print("   📊 시스템 상태: http://localhost:8000/health")
        print("\n⏹️  종료하려면 Ctrl+C를 누르세요")
        
        return True
    
    def stop_backend(self):
        """백엔드 서버 중지"""
        if self.backend_process:
            print("🛑 백엔드 서버 중지 중...")
            self.backend_process.terminate()
            self.backend_process.wait()
            self.backend_process = None
    
    def stop_frontend(self):
        """프론트엔드 서버 중지"""
        if self.frontend_process:
            print("🛑 프론트엔드 서버 중지 중...")
            self.frontend_process.terminate()
            self.frontend_process.wait()
            self.frontend_process = None
    
    def stop_services(self):
        """모든 서비스 중지"""
        print("\n🛑 HVDC Full Stack 시스템 종료 중...")
        self.running = False
        
        self.stop_frontend()
        self.stop_backend()
        
        print("✅ 모든 서비스가 종료되었습니다")
    
    def run(self):
        """메인 실행 루프"""
        try:
            if not self.start_services():
                print("❌ 서비스 시작 실패")
                return 1
            
            # 서비스가 실행되는 동안 대기
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  사용자에 의해 중단됨")
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")
        finally:
            self.stop_services()
        
        return 0

def main():
    """메인 함수"""
    print("=" * 60)
    print("🚀 HVDC Project Full Stack Runner")
    print("=" * 60)
    
    # Python 버전 확인
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다")
        return 1
    
    # 필요한 디렉토리 확인
    project_root = Path(__file__).parent
    backend_dir = project_root / "src" / "backend"
    frontend_dir = project_root / "src" / "frontend"
    
    if not backend_dir.exists():
        print(f"❌ 백엔드 디렉토리를 찾을 수 없습니다: {backend_dir}")
        return 1
    
    if not frontend_dir.exists():
        print(f"❌ 프론트엔드 디렉토리를 찾을 수 없습니다: {frontend_dir}")
        return 1
    
    # 실행
    runner = FullStackRunner()
    return runner.run()

if __name__ == "__main__":
    sys.exit(main())









