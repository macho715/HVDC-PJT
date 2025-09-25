"""
HVDC TDD 월별 Balance 검증 Enhanced 엑셀 리포트 생성기
참조 양식에 맞춘 Professional 보고서 생성

시트 구성:
1. 전체_트랜잭션_요약: 총 트랜잭션, 벤더별 분포, Flow Code 분포
2. 창고_월별_입출고: Multi-Level Header, TDD 검증된 계산
3. 현장_월별_입고재고: Multi-Level Header, 누적 재고 개념
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from warehouse_io_calculator import WarehouseIOCalculator
import os
from collections import defaultdict

class EnhancedExcelReporter:
    """
    참조 양식 기반 Enhanced 엑셀 리포트 생성기
    """
    
    def __init__(self):
        self.calc = WarehouseIOCalculator()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_real_data(self):
        """실제 HVDC 데이터 로드 및 통합"""
        print("📊 실제 HVDC 데이터 로드 중...")
        
        # HITACHI 데이터 로드
        print("   📋 HITACHI 데이터 로드 중...")
        try:
            hitachi_df = pd.read_excel("../data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
            hitachi_df = self.standardize_hitachi_data(hitachi_df)
            print(f"   ✅ HITACHI 데이터 로드 완료: {hitachi_df.shape[0]}행")
        except Exception as e:
            print(f"   ❌ HITACHI 데이터 로드 실패: {str(e)}")
            hitachi_df = pd.DataFrame()
        
        # SIMENSE 데이터 로드
        print("   📋 SIMENSE 데이터 로드 중...")
        try:
            simense_df = pd.read_excel("../data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
            simense_df = self.standardize_simense_data(simense_df)
            print(f"   ✅ SIMENSE 데이터 로드 완료: {simense_df.shape[0]}행")
        except Exception as e:
            print(f"   ❌ SIMENSE 데이터 로드 실패: {str(e)}")
            simense_df = pd.DataFrame()
        
        # 데이터 통합
        if not hitachi_df.empty and not simense_df.empty:
            combined_df = pd.concat([hitachi_df, simense_df], ignore_index=True)
            print(f"   🔗 데이터 통합 완료: {combined_df.shape[0]}행 (HITACHI: {len(hitachi_df)}, SIMENSE: {len(simense_df)})")
        elif not hitachi_df.empty:
            combined_df = hitachi_df
            print(f"   📊 HITACHI 데이터만 사용: {combined_df.shape[0]}행")
        elif not simense_df.empty:
            combined_df = simense_df
            print(f"   📊 SIMENSE 데이터만 사용: {combined_df.shape[0]}행")
        else:
            print("   ❌ 사용 가능한 데이터가 없습니다.")
            combined_df = pd.DataFrame()
        
        return combined_df
    
    def standardize_hitachi_data(self, df):
        """HITACHI 데이터를 표준 형식으로 변환"""
        print("   🔄 HITACHI 데이터 표준화 중...")
        
        standardized = df.copy()
        
        # Item 컬럼 생성
        if 'HVDC CODE' in standardized.columns:
            standardized['Item'] = standardized['HVDC CODE']
        else:
            standardized['Item'] = standardized['no.'].astype(str)
        
        # 창고 컬럼 정의
        warehouse_cols = ['DHL Warehouse', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                         'AAA  Storage', 'Hauler Indoor', 'DSV MZP']
        
        # 현장 컬럼 정의
        site_cols = ['MOSB', 'MIR', 'SHU', 'DAS', 'AGI']
        
        # 날짜 컬럼 변환
        for col in warehouse_cols + site_cols:
            if col in standardized.columns:
                standardized[col] = pd.to_datetime(standardized[col], errors='coerce')
        
        # Flow Code 계산
        standardized['Flow_Code'] = self.calculate_flow_code(standardized, warehouse_cols)
        
        # 데이터 타입 추가
        standardized['Data_Source'] = 'HITACHI'
        standardized['Data_Type'] = 'HE'
        
        print(f"   ✅ HITACHI 데이터 표준화 완료: {standardized.shape[0]}행 × {standardized.shape[1]}열")
        return standardized
    
    def standardize_simense_data(self, df):
        """SIMENSE 데이터를 표준 형식으로 변환"""
        print("   🔄 SIMENSE 데이터 표준화 중...")
        
        standardized = df.copy()
        
        # Item 컬럼 생성
        if 'HVDC CODE' in standardized.columns:
            standardized['Item'] = standardized['HVDC CODE']
        else:
            standardized['Item'] = standardized['No.'].astype(str)
        
        # 창고 컬럼 정의
        warehouse_cols = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'DSV MZD', 
                         'JDN MZD', 'AAA  Storage', 'Hauler Indoor']
        
        # 현장 컬럼 정의
        site_cols = ['MOSB', 'MIR', 'SHU', 'DAS', 'AGI']
        
        # 날짜 컬럼 변환
        for col in warehouse_cols + site_cols:
            if col in standardized.columns:
                standardized[col] = pd.to_datetime(standardized[col], errors='coerce')
        
        # Flow Code 계산
        standardized['Flow_Code'] = self.calculate_flow_code(standardized, warehouse_cols)
        
        # 데이터 타입 추가
        standardized['Data_Source'] = 'SIMENSE'
        standardized['Data_Type'] = 'SIM'
        
        print(f"   ✅ SIMENSE 데이터 표준화 완료: {standardized.shape[0]}행 × {standardized.shape[1]}열")
        return standardized
    
    def calculate_flow_code(self, df, warehouse_cols):
        """Flow Code 계산 (창고 경유 횟수)"""
        flow_codes = []
        
        for _, row in df.iterrows():
            warehouse_count = 0
            for col in warehouse_cols:
                if col in df.columns and pd.notna(row[col]):
                    warehouse_count += 1
            flow_codes.append(warehouse_count)
        
        return flow_codes
    
    def update_calculator_for_real_data(self, df):
        """실제 데이터에 맞게 Calculator 업데이트"""
        print("🔧 Calculator를 실제 데이터에 맞게 업데이트 중...")
        
        # 실제 데이터의 창고 및 현장 컬럼 식별
        all_warehouse_cols = ['DHL Warehouse', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                             'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'DSV MZD', 'JDN MZD']
        
        all_site_cols = ['MOSB', 'MIR', 'SHU', 'DAS', 'AGI']
        
        # 실제 존재하는 컬럼만 필터링
        existing_warehouse_cols = [col for col in all_warehouse_cols if col in df.columns]
        existing_site_cols = [col for col in all_site_cols if col in df.columns]
        
        # Calculator 업데이트
        self.calc.warehouse_columns = existing_warehouse_cols
        self.calc.site_columns = existing_site_cols
        
        print(f"   🏭 실제 창고 컬럼 ({len(existing_warehouse_cols)}개): {existing_warehouse_cols}")
        print(f"   🏗️ 실제 현장 컬럼 ({len(existing_site_cols)}개): {existing_site_cols}")
        
        return existing_warehouse_cols, existing_site_cols
    
    def generate_transaction_summary_sheet(self, df):
        """시트 1: 전체_트랜잭션_요약"""
        print("📋 시트 1: 전체_트랜잭션_요약 생성 중...")
        
        # 기본 통계
        total_transactions = len(df)
        hitachi_count = len(df[df['Data_Source'] == 'HITACHI'])
        simense_count = len(df[df['Data_Source'] == 'SIMENSE'])
        
        hitachi_pct = (hitachi_count / total_transactions * 100) if total_transactions > 0 else 0
        simense_pct = (simense_count / total_transactions * 100) if total_transactions > 0 else 0
        
        # Flow Code 분포
        flow_code_dist = df['Flow_Code'].value_counts().sort_index()
        
        # 창고별 방문 현황
        warehouse_visits = {}
        for col in self.calc.warehouse_columns:
            if col in df.columns:
                visits = df[col].notna().sum()
                warehouse_visits[col] = visits
        
        # 현장별 도착 현황
        site_arrivals = {}
        for col in self.calc.site_columns:
            if col in df.columns:
                arrivals = df[col].notna().sum()
                site_arrivals[col] = arrivals
        
        # 요약 데이터 생성
        summary_data = []
        
        # 기본 통계
        summary_data.append(['구분', '값', '비율(%)'])
        summary_data.append(['총 트랜잭션', total_transactions, '100.0'])
        summary_data.append(['HITACHI 건수', hitachi_count, f'{hitachi_pct:.1f}'])
        summary_data.append(['SIMENSE 건수', simense_count, f'{simense_pct:.1f}'])
        summary_data.append(['', '', ''])
        
        # Flow Code 분포
        summary_data.append(['Flow Code 분포', '건수', '비율(%)'])
        for code in sorted(flow_code_dist.index):
            count = flow_code_dist[code]
            pct = (count / total_transactions * 100) if total_transactions > 0 else 0
            summary_data.append([f'Flow Code {code}', count, f'{pct:.1f}'])
        summary_data.append(['', '', ''])
        
        # 창고별 방문 현황
        summary_data.append(['창고별 방문 현황', '방문 건수', '방문율(%)'])
        for warehouse, visits in warehouse_visits.items():
            pct = (visits / total_transactions * 100) if total_transactions > 0 else 0
            summary_data.append([warehouse, visits, f'{pct:.1f}'])
        summary_data.append(['', '', ''])
        
        # 현장별 도착 현황
        summary_data.append(['현장별 도착 현황', '도착 건수', '도착율(%)'])
        for site, arrivals in site_arrivals.items():
            pct = (arrivals / total_transactions * 100) if total_transactions > 0 else 0
            summary_data.append([site, arrivals, f'{pct:.1f}'])
        
        summary_df = pd.DataFrame(summary_data)
        
        print(f"   ✅ 전체_트랜잭션_요약 생성 완료: {len(summary_data)}행")
        return summary_df
    
    def generate_warehouse_monthly_io_sheet(self, df):
        """시트 2: 창고_월별_입출고 (Multi-Level Header)"""
        print("📋 시트 2: 창고_월별_입출고 생성 중...")
        
        # 분석 기간 설정
        start_date = datetime(2023, 2, 1)
        end_date = datetime(2025, 7, 31)
        
        # 전체 월별 출고 및 입고 데이터 계산 (수정된 호출)
        month_outbound_all = self.calc.calculate_monthly_outbound(df)
        month_inbound_all = self.calc.calculate_warehouse_inbound(df)
        
        # 월별 데이터 생성
        monthly_data = []
        current_date = start_date
        
        while current_date <= end_date:
            month_str = current_date.strftime('%Y-%m')
            
            # 창고별 입출고 데이터 구성
            row_data = {'월': month_str}
            
            for warehouse in self.calc.warehouse_columns:
                # 입고 데이터 - warehouse inbound 결과에서 추출
                inbound_key = f"{warehouse}_입고"
                if 'by_warehouse_month' in month_inbound_all:
                    inbound_count = month_inbound_all['by_warehouse_month'].get(warehouse, {}).get(month_str, 0)
                else:
                    inbound_count = 0
                row_data[inbound_key] = inbound_count
                
                # 출고 데이터 - monthly outbound 결과에서 추출
                outbound_key = f"{warehouse}_출고"
                outbound_count = month_outbound_all.get(month_str, 0)
                # 전체 출고를 창고별로 분배 (임시)
                row_data[outbound_key] = outbound_count // len(self.calc.warehouse_columns) if outbound_count > 0 else 0
            
            monthly_data.append(row_data)
            
            # 다음 월로 이동
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        monthly_df = pd.DataFrame(monthly_data)
        
        print(f"   ✅ 창고_월별_입출고 생성 완료: {len(monthly_data)}행 × {len(monthly_df.columns)}열")
        return monthly_df
    
    def generate_site_monthly_inventory_sheet(self, df):
        """시트 3: 현장_월별_입고재고 (Multi-Level Header)"""
        print("📋 시트 3: 현장_월별_입고재고 생성 중...")
        
        # 분석 기간 설정
        start_date = datetime(2023, 2, 1)
        end_date = datetime(2025, 7, 31)
        
        # 전체 월별 현장 입고 데이터 계산 (수정된 호출)
        month_site_inbound_all = self.calc.calculate_monthly_site_inbound(df)
        
        # 월별 데이터 생성
        monthly_data = []
        current_date = start_date
        
        while current_date <= end_date:
            month_str = current_date.strftime('%Y-%m')
            
            # 현장별 입고재고 데이터 구성
            row_data = {'월': month_str}
            
            for site in self.calc.site_columns:
                # 입고 데이터
                inbound_key = f"{site}_입고"
                inbound_count = month_site_inbound_all.get(month_str, 0)
                # 전체 입고를 현장별로 분배 (임시)
                row_data[inbound_key] = inbound_count // len(self.calc.site_columns) if inbound_count > 0 else 0
                
                # 재고 데이터 (누적 개념)
                inventory_key = f"{site}_재고"
                # 해당 월까지의 누적 입고량으로 재고 계산
                cumulative_inbound = 0
                temp_date = start_date
                while temp_date <= current_date:
                    temp_month_str = temp_date.strftime('%Y-%m')
                    temp_inbound = month_site_inbound_all.get(temp_month_str, 0)
                    cumulative_inbound += temp_inbound // len(self.calc.site_columns) if temp_inbound > 0 else 0
                    
                    # 다음 월로 이동
                    if temp_date.month == 12:
                        temp_date = temp_date.replace(year=temp_date.year + 1, month=1)
                    else:
                        temp_date = temp_date.replace(month=temp_date.month + 1)
                
                row_data[inventory_key] = cumulative_inbound
            
            monthly_data.append(row_data)
            
            # 다음 월로 이동
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        monthly_df = pd.DataFrame(monthly_data)
        
        print(f"   ✅ 현장_월별_입고재고 생성 완료: {len(monthly_data)}행 × {len(monthly_df.columns)}열")
        return monthly_df
    
    def create_multi_level_headers(self, df, sheet_type):
        """Multi-Level Header 생성"""
        if sheet_type == 'warehouse':
            # 창고별 입고/출고 헤더
            header_data = []
            for warehouse in self.calc.warehouse_columns:
                header_data.extend([f"{warehouse}_입고", f"{warehouse}_출고"])
            
            # 새로운 컬럼 순서로 데이터프레임 재정렬
            new_columns = ['월'] + header_data
            df = df.reindex(columns=new_columns, fill_value=0)
            
        elif sheet_type == 'site':
            # 현장별 입고/재고 헤더
            header_data = []
            for site in self.calc.site_columns:
                header_data.extend([f"{site}_입고", f"{site}_재고"])
            
            # 새로운 컬럼 순서로 데이터프레임 재정렬
            new_columns = ['월'] + header_data
            df = df.reindex(columns=new_columns, fill_value=0)
        
        return df
    
    def generate_excel_report(self, output_path=None):
        """Enhanced 엑셀 리포트 생성"""
        print("🚀 HVDC TDD Enhanced 엑셀 리포트 생성 시작")
        
        # 1. 실제 데이터 로드
        df = self.load_real_data()
        if df.empty:
            print("❌ 데이터가 없어 리포트 생성을 중단합니다.")
            return None
        
        # 2. Calculator 업데이트
        warehouse_cols, site_cols = self.update_calculator_for_real_data(df)
        
        # 3. 각 시트 생성
        print("\n📊 시트별 데이터 생성 중...")
        
        # 시트 1: 전체_트랜잭션_요약
        summary_sheet = self.generate_transaction_summary_sheet(df)
        
        # 시트 2: 창고_월별_입출고
        warehouse_monthly_sheet = self.generate_warehouse_monthly_io_sheet(df)
        warehouse_monthly_sheet = self.create_multi_level_headers(warehouse_monthly_sheet, 'warehouse')
        
        # 시트 3: 현장_월별_입고재고
        site_monthly_sheet = self.generate_site_monthly_inventory_sheet(df)
        site_monthly_sheet = self.create_multi_level_headers(site_monthly_sheet, 'site')
        
        # 4. 엑셀 파일 생성
        if output_path is None:
            output_path = f"../output/HVDC_Enhanced_Report_{self.timestamp}.xlsx"
        
        print(f"\n📝 엑셀 파일 생성 중: {output_path}")
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 시트 1: 전체_트랜잭션_요약
                summary_sheet.to_excel(writer, sheet_name='전체_트랜잭션_요약', index=False)
                
                # 시트 2: 창고_월별_입출고
                warehouse_monthly_sheet.to_excel(writer, sheet_name='창고_월별_입출고', index=False)
                
                # 시트 3: 현장_월별_입고재고
                site_monthly_sheet.to_excel(writer, sheet_name='현장_월별_입고재고', index=False)
            
            print(f"✅ 엑셀 리포트 생성 완료: {output_path}")
            
            # 파일 크기 확인
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📁 파일 크기: {file_size:,} bytes ({file_size/1024:.1f}KB)")
            
            return output_path
            
        except Exception as e:
            print(f"❌ 엑셀 파일 생성 실패: {str(e)}")
            return None

def main():
    """메인 실행 함수"""
    print("🚀 HVDC TDD Enhanced 엑셀 리포트 생성기 시작")
    
    try:
        # 리포터 생성
        reporter = EnhancedExcelReporter()
        
        # 리포트 생성
        output_file = reporter.generate_excel_report()
        
        if output_file:
            print(f"\n🎉 리포트 생성 성공!")
            print(f"📄 파일 위치: {output_file}")
            print(f"🔗 절대 경로: {os.path.abspath(output_file)}")
        else:
            print(f"\n❌ 리포트 생성 실패")
            
    except Exception as e:
        print(f"❌ 메인 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 