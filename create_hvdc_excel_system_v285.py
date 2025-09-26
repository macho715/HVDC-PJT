#!/usr/bin/env python3
"""
🚀 HVDC Excel 시스템 생성기 v2.8.5
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini

HVDC_SYSTEM_ARCHITECTURE_REPORT_v285.md 기준 완전 구현:
✅ Multi-Level Header 구조
✅ 7개 창고 × 4개 현장 통합 관리
✅ 5개 시트 완전한 최종 리포트
✅ 월별 입출고·재고 실시간 추적
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class HVDCExcelSystemGenerator:
    def __init__(self):
        print("🚀 HVDC Excel 시스템 생성기 v2.8.5")
        print("=" * 80)
        print("📋 Multi-Level Header & Advanced Pivot Integration")
        print("-" * 80)
        
        # 시스템 구성 요소
        self.warehouses = [
            'AAA Storage',    # AAA 저장소
            'DSV Indoor',     # DSV 실내 창고
            'DSV Outdoor',    # DSV 실외 창고
            'DSV Al Markaz',  # DSV 알마르카즈
            'DSV MZP',        # DSV MZP 창고
            'Hauler Indoor',  # 운송업체 실내
            'MOSB'            # 해상 기지
        ]
        
        self.sites = [
            'AGI',    # AGI 현장
            'DAS',    # DAS 현장
            'MIR',    # MIR 현장
            'SHU'     # SHU 현장
        ]
        
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
        
        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 출력 파일명
        self.output_file = f"HVDC_Complete_System_Report_{self.timestamp}.xlsx"
        
        print(f"📊 창고 수: {len(self.warehouses)}개")
        print(f"🏭 현장 수: {len(self.sites)}개")
        print(f"📅 월별 추적: {len(self.months)}개월")
        print(f"📋 Flow Code: {len(self.flow_codes)}개 유형")
        
    def generate_sample_transaction_data(self, num_transactions=7573):
        """샘플 트랜잭션 데이터 생성 (실제 HVDC 데이터 패턴 기반)"""
        print(f"\n🔧 샘플 트랜잭션 데이터 생성 중... ({num_transactions:,}건)")
        
        # HVDC 프로젝트 실제 패턴 기반 데이터 생성
        vendors = ['HITACHI', 'SIMENSE', 'SAMSUNG', 'OTHERS']
        categories = ['HE', 'SIM', 'SCT', 'DGR', 'OTH']
        
        data = []
        for i in range(num_transactions):
            # 기본 정보
            case_no = f"HVDC{i+1:06d}"
            vendor = random.choice(vendors)
            category = random.choice(categories)
            
            # 위치 정보 (창고 및 현장)
            warehouse_data = {}
            for wh in self.warehouses:
                if random.random() < 0.3:  # 30% 확률로 창고 사용
                    warehouse_data[wh] = datetime.now() - timedelta(days=random.randint(1, 365))
            
            site_data = {}
            for site in self.sites:
                if random.random() < 0.15:  # 15% 확률로 현장 사용
                    site_data[site] = datetime.now() - timedelta(days=random.randint(1, 180))
            
            # Flow Code 계산
            wh_count = len(warehouse_data)
            has_mosb = 'MOSB' in warehouse_data
            
            if wh_count == 0:
                flow_code = 0  # Pre Arrival
            elif wh_count == 1 and not has_mosb:
                flow_code = 1  # Port → Site
            elif wh_count == 2 and not has_mosb:
                flow_code = 2  # Port → WH → Site
            elif has_mosb:
                flow_code = 3  # Port → WH → MOSB → Site
            else:
                flow_code = min(4, wh_count)  # 최대 4
            
            # 물류 정보
            weight = random.uniform(0.5, 50.0)
            cbm = random.uniform(0.1, 20.0)
            sqm = random.uniform(0.1, 15.0)
            pkg_count = random.randint(1, 100)
            
            # 데이터 레코드 생성
            record = {
                'Case No.': case_no,
                'Vendor': vendor,
                'Category': category,
                'Description': f'{vendor} {category} Equipment',
                'Weight': round(weight, 2),
                'CBM': round(cbm, 2),
                'SQM': round(sqm, 2),
                'PKG': pkg_count,
                'FLOW_CODE': flow_code,
                'FLOW_DESCRIPTION': self.flow_codes[flow_code],
                'WH_HANDLING': wh_count,
                'STATUS': 'ACTIVE' if flow_code > 0 else 'PRE_ARRIVAL',
                'CREATED_DATE': datetime.now() - timedelta(days=random.randint(1, 730)),
                'LAST_UPDATED': datetime.now()
            }
            
            # 창고 정보 추가
            for wh in self.warehouses:
                record[wh] = warehouse_data.get(wh, '')
            
            # 현장 정보 추가
            for site in self.sites:
                record[site] = site_data.get(site, '')
            
            data.append(record)
        
        df = pd.DataFrame(data)
        print(f"✅ 생성 완료: {len(df):,}건")
        return df
    
    def create_warehouse_monthly_sheet(self, df):
        """창고별 월별 입출고 시트 생성 (Multi-Level Header)"""
        print("\n📊 창고별 월별 입출고 시트 생성 중...")
        
        # Multi-level 컬럼 생성: [입고/출고] × [창고명들]
        level_0 = ['입고'] * len(self.warehouses) + ['출고'] * len(self.warehouses)
        level_1 = self.warehouses + self.warehouses
        
        multi_columns = pd.MultiIndex.from_arrays(
            [level_0, level_1], 
            names=['구분', 'Warehouse']
        )
        
        # 월별 데이터 생성
        monthly_data = []
        for month_idx, month in enumerate(self.months):
            row_data = []
            
            # 입고 데이터 (각 창고별)
            for warehouse in self.warehouses:
                # 해당 월에 창고를 사용한 케이스 수 계산
                warehouse_usage = df[df[warehouse] != '']
                if not warehouse_usage.empty:
                    # 월별 패턴 적용 (계절성 고려)
                    seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * month_idx / 12)
                    base_count = len(warehouse_usage) // 12
                    monthly_count = int(base_count * seasonal_factor * random.uniform(0.8, 1.2))
                    row_data.append(max(0, monthly_count))
                else:
                    row_data.append(0)
            
            # 출고 데이터 (각 창고별)
            for warehouse in self.warehouses:
                warehouse_usage = df[df[warehouse] != '']
                if not warehouse_usage.empty:
                    # 출고는 입고보다 약간 적게 (재고 유지)
                    inbound_count = row_data[self.warehouses.index(warehouse)]
                    outbound_count = int(inbound_count * random.uniform(0.7, 0.9))
                    row_data.append(max(0, outbound_count))
                else:
                    row_data.append(0)
            
            monthly_data.append(row_data)
        
        warehouse_df = pd.DataFrame(monthly_data, columns=multi_columns, index=self.months)
        print(f"✅ 창고별 월별 시트 생성 완료: {warehouse_df.shape}")
        return warehouse_df
    
    def create_site_monthly_sheet(self, df):
        """현장별 월별 입고재고 시트 생성 (Multi-Level Header)"""
        print("\n🏭 현장별 월별 입고재고 시트 생성 중...")
        
        # Multi-level 컬럼 생성: [입고/재고] × [현장명들]
        level_0 = ['입고'] * len(self.sites) + ['재고'] * len(self.sites)
        level_1 = self.sites + self.sites
        
        multi_columns = pd.MultiIndex.from_arrays(
            [level_0, level_1], 
            names=['구분', 'Site']
        )
        
        # 월별 데이터 생성
        monthly_data = []
        cumulative_inventory = {site: 0 for site in self.sites}
        
        for month_idx, month in enumerate(self.months):
            row_data = []
            
            # 입고 데이터 (각 현장별)
            for site in self.sites:
                site_usage = df[df[site] != '']
                if not site_usage.empty:
                    # 프로젝트 진행률 반영 (초기에 많이, 후반에 적게)
                    progress_factor = max(0.2, 1 - (month_idx / 12) * 0.6)
                    seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * month_idx / 12)
                    base_count = len(site_usage) // 12
                    monthly_inbound = int(base_count * progress_factor * seasonal_factor * random.uniform(0.8, 1.2))
                    monthly_inbound = max(0, monthly_inbound)
                    row_data.append(monthly_inbound)
                    
                    # 재고 누적
                    cumulative_inventory[site] += monthly_inbound
                else:
                    row_data.append(0)
            
            # 재고 데이터 (각 현장별)
            for site in self.sites:
                # 현장에서는 일부 소비 발생
                consumption = int(cumulative_inventory[site] * random.uniform(0.05, 0.15))
                cumulative_inventory[site] = max(0, cumulative_inventory[site] - consumption)
                row_data.append(cumulative_inventory[site])
            
            monthly_data.append(row_data)
        
        site_df = pd.DataFrame(monthly_data, columns=multi_columns, index=self.months)
        print(f"✅ 현장별 월별 시트 생성 완료: {site_df.shape}")
        return site_df
    
    def create_flow_code_analysis(self, df):
        """Flow Code 분석 시트 생성"""
        print("\n📋 Flow Code 분석 시트 생성 중...")
        
        # Flow Code별 집계
        flow_summary = df.groupby('FLOW_CODE').agg({
            'Case No.': 'count',
            'Weight': 'sum',
            'CBM': 'sum',
            'SQM': 'sum',
            'PKG': 'sum'
        }).reset_index()
        
        flow_summary.columns = ['Flow_Code', 'Count', 'Total_Weight', 'Total_CBM', 'Total_SQM', 'Total_PKG']
        
        # Flow Code 설명 추가
        flow_summary['Description'] = flow_summary['Flow_Code'].map(self.flow_codes)
        
        # 비율 계산
        total_count = flow_summary['Count'].sum()
        flow_summary['Percentage'] = (flow_summary['Count'] / total_count * 100).round(2)
        
        # 컬럼 순서 재정렬
        flow_summary = flow_summary[['Flow_Code', 'Description', 'Count', 'Percentage', 
                                   'Total_Weight', 'Total_CBM', 'Total_SQM', 'Total_PKG']]
        
        print(f"✅ Flow Code 분석 완료: {len(flow_summary)}개 코드")
        return flow_summary
    
    def create_pre_arrival_analysis(self, df):
        """Pre Arrival 상세 분석 시트 생성"""
        print("\n⏳ Pre Arrival 상세 분석 시트 생성 중...")
        
        # Pre Arrival 데이터 필터링
        pre_arrival_df = df[df['FLOW_CODE'] == 0].copy()
        
        if pre_arrival_df.empty:
            print("⚠️ Pre Arrival 데이터가 없습니다.")
            return pd.DataFrame({'Message': ['No Pre Arrival Data Available']})
        
        # 벤더별 Pre Arrival 분석
        vendor_analysis = pre_arrival_df.groupby('Vendor').agg({
            'Case No.': 'count',
            'Weight': 'sum',
            'CBM': 'sum',
            'SQM': 'sum',
            'PKG': 'sum'
        }).reset_index()
        
        vendor_analysis.columns = ['Vendor', 'Pre_Arrival_Count', 'Total_Weight', 'Total_CBM', 'Total_SQM', 'Total_PKG']
        
        # 카테고리별 Pre Arrival 분석
        category_analysis = pre_arrival_df.groupby('Category').agg({
            'Case No.': 'count',
            'Weight': 'sum'
        }).reset_index()
        
        category_analysis.columns = ['Category', 'Pre_Arrival_Count', 'Total_Weight']
        
        # 결합된 분석 결과 생성
        analysis_results = []
        
        # 요약 정보 추가
        analysis_results.append({
            'Analysis_Type': 'SUMMARY',
            'Category': 'Total Pre Arrival',
            'Count': len(pre_arrival_df),
            'Percentage': f"{len(pre_arrival_df)/len(df)*100:.1f}%",
            'Total_Weight': pre_arrival_df['Weight'].sum(),
            'Avg_Weight': pre_arrival_df['Weight'].mean()
        })
        
        # 벤더별 정보 추가
        for _, row in vendor_analysis.iterrows():
            analysis_results.append({
                'Analysis_Type': 'VENDOR',
                'Category': row['Vendor'],
                'Count': row['Pre_Arrival_Count'],
                'Percentage': f"{row['Pre_Arrival_Count']/len(pre_arrival_df)*100:.1f}%",
                'Total_Weight': row['Total_Weight'],
                'Avg_Weight': row['Total_Weight'] / row['Pre_Arrival_Count'] if row['Pre_Arrival_Count'] > 0 else 0
            })
        
        analysis_df = pd.DataFrame(analysis_results)
        print(f"✅ Pre Arrival 분석 완료: {len(pre_arrival_df)}건")
        return analysis_df
    
    def create_complete_excel_report(self):
        """5개 시트 포함 완전한 Excel 리포트 생성"""
        print(f"\n🚀 완전한 Excel 리포트 생성 시작...")
        print("=" * 60)
        
        # 1. 샘플 트랜잭션 데이터 생성
        df = self.generate_sample_transaction_data()
        
        # 2. 각 시트 데이터 생성
        print("\n📊 각 시트 데이터 생성 중...")
        warehouse_monthly = self.create_warehouse_monthly_sheet(df)
        site_monthly = self.create_site_monthly_sheet(df)
        flow_analysis = self.create_flow_code_analysis(df)
        pre_arrival_analysis = self.create_pre_arrival_analysis(df)
        
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
            
            # 시트 4: 창고별 월별 (Multi-Level Header)
            warehouse_monthly.to_excel(writer, sheet_name='창고별_월별_입출고_완전체계', merge_cells=True)
            print("✅ 시트 4: 창고별_월별_입출고_완전체계")
            
            # 시트 5: 현장별 월별 (Multi-Level Header)
            site_monthly.to_excel(writer, sheet_name='현장별_월별_입고재고_완전체계', merge_cells=True)
            print("✅ 시트 5: 현장별_월별_입고재고_완전체계")
        
        # 4. 결과 요약
        print("\n" + "=" * 60)
        print("🎉 HVDC Excel 시스템 생성 완료!")
        print("=" * 60)
        print(f"📁 출력 파일: {self.output_file}")
        print(f"📊 총 트랜잭션: {len(df):,}건")
        print(f"🏭 시트 수: 5개")
        print(f"📋 창고 수: {len(self.warehouses)}개")
        print(f"🎯 현장 수: {len(self.sites)}개")
        
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
            'warehouses': len(self.warehouses),
            'sites': len(self.sites),
            'flow_code_distribution': flow_dist.to_dict()
        }

def main():
    """메인 실행 함수"""
    print("🚀 HVDC Excel 시스템 생성기 v2.8.5 시작")
    print("Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini")
    print("=" * 80)
    
    # Excel 생성기 초기화
    generator = HVDCExcelSystemGenerator()
    
    # 완전한 Excel 리포트 생성
    result = generator.create_complete_excel_report()
    
    if result['status'] == 'SUCCESS':
        print("\n🔧 추천 명령어:")
        print(f"📁 파일 열기: start {result['output_file']}")
        print("📊 데이터 검증: python validate_excel_output.py")
        print("🎯 추가 분석: python analyze_hvdc_data.py")
        
        return result
    else:
        print("❌ Excel 생성 실패")
        return None

if __name__ == "__main__":
    main() 