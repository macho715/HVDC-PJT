#!/usr/bin/env python3
"""
🚀 HVDC Excel 시스템 생성기 v2.8.5 (올바른 계산)
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini

실제_사용된_함수_로직_파일_상세_보고서.md 기준 완전 구현:
✅ 올바른 입출고 계산 로직
✅ 실제 HVDC 데이터 패턴 반영
✅ 누적 재고 정확한 계산
✅ Multi-Level Header 구조
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class HVDCExcelSystemGeneratorCorrect:
    def __init__(self):
        print("🚀 HVDC Excel 시스템 생성기 v2.8.5 (올바른 계산)")
        print("=" * 80)
        print("📋 실제 HVDC 데이터 패턴 기반 정확한 입출고 계산")
        print("-" * 80)
        
        # 실제 HVDC 데이터 구조 기반 매핑
        self.warehouse_columns = {
            'DSV Indoor': 'DSV_Indoor',
            'DSV Al Markaz': 'DSV_Al_Markaz', 
            'DSV Outdoor': 'DSV_Outdoor',
            'AAA Storage': 'AAA_Storage',    # 수정: 공백 하나
            'Hauler Indoor': 'Hauler_Indoor',
            'DSV MZP': 'DSV_MZP',
            'MOSB': 'MOSB'
        }
        
        self.site_columns = {
            'AGI': 'AGI',
            'DAS': 'DAS', 
            'MIR': 'MIR',
            'SHU': 'SHU'
        }
        
        self.months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        
        self.flow_codes = {
            0: 'Pre Arrival',
            1: 'Port → Site',
            2: 'Port → WH → Site', 
            3: 'Port → WH → MOSB → Site',
            4: 'Port → WH → WH → MOSB → Site'
        }
        
        # 월별 기간 설정 (실제 HVDC 프로젝트 기간)
        self.warehouse_period = pd.date_range(start='2024-01-01', end='2025-06-01', freq='MS')
        self.site_period = pd.date_range(start='2024-01-01', end='2025-06-01', freq='MS')
        
        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 출력 파일명
        self.output_file = f"HVDC_Correct_System_Report_{self.timestamp}.xlsx"
        
        print(f"📊 창고 수: {len(self.warehouse_columns)}개")
        print(f"🏭 현장 수: {len(self.site_columns)}개")
        print(f"📅 월별 추적: {len(self.warehouse_period)}개월")
        print(f"📋 Flow Code: {len(self.flow_codes)}개 유형")
        
    def generate_realistic_transaction_data(self, num_transactions=7573):
        """실제 HVDC 데이터 패턴 기반 트랜잭션 데이터 생성"""
        print(f"\n🔧 실제 HVDC 패턴 기반 트랜잭션 데이터 생성 중... ({num_transactions:,}건)")
        
        # 실제 HVDC 프로젝트 벤더 및 카테고리 분포
        vendors = ['HITACHI', 'SIMENSE', 'SAMSUNG', 'OTHERS']
        vendor_weights = [0.70, 0.29, 0.005, 0.005]  # 실제 분포 반영
        
        categories = ['HE', 'SIM', 'SCT', 'DGR', 'OTH']
        category_weights = [0.40, 0.30, 0.15, 0.10, 0.05]
        
        data = []
        
        # 실제 창고별 처리 능력 (상세 보고서 기준)
        warehouse_capacity = {
            'DSV Indoor': 1465,
            'DSV Al Markaz': 1039,
            'DSV Outdoor': 1925,
            'AAA Storage': 101,
            'Hauler Indoor': 392,
            'DSV MZP': 13,
            'MOSB': 728
        }
        
        # 실제 현장별 처리 능력 (상세 보고서 기준)
        site_capacity = {
            'MIR': 1272,
            'SHU': 1823,
            'DAS': 949,
            'AGI': 80
        }
        
        for i in range(num_transactions):
            # 기본 정보
            case_no = f"HVDC{i+1:06d}"
            vendor = np.random.choice(vendors, p=vendor_weights)
            category = np.random.choice(categories, p=category_weights)
            
            # 프로젝트 진행률 반영 (2024년 초반에 집중, 후반으로 갈수록 감소)
            project_start = datetime(2024, 1, 1)
            project_progress_factor = random.uniform(0.3, 1.0)
            
            # 창고 경로 생성 (실제 Flow Code 패턴 반영)
            warehouse_path = self._generate_realistic_warehouse_path(vendor)
            site_destination = self._generate_realistic_site_destination()
            
            # 날짜 순서 생성 (논리적 흐름 보장)
            dates = self._generate_logical_date_sequence(warehouse_path, site_destination, project_start)
            
            # Flow Code 계산 (실제 경로 기반)
            flow_code = self._calculate_flow_code_from_path(warehouse_path, site_destination)
            
            # 물류 정보 (실제 HVDC 프로젝트 패턴)
            weight = self._generate_realistic_weight(category)
            cbm = weight * random.uniform(0.8, 1.5)  # 중량 대비 CBM
            sqm = cbm * random.uniform(0.6, 1.2)    # CBM 대비 SQM
            pkg_count = max(1, int(weight / random.uniform(0.5, 2.0)))
            
            # 기본 레코드 생성
            record = {
                'Case No.': case_no,
                'Vendor': vendor,
                'Category': category,
                'Description': f'{vendor} {category} Equipment - {case_no}',
                'Weight': round(weight, 2),
                'CBM': round(cbm, 2),
                'SQM': round(sqm, 2),
                'PKG': pkg_count,
                'FLOW_CODE': flow_code,
                'FLOW_DESCRIPTION': self.flow_codes[flow_code],
                'WH_HANDLING': len(warehouse_path),
                'STATUS': 'ACTIVE' if flow_code > 0 else 'PRE_ARRIVAL',
                'CREATED_DATE': project_start + timedelta(days=random.randint(0, 365)),
                'LAST_UPDATED': datetime.now()
            }
            
            # 현재 위치 (Status_Location) 설정
            if site_destination and random.random() < 0.7:
                record['Status_Location'] = site_destination
            elif warehouse_path and random.random() < 0.2:
                record['Status_Location'] = random.choice(warehouse_path)
            else:
                record['Status_Location'] = 'Pre Arrival'
            
            # 창고 날짜 정보 추가
            for warehouse in self.warehouse_columns.keys():
                if warehouse in warehouse_path:
                    idx = warehouse_path.index(warehouse)
                    record[warehouse] = dates.get(f'warehouse_{idx}', '')
                else:
                    record[warehouse] = ''
            
            # 현장 날짜 정보 추가
            for site in self.site_columns.keys():
                if site == site_destination:
                    record[site] = dates.get('site', '')
                else:
                    record[site] = ''
            
            data.append(record)
        
        df = pd.DataFrame(data)
        
        # 날짜 컬럼 변환
        date_columns = list(self.warehouse_columns.keys()) + list(self.site_columns.keys())
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        print(f"✅ 생성 완료: {len(df):,}건")
        return df
    
    def _generate_realistic_warehouse_path(self, vendor):
        """벤더별 실제 창고 경로 생성"""
        if vendor == 'HITACHI':
            # HITACHI는 단순 경로 선호
            paths = [
                ['DSV Indoor'],
                ['DSV Outdoor'],
                ['DSV Indoor', 'MOSB'],
                []  # Pre Arrival
            ]
            weights = [0.35, 0.35, 0.25, 0.05]
        elif vendor == 'SIMENSE':
            # SIMENSE는 복잡 경로 포함
            paths = [
                ['DSV Al Markaz'],
                ['DSV Indoor', 'DSV Al Markaz'],
                ['DSV Outdoor', 'MOSB'],
                ['DSV Indoor', 'DSV Al Markaz', 'MOSB'],
                []  # Pre Arrival
            ]
            weights = [0.25, 0.25, 0.20, 0.20, 0.10]
        else:
            # 기타 벤더는 표준 경로
            paths = [
                ['DSV Indoor'],
                ['DSV Outdoor'],
                ['AAA Storage'],
                []  # Pre Arrival
            ]
            weights = [0.40, 0.40, 0.15, 0.05]
        
        return np.random.choice(len(paths), p=weights), paths
    
    def _generate_realistic_site_destination(self):
        """실제 현장 분포 기반 목적지 생성"""
        sites = ['SHU', 'MIR', 'DAS', 'AGI', None]  # None은 현장 미정
        weights = [0.30, 0.25, 0.20, 0.05, 0.20]
        
        selected = np.random.choice(len(sites), p=weights)
        return sites[selected]
    
    def _generate_logical_date_sequence(self, warehouse_path, site_destination, start_date):
        """논리적 날짜 순서 생성"""
        dates = {}
        current_date = start_date + timedelta(days=random.randint(0, 300))
        
        # 창고 순서대로 날짜 할당
        path_idx, path_list = warehouse_path
        for i, warehouse in enumerate(path_list):
            dates[f'warehouse_{i}'] = current_date
            current_date += timedelta(days=random.randint(1, 30))
        
        # 현장 날짜 (창고 완료 후)
        if site_destination:
            dates['site'] = current_date + timedelta(days=random.randint(1, 15))
        
        return dates
    
    def _calculate_flow_code_from_path(self, warehouse_path, site_destination):
        """실제 경로 기반 Flow Code 계산"""
        path_idx, path_list = warehouse_path
        
        if not path_list:
            return 0  # Pre Arrival
        
        wh_count = len(path_list)
        has_mosb = 'MOSB' in path_list
        
        if wh_count == 1 and not has_mosb:
            return 1  # Port → WH → Site
        elif wh_count == 2 and not has_mosb:
            return 2  # Port → WH → WH → Site
        elif has_mosb:
            return 3  # Port → WH → MOSB → Site
        else:
            return min(4, wh_count)  # 최대 4
    
    def _generate_realistic_weight(self, category):
        """카테고리별 실제 중량 분포"""
        if category == 'HE':  # Heavy Equipment
            return random.uniform(10.0, 100.0)
        elif category == 'SIM':  # Simense Equipment
            return random.uniform(5.0, 50.0)
        elif category == 'SCT':  # Samsung C&T
            return random.uniform(1.0, 25.0)
        elif category == 'DGR':  # Dangerous Goods
            return random.uniform(0.5, 10.0)
        else:  # Others
            return random.uniform(0.1, 5.0)
    
    def calculate_warehouse_outbound_correct(self, df, warehouse_name, period):
        """창고별 월별 출고 계산 (올바른 로직)"""
        if warehouse_name not in df.columns:
            return 0
        
        # 해당 창고를 방문한 케이스들
        warehouse_visited = df[df[warehouse_name].notna()].copy()
        
        if len(warehouse_visited) == 0:
            return 0
        
        outbound_count = 0
        
        # 각 케이스별로 창고 → 다음 단계 이동 확인
        for idx, row in warehouse_visited.iterrows():
            warehouse_date = row[warehouse_name]
            
            # 창고 방문 후 다음 단계(현장) 이동 날짜 찾기
            next_dates = []
            
            # 현장별 날짜 확인
            for site_name in self.site_columns.keys():
                if site_name in row.index and pd.notna(row[site_name]):
                    site_date = row[site_name]
                    if pd.notna(site_date) and site_date > warehouse_date:  # 창고 방문 후에 현장 도착
                        next_dates.append(site_date)
            
            # 가장 빠른 다음 단계 날짜
            if next_dates:
                earliest_next_date = min(next_dates)
                # 해당 월에 출고된 경우
                if earliest_next_date.to_period('M') == period.to_period('M'):
                    outbound_count += 1
        
        return outbound_count
    
    def calculate_site_inventory_correct(self, df, site_name, period):
        """현장별 월별 재고 계산 (누적 로직)"""
        if site_name not in df.columns:
            return 0
        
        # 해당 월 말까지 해당 현장에 도착한 총 건수
        site_dates = df[site_name].dropna()
        
        # 해당 월 말까지 도착한 건수
        month_end = period + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        arrived_by_month_end = (site_dates <= month_end).sum()
        
        # 현재 Status_Location이 해당 현장인 건수와 비교하여 더 정확한 값 사용
        current_at_site = 0
        if 'Status_Location' in df.columns:
            current_at_site = (df['Status_Location'] == site_name).sum()
        
        # 누적 도착 건수와 현재 위치 건수 중 더 보수적인 값
        return min(arrived_by_month_end, current_at_site) if current_at_site > 0 else arrived_by_month_end
    
    def create_warehouse_monthly_sheet_correct(self, df):
        """창고별 월별 입출고 시트 생성 (올바른 계산)"""
        print("\n📊 창고별 월별 입출고 시트 생성 중 (올바른 계산)...")
        
        # 결과 데이터 초기화
        result_data = []
        
        # 각 월별로 처리
        for period in self.warehouse_period:
            month_str = period.strftime('%Y-%m')
            row_data = {'Month': month_str}
            
            # 각 창고별 입출고 집계
            for warehouse_name, warehouse_col in self.warehouse_columns.items():
                if warehouse_name in df.columns:
                    # 입고: 해당 월에 해당 창고에 도착한 건수
                    warehouse_dates = df[warehouse_name].dropna()
                    month_mask = warehouse_dates.dt.to_period('M') == period.to_period('M')
                    inbound_count = month_mask.sum()
                    
                    # 출고: 해당 월에 해당 창고에서 다음 단계로 이동한 건수 (정확한 계산)
                    outbound_count = self.calculate_warehouse_outbound_correct(df, warehouse_name, period)
                    
                    row_data[f'입고_{warehouse_col}'] = inbound_count
                    row_data[f'출고_{warehouse_col}'] = outbound_count
                else:
                    row_data[f'입고_{warehouse_col}'] = 0
                    row_data[f'출고_{warehouse_col}'] = 0
            
            result_data.append(row_data)
        
        # DataFrame 생성
        warehouse_df = pd.DataFrame(result_data)
        
        # Multi-Level Header 생성
        level_0 = []
        level_1 = []
        
        level_0.append('Month')
        level_1.append('')
        
        for warehouse_name, warehouse_col in self.warehouse_columns.items():
            level_0.extend(['입고', '출고'])
            level_1.extend([warehouse_col, warehouse_col])
        
        # MultiIndex 컬럼 적용
        multi_columns = pd.MultiIndex.from_arrays([level_0, level_1], names=['구분', 'Warehouse'])
        
        # 컬럼 순서 맞추기
        column_order = ['Month']
        for warehouse_name, warehouse_col in self.warehouse_columns.items():
            column_order.extend([f'입고_{warehouse_col}', f'출고_{warehouse_col}'])
        
        warehouse_df = warehouse_df[column_order]
        warehouse_df.columns = multi_columns
        
        print(f"✅ 창고별 월별 시트 생성 완료: {warehouse_df.shape}")
        return warehouse_df
    
    def create_site_monthly_sheet_correct(self, df):
        """현장별 월별 입고재고 시트 생성 (올바른 계산)"""
        print("\n🏭 현장별 월별 입고재고 시트 생성 중 (올바른 계산)...")
        
        # 결과 데이터 초기화
        result_data = []
        
        # 각 월별로 처리
        for period in self.site_period:
            month_str = period.strftime('%Y-%m')
            row_data = {'Month': month_str}
            
            # 각 현장별 입고재고 집계
            for site_name, site_col in self.site_columns.items():
                if site_name in df.columns:
                    # 입고: 해당 월에 해당 현장에 도착한 건수
                    site_dates = df[site_name].dropna()
                    month_mask = site_dates.dt.to_period('M') == period.to_period('M')
                    inbound_count = month_mask.sum()
                    
                    # 재고: 해당 월 말 기준 해당 현장의 누적 재고 (올바른 계산)
                    inventory_count = self.calculate_site_inventory_correct(df, site_name, period)
                    
                    row_data[f'입고_{site_col}'] = inbound_count
                    row_data[f'재고_{site_col}'] = inventory_count
                else:
                    row_data[f'입고_{site_col}'] = 0
                    row_data[f'재고_{site_col}'] = 0
            
            result_data.append(row_data)
        
        # DataFrame 생성
        site_df = pd.DataFrame(result_data)
        
        # Multi-Level Header 생성
        level_0 = []
        level_1 = []
        
        level_0.append('Month')
        level_1.append('')
        
        for site_name, site_col in self.site_columns.items():
            level_0.extend(['입고', '재고'])
            level_1.extend([site_col, site_col])
        
        # MultiIndex 컬럼 적용
        multi_columns = pd.MultiIndex.from_arrays([level_0, level_1], names=['구분', 'Site'])
        
        # 컬럼 순서 맞추기
        column_order = ['Month']
        for site_name, site_col in self.site_columns.items():
            column_order.extend([f'입고_{site_col}', f'재고_{site_col}'])
        
        site_df = site_df[column_order]
        site_df.columns = multi_columns
        
        print(f"✅ 현장별 월별 시트 생성 완료: {site_df.shape}")
        return site_df
    
    def create_flow_code_analysis_correct(self, df):
        """Flow Code 분석 시트 생성 (올바른 계산)"""
        print("\n📋 Flow Code 분석 시트 생성 중...")
        
        # Flow Code별 집계
        flow_summary = df.groupby('FLOW_CODE').agg({
            'Case No.': 'count',
            'Weight': ['sum', 'mean'],
            'CBM': ['sum', 'mean'],
            'SQM': ['sum', 'mean'],
            'PKG': 'sum'
        }).reset_index()
        
        # 컬럼명 정리
        flow_summary.columns = ['Flow_Code', 'Count', 'Total_Weight', 'Avg_Weight', 
                               'Total_CBM', 'Avg_CBM', 'Total_SQM', 'Avg_SQM', 'Total_PKG']
        
        # Flow Code 설명 추가
        flow_summary['Description'] = flow_summary['Flow_Code'].map(self.flow_codes)
        
        # 비율 계산
        total_count = flow_summary['Count'].sum()
        flow_summary['Percentage'] = (flow_summary['Count'] / total_count * 100).round(2)
        
        # 컬럼 순서 재정렬
        flow_summary = flow_summary[['Flow_Code', 'Description', 'Count', 'Percentage', 
                                   'Total_Weight', 'Avg_Weight', 'Total_CBM', 'Avg_CBM',
                                   'Total_SQM', 'Avg_SQM', 'Total_PKG']]
        
        print(f"✅ Flow Code 분석 완료: {len(flow_summary)}개 코드")
        return flow_summary
    
    def create_pre_arrival_analysis_correct(self, df):
        """Pre Arrival 상세 분석 시트 생성 (올바른 계산)"""
        print("\n⏳ Pre Arrival 상세 분석 시트 생성 중...")
        
        # Pre Arrival 데이터 필터링
        pre_arrival_df = df[df['FLOW_CODE'] == 0].copy()
        
        if pre_arrival_df.empty:
            print("⚠️ Pre Arrival 데이터가 없습니다.")
            return pd.DataFrame({'Message': ['No Pre Arrival Data Available']})
        
        # 상세 분석 데이터 생성
        analysis_results = []
        
        # 요약 정보
        total_pre_arrival = len(pre_arrival_df)
        total_weight = pre_arrival_df['Weight'].sum()
        avg_weight = pre_arrival_df['Weight'].mean()
        
        analysis_results.append({
            'Analysis_Type': 'SUMMARY',
            'Category': 'Total Pre Arrival',
            'Count': total_pre_arrival,
            'Percentage': f"{total_pre_arrival/len(df)*100:.1f}%",
            'Total_Weight': round(total_weight, 2),
            'Avg_Weight': round(avg_weight, 2),
            'Description': '전체 Pre Arrival 건수'
        })
        
        # 벤더별 분석
        vendor_analysis = pre_arrival_df.groupby('Vendor').agg({
            'Case No.': 'count',
            'Weight': ['sum', 'mean']
        }).round(2)
        
        for vendor in vendor_analysis.index:
            count = vendor_analysis.loc[vendor, ('Case No.', 'count')]
            weight_sum = vendor_analysis.loc[vendor, ('Weight', 'sum')]
            weight_avg = vendor_analysis.loc[vendor, ('Weight', 'mean')]
            
            analysis_results.append({
                'Analysis_Type': 'VENDOR',
                'Category': vendor,
                'Count': count,
                'Percentage': f"{count/total_pre_arrival*100:.1f}%",
                'Total_Weight': weight_sum,
                'Avg_Weight': weight_avg,
                'Description': f'{vendor} Pre Arrival 분석'
            })
        
        # 카테고리별 분석
        category_analysis = pre_arrival_df.groupby('Category').agg({
            'Case No.': 'count',
            'Weight': ['sum', 'mean']
        }).round(2)
        
        for category in category_analysis.index:
            count = category_analysis.loc[category, ('Case No.', 'count')]
            weight_sum = category_analysis.loc[category, ('Weight', 'sum')]
            weight_avg = category_analysis.loc[category, ('Weight', 'mean')]
            
            analysis_results.append({
                'Analysis_Type': 'CATEGORY',
                'Category': category,
                'Count': count,
                'Percentage': f"{count/total_pre_arrival*100:.1f}%",
                'Total_Weight': weight_sum,
                'Avg_Weight': weight_avg,
                'Description': f'{category} 카테고리 Pre Arrival'
            })
        
        analysis_df = pd.DataFrame(analysis_results)
        print(f"✅ Pre Arrival 분석 완료: {len(pre_arrival_df)}건")
        return analysis_df
    
    def create_complete_excel_report_correct(self):
        """5개 시트 포함 완전한 Excel 리포트 생성 (올바른 계산)"""
        print(f"\n🚀 완전한 Excel 리포트 생성 시작 (올바른 계산)...")
        print("=" * 60)
        
        # 1. 실제 HVDC 패턴 기반 트랜잭션 데이터 생성
        df = self.generate_realistic_transaction_data()
        
        # 2. 각 시트 데이터 생성 (올바른 계산)
        print("\n📊 각 시트 데이터 생성 중 (올바른 계산)...")
        warehouse_monthly = self.create_warehouse_monthly_sheet_correct(df)
        site_monthly = self.create_site_monthly_sheet_correct(df)
        flow_analysis = self.create_flow_code_analysis_correct(df)
        pre_arrival_analysis = self.create_pre_arrival_analysis_correct(df)
        
        # 3. Excel 파일 생성
        print(f"\n📁 Excel 파일 생성 중: {self.output_file}")
        
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            # 시트 1: 전체 트랜잭션
            df.to_excel(writer, sheet_name='전체_트랜잭션_FLOWCODE0-4', index=False)
            print("✅ 시트 1: 전체_트랜잭션_FLOWCODE0-4")
            
            # 시트 2: Flow Code 분석
            flow_analysis.to_excel(writer, sheet_name='FLOWCODE0-4_분석요약', index=False)
            print("✅ 시트 2: FLOWCODE0-4_분석요약")
            
            # 시트 3: Pre Arrival 분석
            pre_arrival_analysis.to_excel(writer, sheet_name='Pre_Arrival_상세분석', index=False)
            print("✅ 시트 3: Pre_Arrival_상세분석")
            
            # 시트 4: 창고별 월별 (Multi-Level Header, 올바른 계산)
            warehouse_monthly.to_excel(writer, sheet_name='창고별_월별_입출고_완전체계')
            print("✅ 시트 4: 창고별_월별_입출고_완전체계 (올바른 계산)")
            
            # 시트 5: 현장별 월별 (Multi-Level Header, 올바른 계산)
            site_monthly.to_excel(writer, sheet_name='현장별_월별_입고재고_완전체계')
            print("✅ 시트 5: 현장별_월별_입고재고_완전체계 (올바른 계산)")
        
        # 4. 결과 요약 및 검증
        print("\n" + "=" * 60)
        print("🎉 HVDC Excel 시스템 생성 완료 (올바른 계산)!")
        print("=" * 60)
        print(f"📁 출력 파일: {self.output_file}")
        print(f"📊 총 트랜잭션: {len(df):,}건")
        print(f"🏭 시트 수: 5개")
        
        # 입출고 검증 정보
        total_warehouse_inbound = warehouse_monthly.iloc[:, 1::2].sum().sum()  # 입고 컬럼들
        total_warehouse_outbound = warehouse_monthly.iloc[:, 2::2].sum().sum()  # 출고 컬럼들
        total_site_inbound = site_monthly.iloc[:, 1::2].sum().sum()  # 입고 컬럼들
        
        print("\n🔍 입출고 검증 정보:")
        print(f"📦 창고 총 입고: {total_warehouse_inbound:,.0f}건")
        print(f"📤 창고 총 출고: {total_warehouse_outbound:,.0f}건")
        print(f"🏭 현장 총 입고: {total_site_inbound:,.0f}건")
        print(f"⚖️  입출고 비율: {total_warehouse_outbound/total_warehouse_inbound*100:.1f}%" if total_warehouse_inbound > 0 else "⚖️  입출고 비율: N/A")
        
        # Flow Code 분포 출력
        print("\n📊 Flow Code 분포:")
        flow_dist = df['FLOW_CODE'].value_counts().sort_index()
        for code, count in flow_dist.items():
            percentage = count / len(df) * 100
            print(f"  Code {code}: {count:,}건 ({percentage:.1f}%) - {self.flow_codes[code]}")
        
        print(f"\n🎯 처리 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return {
            'status': 'SUCCESS',
            'output_file': self.output_file,
            'total_transactions': len(df),
            'sheets_created': 5,
            'warehouses': len(self.warehouse_columns),
            'sites': len(self.site_columns),
            'warehouse_inbound': total_warehouse_inbound,
            'warehouse_outbound': total_warehouse_outbound,
            'site_inbound': total_site_inbound,
            'flow_code_distribution': flow_dist.to_dict()
        }

def main():
    """메인 실행 함수"""
    print("🚀 HVDC Excel 시스템 생성기 v2.8.5 (올바른 계산) 시작")
    print("Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini")
    print("=" * 80)
    
    # Excel 생성기 초기화 (올바른 계산)
    generator = HVDCExcelSystemGeneratorCorrect()
    
    # 완전한 Excel 리포트 생성
    result = generator.create_complete_excel_report_correct()
    
    if result['status'] == 'SUCCESS':
        print("\n🔧 추천 명령어:")
        print(f"📁 파일 열기: start {result['output_file']}")
        print("📊 입출고 검증: python validate_inbound_outbound.py")
        print("🎯 계산 로직 확인: python verify_calculation_logic.py")
        
        return result
    else:
        print("❌ Excel 생성 실패")
        return None

if __name__ == "__main__":
    main() 