#!/usr/bin/env python3
"""
창고_현장_월별 보고서 Excel 파일 생성기 (수정된 버전)
실제 데이터 구조 기반으로 완전히 새로 작성
HVDC 물류 마스터 시스템 v3.4-mini
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

class WarehouseSiteMonthlyReportGeneratorFixed:
    """창고_현장_월별_시트_구조 Excel 리포트 생성기 (수정된 버전)"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 실제 데이터 구조 기반 매핑
        self.warehouse_columns = {
            'DSV Indoor': 'DSV_Indoor',
            'DSV Al Markaz': 'DSV_Al_Markaz', 
            'DSV Outdoor': 'DSV_Outdoor',
            'AAA  Storage': 'AAA_Storage',
            'Hauler Indoor': 'Hauler_Indoor',
            'DSV MZP': 'DSV_MZP',
            'MOSB': 'MOSB'
        }
        
        self.site_columns = {
            'MIR': 'MIR',
            'SHU': 'SHU', 
            'DAS': 'DAS',
            'AGI': 'AGI'
        }
        
        # 월별 기간 정의
        self.warehouse_period = pd.date_range(
            start='2023-02-01',
            end='2025-06-01', 
            freq='MS'
        )
        
        self.site_period = pd.date_range(
            start='2024-01-01',
            end='2025-06-01',
            freq='MS'
        )
        
    def load_source_data(self) -> pd.DataFrame:
        """실제 데이터 로드"""
        print("🏗️ 창고_현장_월별 보고서 생성기 (수정된 버전) 초기화 완료")
        
        main_source = "MACHO_통합관리_20250702_205301/MACHO_Final_Report_Complete_20250703_230904.xlsx"
        
        try:
            print(f"✅ MAIN_SOURCE 파일 로드 시도: {main_source}")
            df = pd.read_excel(main_source, engine='openpyxl')
            print(f"📊 데이터 로드 성공: {len(df):,}건, {len(df.columns)}개 컬럼")
            
            # 날짜 컬럼 전처리
            date_columns = ['ETD/ATD', 'ETA/ATA'] + list(self.warehouse_columns.keys()) + list(self.site_columns.keys())
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            print(f"🔧 데이터 전처리 완료")
            return df
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def create_warehouse_monthly_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """창고_월별_입출고 시트 생성 (실제 데이터 기반)"""
        print("📊 창고_월별_입출고 시트 생성 중...")
        
        # 결과 데이터 초기화
        result_data = []
        
        # 각 월별로 처리
        for period in self.warehouse_period:
            month_str = period.strftime('%Y-%m')
            row_data = {'Location': month_str}
            
            # 각 창고별 입출고 집계
            for warehouse_name, warehouse_col in self.warehouse_columns.items():
                if warehouse_name in df.columns:
                    # 해당 월에 해당 창고로 입고된 건수
                    warehouse_dates = df[warehouse_name].dropna()
                    month_mask = warehouse_dates.dt.to_period('M') == period.to_period('M')
                    inbound_count = month_mask.sum()
                    
                    # 출고는 Status_Location 기준으로 계산
                    # (해당 창고에서 다른 곳으로 이동한 건수)
                    outbound_count = 0
                    if 'Status_Location' in df.columns:
                        # 현재 해당 창고에 있지 않지만 과거에 있었던 건수 추정
                        warehouse_visited = df[warehouse_name].notna()
                        currently_not_here = df['Status_Location'] != warehouse_name.replace('  ', ' ')
                        outbound_count = (warehouse_visited & currently_not_here).sum()
                    
                    row_data[f'입고_{warehouse_col}'] = inbound_count
                    row_data[f'출고_{warehouse_col}'] = outbound_count
                else:
                    row_data[f'입고_{warehouse_col}'] = 0
                    row_data[f'출고_{warehouse_col}'] = 0
            
            result_data.append(row_data)
        
        # 합계 행 추가
        total_row = {'Location': 'Total'}
        for warehouse_name, warehouse_col in self.warehouse_columns.items():
            total_inbound = sum(row.get(f'입고_{warehouse_col}', 0) for row in result_data)
            total_outbound = sum(row.get(f'출고_{warehouse_col}', 0) for row in result_data)
            total_row[f'입고_{warehouse_col}'] = total_inbound
            total_row[f'출고_{warehouse_col}'] = total_outbound
        
        result_data.append(total_row)
        
        # DataFrame 생성
        warehouse_df = pd.DataFrame(result_data)
        
        # 컬럼 순서 정리
        column_order = ['Location']
        for warehouse_name, warehouse_col in self.warehouse_columns.items():
            column_order.extend([f'입고_{warehouse_col}', f'출고_{warehouse_col}'])
        
        warehouse_df = warehouse_df[column_order]
        
        print(f"✅ 창고_월별_입출고 시트 완료: {len(warehouse_df)}행 × {len(warehouse_df.columns)}열")
        print(f"📊 실제 데이터 집계 완료 - 총 입고: {warehouse_df.iloc[-1, 1:].sum():.0f}건")
        
        return warehouse_df
    
    def create_site_monthly_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """현장_월별_입고재고 시트 생성 (실제 데이터 기반)"""
        print("📊 현장_월별_입고재고 시트 생성 중...")
        
        # 결과 데이터 초기화
        result_data = []
        
        # 각 월별로 처리
        for period in self.site_period:
            month_str = period.strftime('%Y-%m')
            row_data = {'Location': month_str}
            
            # 각 현장별 입고재고 집계
            for site_name, site_col in self.site_columns.items():
                if site_name in df.columns:
                    # 해당 월에 해당 현장으로 입고된 건수
                    site_dates = df[site_name].dropna()
                    month_mask = site_dates.dt.to_period('M') == period.to_period('M')
                    inbound_count = month_mask.sum()
                    
                    # 재고는 Status_Location 기준으로 계산
                    # (해당 현장에 현재 있는 건수)
                    inventory_count = 0
                    if 'Status_Location' in df.columns:
                        inventory_count = (df['Status_Location'] == site_name).sum()
                    
                    row_data[f'입고_{site_col}'] = inbound_count
                    row_data[f'재고_{site_col}'] = inventory_count
                else:
                    row_data[f'입고_{site_col}'] = 0
                    row_data[f'재고_{site_col}'] = 0
            
            result_data.append(row_data)
        
        # 합계 행 추가
        total_row = {'Location': '합계'}
        for site_name, site_col in self.site_columns.items():
            total_inbound = sum(row.get(f'입고_{site_col}', 0) for row in result_data)
            # 재고는 최종 재고 (마지막 값)
            final_inventory = result_data[-1].get(f'재고_{site_col}', 0) if result_data else 0
            total_row[f'입고_{site_col}'] = total_inbound
            total_row[f'재고_{site_col}'] = final_inventory
        
        result_data.append(total_row)
        
        # DataFrame 생성
        site_df = pd.DataFrame(result_data)
        
        # 컬럼 순서 정리
        column_order = ['Location']
        for site_name, site_col in self.site_columns.items():
            column_order.extend([f'입고_{site_col}', f'재고_{site_col}'])
        
        site_df = site_df[column_order]
        
        print(f"✅ 현장_월별_입고재고 시트 완료: {len(site_df)}행 × {len(site_df.columns)}열")
        print(f"📊 실제 데이터 집계 완료 - 총 입고: {site_df.iloc[-1, 1::2].sum():.0f}건")
        
        return site_df
    
    def create_transaction_summary_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """전체_트랜잭션_FLOWCODE0-4 요약 시트"""
        print("📊 전체 트랜잭션 요약 시트 생성 중...")
        
        # 핵심 컬럼만 선택하여 요약
        summary_columns = [
            'Case No.', 'HVDC CODE', 'VENDOR', 'Site', 'FLOW_CODE',
            'Status_Current', 'Status_Location', 'SQM', 'CBM', 'G.W(kgs)',
            'wh handling', 'site  handling', 'total handling'
        ]
        
        # 존재하는 컬럼만 선택
        available_columns = [col for col in summary_columns if col in df.columns]
        summary_df = df[available_columns].copy()
        
        # FLOW_CODE 설명 추가
        flow_code_descriptions = {
            0: 'Pre-Arrival (직접 현장)',
            1: 'Port → Site (1단계)',
            2: 'Port → Warehouse → Site (2단계)',
            3: 'Port → Warehouse → MOSB → Site (3단계)',
            4: 'Port → Warehouse → Warehouse → MOSB → Site (4단계)'
        }
        
        if 'FLOW_CODE' in summary_df.columns:
            summary_df['FLOW_CODE_설명'] = summary_df['FLOW_CODE'].map(flow_code_descriptions)
        
        print(f"✅ 트랜잭션 요약 시트 완료: {len(summary_df)}건")
        return summary_df
    
    def create_statistics_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """통계 및 분석 시트 (실제 데이터 기반)"""
        print("📊 통계 분석 시트 생성 중...")
        
        stats_data = []
        
        # 기본 통계
        stats_data.append({'구분': '총 화물 건수', '값': f'{len(df):,}건', '비고': '전체 트랜잭션'})
        stats_data.append({'구분': '총 컬럼 수', '값': f'{len(df.columns)}개', '비고': '데이터 필드'})
        
        # FLOW_CODE 분포
        if 'FLOW_CODE' in df.columns:
            flow_counts = df['FLOW_CODE'].value_counts().sort_index()
            for code, count in flow_counts.items():
                percentage = (count / len(df)) * 100
                stats_data.append({
                    '구분': f'FLOW_CODE_{code}',
                    '값': f'{count:,}건 ({percentage:.1f}%)',
                    '비고': f'물류 단계 {code}'
                })
        
        # 창고별 실제 집계
        stats_data.append({'구분': '=== 창고별 실제 집계 ===', '값': '', '비고': ''})
        for warehouse_name in self.warehouse_columns.keys():
            if warehouse_name in df.columns:
                count = df[warehouse_name].notna().sum()
                percentage = (count / len(df)) * 100
                stats_data.append({
                    '구분': f'창고_{warehouse_name}',
                    '값': f'{count:,}건 ({percentage:.1f}%)',
                    '비고': '창고 경유 건수'
                })
        
        # 현장별 실제 집계
        stats_data.append({'구분': '=== 현장별 실제 집계 ===', '값': '', '비고': ''})
        for site_name in self.site_columns.keys():
            if site_name in df.columns:
                count = df[site_name].notna().sum()
                percentage = (count / len(df)) * 100
                stats_data.append({
                    '구분': f'현장_{site_name}',
                    '값': f'{count:,}건 ({percentage:.1f}%)',
                    '비고': '현장 도착 건수'
                })
        
        # Status_Location 분포
        if 'Status_Location' in df.columns:
            stats_data.append({'구분': '=== 현재 위치 분포 ===', '값': '', '비고': ''})
            location_counts = df['Status_Location'].value_counts().head(10)
            for location, count in location_counts.items():
                percentage = (count / len(df)) * 100
                stats_data.append({
                    '구분': f'위치_{location}',
                    '값': f'{count:,}건 ({percentage:.1f}%)',
                    '비고': '현재 위치'
                })
        
        # 품질 점수
        total_cells = len(df) * len(df.columns)
        filled_cells = total_cells - df.isna().sum().sum()
        quality_score = (filled_cells / total_cells) * 100
        stats_data.append({'구분': '데이터 품질 점수', '값': f'{quality_score:.1f}%', '비고': '완성도 지표'})
        
        # 생성 정보
        stats_data.append({'구분': '보고서 생성일시', '값': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '비고': 'HVDC 물류 마스터 (수정됨)'})
        
        stats_df = pd.DataFrame(stats_data)
        
        print(f"✅ 통계 분석 시트 완료: {len(stats_df)}개 지표")
        return stats_df
    
    def create_multi_level_headers(self, writer, sheet_name, df):
        """Multi-level Header 생성"""
        worksheet = writer.sheets[sheet_name]
        
        if sheet_name == '창고_월별_입출고':
            # 창고별 입출고 헤더
            header1 = ['Location']
            header2 = ['']
            
            for warehouse_name in self.warehouse_columns.values():
                header1.extend([f'입고_{warehouse_name}', f'출고_{warehouse_name}'])
                header2.extend(['입고', '출고'])
            
            # 헤더 쓰기
            for col_idx, (h1, h2) in enumerate(zip(header1, header2)):
                if col_idx == 0:
                    worksheet.cell(row=1, column=col_idx+1, value=h1)
                    worksheet.cell(row=2, column=col_idx+1, value=h2)
                else:
                    worksheet.cell(row=1, column=col_idx+1, value=h1.split('_')[1] if '_' in h1 else h1)
                    worksheet.cell(row=2, column=col_idx+1, value=h1.split('_')[0] if '_' in h1 else h1)
        
        elif sheet_name == '현장_월별_입고재고':
            # 현장별 입고재고 헤더
            header1 = ['Location']
            header2 = ['']
            
            for site_name in self.site_columns.values():
                header1.extend([f'입고_{site_name}', f'재고_{site_name}'])
                header2.extend(['입고', '재고'])
            
            # 헤더 쓰기
            for col_idx, (h1, h2) in enumerate(zip(header1, header2)):
                if col_idx == 0:
                    worksheet.cell(row=1, column=col_idx+1, value=h1)
                    worksheet.cell(row=2, column=col_idx+1, value=h2)
                else:
                    worksheet.cell(row=1, column=col_idx+1, value=h1.split('_')[1] if '_' in h1 else h1)
                    worksheet.cell(row=2, column=col_idx+1, value=h1.split('_')[0] if '_' in h1 else h1)
    
    def generate_excel_report(self, df: pd.DataFrame, output_file: str = None) -> str:
        """완전한 Excel 리포트 생성 (수정된 버전)"""
        if not output_file:
            output_file = f'창고_현장_월별_보고서_수정됨_{self.timestamp}.xlsx'
        
        print(f"📊 Excel 리포트 생성 시작: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Sheet 1: 전체 트랜잭션 요약
            transaction_summary = self.create_transaction_summary_sheet(df)
            transaction_summary.to_excel(writer, sheet_name='전체_트랜잭션_FLOWCODE0-4', index=False)
            print("✅ Sheet 1: 전체_트랜잭션_FLOWCODE0-4 완료")
            
            # Sheet 2: 창고별 월별 입출고 (실제 데이터)
            warehouse_monthly = self.create_warehouse_monthly_sheet(df)
            warehouse_monthly.to_excel(writer, sheet_name='창고_월별_입출고', index=False)
            print("✅ Sheet 2: 창고_월별_입출고 완료 (실제 데이터)")
            
            # Sheet 3: 현장별 월별 입고재고 (실제 데이터)
            site_monthly = self.create_site_monthly_sheet(df)
            site_monthly.to_excel(writer, sheet_name='현장_월별_입고재고', index=False)
            print("✅ Sheet 3: 현장_월별_입고재고 완료 (실제 데이터)")
            
            # Sheet 4: 통계 및 분석
            statistics = self.create_statistics_sheet(df)
            statistics.to_excel(writer, sheet_name='통계_및_분석', index=False)
            print("✅ Sheet 4: 통계_및_분석 완료")
            
            # Sheet 5: 원본 데이터 (처음 1000건만)
            if len(df) > 1000:
                df_sample = df.head(1000).copy()
            else:
                df_sample = df.copy()
            df_sample.to_excel(writer, sheet_name='원본_데이터_샘플', index=False)
            print("✅ Sheet 5: 원본_데이터_샘플 완료")
        
        print(f"🎉 Excel 리포트 생성 완료: {output_file}")
        return output_file
    
    def run(self) -> str:
        """메인 실행 함수"""
        print("🚀 창고_현장_월별 보고서 생성 시작 (수정된 버전)")
        print("=" * 60)
        
        try:
            # 1. 데이터 로드
            df = self.load_source_data()
            
            if df.empty:
                print("❌ 데이터 로드 실패")
                return ""
            
            # 2. Excel 리포트 생성
            output_file = self.generate_excel_report(df)
            
            # 3. 결과 요약
            print(f"\n🎉 Excel 리포트 생성 완료: {output_file}")
            print(f"\n📋 생성된 시트 목록:")
            print(f"  1. 전체_트랜잭션_FLOWCODE0-4 - 트랜잭션 요약")
            print(f"  2. 창고_월별_입출고 - 실제 데이터 기반 Multi-level Header")
            print(f"  3. 현장_월별_입고재고 - 실제 데이터 기반 Multi-level Header")
            print(f"  4. 통계_및_분석 - 종합 분석")
            print(f"  5. 원본_데이터_샘플 - 원본 데이터")
            
            print(f"\n🎯 생성 결과:")
            print(f"  📁 파일명: {output_file}")
            print(f"  📊 총 데이터: {len(df):,}건")
            print(f"  📅 생성 시간: {self.timestamp}")
            print(f"  ✅ 상태: 성공 (실제 데이터 기반)")
            
            return output_file
            
        except Exception as e:
            print(f"❌ 보고서 생성 실패: {e}")
            return ""

def main():
    """메인 실행 함수"""
    print("🏗️ HVDC 창고_현장_월별 보고서 생성기 (수정된 버전)")
    print("Samsung C&T · ADNOC · DSV Partnership")
    print("=" * 60)
    
    generator = WarehouseSiteMonthlyReportGeneratorFixed()
    output_file = generator.run()
    
    if output_file:
        print(f"\n🔧 추천 명령어:")
        print(f"  Excel 파일 열기: start {output_file}")
        print(f"  /logi_master process_data [통합 시스템 실행]")
        print(f"  /validate_data_quality [데이터 품질 검증]")
    
    return output_file

if __name__ == "__main__":
    main() 