#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC 프로젝트 종합 피벗 테이블 분석
- 월별 출고 피벗
- 현장 입고 피벗  
- 직배송/이동 경로 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
from collections import defaultdict

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class CompletePivotAnalyzer:
    """종합 피벗 테이블 분석 클래스"""
    
    def __init__(self):
        self.data_file = project_root / "correct_hvdc_analysis_20250712_182510.xlsx"
        self.df = None
        self.analysis_results = {}
        
        # 창고 및 현장 컬럼 정의
        self.warehouse_columns = [
            'DHL Warehouse', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
            'AAA  Storage', 'Hauler Indoor', 'DSV MZP'
        ]
        
        self.site_columns = ['MOSB', 'MIR', 'SHU', 'DAS', 'AGI']
        
    def load_existing_data(self):
        """기존 분석 데이터 로드"""
        print("📊 기존 분석 데이터 로드 중...")
        
        try:
            # 각 시트별로 데이터 로드
            self.df = {}
            self.df['inbound_detail'] = pd.read_excel(self.data_file, sheet_name='입고상세')
            self.df['outbound_detail'] = pd.read_excel(self.data_file, sheet_name='출고상세')
            self.df['original_data'] = pd.read_excel(self.data_file, sheet_name='원본데이터')
            
            print("✅ 데이터 로드 완료")
            print(f"  - 입고상세: {len(self.df['inbound_detail']):,}건")
            print(f"  - 출고상세: {len(self.df['outbound_detail']):,}건")
            print(f"  - 원본데이터: {len(self.df['original_data']):,}건")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def create_monthly_outbound_pivot(self):
        """월별 출고 피벗 테이블 생성"""
        print("\n📤 월별 출고 피벗 테이블 생성 중...")
        
        outbound_df = self.df['outbound_detail'].copy()
        
        # 출고 날짜를 월별로 변환
        outbound_df['Outbound_Month'] = pd.to_datetime(outbound_df['Outbound_Date']).dt.to_period('M')
        
        # 1. 창고별 월별 출고 피벗
        warehouse_outbound_pivot = outbound_df.pivot_table(
            index='Outbound_Month',
            columns='From_Warehouse',
            values='PKG_Quantity',
            aggfunc='sum',
            fill_value=0
        ).astype(int)
        
        # 2. 현장별 월별 출고 피벗
        site_outbound_pivot = outbound_df.pivot_table(
            index='Outbound_Month',
            columns='To_Site',
            values='PKG_Quantity',
            aggfunc='sum',
            fill_value=0
        ).astype(int)
        
        # 3. 창고→현장 매트릭스 피벗
        warehouse_site_pivot = outbound_df.pivot_table(
            index='From_Warehouse',
            columns='To_Site',
            values='PKG_Quantity',
            aggfunc='sum',
            fill_value=0
        ).astype(int)
        
        result = {
            'warehouse_monthly': warehouse_outbound_pivot,
            'site_monthly': site_outbound_pivot,
            'warehouse_site_matrix': warehouse_site_pivot
        }
        
        print("✅ 월별 출고 피벗 생성 완료")
        print(f"  - 창고별 월별 출고: {warehouse_outbound_pivot.shape}")
        print(f"  - 현장별 월별 출고: {site_outbound_pivot.shape}")
        print(f"  - 창고→현장 매트릭스: {warehouse_site_pivot.shape}")
        
        return result
    
    def create_site_inbound_pivot(self):
        """현장 입고 피벗 테이블 생성"""
        print("\n🏗️  현장 입고 피벗 테이블 생성 중...")
        
        # 원본 데이터에서 현장 입고 정보 추출
        original_df = self.df['original_data'].copy()
        
        site_inbound_data = []
        
        for idx, row in original_df.iterrows():
            for site in self.site_columns:
                if site in row.index and pd.notna(row[site]):
                    try:
                        site_date = pd.to_datetime(row[site], errors='coerce')
                        if pd.notna(site_date):
                            # PKG 수량 추출
                            pkg_quantity = self._get_pkg_quantity(row)
                            
                            site_inbound_data.append({
                                'Item_ID': idx,
                                'Site': site,
                                'Site_Date': site_date,
                                'Year_Month': site_date.strftime('%Y-%m'),
                                'PKG_Quantity': pkg_quantity
                            })
                    except Exception as e:
                        continue
        
        if not site_inbound_data:
            print("⚠️  현장 입고 데이터가 없음")
            return None
        
        site_inbound_df = pd.DataFrame(site_inbound_data)
        
        # 1. 현장별 월별 입고 피벗
        site_monthly_pivot = site_inbound_df.pivot_table(
            index='Year_Month',
            columns='Site',
            values='PKG_Quantity',
            aggfunc='sum',
            fill_value=0
        ).astype(int)
        
        # 2. 현장별 총 입고 집계
        site_total_pivot = site_inbound_df.groupby('Site')['PKG_Quantity'].sum().to_frame('Total_Inbound')
        
        result = {
            'site_monthly': site_monthly_pivot,
            'site_total': site_total_pivot,
            'site_inbound_data': site_inbound_df
        }
        
        print("✅ 현장 입고 피벗 생성 완료")
        print(f"  - 현장별 월별 입고: {site_monthly_pivot.shape}")
        print(f"  - 현장별 총 입고: {len(site_total_pivot)}개 현장")
        
        return result
    
    def analyze_direct_delivery_and_transfer(self):
        """직배송 및 창고 간 이동 경로 분석"""
        print("\n🚚 직배송 및 이동 경로 분석 중...")
        
        original_df = self.df['original_data'].copy()
        
        # 1. 직배송 분석 (창고를 거치지 않고 바로 현장으로)
        direct_delivery_data = []
        
        for idx, row in original_df.iterrows():
            # Status_Location이 현장인 항목들
            if 'Status_Location' in row.index and pd.notna(row['Status_Location']):
                status_location = str(row['Status_Location']).strip()
                
                # 현장에 있는 항목
                if any(site.lower() in status_location.lower() for site in self.site_columns):
                    # 모든 창고 컬럼에 날짜가 없는지 확인
                    has_warehouse_date = False
                    for warehouse in self.warehouse_columns:
                        if warehouse in row.index and pd.notna(row[warehouse]):
                            has_warehouse_date = True
                            break
                    
                    # 창고를 거치지 않고 바로 현장으로 간 경우
                    if not has_warehouse_date:
                        # 현장 도착 날짜 찾기
                        site_date = None
                        for site in self.site_columns:
                            if site in row.index and pd.notna(row[site]):
                                site_date = pd.to_datetime(row[site], errors='coerce')
                                if pd.notna(site_date):
                                    break
                        
                        if site_date:
                            pkg_quantity = self._get_pkg_quantity(row)
                            
                            direct_delivery_data.append({
                                'Item_ID': idx,
                                'Site': status_location,
                                'Date': site_date,
                                'Year_Month': site_date.strftime('%Y-%m'),
                                'PKG_Quantity': pkg_quantity,
                                'Type': 'Direct_Delivery'
                            })
        
        # 2. 창고 간 이동 분석
        warehouse_transfer_data = []
        
        for idx, row in original_df.iterrows():
            warehouse_dates = []
            
            # 각 창고별 방문 날짜 수집
            for warehouse in self.warehouse_columns:
                if warehouse in row.index and pd.notna(row[warehouse]):
                    warehouse_date = pd.to_datetime(row[warehouse], errors='coerce')
                    if pd.notna(warehouse_date):
                        warehouse_dates.append((warehouse, warehouse_date))
            
            # 2개 이상 창고를 방문한 경우 이동 경로 분석
            if len(warehouse_dates) >= 2:
                warehouse_dates.sort(key=lambda x: x[1])  # 날짜순 정렬
                
                for i in range(len(warehouse_dates) - 1):
                    from_warehouse, from_date = warehouse_dates[i]
                    to_warehouse, to_date = warehouse_dates[i + 1]
                    
                    pkg_quantity = self._get_pkg_quantity(row)
                    
                    warehouse_transfer_data.append({
                        'Item_ID': idx,
                        'From_Warehouse': from_warehouse,
                        'To_Warehouse': to_warehouse,
                        'Transfer_Date': to_date,
                        'Year_Month': to_date.strftime('%Y-%m'),
                        'PKG_Quantity': pkg_quantity,
                        'Type': 'Warehouse_Transfer'
                    })
        
        # 3. 피벗 테이블 생성
        if direct_delivery_data:
            direct_df = pd.DataFrame(direct_delivery_data)
            direct_monthly_pivot = direct_df.pivot_table(
                index='Year_Month',
                columns='Site',
                values='PKG_Quantity',
                aggfunc='sum',
                fill_value=0
            ).astype(int)
        else:
            direct_monthly_pivot = pd.DataFrame()
        
        if warehouse_transfer_data:
            transfer_df = pd.DataFrame(warehouse_transfer_data)
            transfer_monthly_pivot = transfer_df.pivot_table(
                index='Year_Month',
                columns='From_Warehouse',
                values='PKG_Quantity',
                aggfunc='sum',
                fill_value=0
            ).astype(int)
            
            transfer_matrix_pivot = transfer_df.pivot_table(
                index='From_Warehouse',
                columns='To_Warehouse',
                values='PKG_Quantity',
                aggfunc='sum',
                fill_value=0
            ).astype(int)
        else:
            transfer_monthly_pivot = pd.DataFrame()
            transfer_matrix_pivot = pd.DataFrame()
        
        result = {
            'direct_delivery_monthly': direct_monthly_pivot,
            'warehouse_transfer_monthly': transfer_monthly_pivot,
            'warehouse_transfer_matrix': transfer_matrix_pivot,
            'direct_delivery_data': direct_delivery_data,
            'warehouse_transfer_data': warehouse_transfer_data
        }
        
        print("✅ 직배송 및 이동 경로 분석 완료")
        print(f"  - 직배송: {len(direct_delivery_data):,}건")
        print(f"  - 창고 간 이동: {len(warehouse_transfer_data):,}건")
        
        return result
    
    def _get_pkg_quantity(self, row):
        """PKG 수량 안전 추출"""
        pkg_columns = ['Pkg', 'PKG', 'Quantity', 'Qty', 'Amount']
        
        for col in pkg_columns:
            if col in row.index and pd.notna(row[col]):
                try:
                    pkg_value = row[col]
                    if isinstance(pkg_value, (int, float)) and pkg_value > 0:
                        return int(pkg_value)
                    elif isinstance(pkg_value, str):
                        import re
                        numbers = re.findall(r'\d+', pkg_value)
                        if numbers:
                            return int(numbers[0])
                except:
                    continue
        
        return 1
    
    def run_complete_analysis(self):
        """종합 피벗 테이블 분석 실행"""
        print("🚀 HVDC 종합 피벗 테이블 분석 시작")
        print("="*60)
        
        # 1. 데이터 로드
        if not self.load_existing_data():
            return False
        
        # 2. 각종 피벗 테이블 생성
        self.analysis_results['outbound_pivot'] = self.create_monthly_outbound_pivot()
        self.analysis_results['site_inbound_pivot'] = self.create_site_inbound_pivot()
        self.analysis_results['delivery_transfer'] = self.analyze_direct_delivery_and_transfer()
        
        # 3. 결과 출력
        self.print_complete_summary()
        
        # 4. 결과 내보내기
        output_file = self.export_complete_results()
        
        if output_file:
            print(f"\n✅ 종합 분석 완료! 결과 파일: {output_file}")
        else:
            print("\n⚠️  결과 내보내기 실패")
        
        return True
    
    def print_complete_summary(self):
        """종합 분석 결과 요약 출력"""
        print("\n" + "="*60)
        print("📋 HVDC 종합 피벗 테이블 분석 결과 요약")
        print("="*60)
        
        # 출고 피벗 요약
        if 'outbound_pivot' in self.analysis_results:
            outbound = self.analysis_results['outbound_pivot']
            print(f"\n📤 월별 출고 피벗:")
            print(f"  - 창고별 월별 출고: {outbound['warehouse_monthly'].shape}")
            print(f"  - 현장별 월별 출고: {outbound['site_monthly'].shape}")
            print(f"  - 창고→현장 매트릭스: {outbound['warehouse_site_matrix'].shape}")
        
        # 현장 입고 피벗 요약
        if 'site_inbound_pivot' in self.analysis_results:
            site_inbound = self.analysis_results['site_inbound_pivot']
            if site_inbound:
                print(f"\n🏗️  현장 입고 피벗:")
                print(f"  - 현장별 월별 입고: {site_inbound['site_monthly'].shape}")
                print(f"  - 현장별 총 입고: {len(site_inbound['site_total'])}개 현장")
        
        # 직배송/이동 경로 요약
        if 'delivery_transfer' in self.analysis_results:
            delivery = self.analysis_results['delivery_transfer']
            print(f"\n🚚 직배송 및 이동 경로:")
            print(f"  - 직배송: {len(delivery['direct_delivery_data']):,}건")
            print(f"  - 창고 간 이동: {len(delivery['warehouse_transfer_data']):,}건")
        
        print("\n" + "="*60)
    
    def export_complete_results(self):
        """종합 분석 결과 내보내기"""
        print("\n💾 종합 분석 결과 내보내기 중...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = project_root / f"complete_pivot_analysis_{timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 1. 월별 출고 피벗
                if 'outbound_pivot' in self.analysis_results:
                    outbound = self.analysis_results['outbound_pivot']
                    outbound['warehouse_monthly'].to_excel(writer, sheet_name='월별창고출고피벗')
                    outbound['site_monthly'].to_excel(writer, sheet_name='월별현장출고피벗')
                    outbound['warehouse_site_matrix'].to_excel(writer, sheet_name='창고현장출고매트릭스')
                
                # 2. 현장 입고 피벗
                if 'site_inbound_pivot' in self.analysis_results and self.analysis_results['site_inbound_pivot']:
                    site_inbound = self.analysis_results['site_inbound_pivot']
                    site_inbound['site_monthly'].to_excel(writer, sheet_name='월별현장입고피벗')
                    site_inbound['site_total'].to_excel(writer, sheet_name='현장별총입고')
                    site_inbound['site_inbound_data'].to_excel(writer, sheet_name='현장입고상세', index=False)
                
                # 3. 직배송 및 이동 경로
                if 'delivery_transfer' in self.analysis_results:
                    delivery = self.analysis_results['delivery_transfer']
                    
                    if 'direct_monthly_pivot' in delivery and not delivery['direct_monthly_pivot'].empty:
                        delivery['direct_monthly_pivot'].to_excel(writer, sheet_name='월별직배송피벗')
                    
                    if 'warehouse_transfer_monthly' in delivery and not delivery['warehouse_transfer_monthly'].empty:
                        delivery['warehouse_transfer_monthly'].to_excel(writer, sheet_name='월별창고이동피벗')
                        delivery['warehouse_transfer_matrix'].to_excel(writer, sheet_name='창고이동매트릭스')
                    
                    # 상세 데이터
                    if delivery['direct_delivery_data']:
                        direct_df = pd.DataFrame(delivery['direct_delivery_data'])
                        direct_df.to_excel(writer, sheet_name='직배송상세', index=False)
                    
                    if delivery['warehouse_transfer_data']:
                        transfer_df = pd.DataFrame(delivery['warehouse_transfer_data'])
                        transfer_df.to_excel(writer, sheet_name='창고이동상세', index=False)
                
                # 4. 분석 요약
                summary_data = []
                for key, value in self.analysis_results.items():
                    if key == 'outbound_pivot':
                        summary_data.append({'분석항목': '월별출고피벗', '상태': '완료'})
                    elif key == 'site_inbound_pivot':
                        summary_data.append({'분석항목': '현장입고피벗', '상태': '완료' if value else '데이터없음'})
                    elif key == 'delivery_transfer':
                        summary_data.append({'분석항목': '직배송분석', '상태': '완료'})
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='분석요약', index=False)
            
            print(f"✅ 종합 분석 결과 저장 완료: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"❌ 결과 내보내기 실패: {e}")
            return None

def main():
    """메인 실행 함수"""
    analyzer = CompletePivotAnalyzer()
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n🔧 **추천 명령어:**")
        print("/logi_master analyze_outbound_trend [출고 추이 분석]")
        print("/logi_master analyze_site_performance [현장 성과 분석]")
        print("/logi_master analyze_transfer_patterns [이동 패턴 분석]")
        print("/automate test-pipeline [전체 테스트 파이프라인 실행]")
    else:
        print("\n❌ 분석 실패")

if __name__ == "__main__":
    main() 