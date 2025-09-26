#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini: 실제 데이터 기반 월별/위치별 입고 및 재고 집계기
warehouse_site_monthly_report.py 로직을 기반으로 재작성됨.
"""

import pandas as pd
from datetime import datetime
import os

class SiteMonthlyAggregator:
    def __init__(self, base_path='HVDC_PJT/hvdc_macho_gpt/WAREHOUSE/data'):
        """초기화"""
        self.base_path = base_path
        self.file_paths = {
            'HITACHI': os.path.join(self.base_path, 'HVDC WAREHOUSE_HITACHI(HE).xlsx'),
            'SIMENSE': os.path.join(self.base_path, 'HVDC WAREHOUSE_SIMENSE(SIM).xlsx')
        }
        self.output_dir = 'HVDC_PJT/MACHO_통합관리_20250702_205301/01_원본파일'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load_data(self):
        """HITACHI 및 SIMENSE 데이터 로드 및 통합"""
        try:
            df_hitachi = pd.read_excel(self.file_paths['HITACHI'])
            df_simense = pd.read_excel(self.file_paths['SIMENSE'])
            df_hitachi['Vendor'] = 'HITACHI'
            df_simense['Vendor'] = 'SIMENSE'
            return pd.concat([df_hitachi, df_simense], ignore_index=True)
        except FileNotFoundError as e:
            print(f"❌ 파일 로드 실패: {e}. 경로를 확인하세요.")
            return None

    @staticmethod
    def classify_location(row):
        """행 데이터를 기반으로 위치(Site/Warehouse) 분류"""
        # 현장 컬럼 우선 확인
        site_cols = ['AGI', 'DAS', 'MIR', 'SHU']
        for col in site_cols:
            if col in row.index and pd.notna(row[col]):
                return 'Site', col

        # 창고 컬럼 확인
        warehouse_cols = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'AAA  Storage']
        for col in warehouse_cols:
             if col in row.index and pd.notna(row[col]):
                return 'Warehouse', col

        # Status_Location에서 2차 확인
        if 'Status_Location' in row.index and pd.notna(row['Status_Location']):
            loc = str(row['Status_Location']).upper()
            if any(site in loc for site in site_cols):
                return 'Site', row['Status_Location']
            else:
                return 'Warehouse', row['Status_Location']
        
        return '기타', '알 수 없음'

    @staticmethod
    def get_first_valid_date(row, date_columns):
        """여러 날짜 컬럼에서 첫 번째 유효한 날짜를 찾아 반환"""
        for col in date_columns:
            if pd.notna(row[col]):
                return pd.to_datetime(row[col], errors='coerce')
        return pd.NaT

    def process_data(self, df):
        """데이터 처리: 위치 분류, 날짜 추출, 월별 집계"""
        # 날짜 컬럼 식별
        date_columns = [col for col in df.columns if any(x in col.upper() for x in ['DSV', 'AGI', 'DAS', 'MIR', 'SHU', 'HAULER', 'AAA', 'JDN'])]

        # 위치 및 날짜 정보 추가
        df[['구분', 'Location']] = df.apply(self.classify_location, axis=1, result_type='expand')
        df['입고일'] = df.apply(self.get_first_valid_date, axis=1, date_columns=date_columns)
        
        # 유효한 입고일이 있는 데이터만 필터링
        df = df.dropna(subset=['입고일'])
        df['입고월'] = df['입고일'].dt.to_period('M').astype(str)
        
        # Pkg 컬럼이 없을 경우 1로 간주
        if 'Pkg' not in df.columns:
            df['Pkg'] = 1
            
        # 입고와 실제출고 분리
        df['입고'] = df['Pkg'].apply(lambda x: x if x > 0 else 0)
        df['실제출고'] = df['Pkg'].apply(lambda x: -x if x < 0 else 0) # 출고는 양수로 표현

        # 월별 입고량/출고량 집계
        monthly_inbound = df.pivot_table(
            index=['구분', 'Location'], columns='입고월', values='입고', aggfunc='sum', fill_value=0
        )
        monthly_outbound = df.pivot_table(
            index=['구분', 'Location'], columns='입고월', values='실제출고', aggfunc='sum', fill_value=0
        )

        # 누적 재고 계산 (재고변동의 누적합)
        df_sorted = df.sort_values(by=['구분', 'Location', '입고일'])
        df_sorted['재고변동'] = df_sorted['입고'] - df_sorted['실제출고']
        df_sorted['누적재고'] = df_sorted.groupby(['구분', 'Location'])['재고변동'].cumsum()
        
        cumulative_stock = df_sorted.pivot_table(
            index=['구분', 'Location'],
            columns='입고월',
            values='누적재고',
            aggfunc='last',
            fill_value=0
        )
        # 이전 월의 마지막 누적값을 채우기
        cumulative_stock = cumulative_stock.ffill(axis=1)

        return monthly_inbound, monthly_outbound, cumulative_stock
        
    def generate_report(self):
        """요청 이미지와 동일한 구조의 분리된 리포트 생성"""
        df = self.load_data()
        if df is None:
            return

        monthly_inbound_pivot, monthly_outbound_pivot, cumulative_stock_pivot = self.process_data(df)

        # --- 1. 창고(Warehouse) 리포트 생성 ---
        wh_inbound = monthly_inbound_pivot[monthly_inbound_pivot.index.get_level_values('구분') == 'Warehouse']
        wh_outbound = monthly_outbound_pivot[monthly_outbound_pivot.index.get_level_values('구분') == 'Warehouse']

        # Multi-level column 생성 (수정된 방식)
        wh_inbound.columns = pd.MultiIndex.from_tuples([('입고', col) for col in wh_inbound.columns])
        wh_outbound.columns = pd.MultiIndex.from_tuples([('출고', col) for col in wh_outbound.columns])
        
        # 행 인덱스에서 '구분' 레벨 제거 및 재구성
        df_report_wh = pd.concat([wh_inbound.droplevel('구분'), wh_outbound.droplevel('구분')], axis=1).fillna(0).astype(int)
        df_report_wh = df_report_wh.T.reindex(['입고', '출고'], level=0).T # 순서 고정

        
        # --- 2. 현장(Site) 리포트 생성 ---
        site_inbound = monthly_inbound_pivot[monthly_inbound_pivot.index.get_level_values('구분') == 'Site']
        site_stock = cumulative_stock_pivot[cumulative_stock_pivot.index.get_level_values('구분') == 'Site']

        # Multi-level column 생성 (수정된 방식)
        site_inbound.columns = pd.MultiIndex.from_tuples([('입고', col) for col in site_inbound.columns])
        site_stock.columns = pd.MultiIndex.from_tuples([('재고', col) for col in site_stock.columns])
        
        # 행 인덱스에서 '구분' 레벨 제거 및 재구성
        df_report_site = pd.concat([site_inbound.droplevel('구분'), site_stock.droplevel('구분')], axis=1).fillna(0).astype(int)
        df_report_site = df_report_site.T.reindex(['입고', '재고'], level=0).T # 순서 고정

        # 보고서 파일명
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = os.path.join(self.output_dir, f'MACHO_최종_월별리포트_{timestamp}.xlsx')

        # 합계 행 추가
        df_report_wh.loc['Total'] = df_report_wh.sum().astype(int)
        df_report_site.loc['합계'] = df_report_site.sum().astype(int)

        with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
            df_report_wh.T.to_excel(writer, sheet_name='창고_월별_입출고')
            df_report_site.T.to_excel(writer, sheet_name='현장_월별_입고재고')
            
            # 요약 시트 추가
            summary_df = pd.DataFrame({
                '항목': ['리포트 유형', '생성 시간', '데이터 소스'],
                '값': ['최종 월별 리포트 (분리형)', timestamp, self.base_path]
            })
            summary_df.to_excel(writer, sheet_name='리포트_정보', index=False)

        print(f"✅ 최종 월별 리포트 (분리형) 생성 완료: {output_filename}")
        return output_filename

def main():
    """메인 실행 함수"""
    print("🚀 실제 데이터 기반 월별 입고/재고 집계 시작")
    aggregator = SiteMonthlyAggregator()
    aggregator.generate_report()
    print("✅ 작업 완료")

if __name__ == "__main__":
    main() 