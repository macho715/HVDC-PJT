#!/usr/bin/env python3
"""
TDD Test Suite for CorrectInventoryCalculator
HVDC 프로젝트 재고 계산기 테스트

목표: HITACHI 5,126개, SIMENSE 1,853개, Total 6,979개 정확한 계산 검증
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import SIMPLE.PY
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SIMPLE import CorrectInventoryCalculator


class TestCorrectInventoryCalculatorInitialization(unittest.TestCase):
    """CorrectInventoryCalculator 초기화 테스트"""
    
    def test_should_initialize_with_correct_location_mappings(self):
        """위치 매핑이 올바르게 초기화되어야 함"""
        # Given: CorrectInventoryCalculator 인스턴스 생성
        calculator = CorrectInventoryCalculator()
        
        # Then: 위치 매핑이 올바르게 설정되어야 함
        expected_sites = ['AGI', 'DAS', 'MIR', 'SHU']
        expected_warehouses = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP',
            'MOSB', 'AAA Storage', 'Hauler Indoor', 'DHL Warehouse'
        ]
        
        self.assertEqual(calculator.location_mappings['sites'], expected_sites)
        self.assertEqual(calculator.location_mappings['warehouses'], expected_warehouses)
        self.assertEqual(calculator.location_mappings['special'], ['Pre Arrival'])
    
    def test_should_initialize_with_correct_vendor_mappings(self):
        """벤더 매핑이 올바르게 초기화되어야 함"""
        # Given: CorrectInventoryCalculator 인스턴스 생성
        calculator = CorrectInventoryCalculator()
        
        # Then: 벤더 매핑이 올바르게 설정되어야 함
        expected_hitachi = ['HITACHI', 'HE', 'Hitachi']
        expected_simense = ['SIMENSE', 'SIM', 'Siemens', 'SIEMENS']
        
        self.assertEqual(calculator.vendor_mappings['HITACHI'], expected_hitachi)
        self.assertEqual(calculator.vendor_mappings['SIMENSE'], expected_simense)


class TestCorrectInventoryCalculatorDataPreparation(unittest.TestCase):
    """데이터 준비 및 정제 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.calculator = CorrectInventoryCalculator()
        
        # 테스트용 데이터프레임 생성
        self.test_data = pd.DataFrame({
            'Case No.': ['CASE001', 'CASE002', 'CASE003'],
            'HVDC CODE 3': ['HE', 'SIM', 'SCT'],
            'DSV Indoor': ['2024-01-01', '2024-01-02', None],
            'DSV Outdoor': [None, None, '2024-01-03'],
            'Status_Location': ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz'],
            'Status_Current': ['In Stock', 'In Stock', 'Pre Arrival']
        })
    
    def test_should_create_vendor_column_from_hvdc_code_3(self):
        """HVDC CODE 3에서 Vendor 컬럼을 올바르게 생성해야 함"""
        # When: 데이터 준비 실행
        result = self.calculator._prepare_data(self.test_data)
        
        # Then: Vendor 컬럼이 올바르게 생성되어야 함
        expected_vendors = ['HITACHI', 'SIMENSE', 'SAMSUNG']
        self.assertListEqual(result['Vendor'].tolist(), expected_vendors)
    
    def test_should_handle_missing_hvdc_code_3_column(self):
        """HVDC CODE 3 컬럼이 없을 때 Unknown으로 설정해야 함"""
        # Given: HVDC CODE 3 컬럼이 없는 데이터
        data_without_code = self.test_data.drop('HVDC CODE 3', axis=1)
        
        # When: 데이터 준비 실행
        result = self.calculator._prepare_data(data_without_code)
        
        # Then: Vendor가 Unknown으로 설정되어야 함
        self.assertTrue(all(result['Vendor'] == 'Unknown'))
    
    def test_should_create_location_column_from_date_columns(self):
        """날짜 컬럼에서 Location 컬럼을 올바르게 생성해야 함"""
        # When: 데이터 준비 실행
        result = self.calculator._prepare_data(self.test_data)
        
        # Then: Location 컬럼이 생성되어야 함
        self.assertIn('Location', result.columns)
        # 첫 번째 행은 DSV Indoor (2024-01-01이 가장 최신)
        self.assertEqual(result.iloc[0]['Location'], 'DSV Indoor')


class TestCorrectInventoryCalculatorLocationCalculation(unittest.TestCase):
    """현재 위치 계산 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.calculator = CorrectInventoryCalculator()
        
        self.test_data = pd.DataFrame({
            'Status_Location': ['DSV Indoor', 'DSV Outdoor', None, 'Pre Arrival'],
            'Status_Current': ['In Stock', 'In Stock', 'Pre Arrival', 'In Stock'],
            'DSV Indoor': ['2024-01-01', None, None, None],
            'DSV Outdoor': [None, '2024-01-02', None, None],
            'AGI': [None, None, '2024-01-03', None],
            'Vendor': ['HITACHI', 'SIMENSE', 'HITACHI', 'SIMENSE']
        })
    
    def test_should_use_status_location_when_available(self):
        """Status_Location이 있으면 그것을 사용해야 함"""
        # When: 현재 위치 계산 실행
        result = self.calculator._calculate_current_location(self.test_data)
        
        # Then: Status_Location 값이 Current_Location에 반영되어야 함
        self.assertEqual(result.iloc[0]['Current_Location'], 'DSV Indoor')
        self.assertEqual(result.iloc[1]['Current_Location'], 'DSV Outdoor')
    
    def test_should_identify_pre_arrival_status_correctly(self):
        """Pre Arrival 상태를 올바르게 식별해야 함"""
        # When: 현재 위치 계산 실행
        result = self.calculator._calculate_current_location(self.test_data)
        
        # Then: Pre Arrival 상태가 올바르게 식별되어야 함
        self.assertEqual(result.iloc[2]['Current_Location'], 'Pre Arrival')
    
    def test_should_fallback_to_dsv_indoor_when_no_location_found(self):
        """위치를 찾을 수 없을 때 DSV Indoor로 기본 설정해야 함"""
        # Given: 모든 위치 정보가 없는 데이터
        empty_data = pd.DataFrame({
            'Status_Location': [None, None],
            'Status_Current': ['In Stock', 'In Stock'],
            'Vendor': ['HITACHI', 'SIMENSE']
        })
        
        # When: 현재 위치 계산 실행
        result = self.calculator._calculate_current_location(empty_data)
        
        # Then: DSV Indoor로 기본 설정되어야 함
        self.assertEqual(result.iloc[0]['Current_Location'], 'DSV Indoor')
        self.assertEqual(result.iloc[1]['Current_Location'], 'DSV Indoor')


class TestCorrectInventoryCalculatorVendorClassification(unittest.TestCase):
    """벤더 분류 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.calculator = CorrectInventoryCalculator()
        
        self.test_data = pd.DataFrame({
            'Vendor': ['HITACHI', 'HE', 'Hitachi', 'SIMENSE', 'SIM', 'Siemens', 'SIEMENS', 'SCT', 'Unknown']
        })
    
    def test_should_classify_hitachi_variants_correctly(self):
        """HITACHI 변형들을 올바르게 분류해야 함"""
        # When: 벤더 분류 실행
        result = self.calculator._classify_vendor_correctly(self.test_data)
        
        # Then: HITACHI 변형들이 올바르게 분류되어야 함
        hitachi_rows = result[result['Vendor_Clean'] == 'HITACHI']
        self.assertEqual(len(hitachi_rows), 3)  # HITACHI, HE, Hitachi
    
    def test_should_classify_simense_variants_correctly(self):
        """SIMENSE 변형들을 올바르게 분류해야 함"""
        # When: 벤더 분류 실행
        result = self.calculator._classify_vendor_correctly(self.test_data)
        
        # Then: SIMENSE 변형들이 올바르게 분류되어야 함
        simense_rows = result[result['Vendor_Clean'] == 'SIMENSE']
        self.assertEqual(len(simense_rows), 4)  # SIMENSE, SIM, Siemens, SIEMENS
    
    def test_should_handle_unknown_vendors(self):
        """알 수 없는 벤더를 Other로 분류해야 함"""
        # When: 벤더 분류 실행
        result = self.calculator._classify_vendor_correctly(self.test_data)
        
        # Then: 알 수 없는 벤더가 Other로 분류되어야 함
        other_rows = result[result['Vendor_Clean'] == 'Other']
        self.assertEqual(len(other_rows), 2)  # SCT, Unknown


class TestCorrectInventoryCalculatorAggregation(unittest.TestCase):
    """집계 계산 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.calculator = CorrectInventoryCalculator()
        
        # 완전히 처리된 테스트 데이터
        self.processed_data = pd.DataFrame({
            'Current_Location': ['DSV Indoor', 'DSV Indoor', 'DSV Outdoor', 'DSV Outdoor', 'AGI', 'AGI'],
            'Vendor_Clean': ['HITACHI', 'SIMENSE', 'HITACHI', 'SIMENSE', 'HITACHI', 'SIMENSE']
        })
    
    def test_should_aggregate_by_location_and_vendor(self):
        """위치별/벤더별로 올바르게 집계해야 함"""
        # When: 집계 실행
        result = self.calculator._aggregate_by_location_vendor(self.processed_data)
        
        # Then: 집계 결과가 올바르게 계산되어야 함
        self.assertEqual(result['by_location_vendor']['DSV Indoor']['HITACHI'], 1)
        self.assertEqual(result['by_location_vendor']['DSV Indoor']['SIMENSE'], 1)
        self.assertEqual(result['by_location_vendor']['DSV Outdoor']['HITACHI'], 1)
        self.assertEqual(result['by_location_vendor']['DSV Outdoor']['SIMENSE'], 1)
        self.assertEqual(result['by_location_vendor']['AGI']['HITACHI'], 1)
        self.assertEqual(result['by_location_vendor']['AGI']['SIMENSE'], 1)
    
    def test_should_calculate_vendor_totals_correctly(self):
        """벤더별 총합을 올바르게 계산해야 함"""
        # When: 집계 실행
        result = self.calculator._aggregate_by_location_vendor(self.processed_data)
        
        # Then: 벤더별 총합이 올바르게 계산되어야 함
        self.assertEqual(result['totals_by_vendor']['HITACHI'], 3)
        self.assertEqual(result['totals_by_vendor']['SIMENSE'], 3)
    
    def test_should_calculate_location_totals_correctly(self):
        """위치별 총합을 올바르게 계산해야 함"""
        # When: 집계 실행
        result = self.calculator._aggregate_by_location_vendor(self.processed_data)
        
        # Then: 위치별 총합이 올바르게 계산되어야 함
        self.assertEqual(result['totals_by_location']['DSV Indoor'], 2)
        self.assertEqual(result['totals_by_location']['DSV Outdoor'], 2)
        self.assertEqual(result['totals_by_location']['AGI'], 2)
    
    def test_should_calculate_grand_total_correctly(self):
        """전체 총합을 올바르게 계산해야 함"""
        # When: 집계 실행
        result = self.calculator._aggregate_by_location_vendor(self.processed_data)
        
        # Then: 전체 총합이 올바르게 계산되어야 함
        self.assertEqual(result['grand_total'], 6)


class TestCorrectInventoryCalculatorTargetValidation(unittest.TestCase):
    """목표 숫자 검증 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.calculator = CorrectInventoryCalculator()
        
        # 목표 숫자와 일치하는 테스트 결과
        self.target_result = {
            'totals_by_vendor': {
                'HITACHI': 5126,
                'SIMENSE': 1853
            },
            'grand_total': 6979
        }
        
        # 목표 숫자와 다른 테스트 결과
        self.wrong_result = {
            'totals_by_vendor': {
                'HITACHI': 5000,
                'SIMENSE': 1800
            },
            'grand_total': 6800
        }
    
    def test_should_validate_correct_target_numbers(self):
        """올바른 목표 숫자에 대해 검증이 통과해야 함"""
        # When: 목표 숫자 검증 실행
        validation = self.calculator.validate_against_target(self.target_result)
        
        # Then: 모든 검증이 통과해야 함
        self.assertTrue(validation['hitachi_match'])
        self.assertTrue(validation['simense_match'])
        self.assertTrue(validation['total_match'])
    
    def test_should_fail_validation_for_wrong_numbers(self):
        """잘못된 숫자에 대해 검증이 실패해야 함"""
        # When: 목표 숫자 검증 실행
        validation = self.calculator.validate_against_target(self.wrong_result)
        
        # Then: 모든 검증이 실패해야 함
        self.assertFalse(validation['hitachi_match'])
        self.assertFalse(validation['simense_match'])
        self.assertFalse(validation['total_match'])


class TestCorrectInventoryCalculatorIntegration(unittest.TestCase):
    """통합 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.calculator = CorrectInventoryCalculator()
        
        # 통합 테스트용 데이터
        self.integration_data = pd.DataFrame({
            'Case No.': [f'CASE{i:03d}' for i in range(1, 11)],
            'HVDC CODE 3': ['HE', 'SIM', 'HE', 'SIM', 'HE', 'SIM', 'HE', 'SIM', 'HE', 'SIM'],
            'Status_Location': ['DSV Indoor', 'DSV Outdoor', 'AGI', 'DSV Indoor', 'DSV Outdoor', 
                               'AGI', 'DSV Indoor', 'DSV Outdoor', 'AGI', 'DSV Indoor'],
            'Status_Current': ['In Stock'] * 10,
            'DSV Indoor': ['2024-01-01', None, None, '2024-01-04', None, 
                          None, '2024-01-07', None, None, '2024-01-10'],
            'DSV Outdoor': [None, '2024-01-02', None, None, '2024-01-05', 
                           None, None, '2024-01-08', None, None],
            'AGI': [None, None, '2024-01-03', None, None, 
                   '2024-01-06', None, None, '2024-01-09', None]
        })
    
    def test_should_calculate_complete_inventory_snapshot(self):
        """완전한 재고 스냅샷을 계산해야 함"""
        # When: 완전한 재고 계산 실행
        result = self.calculator.calculate_current_inventory_snapshot(self.integration_data)
        
        # Then: 결과가 올바른 구조를 가져야 함
        self.assertIn('by_location_vendor', result)
        self.assertIn('totals_by_vendor', result)
        self.assertIn('totals_by_location', result)
        self.assertIn('grand_total', result)
        
        # Then: 총합이 올바르게 계산되어야 함
        self.assertEqual(result['grand_total'], 10)
        self.assertEqual(result['totals_by_vendor']['HITACHI'], 5)
        self.assertEqual(result['totals_by_vendor']['SIMENSE'], 5)


class TestCorrectInventoryCalculatorEdgeCases(unittest.TestCase):
    """엣지 케이스 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.calculator = CorrectInventoryCalculator()
    
    def test_should_handle_empty_dataframe(self):
        """빈 데이터프레임을 올바르게 처리해야 함"""
        # Given: 빈 데이터프레임
        empty_df = pd.DataFrame()
        
        # When: 재고 계산 실행
        result = self.calculator.calculate_current_inventory_snapshot(empty_df)
        
        # Then: 빈 결과가 반환되어야 함
        self.assertEqual(result['grand_total'], 0)
        self.assertEqual(result['totals_by_vendor']['HITACHI'], 0)
        self.assertEqual(result['totals_by_vendor']['SIMENSE'], 0)
    
    def test_should_handle_missing_columns(self):
        """누락된 컬럼을 올바르게 처리해야 함"""
        # Given: 최소한의 데이터프레임
        minimal_df = pd.DataFrame({
            'Case No.': ['CASE001']
        })
        
        # When: 재고 계산 실행
        result = self.calculator.calculate_current_inventory_snapshot(minimal_df)
        
        # Then: 기본값으로 처리되어야 함
        self.assertEqual(result['grand_total'], 1)
        self.assertIn('Unknown', result['totals_by_vendor'])
    
    def test_should_handle_null_values(self):
        """NULL 값을 올바르게 처리해야 함"""
        # Given: NULL 값이 포함된 데이터
        null_data = pd.DataFrame({
            'Case No.': ['CASE001', 'CASE002'],
            'HVDC CODE 3': [None, 'HE'],
            'Status_Location': [None, 'DSV Indoor'],
            'Status_Current': [None, 'In Stock']
        })
        
        # When: 재고 계산 실행
        result = self.calculator.calculate_current_inventory_snapshot(null_data)
        
        # Then: NULL 값이 올바르게 처리되어야 함
        self.assertEqual(result['grand_total'], 2)


def run_all_tests():
    """모든 테스트 실행"""
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스들 추가
    test_classes = [
        TestCorrectInventoryCalculatorInitialization,
        TestCorrectInventoryCalculatorDataPreparation,
        TestCorrectInventoryCalculatorLocationCalculation,
        TestCorrectInventoryCalculatorVendorClassification,
        TestCorrectInventoryCalculatorAggregation,
        TestCorrectInventoryCalculatorTargetValidation,
        TestCorrectInventoryCalculatorIntegration,
        TestCorrectInventoryCalculatorEdgeCases
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 HVDC 프로젝트 CorrectInventoryCalculator TDD 테스트 시작")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ 모든 테스트 통과!")
    else:
        print("❌ 일부 테스트 실패")
    
    print("\n🔧 **추천 명령어:**")
    print("/test-scenario unit-tests [TDD 사이클 검증 - 현재 테스트 상태 확인]")
    print("/validate-data code-quality [코드 품질 표준 준수 검증 - 물류 도메인 특화]")
    print("/automate test-pipeline [자동화된 테스트 파이프라인 구축 - CI/CD 통합]") 