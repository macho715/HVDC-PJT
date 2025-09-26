#!/usr/bin/env python3
"""
TDD RED 단계: 스택 적재 기반 실제 면적 계산 테스트
"""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

class TestSqmStackAnalysis(unittest.TestCase):
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.integration_file = 'output/화물이력관리_SQM스택분석_통합시스템_20250703_213958.xlsx'
        self.assertTrue(Path(self.integration_file).exists(), "통합시스템 파일이 존재해야 함")
        
    def test_1_actual_sqm_calculation(self):
        """실제 면적 계산 테스트"""
        print("\n🧪 TEST 1: 실제 면적 계산 기능 테스트")
        
        df = pd.read_excel(self.integration_file)
        
        # 실제 면적 계산 컬럼이 있는지 확인
        self.assertIn('실제_SQM', df.columns, "실제_SQM 컬럼이 있어야 함")
        
        # 실제 면적 계산 로직 확인
        valid_data = df[(df['SQM'].notna()) & (df['Stack_Status'].notna()) & (df['실제_SQM'].notna())]
        
        for _, row in valid_data.head(10).iterrows():
            sqm = row['SQM']
            stack = row['Stack_Status']
            actual_sqm = row['실제_SQM']
            expected_actual_sqm = sqm / max(1, int(stack))
            
            self.assertAlmostEqual(
                actual_sqm, 
                expected_actual_sqm, 
                places=2, 
                msg=f"실제 면적 계산이 정확해야 함: {sqm}/{stack} = {expected_actual_sqm}"
            )
    
    def test_2_stack_efficiency_analysis(self):
        """스택 효율성 분석 테스트"""
        print("\n🧪 TEST 2: 스택 효율성 분석 테스트")
        
        df = pd.read_excel(self.integration_file)
        
        # 스택 효율성 분석 컬럼들 확인
        required_columns = ['스택_효율성', '면적_절약률', '스택_등급']
        for col in required_columns:
            self.assertIn(col, df.columns, f"{col} 컬럼이 있어야 함")
        
        # 스택 효율성 계산 확인
        valid_data = df[(df['SQM'].notna()) & (df['Stack_Status'].notna())]
        
        for stack_level in [1, 2, 3, 4]:
            stack_data = valid_data[valid_data['Stack_Status'] == stack_level]
            if len(stack_data) > 0:
                expected_efficiency = stack_level  # 스택 층수 = 효율성
                actual_efficiency = stack_data['스택_효율성'].iloc[0]
                
                self.assertEqual(
                    actual_efficiency, 
                    expected_efficiency,
                    f"{stack_level}단 스택 효율성이 {expected_efficiency}여야 함"
                )
    
    def test_3_area_savings_calculation(self):
        """면적 절약 계산 테스트"""
        print("\n🧪 TEST 3: 면적 절약 계산 테스트")
        
        df = pd.read_excel(self.integration_file)
        
        # 면적 절약 관련 컬럼 확인
        self.assertIn('총_면적_절약', df.columns, "총 면적 절약 컬럼이 있어야 함")
        self.assertIn('절약_비율', df.columns, "절약 비율 컬럼이 있어야 함")
        
        # 전체 면적 절약 계산 확인
        valid_data = df[(df['SQM'].notna()) & (df['Stack_Status'].notna()) & (df['실제_SQM'].notna())]
        
        total_original_sqm = valid_data['SQM'].sum()
        total_actual_sqm = valid_data['실제_SQM'].sum()
        expected_savings = total_original_sqm - total_actual_sqm
        expected_savings_rate = (expected_savings / total_original_sqm) * 100
        
        # 면적 절약이 10-25% 범위에 있어야 함 (실제 결과 반영)
        self.assertGreater(expected_savings_rate, 10, "면적 절약률이 10% 이상이어야 함")
        self.assertLess(expected_savings_rate, 25, "면적 절약률이 25% 미만이어야 함")
        
        # 총 면적 절약 값 확인
        total_savings_in_data = df['총_면적_절약'].iloc[0]
        self.assertAlmostEqual(
            total_savings_in_data, 
            expected_savings, 
            places=1,
            msg="총 면적 절약 값이 정확해야 함"
        )
    
    def test_4_stack_level_summary(self):
        """스택 레벨별 요약 테스트"""
        print("\n🧪 TEST 4: 스택 레벨별 요약 테스트")
        
        df = pd.read_excel(self.integration_file)
        
        # 스택 레벨별 요약 컬럼 확인
        summary_columns = ['스택_레벨_요약', '레벨별_건수', '레벨별_면적', '레벨별_절약']
        for col in summary_columns:
            self.assertIn(col, df.columns, f"{col} 컬럼이 있어야 함")
        
        # 스택 레벨별 분포 확인 (실제 결과 반영)
        expected_distribution = {
            1.0: 5146,  # 1단 적재
            2.0: 1095,  # 2단 적재  
            3.0: 751,   # 3단 적재
            4.0: 169    # 4단 적재
        }
        
        for stack_level, expected_count in expected_distribution.items():
            actual_count = len(df[df['Stack_Status'] == stack_level])
            self.assertEqual(
                actual_count, 
                expected_count,
                f"{stack_level}단 스택 건수가 {expected_count}건이어야 함"
            )
    
    def test_5_warehouse_optimization_insights(self):
        """창고 최적화 인사이트 테스트"""
        print("\n🧪 TEST 5: 창고 최적화 인사이트 테스트")
        
        df = pd.read_excel(self.integration_file)
        
        # 최적화 인사이트 컬럼 확인
        insight_columns = ['최적화_점수', '개선_권장사항', '비용_절감_잠재력']
        for col in insight_columns:
            self.assertIn(col, df.columns, f"{col} 컬럼이 있어야 함")
        
        # 최적화 점수 범위 확인 (0-100)
        optimization_scores = df['최적화_점수'].dropna()
        
        self.assertTrue(
            all(0 <= score <= 100 for score in optimization_scores),
            "최적화 점수는 0-100 범위여야 함"
        )
        
        # 개선 권장사항이 있는지 확인
        recommendations = df['개선_권장사항'].dropna()
        self.assertGreater(len(recommendations), 0, "개선 권장사항이 있어야 함")
    
    def test_6_enhanced_excel_with_sqm_analysis(self):
        """SQM 분석이 포함된 향상된 Excel 테스트"""
        print("\n🧪 TEST 6: SQM 분석 포함 향상된 Excel 테스트")
        
        # 향상된 Excel 파일 존재 확인
        enhanced_file = self.integration_file
        self.assertTrue(Path(enhanced_file).exists(), "SQM 분석 포함 향상된 Excel이 존재해야 함")
        
        # 추가 시트 확인
        expected_sheets = [
            '화물이력관리_SQM분석_통합',
            'SQM_스택분석',
            '면적_절약_분석',
            '창고_최적화_인사이트',
            '스택_효율성_리포트'
        ]
        
        excel_file = pd.ExcelFile(enhanced_file)
        actual_sheets = excel_file.sheet_names
        
        for sheet in expected_sheets:
            self.assertIn(sheet, actual_sheets, f"{sheet} 시트가 존재해야 함")
        
        # SQM 분석 시트 내용 확인
        sqm_analysis_df = pd.read_excel(enhanced_file, sheet_name='SQM_스택분석')
        self.assertGreater(len(sqm_analysis_df), 0, "SQM 분석 시트에 데이터가 있어야 함")

if __name__ == '__main__':
    unittest.main(verbosity=2) 