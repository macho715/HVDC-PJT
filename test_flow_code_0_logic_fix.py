#!/usr/bin/env python3
"""
TDD Green Phase: FLOW CODE 0 로직 보정 테스트
MACHO-GPT v3.4-mini | TDD 방식으로 2,543건 차이 해결

테스트 목적:
1. determine_flow_code 함수 수정 검증
2. 실제 Pre Arrival 상태 식별 로직 추가 검증
3. WH HANDLING NaN 처리 방식 개선 검증
4. 검증 로직 강화 검증
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 개선된 Flow Code 시스템 import
from improved_flow_code_system import (
    improved_flow_code_system, 
    enhanced_flow_code_validator,
    enhanced_validator,
    run_improved_flow_code_logic
)

class TestFlowCode0LogicFix(unittest.TestCase):
    """FLOW CODE 0 로직 보정 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정 초기화"""
        self.warehouse_columns = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB']
        self.site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 예상 결과 (보정 목표)
        self.expected_flow_code_0_count = 2845
        self.actual_flow_code_0_count = 302
        self.difference_to_fix = 2543
        
    def test_should_identify_actual_pre_arrival_status(self):
        """Test: 실제 Pre Arrival 상태를 정확히 식별해야 함"""
        # Given: 모든 창고와 현장 컬럼이 비어있는 레코드
        pre_arrival_row = pd.Series({
            'Case No.': 'TEST001',
            'DSV Indoor': None,
            'DSV Al Markaz': None,
            'DSV Outdoor': None,
            'AAA  Storage': None,
            'Hauler Indoor': None,
            'DSV MZP': None,
            'MOSB': None,
            'AGI': None,
            'DAS': None,
            'MIR': None,
            'SHU': None,
            'WH_HANDLING': np.nan
        })
        
        # When: Pre Arrival 상태 식별 함수 실행
        result = improved_flow_code_system.is_actual_pre_arrival(pre_arrival_row)
        
        # Then: True를 반환해야 함
        self.assertTrue(result, "모든 위치 데이터가 비어있으면 Pre Arrival로 식별되어야 함")
    
    def test_should_not_identify_warehouse_data_as_pre_arrival(self):
        """Test: 창고 데이터가 있으면 Pre Arrival로 식별하지 않아야 함"""
        # Given: 창고 데이터가 있는 레코드
        warehouse_row = pd.Series({
            'Case No.': 'TEST002',
            'DSV Indoor': '2024-01-15',
            'DSV Al Markaz': None,
            'DSV Outdoor': None,
            'AAA  Storage': None,
            'Hauler Indoor': None,
            'DSV MZP': None,
            'MOSB': None,
            'AGI': None,
            'DAS': None,
            'MIR': None,
            'SHU': None,
            'WH_HANDLING': 1
        })
        
        # When: Pre Arrival 상태 식별 함수 실행
        result = improved_flow_code_system.is_actual_pre_arrival(warehouse_row)
        
        # Then: False를 반환해야 함
        self.assertFalse(result, "창고 데이터가 있으면 Pre Arrival로 식별되지 않아야 함")
    
    def test_should_handle_nan_wh_handling_correctly(self):
        """Test: WH HANDLING NaN 값을 올바르게 처리해야 함"""
        # Given: WH_HANDLING이 NaN인 다양한 케이스
        test_cases = [
            {
                'description': 'Pre Arrival - 모든 위치 데이터 없음',
                'row': {'WH_HANDLING': np.nan, 'DSV Indoor': None, 'AGI': None},
                'expected_flow_code': 0
            },
            {
                'description': 'Not Pre Arrival - 현장 데이터 있음',
                'row': {'WH_HANDLING': np.nan, 'DSV Indoor': None, 'AGI': '2024-01-15'},
                'expected_flow_code': 1  # 기본값으로 변경
            },
            {
                'description': 'Not Pre Arrival - 창고 데이터 있지만 WH_HANDLING NaN',
                'row': {'WH_HANDLING': np.nan, 'DSV Indoor': '2024-01-15', 'AGI': None},
                'expected_flow_code': 1  # 기본값으로 변경
            }
        ]
        
        for case in test_cases:
            with self.subTest(description=case['description']):
                # When: 개선된 determine_flow_code 함수 실행
                result = improved_flow_code_system.determine_flow_code_improved(
                    case['row']['WH_HANDLING'], 
                    pd.Series(case['row'])
                )
                
                # Then: 예상 Flow Code와 일치해야 함
                self.assertEqual(result, case['expected_flow_code'], 
                                f"케이스 '{case['description']}'에서 예상 Flow Code {case['expected_flow_code']}와 일치하지 않음")
    
    def test_should_fix_2543_count_difference(self):
        """Test: 2,543건 차이를 해결해야 함"""
        # Given: 현재 문제 상황
        current_code_0_count = 302
        expected_code_0_count = 2845
        difference = expected_code_0_count - current_code_0_count
        
        # When: 로직 보정 후 Flow Code 0 재계산
        improved_code_0_count = run_improved_flow_code_logic()
        
        # Then: 차이가 2,543건 이하로 줄어야 함
        improved_difference = abs(expected_code_0_count - improved_code_0_count)
        self.assertLessEqual(improved_difference, 100, 
                            f"개선 후에도 차이가 100건을 초과함: {improved_difference}건")
    
    def test_should_validate_flow_code_distribution(self):
        """Test: Flow Code 분포 검증이 강화되어야 함"""
        # Given: 예상 Flow Code 분포
        expected_distribution = {
            0: 2845,  # Pre Arrival
            1: 3517,  # Port → Site
            2: 1131,  # Port → WH → Site
            3: 80     # Port → WH → MOSB → Site
        }
        
        # When: 검증 로직 실행
        actual_distribution = {0: 2800, 1: 3500, 2: 1150, 3: 85}  # 개선된 결과로 가정
        validation_result = enhanced_flow_code_validator.validate_distribution(actual_distribution)
        
        # Then: 검증이 통과해야 함
        self.assertTrue(validation_result['is_valid'], 
                       f"Flow Code 분포 검증 실패: {validation_result['errors']}")
    
    def test_should_handle_edge_cases(self):
        """Test: 엣지 케이스들을 올바르게 처리해야 함"""
        edge_cases = [
            {
                'description': '공백 문자열 처리',
                'wh_handling': '',
                'row_data': {'DSV Indoor': '   ', 'AGI': ''},
                'expected_flow_code': 0
            },
            {
                'description': '0 값 처리',
                'wh_handling': 0,
                'row_data': {'DSV Indoor': None, 'AGI': None},
                'expected_flow_code': 0
            },
            {
                'description': '음수 값 처리',
                'wh_handling': -1,
                'row_data': {'DSV Indoor': None, 'AGI': None},
                'expected_flow_code': 0
            },
            {
                'description': '매우 큰 값 처리',
                'wh_handling': 999,
                'row_data': {'DSV Indoor': '2024-01-15', 'AGI': None},
                'expected_flow_code': 3
            }
        ]
        
        for case in edge_cases:
            with self.subTest(description=case['description']):
                # When: 엣지 케이스 처리
                result = improved_flow_code_system.determine_flow_code_improved(
                    case['wh_handling'], 
                    pd.Series(case['row_data'])
                )
                
                # Then: 예상 결과와 일치해야 함
                self.assertEqual(result, case['expected_flow_code'], 
                                f"엣지 케이스 '{case['description']}'에서 예상 결과와 다름")
    
    def test_should_maintain_backward_compatibility(self):
        """Test: 기존 로직과의 호환성을 유지해야 함"""
        # Given: 기존 로직에서 정상 작동하던 케이스들
        backward_compatible_cases = [
            {'wh_handling': 1, 'expected_flow_code': 1},
            {'wh_handling': 2, 'expected_flow_code': 2},
            {'wh_handling': 3, 'expected_flow_code': 3},
            {'wh_handling': 4, 'expected_flow_code': 3}  # 3 이상은 모두 3
        ]
        
        for case in backward_compatible_cases:
            with self.subTest(wh_handling=case['wh_handling']):
                # When: 개선된 로직 실행
                result = improved_flow_code_system.determine_flow_code_improved(
                    case['wh_handling'], 
                    pd.Series({'DSV Indoor': '2024-01-15'})  # 창고 데이터 있음
                )
                
                # Then: 기존 로직과 동일한 결과
                self.assertEqual(result, case['expected_flow_code'], 
                                f"WH_HANDLING {case['wh_handling']}에서 기존 로직과 다른 결과")

class TestFlowCodeValidationEnhancement(unittest.TestCase):
    """Flow Code 검증 로직 강화 테스트"""
    
    def test_should_provide_detailed_validation_report(self):
        """Test: 상세한 검증 리포트를 제공해야 함"""
        # Given: 검증 대상 데이터
        test_data = {
            'actual_counts': {0: 2800, 1: 3500, 2: 1150, 3: 85},
            'expected_counts': {0: 2845, 1: 3517, 2: 1131, 3: 80}
        }
        
        # When: 상세 검증 실행
        validation_report = enhanced_validator.generate_detailed_report(test_data)
        
        # Then: 상세 리포트가 생성되어야 함
        self.assertIn('summary', validation_report)
        self.assertIn('code_wise_analysis', validation_report)
        self.assertIn('recommendations', validation_report)
    
    def test_should_identify_anomalies(self):
        """Test: 이상치를 식별해야 함"""
        # Given: 이상치가 포함된 데이터
        anomaly_data = {
            'case_no': 'ANOMALY001',
            'wh_handling': 100,  # 비정상적으로 큰 값
            'flow_code': 0,     # 불일치
            'warehouse_data': {'DSV Indoor': '2024-01-15'}  # Pre Arrival이 아님
        }
        
        # When: 이상치 감지 실행
        is_anomaly = enhanced_validator.detect_anomaly(anomaly_data)
        
        # Then: 이상치로 식별되어야 함
        self.assertTrue(is_anomaly, "명백한 이상치가 감지되지 않음")

def run_tests():
    """테스트 실행"""
    print("🧪 TDD Green Phase: FLOW CODE 0 로직 보정 테스트 시작")
    print("=" * 80)
    print("테스트 목적:")
    print("1. determine_flow_code 함수 수정 검증")
    print("2. 실제 Pre Arrival 상태 식별 로직 추가 검증")
    print("3. WH HANDLING NaN 처리 방식 개선 검증")
    print("4. 검증 로직 강화 검증")
    print("=" * 80)
    
    # 테스트 실행
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestFlowCode0LogicFix))
    suite.addTests(loader.loadTestsFromTestCase(TestFlowCodeValidationEnhancement))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 출력
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("🟢 GREEN PHASE 성공: 모든 테스트 통과!")
        print("다음 단계: REFACTOR PHASE - 코드 개선 및 최적화")
    else:
        print(f"🔴 일부 테스트 실패: {result.testsRun}개 테스트 중 {len(result.failures + result.errors)}개 실패")
        print("실패한 테스트를 확인하고 구현을 수정하세요.")
    print("=" * 80)
    
    return result

if __name__ == "__main__":
    run_tests() 