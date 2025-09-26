#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
📋 MACHO-GPT TDD Test Suite: 첨부 이미지 정확한 수치 검증
첨부된 Excel 스크린샷의 실제 수치값과 100% 일치하는 테스트

🎯 테스트 대상:
- 창고별 입고 Total: DSV Outdoor=1300, DSV Indoor=1277, DSV Al Markaz=1069, MOSB=446
- 현장별 입고 합계: AGI=27, DAS=531, MIR=680, SHU=1165
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

class TestAccuratePivotValues(unittest.TestCase):
    """첨부된 이미지의 정확한 수치값과 일치하는 피벗 테이블 테스트"""
    
    def test_warehouse_total_values_should_match_image_exactly(self):
        """
        🏪 테스트: 창고별 입고 Total 값이 첨부 이미지와 정확히 일치해야 함
        
        Expected Values from Image 1:
        - DSV Outdoor: 1300
        - DSV Indoor: 1277  
        - DSV Al Markaz: 1069
        - MOSB: 446
        - DSV MZP: 14
        - Hauler Indoor: 392
        - AAA Storage: 0
        """
        try:
            from accurate_pivot_generator import create_accurate_warehouse_pivot
            pivot_df = create_accurate_warehouse_pivot()
            
            # Total 행 추출
            total_row = pivot_df.loc['Total']
            
            # 정확한 입고 수치 검증 (첨부 이미지 기준)
            expected_incoming_totals = {
                'DSV Outdoor': 1300,
                'DSV Indoor': 1277,
                'DSV Al Markaz': 1069,
                'MOSB': 446,
                'DSV MZP': 14,
                'Hauler Indoor': 392,
                'AAA Storage': 0
            }
            
            for warehouse, expected_value in expected_incoming_totals.items():
                actual_value = total_row[('입고', warehouse)]
                self.assertEqual(actual_value, expected_value,
                               f"창고 {warehouse} 입고 Total이 {expected_value}여야 함 (실제: {actual_value})")
            
            print("✅ 창고별 입고 Total 정확한 수치 검증 통과")
            
        except ImportError:
            self.fail("❌ create_accurate_warehouse_pivot 함수가 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 창고 피벗 테이블 정확한 수치 검증 실패: {e}")
    
    def test_warehouse_outgoing_values_should_be_realistic(self):
        """
        📦 테스트: 창고별 출고 Total 값이 실제적이어야 함 (입고보다 작거나 같음)
        """
        try:
            from accurate_pivot_generator import create_accurate_warehouse_pivot
            pivot_df = create_accurate_warehouse_pivot()
            
            total_row = pivot_df.loc['Total']
            
            # 각 창고별로 출고 <= 입고 검증
            warehouses = ['DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'MOSB', 
                         'DSV MZP', 'Hauler Indoor', 'AAA Storage']
            
            for warehouse in warehouses:
                incoming = total_row[('입고', warehouse)]
                outgoing = total_row[('출고', warehouse)]
                
                self.assertLessEqual(outgoing, incoming,
                                   f"창고 {warehouse} 출고({outgoing})가 입고({incoming})보다 작거나 같아야 함")
            
            print("✅ 창고별 출고 값 실제성 검증 통과")
            
        except ImportError:
            self.fail("❌ create_accurate_warehouse_pivot 함수가 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 창고 출고 값 검증 실패: {e}")
    
    def test_site_total_values_should_match_image_exactly(self):
        """
        🏗️ 테스트: 현장별 입고 합계 값이 첨부 이미지와 정확히 일치해야 함
        
        Expected Values from Image 2:
        - AGI: 27
        - DAS: 531
        - MIR: 680  
        - SHU: 1165
        """
        try:
            from accurate_pivot_generator import create_accurate_site_pivot
            pivot_df = create_accurate_site_pivot()
            
            # 합계 행 추출
            total_row = pivot_df.loc['합계']
            
            # 정확한 입고 수치 검증 (첨부 이미지 기준)
            expected_incoming_totals = {
                'AGI': 27,
                'DAS': 531,
                'MIR': 680,
                'SHU': 1165
            }
            
            for site, expected_value in expected_incoming_totals.items():
                actual_value = total_row[('입고', site)]
                self.assertEqual(actual_value, expected_value,
                               f"현장 {site} 입고 합계가 {expected_value}여야 함 (실제: {actual_value})")
            
            print("✅ 현장별 입고 합계 정확한 수치 검증 통과")
            
        except ImportError:
            self.fail("❌ create_accurate_site_pivot 함수가 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 현장 피벗 테이블 정확한 수치 검증 실패: {e}")
    
    def test_site_inventory_values_should_be_cumulative(self):
        """
        📊 테스트: 현장별 재고 값이 누적 특성을 가져야 함 (입고 기반)
        """
        try:
            from accurate_pivot_generator import create_accurate_site_pivot
            pivot_df = create_accurate_site_pivot()
            
            # 각 현장별로 재고가 입고와 합리적 관계인지 확인
            sites = ['AGI', 'DAS', 'MIR', 'SHU']
            
            for site in sites:
                # 월별 입고 합계 vs 최종 재고
                monthly_incoming = pivot_df[('입고', site)].iloc[:-1].sum()  # 합계 제외
                final_inventory = pivot_df.loc['합계', ('재고', site)]
                
                # 재고는 월별 입고의 일정 비율 이하여야 함 (출고 고려)
                self.assertLessEqual(final_inventory, monthly_incoming * 1.2,
                                   f"현장 {site} 최종 재고가 입고 총량 대비 합리적이어야 함")
                
                # 재고는 0 이상이어야 함
                self.assertGreaterEqual(final_inventory, 0,
                                      f"현장 {site} 재고가 0 이상이어야 함")
            
            print("✅ 현장별 재고 누적 특성 검증 통과")
            
        except ImportError:
            self.fail("❌ create_accurate_site_pivot 함수가 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 현장 재고 누적 특성 검증 실패: {e}")
    
    def test_monthly_distribution_should_be_realistic(self):
        """
        📅 테스트: 월별 분포가 실제적이어야 함 (첨부 이미지 패턴 반영)
        """
        try:
            from accurate_pivot_generator import create_accurate_warehouse_pivot, create_accurate_site_pivot
            
            warehouse_pivot = create_accurate_warehouse_pivot()
            site_pivot = create_accurate_site_pivot()
            
            # 창고별 월별 변동성 확인
            warehouse_monthly_totals = []
            for month in warehouse_pivot.index[:-1]:  # Total 제외
                month_total = warehouse_pivot.loc[month, ('입고', slice(None))].sum()
                warehouse_monthly_totals.append(month_total)
            
            # 변동성이 있어야 함 (모든 월이 같지 않음)
            self.assertGreater(np.std(warehouse_monthly_totals), 0,
                             "창고별 월별 입고에 변동성이 있어야 함")
            
            # 현장별 프로젝트 진행 패턴 확인 (AGI는 나중에 시작)
            agi_early_months = site_pivot[('입고', 'AGI')].iloc[:12].sum()  # 첫 12개월
            agi_later_months = site_pivot[('입고', 'AGI')].iloc[12:-1].sum()  # 나머지 월 (합계 제외)
            
            # AGI는 나중에 더 활발해야 함
            if agi_later_months > 0:
                self.assertLessEqual(agi_early_months, agi_later_months,
                                   "AGI는 후반기에 더 활발해야 함")
            
            print("✅ 월별 분포 실제성 검증 통과")
            
        except ImportError:
            self.fail("❌ accurate_pivot_generator 함수들이 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 월별 분포 검증 실패: {e}")
    
    def test_accurate_excel_generation_with_correct_values(self):
        """
        📊 테스트: 정확한 수치로 Excel 파일 생성되어야 함
        """
        try:
            from accurate_pivot_generator import generate_accurate_pivot_excel
            excel_path = generate_accurate_pivot_excel()
            
            # 파일 존재 검증
            self.assertTrue(os.path.exists(excel_path),
                          f"정확한 수치 Excel 파일 {excel_path}이 생성되어야 함")
            
            # Excel 파일에서 수치 재검증
            warehouse_df = pd.read_excel(excel_path, sheet_name='창고별_월별_입출고', 
                                       header=[0,1], index_col=0)
            site_df = pd.read_excel(excel_path, sheet_name='현장별_월별_입고재고',
                                  header=[0,1], index_col=0)
            
            # 핵심 수치 재확인
            self.assertEqual(warehouse_df.loc['Total', ('입고', 'DSV Outdoor')], 1300,
                           "Excel에서 DSV Outdoor 입고 Total이 1300이어야 함")
            self.assertEqual(site_df.loc['합계', ('입고', 'DAS')], 531,
                           "Excel에서 DAS 입고 합계가 531이어야 함")
            
            print("✅ 정확한 수치 Excel 생성 검증 통과")
            
        except ImportError:
            self.fail("❌ generate_accurate_pivot_excel 함수가 구현되지 않음")
        except Exception as e:
            self.fail(f"❌ 정확한 수치 Excel 생성 실패: {e}")

if __name__ == '__main__':
    print("🔴 RED Phase: 첨부 이미지 정확한 수치 검증 테스트 실행")
    print("=" * 65)
    print("📋 테스트 대상: 첨부된 Excel 스크린샷의 실제 수치값과 100% 일치")
    print("🎯 예상 결과: 모든 테스트 실패 (정확한 수치 미구현)")
    print()
    print("📊 검증할 정확한 수치:")
    print("  창고 입고 Total: DSV Outdoor=1300, DSV Indoor=1277, DSV Al Markaz=1069")
    print("  현장 입고 합계: AGI=27, DAS=531, MIR=680, SHU=1165")
    print()
    
    unittest.main(verbosity=2) 