#!/usr/bin/env python3
"""
Flow Code 분석 데이터 구조 테스트
MACHO-GPT v3.4-mini | TDD 원칙에 따른 테스트 작성

목적:
1. 정확한 창고/현장 컬럼 분류 테스트
2. Flow Code 계산 로직 검증
3. 데이터 구조 일치성 확인
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_flow_code_structure.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 테스트 데이터 생성을 위한 정확한 컬럼 정의
WAREHOUSE_COLUMNS = [
    'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA Storage', 
    'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse'
]

SITE_COLUMNS = ['AGI', 'DAS', 'MIR', 'SHU']

BASIC_COLUMNS = [
    'no.', 'Case No.', 'Pkg', 'L(CM)', 'W(CM)', 'H(CM)', 'CBM'
]

MATERIAL_COLUMNS = [
    'N.W(kgs)', 'G.W(kgs)', 'Stack', 'HS Code', 'Currency'
]

ADDITIONAL_COLUMNS = [
    'SQM', 'Stack_Status', 'Description', 'Site', 'EQ No'
]

ANALYSIS_COLUMNS = [
    'WH_HANDLING', 'FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_PATTERN'
]

META_COLUMNS = [
    'VENDOR', 'SOURCE_FILE', 'PROCESSED_AT', 'TRANSACTION_ID',
    'Status_Location_Date', 'Status_Location_Location', 
    'Status_Location_Date_Year', 'Status_Location_Date_Month'
]

class TestFlowCodeDataStructure(unittest.TestCase):
    
    def setUp(self):
        """테스트 데이터 설정"""
        logger.info("테스트 데이터 설정 중...")
        
        self.all_columns = (
            BASIC_COLUMNS + MATERIAL_COLUMNS + ADDITIONAL_COLUMNS + 
            WAREHOUSE_COLUMNS + SITE_COLUMNS + ANALYSIS_COLUMNS + META_COLUMNS
        )
        
        # 샘플 데이터 생성
        self.sample_data = pd.DataFrame({
            'no.': [1, 2, 3, 4, 5],
            'Case No.': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'Pkg': [10, 20, 15, 8, 12],
            'CBM': [1.5, 2.0, 1.8, 1.2, 1.6],
            'Site': ['Site A', 'Site B', None, 'Site C', 'Site D'],
            'WH_HANDLING': [1, 2, 0, 1, 2],
            'DSV Indoor': ['2024-01-15', None, None, '2024-01-20', None],
            'DSV Outdoor': [None, '2024-01-18', None, None, '2024-01-22'],
            'MOSB': [None, None, None, None, '2024-01-25'],
            'AGI': [None, None, None, '2024-01-25', None],
            'DAS': ['2024-01-20', None, None, None, None],
            'MIR': [None, '2024-01-22', None, None, None],
            'SHU': [None, None, None, None, '2024-01-28']
        })
        
        logger.info(f"샘플 데이터 생성 완료: {len(self.sample_data)}건")
    
    def test_warehouse_column_detection_should_identify_correct_columns(self):
        """창고 컬럼 검색이 정확한 컬럼을 식별해야 함"""
        logger.info("창고 컬럼 검색 테스트 시작")
        
        # Given: 테스트 데이터프레임
        df = self.sample_data
        
        # When: 창고 컬럼 검색
        warehouse_cols = [col for col in df.columns if col in WAREHOUSE_COLUMNS]
        
        # Then: 정확한 창고 컬럼만 검색되어야 함
        expected_warehouse_cols = ['DSV Indoor', 'DSV Outdoor', 'MOSB']
        self.assertEqual(set(warehouse_cols), set(expected_warehouse_cols),
                        "창고 컬럼이 정확히 식별되어야 함")
        
        # And: 현장 컬럼은 포함되지 않아야 함
        site_cols_in_warehouse = [col for col in warehouse_cols if col in SITE_COLUMNS]
        self.assertEqual(len(site_cols_in_warehouse), 0,
                        "현장 컬럼이 창고로 분류되면 안됨")
        
        logger.info(f"창고 컬럼 검색 성공: {warehouse_cols}")
    
    def test_site_column_detection_should_identify_correct_columns(self):
        """현장 컬럼 검색이 정확한 컬럼을 식별해야 함"""
        logger.info("현장 컬럼 검색 테스트 시작")
        
        # Given: 테스트 데이터프레임
        df = self.sample_data
        
        # When: 현장 컬럼 검색
        site_cols = [col for col in df.columns if col in SITE_COLUMNS]
        
        # Then: 정확한 현장 컬럼만 검색되어야 함
        expected_site_cols = ['AGI', 'DAS', 'MIR', 'SHU']
        self.assertEqual(set(site_cols), set(expected_site_cols),
                        "현장 컬럼이 정확히 식별되어야 함")
        
        # And: 창고 컬럼은 포함되지 않아야 함
        warehouse_cols_in_site = [col for col in site_cols if col in WAREHOUSE_COLUMNS]
        self.assertEqual(len(warehouse_cols_in_site), 0,
                        "창고 컬럼이 현장으로 분류되면 안됨")
        
        logger.info(f"현장 컬럼 검색 성공: {site_cols}")
    
    def test_flow_code_calculation_should_handle_warehouse_and_site_correctly(self):
        """Flow Code 계산이 창고와 현장을 올바르게 처리해야 함"""
        logger.info("Flow Code 계산 테스트 시작")
        
        # Given: 테스트 케이스들
        test_cases = [
            {
                'name': 'Pre Arrival - 현장 데이터 없음',
                'site': None,
                'warehouses': {},
                'expected_flow_code': 0
            },
            {
                'name': 'Port → Site 직송',
                'site': 'Site A',
                'warehouses': {},
                'expected_flow_code': 1
            },
            {
                'name': 'Port → WH → Site',
                'site': 'Site A',
                'warehouses': {'DSV Indoor': '2024-01-15'},
                'expected_flow_code': 2
            },
            {
                'name': 'Port → WH → MOSB → Site',
                'site': 'Site A',
                'warehouses': {'DSV Indoor': '2024-01-15', 'MOSB': '2024-01-20'},
                'expected_flow_code': 3
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case['name']):
                # When: Flow Code 계산
                flow_code = self._calculate_flow_code(case['site'], case['warehouses'])
                
                # Then: 예상 Flow Code와 일치해야 함
                self.assertEqual(flow_code, case['expected_flow_code'],
                               f"{case['name']} 케이스의 Flow Code가 {case['expected_flow_code']}이어야 함")
                
                logger.info(f"Flow Code 계산 성공: {case['name']} → {flow_code}")
    
    def test_data_structure_completeness_should_include_all_required_columns(self):
        """데이터 구조가 모든 필수 컬럼을 포함해야 함"""
        logger.info("데이터 구조 완전성 테스트 시작")
        
        # Given: 전체 컬럼 목록
        all_required_columns = (
            BASIC_COLUMNS + MATERIAL_COLUMNS + ADDITIONAL_COLUMNS + 
            WAREHOUSE_COLUMNS + SITE_COLUMNS + ANALYSIS_COLUMNS + META_COLUMNS
        )
        
        # When: 컬럼 분류 검증
        warehouse_check = all(col in WAREHOUSE_COLUMNS for col in ['DSV Indoor', 'DSV Outdoor', 'MOSB'])
        site_check = all(col in SITE_COLUMNS for col in ['AGI', 'DAS', 'MIR', 'SHU'])
        
        # Then: 모든 필수 컬럼이 올바르게 분류되어야 함
        self.assertTrue(warehouse_check, "주요 창고 컬럼이 WAREHOUSE_COLUMNS에 포함되어야 함")
        self.assertTrue(site_check, "주요 현장 컬럼이 SITE_COLUMNS에 포함되어야 함")
        
        # And: 컬럼 분류가 중복되지 않아야 함
        warehouse_site_overlap = set(WAREHOUSE_COLUMNS) & set(SITE_COLUMNS)
        self.assertEqual(len(warehouse_site_overlap), 0,
                        "창고 컬럼과 현장 컬럼이 중복되면 안됨")
        
        logger.info(f"데이터 구조 완전성 검증 성공: 창고 {len(WAREHOUSE_COLUMNS)}개, 현장 {len(SITE_COLUMNS)}개")
    
    def test_flow_code_distribution_should_match_expected_patterns(self):
        """Flow Code 분포가 예상 패턴과 일치해야 함"""
        logger.info("Flow Code 분포 테스트 시작")
        
        # Given: 다양한 케이스의 테스트 데이터 - 직송 케이스 포함
        test_data = pd.DataFrame({
            'Site': [None, 'Site A', 'Site B', 'Site C', 'Site D'] * 20,
            'DSV Indoor': [None, None, None, '2024-01-16', None] * 20,  # 직송 케이스를 위해 수정
            'DSV Outdoor': [None, None, '2024-01-18', None, '2024-01-19'] * 20,
            'MOSB': [None, None, None, None, '2024-01-20'] * 20,
            'AGI': [None, None, None, '2024-01-25', None] * 20,
            'DAS': [None, None, None, None, None] * 20,
            'MIR': [None, None, None, None, None] * 20,
            'SHU': [None, None, None, None, None] * 20
        })
        
        # When: Flow Code 계산
        flow_codes = []
        for _, row in test_data.iterrows():
            site = row['Site']
            warehouses = {col: row[col] for col in WAREHOUSE_COLUMNS if col in row.index and pd.notna(row[col])}
            flow_code = self._calculate_flow_code(site, warehouses)
            flow_codes.append(flow_code)
        
        test_data['FLOW_CODE'] = flow_codes
        
        # Then: Flow Code 분포가 합리적이어야 함
        distribution = test_data['FLOW_CODE'].value_counts().sort_index()
        
        logger.info(f"Flow Code 분포: {distribution.to_dict()}")
        
        # Pre Arrival (Code 0) 케이스가 존재해야 함
        self.assertGreater(distribution.get(0, 0), 0, "Pre Arrival 케이스가 존재해야 함")
        
        # 직송 (Code 1) 케이스가 존재해야 함
        self.assertGreater(distribution.get(1, 0), 0, "직송 케이스가 존재해야 함")
        
        # 창고 경유 (Code 2+) 케이스가 존재해야 함
        warehouse_cases = distribution.get(2, 0) + distribution.get(3, 0)
        self.assertGreater(warehouse_cases, 0, "창고 경유 케이스가 존재해야 함")
        
        logger.info("Flow Code 분포 테스트 완료")
    
    def _calculate_flow_code(self, site, warehouses):
        """Flow Code 계산 헬퍼 함수"""
        # 현장 데이터 확인
        has_site = site is not None and site != ''
        
        # 창고 개수 계산
        warehouse_count = len([w for w in warehouses.values() if w is not None and w != ''])
        
        # MOSB 확인
        has_mosb = 'MOSB' in warehouses and warehouses['MOSB'] is not None
        
        # Flow Code 결정
        if not has_site:
            return 0  # Pre Arrival
        elif warehouse_count == 0:
            return 1  # Port → Site 직송
        elif has_mosb:
            return 3  # MOSB 경유
        else:
            return 2  # 일반 창고 경유

if __name__ == '__main__':
    try:
        logger.info("🧪 Flow Code 데이터 구조 테스트 시작")
        unittest.main(verbosity=2, exit=False)
        logger.info("✅ 모든 테스트 완료")
    except Exception as e:
        logger.error(f"❌ 테스트 실행 중 오류: {e}")
        print(f"오류 발생: {e}")
        sys.exit(1) 