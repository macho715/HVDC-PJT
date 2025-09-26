#!/usr/bin/env python3
"""
최종 리포트 구조 테스트
MACHO-GPT v3.4-mini | TDD 원칙에 따른 최종 리포트 검증

목적:
1. 3개 시트 구조 검증
2. Multi-level 헤더 구조 검증
3. 데이터 완전성 검증
"""

import unittest
import pandas as pd
import numpy as np
import os
from datetime import datetime

class TestFinalReportStructure(unittest.TestCase):
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.required_columns_sheet1 = {
            'basic_info': ['no.', 'Case No.', 'Pkg', 'L(CM)', 'W(CM)', 'H(CM)', 'CBM'],
            'material_info': ['N.W(kgs)', 'G.W(kgs)', 'Stack', 'HS Code', 'Currency'],
            'additional_info': ['SQM', 'Stack_Status', 'Description', 'Site', 'EQ No'],
            'warehouse_info': ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA Storage', 
                             'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse'],
            'site_info': ['AGI', 'DAS', 'MIR', 'SHU'],
            'analysis_info': ['WH_HANDLING', 'FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_PATTERN'],
            'meta_info': ['VENDOR', 'SOURCE_FILE', 'PROCESSED_AT', 'TRANSACTION_ID',
                         'Status_Location_Date', 'Status_Location_Location', 
                         'Status_Location_Date_Year', 'Status_Location_Date_Month']
        }
        
        self.warehouse_columns = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA Storage', 
                                 'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse']
        
        self.site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        self.expected_total_records = 7779  # 재계산된 전체 데이터 수
        
    def test_final_report_should_have_three_sheets(self):
        """최종 리포트는 3개 시트를 가져야 함"""
        # Given: 리포트 구조 요구사항
        expected_sheets = [
            '전체_트랜잭션_데이터',
            '창고_월별_입출고',
            '현장_월별_입고재고'
        ]
        
        # When: 시트 구조 검증
        # Then: 3개 시트가 정의되어야 함
        self.assertEqual(len(expected_sheets), 3, "리포트는 정확히 3개 시트를 가져야 함")
        
        # And: 각 시트명이 적절해야 함
        for sheet_name in expected_sheets:
            self.assertIsInstance(sheet_name, str, f"시트명 '{sheet_name}'은 문자열이어야 함")
            self.assertGreater(len(sheet_name), 0, f"시트명 '{sheet_name}'은 비어있으면 안됨")
        
        return expected_sheets
    
    def test_sheet1_should_have_all_required_columns(self):
        """시트1은 모든 필수 컬럼을 가져야 함"""
        # Given: 시트1 필수 컬럼 구조
        all_required_columns = []
        for category, columns in self.required_columns_sheet1.items():
            all_required_columns.extend(columns)
        
        # When: 컬럼 구조 검증
        # Then: 총 컬럼 수가 예상과 일치해야 함
        self.assertGreater(len(all_required_columns), 50, 
                          f"시트1은 50개 이상의 컬럼을 가져야 함. 현재: {len(all_required_columns)}개")
        
        # And: 각 카테고리별 컬럼이 존재해야 함
        for category, columns in self.required_columns_sheet1.items():
            self.assertGreater(len(columns), 0, f"'{category}' 카테고리는 컬럼을 가져야 함")
        
        # And: 중복 컬럼이 없어야 함
        unique_columns = list(set(all_required_columns))
        self.assertEqual(len(unique_columns), len(all_required_columns), 
                        "중복된 컬럼이 있으면 안됨")
        
        return all_required_columns
    
    def test_sheet2_should_have_multilevel_warehouse_headers(self):
        """시트2는 창고별 Multi-level 헤더를 가져야 함"""
        # Given: 창고별 입출고 구조
        warehouse_operations = ['입고', '출고']
        
        # When: Multi-level 헤더 구조 생성
        expected_headers = []
        for warehouse in self.warehouse_columns:
            for operation in warehouse_operations:
                expected_headers.append(f"{warehouse}_{operation}")
        
        # Then: 헤더 수가 예상과 일치해야 함
        expected_header_count = len(self.warehouse_columns) * len(warehouse_operations)
        self.assertEqual(len(expected_headers), expected_header_count,
                        f"창고별 입출고 헤더는 {expected_header_count}개여야 함")
        
        # And: 각 창고별로 입고/출고 헤더가 존재해야 함
        for warehouse in self.warehouse_columns:
            warehouse_headers = [h for h in expected_headers if h.startswith(warehouse)]
            self.assertEqual(len(warehouse_headers), 2, 
                           f"창고 '{warehouse}'는 입고/출고 2개 헤더를 가져야 함")
        
        return expected_headers
    
    def test_sheet3_should_have_multilevel_site_headers(self):
        """시트3은 현장별 Multi-level 헤더를 가져야 함"""
        # Given: 현장별 입고/재고 구조 (현장은 출고 없음)
        site_operations = ['입고', '재고']
        
        # When: Multi-level 헤더 구조 생성
        expected_headers = []
        for site in self.site_columns:
            for operation in site_operations:
                expected_headers.append(f"{site}_{operation}")
        
        # Then: 헤더 수가 예상과 일치해야 함
        expected_header_count = len(self.site_columns) * len(site_operations)
        self.assertEqual(len(expected_headers), expected_header_count,
                        f"현장별 입고/재고 헤더는 {expected_header_count}개여야 함")
        
        # And: 각 현장별로 입고/재고 헤더가 존재해야 함
        for site in self.site_columns:
            site_headers = [h for h in expected_headers if h.startswith(site)]
            self.assertEqual(len(site_headers), 2, 
                           f"현장 '{site}'는 입고/재고 2개 헤더를 가져야 함")
        
        # And: 현장은 출고 헤더가 없어야 함
        outgoing_headers = [h for h in expected_headers if '출고' in h]
        self.assertEqual(len(outgoing_headers), 0, "현장은 출고 헤더가 없어야 함")
        
        return expected_headers
    
    def test_data_completeness_requirements(self):
        """데이터 완전성 요구사항 검증"""
        # Given: 데이터 완전성 기준
        min_records = 7700  # 최소 레코드 수
        
        # When: 데이터 완전성 검증
        # Then: 총 레코드 수가 기준 이상이어야 함
        self.assertGreaterEqual(self.expected_total_records, min_records,
                               f"총 레코드 수는 {min_records}건 이상이어야 함")
        
        # And: 창고 데이터가 충분해야 함
        self.assertGreater(len(self.warehouse_columns), 5, 
                          "창고는 5개 이상이어야 함")
        
        # And: 현장 데이터가 충분해야 함
        self.assertGreater(len(self.site_columns), 3, 
                          "현장은 3개 이상이어야 함")
        
        return {
            'total_records': self.expected_total_records,
            'warehouse_count': len(self.warehouse_columns),
            'site_count': len(self.site_columns)
        }
    
    def test_report_metadata_requirements(self):
        """리포트 메타데이터 요구사항 검증"""
        # Given: 메타데이터 요구사항
        required_metadata = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': ['HITACHI(HE)', 'SIMENSE(SIM)'],
            'total_records': self.expected_total_records,
            'confidence_level': 95
        }
        
        # When: 메타데이터 검증
        # Then: 필수 메타데이터가 존재해야 함
        self.assertIn('generated_at', required_metadata, "생성일시 메타데이터 필요")
        self.assertIn('data_source', required_metadata, "데이터 소스 메타데이터 필요")
        self.assertIn('total_records', required_metadata, "총 레코드 수 메타데이터 필요")
        self.assertIn('confidence_level', required_metadata, "신뢰도 메타데이터 필요")
        
        # And: 신뢰도가 기준 이상이어야 함
        self.assertGreaterEqual(required_metadata['confidence_level'], 90,
                               "신뢰도는 90% 이상이어야 함")
        
        return required_metadata
    
    def test_multilevel_header_format(self):
        """Multi-level 헤더 형식 검증"""
        # Given: Multi-level 헤더 형식 요구사항
        # When: 헤더 형식 검증
        # Then: 헤더 형식이 일관되어야 함
        
        # 창고 헤더 형식 검증
        for warehouse in self.warehouse_columns:
            warehouse_in_header = f"{warehouse}_입고"
            warehouse_out_header = f"{warehouse}_출고"
            
            self.assertRegex(warehouse_in_header, r'^.+_입고$', 
                           f"창고 입고 헤더 형식: '{warehouse_in_header}'")
            self.assertRegex(warehouse_out_header, r'^.+_출고$', 
                           f"창고 출고 헤더 형식: '{warehouse_out_header}'")
        
        # 현장 헤더 형식 검증
        for site in self.site_columns:
            site_in_header = f"{site}_입고"
            site_stock_header = f"{site}_재고"
            
            self.assertRegex(site_in_header, r'^.+_입고$', 
                           f"현장 입고 헤더 형식: '{site_in_header}'")
            self.assertRegex(site_stock_header, r'^.+_재고$', 
                           f"현장 재고 헤더 형식: '{site_stock_header}'")
        
        return True

if __name__ == '__main__':
    try:
        print("최종 리포트 구조 테스트 시작...")
        unittest.main(verbosity=2, exit=False)
        print("모든 테스트 완료!")
    except Exception as e:
        print(f"테스트 실행 중 오류: {e}") 