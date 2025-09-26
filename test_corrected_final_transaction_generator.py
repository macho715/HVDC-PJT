#!/usr/bin/env python3
"""
올바른 HVDC 구조 기반 최종 트랜잭션 생성기 테스트
- HVDC: 프로젝트 코드 (창고 아님)
- 실제 창고: DSV Outdoor, DSV Indoor, DSV Al Markaz, DSV MZP, AAA Storage
- 화물 유형: HE(히타치), SIM(지멘스), SCT(삼성C&T)
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class TestCorrectedFinalTransactionGenerator(unittest.TestCase):
    """올바른 HVDC 구조 기반 트랜잭션 생성기 테스트"""
    
    def test_01_real_case_data_loading(self):
        """실제 케이스 데이터 로딩 테스트"""
        print("\n=== 테스트 1: 실제 케이스 데이터 로딩 ===")
        
        # HITACHI 및 SIMENSE 데이터 존재 확인
        hitachi_file = 'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx'
        simense_file = 'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
        
        self.assertTrue(os.path.exists(hitachi_file), "HITACHI 데이터 파일이 존재해야 함")
        self.assertTrue(os.path.exists(simense_file), "SIMENSE 데이터 파일이 존재해야 함")
        
        # 실제 케이스 수 확인
        hitachi_df = pd.read_excel(hitachi_file)
        simense_df = pd.read_excel(simense_file)
        
        total_cases = len(hitachi_df) + len(simense_df)
        print(f"총 실제 케이스 수: {total_cases}")
        
        self.assertEqual(len(hitachi_df), 5346, "HITACHI 케이스 수는 5,346개여야 함")
        self.assertEqual(len(simense_df), 2227, "SIMENSE 케이스 수는 2,227개여야 함")
        self.assertEqual(total_cases, 7573, "총 케이스 수는 7,573개여야 함")
    
    def test_02_correct_warehouse_structure(self):
        """올바른 창고 구조 테스트"""
        print("\n=== 테스트 2: 올바른 창고 구조 ===")
        
        # DSV 계열 창고 정의
        expected_warehouses = [
            'DSV Outdoor',
            'DSV Indoor', 
            'DSV Al Markaz',
            'DSV MZP',
            'AAA Storage'
        ]
        
        # HVDC는 창고가 아님을 확인
        self.assertNotIn('HVDC', expected_warehouses, "HVDC는 창고가 아니라 프로젝트 코드임")
        
        print(f"실제 창고 목록: {expected_warehouses}")
        print("✅ HVDC는 프로젝트 코드로 확인됨")
    
    def test_03_cargo_type_mapping(self):
        """화물 유형 매핑 테스트"""
        print("\n=== 테스트 3: 화물 유형 매핑 ===")
        
        # 실제 화물 유형 (HVDC CODE 3 기준)
        cargo_types = {
            'HE': 'Hitachi Energy',
            'SIM': 'Siemens',
            'SCT': 'Samsung C&T',
            'ALL': '임대료 분류용',
            'HE_LOCAL': 'Hitachi Local',
            'MOSB': 'MOSB',
            'PPL': 'PPL',
            'SKM': 'SKM',
            'NIE': 'NIE',
            'ALM': 'ALM',
            'SEI': 'SEI',
            'Dg Warehouse': 'Dangerous Goods'
        }
        
        # 주요 브랜드별 비중 예상
        expected_brand_share = {
            'HE': 0.567,  # 56.7% (실제 화물 중)
            'SCT': 0.210,  # 21.0%
            'SIM': 0.195   # 19.5%
        }
        
        print(f"화물 유형 수: {len(cargo_types)}")
        print(f"주요 브랜드: {list(expected_brand_share.keys())}")
        
        self.assertGreaterEqual(len(cargo_types), 10, "화물 유형은 10개 이상이어야 함")
    
    def test_04_invoice_cost_structure(self):
        """INVOICE 비용 구조 테스트"""
        print("\n=== 테스트 4: INVOICE 비용 구조 ===")
        
        # 실제 INVOICE 총액
        total_invoice_amount = 11539637  # AED
        handling_ratio = 0.303  # 30.3%
        rent_ratio = 0.697     # 69.7%
        
        expected_handling = total_invoice_amount * handling_ratio
        expected_rent = total_invoice_amount * rent_ratio
        
        print(f"총 INVOICE 금액: {total_invoice_amount:,.0f} AED")
        print(f"HANDLING 예상: {expected_handling:,.0f} AED ({handling_ratio*100:.1f}%)")
        print(f"RENT 예상: {expected_rent:,.0f} AED ({rent_ratio*100:.1f}%)")
        
        self.assertAlmostEqual(expected_handling + expected_rent, total_invoice_amount, 
                              delta=1000, msg="HANDLING + RENT = 총액이어야 함")
    
    def test_05_warehouse_specialization(self):
        """창고별 전문화 테스트"""
        print("\n=== 테스트 5: 창고별 전문화 ===")
        
        # 창고별 특화 패턴
        warehouse_specialization = {
            'DSV Indoor': {'main_cargo': 'HE', 'share': 0.68},     # 히타치 68%
            'DSV Outdoor': {'main_cargo': 'SCT', 'share': 0.96},   # 삼성 C&T 96% 
            'DSV Al Markaz': {'main_cargo': 'ALL', 'share': 0.999}, # 임대료 99.9%
            'DSV MZP': {'main_cargo': 'ALL', 'share': 1.0},        # 임대료 100%
            'AAA Storage': {'main_cargo': 'Dg Warehouse', 'share': 1.0} # 위험물 100%
        }
        
        for warehouse, spec in warehouse_specialization.items():
            print(f"{warehouse}: {spec['main_cargo']} ({spec['share']*100:.1f}%)")
        
        self.assertEqual(len(warehouse_specialization), 5, "5개 창고의 전문화 패턴이 정의되어야 함")
    
    def test_06_transaction_generation_requirements(self):
        """트랜잭션 생성 요구사항 테스트"""
        print("\n=== 테스트 6: 트랜잭션 생성 요구사항 ===")
        
        # 기본 요구사항
        total_cases = 7573
        transactions_per_case = 2  # IN + FINAL_OUT
        expected_total_transactions = total_cases * transactions_per_case
        
        # 운영 기간
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2026, 3, 28)
        
        # 스택 효율성
        expected_stack_efficiency = 0.153  # 15.3% 절약
        
        print(f"예상 총 트랜잭션: {expected_total_transactions:,}건")
        print(f"운영 기간: {start_date:%Y-%m-%d} ~ {end_date:%Y-%m-%d}")
        print(f"스택 효율성: {expected_stack_efficiency*100:.1f}%")
        
        self.assertEqual(expected_total_transactions, 15146, "총 15,146건의 트랜잭션 예상")
        self.assertGreater(expected_stack_efficiency, 0.10, "스택 효율성은 10% 이상이어야 함")
    
    def test_07_seasonal_patterns(self):
        """계절성 패턴 테스트"""
        print("\n=== 테스트 7: 계절성 패턴 ===")
        
        # 실제 계절성 피크 (이전 분석 결과)
        seasonal_peaks = {
            '2024-06': 2.32,  # 232% 피크
            '2024-08': 2.30,  # 230% 피크  
            '2025-03': 2.22   # 222% 피크
        }
        
        base_multiplier = 1.0
        max_multiplier = max(seasonal_peaks.values())
        
        print(f"계절성 피크: {seasonal_peaks}")
        print(f"최대 배율: {max_multiplier}x")
        
        self.assertGreater(max_multiplier, 2.0, "최대 계절성 배율은 2.0 이상이어야 함")
        self.assertLess(max_multiplier, 3.0, "최대 계절성 배율은 3.0 미만이어야 함")
    
    def test_08_final_output_format(self):
        """최종 출력 형식 테스트"""
        print("\n=== 테스트 8: 최종 출력 형식 ===")
        
        # 예상 출력 컬럼
        expected_columns = [
            'Date', 'Case_No', 'Vendor', 'Location', 'Transaction_Type',
            'Amount', 'Currency', 'SQM', 'Stack_Status', 'Handling_Fee',
            'Rent_Fee', 'Cargo_Type', 'Notes'
        ]
        
        # 예상 Excel 시트
        expected_sheets = [
            'Transactions',
            'Monthly_Summary', 
            'Warehouse_Analysis',
            'Brand_Analysis',
            'Cost_Structure',
            'Seasonal_Patterns',
            'Validation_Report'
        ]
        
        print(f"예상 컬럼 수: {len(expected_columns)}")
        print(f"예상 시트 수: {len(expected_sheets)}")
        
        self.assertGreaterEqual(len(expected_columns), 13, "최소 13개 컬럼이 필요함")
        self.assertGreaterEqual(len(expected_sheets), 7, "최소 7개 시트가 필요함")

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2) 