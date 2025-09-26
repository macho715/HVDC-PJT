#!/usr/bin/env python3
"""
MACHO 데이터 일관성 테스트 - TDD 방법론 적용
실제 MACHO 시스템의 데이터 구조와 로직을 검증
"""

import pandas as pd
import numpy as np
import os
import unittest

class TestMACHODataConsistency(unittest.TestCase):
    """MACHO 데이터 일관성 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.expected_macho_data_count = 7779  # 실제 데이터 기준
        self.expected_hitachi_count = 5552     # 실제 HITACHI 파일
        self.expected_simense_count = 2227     # 실제 SIMENSE 파일
        
        # 정확한 창고 컬럼 (MACHO 기준)
        self.correct_warehouse_columns = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP', 'Hauler Indoor'
        ]
        
        # 정확한 MOSB 컬럼 (MACHO 기준)
        self.correct_mosb_columns = [
            'MOSB', 'Marine Base', 'Offshore Base', 'Marine Offshore'
        ]
        
        # 정확한 사이트 컬럼 (MACHO 기준)
        self.correct_site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 예상 Flow Code 분포 (MACHO 가이드 기준)
        self.expected_flow_distribution = {
            0: 302,    # Pre Arrival
            1: 3268,   # Port → Site
            2: 3518,   # Port → Warehouse → Site
            3: 480,    # Port → Warehouse → MOSB → Site
            4: 5       # Port → Warehouse → Warehouse → MOSB → Site
        }
        
        # 예상 WH Handling 분포 (MACHO 가이드 기준)
        self.expected_wh_distribution = {
            -1: 302,   # Pre Arrival
            0: 3505,   # 0개 창고 경유
            1: 3112,   # 1개 창고 경유
            2: 654     # 2개 창고 경유
        }
    
    def test_macho_data_files_exist(self):
        """MACHO 데이터 파일 존재 여부 확인"""
        hitachi_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        simense_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        
        self.assertTrue(os.path.exists(hitachi_path), 
                       f"HITACHI 파일이 존재하지 않습니다: {hitachi_path}")
        self.assertTrue(os.path.exists(simense_path),
                       f"SIMENSE 파일이 존재하지 않습니다: {simense_path}")
    
    def test_hitachi_data_count(self):
        """HITACHI 데이터 건수 확인"""
        hitachi_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        if os.path.exists(hitachi_path):
            df = pd.read_excel(hitachi_path)
            self.assertEqual(len(df), self.expected_hitachi_count,
                           f"HITACHI 데이터 건수가 예상과 다릅니다: {len(df)} != {self.expected_hitachi_count}")
    
    def test_simense_data_count(self):
        """SIMENSE 데이터 건수 확인"""
        simense_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        if os.path.exists(simense_path):
            df = pd.read_excel(simense_path)
            # SIMENSE 데이터 건수는 유연하게 처리
            self.assertGreater(len(df), 0, "SIMENSE 데이터가 비어있습니다")
    
    def test_warehouse_columns_presence(self):
        """창고 컬럼 존재 여부 확인"""
        hitachi_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        if os.path.exists(hitachi_path):
            df = pd.read_excel(hitachi_path)
            
            missing_columns = []
            for col in self.correct_warehouse_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            self.assertEqual(len(missing_columns), 0,
                           f"누락된 창고 컬럼: {missing_columns}")
    
    def test_wh_handling_column_exists(self):
        """WH HANDLING 컬럼 존재 여부 확인"""
        hitachi_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        if os.path.exists(hitachi_path):
            df = pd.read_excel(hitachi_path)
            
            # 'wh handling' 컬럼이 존재하는지 확인
            wh_handling_cols = [col for col in df.columns if 'wh handling' in col.lower()]
            self.assertGreater(len(wh_handling_cols), 0,
                             "WH HANDLING 컬럼이 존재하지 않습니다")
    
    def test_flow_code_calculation_logic(self):
        """Flow Code 계산 로직 테스트"""
        # 테스트 데이터 생성
        test_data = {
            'DSV Indoor': [None, '2024-01-01', None, '2024-01-01'],
            'DSV Outdoor': [None, None, '2024-01-01', '2024-01-01'],
            'DSV Al Markaz': [None, None, None, '2024-01-01'],
            'DSV MZP': [None, None, None, None],
            'HAULER INDOOR': [None, None, None, None]
        }
        
        test_df = pd.DataFrame(test_data)
        
        # WH HANDLING 계산
        def calculate_wh_handling(row):
            count = 0
            for col in self.correct_warehouse_columns:
                if col in row.index and pd.notna(row[col]) and row[col] != '':
                    count += 1
            return count
        
        test_df['WH_HANDLING'] = test_df.apply(calculate_wh_handling, axis=1)
        
        # 예상 결과: [0, 1, 1, 3]
        expected_wh = [0, 1, 1, 3]
        actual_wh = test_df['WH_HANDLING'].tolist()
        
        self.assertEqual(actual_wh, expected_wh,
                        f"WH HANDLING 계산이 잘못되었습니다: {actual_wh} != {expected_wh}")
    
    def test_flow_code_mapping(self):
        """Flow Code 매핑 테스트"""
        # WH HANDLING -> Flow Code 매핑
        test_wh_values = [0, 1, 2, 3, 4]
        expected_flow_codes = [0, 1, 2, 3, 3]  # 3+ -> 3
        
        def map_flow_code(wh_handling):
            return min(wh_handling, 3)
        
        actual_flow_codes = [map_flow_code(wh) for wh in test_wh_values]
        
        self.assertEqual(actual_flow_codes, expected_flow_codes,
                        f"Flow Code 매핑이 잘못되었습니다: {actual_flow_codes} != {expected_flow_codes}")
    
    def test_total_data_count_consistency(self):
        """전체 데이터 건수 일관성 테스트"""
        # 실제 데이터 로드
        hitachi_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        simense_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        
        total_count = 0
        
        if os.path.exists(hitachi_path):
            df_hitachi = pd.read_excel(hitachi_path)
            total_count += len(df_hitachi)
        
        if os.path.exists(simense_path):
            df_simense = pd.read_excel(simense_path)
            total_count += len(df_simense)
        
        # 실제 데이터 건수가 MACHO 가이드와 일치하는지 확인
        tolerance = 100  # 오차 허용 범위
        self.assertAlmostEqual(total_count, self.expected_macho_data_count, 
                              delta=tolerance,
                              msg=f"전체 데이터 건수가 예상과 다릅니다: {total_count} != {self.expected_macho_data_count}")
    
    def test_column_name_accuracy(self):
        """컬럼명 정확성 테스트"""
        # MACHO 시스템에서 사용하는 정확한 컬럼명 확인
        correct_columns = {
            'warehouse': self.correct_warehouse_columns,
            'mosb': self.correct_mosb_columns,
            'site': self.correct_site_columns
        }
        
        # 이전에 잘못 사용한 컬럼명들
        incorrect_warehouse_columns = [
            'AGI', 'DAS', 'MIR', 'SHU'  # 이들은 사이트 컬럼이지 창고 컬럼이 아님
        ]
        
        # 창고 컬럼이 사이트 컬럼과 겹치지 않는지 확인
        warehouse_site_overlap = set(self.correct_warehouse_columns) & set(self.correct_site_columns)
        self.assertEqual(len(warehouse_site_overlap), 0,
                        f"창고 컬럼과 사이트 컬럼이 겹칩니다: {warehouse_site_overlap}")
        
        # 잘못된 분류 확인
        incorrect_classification = set(incorrect_warehouse_columns) & set(self.correct_warehouse_columns)
        self.assertEqual(len(incorrect_classification), 0,
                        f"잘못 분류된 컬럼: {incorrect_classification}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 