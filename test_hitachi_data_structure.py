#!/usr/bin/env python3
"""
HITACHI 데이터 구조 확인 테스트
MACHO-GPT v3.4-mini | TDD 원칙에 따른 데이터 검증

목적:
1. HITACHI 데이터 파일의 실제 구조 확인
2. 모든 시트 및 데이터 로드 검증
3. 예상되는 데이터 건수 확인
"""

import unittest
import pandas as pd
import numpy as np
import os
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_hitachi_data.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestHitachiDataStructure(unittest.TestCase):
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.file_path = "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.expected_min_rows = 1000  # 3MB 파일이면 최소 1000건 이상 예상
        
    def test_hitachi_file_should_exist_and_be_accessible(self):
        """HITACHI 파일이 존재하고 접근 가능해야 함"""
        # Given: 파일 경로
        file_path = self.file_path
        
        # When: 파일 존재 확인
        file_exists = os.path.exists(file_path)
        
        # Then: 파일이 존재해야 함
        self.assertTrue(file_exists, f"HITACHI 파일이 존재해야 함: {file_path}")
        
        # And: 파일 크기가 1MB 이상이어야 함
        file_size = os.path.getsize(file_path)
        self.assertGreater(file_size, 1024*1024, "파일 크기가 1MB 이상이어야 함")
        
        logger.info(f"파일 크기: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)")
    
    def test_hitachi_excel_should_have_multiple_sheets(self):
        """HITACHI Excel 파일의 시트 구조 확인"""
        # Given: Excel 파일
        file_path = self.file_path
        
        # When: Excel 파일 정보 확인
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        # Then: 시트가 존재해야 함
        self.assertGreater(len(sheet_names), 0, "Excel 파일에 시트가 존재해야 함")
        
        logger.info(f"시트 목록: {sheet_names}")
        
        # And: 각 시트의 데이터 확인
        for sheet_name in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"시트 '{sheet_name}': {len(df):,}건, 컬럼 {len(df.columns)}개")
            
            # 빈 시트가 아니어야 함
            if len(df) > 0:
                self.assertGreater(len(df.columns), 0, f"시트 '{sheet_name}'에 컬럼이 존재해야 함")
        
        return sheet_names
    
    def test_hitachi_data_should_have_expected_columns(self):
        """HITACHI 데이터가 예상 컬럼들을 가져야 함"""
        # Given: 예상 컬럼들
        expected_columns = [
            'no.', 'Case No.', 'Pkg', 'Site', 
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'MOSB'
        ]
        
        # When: 첫 번째 시트 데이터 로드
        df = pd.read_excel(self.file_path, sheet_name=0)
        
        # Then: 최소 기본 컬럼들이 존재해야 함
        basic_columns_found = []
        for col in expected_columns:
            if col in df.columns:
                basic_columns_found.append(col)
        
        self.assertGreater(len(basic_columns_found), 0, 
                          f"기본 컬럼들이 존재해야 함. 찾은 컬럼: {basic_columns_found}")
        
        logger.info(f"전체 컬럼 ({len(df.columns)}개): {list(df.columns)}")
        logger.info(f"기본 컬럼 발견: {basic_columns_found}")
        
        return df.columns.tolist()
    
    def test_hitachi_data_should_have_sufficient_rows(self):
        """HITACHI 데이터가 충분한 행을 가져야 함"""
        # Given: Excel 파일
        file_path = self.file_path
        
        # When: 모든 시트의 데이터 로드
        excel_file = pd.ExcelFile(file_path)
        total_rows = 0
        sheet_data = {}
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            sheet_data[sheet_name] = len(df)
            total_rows += len(df)
        
        # Then: 총 행수가 예상보다 많아야 함
        self.assertGreater(total_rows, 100, 
                          f"총 데이터가 100건 이상이어야 함. 현재: {total_rows:,}건")
        
        logger.info(f"총 데이터: {total_rows:,}건")
        for sheet_name, row_count in sheet_data.items():
            logger.info(f"  시트 '{sheet_name}': {row_count:,}건")
        
        return total_rows, sheet_data
    
    def test_hitachi_data_loading_with_different_methods(self):
        """다양한 방법으로 HITACHI 데이터 로드 테스트"""
        # Given: 파일 경로
        file_path = self.file_path
        
        # When: 다양한 방법으로 데이터 로드
        methods_results = {}
        
        # 방법 1: 기본 로드
        try:
            df1 = pd.read_excel(file_path)
            methods_results['basic'] = len(df1)
        except Exception as e:
            methods_results['basic'] = f"Error: {e}"
        
        # 방법 2: 첫 번째 시트 명시적 로드
        try:
            df2 = pd.read_excel(file_path, sheet_name=0)
            methods_results['sheet_0'] = len(df2)
        except Exception as e:
            methods_results['sheet_0'] = f"Error: {e}"
        
        # 방법 3: 모든 시트 로드
        try:
            excel_file = pd.ExcelFile(file_path)
            total_rows = 0
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                total_rows += len(df)
            methods_results['all_sheets'] = total_rows
        except Exception as e:
            methods_results['all_sheets'] = f"Error: {e}"
        
        # 방법 4: 헤더 없이 로드
        try:
            df4 = pd.read_excel(file_path, header=None)
            methods_results['no_header'] = len(df4)
        except Exception as e:
            methods_results['no_header'] = f"Error: {e}"
        
        # Then: 결과 확인
        logger.info("다양한 로드 방법 결과:")
        for method, result in methods_results.items():
            logger.info(f"  {method}: {result}")
        
        # 최소 하나의 방법은 성공해야 함
        successful_methods = [method for method, result in methods_results.items() 
                            if isinstance(result, int) and result > 0]
        
        self.assertGreater(len(successful_methods), 0, 
                          "최소 하나의 방법으로는 데이터를 로드할 수 있어야 함")
        
        return methods_results
    
    def test_hitachi_data_quality_check(self):
        """HITACHI 데이터 품질 확인"""
        # Given: 데이터 로드
        df = pd.read_excel(self.file_path, sheet_name=0)
        
        # When: 데이터 품질 확인
        quality_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'null_rows': df.isnull().all(axis=1).sum(),
            'duplicate_rows': df.duplicated().sum(),
            'empty_columns': (df.isnull().all()).sum()
        }
        
        # Then: 품질 기준 확인
        self.assertGreater(quality_report['total_rows'], 0, "데이터 행이 존재해야 함")
        self.assertGreater(quality_report['total_columns'], 0, "데이터 컬럼이 존재해야 함")
        
        # 전체가 null인 행은 50% 미만이어야 함
        null_percentage = (quality_report['null_rows'] / quality_report['total_rows']) * 100
        self.assertLess(null_percentage, 50, 
                       f"전체 null 행이 50% 미만이어야 함. 현재: {null_percentage:.1f}%")
        
        logger.info("데이터 품질 리포트:")
        for key, value in quality_report.items():
            logger.info(f"  {key}: {value:,}")
        
        return quality_report

if __name__ == '__main__':
    try:
        logger.info("🧪 HITACHI 데이터 구조 테스트 시작")
        unittest.main(verbosity=2, exit=False)
        logger.info("✅ 모든 테스트 완료")
    except Exception as e:
        logger.error(f"❌ 테스트 실행 중 오류: {e}")
        print(f"오류 발생: {e}") 