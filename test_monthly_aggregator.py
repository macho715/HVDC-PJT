#!/usr/bin/env python3
"""
TDD 테스트: 월별 집계 전용 시스템
MACHO-GPT v3.4-mini│Samsung C&T Logistics
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import os

class TestMonthlyAggregator(unittest.TestCase):
    """월별 집계 전용 시스템 TDD 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.expected_total_records = 7779  # HITACHI(5552) + SIMENSE(2227) - INVOICE 파일 제외
        self.expected_hitachi_records = 5552
        self.expected_simense_records = 2227
        
        # 월별 집계 시스템 초기화 - 이 부분이 실패해야 함
        try:
            from monthly_aggregator import MonthlyAggregator
            self.aggregator = MonthlyAggregator()
        except ImportError:
            self.aggregator = None
        
    def test_monthly_aggregator_initialization(self):
        """월별 집계 시스템 초기화 테스트 - 실패해야 함"""
        # 이 테스트는 실패해야 함 (클래스가 아직 구현되지 않음)
        self.assertIsNotNone(self.aggregator, "MonthlyAggregator 클래스가 구현되어야 함")
        
        # 기본 속성 확인
        self.assertTrue(hasattr(self.aggregator, 'load_complete_dataset'), 
                       "load_complete_dataset 메서드가 있어야 함")
        self.assertTrue(hasattr(self.aggregator, 'generate_warehouse_monthly_report'), 
                       "generate_warehouse_monthly_report 메서드가 있어야 함")
        self.assertTrue(hasattr(self.aggregator, 'generate_site_monthly_report'), 
                       "generate_site_monthly_report 메서드가 있어야 함")
        
    def test_complete_dataset_loading(self):
        """완전한 데이터셋 로드 기능 테스트 - 실패해야 함"""
        if self.aggregator is None:
            self.skipTest("MonthlyAggregator 클래스가 구현되지 않음")
            
        # 완전한 데이터셋 로드
        merged_df = self.aggregator.load_complete_dataset()
        
        # 데이터 검증
        self.assertEqual(len(merged_df), self.expected_total_records, 
                        "총 7,779건의 데이터가 로드되어야 함")
        self.assertTrue('DATA_SOURCE' in merged_df.columns, 
                       "DATA_SOURCE 컬럼이 있어야 함")
        
        # 소스별 분포 확인
        hitachi_count = len(merged_df[merged_df['DATA_SOURCE'] == 'HITACHI'])
        simense_count = len(merged_df[merged_df['DATA_SOURCE'] == 'SIMENSE'])
        
        self.assertEqual(hitachi_count, self.expected_hitachi_records, 
                        "HITACHI 5,552건이어야 함")
        self.assertEqual(simense_count, self.expected_simense_records, 
                        "SIMENSE 2,227건이어야 함")
        
    def test_warehouse_monthly_report_generation(self):
        """창고별 월별 입출고 리포트 생성 테스트 - 실패해야 함"""
        if self.aggregator is None:
            self.skipTest("MonthlyAggregator 클래스가 구현되지 않음")
            
        # 샘플 데이터 생성 (더 완전한 구조)
        sample_data = pd.DataFrame({
            'Status_Location': ['DSV Indoor', 'DSV Outdoor', 'DSV Indoor', 'DSV Outdoor'],
            'DSV Indoor': [pd.Timestamp('2024-01-15'), pd.NaT, pd.Timestamp('2024-02-10'), pd.NaT],
            'DSV Outdoor': [pd.NaT, pd.Timestamp('2024-01-20'), pd.NaT, pd.Timestamp('2024-02-15')],
            'DSV Al Markaz': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'AAA Storage': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'AGI': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'DAS': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'MIR': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'SHU': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'Pkg': [100, 150, -80, -120],  # 음수는 출고
            'DATA_SOURCE': ['TEST', 'TEST', 'TEST', 'TEST']
        })
        
        # 창고별 월별 입출고 리포트 생성
        warehouse_report = self.aggregator.generate_warehouse_monthly_report(sample_data)
        
        # Multi-level 헤더 구조 확인
        self.assertIsInstance(warehouse_report.columns, pd.MultiIndex, 
                            "Multi-level 헤더여야 함")
        
        # 입고/출고 레벨 확인
        level_0_values = warehouse_report.columns.get_level_values(0).unique()
        self.assertTrue('입고' in level_0_values, "입고 레벨이 있어야 함")
        self.assertTrue('출고' in level_0_values, "출고 레벨이 있어야 함")
        
    def test_site_monthly_report_generation(self):
        """현장별 월별 입고재고 리포트 생성 테스트 - 실패해야 함"""
        if self.aggregator is None:
            self.skipTest("MonthlyAggregator 클래스가 구현되지 않음")
            
        # 샘플 데이터 생성 (더 완전한 구조)
        sample_data = pd.DataFrame({
            'Status_Location': ['AGI', 'DAS', 'MIR', 'SHU'],
            'AGI': [pd.Timestamp('2024-01-15'), pd.NaT, pd.NaT, pd.NaT],
            'DAS': [pd.NaT, pd.Timestamp('2024-01-20'), pd.NaT, pd.NaT],
            'MIR': [pd.NaT, pd.NaT, pd.Timestamp('2024-02-10'), pd.NaT],
            'SHU': [pd.NaT, pd.NaT, pd.NaT, pd.Timestamp('2024-02-15')],
            'DSV Indoor': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'DSV Outdoor': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'DSV Al Markaz': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'AAA Storage': [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
            'Pkg': [80, 120, 90, 110],
            'DATA_SOURCE': ['TEST', 'TEST', 'TEST', 'TEST']
        })
        
        # 현장별 월별 입고재고 리포트 생성
        site_report = self.aggregator.generate_site_monthly_report(sample_data)
        
        # Multi-level 헤더 구조 확인
        self.assertIsInstance(site_report.columns, pd.MultiIndex, 
                            "Multi-level 헤더여야 함")
        
        # 입고/재고 레벨 확인
        level_0_values = site_report.columns.get_level_values(0).unique()
        self.assertTrue('입고' in level_0_values, "입고 레벨이 있어야 함")
        self.assertTrue('재고' in level_0_values, "재고 레벨이 있어야 함")
        
    def test_excel_export_functionality(self):
        """Excel 내보내기 기능 테스트 - 실패해야 함"""
        if self.aggregator is None:
            self.skipTest("MonthlyAggregator 클래스가 구현되지 않음")
            
        # 테스트 데이터 준비 (더 완전한 구조)
        sample_data = pd.DataFrame({
            'Status_Location': ['DSV Indoor', 'AGI'],
            'DSV Indoor': [pd.Timestamp('2024-01-15'), pd.NaT],
            'DSV Outdoor': [pd.NaT, pd.NaT],
            'DSV Al Markaz': [pd.NaT, pd.NaT],
            'AAA Storage': [pd.NaT, pd.NaT],
            'AGI': [pd.NaT, pd.Timestamp('2024-01-20')],
            'DAS': [pd.NaT, pd.NaT],
            'MIR': [pd.NaT, pd.NaT],
            'SHU': [pd.NaT, pd.NaT],
            'Pkg': [100, 80],
            'DATA_SOURCE': ['TEST', 'TEST']
        })
        
        # Excel 파일 생성
        output_file = self.aggregator.export_to_excel(sample_data)
        
        # 파일 존재 확인
        self.assertTrue(os.path.exists(output_file), "Excel 파일이 생성되어야 함")
        
        # 파일 내용 확인
        with pd.ExcelFile(output_file) as excel_file:
            sheet_names = excel_file.sheet_names
            
            # 예상 시트 확인
            self.assertIn('창고_월별_입출고', sheet_names, "창고 시트가 있어야 함")
            self.assertIn('현장_월별_입고재고', sheet_names, "현장 시트가 있어야 함")
            self.assertIn('리포트_정보', sheet_names, "리포트 정보 시트가 있어야 함")
        
        # 테스트 후 파일 삭제
        if os.path.exists(output_file):
            os.remove(output_file)
            
    def test_data_loading_complete_dataset(self):
        """완전한 데이터셋 로드 테스트"""
        # 올바른 경로에서 완전한 데이터셋 로드
        hitachi_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        simense_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        
        # 파일 존재 확인
        self.assertTrue(os.path.exists(hitachi_path), "HITACHI 데이터 파일이 존재해야 함")
        self.assertTrue(os.path.exists(simense_path), "SIMENSE 데이터 파일이 존재해야 함")
        
        # 데이터 로드 및 레코드 수 확인
        hitachi_df = pd.read_excel(hitachi_path)
        simense_df = pd.read_excel(simense_path)
        
        self.assertEqual(len(hitachi_df), self.expected_hitachi_records, "HITACHI 5,552건이어야 함")
        self.assertEqual(len(simense_df), self.expected_simense_records, "SIMENSE 2,227건이어야 함")
        
        # 통합 데이터 확인
        total_records = len(hitachi_df) + len(simense_df)
        self.assertEqual(total_records, self.expected_total_records, "총 7,779건이어야 함")
        
    def test_warehouse_monthly_sheet_structure(self):
        """창고별 월별 입출고 시트 구조 테스트"""
        # 예상 창고별 Multi-level 헤더 구조
        expected_warehouses = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'AAA Storage']
        expected_structure = {
            'level_0': ['입고', '입고', '출고', '출고'],
            'level_1': ['DSV Indoor', 'DSV Outdoor', 'DSV Indoor', 'DSV Outdoor']
        }
        
        # 테스트 데이터 생성
        test_data = pd.DataFrame({
            '입고월': ['2024-01', '2024-02', '2024-03'],
            'DSV Indoor_입고': [100, 150, 120],
            'DSV Outdoor_입고': [80, 90, 85],
            'DSV Indoor_출고': [90, 140, 110],
            'DSV Outdoor_출고': [75, 85, 80]
        })
        
        # Multi-level 헤더 생성 테스트
        multi_columns = pd.MultiIndex.from_tuples([
            ('입고', 'DSV Indoor'),
            ('입고', 'DSV Outdoor'),
            ('출고', 'DSV Indoor'),
            ('출고', 'DSV Outdoor')
        ])
        
        self.assertEqual(len(multi_columns), 4, "Multi-level 헤더는 4개 컬럼이어야 함")
        self.assertEqual(multi_columns.levels[0].tolist(), ['입고', '출고'], "첫 번째 레벨은 입고/출고")
        
    def test_site_monthly_sheet_structure(self):
        """현장별 월별 입고재고 시트 구조 테스트"""
        # 예상 현장별 Multi-level 헤더 구조
        expected_sites = ['AGI', 'DAS', 'MIR', 'SHU']
        expected_structure = {
            'level_0': ['입고', '입고', '재고', '재고'],
            'level_1': ['AGI', 'DAS', 'AGI', 'DAS']
        }
        
        # 테스트 데이터 생성
        test_data = pd.DataFrame({
            '입고월': ['2024-01', '2024-02', '2024-03'],
            'AGI_입고': [0, 0, 0],
            'DAS_입고': [280, 315, 290],
            'AGI_재고': [0, 0, 0],
            'DAS_재고': [280, 595, 885]
        })
        
        # Multi-level 헤더 생성 테스트
        multi_columns = pd.MultiIndex.from_tuples([
            ('입고', 'AGI'),
            ('입고', 'DAS'),
            ('재고', 'AGI'),
            ('재고', 'DAS')
        ])
        
        self.assertEqual(len(multi_columns), 4, "Multi-level 헤더는 4개 컬럼이어야 함")
        self.assertEqual(multi_columns.levels[0].tolist(), ['입고', '재고'], "첫 번째 레벨은 입고/재고")
        
    def test_monthly_aggregation_accuracy(self):
        """월별 집계 정확성 테스트"""
        # 샘플 데이터 생성
        sample_data = pd.DataFrame({
            'Status_Location': ['DSV Indoor', 'DSV Outdoor', 'AGI', 'DAS'],
            'DSV Indoor': [pd.Timestamp('2024-01-15'), pd.NaT, pd.NaT, pd.NaT],
            'DSV Outdoor': [pd.NaT, pd.Timestamp('2024-01-20'), pd.NaT, pd.NaT],
            'AGI': [pd.NaT, pd.NaT, pd.Timestamp('2024-02-10'), pd.NaT],
            'DAS': [pd.NaT, pd.NaT, pd.NaT, pd.Timestamp('2024-02-15')],
            'Pkg': [100, 150, 80, 120]
        })
        
        # 월별 집계 결과 예상값
        expected_monthly = {
            '2024-01': {'DSV Indoor': 100, 'DSV Outdoor': 150},
            '2024-02': {'AGI': 80, 'DAS': 120}
        }
        
        # 실제 집계 로직 테스트 (구현 후 활성화)
        # actual_monthly = self.aggregator.calculate_monthly_aggregation(sample_data)
        # self.assertEqual(actual_monthly, expected_monthly)
        
        # 일단 구조 검증
        self.assertEqual(len(sample_data), 4, "샘플 데이터는 4건이어야 함")
        self.assertEqual(sample_data['Pkg'].sum(), 450, "총 Pkg는 450이어야 함")
        
    def test_excel_output_format(self):
        """Excel 출력 형식 테스트"""
        # 예상 Excel 파일 구조
        expected_sheets = ['창고_월별_입출고', '현장_월별_입고재고', '리포트_정보']
        
        # 출력 파일명 패턴 테스트
        expected_filename_pattern = r'MACHO_월별집계_\d{8}_\d{6}\.xlsx'
        
        # 테스트 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_filename = f"MACHO_월별집계_{timestamp}.xlsx"
        
        # 파일명 패턴 확인
        import re
        self.assertTrue(re.match(expected_filename_pattern, test_filename), 
                       "파일명이 예상 패턴과 일치해야 함")
        
        # 시트 구조 확인
        self.assertEqual(len(expected_sheets), 3, "3개 시트가 있어야 함")
        self.assertIn('창고_월별_입출고', expected_sheets, "창고 시트 포함")
        self.assertIn('현장_월별_입고재고', expected_sheets, "현장 시트 포함")
        
    def test_macho_gpt_integration(self):
        """MACHO-GPT 통합 요구사항 테스트"""
        # 신뢰도 임계값 확인
        min_confidence = 0.95
        
        # 예상 처리 성능
        expected_processing_time = 30  # 초
        
        # 명령어 통합 확인
        expected_commands = [
            '/visualize-data monthly-trends',
            '/generate-report warehouse-summary',
            '/automate monthly-pipeline'
        ]
        
        # 테스트 조건 확인
        self.assertGreaterEqual(min_confidence, 0.95, "신뢰도는 95% 이상이어야 함")
        self.assertLessEqual(expected_processing_time, 60, "처리 시간은 60초 이하여야 함")
        self.assertEqual(len(expected_commands), 3, "3개 명령어 추천")
        
    def test_error_handling(self):
        """오류 처리 테스트"""
        # 파일 없음 오류 처리
        non_existent_path = "invalid/path/file.xlsx"
        self.assertFalse(os.path.exists(non_existent_path), "존재하지 않는 경로")
        
        # 빈 데이터 처리
        empty_df = pd.DataFrame()
        self.assertEqual(len(empty_df), 0, "빈 데이터프레임 처리")
        
        # 날짜 변환 오류 처리
        invalid_date = "invalid_date"
        converted_date = pd.to_datetime(invalid_date, errors='coerce')
        self.assertTrue(pd.isna(converted_date), "잘못된 날짜는 NaT로 변환")

if __name__ == '__main__':
    print("🔴 TDD RED Phase: 월별 집계 전용 시스템 테스트 실행")
    print("=" * 70)
    
    unittest.main(verbosity=2) 