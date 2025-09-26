#!/usr/bin/env python3
"""
창고_현장_월별_시트_구조.md 기반 Excel 파일 생성기

목적: 창고_현장_월별_시트_구조.md 문서에 기술된 정확한 구조의 Excel 파일 생성
- 시트 1: 창고_월별_입출고 (2023-02 ~ 2025-06, 7개 창고, Multi-level 헤더)
- 시트 2: 현장_월별_입고재고 (2024-01 ~ 2025-06, 4개 현장, Multi-level 헤더)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class WarehouseSiteMonthlyExcelGenerator:
    """창고_현장_월별_시트_구조.md 기반 Excel 생성기"""
    
    def __init__(self):
        """Excel 생성기 초기화"""
        self.warehouse_cols = [
            'AAA Storage', 'DSV Indoor', 'DSV Outdoor', 
            'DSV Al Markaz', 'DSV MZP', 'Hauler Indoor', 'MOSB'
        ]
        
        self.site_cols = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 창고 월별 기간: 2023-02 ~ 2025-06
        self.warehouse_months = pd.date_range('2023-02', '2025-06', freq='MS')
        
        # 현장 월별 기간: 2024-01 ~ 2025-06  
        self.site_months = pd.date_range('2024-01', '2025-06', freq='MS')
        
        # 현장별 특성 (문서에서 언급된 비율 반영)
        self.site_ratios = {
            'AGI': 0.02,   # 2% (초기 단계)
            'DAS': 0.35,   # 35% (주요 현장) 
            'MIR': 0.38,   # 38% (최대 현장)
            'SHU': 0.25    # 25% (보조 현장)
        }
        
        # 현장별 시작 시기
        self.site_start_months = {
            'AGI': '2025-04',  # AGI는 2025년 4월부터 본격 시작
            'DAS': '2024-02',  # DAS는 2024년 2월부터 활발
            'MIR': '2024-01',  # MIR은 첫 달부터 시작
            'SHU': '2024-01'   # SHU도 초기부터 활발
        }
    
    def create_warehouse_monthly_sheet(self):
        """창고_월별_입출고 시트 생성"""
        print("📊 창고_월별_입출고 시트 생성 중...")
        
        # 월별 인덱스 생성
        month_labels = [month.strftime('%Y-%m') for month in self.warehouse_months]
        
        # Multi-level 컬럼 생성
        # 상위 헤더: 입고 (7개) + 출고 (7개) = 14개
        level_0 = ['입고'] * len(self.warehouse_cols) + ['출고'] * len(self.warehouse_cols)
        level_1 = self.warehouse_cols + self.warehouse_cols
        
        multi_columns = pd.MultiIndex.from_arrays([level_0, level_1], names=['구분', 'Location'])
        
        # 데이터프레임 초기화
        warehouse_data = pd.DataFrame(
            index=month_labels + ['Total'],
            columns=multi_columns
        )
        
        # 실제 데이터 생성 (문서의 설명에 따른 현실적인 패턴)
        base_monthly_volume = 800  # 월별 기본 물량
        
        for i, month in enumerate(month_labels):
            year = int(month.split('-')[0])
            month_num = int(month.split('-')[1])
            
            # 계절성 반영 (여름철 증가, 겨울철 감소)
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * (month_num - 3) / 12)
            
            # 프로젝트 진행률 반영 (2024년이 피크)
            if year == 2023:
                progress_factor = 0.3 + 0.4 * (month_num / 12)
            elif year == 2024:
                progress_factor = 0.8 + 0.2 * np.sin(np.pi * month_num / 6)
            else:  # 2025
                progress_factor = 0.9 - 0.3 * (month_num / 12)
            
            monthly_total = int(base_monthly_volume * seasonal_factor * progress_factor)
            
            # 창고별 입고 데이터 생성
            for warehouse in self.warehouse_cols:
                # 창고별 특성 반영
                if warehouse == 'DSV Indoor':
                    warehouse_ratio = 0.25
                elif warehouse == 'DSV Outdoor':
                    warehouse_ratio = 0.20
                elif warehouse == 'DSV Al Markaz':
                    warehouse_ratio = 0.18
                elif warehouse == 'MOSB':
                    warehouse_ratio = 0.15
                elif warehouse == 'Hauler Indoor':
                    warehouse_ratio = 0.12
                elif warehouse == 'DSV MZP':
                    warehouse_ratio = 0.07
                else:  # AAA Storage
                    warehouse_ratio = 0.03
                
                # 입고량 계산
                incoming = int(monthly_total * warehouse_ratio * np.random.uniform(0.8, 1.2))
                warehouse_data.loc[month, ('입고', warehouse)] = incoming
                
                # 출고량 계산 (입고량의 85-95%)
                outgoing = int(incoming * np.random.uniform(0.85, 0.95))
                warehouse_data.loc[month, ('출고', warehouse)] = outgoing
        
        # Total 행 계산
        for warehouse in self.warehouse_cols:
            warehouse_data.loc['Total', ('입고', warehouse)] = warehouse_data.loc[month_labels, ('입고', warehouse)].astype(int).sum()
            warehouse_data.loc['Total', ('출고', warehouse)] = warehouse_data.loc[month_labels, ('출고', warehouse)].astype(int).sum()
        
        # 데이터타입 정수로 변환
        warehouse_data = warehouse_data.fillna(0).astype(int)
        
        print(f"✅ 창고_월별_입출고 시트 완성: {len(month_labels)}개월 + Total, {len(self.warehouse_cols)}개 창고")
        return warehouse_data
    
    def create_site_monthly_sheet(self):
        """현장_월별_입고재고 시트 생성"""
        print("📊 현장_월별_입고재고 시트 생성 중...")
        
        # 월별 인덱스 생성
        month_labels = [month.strftime('%Y-%m') for month in self.site_months]
        
        # Multi-level 컬럼 생성
        # 상위 헤더: 입고 (4개) + 재고 (4개) = 8개
        level_0 = ['입고'] * len(self.site_cols) + ['재고'] * len(self.site_cols)
        level_1 = self.site_cols + self.site_cols
        
        multi_columns = pd.MultiIndex.from_arrays([level_0, level_1], names=['구분', 'Location'])
        
        # 데이터프레임 초기화
        site_data = pd.DataFrame(
            index=month_labels + ['합계'],
            columns=multi_columns
        )
        
        # 현장별 누적 재고 추적
        cumulative_inventory = {site: 0 for site in self.site_cols}
        
        # 실제 데이터 생성
        base_monthly_volume = 600  # 현장 월별 기본 물량
        
        for i, month in enumerate(month_labels):
            year = int(month.split('-')[0])
            month_num = int(month.split('-')[1])
            
            # 프로젝트 단계별 물량 조정
            if year == 2024 and month_num <= 6:
                stage_factor = 0.6 + 0.4 * (month_num / 6)  # 초기 단계
            elif year == 2024 and month_num > 6:
                stage_factor = 1.0 + 0.3 * ((month_num - 6) / 6)  # 본격 단계
            else:  # 2025
                stage_factor = 1.2 - 0.2 * (month_num / 12)  # 완료 단계
            
            monthly_total = int(base_monthly_volume * stage_factor)
            
            # 현장별 입고 및 재고 계산
            for site in self.site_cols:
                # 현장 시작 시기 확인
                if month < self.site_start_months[site]:
                    incoming = 0
                else:
                    # 현장별 비율 적용
                    site_ratio = self.site_ratios[site]
                    
                    # 현장별 특성 반영
                    if site == 'AGI' and month >= '2025-04':
                        # AGI는 2025년 4월부터 본격 시작
                        incoming = int(monthly_total * site_ratio * 3.0 * np.random.uniform(0.8, 1.2))
                    elif site == 'DAS':
                        # DAS는 지속적으로 활발
                        incoming = int(monthly_total * site_ratio * np.random.uniform(1.0, 1.3))
                    elif site == 'MIR':
                        # MIR은 최대 물량 처리
                        incoming = int(monthly_total * site_ratio * np.random.uniform(1.1, 1.4))
                    elif site == 'SHU':
                        # SHU는 안정적인 물량
                        incoming = int(monthly_total * site_ratio * np.random.uniform(0.9, 1.1))
                    else:
                        incoming = int(monthly_total * site_ratio)
                
                # 입고 데이터 설정
                site_data.loc[month, ('입고', site)] = incoming
                
                # 재고 계산 (누적 방식)
                cumulative_inventory[site] += incoming
                
                # 일부 출고 반영 (재고의 10-30%)
                if cumulative_inventory[site] > 0:
                    outgoing_rate = np.random.uniform(0.1, 0.3)
                    outgoing = int(cumulative_inventory[site] * outgoing_rate)
                    cumulative_inventory[site] = max(0, cumulative_inventory[site] - outgoing)
                
                site_data.loc[month, ('재고', site)] = cumulative_inventory[site]
        
        # 합계 행 계산
        for site in self.site_cols:
            site_data.loc['합계', ('입고', site)] = site_data.loc[month_labels, ('입고', site)].astype(int).sum()
            site_data.loc['합계', ('재고', site)] = site_data.loc[month_labels[-1], ('재고', site)]  # 마지막 월 재고
        
        # 데이터타입 정수로 변환
        site_data = site_data.fillna(0).astype(int)
        
        print(f"✅ 현장_월별_입고재고 시트 완성: {len(month_labels)}개월 + 합계, {len(self.site_cols)}개 현장")
        return site_data
    
    def generate_excel_file(self):
        """최종 Excel 파일 생성"""
        print("🎯 창고_현장_월별_시트_구조.xlsx 생성 시작")
        print("=" * 60)
        
        # 두 시트 생성
        warehouse_sheet = self.create_warehouse_monthly_sheet()
        site_sheet = self.create_site_monthly_sheet()
        
        # Excel 파일 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'창고_현장_월별_시트_구조_{timestamp}.xlsx'
        
        print("\n📁 Excel 파일 저장 중...")
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # 시트 1: 창고_월별_입출고
            warehouse_sheet.to_excel(
                writer, 
                sheet_name='창고_월별_입출고',
                merge_cells=True
            )
            
            # 시트 2: 현장_월별_입고재고
            site_sheet.to_excel(
                writer, 
                sheet_name='현장_월별_입고재고',
                merge_cells=True
            )
            
            # 워크북 및 워크시트 객체 가져오기
            workbook = writer.book
            
            # 시트 1 포맷팅
            worksheet1 = writer.sheets['창고_월별_입출고']
            
            # 헤더 포맷
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'vcenter',
                'align': 'center',
                'bg_color': '#D7E4BC',
                'border': 1
            })
            
            # 데이터 포맷
            data_format = workbook.add_format({
                'align': 'center',
                'border': 1,
                'num_format': '#,##0'
            })
            
            # Total/합계 행 포맷
            total_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'border': 1,
                'bg_color': '#FFF2CC',
                'num_format': '#,##0'
            })
            
            # 컬럼 너비 조정
            worksheet1.set_column('A:A', 12)  # Location 컬럼
            worksheet1.set_column('B:O', 10)  # 데이터 컬럼들
            
            # 시트 2 포맷팅
            worksheet2 = writer.sheets['현장_월별_입고재고']
            worksheet2.set_column('A:A', 12)  # Location 컬럼  
            worksheet2.set_column('B:I', 10)  # 데이터 컬럼들
        
        print(f"✅ Excel 파일 생성 완료: {output_file}")
        print(f"📊 파일 크기: {os.path.getsize(output_file) / 1024:.1f} KB")
        
        # 생성된 파일 정보 출력
        print("\n📋 생성된 시트 정보:")
        print(f"   시트 1: 창고_월별_입출고")
        print(f"   - 기간: 2023-02 ~ 2025-06 ({len(self.warehouse_months)}개월)")
        print(f"   - 창고: {len(self.warehouse_cols)}개 ({', '.join(self.warehouse_cols)})")
        print(f"   - 구조: Multi-level 헤더 (입고/출고 × 창고명)")
        
        print(f"   시트 2: 현장_월별_입고재고")
        print(f"   - 기간: 2024-01 ~ 2025-06 ({len(self.site_months)}개월)")
        print(f"   - 현장: {len(self.site_cols)}개 ({', '.join(self.site_cols)})")
        print(f"   - 구조: Multi-level 헤더 (입고/재고 × 현장명)")
        
        return output_file
    
    def validate_structure(self, excel_file):
        """생성된 Excel 파일 구조 검증"""
        print(f"\n🔍 Excel 파일 구조 검증: {excel_file}")
        
        try:
            # 시트 1 검증
            df1 = pd.read_excel(excel_file, sheet_name='창고_월별_입출고', header=[0, 1], index_col=0)
            print(f"✅ 시트 1 검증 성공: {df1.shape[0]}행 × {df1.shape[1]}열")
            print(f"   - Multi-level 컬럼: {df1.columns.nlevels}레벨")
            print(f"   - 상위 헤더: {list(df1.columns.get_level_values(0).unique())}")
            
            # 시트 2 검증
            df2 = pd.read_excel(excel_file, sheet_name='현장_월별_입고재고', header=[0, 1], index_col=0)
            print(f"✅ 시트 2 검증 성공: {df2.shape[0]}행 × {df2.shape[1]}열")
            print(f"   - Multi-level 컬럼: {df2.columns.nlevels}레벨")
            print(f"   - 상위 헤더: {list(df2.columns.get_level_values(0).unique())}")
            
            return True
            
        except Exception as e:
            print(f"❌ 구조 검증 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    print("🏭 창고_현장_월별_시트_구조.md 기반 Excel 생성기 v1.0")
    print("📝 문서 기반 정확한 Multi-level 헤더 구조 구현")
    print("=" * 60)
    
    # Excel 생성기 초기화
    generator = WarehouseSiteMonthlyExcelGenerator()
    
    # Excel 파일 생성
    output_file = generator.generate_excel_file()
    
    # 구조 검증
    if generator.validate_structure(output_file):
        print("\n🎉 창고_현장_월별_시트_구조.xlsx 생성 완료!")
        print(f"📂 저장 위치: {os.path.abspath(output_file)}")
    else:
        print("\n⚠️  파일 생성은 완료되었으나 구조 검증에서 문제가 발견되었습니다.")
    
    print("\n" + "=" * 60)
    print("💡 사용법:")
    print("   1. Excel에서 파일을 열어 Multi-level 헤더 구조 확인")
    print("   2. 데이터는 실제 프로젝트 패턴을 반영하여 생성됨")
    print("   3. Power Pivot 연동 시 추가 커스터마이징 가능")

if __name__ == '__main__':
    main() 