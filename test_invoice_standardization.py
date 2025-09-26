#!/usr/bin/env python3
"""
원본 INVOICE 데이터 표준화 테스트
- TDD 방식으로 INVOICE 데이터 표준화 검증
- 데이터 품질 및 구조 검증
- 피벗 테이블과의 일관성 검증
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import os

class TestInvoiceStandardization:
    """INVOICE 데이터 표준화 테스트"""
    
    @pytest.fixture
    def invoice_file_path(self):
        """원본 INVOICE 파일 경로"""
        return r"C:\HVDC PJT\hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_INVOICE_.xlsx"
    
    @pytest.fixture
    def expected_columns(self):
        """표준화된 INVOICE 데이터가 가져야 할 필수 컬럼"""
        return [
            'Category',           # 실제 창고명 (DSV Outdoor, DSV Indoor, etc.)
            'HVDC CODE 1',       # 프로젝트 코드 (주로 'HVDC')
            'HVDC CODE 2',       # 작업 유형 (ADOPT 등)
            'HVDC CODE 3',       # 화물 유형 (HE, SIM, SCT 등)
            'HVDC CODE 4',       # 추가 분류 코드
            'HVDC CODE 5',       # 비용 유형 (HANDLING/RENT)
            'Amount',            # 금액
            'pkg'                # 패키지 수
        ]
    
    @pytest.fixture
    def expected_warehouse_names(self):
        """예상되는 창고명 목록"""
        return [
            'DSV Outdoor',
            'DSV Indoor', 
            'DSV Al Markaz',
            'DSV MZP',
            'AAA Storage'
        ]
    
    @pytest.fixture
    def expected_cargo_types(self):
        """예상되는 화물 유형"""
        return ['HE', 'SIM', 'SCT', 'ALL']
    
    def test_invoice_file_exists(self, invoice_file_path):
        """원본 INVOICE 파일 존재 확인"""
        assert os.path.exists(invoice_file_path), f"INVOICE 파일이 존재하지 않음: {invoice_file_path}"
        
    def test_invoice_file_readable(self, invoice_file_path):
        """INVOICE 파일 읽기 가능 여부 확인"""
        try:
            df = pd.read_excel(invoice_file_path)
            assert len(df) > 0, "INVOICE 파일이 비어있음"
            assert len(df.columns) > 0, "INVOICE 파일에 컬럼이 없음"
        except Exception as e:
            pytest.fail(f"INVOICE 파일 읽기 실패: {e}")
    
    def test_required_columns_present(self, invoice_file_path, expected_columns):
        """필수 컬럼 존재 확인"""
        df = pd.read_excel(invoice_file_path)
        missing_columns = set(expected_columns) - set(df.columns)
        assert len(missing_columns) == 0, f"누락된 필수 컬럼: {missing_columns}"
    
    def test_warehouse_names_validation(self, invoice_file_path, expected_warehouse_names):
        """창고명 검증 - Category 컬럼이 실제 창고명을 포함하는지 확인"""
        df = pd.read_excel(invoice_file_path)
        
        if 'Category' in df.columns:
            unique_categories = df['Category'].dropna().unique()
            found_warehouses = [wh for wh in expected_warehouse_names 
                              if any(wh in str(cat) for cat in unique_categories)]
            
            assert len(found_warehouses) > 0, f"예상 창고명이 Category에서 발견되지 않음: {expected_warehouse_names}"
            
    def test_cargo_types_validation(self, invoice_file_path, expected_cargo_types):
        """화물 유형 검증 - HVDC CODE 3이 예상 화물 유형을 포함하는지 확인"""
        df = pd.read_excel(invoice_file_path)
        
        if 'HVDC CODE 3' in df.columns:
            unique_cargo_types = df['HVDC CODE 3'].dropna().unique()
            found_cargo_types = [ct for ct in expected_cargo_types 
                               if ct in unique_cargo_types]
            
            assert len(found_cargo_types) > 0, f"예상 화물 유형이 발견되지 않음: {expected_cargo_types}"
    
    def test_amount_column_validation(self, invoice_file_path):
        """금액 컬럼 검증"""
        df = pd.read_excel(invoice_file_path)
        
        amount_columns = [col for col in df.columns if 'amount' in col.lower()]
        assert len(amount_columns) > 0, "금액 관련 컬럼이 발견되지 않음"
        
        # 첫 번째 금액 컬럼 검증
        amount_col = amount_columns[0]
        numeric_amounts = pd.to_numeric(df[amount_col], errors='coerce')
        valid_amounts = numeric_amounts.dropna()
        
        assert len(valid_amounts) > 0, f"유효한 금액이 없음: {amount_col}"
        assert (valid_amounts >= 0).all(), f"음수 금액이 존재함: {amount_col}"
        
    def test_package_count_validation(self, invoice_file_path):
        """패키지 수 검증"""
        df = pd.read_excel(invoice_file_path)
        
        pkg_columns = [col for col in df.columns if 'pkg' in col.lower()]
        assert len(pkg_columns) > 0, "패키지 수 컬럼이 발견되지 않음"
        
        # 첫 번째 패키지 컬럼 검증
        pkg_col = pkg_columns[0]
        numeric_pkgs = pd.to_numeric(df[pkg_col], errors='coerce')
        valid_pkgs = numeric_pkgs.dropna()
        
        assert len(valid_pkgs) > 0, f"유효한 패키지 수가 없음: {pkg_col}"
        assert (valid_pkgs >= 0).all(), f"음수 패키지 수가 존재함: {pkg_col}"
        
    def test_data_completeness(self, invoice_file_path):
        """데이터 완전성 검증"""
        df = pd.read_excel(invoice_file_path)
        
        # 전체 행 수 확인 - 실제 파일 기준
        expected_rows = 465  # 실제 분석 결과 기준
        tolerance = 0.05  # 5% 허용 오차
        min_rows = int(expected_rows * (1 - tolerance))
        max_rows = int(expected_rows * (1 + tolerance))
        
        assert min_rows <= len(df) <= max_rows, \
            f"데이터 행 수가 예상 범위를 벗어남: {len(df)}행 (예상: {min_rows}-{max_rows}행)"
        
        # 핵심 컬럼의 결측값 비율 확인
        core_columns = ['Category', 'HVDC CODE 1', 'HVDC CODE 3']
        existing_core_columns = [col for col in core_columns if col in df.columns]
        
        for col in existing_core_columns:
            null_ratio = df[col].isnull().sum() / len(df)
            assert null_ratio < 0.5, f"핵심 컬럼 {col}의 결측값 비율이 너무 높음: {null_ratio:.1%}"
    
    def test_total_amount_consistency(self, invoice_file_path):
        """총 금액 일관성 검증 - 실제 파일 데이터 기준"""
        df = pd.read_excel(invoice_file_path)
        
        amount_columns = [col for col in df.columns if 'amount' in col.lower()]
        if len(amount_columns) > 0:
            amount_col = amount_columns[0]
            total_amount = pd.to_numeric(df[amount_col], errors='coerce').sum()
            
            # 실제 파일 기준 검증 (유효한 금액 데이터 존재 여부)
            expected_total = 7416326.89  # 실제 분석 결과 기준
            tolerance = 0.05  # 5% 허용 오차
            
            assert abs(total_amount - expected_total) / expected_total <= tolerance, \
                f"총 금액이 예상값과 차이 남: 실제 {total_amount:,.2f}, 예상 {expected_total:,.2f}"
    
    def test_warehouse_distribution_pattern(self, invoice_file_path, expected_warehouse_names):
        """창고별 분포 패턴 검증"""
        df = pd.read_excel(invoice_file_path)
        
        if 'Category' in df.columns:
            # 각 창고별 데이터 수 확인
            warehouse_counts = {}
            for warehouse in expected_warehouse_names:
                count = sum(df['Category'].astype(str).str.contains(warehouse, na=False))
                warehouse_counts[warehouse] = count
            
            # DSV Outdoor가 가장 많아야 함 (실제 분석 기준: 301건)
            dsv_outdoor_count = warehouse_counts.get('DSV Outdoor', 0)
            expected_dsv_outdoor = 301
            tolerance = 0.1  # 10% 허용 오차
            min_count = int(expected_dsv_outdoor * (1 - tolerance))
            
            assert dsv_outdoor_count >= min_count, \
                f"DSV Outdoor 데이터가 예상보다 적음: {dsv_outdoor_count}건 (최소 {min_count}건 예상)"
            
    def test_he_sim_others_classification_base(self, invoice_file_path):
        """HE/SIM vs OTHERS 분류 기반 데이터 검증"""
        df = pd.read_excel(invoice_file_path)
        
        if 'HVDC CODE 3' in df.columns:
            cargo_types = df['HVDC CODE 3'].dropna().unique()
            
            # HE/SIM 관련 데이터 확인
            he_sim_types = [ct for ct in cargo_types if ct in ['HE', 'SIM']]
            others_types = [ct for ct in cargo_types if ct not in ['HE', 'SIM']]
            
            assert len(he_sim_types) > 0, "HE/SIM 화물 유형이 발견되지 않음"
            assert len(others_types) > 0, "OTHERS 화물 유형이 발견되지 않음"

def run_standardization_tests():
    """표준화 테스트 실행"""
    print("🧪 INVOICE 데이터 표준화 테스트 시작")
    print("=" * 50)
    
    # pytest 실행
    result = pytest.main([__file__, "-v", "--tb=short"])
    
    if result == 0:
        print("\n✅ 모든 테스트 통과 - 표준화 작업 진행 가능")
        return True
    else:
        print("\n❌ 테스트 실패 - 데이터 구조 확인 필요")
        return False

if __name__ == "__main__":
    success = run_standardization_tests()
    
    if success:
        print("\n🔧 **추천 명령어:**")
        print("/implement_data_cleaner [데이터 클리너 구현]")
        print("/create_standard_schema [표준 스키마 정의]")
        print("/analyze_data_quality [데이터 품질 상세 분석]")
    else:
        print("\n🔧 **추천 명령어:**")
        print("/investigate_data_structure [데이터 구조 상세 조사]")
        print("/fix_data_issues [데이터 이슈 수정]")
        print("/validate_file_format [파일 형식 검증]") 