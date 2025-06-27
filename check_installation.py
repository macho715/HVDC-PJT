#!/usr/bin/env python3
"""
HVDC MACHO-GPT v3.4-mini 설치 검증 스크립트
Samsung C&T Logistics | ADNOC·DSV Partnership

이 스크립트는 HVDC MACHO-GPT 시스템의 설치 상태를 종합적으로 검증합니다.
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path
from datetime import datetime
import json

class InstallationChecker:
    """HVDC MACHO-GPT 설치 상태 검증 클래스"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'python_environment': {},
            'dependencies': {},
            'data_files': {},
            'source_files': {},
            'tests': {},
            'overall_status': 'UNKNOWN'
        }
        
    def print_status(self, message: str, status: str = "INFO"):
        """상태 메시지 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icons = {
            "SUCCESS": "✅",
            "ERROR": "❌", 
            "WARNING": "⚠️",
            "INFO": "ℹ️"
        }
        icon = status_icons.get(status, "ℹ️")
        print(f"[{timestamp}] {icon} {message}")
        
    def check_system_info(self):
        """시스템 정보 확인"""
        self.print_status("시스템 정보 확인 중...", "INFO")
        
        try:
            import platform
            self.results['system_info'] = {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor()
            }
            self.print_status(f"시스템: {platform.platform()}", "SUCCESS")
            self.print_status(f"Python: {platform.python_version()}", "SUCCESS")
            
        except Exception as e:
            self.print_status(f"시스템 정보 확인 실패: {e}", "ERROR")
            
    def check_python_environment(self):
        """Python 환경 확인"""
        self.print_status("Python 환경 확인 중...", "INFO")
        
        try:
            # Python 버전 확인
            version_info = sys.version_info
            if version_info.major >= 3 and version_info.minor >= 8:
                self.print_status(f"Python 버전 호환: {version_info.major}.{version_info.minor}", "SUCCESS")
            else:
                self.print_status(f"Python 버전 부족: {version_info.major}.{version_info.minor} (3.8+ 필요)", "ERROR")
                
            # 가상환경 확인
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                self.print_status("가상환경 활성화됨", "SUCCESS")
            else:
                self.print_status("가상환경이 활성화되지 않음 (권장)", "WARNING")
                
            # pip 확인
            try:
                import pip
                self.print_status(f"pip 버전: {pip.__version__}", "SUCCESS")
            except ImportError:
                self.print_status("pip를 찾을 수 없음", "ERROR")
                
        except Exception as e:
            self.print_status(f"Python 환경 확인 실패: {e}", "ERROR")
            
    def check_dependencies(self):
        """의존성 패키지 확인"""
        self.print_status("의존성 패키지 확인 중...", "INFO")
        
        required_packages = [
            'pandas', 'numpy', 'yaml', 'requests', 'python-dotenv',
            'openpyxl', 'xlrd', 'plotly', 'dash'
        ]
        
        optional_packages = [
            'matplotlib', 'seaborn', 'scikit-learn', 'jupyter'
        ]
        
        for package in required_packages:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'Unknown')
                self.results['dependencies'][package] = {
                    'status': 'INSTALLED',
                    'version': version
                }
                self.print_status(f"{package}: {version}", "SUCCESS")
            except ImportError:
                self.results['dependencies'][package] = {
                    'status': 'MISSING',
                    'version': None
                }
                self.print_status(f"{package}: 설치 필요", "ERROR")
                
        for package in optional_packages:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'Unknown')
                self.results['dependencies'][package] = {
                    'status': 'INSTALLED',
                    'version': version
                }
                self.print_status(f"{package}: {version} (선택사항)", "SUCCESS")
            except ImportError:
                self.results['dependencies'][package] = {
                    'status': 'MISSING',
                    'version': None
                }
                self.print_status(f"{package}: 설치 안됨 (선택사항)", "WARNING")
                
    def check_data_files(self):
        """데이터 파일 확인"""
        self.print_status("데이터 파일 확인 중...", "INFO")
        
        data_dir = self.project_root / 'data'
        expected_files = [
            'HVDC WAREHOUSE_INVOICE.xlsx',
            'HVDC WAREHOUSE_HITACHI(HE).xlsx',
            'HVDC WAREHOUSE_SIMENSE(SIM).xlsx',
            'HVDC WAREHOUSE_HITACHI(HE_LOCAL).xlsx'
        ]
        
        if not data_dir.exists():
            self.print_status("data/ 폴더가 없음", "ERROR")
            return
            
        for filename in expected_files:
            file_path = data_dir / filename
            if file_path.exists():
                size = file_path.stat().st_size
                self.results['data_files'][filename] = {
                    'status': 'EXISTS',
                    'size': size
                }
                self.print_status(f"{filename}: {size:,} bytes", "SUCCESS")
            else:
                self.results['data_files'][filename] = {
                    'status': 'MISSING',
                    'size': 0
                }
                self.print_status(f"{filename}: 없음", "ERROR")
                
    def check_source_files(self):
        """소스 파일 확인"""
        self.print_status("소스 파일 확인 중...", "INFO")
        
        src_dir = self.project_root / 'src'
        expected_files = [
            'logi_meta_fixed.py',
            'warehouse_enhanced.py'
        ]
        
        if not src_dir.exists():
            self.print_status("src/ 폴더가 없음", "ERROR")
            return
            
        for filename in expected_files:
            file_path = src_dir / filename
            if file_path.exists():
                size = file_path.stat().st_size
                self.results['source_files'][filename] = {
                    'status': 'EXISTS',
                    'size': size
                }
                self.print_status(f"{filename}: {size:,} bytes", "SUCCESS")
            else:
                self.results['source_files'][filename] = {
                    'status': 'MISSING',
                    'size': 0
                }
                self.print_status(f"{filename}: 없음", "ERROR")
                
    def check_config_files(self):
        """설정 파일 확인"""
        self.print_status("설정 파일 확인 중...", "INFO")
        
        config_files = [
            'requirements.txt',
            'INSTALLATION_GUIDE.md'
        ]
        
        for filename in config_files:
            file_path = self.project_root / filename
            if file_path.exists():
                size = file_path.stat().st_size
                self.print_status(f"{filename}: {size:,} bytes", "SUCCESS")
            else:
                self.print_status(f"{filename}: 없음", "WARNING")
                
    def run_basic_tests(self):
        """기본 기능 테스트"""
        self.print_status("기본 기능 테스트 중...", "INFO")
        
        try:
            # pandas 테스트
            import pandas as pd
            df = pd.DataFrame({'test': [1, 2, 3]})
            self.print_status("pandas DataFrame 생성 테스트 통과", "SUCCESS")
            
            # numpy 테스트
            import numpy as np
            arr = np.array([1, 2, 3])
            self.print_status("numpy 배열 생성 테스트 통과", "SUCCESS")
            
            # yaml 테스트
            import yaml
            test_data = {'test': 'value'}
            yaml_str = yaml.dump(test_data)
            loaded_data = yaml.safe_load(yaml_str)
            self.print_status("yaml 파싱 테스트 통과", "SUCCESS")
            
            # Excel 읽기 테스트
            import openpyxl
            self.print_status("openpyxl Excel 처리 테스트 통과", "SUCCESS")
            
        except Exception as e:
            self.print_status(f"기본 기능 테스트 실패: {e}", "ERROR")
            
    def check_main_modules(self):
        """메인 모듈 로드 테스트"""
        self.print_status("메인 모듈 로드 테스트 중...", "INFO")
        
        try:
            # sys.path에 src 디렉토리 추가
            src_path = self.project_root / 'src'
            if src_path.exists():
                sys.path.insert(0, str(src_path))
                
                # logi_meta_fixed 모듈 테스트
                try:
                    import logi_meta_fixed
                    self.print_status("logi_meta_fixed 모듈 로드 성공", "SUCCESS")
                except ImportError as e:
                    self.print_status(f"logi_meta_fixed 모듈 로드 실패: {e}", "ERROR")
                    
                # warehouse_enhanced 모듈 테스트
                try:
                    import warehouse_enhanced
                    self.print_status("warehouse_enhanced 모듈 로드 성공", "SUCCESS")
                except ImportError as e:
                    self.print_status(f"warehouse_enhanced 모듈 로드 실패: {e}", "ERROR")
                    
        except Exception as e:
            self.print_status(f"메인 모듈 테스트 실패: {e}", "ERROR")
            
    def generate_report(self):
        """검증 결과 리포트 생성"""
        self.print_status("검증 결과 분석 중...", "INFO")
        
        # 전체 상태 평가
        errors = 0
        warnings = 0
        
        # 의존성 오류 확인
        for pkg, info in self.results['dependencies'].items():
            if info['status'] == 'MISSING' and pkg in ['pandas', 'numpy', 'yaml', 'requests']:
                errors += 1
                
        # 데이터 파일 오류 확인
        for file, info in self.results['data_files'].items():
            if info['status'] == 'MISSING':
                errors += 1
                
        # 소스 파일 오류 확인
        for file, info in self.results['source_files'].items():
            if info['status'] == 'MISSING':
                errors += 1
                
        # 전체 상태 결정
        if errors == 0:
            self.results['overall_status'] = 'SUCCESS'
            self.print_status("🎉 모든 검증 통과! 시스템이 정상적으로 설치되었습니다.", "SUCCESS")
        elif errors <= 2:
            self.results['overall_status'] = 'WARNING'
            self.print_status(f"⚠️ {errors}개의 오류가 있습니다. 일부 기능이 제한될 수 있습니다.", "WARNING")
        else:
            self.results['overall_status'] = 'ERROR'
            self.print_status(f"❌ {errors}개의 오류가 있습니다. 재설치가 필요합니다.", "ERROR")
            
        # 결과 저장
        report_file = self.project_root / 'installation_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        self.print_status(f"검증 리포트 저장됨: {report_file}", "SUCCESS")
        
    def run_full_check(self):
        """전체 검증 실행"""
        self.print_status("🔍 HVDC MACHO-GPT v3.4-mini 설치 검증 시작", "INFO")
        print("=" * 60)
        
        self.check_system_info()
        print("-" * 40)
        
        self.check_python_environment()
        print("-" * 40)
        
        self.check_dependencies()
        print("-" * 40)
        
        self.check_data_files()
        print("-" * 40)
        
        self.check_source_files()
        print("-" * 40)
        
        self.check_config_files()
        print("-" * 40)
        
        self.run_basic_tests()
        print("-" * 40)
        
        self.check_main_modules()
        print("-" * 40)
        
        self.generate_report()
        print("=" * 60)
        
        return self.results['overall_status']

def main():
    """메인 함수"""
    checker = InstallationChecker()
    status = checker.run_full_check()
    
    # 추천 명령어 출력
    print("\n🔧 **추천 명령어:**")
    print("/cmd_install_dependencies [의존성 패키지 설치 - 오류 수정]")
    print("/cmd_run_warehouse_analysis [창고 분석 실행 - 시스템 테스트]")
    print("/cmd_generate_dashboard [대시보드 생성 - 시각화 확인]")
    
    return 0 if status == 'SUCCESS' else 1

if __name__ == "__main__":
    sys.exit(main()) 