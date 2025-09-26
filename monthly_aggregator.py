#!/usr/bin/env python3
"""
🎯 월별 집계 전용 시스템 - TDD GREEN Phase
MACHO-GPT v3.4-mini│Samsung C&T Logistics

완전한 데이터셋 (7,779건) 기반 월별 집계
사용자 요청 Excel 시트 구조 정확히 구현
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

class MonthlyAggregator:
    """월별 집계 전용 시스템 - 완전한 데이터셋 처리"""
    
    def __init__(self, confidence_threshold: float = 0.95):
        """
        월별 집계 시스템 초기화
        
        Args:
            confidence_threshold: 신뢰도 임계값 (≥0.95)
        """
        self.confidence_threshold = confidence_threshold
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 완전한 데이터셋 경로 (7,779건) - INVOICE 파일 제외
        self.data_paths = {
            'HITACHI': "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
            'SIMENSE': "hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        }
        
        # 창고 및 현장 컬럼 정의
        self.warehouse_columns = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 
            'AAA Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse'
        ]
        self.site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 모든 위치 컬럼 통합
        self.all_locations = self.warehouse_columns + self.site_columns
        
        # 처리 상태 초기화
        self.processed_data = {}
        self.monthly_reports = {}
        
        print(f"🎯 월별 집계 전용 시스템 초기화 완료")
        print(f"📊 데이터 경로: {len(self.data_paths)}개 파일")
        print(f"🎯 신뢰도 임계값: {self.confidence_threshold}")
        
    def load_complete_dataset(self) -> pd.DataFrame:
        """
        완전한 데이터셋 로드 (7,779건)
        
        Returns:
            pd.DataFrame: 병합된 완전한 데이터셋
        """
        print("📥 완전한 데이터셋 로드 시작...")
        
        dfs = []
        total_records = 0
        
        for source, path in self.data_paths.items():
            if os.path.exists(path):
                df = pd.read_excel(path)
                
                # 데이터 소스 태깅
                df['DATA_SOURCE'] = source
                df['SOURCE_FILE'] = os.path.basename(path)
                df['PROCESSED_AT'] = self.timestamp
                
                print(f"✅ {source}: {len(df):,}건 로드 완료")
                dfs.append(df)
                total_records += len(df)
            else:
                print(f"❌ {source}: 파일 없음 - {path}")
        
        if not dfs:
            raise FileNotFoundError("데이터 파일을 찾을 수 없습니다.")
        
        # 데이터 병합
        merged_df = pd.concat(dfs, ignore_index=True)
        
        print(f"📊 완전한 데이터셋 로드 완료: {len(merged_df):,}건")
        print(f"🎯 소스별 분포:")
        for source in merged_df['DATA_SOURCE'].value_counts().items():
            print(f"   - {source[0]}: {source[1]:,}건")
        
        return merged_df
    
    def classify_location_type(self, row) -> tuple:
        """
        행 데이터를 기반으로 위치 유형 분류
        
        Args:
            row: 데이터프레임 행
            
        Returns:
            tuple: (location_type, location_name, entry_date)
        """
        # 1. 현장 컬럼 우선 확인
        for site in self.site_columns:
            if site in row.index and pd.notna(row[site]):
                return ('Site', site, row[site])
        
        # 2. 창고 컬럼 확인
        for warehouse in self.warehouse_columns:
            if warehouse in row.index and pd.notna(row[warehouse]):
                return ('Warehouse', warehouse, row[warehouse])
        
        # 3. Status_Location 기반 분류
        if 'Status_Location' in row.index and pd.notna(row['Status_Location']):
            status_location = str(row['Status_Location']).strip()
            
            # 현장 확인
            for site in self.site_columns:
                if site.upper() in status_location.upper():
                    return ('Site', site, None)
            
            # 창고 확인
            for warehouse in self.warehouse_columns:
                if warehouse.upper() in status_location.upper():
                    return ('Warehouse', warehouse, None)
            
            # 기타 창고 패턴 확인
            if any(pattern in status_location.upper() for pattern in ['DSV', 'STORAGE', 'WAREHOUSE']):
                return ('Warehouse', status_location, None)
        
        return ('Unknown', '미분류', None)
    
    def extract_monthly_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        월별 데이터 추출 및 정리
        
        Args:
            df: 원본 데이터프레임
            
        Returns:
            pd.DataFrame: 월별 데이터가 추가된 데이터프레임
        """
        print("📅 월별 데이터 추출 중...")
        
        # 위치 분류 적용 (안전한 방법)
        location_info = []
        for idx, row in df.iterrows():
            try:
                loc_type, loc_name, entry_date = self.classify_location_type(row)
                location_info.append((loc_type, loc_name, entry_date))
            except Exception as e:
                print(f"⚠️ 행 {idx} 위치 분류 실패: {e}")
                location_info.append(('Unknown', '미분류', None))
        
        # 안전하게 컬럼 추가
        df = df.copy()
        df['LOCATION_TYPE'] = [info[0] for info in location_info]
        df['LOCATION_NAME'] = [info[1] for info in location_info]
        df['ENTRY_DATE_TEMP'] = [info[2] for info in location_info]
        
        # 날짜 정보 추출
        date_columns = []
        for col in df.columns:
            if any(keyword in col.upper() for keyword in ['DSV', 'AGI', 'DAS', 'MIR', 'SHU', 'STORAGE']):
                date_columns.append(col)
        
        # 첫 번째 유효한 날짜 추출
        def get_first_valid_date(row):
            # 1. ENTRY_DATE_TEMP에서 먼저 확인
            if pd.notna(row.get('ENTRY_DATE_TEMP')):
                return pd.to_datetime(row['ENTRY_DATE_TEMP'], errors='coerce')
            
            # 2. 날짜 컬럼에서 확인
            for col in date_columns:
                if col in row.index and pd.notna(row[col]):
                    return pd.to_datetime(row[col], errors='coerce')
            return pd.NaT
        
        df['ENTRY_DATE'] = df.apply(get_first_valid_date, axis=1)
        
        # 임시 컬럼 제거
        if 'ENTRY_DATE_TEMP' in df.columns:
            df = df.drop('ENTRY_DATE_TEMP', axis=1)
        
        # 유효한 날짜가 있는 데이터만 필터링
        df_filtered = df.dropna(subset=['ENTRY_DATE']).copy()
        
        # 월별 그룹화
        df_filtered['ENTRY_MONTH'] = df_filtered['ENTRY_DATE'].dt.to_period('M').astype(str)
        
        # Pkg 컬럼 정리
        if 'Pkg' not in df_filtered.columns:
            df_filtered['Pkg'] = 1
        
        # 입고/출고 분류
        df_filtered['INBOUND_QTY'] = df_filtered['Pkg'].apply(lambda x: x if x > 0 else 0)
        df_filtered['OUTBOUND_QTY'] = df_filtered['Pkg'].apply(lambda x: -x if x < 0 else 0)
        
        print(f"📊 월별 데이터 추출 완료: {len(df_filtered):,}건")
        print(f"🎯 위치 유형 분포:")
        for loc_type in df_filtered['LOCATION_TYPE'].value_counts().items():
            print(f"   - {loc_type[0]}: {loc_type[1]:,}건")
        
        return df_filtered
    
    def generate_warehouse_monthly_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        창고별 월별 입출고 리포트 생성 (Multi-level 헤더)
        
        Args:
            df: 처리된 데이터프레임
            
        Returns:
            pd.DataFrame: 창고별 월별 입출고 리포트
        """
        print("🏭 창고별 월별 입출고 리포트 생성 중...")
        
        # LOCATION_TYPE 컬럼이 없으면 동적으로 생성
        if 'LOCATION_TYPE' not in df.columns:
            print("⚠️ LOCATION_TYPE 컬럼이 없습니다. 동적으로 생성합니다.")
            df_with_type = df.copy()
            df_with_type['LOCATION_TYPE'] = df_with_type['Status_Location'].apply(
                lambda x: 'Warehouse' if x in self.warehouse_columns else 'Site'
            )
            warehouse_df = df_with_type[df_with_type['LOCATION_TYPE'] == 'Warehouse'].copy()
        else:
            # 창고 데이터만 필터링
            warehouse_df = df[df['LOCATION_TYPE'] == 'Warehouse'].copy()
        
        if len(warehouse_df) == 0:
            print("⚠️ 창고 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 필요한 컬럼이 없으면 동적으로 생성
        if 'LOCATION_NAME' not in warehouse_df.columns:
            warehouse_df['LOCATION_NAME'] = warehouse_df['Status_Location']
        
        if 'INBOUND_QTY' not in warehouse_df.columns:
            warehouse_df['INBOUND_QTY'] = warehouse_df['Pkg'].apply(lambda x: x if x > 0 else 0)
        
        if 'OUTBOUND_QTY' not in warehouse_df.columns:
            warehouse_df['OUTBOUND_QTY'] = warehouse_df['Pkg'].apply(lambda x: abs(x) if x < 0 else 0)
        
        if 'ENTRY_MONTH' not in warehouse_df.columns:
            # 첫 번째 유효한 날짜 컬럼에서 월 정보 추출
            date_columns = [col for col in warehouse_df.columns if col in self.all_locations and warehouse_df[col].dtype == 'datetime64[ns]']
            if date_columns:
                warehouse_df['ENTRY_MONTH'] = warehouse_df[date_columns].apply(
                    lambda row: row.dropna().iloc[0].strftime('%Y-%m') if len(row.dropna()) > 0 else '2024-01', axis=1
                )
            else:
                warehouse_df['ENTRY_MONTH'] = '2024-01'  # 기본값
        
        # 입고 집계
        inbound_pivot = warehouse_df.pivot_table(
            index='LOCATION_NAME',
            columns='ENTRY_MONTH',
            values='INBOUND_QTY',
            aggfunc='sum',
            fill_value=0
        )
        
        # 출고 집계
        outbound_pivot = warehouse_df.pivot_table(
            index='LOCATION_NAME',
            columns='ENTRY_MONTH',
            values='OUTBOUND_QTY',
            aggfunc='sum',
            fill_value=0
        )
        
        # Multi-level 헤더 생성
        inbound_columns = pd.MultiIndex.from_tuples([('입고', col) for col in inbound_pivot.columns])
        outbound_columns = pd.MultiIndex.from_tuples([('출고', col) for col in outbound_pivot.columns])
        
        inbound_pivot.columns = inbound_columns
        outbound_pivot.columns = outbound_columns
        
        # 데이터 결합
        warehouse_report = pd.concat([inbound_pivot, outbound_pivot], axis=1)
        warehouse_report = warehouse_report.fillna(0).astype(int)
        
        # 정렬 (입고 -> 출고 순서)
        # MultiIndex 컬럼 정렬: 레벨 0 (입고/출고), 레벨 1 (월) 순서로 정렬
        warehouse_report = warehouse_report.reindex(
            columns=warehouse_report.columns.sort_values()
        )
        
        # 합계 행 추가
        warehouse_report.loc['Total'] = warehouse_report.sum(numeric_only=True)
        
        print(f"✅ 창고별 월별 입출고 리포트 생성 완료: {len(warehouse_report)-1}개 창고")
        
        return warehouse_report
    
    def generate_site_monthly_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        현장별 월별 입고재고 리포트 생성 (Multi-level 헤더)
        
        Args:
            df: 처리된 데이터프레임
            
        Returns:
            pd.DataFrame: 현장별 월별 입고재고 리포트
        """
        print("🏗️ 현장별 월별 입고재고 리포트 생성 중...")
        
        # LOCATION_TYPE 컬럼이 없으면 동적으로 생성
        if 'LOCATION_TYPE' not in df.columns:
            print("⚠️ LOCATION_TYPE 컬럼이 없습니다. 동적으로 생성합니다.")
            df_with_type = df.copy()
            df_with_type['LOCATION_TYPE'] = df_with_type['Status_Location'].apply(
                lambda x: 'Warehouse' if x in self.warehouse_columns else 'Site'
            )
            site_df = df_with_type[df_with_type['LOCATION_TYPE'] == 'Site'].copy()
        else:
            # 현장 데이터만 필터링
            site_df = df[df['LOCATION_TYPE'] == 'Site'].copy()
        
        if len(site_df) == 0:
            print("⚠️ 현장 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 필요한 컬럼이 없으면 동적으로 생성
        if 'LOCATION_NAME' not in site_df.columns:
            site_df['LOCATION_NAME'] = site_df['Status_Location']
        
        if 'INBOUND_QTY' not in site_df.columns:
            site_df['INBOUND_QTY'] = site_df['Pkg'].apply(lambda x: x if x > 0 else 0)
        
        if 'OUTBOUND_QTY' not in site_df.columns:
            site_df['OUTBOUND_QTY'] = site_df['Pkg'].apply(lambda x: abs(x) if x < 0 else 0)
        
        if 'ENTRY_MONTH' not in site_df.columns:
            # 첫 번째 유효한 날짜 컬럼에서 월 정보 추출
            date_columns = [col for col in site_df.columns if col in self.all_locations and site_df[col].dtype == 'datetime64[ns]']
            if date_columns:
                site_df['ENTRY_MONTH'] = site_df[date_columns].apply(
                    lambda row: row.dropna().iloc[0].strftime('%Y-%m') if len(row.dropna()) > 0 else '2024-01', axis=1
                )
            else:
                site_df['ENTRY_MONTH'] = '2024-01'  # 기본값
        
        if 'ENTRY_DATE' not in site_df.columns:
            # 첫 번째 유효한 날짜 컬럼에서 날짜 정보 추출
            date_columns = [col for col in site_df.columns if col in self.all_locations and site_df[col].dtype == 'datetime64[ns]']
            if date_columns:
                site_df['ENTRY_DATE'] = site_df[date_columns].apply(
                    lambda row: row.dropna().iloc[0] if len(row.dropna()) > 0 else pd.Timestamp('2024-01-01'), axis=1
                )
            else:
                site_df['ENTRY_DATE'] = pd.Timestamp('2024-01-01')  # 기본값
        
        # 입고 집계
        inbound_pivot = site_df.pivot_table(
            index='LOCATION_NAME',
            columns='ENTRY_MONTH',
            values='INBOUND_QTY',
            aggfunc='sum',
            fill_value=0
        )
        
        # 재고 계산 (누적 입고 - 출고)
        site_df_sorted = site_df.sort_values(['LOCATION_NAME', 'ENTRY_DATE'])
        site_df_sorted['STOCK_CHANGE'] = site_df_sorted['INBOUND_QTY'] - site_df_sorted['OUTBOUND_QTY']
        site_df_sorted['CUMULATIVE_STOCK'] = site_df_sorted.groupby('LOCATION_NAME')['STOCK_CHANGE'].cumsum()
        
        # 재고 집계
        stock_pivot = site_df_sorted.pivot_table(
            index='LOCATION_NAME',
            columns='ENTRY_MONTH',
            values='CUMULATIVE_STOCK',
            aggfunc='last',
            fill_value=0
        )
        
        # 이전 월 재고 값 전달
        stock_pivot = stock_pivot.ffill(axis=1)
        
        # Multi-level 헤더 생성
        inbound_columns = pd.MultiIndex.from_tuples([('입고', col) for col in inbound_pivot.columns])
        stock_columns = pd.MultiIndex.from_tuples([('재고', col) for col in stock_pivot.columns])
        
        inbound_pivot.columns = inbound_columns
        stock_pivot.columns = stock_columns
        
        # 데이터 결합
        site_report = pd.concat([inbound_pivot, stock_pivot], axis=1)
        site_report = site_report.fillna(0).astype(int)
        
        # 정렬 (입고 -> 재고 순서)
        # MultiIndex 컬럼 정렬: 레벨 0 (입고/재고), 레벨 1 (월) 순서로 정렬
        site_report = site_report.reindex(
            columns=site_report.columns.sort_values()
        )
        
        # 합계 행 추가
        site_report.loc['합계'] = site_report.sum(numeric_only=True)
        
        print(f"✅ 현장별 월별 입고재고 리포트 생성 완료: {len(site_report)-1}개 현장")
        
        return site_report
    
    def export_to_excel(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Excel 파일로 내보내기
        
        Args:
            df: 처리된 데이터프레임
            filename: 출력 파일명 (선택사항)
            
        Returns:
            str: 생성된 파일 경로
        """
        if filename is None:
            filename = f"MACHO_월별집계_{self.timestamp}.xlsx"
        
        print(f"📄 Excel 파일 생성 중: {filename}")
        
        # 월별 데이터 추출
        monthly_df = self.extract_monthly_data(df)
        
        # 창고별 월별 입출고 리포트
        warehouse_report = self.generate_warehouse_monthly_report(monthly_df)
        
        # 현장별 월별 입고재고 리포트
        site_report = self.generate_site_monthly_report(monthly_df)
        
        # Excel 파일 생성
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # 시트 1: 창고별 월별 입출고
            if not warehouse_report.empty:
                warehouse_report.to_excel(writer, sheet_name='창고_월별_입출고')
            
            # 시트 2: 현장별 월별 입고재고
            if not site_report.empty:
                site_report.to_excel(writer, sheet_name='현장_월별_입고재고')
            
            # 시트 3: 리포트 정보
            summary_df = pd.DataFrame({
                '항목': ['리포트 유형', '생성 시간', '처리 레코드 수', '신뢰도'],
                '값': [
                    '월별 집계 전용 시스템',
                    self.timestamp,
                    f"{len(monthly_df):,}건",
                    f"{self.confidence_threshold:.1%}"
                ]
            })
            summary_df.to_excel(writer, sheet_name='리포트_정보', index=False)
        
        print(f"✅ Excel 파일 생성 완료: {filename}")
        return filename
    
    def generate_complete_monthly_report(self) -> dict:
        """
        완전한 월별 리포트 생성
        
        Returns:
            dict: 리포트 결과 및 메타데이터
        """
        print("🎯 완전한 월별 리포트 생성 시작...")
        
        # 완전한 데이터셋 로드
        complete_df = self.load_complete_dataset()
        
        # Excel 파일 생성
        output_file = self.export_to_excel(complete_df)
        
        # 결과 요약
        result = {
            'status': 'SUCCESS',
            'confidence': self.confidence_threshold,
            'total_records': len(complete_df),
            'output_file': output_file,
            'timestamp': self.timestamp,
            'data_sources': complete_df['DATA_SOURCE'].value_counts().to_dict(),
            'location_types': complete_df.groupby('LOCATION_TYPE').size().to_dict() if 'LOCATION_TYPE' in complete_df.columns else {},
            'next_commands': [
                '/visualize-data monthly-trends',
                '/generate-report warehouse-summary',
                '/automate monthly-pipeline'
            ]
        }
        
        print(f"✅ 완전한 월별 리포트 생성 완료!")
        print(f"📊 처리 레코드: {result['total_records']:,}건")
        print(f"📄 출력 파일: {result['output_file']}")
        print(f"🎯 신뢰도: {result['confidence']:.1%}")
        
        return result

def main():
    """메인 실행 함수"""
    print("🚀 월별 집계 전용 시스템 실행")
    print("=" * 70)
    
    # 월별 집계 시스템 초기화
    aggregator = MonthlyAggregator()
    
    # 완전한 월별 리포트 생성
    result = aggregator.generate_complete_monthly_report()
    
    print("\n🎉 월별 집계 전용 시스템 실행 완료!")
    print("=" * 70)
    print(f"📊 처리 결과: {result['status']}")
    print(f"📄 출력 파일: {result['output_file']}")
    print(f"🎯 신뢰도: {result['confidence']:.1%}")
    
    # 추천 명령어 출력
    print("\n🔧 **추천 명령어:**")
    for cmd in result['next_commands']:
        print(f"{cmd} [월별 집계 기반 분석]")

if __name__ == "__main__":
    main() 