#!/usr/bin/env python3
"""
TDD Red Phase: 월말 재고 vs 현재 위치 정합성 검증 테스트
MACHO-GPT v3.4-mini | 시스템 로직 보정 4단계

테스트 목적:
1. 월말 재고 수량과 현재 위치별 분산 수량 일치성 검증
2. 위치 이동 중 누락된 아이템 감지
3. 시간 기반 위치 변경 추적 및 검증
4. 재고 데이터 무결성 보장
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# 개선된 Flow Code 시스템 import
from improved_flow_code_system import improved_flow_code_system

# 재고 위치 정합성 검증 함수들 import
from inventory_location_consistency import (
    validate_quantity_consistency,
    detect_quantity_mismatch,
    validate_location_existence,
    detect_missing_location_data,
    validate_movement_timeline,
    detect_invalid_timeline,
    calculate_location_distribution,
    validate_monthly_stock_total,
    generate_consistency_report,
    detect_phantom_inventory,
    validate_location_capacity,
    track_movement_history,
    validate_data_completeness,
    detect_duplicate_entries
)

class TestInventoryLocationConsistency(unittest.TestCase):
    """월말 재고 vs 현재 위치 정합성 검증 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정 초기화"""
        self.warehouse_columns = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB']
        self.site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 테스트용 샘플 데이터
        self.sample_inventory_data = pd.DataFrame({
            'Case No.': ['INV001', 'INV002', 'INV003', 'INV004'],
            'Package': [100, 50, 200, 75],
            'Monthly_Stock': [100, 50, 200, 75],  # 월말 재고
            'Current_Location': ['DSV Indoor', 'AGI', 'DSV Outdoor', 'DAS'],
            'Last_Movement_Date': ['2024-01-15', '2024-01-20', '2024-01-18', '2024-01-22'],
            'DSV Indoor': ['2024-01-15', None, None, None],
            'DSV Outdoor': [None, None, '2024-01-18', None],
            'AGI': [None, '2024-01-20', None, None],
            'DAS': [None, None, None, '2024-01-22']
        })
        
        # 불일치 케이스 데이터
        self.inconsistent_data = pd.DataFrame({
            'Case No.': ['INC001', 'INC002', 'INC003'],
            'Package': [100, 50, 80],
            'Monthly_Stock': [100, 60, 80],  # 수량 불일치
            'Current_Location': ['DSV Indoor', 'Missing', 'DSV Outdoor'],  # 위치 누락
            'Last_Movement_Date': ['2024-01-15', None, '2024-01-18'],
            'DSV Indoor': ['2024-01-15', None, None],
            'DSV Outdoor': [None, None, '2024-01-18'],
            'AGI': [None, None, None]
        })
        
    def test_should_validate_inventory_quantity_consistency(self):
        """Test: 재고 수량 일치성을 검증해야 함"""
        # Given: 재고 데이터
        inventory_data = pd.DataFrame({
            'ITEM_ID': ['QTY001'],
            'QUANTITY': [100],
            'LOCATION': ['DSV Indoor']
        })
        
        location_data = pd.DataFrame({
            'ITEM_ID': ['QTY001'],
            'QTY': [100],
            'LOCATION': ['DSV Indoor']
        })
        
        # When: 수량 일치성 검증
        result = validate_quantity_consistency(inventory_data, location_data)
        
        # Then: 일치성을 확인해야 함
        self.assertIsNotNone(result, "검증 결과가 None이 아니어야 함")
        self.assertIn('consistent', result, "consistent 키가 있어야 함")
        self.assertIn('total_inventory', result, "total_inventory 키가 있어야 함")
        self.assertIn('total_location', result, "total_location 키가 있어야 함")
        self.assertIn('consistency_rate', result, "consistency_rate 키가 있어야 함")
    
    def test_should_detect_quantity_mismatch(self):
        """Test: 수량 불일치를 감지해야 함"""
        # Given: 수량 불일치 데이터
        inventory_data = pd.DataFrame({
            'ITEM_ID': ['MISMATCH001'],
            'QUANTITY': [100],
            'LOCATION': ['DSV Indoor']
        })
        
        location_data = pd.DataFrame({
            'ITEM_ID': ['MISMATCH001'],
            'QTY': [80],  # 20개 차이
            'LOCATION': ['DSV Indoor']
        })
        
        # When: 수량 불일치 감지
        mismatches = detect_quantity_mismatch(inventory_data, location_data)
        
        # Then: 불일치를 감지해야 함
        self.assertIsInstance(mismatches, list, "불일치 결과는 리스트여야 함")
        self.assertGreater(len(mismatches), 0, "불일치 항목이 있어야 함")
        if mismatches:
            self.assertEqual(mismatches[0]['item_id'], 'MISMATCH001', "불일치 아이템 ID가 일치해야 함")
            self.assertEqual(mismatches[0]['difference'], 20.0, "차이는 20개여야 함")
    
    def test_should_validate_current_location_existence(self):
        """Test: 현재 위치 존재 여부를 검증해야 함"""
        # Given: 재고 데이터와 위치 데이터
        inventory_data = pd.DataFrame({
            'ITEM_ID': ['LOC001'],
            'QUANTITY': [100],
            'LOCATION': ['DSV Indoor']
        })
        
        location_data = pd.DataFrame({
            'ITEM_ID': ['LOC001'],
            'QTY': [100],
            'LOCATION': ['DSV Indoor']
        })
        
        # When: 위치 존재 여부 검증
        result = validate_location_existence(inventory_data, location_data)
        
        # Then: 올바른 결과를 반환해야 함
        self.assertIsInstance(result, dict, "결과는 딕셔너리여야 함")
        self.assertIn('all_locations_exist', result, "all_locations_exist 키가 있어야 함")
        self.assertIn('missing_locations', result, "missing_locations 키가 있어야 함")
        self.assertIn('location_coverage', result, "location_coverage 키가 있어야 함")
    
    def test_should_detect_missing_location_data(self):
        """Test: 누락된 위치 데이터를 감지해야 함"""
        # Given: 위치 데이터가 누락된 케이스
        inventory_data = pd.DataFrame({
            'ITEM_ID': ['MISSING001'],
            'QUANTITY': [100],
            'LOCATION': ['DSV Indoor']
        })
        
        location_data = pd.DataFrame({
            'ITEM_ID': ['OTHER001'],  # 다른 아이템 (누락 상황)
            'QTY': [50],
            'LOCATION': ['DSV Outdoor']
        })
        
        # When: 누락된 위치 데이터 감지
        missing_data = detect_missing_location_data(inventory_data, location_data)
        
        # Then: 누락된 데이터를 감지해야 함
        self.assertIsInstance(missing_data, list, "누락 데이터는 리스트여야 함")
    
    def test_should_validate_movement_timeline(self):
        """Test: 이동 시간선을 검증해야 함"""
        # Given: 시간순 이동 데이터
        movement_data = pd.DataFrame({
            'ITEM_ID': ['TIME001', 'TIME001', 'TIME001'],
            'DATE': ['2024-01-15', '2024-01-18', '2024-01-20'],
            'QTY': [100, 100, 100],
            'LOCATION': ['DSV Indoor', 'DSV Outdoor', 'AGI']
        })
        
        # When: 이동 시간선 검증
        result = validate_movement_timeline(movement_data)
        
        # Then: 올바른 결과를 반환해야 함
        self.assertIsInstance(result, dict, "결과는 딕셔너리여야 함")
        self.assertIn('timeline_valid', result, "timeline_valid 키가 있어야 함")
        self.assertIn('total_movements', result, "total_movements 키가 있어야 함")
        self.assertIn('invalid_movements', result, "invalid_movements 키가 있어야 함")
    
    def test_should_detect_invalid_timeline(self):
        """Test: 잘못된 이동 시간선을 감지해야 함"""
        # Given: 잘못된 시간순 데이터
        invalid_movement_data = pd.DataFrame({
            'ITEM_ID': ['INVALID001'],
            'DATE': ['2024-12-31'],  # 미래 날짜
            'QTY': [100],
            'LOCATION': ['DSV Indoor']
        })
        
        # When: 잘못된 시간선 감지
        invalid_entries = detect_invalid_timeline(invalid_movement_data)
        
        # Then: 잘못된 항목을 감지해야 함
        self.assertIsInstance(invalid_entries, list, "잘못된 시간선 결과는 리스트여야 함")
    
    def test_should_calculate_location_distribution(self):
        """Test: 위치별 분산을 계산해야 함"""
        # Given: 여러 위치에 분산된 데이터
        location_data = pd.DataFrame({
            'ITEM_ID': ['DIST001', 'DIST002', 'DIST003'],
            'QTY': [50, 30, 20],
            'LOCATION': ['DSV Indoor', 'DSV Outdoor', 'AGI']
        })
        
        # When: 위치별 분산 계산
        distribution = calculate_location_distribution(location_data)
        
        # Then: 올바른 분산을 반환해야 함
        self.assertIsInstance(distribution, dict, "분산 결과는 딕셔너리여야 함")
        self.assertIn('total_locations', distribution, "total_locations 키가 있어야 함")
        self.assertIn('distribution', distribution, "distribution 키가 있어야 함")
        self.assertIn('concentration_index', distribution, "concentration_index 키가 있어야 함")
        self.assertIn('distribution_balance', distribution, "distribution_balance 키가 있어야 함")
    
    def test_should_validate_monthly_stock_total(self):
        """Test: 월말 재고 총합을 검증해야 함"""
        # Given: 월말 재고 데이터
        monthly_data = pd.DataFrame({
            'ITEM_ID': ['STOCK001', 'STOCK002', 'STOCK003'],
            'QTY': [100, 50, 30],
            'DATE': ['2024-01-31', '2024-02-29', '2024-03-31'],
            'LOCATION': ['DSV Indoor', 'DSV Outdoor', 'AGI']
        })
        
        # When: 월말 재고 총합 검증
        result = validate_monthly_stock_total(monthly_data)
        
        # Then: 검증 결과를 반환해야 함
        self.assertIsInstance(result, dict, "검증 결과는 딕셔너리여야 함")
        self.assertIn('total_valid', result, "total_valid 키가 있어야 함")
        self.assertIn('monthly_totals', result, "monthly_totals 키가 있어야 함")
        self.assertIn('inconsistencies', result, "inconsistencies 키가 있어야 함")
        self.assertIn('total_stock_value', result, "total_stock_value 키가 있어야 함")
    
    def test_should_generate_consistency_report(self):
        """Test: 정합성 검증 리포트를 생성해야 함"""
        # Given: 재고 데이터와 위치 데이터
        inventory_data = pd.DataFrame({
            'ITEM_ID': ['REPORT001', 'REPORT002'],
            'QUANTITY': [100, 50],
            'LOCATION': ['DSV Indoor', 'DSV Outdoor']
        })
        
        location_data = pd.DataFrame({
            'ITEM_ID': ['REPORT001', 'REPORT002'],
            'QTY': [100, 50],
            'LOCATION': ['DSV Indoor', 'DSV Outdoor']
        })
        
        # When: 정합성 리포트 생성
        report = generate_consistency_report(inventory_data, location_data)
        
        # Then: 정합성 리포트가 생성되어야 함
        self.assertIsInstance(report, dict, "리포트는 딕셔너리여야 함")
        self.assertIn('timestamp', report, "timestamp 키가 있어야 함")
        self.assertIn('summary', report, "summary 키가 있어야 함")
        self.assertIn('detailed_results', report, "detailed_results 키가 있어야 함")
        self.assertIn('recommendations', report, "recommendations 키가 있어야 함")

class TestAdvancedInventoryValidation(unittest.TestCase):
    """고급 재고 검증 테스트"""
    
    def test_should_detect_phantom_inventory(self):
        """Test: 유령 재고를 감지해야 함"""
        # Given: 재고 데이터와 위치 데이터 (불일치)
        inventory_data = pd.DataFrame({
            'ITEM_ID': ['PHANTOM001', 'PHANTOM002'],
            'QUANTITY': [100, 50],
            'LOCATION': ['DSV Indoor', 'DSV Outdoor']
        })
        
        location_data = pd.DataFrame({
            'ITEM_ID': ['PHANTOM001'],  # PHANTOM002가 누락됨
            'QTY': [100],
            'LOCATION': ['DSV Indoor']
        })
        
        # When: 유령 재고 감지
        phantoms = detect_phantom_inventory(inventory_data, location_data)
        
        # Then: 유령 재고를 감지해야 함
        self.assertIsInstance(phantoms, list, "유령 재고 결과는 리스트여야 함")
    
    def test_should_validate_location_capacity(self):
        """Test: 위치별 용량을 검증해야 함"""
        # Given: 위치별 재고 데이터
        location_data = pd.DataFrame({
            'ITEM_ID': ['CAP001', 'CAP002', 'CAP003'],
            'QTY': [300, 400, 200],
            'LOCATION': ['DSV Indoor', 'DSV Indoor', 'DSV Indoor']
        })
        
        # When: 위치별 용량 검증
        capacity_result = validate_location_capacity(location_data)
        
        # Then: 용량 검증 결과를 반환해야 함
        self.assertIsInstance(capacity_result, dict, "용량 검증 결과는 딕셔너리여야 함")
        self.assertIn('all_within_capacity', capacity_result, "all_within_capacity 키가 있어야 함")
        self.assertIn('capacity_violations', capacity_result, "capacity_violations 키가 있어야 함")
        self.assertIn('utilization_rates', capacity_result, "utilization_rates 키가 있어야 함")
    
    def test_should_track_movement_history(self):
        """Test: 이동 이력을 추적해야 함"""
        # Given: 복잡한 이동 이력 데이터
        movement_data = pd.DataFrame({
            'ITEM_ID': ['HIST001', 'HIST001', 'HIST001'],
            'FROM_LOCATION': ['Port', 'DSV Indoor', 'DSV Outdoor'],
            'TO_LOCATION': ['DSV Indoor', 'DSV Outdoor', 'AGI'],
            'DATE': ['2024-01-15', '2024-01-18', '2024-01-22'],
            'QTY': [100, 100, 100]
        })
        
        # When: 이동 이력 추적
        history = track_movement_history(movement_data)
        
        # Then: 완전한 이동 이력을 반환해야 함
        self.assertIsInstance(history, dict, "이동 이력 결과는 딕셔너리여야 함")
        self.assertIn('total_movements', history, "total_movements 키가 있어야 함")
        self.assertIn('movement_patterns', history, "movement_patterns 키가 있어야 함")
        self.assertIn('frequent_routes', history, "frequent_routes 키가 있어야 함")
        self.assertIn('movement_summary', history, "movement_summary 키가 있어야 함")

class TestInventoryDataIntegrity(unittest.TestCase):
    """재고 데이터 무결성 테스트"""
    
    def test_should_validate_data_completeness(self):
        """Test: 데이터 완전성을 검증해야 함"""
        # Given: 불완전한 데이터
        incomplete_data = pd.DataFrame({
            'ITEM_ID': ['COMP001', 'COMP002', None],  # 누락된 케이스 번호
            'QTY': [100, None, 50],                # 누락된 패키지 수
            'LOCATION': ['DSV Indoor', 'AGI', None]  # 누락된 위치
        })
        
        # When: 데이터 완전성 검증
        completeness_result = validate_data_completeness(incomplete_data)
        
        # Then: 완전성 리포트를 반환해야 함
        self.assertIsInstance(completeness_result, dict, "완전성 검증 결과는 딕셔너리여야 함")
        self.assertIn('complete', completeness_result, "complete 키가 있어야 함")
        self.assertIn('missing_fields', completeness_result, "missing_fields 키가 있어야 함")
        self.assertIn('completeness_rate', completeness_result, "completeness_rate 키가 있어야 함")
        self.assertIn('total_records', completeness_result, "total_records 키가 있어야 함")
    
    def test_should_detect_duplicate_entries(self):
        """Test: 중복 엔트리를 감지해야 함"""
        # Given: 중복 데이터
        duplicate_data = pd.DataFrame({
            'ITEM_ID': ['DUP001', 'DUP001', 'DUP002'],  # 중복 케이스
            'QTY': [100, 100, 50],
            'LOCATION': ['DSV Indoor', 'DSV Indoor', 'AGI'],
            'DATE': ['2024-01-15', '2024-01-15', '2024-01-16']
        })
        
        # When: 중복 엔트리 감지
        duplicates = detect_duplicate_entries(duplicate_data)
        
        # Then: 중복 리포트를 반환해야 함
        self.assertIsInstance(duplicates, list, "중복 엔트리 결과는 리스트여야 함")

def run_tests():
    """테스트 실행"""
    print("🧪 TDD Red Phase: 월말 재고 vs 현재 위치 정합성 검증 테스트 시작")
    print("=" * 80)
    print("테스트 목적:")
    print("1. 월말 재고 수량과 현재 위치별 분산 수량 일치성 검증")
    print("2. 위치 이동 중 누락된 아이템 감지")
    print("3. 시간 기반 위치 변경 추적 및 검증")
    print("4. 재고 데이터 무결성 보장")
    print("=" * 80)
    
    # 테스트 실행
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestInventoryLocationConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedInventoryValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestInventoryDataIntegrity))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 출력
    print("\n" + "=" * 80)
    print(f"🔴 RED PHASE 결과: {result.testsRun}개 테스트 중 {len(result.failures + result.errors)}개 실패")
    print("다음 단계: GREEN PHASE - 테스트를 통과하는 최소한의 구현 작성")
    print("=" * 80)
    
    return result

if __name__ == "__main__":
    run_tests() 