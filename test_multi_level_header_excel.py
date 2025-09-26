#!/usr/bin/env python3
"""
Multi-Level Header 구조 엑셀 파일 생성 TDD 테스트
HVDC Project - Samsung C&T Logistics
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

class TestMultiLevelHeaderExcel(unittest.TestCase):
    """Multi-Level Header 구조 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.warehouses = ['AAA Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV Outdoor', 'Hauler Indoor', 'MOSB']
        self.sites = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 창고 월별 기간: 2023-02 ~ 2024-07 (18개월)
        self.warehouse_months = pd.date_range('2023-02', '2024-07', freq='MS')
        
        # 현장 월별 기간: 2024-01 ~ 2025-06 (18개월)
        self.site_months = pd.date_range('2024-01', '2025-06', freq='MS')
        
        # 임시 출력 디렉토리
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, 'test_multi_level_header.xlsx')
    
    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        os.rmdir(self.temp_dir)
    
    def test_warehouse_multi_level_header_structure_should_have_correct_columns(self):
        """
        창고 Multi-Level Header 구조 테스트
        - 상위 헤더: 입고, 출고
        - 하위 헤더: 7개 창고명
        - 총 15열 (Location + 입고7 + 출고7)
        """
        # Given: 창고 데이터 생성 클래스 필요
        generator = HVDCExcelGenerator()
        
        # When: 창고 Multi-Level Header 생성
        warehouse_sheet = generator.create_warehouse_monthly_sheet()
        
        # Then: 헤더 구조 검증
        self.assertEqual(len(warehouse_sheet.columns), 15)  # Location + 입고7 + 출고7
        
        # Multi-Level 헤더 구조 검증
        level_0_headers = warehouse_sheet.columns.get_level_values(0).unique()
        expected_level_0 = ['입고월', '입고', '출고']
        self.assertEqual(list(level_0_headers), expected_level_0)
        
        # 하위 헤더에서 창고명 검증
        level_1_headers = warehouse_sheet.columns.get_level_values(1).unique()
        for warehouse in self.warehouses:
            self.assertIn(warehouse, level_1_headers)
    
    def test_site_multi_level_header_structure_should_have_correct_columns(self):
        """
        현장 Multi-Level Header 구조 테스트
        - 상위 헤더: 입고, 재고
        - 하위 헤더: 4개 현장명
        - 총 9열 (Location + 입고4 + 재고4)
        """
        # Given: 현장 데이터 생성 클래스 필요
        generator = HVDCExcelGenerator()
        
        # When: 현장 Multi-Level Header 생성
        site_sheet = generator.create_site_monthly_sheet()
        
        # Then: 헤더 구조 검증
        self.assertEqual(len(site_sheet.columns), 9)  # Location + 입고4 + 재고4
        
        # Multi-Level 헤더 구조 검증
        level_0_headers = site_sheet.columns.get_level_values(0).unique()
        expected_level_0 = ['입고월', '입고', '재고']
        self.assertEqual(list(level_0_headers), expected_level_0)
        
        # 하위 헤더에서 현장명 검증
        level_1_headers = site_sheet.columns.get_level_values(1).unique()
        for site in self.sites:
            self.assertIn(site, level_1_headers)
    
    def test_warehouse_data_should_have_correct_month_range(self):
        """
        창고 데이터 월별 범위 테스트
        - 2023-02 ~ 2025-06 + Total (합계)
        - 총 20행
        """
        # Given: 창고 데이터 생성
        generator = HVDCExcelGenerator()
        
        # When: 창고 월별 데이터 생성
        warehouse_sheet = generator.create_warehouse_monthly_sheet()
        
        # Then: 월별 범위 검증
        self.assertEqual(len(warehouse_sheet), 20)  # 18개월 + 총합계
        
        # 첫 번째 월과 마지막 월 검증
        first_month = warehouse_sheet.iloc[0, 0]  # 첫 번째 행, 첫 번째 컬럼
        last_month = warehouse_sheet.iloc[-2, 0]  # 마지막에서 두 번째 행, 첫 번째 컬럼
        
        self.assertEqual(first_month, '2023-02')
        self.assertEqual(last_month, '2024-07')
        
        # 총합계 행 검증
        self.assertEqual(warehouse_sheet.iloc[-1, 0], 'Total')
    
    def test_site_data_should_have_correct_month_range(self):
        """
        현장 데이터 월별 범위 테스트
        - 2024-01 ~ 2025-06 + Total (합계)
        - 총 20행
        """
        # Given: 현장 데이터 생성
        generator = HVDCExcelGenerator()
        
        # When: 현장 월별 데이터 생성
        site_sheet = generator.create_site_monthly_sheet()
        
        # Then: 월별 범위 검증
        self.assertEqual(len(site_sheet), 20)  # 18개월 + 총합계
        
        # 첫 번째 월과 마지막 월 검증
        first_month = site_sheet.iloc[0, 0]  # 첫 번째 행, 첫 번째 컬럼
        last_month = site_sheet.iloc[-2, 0]  # 마지막에서 두 번째 행, 첫 번째 컬럼
        
        self.assertEqual(first_month, '2024-01')
        self.assertEqual(last_month, '2025-06')
        
        # 총합계 행 검증
        self.assertEqual(site_sheet.iloc[-1, 0], 'Total')
    
    def test_excel_file_creation_should_save_with_multi_level_headers(self):
        """
        Excel 파일 생성 테스트
        - Multi-Level Header 구조로 저장
        - 창고_월별_입출고 시트
        - 현장_월별_입고재고 시트
        """
        # Given: Excel 생성기
        generator = HVDCExcelGenerator()
        
        # When: Excel 파일 생성
        generator.create_excel_file(self.output_file)
        
        # Then: 파일 존재 확인
        self.assertTrue(os.path.exists(self.output_file))
        
        # 파일 내용 검증
        with pd.ExcelFile(self.output_file) as excel_file:
            sheet_names = excel_file.sheet_names
            self.assertIn('창고_월별_입출고', sheet_names)
            self.assertIn('현장_월별_입고재고', sheet_names)
            
            # 창고 시트 검증
            warehouse_df = pd.read_excel(excel_file, sheet_name='창고_월별_입출고', header=[0, 1])
            self.assertEqual(len(warehouse_df.columns), 15)
            
            # 현장 시트 검증
            site_df = pd.read_excel(excel_file, sheet_name='현장_월별_입고재고', header=[0, 1])
            self.assertEqual(len(site_df.columns), 9)


class HVDCExcelGenerator:
    """HVDC Excel 생성기 - 실제 구현은 여기서"""
    
    def __init__(self):
        self.warehouses = ['AAA Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV Outdoor', 'Hauler Indoor', 'MOSB']
        self.sites = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 실제 HVDC 데이터 기반 분포 (메모리 데이터 기반)
        self.warehouse_distribution = {
            'DSV Indoor': 1465,
            'DSV Al Markaz': 1039,
            'DSV Outdoor': 1925,
            'AAA Storage': 101,
            'Hauler Indoor': 392,
            'DSV MZP': 13,
            'MOSB': 728
        }
        
        self.site_distribution = {
            'MIR': 1272,
            'SHU': 1823,
            'DAS': 949,
            'AGI': 80
        }
    
    def create_warehouse_monthly_sheet(self):
        """창고 월별 입출고 시트 생성"""
        # 월별 기간 생성 (2023-02 ~ 2024-07, 18개월)
        warehouse_months = pd.date_range('2023-02', periods=18, freq='MS')
        month_strings = [month.strftime('%Y-%m') for month in warehouse_months]
        month_strings.append('Total')  # 총합계 행 추가
        
        # Multi-Level Header 생성
        level_0_headers = ['입고월']
        level_1_headers = ['']
        
        # 입고 헤더 (7개 창고)
        for warehouse in self.warehouses:
            level_0_headers.append('입고')
            level_1_headers.append(warehouse)
        
        # 출고 헤더 (7개 창고)
        for warehouse in self.warehouses:
            level_0_headers.append('출고')
            level_1_headers.append(warehouse)
        
        # MultiIndex 생성
        multi_columns = pd.MultiIndex.from_arrays([level_0_headers, level_1_headers])
        
        # 데이터 생성 (실제 HVDC 데이터 분포 기반)
        data = []
        for month in month_strings:
            if month == 'Total':
                # 총합계 행 생성
                row = []
                row.append(month)  # 첫 번째 컬럼
                for warehouse in self.warehouses:
                    # 입고 총합
                    total_inbound = self.warehouse_distribution[warehouse]
                    row.append(total_inbound)
                for warehouse in self.warehouses:
                    # 출고 총합 (입고의 85% 가정)
                    total_outbound = int(self.warehouse_distribution[warehouse] * 0.85)
                    row.append(total_outbound)
                data.append(row)
            else:
                # 월별 데이터 생성
                row = []
                row.append(month)  # 첫 번째 컬럼
                for warehouse in self.warehouses:
                    # 월별 입고 (총량을 18개월로 분배)
                    monthly_inbound = self.warehouse_distribution[warehouse] // 18
                    row.append(monthly_inbound)
                for warehouse in self.warehouses:
                    # 월별 출고 (입고의 85% 가정)
                    monthly_outbound = int((self.warehouse_distribution[warehouse] // 18) * 0.85)
                    row.append(monthly_outbound)
                data.append(row)
        
        # DataFrame 생성
        warehouse_df = pd.DataFrame(data, columns=multi_columns)
        
        return warehouse_df
    
    def create_site_monthly_sheet(self):
        """현장 월별 입고재고 시트 생성"""
        # 월별 기간 생성 (2024-01 ~ 2025-06, 18개월)
        site_months = pd.date_range('2024-01', periods=18, freq='MS')
        month_strings = [month.strftime('%Y-%m') for month in site_months]
        month_strings.append('Total')  # 총합계 행 추가
        
        # Multi-Level Header 생성
        level_0_headers = ['입고월']
        level_1_headers = ['']
        
        # 입고 헤더 (4개 현장)
        for site in self.sites:
            level_0_headers.append('입고')
            level_1_headers.append(site)
        
        # 재고 헤더 (4개 현장)
        for site in self.sites:
            level_0_headers.append('재고')
            level_1_headers.append(site)
        
        # MultiIndex 생성
        multi_columns = pd.MultiIndex.from_arrays([level_0_headers, level_1_headers])
        
        # 데이터 생성 (실제 HVDC 데이터 분포 기반)
        data = []
        cumulative_inventory = {site: 0 for site in self.sites}
        
        for month in month_strings:
            if month == 'Total':
                # 총합계 행 생성
                row = []
                row.append(month)  # 첫 번째 컬럼
                for site in self.sites:
                    # 입고 총합
                    total_inbound = self.site_distribution[site]
                    row.append(total_inbound)
                for site in self.sites:
                    # 재고 총합 (입고의 30% 가정)
                    total_inventory = int(self.site_distribution[site] * 0.30)
                    row.append(total_inventory)
                data.append(row)
            else:
                # 월별 데이터 생성
                row = []
                row.append(month)  # 첫 번째 컬럼
                for site in self.sites:
                    # 월별 입고 (총량을 18개월로 분배)
                    monthly_inbound = self.site_distribution[site] // 18
                    row.append(monthly_inbound)
                    cumulative_inventory[site] += monthly_inbound
                
                for site in self.sites:
                    # 월별 재고 (누적 - 소비)
                    consumption = cumulative_inventory[site] * 0.05  # 5% 소비
                    cumulative_inventory[site] = int(cumulative_inventory[site] - consumption)
                    row.append(cumulative_inventory[site])
                data.append(row)
        
        # DataFrame 생성
        site_df = pd.DataFrame(data, columns=multi_columns)
        
        return site_df
    
    def create_excel_file(self, output_file):
        """Excel 파일 생성"""
        # 창고별 월별 입출고 시트 생성
        warehouse_sheet = self.create_warehouse_monthly_sheet()
        
        # 현장별 월별 입고재고 시트 생성
        site_sheet = self.create_site_monthly_sheet()
        
        # Excel 파일 생성
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 창고_월별_입출고 시트
            warehouse_sheet.to_excel(writer, sheet_name='창고_월별_입출고')
            
            # 현장_월별_입고재고 시트
            site_sheet.to_excel(writer, sheet_name='현장_월별_입고재고')
        
        print(f"✅ Excel 파일 생성 완료: {output_file}")


if __name__ == '__main__':
    unittest.main() 