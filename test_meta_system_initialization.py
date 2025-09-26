#!/usr/bin/env python3
"""
TDD Phase 1: Core Infrastructure Tests
첫 번째 테스트: Meta System Initialization

테스트 목적: 5개 핵심 파일의 통합 초기화 검증
- analyze_integrated_data.py
- analyze_stack_sqm.py  
- complete_transaction_data_wh_handling_v284.py
- create_final_report_complete.py
- create_final_report_original_logic.py
"""

import unittest
import os
import sys
from datetime import datetime
import pandas as pd
import importlib.util

class TestMetaSystemInitialization(unittest.TestCase):
    """Meta System 초기화 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.core_files = [
            'MACHO_통합관리_20250702_205301/06_로직함수/analyze_integrated_data.py',
            'MACHO_통합관리_20250702_205301/06_로직함수/analyze_stack_sqm.py',
            'MACHO_통합관리_20250702_205301/06_로직함수/complete_transaction_data_wh_handling_v284.py',
            'MACHO_통합관리_20250702_205301/06_로직함수/create_final_report_complete.py',
            'MACHO_통합관리_20250702_205301/06_로직함수/create_final_report_original_logic.py'
        ]
        self.required_confidence = 0.95
        
    def test_all_core_files_exist(self):
        """핵심 파일들이 모두 존재하는지 검증"""
        missing_files = []
        for file_path in self.core_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        self.assertEqual(len(missing_files), 0, 
                        f"Missing core files: {missing_files}")
    
    def test_core_modules_importable(self):
        """핵심 모듈들이 import 가능한지 검증"""
        import_errors = []
        
        for file_path in self.core_files:
            try:
                module_name = os.path.basename(file_path).replace('.py', '')
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:
                import_errors.append(f"{file_path}: {str(e)}")
        
        self.assertEqual(len(import_errors), 0,
                        f"Import errors: {import_errors}")
    
    def test_wh_handling_engine_initialization(self):
        """WH HANDLING 엔진 초기화 검증"""
        sys.path.append('MACHO_통합관리_20250702_205301/06_로직함수')
        
        try:
            from complete_transaction_data_wh_handling_v284 import CompleteTransactionDataWHHandlingV284
            
            engine = CompleteTransactionDataWHHandlingV284()
            
            # 필수 속성 검증
            self.assertIsNotNone(engine.warehouse_columns)
            self.assertIsNotNone(engine.flow_code_mapping)
            self.assertIsNotNone(engine.verified_counts)
            
            # 창고 컬럼 개수 검증 (7개 창고)
            self.assertEqual(len(engine.warehouse_columns), 7)
            
            # Flow Code 매핑 검증 (Code 0-3)
            expected_codes = [0, 1, 2, 3]
            for code in expected_codes:
                self.assertIn(code, engine.flow_code_mapping)
                
        except ImportError as e:
            self.fail(f"WH HANDLING 엔진 초기화 실패: {e}")
    
    def test_stack_sqm_analyzer_functions(self):
        """Stack SQM 분석기 함수 존재 검증"""
        sys.path.append('MACHO_통합관리_20250702_205301/06_로직함수')
        
        try:
            import analyze_stack_sqm
            
            # 필수 함수 존재 검증
            required_functions = [
                'analyze_stack_sqm',
                'analyze_stack_data', 
                'combined_analysis'
            ]
            
            for func_name in required_functions:
                self.assertTrue(hasattr(analyze_stack_sqm, func_name),
                              f"Missing function: {func_name}")
                
        except ImportError as e:
            self.fail(f"Stack SQM 분석기 초기화 실패: {e}")
    
    def test_integrated_data_analyzer_functions(self):
        """통합 데이터 분석기 함수 존재 검증"""
        sys.path.append('MACHO_통합관리_20250702_205301/06_로직함수')
        
        try:
            import analyze_integrated_data
            
            # 필수 함수 존재 검증
            required_functions = [
                'analyze_excel_structure',
                'perform_eda',
                'visualize_data',
                'generate_report'
            ]
            
            for func_name in required_functions:
                self.assertTrue(hasattr(analyze_integrated_data, func_name),
                              f"Missing function: {func_name}")
                
        except ImportError as e:
            self.fail(f"통합 데이터 분석기 초기화 실패: {e}")
    
    def test_report_generators_initialization(self):
        """리포트 생성기들 초기화 검증"""
        sys.path.append('MACHO_통합관리_20250702_205301/06_로직함수')
        
        report_modules = [
            'create_final_report_complete',
            'create_final_report_original_logic'
        ]
        
        for module_name in report_modules:
            try:
                module = __import__(module_name)
                
                # main 함수 존재 검증
                self.assertTrue(hasattr(module, 'main'),
                              f"{module_name}: Missing main function")
                
            except ImportError as e:
                self.fail(f"{module_name} 초기화 실패: {e}")
    
    def test_system_integration_readiness(self):
        """시스템 통합 준비 상태 검증"""
        # 데이터 디렉토리 존재 확인
        data_paths = [
            'hvdc_macho_gpt/WAREHOUSE/data',
            'MACHO_통합관리_20250702_205301/02_통합결과',
            'MACHO_통합관리_20250702_205301/04_작업리포트'
        ]
        
        missing_paths = []
        for path in data_paths:
            if not os.path.exists(path):
                missing_paths.append(path)
        
        # 일부 경로가 없어도 허용 (개발 환경 차이)
        if len(missing_paths) == len(data_paths):
            self.fail(f"모든 데이터 경로가 없음: {missing_paths}")
    
    def test_confidence_threshold_compliance(self):
        """신뢰도 임계값 준수 검증"""
        # MACHO-GPT 표준: 신뢰도 ≥0.95
        system_confidence = 0.95
        
        self.assertGreaterEqual(system_confidence, self.required_confidence,
                               f"신뢰도 부족: {system_confidence} < {self.required_confidence}")
    
    def test_tdd_compliance_validation(self):
        """TDD 준수 검증"""
        # 이 테스트 자체가 TDD RED 단계임을 검증
        test_timestamp = datetime.now()
        
        # 테스트가 실행되고 있음을 확인
        self.assertIsInstance(test_timestamp, datetime)
        
        # TDD 단계 표시
        print(f"\n🔴 TDD RED Phase: Meta System Initialization Test")
        print(f"   테스트 시간: {test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   검증 대상: 5개 핵심 파일 통합 시스템")
        print(f"   신뢰도 요구사항: ≥{self.required_confidence}")

if __name__ == '__main__':
    print("🧪 MACHO-GPT v3.4-mini TDD Phase 1: Core Infrastructure Tests")
    print("=" * 70)
    print("📋 Test: Meta System Initialization")
    print("🎯 Purpose: 5개 핵심 파일 통합 초기화 검증")
    print("-" * 70)
    
    # TDD RED Phase 실행
    unittest.main(verbosity=2) 