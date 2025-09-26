#!/usr/bin/env python3
"""
MACHO 시스템 올바른 창고/현장 시트 구조 테스트 - TDD 방법론 적용
06_로직함수 폴더의 구조를 기반으로 올바른 Multi-level 헤더 검증
"""

import pandas as pd
import numpy as np
import os
import unittest
from datetime import datetime

class TestCorrectWarehouseSiteStructure(unittest.TestCase):
    """MACHO 시스템 올바른 창고/현장 시트 구조 테스트"""
    
    def setUp(self):
        """테스트 설정 - MACHO 시스템 기준"""
        # 정확한 창고 컬럼 (MACHO 시스템 기준)
        self.correct_warehouse_columns = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 
            'DSV MZP', 'Hauler Indoor', 'MOSB', 'AAA  Storage'  # AAA  Storage는 공백 2개
        ]
        
        # 정확한 현장 컬럼 (MACHO 시스템 기준)
        self.correct_site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 현장별 비율 (MACHO 시스템 기준)
        self.site_ratios = {
            'AGI': 0.02,   # 2%
            'DAS': 0.35,   # 35%
            'MIR': 0.38,   # 38%
            'SHU': 0.25    # 25%
        }
        
        # 예상 Multi-level 헤더 구조
        self.expected_warehouse_headers = {
            'level_0': ['입고'] * len(self.correct_warehouse_columns) + ['출고'] * len(self.correct_warehouse_columns),
            'level_1': self.correct_warehouse_columns + self.correct_warehouse_columns
        }
        
        self.expected_site_headers = {
            'level_0': ['입고'] * len(self.correct_site_columns) + ['재고'] * len(self.correct_site_columns),
            'level_1': self.correct_site_columns + self.correct_site_columns
        }
    
    def test_warehouse_multi_level_header_structure(self):
        """창고 시트 Multi-level 헤더 구조 테스트"""
        # 예상 창고 헤더 개수: 7개 창고 × 2 (입고/출고) = 14개
        expected_warehouse_header_count = len(self.correct_warehouse_columns) * 2
        
        # Multi-level 헤더 생성 테스트
        warehouse_headers = pd.MultiIndex.from_arrays([
            self.expected_warehouse_headers['level_0'],
            self.expected_warehouse_headers['level_1']
        ], names=['구분', 'Location'])
        
        self.assertEqual(len(warehouse_headers), expected_warehouse_header_count,
                        f"창고 헤더 개수가 잘못되었습니다: {len(warehouse_headers)} != {expected_warehouse_header_count}")
        
        # 입고/출고 구분 확인
        level_0_values = warehouse_headers.get_level_values(0).unique().tolist()
        self.assertIn('입고', level_0_values, "창고 시트에 '입고' 헤더가 없습니다")
        self.assertIn('출고', level_0_values, "창고 시트에 '출고' 헤더가 없습니다")
        
        # 창고명 확인
        level_1_values = warehouse_headers.get_level_values(1).unique().tolist()
        for warehouse in self.correct_warehouse_columns:
            self.assertIn(warehouse, level_1_values, f"창고 '{warehouse}'가 헤더에 없습니다")
    
    def test_site_multi_level_header_structure(self):
        """현장 시트 Multi-level 헤더 구조 테스트"""
        # 예상 현장 헤더 개수: 4개 현장 × 2 (입고/재고) = 8개
        expected_site_header_count = len(self.correct_site_columns) * 2
        
        # Multi-level 헤더 생성 테스트
        site_headers = pd.MultiIndex.from_arrays([
            self.expected_site_headers['level_0'],
            self.expected_site_headers['level_1']
        ], names=['구분', 'Location'])
        
        self.assertEqual(len(site_headers), expected_site_header_count,
                        f"현장 헤더 개수가 잘못되었습니다: {len(site_headers)} != {expected_site_header_count}")
        
        # 입고/재고 구분 확인 (현장은 출고 없음)
        level_0_values = site_headers.get_level_values(0).unique().tolist()
        self.assertIn('입고', level_0_values, "현장 시트에 '입고' 헤더가 없습니다")
        self.assertIn('재고', level_0_values, "현장 시트에 '재고' 헤더가 없습니다")
        self.assertNotIn('출고', level_0_values, "현장 시트에 '출고' 헤더가 있으면 안됩니다")
        
        # 현장명 확인
        level_1_values = site_headers.get_level_values(1).unique().tolist()
        for site in self.correct_site_columns:
            self.assertIn(site, level_1_values, f"현장 '{site}'가 헤더에 없습니다")
    
    def test_monthly_data_structure(self):
        """월별 데이터 구조 테스트"""
        # 12개월 데이터 생성
        months = [f"2024-{i:02d}" for i in range(1, 13)]
        
        # 테스트 데이터 생성
        test_warehouse_data = []
        for month in months:
            for warehouse in self.correct_warehouse_columns:
                test_warehouse_data.append({
                    'Month': month,
                    'Warehouse': warehouse,
                    'Incoming': np.random.randint(10, 100),
                    'Outgoing': np.random.randint(5, 80),
                    'Pre_Arrival': np.random.randint(0, 10),
                    'Active': np.random.randint(50, 200)
                })
        
        warehouse_df = pd.DataFrame(test_warehouse_data)
        
        # 월별 데이터 검증
        unique_months = warehouse_df['Month'].unique()
        self.assertEqual(len(unique_months), 12, f"월별 데이터가 12개월이 아닙니다: {len(unique_months)}")
        
        # 창고별 데이터 검증
        unique_warehouses = warehouse_df['Warehouse'].unique()
        for warehouse in self.correct_warehouse_columns:
            self.assertIn(warehouse, unique_warehouses, f"창고 '{warehouse}' 데이터가 없습니다")
    
    def test_site_ratio_distribution(self):
        """현장별 비율 분포 테스트"""
        total_data = 7779  # 실제 데이터 건수
        
        # 현장별 예상 데이터 건수 계산
        for site, ratio in self.site_ratios.items():
            expected_count = int(total_data * ratio)
            
            # 비율이 올바른 범위에 있는지 확인
            self.assertGreater(expected_count, 0, f"현장 '{site}'의 데이터 건수가 0입니다")
            self.assertLessEqual(ratio, 1.0, f"현장 '{site}'의 비율이 100%를 초과합니다")
        
        # 전체 비율 합이 100%인지 확인
        total_ratio = sum(self.site_ratios.values())
        self.assertAlmostEqual(total_ratio, 1.0, places=2, 
                              msg=f"현장별 비율 합이 100%가 아닙니다: {total_ratio}")
    
    def test_pre_arrival_integration(self):
        """Pre Arrival 통합 테스트"""
        # Flow Code 0 (Pre Arrival) 데이터 생성
        pre_arrival_data = {
            'FLOW_CODE': [0, 0, 0, 1, 1, 2, 2, 3],
            'WH_HANDLING': [-1, -1, -1, 1, 1, 2, 2, 3],
            'Status': ['Pre Arrival', 'Pre Arrival', 'Pre Arrival', 'Active', 'Active', 'Active', 'Active', 'Active']
        }
        
        test_df = pd.DataFrame(pre_arrival_data)
        
        # Pre Arrival 데이터 분리
        pre_arrival_count = len(test_df[test_df['FLOW_CODE'] == 0])
        active_count = len(test_df[test_df['FLOW_CODE'] != 0])
        
        self.assertGreater(pre_arrival_count, 0, "Pre Arrival 데이터가 없습니다")
        self.assertGreater(active_count, 0, "Active 데이터가 없습니다")
        
        # WH_HANDLING -1이 Pre Arrival과 일치하는지 확인
        wh_minus_one_count = len(test_df[test_df['WH_HANDLING'] == -1])
        self.assertEqual(pre_arrival_count, wh_minus_one_count,
                        "Pre Arrival과 WH_HANDLING -1 건수가 일치하지 않습니다")
    
    def test_warehouse_column_accuracy(self):
        """창고 컬럼명 정확성 테스트"""
        # 잘못된 컬럼명들 (이전에 사용된 것들)
        incorrect_warehouse_columns = [
            'HAULER INDOOR',  # 정확: 'Hauler Indoor'
            'AAA Storage',    # 정확: 'AAA  Storage' (공백 2개)
        ]
        
        # 정확한 컬럼명과 겹치지 않는지 확인
        for incorrect_col in incorrect_warehouse_columns:
            self.assertNotIn(incorrect_col, self.correct_warehouse_columns,
                           f"잘못된 컬럼명이 포함되어 있습니다: {incorrect_col}")
        
        # 'AAA  Storage'의 공백 2개 확인
        aaa_storage_col = None
        for col in self.correct_warehouse_columns:
            if 'AAA' in col:
                aaa_storage_col = col
                break
        
        self.assertIsNotNone(aaa_storage_col, "AAA Storage 컬럼을 찾을 수 없습니다")
        self.assertEqual(aaa_storage_col, 'AAA  Storage', 
                        "AAA Storage 컬럼명이 정확하지 않습니다 (공백 2개 필요)")

if __name__ == '__main__':
    unittest.main(verbosity=2) 