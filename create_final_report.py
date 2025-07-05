#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini: 최종 데이터 기반 월별 리포트 생성기
- 입력: complete_transaction_data...py 가 생성한 최종 트랜잭션 데이터
- 출력: 사용자가 요청한 이미지 형식과 100% 동일한 Excel 리포트
"""

import pandas as pd
from datetime import datetime
import os
import glob

class FinalReportGenerator:
    def __init__(self):
        """초기화"""
        self.source_dir = '.' # 현재 디렉토리에서 파일을 찾도록 수정
        self.output_dir = 'HVDC_PJT/MACHO_통합관리_20250702_205301/02_통합결과'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def find_latest_source_file(self):
        """가장 최신의 전체 트랜잭션 데이터 파일을 찾습니다."""
        pattern = os.path.join(self.source_dir, 'MACHO_WH_HANDLING_전체트랜잭션데이터_*.xlsx')
        files = glob.glob(pattern)
        if not files:
            print(f"❌ 원본 트랜잭션 파일을 찾을 수 없습니다: {pattern}")
            return None
        latest_file = max(files, key=os.path.getmtime)
        print(f"✅ 최신 원본 파일 사용: {os.path.basename(latest_file)}")
        return latest_file

    def load_data(self):
        """최종 트랜잭션 데이터 로드"""
        source_file = self.find_latest_source_file()
        if source_file:
            return pd.read_excel(source_file)
        return None

    @staticmethod
    def classify_location(row):
        """행 데이터를 기반으로 위치(Site/Warehouse) 분류"""
        # 이 로직은 실제 데이터의 컬럼 구조에 따라 조정 필요
        site_cols = ['AGI', 'DAS', 'MIR', 'SHU']
        wh_cols = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'AAA  Storage']
        
        # 날짜가 있는 첫번째 컬럼을 기준으로 위치를 찾음
        for col in wh_cols + site_cols:
            if col in row.index and pd.notna(row[col]):
                if col in site_cols:
                    return 'Site', col
                else:
                    return 'Warehouse', col
        return '기타', '알 수 없음'

    @staticmethod
    def get_first_valid_date(row):
        date_columns = [col for col in row.index if any(x in str(col).upper() for x in ['DSV', 'AGI', 'DAS', 'MIR', 'SHU', 'HAULER', 'AAA', 'JDN'])]
        for col in date_columns:
            if pd.notna(row[col]):
                return pd.to_datetime(row[col], errors='coerce')
        return pd.NaT

    def process_data(self, df):
        """
        데이터 처리 로직 V2: Melt와 흐름 추적을 통해 입/출고를 명확히 구분
        1. 데이터를 long-format으로 변환 (Melt)
        2. 케이스별로 날짜순 정렬하여 이동 경로 추적
        3. 이동이 발생하면 이전 위치에서 '출고', 다음 위치에서 '입고'를 생성
        """
        wh_cols = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'AAA  Storage', 'JDN']
        site_cols = ['AGI', 'DAS', 'MIR', 'SHU']
        location_cols = wh_cols + site_cols
        
        # 실제 데이터에 존재하는 위치 컬럼만 사용
        value_cols = [col for col in location_cols if col in df.columns]
        
        # 식별자 컬럼 설정
        case_col = 'Case No.'
        if case_col not in df.columns and 'S/No' in df.columns:
            case_col = 'S/No'
        
        pkg_col = 'Pkg'
        if pkg_col not in df.columns:
            df[pkg_col] = 1

        # id_vars에서 pkg_col 제외
        id_vars = [c for c in [case_col, 'Vendor Name'] if c in df.columns]

        # 데이터 증폭 방지를 위한 고유 ID 생성
        df['__temp_id__'] = range(len(df))
        id_vars_with_temp = id_vars + ['__temp_id__']

        # 데이터 구조 변환 (Wide to Long)
        melted = df.melt(id_vars=id_vars_with_temp, value_vars=value_cols, var_name='Location', value_name='Date')
        melted.dropna(subset=['Date'], inplace=True)
        
        # Pkg 정보 다시 매핑 (고유 ID 사용)
        melted = pd.merge(melted, df[id_vars_with_temp + [pkg_col]], on=id_vars_with_temp, how='left')
        melted.drop(columns=['__temp_id__'], inplace=True)

        melted['Date'] = pd.to_datetime(melted['Date'], errors='coerce')
        melted.dropna(subset=['Date'], inplace=True)
        melted.sort_values(by=[case_col, 'Date'], inplace=True)

        # 모든 이벤트를 '입고'로 기록
        inbounds = melted.copy()
        inbounds.rename(columns={pkg_col: '입고'}, inplace=True)
        inbounds['출고'] = 0

        # '출고' 이벤트 생성
        # 그룹 내에서 다음 이벤트가 있으면 현재 위치에서 출고된 것임
        if not melted.empty:
            outbounds = melted.groupby(case_col).apply(lambda g: g.iloc[:-1]).reset_index(drop=True)
            if not outbounds.empty:
                outbounds.rename(columns={pkg_col: '출고'}, inplace=True)
                outbounds['입고'] = 0
                # 출고일자는 다음 입고일자와 동일
                outbounds['Date'] = melted.groupby(case_col)['Date'].shift(-1).dropna().values
            else:
                outbounds = pd.DataFrame(columns=inbounds.columns) # No outbounds, create empty DF with same columns
        else:
            outbounds = pd.DataFrame(columns=inbounds.columns)


        # 입고, 출고 데이터 통합
        final_df = pd.concat([inbounds[['Date', 'Location', '입고', '출고']], outbounds[['Date', 'Location', '입고', '출고']]], ignore_index=True)
        final_df.fillna(0, inplace=True)

        # 위치 타입(창고/현장) 분류
        def classify_type(location):
            if location in site_cols: return 'Site'
            if location in wh_cols: return 'Warehouse'
            return '기타'
        final_df['구분'] = final_df['Location'].apply(classify_type)
        
        # 비즈니스 규칙 적용: 현장(Site)에서는 출고가 없음
        final_df.loc[(final_df['구분'] == 'Site') & (final_df['출고'] > 0), '출고'] = 0

        # 재고 계산
        final_df['입고월'] = pd.to_datetime(final_df['Date']).dt.to_period('M').astype(str)
        final_df.sort_values(by=['구분', 'Location', 'Date'], inplace=True)
        final_df['재고변동'] = final_df['입고'] - final_df['출고']
        final_df['누적재고'] = final_df.groupby(['구분', 'Location'])['재고변동'].cumsum()
        
        return final_df

    def create_report(self, original_df, processed_df):
        """요청 이미지와 동일한 리포트 생성"""
        # --- 창고 리포트 (가공된 데이터 사용) ---
        wh_df = processed_df[processed_df['구분'] == 'Warehouse']
        wh_inbound = wh_df.pivot_table(index='입고월', columns='Location', values='입고', aggfunc='sum', fill_value=0)
        wh_outbound = wh_df.pivot_table(index='입고월', columns='Location', values='출고', aggfunc='sum', fill_value=0)
        
        wh_inbound.columns = pd.MultiIndex.from_product([['입고'], wh_inbound.columns])
        wh_outbound.columns = pd.MultiIndex.from_product([['출고'], wh_outbound.columns])
        
        df_report_wh = pd.concat([wh_inbound, wh_outbound], axis=1).sort_index(axis=1)
        df_report_wh.loc['Total'] = df_report_wh.sum().astype(int)

        # --- 현장 리포트 ---
        site_df = processed_df[processed_df['구분'] == 'Site']
        site_inbound = site_df.pivot_table(index='입고월', columns='Location', values='입고', aggfunc='sum', fill_value=0)
        site_stock = site_df.pivot_table(index='입고월', columns='Location', values='누적재고', aggfunc='last', fill_value=0).ffill()

        site_inbound.columns = pd.MultiIndex.from_product([['입고'], site_inbound.columns])
        site_stock.columns = pd.MultiIndex.from_product([['재고'], site_stock.columns])

        df_report_site = pd.concat([site_inbound, site_stock], axis=1).sort_index(axis=1)
        if not df_report_site.empty:
            df_report_site.loc['합계'] = df_report_site.iloc[:-1].sum().astype(int) # 누적재고 합계는 의미 없으므로 제외

        # --- Excel 저장 ---
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = os.path.join(self.output_dir, f'MACHO_Final_Report_{timestamp}.xlsx')
        
        with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
            original_df.to_excel(writer, sheet_name='전체_트랜잭션_데이터', index=False)
            df_report_wh.to_excel(writer, sheet_name='창고_월별_입출고')
            df_report_site.to_excel(writer, sheet_name='현장_월별_입고재고')

        print(f"✅ 최종 리포트 생성 완료: {output_filename}")
        return output_filename

    def run(self):
        """전체 실행"""
        original_df = self.load_data()
        if original_df is not None:
            # 원본을 유지하기 위해 복사본을 전달
            processed_df = self.process_data(original_df.copy())
            self.create_report(original_df, processed_df)

def main():
    print("🚀 최종 리포트 생성 시작")
    generator = FinalReportGenerator()
    generator.run()
    print("✅ 작업 완료")

if __name__ == "__main__":
    main() 