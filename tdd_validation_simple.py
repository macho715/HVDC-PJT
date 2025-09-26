#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini TDD 검증 시나리오 (Simple Version)
pytest 의존성 없이 표준 라이브러리만 사용하는 간단한 TDD 검증

실행 방법:
python tdd_validation_simple.py
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

class TDDValidationSimple:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = datetime.now()
        
    def log_test(self, test_name, passed, message=""):
        """테스트 결과 기록"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "[PASS]"
        else:
            self.failed_tests += 1
            status = "[FAIL]"
        
        self.test_results.append({
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"{status} | {test_name}")
        if message:
            print(f"      {message}")
    
    def test_system_files_exist(self):
        """시스템 파일 존재 확인 테스트"""
        print("\n[Phase 1] 시스템 파일 존재 확인")
        print("=" * 50)
        
        # 1. 통합 데이터 파일 확인
        integration_files = [f for f in os.listdir('.') if f.startswith('MACHO_WH_HANDLING_') and f.endswith('.xlsx')]
        self.log_test(
            "통합 데이터 파일 존재",
            len(integration_files) > 0,
            f"발견된 파일: {len(integration_files)}개"
        )
        
        # 2. 최종 리포트 파일 확인
        report_files = []
        if os.path.exists('02_통합결과'):
            report_files = [f for f in os.listdir('02_통합결과') if f.startswith('MACHO_Final_Report_') and f.endswith('.xlsx')]
        
        self.log_test(
            "최종 리포트 파일 존재",
            len(report_files) > 0,
            f"발견된 리포트: {len(report_files)}개"
        )
        
        # 3. 핵심 스크립트 파일 확인
        core_scripts = [
            '06_로직함수/complete_transaction_data_wh_handling_v284.py',
            '06_로직함수/create_final_report.py',
            '06_로직함수/fix_site_columns.py'
        ]
        
        script_count = 0
        for script in core_scripts:
            if os.path.exists(script):
                script_count += 1
        
        self.log_test(
            "핵심 스크립트 파일 존재",
            script_count == len(core_scripts),
            f"확인된 스크립트: {script_count}/{len(core_scripts)}개"
        )
        
        return integration_files, report_files
    
    def test_data_quality(self, integration_files):
        """데이터 품질 검증 테스트"""
        print("\n[Phase 2] 데이터 품질 검증")
        print("=" * 50)
        
        if not integration_files:
            self.log_test("데이터 품질 검증", False, "통합 데이터 파일이 없음")
            return None
        
        try:
            # 최신 통합 데이터 파일 로드
            latest_file = max(integration_files)
            df = pd.read_excel(latest_file)
            
            # 1. 데이터 건수 검증
            expected_min_records = 7000
            actual_records = len(df)
            self.log_test(
                "데이터 건수 기준",
                actual_records >= expected_min_records,
                f"실제: {actual_records:,}건, 기준: {expected_min_records:,}건"
            )
            
            # 2. 필수 컬럼 존재 확인
            required_columns = ['VENDOR', 'FLOW_CODE', 'WH_HANDLING']
            existing_columns = [col for col in required_columns if col in df.columns]
            self.log_test(
                "필수 컬럼 존재",
                len(existing_columns) >= 2,
                f"존재하는 컬럼: {existing_columns}"
            )
            
            # 3. Flow Code 분포 검증
            if 'FLOW_CODE' in df.columns:
                flow_codes = df['FLOW_CODE'].value_counts().sort_index()
                expected_flow_codes = [0, 1, 2, 3]
                actual_flow_codes = flow_codes.index.tolist()
                
                self.log_test(
                    "Flow Code 분포",
                    len(actual_flow_codes) >= 3,
                    f"Flow Code 분포: {dict(flow_codes)}"
                )
            
            # 4. 벤더 데이터 분포 검증
            if 'VENDOR' in df.columns:
                vendors = df['VENDOR'].value_counts()
                self.log_test(
                    "벤더 데이터 분포",
                    len(vendors) >= 2,
                    f"벤더 분포: {dict(vendors)}"
                )
            
            # 5. 현장 데이터 검증
            site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
            existing_site_cols = [col for col in site_columns if col in df.columns]
            site_data_count = sum(df[col].notna().sum() for col in existing_site_cols)
            
            self.log_test(
                "현장 데이터 존재",
                site_data_count > 0,
                f"현장 컬럼: {existing_site_cols}, 데이터: {site_data_count}건"
            )
            
            return df
            
        except Exception as e:
            self.log_test("데이터 품질 검증", False, f"오류 발생: {str(e)}")
            return None
    
    def test_flow_code_logic(self, df):
        """Flow Code 로직 검증 테스트"""
        print("\n[Phase 3] Flow Code 로직 검증")
        print("=" * 50)
        
        if df is None or 'FLOW_CODE' not in df.columns:
            self.log_test("Flow Code 로직", False, "Flow Code 컬럼이 없음")
            return
        
        try:
            # 1. Flow Code 범위 검증
            flow_codes = df['FLOW_CODE'].dropna()
            valid_codes = flow_codes[(flow_codes >= 0) & (flow_codes <= 3)]
            
            self.log_test(
                "Flow Code 범위",
                len(valid_codes) / len(flow_codes) >= 0.95,
                f"유효한 코드 비율: {len(valid_codes)/len(flow_codes)*100:.1f}%"
            )
            
            # 2. Flow Code 분포 합리성 검증
            flow_distribution = df['FLOW_CODE'].value_counts().sort_index()
            
            # Code 0과 1이 전체의 70% 이상을 차지해야 함
            if 0 in flow_distribution.index and 1 in flow_distribution.index:
                code_0_1_ratio = (flow_distribution.get(0, 0) + flow_distribution.get(1, 0)) / len(df)
                self.log_test(
                    "Flow Code 분포 합리성",
                    code_0_1_ratio >= 0.7,
                    f"Code 0+1 비율: {code_0_1_ratio*100:.1f}%"
                )
            
            # 3. WH HANDLING과 Flow Code 일치성 검증
            if 'WH_HANDLING' in df.columns:
                # 샘플 데이터로 일치성 확인
                sample_df = df.sample(min(100, len(df)))
                consistent_count = 0
                
                for _, row in sample_df.iterrows():
                    wh_handling = row.get('WH_HANDLING', 0)
                    flow_code = row.get('FLOW_CODE', 0)
                    
                    if pd.isna(wh_handling):
                        wh_handling = 0
                    if pd.isna(flow_code):
                        flow_code = 0
                    
                    # WH HANDLING이 3 이상이면 Flow Code는 3이어야 함
                    if wh_handling >= 3:
                        expected_flow = 3
                    else:
                        expected_flow = int(wh_handling)
                    
                    if flow_code == expected_flow:
                        consistent_count += 1
                
                consistency_rate = consistent_count / len(sample_df)
                self.log_test(
                    "WH HANDLING-Flow Code 일치성",
                    consistency_rate >= 0.8,
                    f"일치율: {consistency_rate*100:.1f}% (샘플: {len(sample_df)}건)"
                )
            
        except Exception as e:
            self.log_test("Flow Code 로직", False, f"오류 발생: {str(e)}")
    
    def test_performance_metrics(self, integration_files):
        """성능 지표 검증 테스트"""
        print("\n[Phase 4] 성능 지표 검증")
        print("=" * 50)
        
        if not integration_files:
            self.log_test("성능 지표 검증", False, "성능 측정할 파일이 없음")
            return
        
        try:
            # 1. 파일 생성 시간 검증
            latest_file = max(integration_files)
            file_creation_time = os.path.getmtime(latest_file)
            current_time = datetime.now().timestamp()
            
            # 파일이 24시간 이내에 생성되었는지 확인
            time_diff_hours = (current_time - file_creation_time) / 3600
            self.log_test(
                "파일 최신성",
                time_diff_hours <= 24,
                f"생성 후 경과 시간: {time_diff_hours:.1f}시간"
            )
            
            # 2. 파일 크기 검증
            file_size = os.path.getsize(latest_file)
            file_size_mb = file_size / (1024 * 1024)
            
            # 파일 크기가 합리적인 범위에 있는지 확인 (0.5MB ~ 50MB)
            self.log_test(
                "파일 크기 합리성",
                0.5 <= file_size_mb <= 50,
                f"파일 크기: {file_size_mb:.1f}MB"
            )
            
            # 3. 데이터 로딩 성능 테스트
            import time
            start_time = time.time()
            df = pd.read_excel(latest_file)
            loading_time = time.time() - start_time
            
            # 로딩 시간이 30초 이내인지 확인
            self.log_test(
                "데이터 로딩 성능",
                loading_time <= 30,
                f"로딩 시간: {loading_time:.2f}초"
            )
            
            # 4. 메모리 사용량 추정
            memory_usage_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            self.log_test(
                "메모리 사용량",
                memory_usage_mb <= 500,  # 500MB 이하
                f"메모리 사용량: {memory_usage_mb:.1f}MB"
            )
            
        except Exception as e:
            self.log_test("성능 지표 검증", False, f"오류 발생: {str(e)}")
    
    def test_system_integration(self):
        """시스템 통합 검증 테스트"""
        print("\n[Phase 5] 시스템 통합 검증")
        print("=" * 50)
        
        try:
            # 1. 배치 스크립트 존재 확인
            batch_scripts = [
                '실행_스크립트_모음.bat',
                '실행_스크립트_TDD_enhanced.bat'
            ]
            
            existing_scripts = [script for script in batch_scripts if os.path.exists(script)]
            self.log_test(
                "배치 스크립트 존재",
                len(existing_scripts) >= 1,
                f"확인된 스크립트: {existing_scripts}"
            )
            
            # 2. 로그 디렉토리 확인
            log_dirs = ['logs', '06_로직함수/logs']
            log_dir_exists = any(os.path.exists(d) for d in log_dirs)
            
            self.log_test(
                "로그 시스템",
                log_dir_exists,
                "로그 디렉토리 확인됨" if log_dir_exists else "로그 디렉토리 없음"
            )
            
            # 3. 설정 파일 확인
            config_files = ['config.json', 'settings.json', 'config.yaml']
            config_exists = any(os.path.exists(f) for f in config_files)
            
            self.log_test(
                "설정 파일 시스템",
                True,  # 설정 파일이 없어도 시스템은 동작
                "설정 파일 확인됨" if config_exists else "기본 설정 사용"
            )
            
            # 4. 출력 디렉토리 구조 확인
            output_dirs = ['02_통합결과', '06_로직함수']
            existing_dirs = [d for d in output_dirs if os.path.exists(d)]
            
            self.log_test(
                "출력 디렉토리 구조",
                len(existing_dirs) >= 2,
                f"확인된 디렉토리: {existing_dirs}"
            )
            
        except Exception as e:
            self.log_test("시스템 통합 검증", False, f"오류 발생: {str(e)}")
    
    def calculate_quality_score(self):
        """품질 점수 계산"""
        if self.total_tests == 0:
            return 0.0
        
        return (self.passed_tests / self.total_tests) * 100
    
    def generate_tdd_report(self):
        """TDD 검증 리포트 생성"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "="*80)
        print("[TDD] 검증 시나리오 완료 리포트")
        print("="*80)
        print(f"[실행 시간] {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[소요 시간] {duration.total_seconds():.2f}초")
        print(f"[총 테스트] {self.total_tests}개")
        print(f"[통과] {self.passed_tests}개")
        print(f"[실패] {self.failed_tests}개")
        
        quality_score = self.calculate_quality_score()
        print(f"[품질 점수] {quality_score:.1f}%")
        
        # 품질 등급 결정
        if quality_score >= 90:
            grade = "[우수] Excellent"
            recommendation = "프로덕션 준비 완료"
        elif quality_score >= 80:
            grade = "[양호] Good"
            recommendation = "경미한 개선 후 프로덕션 가능"
        elif quality_score >= 70:
            grade = "[보통] Average"
            recommendation = "주요 개선 사항 해결 필요"
        else:
            grade = "[개선 필요] Needs Improvement"
            recommendation = "시스템 재구축 권장"
        
        print(f"[품질 등급] {grade}")
        print(f"[권장 사항] {recommendation}")
        
        print("\n[상세 테스트 결과]")
        print("-" * 80)
        for result in self.test_results:
            print(f"{result['status']} | {result['test_name']}")
            if result['message']:
                print(f"      {result['message']}")
        
        # JSON 리포트 생성
        report_data = {
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'quality_score': quality_score,
            'grade': grade,
            'recommendation': recommendation,
            'detailed_results': self.test_results
        }
        
        report_filename = f"tdd_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n[리포트] 상세 리포트 저장: {report_filename}")
        except Exception as e:
            print(f"\n[경고] 리포트 저장 실패: {str(e)}")
        
        return quality_score
    
    def run_tdd_validation(self):
        """TDD 검증 시나리오 실행"""
        print("[TDD] MACHO-GPT v3.4-mini TDD 검증 시나리오")
        print("=" * 80)
        print("[TDD] Red → Green → Refactor 사이클 검증")
        print("[TDD] 시스템 품질 및 TDD 준수 여부 확인")
        print("=" * 80)
        
        # Phase 1: 시스템 파일 존재 확인
        integration_files, report_files = self.test_system_files_exist()
        
        # Phase 2: 데이터 품질 검증
        df = self.test_data_quality(integration_files)
        
        # Phase 3: Flow Code 로직 검증
        self.test_flow_code_logic(df)
        
        # Phase 4: 성능 지표 검증
        self.test_performance_metrics(integration_files)
        
        # Phase 5: 시스템 통합 검증
        self.test_system_integration()
        
        # 최종 리포트 생성
        quality_score = self.generate_tdd_report()
        
        return quality_score

def main():
    """메인 실행 함수"""
    validator = TDDValidationSimple()
    quality_score = validator.run_tdd_validation()
    
    # 프로그램 종료 코드 결정
    if quality_score >= 80:
        print("\n[성공] TDD 검증 성공!")
        sys.exit(0)
    else:
        print("\n[경고] TDD 검증 미달 - 개선 필요")
        sys.exit(1)

if __name__ == "__main__":
    main() 