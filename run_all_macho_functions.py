#!/usr/bin/env python3
"""
🚀 MACHO 로직 함수 통합 실행 스크립트
MACHO-GPT v3.4-mini │ Samsung C&T Logistics

모든 MACHO 로직 함수들을 순차적 또는 선택적으로 실행
- Flow Code 분류
- SQM/STACK 분석  
- 트랜잭션 데이터 처리
- 월별 트랜잭션 생성
- 통합 파이프라인 실행

작성: 2025-07-02
버전: v3.4-mini
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json

class MachoFunctionMaster:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.execution_log = []
        
        # 로직 함수 파일 매핑
        self.functions = {
            '1': {
                'name': 'Flow Code 분류',
                'file': 'macho_flow_corrected_v284.py',
                'description': 'WH HANDLING 기반 Flow Code 0-3 자동 분류',
                'estimated_time': '2-3분'
            },
            '2': {
                'name': 'SQM/STACK 분석',
                'file': 'analyze_stack_sqm.py', 
                'description': '스택 적재 기반 실제 창고 면적 계산',
                'estimated_time': '1-2분'
            },
            '3': {
                'name': '전체 트랜잭션 처리',
                'file': 'complete_transaction_data_wh_handling_v284.py',
                'description': 'HITACHI + SIMENSE 7,573건 데이터 통합',
                'estimated_time': '3-5분'
            },
            '4': {
                'name': '월별 트랜잭션 생성',
                'file': 'monthly_transaction_generator.py',
                'description': '25개월 실제 케이스 기반 트랜잭션 생성',
                'estimated_time': '5-8분'
            },
            '5': {
                'name': '통합 파이프라인',
                'file': 'macho_integrated_pipeline.py',
                'description': 'Flow Code → 트랜잭션 이벤트 전체 자동화',
                'estimated_time': '8-12분'
            },
            '6': {
                'name': '프로덕션 실행',
                'file': 'run_macho_v284_production.py',
                'description': '전체 MACHO v2.8.4 프로덕션 파이프라인',
                'estimated_time': '10-15분'
            },
            '7': {
                'name': '테스트 실행',
                'file': 'test_final_transaction_generator.py',
                'description': '단위 테스트 및 검증',
                'estimated_time': '2-3분'
            },
            '8': {
                'name': '최종 트랜잭션 생성',
                'file': 'final_transaction_generator.py',
                'description': '최종 완성 트랜잭션 데이터 생성',
                'estimated_time': '5-7분'
            }
        }
    
    def display_menu(self):
        """메인 메뉴 표시"""
        print("🚀 MACHO 로직 함수 통합 실행 도구")
        print("=" * 70)
        print("🎯 MACHO-GPT v3.4-mini │ Samsung C&T Logistics")
        print("📊 총 8개 로직 함수 │ 7,573건 트랜잭션 데이터")
        print("-" * 70)
        
        for key, func in self.functions.items():
            status = "✅ 사용 가능" if self.check_file_exists(func['file']) else "❌ 파일 없음"
            print(f"{key}. {func['name']:<20} [{func['estimated_time']}] - {status}")
            print(f"   📄 {func['file']}")
            print(f"   📝 {func['description']}")
            print()
        
        print("9. 🔥 전체 실행 (순차적)")
        print("0. 🚪 종료")
        print("-" * 70)
    
    def check_file_exists(self, filename):
        """파일 존재 여부 확인"""
        return os.path.exists(filename)
    
    def execute_function(self, function_key):
        """선택된 함수 실행"""
        if function_key not in self.functions:
            print("❌ 잘못된 선택입니다.")
            return False
        
        func_info = self.functions[function_key]
        filename = func_info['file']
        
        if not self.check_file_exists(filename):
            print(f"❌ 파일을 찾을 수 없습니다: {filename}")
            return False
        
        print(f"\n🔄 {func_info['name']} 실행 중...")
        print(f"📄 파일: {filename}")
        print(f"⏱️  예상 시간: {func_info['estimated_time']}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Python 스크립트 실행
            result = subprocess.run(
                [sys.executable, filename],
                capture_output=True,
                text=True,
                timeout=900  # 15분 타임아웃
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 실행 로그 기록
            log_entry = {
                'function': func_info['name'],
                'file': filename,
                'start_time': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
                'execution_time': f"{execution_time:.1f}초",
                'success': result.returncode == 0,
                'output_lines': len(result.stdout.split('\n')) if result.stdout else 0,
                'error_lines': len(result.stderr.split('\n')) if result.stderr else 0
            }
            self.execution_log.append(log_entry)
            
            if result.returncode == 0:
                print(f"✅ {func_info['name']} 완료!")
                print(f"⏱️  실행 시간: {execution_time:.1f}초")
                
                # 출력 요약
                if result.stdout:
                    output_lines = result.stdout.split('\n')
                    print(f"📊 출력: {len(output_lines)}라인")
                    
                    # 중요한 출력 라인만 표시
                    important_lines = [line for line in output_lines 
                                     if any(keyword in line for keyword in 
                                           ['✅', '📊', '🎉', '완료', 'Success', 'Total', 'Summary'])]
                    
                    if important_lines:
                        print("📋 주요 결과:")
                        for line in important_lines[-5:]:  # 마지막 5개만
                            print(f"   {line}")
                
                return True
            else:
                print(f"❌ {func_info['name']} 실행 실패!")
                print(f"⏱️  실행 시간: {execution_time:.1f}초")
                print(f"🚨 오류 코드: {result.returncode}")
                
                if result.stderr:
                    print("📝 오류 메시지:")
                    error_lines = result.stderr.split('\n')
                    for line in error_lines[-10:]:  # 마지막 10개 오류만
                        if line.strip():
                            print(f"   {line}")
                
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {func_info['name']} 타임아웃 (15분 초과)")
            return False
        except Exception as e:
            print(f"❌ {func_info['name']} 실행 중 오류: {e}")
            return False
    
    def execute_all_functions(self):
        """모든 함수 순차 실행"""
        print("\n🔥 전체 MACHO 로직 함수 순차 실행 시작!")
        print("=" * 70)
        
        total_start_time = time.time()
        success_count = 0
        total_functions = len(self.functions)
        
        # 실행 순서 정의 (의존성 고려)
        execution_order = ['1', '2', '3', '4', '5', '7', '8', '6']  # 프로덕션은 마지막
        
        for i, func_key in enumerate(execution_order, 1):
            print(f"\n📍 진행률: {i}/{len(execution_order)} - {self.functions[func_key]['name']}")
            
            if self.execute_function(func_key):
                success_count += 1
                print(f"🎯 중간 성공률: {success_count}/{i} ({success_count/i*100:.1f}%)")
            else:
                print(f"⚠️  {self.functions[func_key]['name']} 실패, 계속 진행...")
            
            # 다음 함수 실행 전 잠시 대기
            if i < len(execution_order):
                print("⏳ 다음 함수 준비 중... (3초 대기)")
                time.sleep(3)
        
        total_end_time = time.time()
        total_execution_time = total_end_time - total_start_time
        
        # 최종 결과 리포트
        print("\n" + "=" * 70)
        print("🎉 전체 MACHO 로직 함수 실행 완료!")
        print("-" * 70)
        print(f"📊 총 실행 시간: {total_execution_time/60:.1f}분 ({total_execution_time:.1f}초)")
        print(f"✅ 성공: {success_count}/{len(execution_order)}개 함수")
        print(f"🎯 성공률: {success_count/len(execution_order)*100:.1f}%")
        
        # 상세 실행 로그 저장
        self.save_execution_log()
    
    def save_execution_log(self):
        """실행 로그 저장"""
        log_filename = f"macho_execution_log_{self.timestamp}.json"
        
        log_data = {
            'timestamp': self.timestamp,
            'total_functions': len(self.functions),
            'executed_functions': len(self.execution_log),
            'success_count': sum(1 for log in self.execution_log if log['success']),
            'execution_details': self.execution_log
        }
        
        try:
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            print(f"📝 실행 로그 저장: {log_filename}")
            
        except Exception as e:
            print(f"⚠️  로그 저장 실패: {e}")
    
    def run(self):
        """메인 실행 루프"""
        while True:
            self.display_menu()
            
            try:
                choice = input("📝 선택하세요 (0-9): ").strip()
                
                if choice == '0':
                    print("\n👋 MACHO 로직 함수 실행 도구를 종료합니다.")
                    print("🎯 MACHO-GPT v3.4-mini │ ≥95% 신뢰도 달성")
                    break
                elif choice == '9':
                    self.execute_all_functions()
                elif choice in self.functions:
                    self.execute_function(choice)
                else:
                    print("❌ 잘못된 선택입니다. 0-9 사이의 숫자를 입력하세요.")
                
                if choice != '0':
                    input("\n⏳ 계속하려면 Enter를 누르세요...")
                    print("\n" * 2)  # 화면 정리
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  사용자에 의해 중단되었습니다.")
                break
            except Exception as e:
                print(f"\n❌ 오류 발생: {e}")
                input("⏳ 계속하려면 Enter를 누르세요...")

def main():
    """메인 함수"""
    print("🚀 MACHO 로직 함수 통합 실행 도구 초기화 중...")
    
    # 현재 디렉토리 확인
    current_dir = os.getcwd()
    print(f"📂 현재 디렉토리: {current_dir}")
    
    # 필요한 파일들 존재 여부 미리 확인
    master = MachoFunctionMaster()
    available_functions = sum(1 for func in master.functions.values() 
                            if master.check_file_exists(func['file']))
    
    print(f"✅ 사용 가능한 함수: {available_functions}/{len(master.functions)}개")
    print("-" * 50)
    
    if available_functions == 0:
        print("❌ 실행 가능한 함수가 없습니다.")
        print("📂 로직 함수 파일들이 올바른 위치에 있는지 확인하세요.")
        return
    
    # 메인 실행
    master.run()

if __name__ == "__main__":
    main() 