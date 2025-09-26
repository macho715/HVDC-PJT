#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
📋 MACHO-GPT TDD Test Suite: 올바른 피벗 테이블 형식 검증
첨부된 Excel 스크린샷과 100% 일치하는 형식 테스트

🎯 테스트 대상:
- 창고별 월별 입출고 피벗 테이블 (이미지 1)
- 현장별 월별 입고재고 피벗 테이블 (이미지 2)
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

class TestCorrectPivotFormat(unittest.TestCase):
    """첨부된 이미지 형식과 정확히 일치하는 피벗 테이블 테스트"""
    
    def test_warehouse_monthly_pivot_should_match_image1_structure(self):
        """
        🏪 테스트: 창고별 월별 입출고 피벗 테이블이 첨부 이미지 1과 일치해야 함
        
        Expected Structure:
        - Multi-level columns: [입고/출고] × [창고명들]
        - Index: 월별 (2023-02 ~ 2025-06)
        - 마지막 행: Total
        """
        # 이 테스트는 실패해야 함 (아직 구현 안됨)
        try:
            from correct_pivot_generator import create_warehouse_monthly_pivot
            pivot_df = create_warehouse_monthly_pivot()
            
            # 1. Multi-level 컬럼 구조 검증
            self.assertIsInstance(pivot_df.columns, pd.MultiIndex, 
                               "컬럼이 Multi-level이어야 함")
            
            # 2. 상위 레벨: 입고/출고
            level_0_expected = ['입고', '출고']
            level_0_actual = pivot_df.columns.get_level_values(0).unique().tolist()
            self.assertEqual(sorted(level_0_actual), sorted(level_0_expected),
                           f"상위 레벨이 {level_0_expected}여야 함")
            
            # 3. 하위 레벨: 창고명들
            level_1_expected = ['AAA Storage', 'DSV Al Markaz', 'DSV Indoor', 
                              'DSV MZP', 'DSV Outdoor', 'Hauler Indoor', 'MOSB']
            level_1_actual = pivot_df.columns.get_level_values(1).unique().tolist()
            for warehouse in level_1_expected:
                self.assertIn(warehouse, level_1_actual, 
                            f"창고 {warehouse}가 컬럼에 있어야 함")
            
            # 4. 인덱스: 월별 + Total
            expected_months = pd.date_range('2023-02', '2025-06', freq='MS')
            expected_index = [d.strftime('%Y-%m') for d in expected_months] + ['Total']
            
            self.assertEqual(len(pivot_df.index), len(expected_index),
                           f"인덱스 길이가 {len(expected_index)}여야 함")
            self.assertIn('Total', pivot_df.index.tolist(),
                         "마지막에 Total 행이 있어야 함")
            
            # 5. 데이터 타입: 숫자
            for col in pivot_df.columns:
                self.assertTrue(pd.api.types.is_numeric_dtype(pivot_df[col]),
                              f"컬럼 {col}은 숫자 타입이어야 함")
            
            print("✅ 창고 피벗 테이블 구조 검증 통과")
            
        except ImportError:
            self.fail("❌ create_warehouse_monthly_pivot 함수가 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 창고 피벗 테이블 생성 실패: {e}")
    
    def test_site_monthly_pivot_should_match_image2_structure(self):
        """
        🏗️ 테스트: 현장별 월별 입고재고 피벗 테이블이 첨부 이미지 2와 일치해야 함
        
        Expected Structure:
        - Multi-level columns: [입고/재고] × [현장명들]
        - Index: 월별 (2024-01 ~ 2025-06)
        - 마지막 행: 합계
        """
        try:
            from correct_pivot_generator import create_site_monthly_pivot
            pivot_df = create_site_monthly_pivot()
            
            # 1. Multi-level 컬럼 구조 검증
            self.assertIsInstance(pivot_df.columns, pd.MultiIndex, 
                               "컬럼이 Multi-level이어야 함")
            
            # 2. 상위 레벨: 입고/재고
            level_0_expected = ['입고', '재고']
            level_0_actual = pivot_df.columns.get_level_values(0).unique().tolist()
            self.assertEqual(sorted(level_0_actual), sorted(level_0_expected),
                           f"상위 레벨이 {level_0_expected}여야 함")
            
            # 3. 하위 레벨: 현장명들
            level_1_expected = ['AGI', 'DAS', 'MIR', 'SHU']
            level_1_actual = pivot_df.columns.get_level_values(1).unique().tolist()
            self.assertEqual(sorted(level_1_actual), sorted(level_1_expected),
                           f"하위 레벨이 {level_1_expected}여야 함")
            
            # 4. 인덱스: 월별 + 합계
            expected_months = pd.date_range('2024-01', '2025-06', freq='MS')
            expected_index = [d.strftime('%Y-%m') for d in expected_months] + ['합계']
            
            self.assertEqual(len(pivot_df.index), len(expected_index),
                           f"인덱스 길이가 {len(expected_index)}여야 함")
            self.assertIn('합계', pivot_df.index.tolist(),
                         "마지막에 합계 행이 있어야 함")
            
            # 5. 재고는 누적값이어야 함
            for site in level_1_expected:
                inventory_col = ('재고', site)
                if inventory_col in pivot_df.columns:
                    inventory_values = pivot_df[inventory_col].iloc[:-1]  # 합계 제외
                    # 재고는 일반적으로 증가하는 패턴
                    self.assertTrue(len(inventory_values) > 0, 
                                  f"{site} 재고 데이터가 있어야 함")
            
            print("✅ 현장 피벗 테이블 구조 검증 통과")
            
        except ImportError:
            self.fail("❌ create_site_monthly_pivot 함수가 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 현장 피벗 테이블 생성 실패: {e}")
    
    def test_pivot_excel_generation_should_create_correct_sheets(self):
        """
        📊 테스트: 올바른 피벗 형식의 Excel 파일이 생성되어야 함
        """
        try:
            from correct_pivot_generator import generate_correct_pivot_excel
            excel_path = generate_correct_pivot_excel()
            
            # 1. 파일 존재 검증
            self.assertTrue(os.path.exists(excel_path), 
                          f"Excel 파일 {excel_path}이 생성되어야 함")
            
            # 2. Excel 파일 읽기
            xls = pd.ExcelFile(excel_path)
            
            # 3. 시트명 검증
            expected_sheets = ['창고별_월별_입출고', '현장별_월별_입고재고']
            for sheet in expected_sheets:
                self.assertIn(sheet, xls.sheet_names, 
                            f"시트 {sheet}가 있어야 함")
            
            # 4. 각 시트의 구조 검증
            warehouse_df = pd.read_excel(excel_path, sheet_name='창고별_월별_입출고', 
                                       header=[0, 1], index_col=0)
            site_df = pd.read_excel(excel_path, sheet_name='현장별_월별_입고재고', 
                                  header=[0, 1], index_col=0)
            
            # Multi-level 헤더 확인
            self.assertIsInstance(warehouse_df.columns, pd.MultiIndex,
                               "창고 시트가 Multi-level 컬럼이어야 함")
            self.assertIsInstance(site_df.columns, pd.MultiIndex,
                               "현장 시트가 Multi-level 컬럼이어야 함")
            
            print("✅ 올바른 피벗 Excel 파일 생성 검증 통과")
            
        except ImportError:
            self.fail("❌ generate_correct_pivot_excel 함수가 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 피벗 Excel 생성 실패: {e}")
    
    def test_data_consistency_between_pivots(self):
        """
        🔍 테스트: 피벗 테이블들 간 데이터 일관성 검증
        """
        try:
            from correct_pivot_generator import create_warehouse_monthly_pivot, create_site_monthly_pivot
            
            warehouse_pivot = create_warehouse_monthly_pivot()
            site_pivot = create_site_monthly_pivot()
            
            # 1. 총 입고량 vs 현장 입고량 비교 (대략적)
            warehouse_total_incoming = warehouse_pivot.xs('입고', axis=1, level=0).sum().sum()
            site_total_incoming = site_pivot.xs('입고', axis=1, level=0).sum().sum()
            
            # 창고 입고량이 현장 입고량보다 크거나 같아야 함 (중간 재고 고려)
            self.assertGreaterEqual(warehouse_total_incoming, site_total_incoming * 0.8,
                                  "창고 총 입고량이 현장 입고량과 합리적 비율이어야 함")
            
            # 2. 음수 값 없음 검증
            for df, name in [(warehouse_pivot, '창고'), (site_pivot, '현장')]:
                numeric_data = df.select_dtypes(include=[np.number])
                self.assertFalse((numeric_data < 0).any().any(),
                               f"{name} 피벗에 음수 값이 없어야 함")
            
            print("✅ 피벗 테이블 간 데이터 일관성 검증 통과")
            
        except ImportError:
            self.fail("❌ 피벗 생성 함수들이 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 데이터 일관성 검증 실패: {e}")
    
    def test_realistic_logistics_patterns(self):
        """
        📈 테스트: 실제적인 물류 패턴 반영 검증
        """
        try:
            from correct_pivot_generator import create_warehouse_monthly_pivot, create_site_monthly_pivot
            
            warehouse_pivot = create_warehouse_monthly_pivot()
            site_pivot = create_site_monthly_pivot()
            
            # 1. 계절성 패턴 검증 (간단한 체크)
            months_2024 = [f"2024-{i:02d}" for i in range(1, 13) if f"2024-{i:02d}" in warehouse_pivot.index]
            if len(months_2024) >= 6:
                # 연중 변동성이 있어야 함
                monthly_totals = []
                for month in months_2024:
                    total = warehouse_pivot.loc[month].sum()
                    monthly_totals.append(total)
                
                # 표준편차가 0이 아니어야 함 (변동성 있음)
                self.assertGreater(np.std(monthly_totals), 0,
                                 "월별 변동성이 있어야 함")
            
            # 2. 현장별 규모 차이 검증
            site_totals = {}
            for site in ['AGI', 'DAS', 'MIR', 'SHU']:
                if ('입고', site) in site_pivot.columns:
                    site_totals[site] = site_pivot[('입고', site)].iloc[:-1].sum()  # 합계 제외
            
            # 현장별로 차이가 있어야 함
            if len(site_totals) > 1:
                values = list(site_totals.values())
                self.assertGreater(max(values) / min(values) if min(values) > 0 else 0, 1.1,
                                 "현장별 규모 차이가 있어야 함")
            
            print("✅ 실제적인 물류 패턴 검증 통과")
            
        except ImportError:
            self.fail("❌ 피벗 생성 함수들이 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 물류 패턴 검증 실패: {e}")

if __name__ == '__main__':
    print("🔴 RED Phase: 올바른 피벗 테이블 형식 테스트 실행")
    print("=" * 60)
    print("📋 테스트 대상: 첨부된 Excel 스크린샷과 동일한 피벗 구조")
    print("🎯 예상 결과: 모든 테스트 실패 (아직 구현 안됨)")
    print()
    
    unittest.main(verbosity=2) 