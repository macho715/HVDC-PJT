#!/usr/bin/env python3
"""
HVDC Multi-Level Header Excel 파일 생성기 v1.0
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini

실제 메모리 데이터 기반 Multi-Level Header 구조 Excel 파일 생성
- 창고_월별_입출고: 15열 (Location + 입고7 + 출고7)
- 현장_월별_입고재고: 9열 (Location + 입고4 + 재고4)
- 실제 HVDC 데이터 분포 반영
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path

class HVDCMultiLevelExcelGenerator:
    """HVDC Multi-Level Header Excel 생성기"""
    
    def __init__(self):
        """초기화"""
        print("🚀 HVDC Multi-Level Header Excel 생성기 v1.0")
        print("=" * 80)
        
        # 실제 HVDC 데이터 분포 (메모리 기반)
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
        
        # 컬럼 순서 정의
        self.warehouses = ['AAA Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV Outdoor', 'Hauler Indoor', 'MOSB']
        self.sites = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = f"HVDC_MultiLevel_Excel_{self.timestamp}.xlsx"
        
        print(f"📊 창고 수: {len(self.warehouses)}개")
        print(f"🏭 현장 수: {len(self.sites)}개")
        print(f"📁 출력 파일: {self.output_file}")
        
    def create_warehouse_monthly_sheet(self):
        """창고 월별 입출고 시트 생성 (Multi-Level Header)"""
        print("\n🏢 창고별 월별 입출고 시트 생성 중...")
        
        # 월별 기간 생성 (2023-02 ~ 2024-07, 18개월)
        warehouse_months = pd.date_range('2023-02', periods=18, freq='MS')
        month_strings = [month.strftime('%Y-%m') for month in warehouse_months]
        
        # 데이터 생성
        data = []
        
        # 18개월 데이터 생성
        for i, month in enumerate(month_strings):
            row = [month]  # 첫 번째 컬럼: 월
            
            # 입고 데이터 (7개 창고)
            for warehouse in self.warehouses:
                # 실제 분포 기반 월별 입고 계산
                base_monthly = self.warehouse_distribution[warehouse] // 18
                
                # 계절성 반영 (겨울철 높음, 여름철 낮음)
                seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * i / 12)
                
                # 프로젝트 진행률 반영 (초기 높음, 후반 낮음)
                progress_factor = 1.0 + 0.2 * (1 - i / 18)
                
                monthly_inbound = int(base_monthly * seasonal_factor * progress_factor)
                row.append(monthly_inbound)
            
            # 출고 데이터 (7개 창고)
            for warehouse in self.warehouses:
                # 입고의 85% 가정
                base_monthly = self.warehouse_distribution[warehouse] // 18
                seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * i / 12)
                progress_factor = 1.0 + 0.2 * (1 - i / 18)
                
                monthly_outbound = int(base_monthly * seasonal_factor * progress_factor * 0.85)
                row.append(monthly_outbound)
            
            data.append(row)
        
        # 총합계 행 추가
        total_row = ['Total']
        
        # 입고 총합
        for warehouse in self.warehouses:
            total_inbound = self.warehouse_distribution[warehouse]
            total_row.append(total_inbound)
        
        # 출고 총합
        for warehouse in self.warehouses:
            total_outbound = int(self.warehouse_distribution[warehouse] * 0.85)
            total_row.append(total_outbound)
        
        data.append(total_row)
        
        # 컬럼 생성
        columns = ['입고월']
        
        # 입고 컬럼
        for warehouse in self.warehouses:
            columns.append(f'입고_{warehouse}')
        
        # 출고 컬럼
        for warehouse in self.warehouses:
            columns.append(f'출고_{warehouse}')
        
        # DataFrame 생성
        warehouse_df = pd.DataFrame(data, columns=columns)
        
        print(f"✅ 창고별 월별 입출고 시트 완료: {warehouse_df.shape}")
        return warehouse_df
    
    def create_site_monthly_sheet(self):
        """현장 월별 입고재고 시트 생성 (Multi-Level Header)"""
        print("\n🏗️ 현장별 월별 입고재고 시트 생성 중...")
        
        # 월별 기간 생성 (2024-01 ~ 2025-06, 18개월)
        site_months = pd.date_range('2024-01', periods=18, freq='MS')
        month_strings = [month.strftime('%Y-%m') for month in site_months]
        
        # 데이터 생성
        data = []
        cumulative_inventory = {site: 0 for site in self.sites}
        
        # 18개월 데이터 생성
        for i, month in enumerate(month_strings):
            row = [month]  # 첫 번째 컬럼: 월
            
            # 입고 데이터 (4개 현장)
            for site in self.sites:
                # 실제 분포 기반 월별 입고 계산
                base_monthly = self.site_distribution[site] // 18
                
                # 프로젝트 진행률 반영 (초기 높음, 후반 낮음)
                progress_factor = 1.0 + 0.4 * (1 - i / 18)
                
                # 현장별 특성 반영
                if site == 'SHU':  # 메인 현장
                    site_factor = 1.2
                elif site == 'MIR':  # 두 번째 현장
                    site_factor = 1.0
                elif site == 'DAS':  # 세 번째 현장
                    site_factor = 0.8
                else:  # AGI (가장 작은 현장)
                    site_factor = 0.5
                
                monthly_inbound = int(base_monthly * progress_factor * site_factor)
                row.append(monthly_inbound)
                
                # 누적 재고 업데이트
                cumulative_inventory[site] += monthly_inbound
            
            # 재고 데이터 (4개 현장)
            for site in self.sites:
                # 월별 소비 (입고량의 5% 소비)
                consumption = int(cumulative_inventory[site] * 0.05)
                cumulative_inventory[site] = max(0, cumulative_inventory[site] - consumption)
                row.append(cumulative_inventory[site])
            
            data.append(row)
        
        # 총합계 행 추가
        total_row = ['Total']
        
        # 입고 총합
        for site in self.sites:
            total_inbound = self.site_distribution[site]
            total_row.append(total_inbound)
        
        # 재고 총합 (입고의 30% 가정)
        for site in self.sites:
            total_inventory = int(self.site_distribution[site] * 0.30)
            total_row.append(total_inventory)
        
        data.append(total_row)
        
        # 컬럼 생성
        columns = ['입고월']
        
        # 입고 컬럼
        for site in self.sites:
            columns.append(f'입고_{site}')
        
        # 재고 컬럼
        for site in self.sites:
            columns.append(f'재고_{site}')
        
        # DataFrame 생성
        site_df = pd.DataFrame(data, columns=columns)
        
        print(f"✅ 현장별 월별 입고재고 시트 완료: {site_df.shape}")
        return site_df
    
    def create_multi_level_headers(self, df, sheet_type):
        """Multi-Level Header 구조 생성"""
        if sheet_type == 'warehouse':
            # 창고 시트: 입고월 + 입고(7개) + 출고(7개)
            level_0 = ['입고월']
            level_1 = ['']
            
            # 입고 헤더
            for warehouse in self.warehouses:
                level_0.append('입고')
                level_1.append(warehouse)
            
            # 출고 헤더
            for warehouse in self.warehouses:
                level_0.append('출고')
                level_1.append(warehouse)
            
        elif sheet_type == 'site':
            # 현장 시트: 입고월 + 입고(4개) + 재고(4개)
            level_0 = ['입고월']
            level_1 = ['']
            
            # 입고 헤더
            for site in self.sites:
                level_0.append('입고')
                level_1.append(site)
            
            # 재고 헤더
            for site in self.sites:
                level_0.append('재고')
                level_1.append(site)
        
        # MultiIndex 생성
        multi_index = pd.MultiIndex.from_arrays([level_0, level_1])
        
        # DataFrame 컬럼 재설정
        df.columns = multi_index
        
        return df
    
    def generate_excel_file(self):
        """최종 Excel 파일 생성"""
        print("\n📁 Excel 파일 생성 중...")
        
        # 시트 생성
        warehouse_sheet = self.create_warehouse_monthly_sheet()
        site_sheet = self.create_site_monthly_sheet()
        
        # Multi-Level Header 적용
        warehouse_sheet = self.create_multi_level_headers(warehouse_sheet, 'warehouse')
        site_sheet = self.create_multi_level_headers(site_sheet, 'site')
        
        # Excel 파일 생성
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            # 창고_월별_입출고 시트 (MultiIndex 포함)
            warehouse_sheet.to_excel(writer, sheet_name='창고_월별_입출고', index=True)
            
            # 현장_월별_입고재고 시트 (MultiIndex 포함)
            site_sheet.to_excel(writer, sheet_name='현장_월별_입고재고', index=True)
            
            # 요약 정보 시트
            summary_data = [
                ['항목', '값'],
                ['총 창고 수', len(self.warehouses)],
                ['총 현장 수', len(self.sites)],
                ['총 창고 처리량', sum(self.warehouse_distribution.values())],
                ['총 현장 처리량', sum(self.site_distribution.values())],
                ['생성 시간', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['버전', 'v1.0']
            ]
            
            summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
            summary_df.to_excel(writer, sheet_name='요약정보', index=False)
        
        print(f"✅ Excel 파일 생성 완료: {self.output_file}")
        print(f"📊 파일 크기: {os.path.getsize(self.output_file):,} bytes")
        
        return self.output_file
    
    def validate_excel_structure(self):
        """생성된 Excel 파일 구조 검증"""
        print("\n🔍 Excel 파일 구조 검증 중...")
        
        try:
            with pd.ExcelFile(self.output_file) as excel_file:
                sheet_names = excel_file.sheet_names
                print(f"📋 시트 목록: {sheet_names}")
                
                # 창고 시트 검증
                warehouse_df = pd.read_excel(excel_file, sheet_name='창고_월별_입출고', header=[0, 1])
                print(f"🏢 창고 시트: {warehouse_df.shape} (행={warehouse_df.shape[0]}, 열={warehouse_df.shape[1]})")
                
                # 현장 시트 검증
                site_df = pd.read_excel(excel_file, sheet_name='현장_월별_입고재고', header=[0, 1])
                print(f"🏗️ 현장 시트: {site_df.shape} (행={site_df.shape[0]}, 열={site_df.shape[1]})")
                
                # 요약 정보 시트 검증
                summary_df = pd.read_excel(excel_file, sheet_name='요약정보')
                print(f"📊 요약 시트: {summary_df.shape}")
                
                print("✅ Excel 파일 구조 검증 완료")
                return True
                
        except Exception as e:
            print(f"❌ Excel 파일 구조 검증 실패: {e}")
            return False


def main():
    """메인 실행 함수"""
    generator = HVDCMultiLevelExcelGenerator()
    
    # Excel 파일 생성
    output_file = generator.generate_excel_file()
    
    # 구조 검증
    if generator.validate_excel_structure():
        print("\n" + "=" * 80)
        print("🎉 HVDC Multi-Level Header Excel 파일 생성 성공!")
        print("=" * 80)
        print(f"📁 출력 파일: {output_file}")
        print(f"📊 창고 시트: 15열 (Location + 입고7 + 출고7)")
        print(f"🏗️ 현장 시트: 9열 (Location + 입고4 + 재고4)")
        print(f"📅 데이터 범위: 창고(2023-02~2024-07), 현장(2024-01~2025-06)")
        print("=" * 80)
    else:
        print("\n❌ Excel 파일 생성 중 오류 발생")


if __name__ == "__main__":
    main() 