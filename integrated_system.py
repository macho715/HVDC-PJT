#!/usr/bin/env python3
"""
HVDC MACHO-GPT v3.4-mini + WAREHOUSE 통합 시스템
Samsung C&T Logistics | ADNOC·DSV Partnership

이 파일은 MACHO-GPT와 WAREHOUSE 시스템을 통합하여 실행하는 인터페이스입니다.
기존 파일들은 수정하지 않고 통합 기능을 제공합니다.
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

class IntegratedSystem:
    """MACHO-GPT와 WAREHOUSE 시스템 통합 클래스"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.macho_gpt_path = self.project_root / "src" / "logi_meta_fixed.py"
        self.warehouse_path = self.project_root / "WAREHOUSE"
        self.warehouse_main = self.warehouse_path / "main.py"
        self.warehouse_test = self.warehouse_path / "test_excel_reporter.py"
        
        # Windows 환경에서 인코딩 설정
        self.env = os.environ.copy()
        self.env['PYTHONIOENCODING'] = 'utf-8'
        
    def run_macho_gpt_status(self):
        """MACHO-GPT 시스템 상태 확인"""
        print("🚛 MACHO-GPT 시스템 상태 확인 중...")
        print("=" * 60)
        
        try:
            result = subprocess.run([
                sys.executable, str(self.macho_gpt_path), "--status"
            ], capture_output=True, text=True, cwd=self.project_root, 
               env=self.env, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"❌ MACHO-GPT 실행 실패: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ MACHO-GPT 실행 오류: {e}")
            return False
    
    def run_warehouse_analysis(self, debug=False):
        """WAREHOUSE 시스템 분석 실행"""
        print("🏭 WAREHOUSE 시스템 분석 실행 중...")
        print("=" * 60)
        
        try:
            cmd = [sys.executable, str(self.warehouse_main)]
            if debug:
                cmd.append("--debug")
                
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  cwd=self.warehouse_path, env=self.env,
                                  encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"❌ WAREHOUSE 실행 실패: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ WAREHOUSE 실행 오류: {e}")
            return False
    
    def run_warehouse_test(self):
        """WAREHOUSE 테스트 실행"""
        print("🧪 WAREHOUSE 테스트 실행 중...")
        print("=" * 60)
        
        try:
            result = subprocess.run([
                sys.executable, str(self.warehouse_test)
            ], capture_output=True, text=True, cwd=self.warehouse_path,
               env=self.env, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"❌ WAREHOUSE 테스트 실패: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ WAREHOUSE 테스트 오류: {e}")
            return False
    
    def run_installation_check(self):
        """설치 검증 실행"""
        print("🔧 시스템 설치 검증 중...")
        print("=" * 60)
        
        try:
            result = subprocess.run([
                sys.executable, "check_installation.py"
            ], capture_output=True, text=True, cwd=self.project_root,
               env=self.env, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"❌ 설치 검증 실패: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 설치 검증 오류: {e}")
            return False
    
    def get_system_info(self):
        """통합 시스템 정보 조회"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "macho_gpt_path": str(self.macho_gpt_path),
            "warehouse_path": str(self.warehouse_path),
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        # 파일 존재 확인
        info["macho_gpt_exists"] = self.macho_gpt_path.exists()
        info["warehouse_main_exists"] = self.warehouse_main.exists()
        info["warehouse_test_exists"] = self.warehouse_test.exists()
        
        return info
    
    def run_integrated_analysis(self):
        """통합 분석 실행"""
        print("🚀 HVDC MACHO-GPT + WAREHOUSE 통합 분석 시작")
        print("=" * 80)
        print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 시스템 정보 출력
        system_info = self.get_system_info()
        print("\n📊 시스템 정보:")
        print(f"   프로젝트 루트: {system_info['project_root']}")
        print(f"   Python 버전: {system_info['python_version']}")
        print(f"   플랫폼: {system_info['platform']}")
        print(f"   MACHO-GPT 파일: {'✅ 존재' if system_info['macho_gpt_exists'] else '❌ 없음'}")
        print(f"   WAREHOUSE 메인: {'✅ 존재' if system_info['warehouse_main_exists'] else '❌ 없음'}")
        print(f"   WAREHOUSE 테스트: {'✅ 존재' if system_info['warehouse_test_exists'] else '❌ 없음'}")
        
        # 2. MACHO-GPT 상태 확인
        print("\n" + "=" * 80)
        macho_success = self.run_macho_gpt_status()
        
        # 3. 설치 검증
        print("\n" + "=" * 80)
        install_success = self.run_installation_check()
        
        # 4. WAREHOUSE 분석 (디버그 모드)
        print("\n" + "=" * 80)
        warehouse_success = self.run_warehouse_analysis(debug=True)
        
        # 5. WAREHOUSE 테스트
        print("\n" + "=" * 80)
        test_success = self.run_warehouse_test()
        
        # 6. 결과 요약
        print("\n" + "=" * 80)
        print("📋 통합 분석 결과 요약")
        print("=" * 80)
        
        results = {
            "MACHO-GPT 상태": "✅ 성공" if macho_success else "❌ 실패",
            "설치 검증": "✅ 성공" if install_success else "❌ 실패", 
            "WAREHOUSE 분석": "✅ 성공" if warehouse_success else "❌ 실패",
            "WAREHOUSE 테스트": "✅ 성공" if test_success else "❌ 실패"
        }
        
        for test_name, result in results.items():
            print(f"   {test_name}: {result}")
        
        success_count = sum(1 for result in results.values() if "성공" in result)
        total_count = len(results)
        success_rate = (success_count / total_count) * 100
        
        print(f"\n📊 전체 성공률: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("🎉 시스템 상태: ✅ 정상 (대부분의 기능이 작동합니다)")
        elif success_rate >= 50:
            print("⚠️ 시스템 상태: ⚠️ 부분 정상 (일부 기능에 문제가 있습니다)")
        else:
            print("❌ 시스템 상태: ❌ 비정상 (심각한 문제가 있습니다)")
        
        # 7. 추천 명령어
        print("\n🔧 **추천 명령어:**")
        print("/cmd_warehouse_status [WAREHOUSE 시스템 상태 확인]")
        print("/cmd_warehouse_test [WAREHOUSE 시스템 테스트 실행]")
        print("/cmd_warehouse_report [WAREHOUSE 리포트 생성]")
        print("/cmd_macho_gpt_status [MACHO-GPT 시스템 상태 확인]")
        print("/cmd_integrated_analysis [통합 분석 재실행]")
        
        return success_rate >= 50

def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print("🚀 HVDC MACHO-GPT + WAREHOUSE 통합 시스템")
        print("=" * 60)
        print("사용법:")
        print("  python integrated_system.py status     # MACHO-GPT 상태")
        print("  python integrated_system.py warehouse  # WAREHOUSE 분석")
        print("  python integrated_system.py test       # WAREHOUSE 테스트")
        print("  python integrated_system.py check      # 설치 검증")
        print("  python integrated_system.py full       # 통합 분석")
        return 0
    
    system = IntegratedSystem()
    command = sys.argv[1].lower()
    
    if command == "status":
        return 0 if system.run_macho_gpt_status() else 1
    elif command == "warehouse":
        return 0 if system.run_warehouse_analysis() else 1
    elif command == "test":
        return 0 if system.run_warehouse_test() else 1
    elif command == "check":
        return 0 if system.run_installation_check() else 1
    elif command == "full":
        return 0 if system.run_integrated_analysis() else 1
    else:
        print(f"❌ 알 수 없는 명령어: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 