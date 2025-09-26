#!/usr/bin/env python3
"""
TDD Green Phase: FLOW CODE 2 로직 보정 테스트
MACHO-GPT v3.4-mini | 2단계 경유 과다 집계 수정

테스트 목적:
1. FLOW CODE 2 과다 집계 수정 (현재 1,206건 → 목표 1,131건)
2. 창고 경유 로직 정교화
3. 다단계 이동 중복 제거
4. MOSB 경유 로직 강화
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
    run_improved_code_2_logic,
    calculate_improved_distribution
)

class TestFlowCode2LogicFix(unittest.TestCase):
    """FLOW CODE 2 로직 보정 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정 초기화"""
        self.warehouse_columns = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB']
        self.site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 목표 수치 (보정 대상)
        self.target_counts = {
            0: 2845,  # Pre Arrival
            1: 3517,  # Port → Site 직송
            2: 1131,  # Port → WH → Site (목표)
            3: 80     # Port → WH → MOSB → Site
        }
        
        # 현재 문제 상황
        self.current_code_2_count = 1206  # 과다 집계
        self.difference_to_fix = 1206 - 1131  # 75건 과다
        
    def test_should_identify_true_two_stage_routing(self):
        """Test: 진짜 2단계 경유를 정확히 식별해야 함"""
        # Given: 창고 1개 + 현장 1개 경유 (진짜 2단계)
        true_two_stage_row = pd.Series({
            'Case No.': 'TWO_STAGE_001',
            'DSV Indoor': '2024-01-15',  # 창고 1개
            'DSV Al Markaz': None,
            'DSV Outdoor': None,
            'AAA  Storage': None,
            'Hauler Indoor': None,
            'DSV MZP': None,
            'MOSB': None,
            'AGI': '2024-01-20',  # 현장 1개
            'DAS': None,
            'MIR': None,
            'SHU': None,
            'WH_HANDLING': 1
        })
        
        # When: 2단계 경유 식별 함수 실행
        is_true_two_stage = improved_flow_code_system.is_true_two_stage_routing(true_two_stage_row)
        
        # Then: True를 반환해야 함
        self.assertTrue(is_true_two_stage, "창고 1개 + 현장 1개 경유는 진짜 2단계로 식별되어야 함")
    
    def test_should_not_identify_false_two_stage_routing(self):
        """Test: 가짜 2단계 경유를 식별하지 않아야 함"""
        # Given: 창고 2개 경유 (실제로는 3단계 이상)
        false_two_stage_row = pd.Series({
            'Case No.': 'FALSE_TWO_STAGE_001',
            'DSV Indoor': '2024-01-15',   # 창고 1개
            'DSV Outdoor': '2024-01-18',  # 창고 2개
            'DSV Al Markaz': None,
            'AAA  Storage': None,
            'Hauler Indoor': None,
            'DSV MZP': None,
            'MOSB': None,
            'AGI': '2024-01-20',  # 현장 1개
            'DAS': None,
            'MIR': None,
            'SHU': None,
            'WH_HANDLING': 2
        })
        
        # When: 2단계 경유 식별 함수 실행
        is_true_two_stage = improved_flow_code_system.is_true_two_stage_routing(false_two_stage_row)
        
        # Then: False를 반환해야 함 (실제로는 3단계)
        self.assertFalse(is_true_two_stage, "창고 2개 경유는 2단계가 아니라 3단계로 분류되어야 함")
    
    def test_should_handle_mosb_routing_correctly(self):
        """Test: MOSB 경유 로직을 올바르게 처리해야 함"""
        # Given: MOSB 경유 케이스들
        test_cases = [
            {
                'description': 'MOSB만 경유 - 2단계',
                'row': {
                    'MOSB': '2024-01-15',
                    'AGI': '2024-01-20',
                    'DSV Indoor': None,
                    'DSV Outdoor': None
                },
                'expected_flow_code': 2
            },
            {
                'description': 'DSV + MOSB 경유 - 3단계',
                'row': {
                    'DSV Indoor': '2024-01-15',
                    'MOSB': '2024-01-18',
                    'AGI': '2024-01-20',
                    'DSV Outdoor': None
                },
                'expected_flow_code': 3
            },
            {
                'description': 'MOSB + 창고 2개 경유 - 3단계',
                'row': {
                    'DSV Indoor': '2024-01-15',
                    'DSV Outdoor': '2024-01-17',
                    'MOSB': '2024-01-18',
                    'AGI': '2024-01-20'
                },
                'expected_flow_code': 3
            }
        ]
        
        for case in test_cases:
            with self.subTest(description=case['description']):
                # When: MOSB 경유 로직 처리
                result = improved_flow_code_system.determine_flow_code_with_mosb_logic(
                    pd.Series(case['row'])
                )
                
                # Then: 예상 Flow Code와 일치해야 함
                self.assertEqual(result, case['expected_flow_code'], 
                                f"MOSB 케이스 '{case['description']}'에서 예상 결과와 다름")
    
    def test_should_fix_code_2_over_counting(self):
        """Test: Code 2 과다 집계를 수정해야 함"""
        # Given: 현재 문제 상황
        current_code_2_count = 1206
        target_code_2_count = 1131
        difference = current_code_2_count - target_code_2_count
        
        # When: 개선된 로직 적용
        improved_code_2_count = run_improved_code_2_logic()
        
        # Then: 과다 집계가 수정되어야 함
        improved_difference = abs(target_code_2_count - improved_code_2_count)
        self.assertLessEqual(improved_difference, 25, 
                            f"개선 후에도 차이가 25건을 초과함: {improved_difference}건")
    
    def test_should_eliminate_duplicate_multi_stage_movements(self):
        """Test: 다단계 이동 중복을 제거해야 함"""
        # Given: 중복 집계 가능성이 있는 케이스
        duplicate_movement_cases = [
            {
                'description': '동일 창고 중복 기록',
                'row': {
                    'Case No.': 'DUP001',
                    'DSV Indoor': '2024-01-15',
                    'DSV Indoor_2': '2024-01-16',  # 동일 창고 중복
                    'AGI': '2024-01-20'
                },
                'expected_warehouse_count': 1  # 중복 제거 후
            },
            {
                'description': '순환 이동 패턴',
                'row': {
                    'Case No.': 'CIRCULAR001',
                    'DSV Indoor': '2024-01-15',
                    'DSV Outdoor': '2024-01-17',
                    'DSV Indoor_return': '2024-01-18',  # 순환 이동
                    'AGI': '2024-01-20'
                },
                'expected_warehouse_count': 2  # 실제 경유 창고 수
            }
        ]
        
        for case in duplicate_movement_cases:
            with self.subTest(description=case['description']):
                # When: 중복 제거 로직 적용
                warehouse_count = improved_flow_code_system.count_unique_warehouses(
                    pd.Series(case['row'])
                )
                
                # Then: 중복이 제거되어야 함
                self.assertEqual(warehouse_count, case['expected_warehouse_count'],
                                f"중복 제거 케이스 '{case['description']}'에서 예상 창고 수와 다름")
    
    def test_should_handle_warehouse_sequence_logic(self):
        """Test: 창고 순서 로직을 올바르게 처리해야 함"""
        # Given: 창고 경유 순서가 중요한 케이스들
        sequence_cases = [
            {
                'description': '정상 순서: Port → WH → Site',
                'row': {
                    'DSV Indoor': '2024-01-15',
                    'AGI': '2024-01-20',
                    'departure_port': '2024-01-10'
                },
                'expected_valid': True
            },
            {
                'description': '비정상 순서: Site → WH (역순)',
                'row': {
                    'DSV Indoor': '2024-01-20',
                    'AGI': '2024-01-15',  # 현장이 창고보다 먼저
                    'departure_port': '2024-01-10'
                },
                'expected_valid': False
            },
            {
                'description': '동시 도착 (같은 날)',
                'row': {
                    'DSV Indoor': '2024-01-15',
                    'AGI': '2024-01-15',  # 같은 날
                    'departure_port': '2024-01-10'
                },
                'expected_valid': True  # 같은 날은 허용
            }
        ]
        
        for case in sequence_cases:
            with self.subTest(description=case['description']):
                # When: 창고 순서 검증
                is_valid_sequence = improved_flow_code_system.validate_warehouse_sequence(
                    pd.Series(case['row'])
                )
                
                # Then: 순서 검증이 올바르게 작동해야 함
                self.assertEqual(is_valid_sequence, case['expected_valid'],
                                f"순서 검증 케이스 '{case['description']}'에서 예상 결과와 다름")
    
    def test_should_recalculate_flow_code_distribution(self):
        """Test: Flow Code 분포를 재계산해야 함"""
        # Given: 목표 분포
        target_distribution = {
            0: 2845,  # Pre Arrival
            1: 3517,  # Port → Site
            2: 1131,  # Port → WH → Site (수정 목표)
            3: 80     # Port → WH → MOSB → Site
        }
        
        # When: 개선된 분포 계산
        improved_distribution = calculate_improved_distribution()
        
        # Then: Code 2가 목표에 근접해야 함
        code_2_difference = abs(target_distribution[2] - improved_distribution[2])
        self.assertLessEqual(code_2_difference, 50, 
                            f"Code 2 차이가 50건을 초과함: {code_2_difference}건")

class TestMultiStageRoutingLogic(unittest.TestCase):
    """다단계 경유 로직 테스트"""
    
    def test_should_distinguish_stage_levels_correctly(self):
        """Test: 단계 수준을 올바르게 구분해야 함"""
        # Given: 다양한 단계 수준 케이스
        stage_cases = [
            {
                'description': '1단계: Port → Site',
                'warehouses': 0,
                'sites': 1,
                'expected_stage': 1
            },
            {
                'description': '2단계: Port → WH → Site',
                'warehouses': 1,
                'sites': 1,
                'expected_stage': 2
            },
            {
                'description': '3단계: Port → WH → WH → Site',
                'warehouses': 2,
                'sites': 1,
                'expected_stage': 3
            },
            {
                'description': '3단계: Port → WH → MOSB → Site',
                'warehouses': 1,
                'sites': 1,
                'mosb': True,
                'expected_stage': 3
            }
        ]
        
        for case in stage_cases:
            with self.subTest(description=case['description']):
                # When: 단계 수준 계산
                stage_level = improved_flow_code_system.calculate_stage_level(
                    warehouses=case['warehouses'],
                    sites=case['sites'],
                    mosb=case.get('mosb', False)
                )
                
                # Then: 예상 단계 수준과 일치해야 함
                self.assertEqual(stage_level, case['expected_stage'],
                                f"단계 수준 케이스 '{case['description']}'에서 예상 결과와 다름")
    
    def test_should_handle_complex_routing_patterns(self):
        """Test: 복잡한 경유 패턴을 처리해야 함"""
        # Given: 복잡한 경유 패턴
        complex_patterns = [
            {
                'description': '병렬 창고 사용',
                'pattern': {
                    'DSV Indoor': '2024-01-15',
                    'DSV Outdoor': '2024-01-15',  # 동시 사용
                    'AGI': '2024-01-20'
                },
                'expected_flow_code': 3  # 2개 창고 = 3단계
            },
            {
                'description': '순차 창고 + MOSB',
                'pattern': {
                    'DSV Indoor': '2024-01-15',
                    'MOSB': '2024-01-18',
                    'DAS': '2024-01-20'
                },
                'expected_flow_code': 3  # 창고 + MOSB = 3단계
            }
        ]
        
        for case in complex_patterns:
            with self.subTest(description=case['description']):
                # When: 복잡한 패턴 처리
                flow_code = improved_flow_code_system.handle_complex_routing(
                    pd.Series(case['pattern'])
                )
                
                # Then: 예상 Flow Code와 일치해야 함
                self.assertEqual(flow_code, case['expected_flow_code'],
                                f"복잡한 패턴 '{case['description']}'에서 예상 결과와 다름")

def run_tests():
    """테스트 실행"""
    print("🧪 TDD Green Phase: FLOW CODE 2 로직 보정 테스트 시작")
    print("=" * 80)
    print("테스트 목적:")
    print("1. FLOW CODE 2 과다 집계 수정 (현재 1,206건 → 목표 1,131건)")
    print("2. 창고 경유 로직 정교화")
    print("3. 다단계 이동 중복 제거")
    print("4. MOSB 경유 로직 강화")
    print("=" * 80)
    
    # 테스트 실행
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestFlowCode2LogicFix))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiStageRoutingLogic))
    
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