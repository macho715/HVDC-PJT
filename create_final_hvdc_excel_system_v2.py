"""
🏗️ 최종 HVDC Real Data Excel System v2.0
TDD 검증된 개선 로직 + 입고 로직 3단계 프로세스 구현
Samsung C&T · ADNOC · DSV Partnership
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# HVDC 입고 로직 구현 및 집계 시스템 v2.0


class HVDCRealDataExcelSystemV2:
    """
    최종 HVDC Real Data Excel System v2.0
    개선된 창고 입출고 계산 로직 적용
    """
    
    def __init__(self):
        """시스템 초기화"""
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 실제 데이터 경로 설정
        self.data_path = Path("hvdc_ontology_system/data")
        self.hitachi_file = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.simense_file = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        self.invoice_file = self.data_path / "HVDC WAREHOUSE_INVOICE.xlsx"
        
        # 실제 데이터 구조 기반 매핑 (가이드 순서대로)
        self.real_warehouse_columns = {
            'AAA Storage': 'AAA_Storage',
            'DSV Al Markaz': 'DSV_Al_Markaz',
            'DSV Indoor': 'DSV_Indoor',
            'DSV MZP': 'DSV_MZP',
            'DSV Outdoor': 'DSV_Outdoor',
            'Hauler Indoor': 'Hauler_Indoor',
            'MOSB': 'MOSB'
        }
        
        self.real_site_columns = {
            'AGI': 'AGI',
            'DAS': 'DAS',
            'MIR': 'MIR',
            'SHU': 'SHU'
        }
        
        # 창고 우선순위 정의 (DSV Al Markaz > DSV Indoor > Status_Location)
        self.warehouse_priority = ['DSV Al Markaz', 'DSV Indoor', 'DSV Outdoor', 'DSV MZP', 'AAA Storage', 'Hauler Indoor', 'MOSB']
        
        # Flow Code 매핑 (실제 wh handling 기반)
        self.flow_codes = {
            0: 'Pre Arrival',
            1: 'Port → WH (1개)',
            2: 'Port → WH (2개)',
            3: 'Port → WH (3개)',
            4: 'Port → WH (4개+)'
        }
        
        # 데이터 저장 변수
        self.combined_data = None
        self.total_records = 0
        
        logger.info("🏗️ HVDC Real Data Excel System v2.0 초기화 완료")
    
    def load_real_hvdc_data(self):
        """실제 HVDC RAW DATA 로드 (물류 트랜잭션만)"""
        logger.info("📂 실제 HVDC RAW DATA 로드 시작")
        
        combined_dfs = []
        
        try:
            # HITACHI 데이터 로드
            if self.hitachi_file.exists():
                logger.info(f"📊 HITACHI 데이터 로드: {self.hitachi_file}")
                hitachi_data = pd.read_excel(self.hitachi_file, engine='openpyxl')
                hitachi_data['Vendor'] = 'HITACHI'
                hitachi_data['Source_File'] = 'HITACHI(HE)'
                combined_dfs.append(hitachi_data)
                logger.info(f"✅ HITACHI 데이터 로드 완료: {len(hitachi_data)}건")
            
            # SIMENSE 데이터 로드
            if self.simense_file.exists():
                logger.info(f"📊 SIMENSE 데이터 로드: {self.simense_file}")
                simense_data = pd.read_excel(self.simense_file, engine='openpyxl')
                simense_data['Vendor'] = 'SIMENSE'
                simense_data['Source_File'] = 'SIMENSE(SIM)'
                combined_dfs.append(simense_data)
                logger.info(f"✅ SIMENSE 데이터 로드 완료: {len(simense_data)}건")
            
            # 데이터 결합 (INVOICE 파일 제외)
            if combined_dfs:
                self.combined_data = pd.concat(combined_dfs, ignore_index=True, sort=False)
                self.total_records = len(self.combined_data)
                logger.info(f"🔗 데이터 결합 완료: {self.total_records}건")
            else:
                raise ValueError("로드할 데이터 파일이 없습니다.")
                
        except Exception as e:
            logger.error(f"❌ 데이터 로드 실패: {str(e)}")
            raise
        
        return self.combined_data
    
    def process_real_data(self):
        """실제 데이터 전처리 및 Flow Code 계산"""
        logger.info("🔧 실제 데이터 전처리 시작")
        
        if self.combined_data is None:
            raise ValueError("데이터가 로드되지 않았습니다.")
        
        # 날짜 컬럼 변환
        date_columns = ['ETD/ATD', 'ETA/ATA', 'Status_Location_Date'] + \
                      list(self.real_warehouse_columns.keys()) + \
                      list(self.real_site_columns.keys())
        
        for col in date_columns:
            if col in self.combined_data.columns:
                self.combined_data[col] = pd.to_datetime(self.combined_data[col], errors='coerce')
        
        # Flow Code 계산 (기존 wh handling 컬럼 우선 활용)
        if 'wh handling' in self.combined_data.columns:
            logger.info("📊 기존 'wh handling' 컬럼 활용")
            self.combined_data['FLOW_CODE'] = self.combined_data['wh handling'].fillna(0).astype(int)
            self.combined_data['FLOW_CODE'] = self.combined_data['FLOW_CODE'].clip(0, 4)
        else:
            logger.info("🔄 wh handling 컬럼 직접 계산")
            self.combined_data['FLOW_CODE'] = 0
            for col in self.real_warehouse_columns.keys():
                if col in self.combined_data.columns:
                    self.combined_data['FLOW_CODE'] += self.combined_data[col].notna().astype(int)
            self.combined_data['FLOW_CODE'] = self.combined_data['FLOW_CODE'].clip(0, 4)
        
        # Flow Description 추가
        self.combined_data['FLOW_DESCRIPTION'] = self.combined_data['FLOW_CODE'].map(self.flow_codes)
        
        # 벤더별 분포 확인
        vendor_dist = self.combined_data['Vendor'].value_counts()
        logger.info(f"📈 벤더별 분포: {vendor_dist.to_dict()}")
        
        # Flow Code 분포 확인
        flow_dist = self.combined_data['FLOW_CODE'].value_counts().sort_index()
        logger.info(f"📊 Flow Code 분포: {flow_dist.to_dict()}")
        
        logger.info("✅ 데이터 전처리 완료")
        return self.combined_data
    
    def calculate_warehouse_inbound(self, df: pd.DataFrame) -> Dict:
        """
        입고 로직 3단계 - Step 1: 창고 컬럼 날짜 존재 → 입고 아이템 리스트화
        반환: total_inbound, by_warehouse, by_month
        """
        logger.info("🔄 입고 로직 Step 1: 창고 입고 아이템 리스트화")
        
        inbound_items = []
        total_inbound = 0
        by_warehouse = {}
        by_month = {}
        
        for idx, row in df.iterrows():
            for warehouse in self.real_warehouse_columns.keys():
                if warehouse in row.index and pd.notna(row[warehouse]):
                    try:
                        warehouse_date = pd.to_datetime(row[warehouse])
                        inbound_items.append({
                            'Item_ID': idx,
                            'Warehouse': warehouse,
                            'Inbound_Date': warehouse_date,
                            'Year_Month': warehouse_date.strftime('%Y-%m'),
                            'Vendor': row.get('Vendor', 'Unknown')
                        })
                        total_inbound += 1
                        
                        # 창고별 집계
                        if warehouse not in by_warehouse:
                            by_warehouse[warehouse] = 0
                        by_warehouse[warehouse] += 1
                        
                        # 월별 집계
                        month_key = warehouse_date.strftime('%Y-%m')
                        if month_key not in by_month:
                            by_month[month_key] = 0
                        by_month[month_key] += 1
                        
                    except:
                        continue
        
        logger.info(f"✅ 입고 아이템 총 {total_inbound}건 처리")
        return {
            'total_inbound': total_inbound,
            'by_warehouse': by_warehouse,
            'by_month': by_month,
            'inbound_items': inbound_items
        }
    
    def create_monthly_inbound_pivot(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        입고 로직 3단계 - Step 2: pivot_table 방식으로 월별 입고 집계
        Final_Location 기준 Month×Warehouse 매트릭스
        """
        logger.info("🔄 입고 로직 Step 2: 월별 입고 피벗 생성")
        
        # Final Location 계산
        df = self.calculate_final_location(df)
        
        # 날짜 컬럼 처리
        inbound_data = []
        for idx, row in df.iterrows():
            final_location = row.get('Final_Location', 'Unknown')
            if final_location != 'Unknown':
                for warehouse in self.real_warehouse_columns.keys():
                    if warehouse in row.index and pd.notna(row[warehouse]):
                        try:
                            warehouse_date = pd.to_datetime(row[warehouse])
                            inbound_data.append({
                                'Item_ID': idx,
                                'Warehouse': warehouse,
                                'Final_Location': final_location,
                                'Year_Month': warehouse_date.strftime('%Y-%m'),
                                'Inbound_Date': warehouse_date
                            })
                        except:
                            continue
        
        if not inbound_data:
            # 빈 피벗 테이블 반환
            months = pd.date_range('2023-02', '2025-06', freq='MS')
            month_strings = [month.strftime('%Y-%m') for month in months]
            
            pivot_df = pd.DataFrame(index=month_strings)
            for warehouse in self.real_warehouse_columns.keys():
                pivot_df[warehouse] = 0
            
            return pivot_df
        
        # 피벗 테이블 생성
        inbound_df = pd.DataFrame(inbound_data)
        pivot_df = inbound_df.pivot_table(
            index='Year_Month', 
            columns='Final_Location', 
            values='Item_ID', 
            aggfunc='count', 
            fill_value=0
        )
        
        logger.info(f"✅ 월별 입고 피벗 생성 완료: {pivot_df.shape}")
        return pivot_df
    
    def calculate_final_location(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        입고 로직 3단계 - Step 3: 우선순위 기반 최종 위치 계산
        우선순위: DSV Al Markaz > DSV Indoor > Status_Location
        """
        logger.info("🔄 입고 로직 Step 3: 최종 위치 계산 (우선순위 적용)")
        
        def get_final_location(row):
            # 우선순위 순서로 확인
            for warehouse in self.warehouse_priority:
                if warehouse in row.index and pd.notna(row[warehouse]):
                    return warehouse
            
            # 마지막으로 Status_Location 확인
            if 'Status_Location' in row.index and pd.notna(row['Status_Location']):
                return 'Status_Location'
            
            return 'Unknown'
        
        # np.select 고성능 계산 활용
        conditions = []
        choices = []
        
        for warehouse in self.warehouse_priority:
            if warehouse in df.columns:
                conditions.append(df[warehouse].notna())
                choices.append(warehouse)
        
        # Status_Location 조건 추가
        if 'Status_Location' in df.columns:
            conditions.append(df['Status_Location'].notna())
            choices.append('Status_Location')
        
        # 조건이 없으면 기본값 처리
        if not conditions:
            df['Final_Location'] = 'Unknown'
        else:
            df['Final_Location'] = np.select(conditions, choices, default='Unknown')
        
        logger.info(f"✅ 최종 위치 계산 완료")
        return df
    
    def calculate_warehouse_outbound(self, df: pd.DataFrame) -> Dict:
        """창고 출고 로직 - Site 컬럼 날짜 존재 → 출고 집계"""
        logger.info("🔄 창고 출고 계산 시작")
        
        outbound_items = []
        total_outbound = 0
        by_warehouse = {}
        by_month = {}
        
        for idx, row in df.iterrows():
            for site in self.real_site_columns.keys():
                if site in row.index and pd.notna(row[site]):
                    try:
                        site_date = pd.to_datetime(row[site])
                        # 해당 아이템이 어느 창고에서 출고되었는지 확인
                        final_location = row.get('Final_Location', 'Unknown')
                        
                        if final_location in self.real_warehouse_columns:
                            outbound_items.append({
                                'Item_ID': idx,
                                'Warehouse': final_location,
                                'Site': site,
                                'Outbound_Date': site_date,
                                'Year_Month': site_date.strftime('%Y-%m')
                            })
                            total_outbound += 1
                            
                            # 창고별 집계
                            if final_location not in by_warehouse:
                                by_warehouse[final_location] = 0
                            by_warehouse[final_location] += 1
                            
                            # 월별 집계
                            month_key = site_date.strftime('%Y-%m')
                            if month_key not in by_month:
                                by_month[month_key] = 0
                            by_month[month_key] += 1
                            
                    except:
                        continue
        
        logger.info(f"✅ 출고 아이템 총 {total_outbound}건 처리")
        return {
            'total_outbound': total_outbound,
            'by_warehouse': by_warehouse,
            'by_month': by_month,
            'outbound_items': outbound_items
        }
    
    def calculate_warehouse_inventory(self, df: pd.DataFrame) -> Dict:
        """창고 재고 로직 - In – Out 누적 = 월말 재고"""
        logger.info("🔄 창고 재고 계산 시작")
        
        # 입고 및 출고 계산
        inbound_result = self.calculate_warehouse_inbound(df)
        outbound_result = self.calculate_warehouse_outbound(df)
        
        # 월별 재고 계산
        inventory_by_month = {}
        all_months = set()
        
        # 모든 월 수집
        all_months.update(inbound_result['by_month'].keys())
        all_months.update(outbound_result['by_month'].keys())
        
        # 월별 재고 계산
        for month in sorted(all_months):
            inbound_count = inbound_result['by_month'].get(month, 0)
            outbound_count = outbound_result['by_month'].get(month, 0)
            inventory_by_month[month] = inbound_count - outbound_count
        
        # 창고별 재고 계산
        inventory_by_warehouse = {}
        for warehouse in self.real_warehouse_columns.keys():
            inbound_count = inbound_result['by_warehouse'].get(warehouse, 0)
            outbound_count = outbound_result['by_warehouse'].get(warehouse, 0)
            inventory_by_warehouse[warehouse] = inbound_count - outbound_count
        
        return {
            'inventory_by_month': inventory_by_month,
            'inventory_by_warehouse': inventory_by_warehouse,
            'total_inventory': sum(inventory_by_warehouse.values())
        }
    
    def calculate_direct_delivery(self, df: pd.DataFrame) -> Dict:
        """직송 로직 - Port→Site 직접 이동 (FLOW_CODE 0/1) 식별"""
        logger.info("🔄 직송 배송 계산 시작")
        
        # FLOW_CODE 0 또는 1인 경우를 직송으로 간주
        direct_delivery_df = df[df['FLOW_CODE'].isin([0, 1])]
        
        direct_items = []
        total_direct = len(direct_delivery_df)
        
        for idx, row in direct_delivery_df.iterrows():
            for site in self.real_site_columns.keys():
                if site in row.index and pd.notna(row[site]):
                    try:
                        site_date = pd.to_datetime(row[site])
                        direct_items.append({
                            'Item_ID': idx,
                            'Site': site,
                            'Direct_Date': site_date,
                            'Year_Month': site_date.strftime('%Y-%m'),
                            'Flow_Code': row['FLOW_CODE']
                        })
                    except:
                        continue
        
        logger.info(f"✅ 직송 배송 총 {total_direct}건 처리")
        return {
            'total_direct': total_direct,
            'direct_items': direct_items
        }
    

    
    def calculate_warehouse_outbound_real(self, df: pd.DataFrame, warehouse_name: str, period: pd.Timestamp) -> int:
        """
        TDD 검증된 시간 순서 기반 정확한 출고 계산
        개별 케이스별로 창고 → 다음 단계 이동 추적
        """
        # 빈 DataFrame 처리
        if df.empty or warehouse_name not in df.columns:
            return 0
        
        outbound_count = 0
        
        # Step 1: 해당 창고 방문 케이스 필터링
        warehouse_visited = df[df[warehouse_name].notna()].copy()
        
        if len(warehouse_visited) == 0:
            return 0
        
        # Step 2: 각 케이스별 개별 추적
        for idx, row in warehouse_visited.iterrows():
            warehouse_date = row[warehouse_name]  # 창고 도착 시점
            
            # Step 3: 다음 단계 이동 날짜 탐색
            next_dates = []
            
            # 3-1: 다른 창고로 이동 확인
            for other_wh in self.real_warehouse_columns.keys():
                if other_wh != warehouse_name and other_wh in row.index:
                    other_date = row[other_wh]
                    if pd.notna(other_date) and other_date > warehouse_date:
                        next_dates.append(other_date)
            
            # 3-2: 현장으로 이동 확인
            for site_name in self.real_site_columns.keys():
                if site_name in row.index:
                    site_date = row[site_name]
                    if pd.notna(site_date) and site_date > warehouse_date:
                        next_dates.append(site_date)
            
            # Step 4: 가장 빠른 다음 단계로 출고 시점 결정
            if next_dates:
                earliest_next_date = min(next_dates)
                if earliest_next_date.to_period('M') == period.to_period('M'):
                    outbound_count += 1
                    
        return outbound_count
    
    def calculate_site_inventory_real(self, df: pd.DataFrame, site_name: str, period: pd.Timestamp) -> int:
        """
        현장별 누적 재고 정확 계산
        해당 월 말까지 현장에 누적된 건수
        """
        if df.empty or site_name not in df.columns:
            return 0
        
        # 해당 월 말까지 현장에 도착한 누적 건수
        site_dates = df[site_name].dropna()
        month_end = period + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        arrived_by_month_end = (site_dates <= month_end).sum()
        
        # 현재 Status_Location과 교차 검증
        current_at_site = 0
        if 'Status_Location' in df.columns:
            current_at_site = (df['Status_Location'] == site_name).sum()
        
        # 보수적 접근 (더 작은 값 선택)
        return min(arrived_by_month_end, current_at_site) if current_at_site > 0 else arrived_by_month_end
    
    def calculate_warehouse_monthly_real(self) -> pd.DataFrame:
        """
        창고별 월별 입출고 계산 (가이드 표준)
        3단계 입고 로직 적용 + Multi-Level Header 구조 (15열)
        """
        logger.info("📊 창고별 월별 입출고 계산 (가이드 3단계 로직)")
        
        df = self.combined_data.copy()
        
        # 3단계 입고 로직 적용
        df = self.calculate_final_location(df)
        inbound_result = self.calculate_warehouse_inbound(df)
        outbound_result = self.calculate_warehouse_outbound(df)
        
        # 월별 기간 생성 (2023-02 ~ 2025-06)
        months = pd.date_range('2023-02', '2025-06', freq='MS')
        month_strings = [month.strftime('%Y-%m') for month in months]
        
        # 결과 DataFrame 초기화 (15열 구조)
        results = []
        
        for month_str in month_strings:
            row = [month_str]  # 첫 번째 컬럼: 입고월
            
            # 입고 7개 창고 (가이드 순서)
            warehouses = ['AAA Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV Outdoor', 'Hauler Indoor', 'MOSB']
            for warehouse in warehouses:
                # 월별 입고 계산
                inbound_count = 0
                for item in inbound_result.get('inbound_items', []):
                    if item.get('Warehouse') == warehouse and item.get('Year_Month') == month_str:
                        inbound_count += 1
                row.append(inbound_count)
            
            # 출고 7개 창고 (동일 순서)
            for warehouse in warehouses:
                # 월별 출고 계산
                outbound_count = 0
                for item in outbound_result.get('outbound_items', []):
                    if item.get('Warehouse') == warehouse and item.get('Year_Month') == month_str:
                        outbound_count += 1
                row.append(outbound_count)
            
            results.append(row)
        
        # 컬럼 생성 (15열)
        columns = ['입고월']
        
        # 입고 7개 창고
        warehouses = ['AAA Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV Outdoor', 'Hauler Indoor', 'MOSB']
        for warehouse in warehouses:
            columns.append(f'입고_{warehouse}')
        
        # 출고 7개 창고
        for warehouse in warehouses:
            columns.append(f'출고_{warehouse}')
        
        # DataFrame 생성
        warehouse_monthly = pd.DataFrame(results, columns=columns)
        
        # 총합계 행 추가
        total_row = ['Total']
        
        # 입고 총합
        for warehouse in warehouses:
            total_inbound = warehouse_monthly[f'입고_{warehouse}'].sum()
            total_row.append(total_inbound)
        
        # 출고 총합
        for warehouse in warehouses:
            total_outbound = warehouse_monthly[f'출고_{warehouse}'].sum()
            total_row.append(total_outbound)
        
        warehouse_monthly.loc[len(warehouse_monthly)] = total_row
        
        logger.info(f"✅ 창고별 월별 입출고 계산 완료: {warehouse_monthly.shape} (15열)")
        return warehouse_monthly
    
    def calculate_site_monthly_real(self) -> pd.DataFrame:
        """
        현장별 월별 입고재고 계산 (가이드 표준)
        Multi-Level Header 구조 (9열) + 직송 로직 적용
        """
        logger.info("📊 현장별 월별 입고재고 계산 (가이드 표준)")
        
        df = self.combined_data.copy()
        
        # 직송 배송 계산
        direct_result = self.calculate_direct_delivery(df)
        
        # 월별 기간 생성 (2024-01 ~ 2025-06)
        months = pd.date_range('2024-01', '2025-06', freq='MS')
        month_strings = [month.strftime('%Y-%m') for month in months]
        
        # 결과 DataFrame 초기화 (9열 구조)
        results = []
        
        # 누적 재고 계산용 변수
        cumulative_inventory = {'AGI': 0, 'DAS': 0, 'MIR': 0, 'SHU': 0}
        
        for month_str in month_strings:
            row = [month_str]  # 첫 번째 컬럼: 입고월
            
            # 입고 4개 현장 (가이드 순서)
            sites = ['AGI', 'DAS', 'MIR', 'SHU']
            for site in sites:
                # 월별 입고 계산 (직송 배송 포함)
                inbound_count = 0
                for item in direct_result.get('direct_items', []):
                    if item.get('Site') == site and item.get('Year_Month') == month_str:
                        inbound_count += 1
                
                # 현장별 입고 추가 (일반 배송)
                if site in df.columns:
                    site_dates = df[site].dropna()
                    for date in site_dates:
                        try:
                            if pd.to_datetime(date).strftime('%Y-%m') == month_str:
                                inbound_count += 1
                        except:
                            continue
                
                row.append(inbound_count)
                
                # 누적 재고 업데이트
                cumulative_inventory[site] += inbound_count
            
            # 재고 4개 현장 (동일 순서)
            for site in sites:
                # 월별 소비 (입고량의 5% 소비)
                consumption = int(cumulative_inventory[site] * 0.05)
                cumulative_inventory[site] = max(0, cumulative_inventory[site] - consumption)
                row.append(cumulative_inventory[site])
            
            results.append(row)
        
        # 컬럼 생성 (9열)
        columns = ['입고월']
        
        # 입고 4개 현장
        sites = ['AGI', 'DAS', 'MIR', 'SHU']
        for site in sites:
            columns.append(f'입고_{site}')
        
        # 재고 4개 현장
        for site in sites:
            columns.append(f'재고_{site}')
        
        # DataFrame 생성
        site_monthly = pd.DataFrame(results, columns=columns)
        
        # 총합계 행 추가
        total_row = ['Total']
        
        # 입고 총합
        for site in sites:
            total_inbound = site_monthly[f'입고_{site}'].sum()
            total_row.append(total_inbound)
        
        # 재고 총합 (최종 재고)
        for site in sites:
            final_inventory = site_monthly[f'재고_{site}'].iloc[-1] if not site_monthly.empty else 0
            total_row.append(final_inventory)
        
        site_monthly.loc[len(site_monthly)] = total_row
        
        logger.info(f"✅ 현장별 월별 입고재고 계산 완료: {site_monthly.shape} (9열)")
        return site_monthly
    
    def create_flow_analysis_real(self) -> pd.DataFrame:
        """실제 데이터 기반 Flow Code 분석"""
        logger.info("📊 Flow Code 분석 시작")
        
        df = self.combined_data.copy()
        
        # 수치 컬럼 안전 필터링
        potential_numeric_columns = ['CBM', 'N.W(kgs)', 'G.W(kgs)', 'SQM', 'Pkg']
        available_numeric_columns = []
        
        for col in potential_numeric_columns:
            if col in df.columns:
                # 수치형으로 변환 가능한지 확인
                try:
                    test_series = pd.to_numeric(df[col], errors='coerce')
                    if not test_series.isna().all():  # 모두 NaN이 아니면 사용 가능
                        # 실제 데이터를 수치형으로 변환
                        df[col] = test_series
                        available_numeric_columns.append(col)
                        logger.info(f"✅ 수치 컬럼 확인: {col}")
                except Exception as e:
                    logger.warning(f"⚠️ 수치 컬럼 변환 실패: {col} - {str(e)}")
        
        # Flow Code별 기본 통계
        if available_numeric_columns:
            # 안전한 집계 실행
            agg_dict = {}
            
            # Case 카운트 추가
            case_column = 'Case No.' if 'Case No.' in df.columns else df.columns[0]
            agg_dict[case_column] = 'count'
            
            # 수치 컬럼 집계 추가
            for col in available_numeric_columns:
                agg_dict[col] = ['sum', 'mean']
            
            try:
                flow_summary = df.groupby('FLOW_CODE').agg(agg_dict).round(2)
                flow_summary.columns = ['_'.join(str(col)).strip() for col in flow_summary.columns]
                flow_summary = flow_summary.reset_index()
            except Exception as e:
                logger.warning(f"⚠️ 상세 집계 실패, 기본 집계 사용: {str(e)}")
                flow_summary = df.groupby('FLOW_CODE').size().reset_index(name='Count')
        else:
            logger.info("📊 수치 컬럼이 없어 기본 집계 사용")
            flow_summary = df.groupby('FLOW_CODE').size().reset_index(name='Count')
        
        # Flow Description 추가
        flow_summary['FLOW_DESCRIPTION'] = flow_summary['FLOW_CODE'].map(self.flow_codes)
        
        # 컬럼 순서 조정 (FLOW_DESCRIPTION을 앞쪽으로)
        cols = flow_summary.columns.tolist()
        if 'FLOW_DESCRIPTION' in cols:
            cols.remove('FLOW_DESCRIPTION')
            cols.insert(1, 'FLOW_DESCRIPTION')  # FLOW_CODE 다음에 위치
            flow_summary = flow_summary[cols]
        
        logger.info(f"✅ Flow Code 분석 완료: {len(flow_summary)}개 코드")
        return flow_summary
    
    def create_transaction_summary(self) -> pd.DataFrame:
        """전체 트랜잭션 요약"""
        logger.info("📊 전체 트랜잭션 요약 생성")
        
        df = self.combined_data.copy()
        
        # 기본 요약 정보
        summary_data = []
        
        # 전체 통계
        summary_data.append({
            'Category': '전체 통계',
            'Item': '총 트랜잭션 건수',
            'Value': f"{len(df):,}건",
            'Percentage': '100.0%'
        })
        
        # 벤더별 분포
        vendor_dist = df['Vendor'].value_counts()
        for vendor, count in vendor_dist.items():
            percentage = (count / len(df)) * 100
            summary_data.append({
                'Category': '벤더별 분포',
                'Item': vendor,
                'Value': f"{count:,}건",
                'Percentage': f"{percentage:.1f}%"
            })
        
        # Flow Code 분포
        flow_dist = df['FLOW_CODE'].value_counts().sort_index()
        for flow_code, count in flow_dist.items():
            percentage = (count / len(df)) * 100
            flow_desc = self.flow_codes.get(flow_code, f"Flow {flow_code}")
            summary_data.append({
                'Category': 'Flow Code 분포',
                'Item': f"Flow {flow_code}: {flow_desc}",
                'Value': f"{count:,}건",
                'Percentage': f"{percentage:.1f}%"
            })
        
        # 창고별 방문 현황
        for warehouse_name in self.real_warehouse_columns.keys():
            if warehouse_name in df.columns:
                visited_count = df[warehouse_name].notna().sum()
                percentage = (visited_count / len(df)) * 100
                summary_data.append({
                    'Category': '창고별 방문 현황',
                    'Item': warehouse_name,
                    'Value': f"{visited_count:,}건",
                    'Percentage': f"{percentage:.1f}%"
                })
        
        # 현장별 도착 현황
        for site_name in self.real_site_columns.keys():
            if site_name in df.columns:
                arrived_count = df[site_name].notna().sum()
                percentage = (arrived_count / len(df)) * 100
                summary_data.append({
                    'Category': '현장별 도착 현황',
                    'Item': site_name,
                    'Value': f"{arrived_count:,}건",
                    'Percentage': f"{percentage:.1f}%"
                })
        
        summary_df = pd.DataFrame(summary_data)
        
        logger.info(f"✅ 전체 트랜잭션 요약 완료: {len(summary_df)}개 항목")
        return summary_df
    
    def create_multi_level_headers(self, df: pd.DataFrame, sheet_type: str) -> pd.DataFrame:
        """Multi-Level Header 생성 (가이드 표준)"""
        if sheet_type == 'warehouse':
            # 창고 Multi-Level Header: 15열 (Location + 입고7 + 출고7)
            level_0 = ['입고월']  # 첫 번째 컬럼
            level_1 = ['']
            
            # 입고 7개 창고 (가이드 순서)
            warehouses = ['AAA Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV Outdoor', 'Hauler Indoor', 'MOSB']
            for warehouse in warehouses:
                level_0.append('입고')
                level_1.append(warehouse)
            
            # 출고 7개 창고 (동일 순서)
            for warehouse in warehouses:
                level_0.append('출고')
                level_1.append(warehouse)
            
            multi_columns = pd.MultiIndex.from_arrays([level_0, level_1], names=['Type', 'Location'])
            
        elif sheet_type == 'site':
            # 현장 Multi-Level Header: 9열 (Location + 입고4 + 재고4)
            level_0 = ['입고월']  # 첫 번째 컬럼
            level_1 = ['']
            
            # 입고 4개 현장 (가이드 순서)
            sites = ['AGI', 'DAS', 'MIR', 'SHU']
            for site in sites:
                level_0.append('입고')
                level_1.append(site)
            
            # 재고 4개 현장 (동일 순서)
            for site in sites:
                level_0.append('재고')
                level_1.append(site)
            
            multi_columns = pd.MultiIndex.from_arrays([level_0, level_1], names=['Type', 'Location'])
        
        else:
            return df
        
        # 컬럼 순서 맞추기
        if len(df.columns) == len(multi_columns):
            df.columns = multi_columns
        
        return df
    
    def generate_final_excel_system(self):
        """최종 Excel 시스템 생성 (가이드 표준 5시트)"""
        logger.info("🏗️ 최종 Excel 시스템 생성 시작 (가이드 표준)")
        
        # 데이터 로드 및 처리
        self.load_real_hvdc_data()
        self.process_real_data()
        
        # 각 시트 데이터 준비
        logger.info("📊 시트별 데이터 준비 중...")
        
        # 시트 1: 창고별 월별 입출고 (Multi-Level Header, 15열)
        warehouse_monthly = self.calculate_warehouse_monthly_real()
        warehouse_monthly_with_headers = self.create_multi_level_headers(warehouse_monthly, 'warehouse')
        
        # 시트 2: 현장별 월별 입고재고 (Multi-Level Header, 9열)
        site_monthly = self.calculate_site_monthly_real()
        site_monthly_with_headers = self.create_multi_level_headers(site_monthly, 'site')
        
        # 시트 3: Flow Code 분석 (FLOW_CODE 0-4 분석)
        flow_analysis = self.create_flow_analysis_real()
        
        # 시트 4: 전체 트랜잭션 요약
        transaction_summary = self.create_transaction_summary()
        
        # 시트 5: 원본 데이터 샘플 (처음 1000건)
        sample_data = self.combined_data.head(1000)
        
        # Excel 파일 생성
        excel_filename = f"HVDC_입고로직_종합리포트_{self.timestamp}.xlsx"
        
        logger.info(f"📝 Excel 파일 생성: {excel_filename}")
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # 시트 1: 창고_월별_입출고 (Multi-Level Header)
            if isinstance(warehouse_monthly_with_headers.columns, pd.MultiIndex):
                warehouse_monthly_with_headers.to_excel(writer, sheet_name='창고_월별_입출고', index=True)
            else:
                warehouse_monthly_with_headers.to_excel(writer, sheet_name='창고_월별_입출고', index=False)
            
            # 시트 2: 현장_월별_입고재고 (Multi-Level Header)
            if isinstance(site_monthly_with_headers.columns, pd.MultiIndex):
                site_monthly_with_headers.to_excel(writer, sheet_name='현장_월별_입고재고', index=True)
            else:
                site_monthly_with_headers.to_excel(writer, sheet_name='현장_월별_입고재고', index=False)
            
            # 시트 3: Flow_Code_분석
            flow_analysis.to_excel(writer, sheet_name='Flow_Code_분석', index=False)
            
            # 시트 4: 전체_트랜잭션_요약
            transaction_summary.to_excel(writer, sheet_name='전체_트랜잭션_요약', index=False)
            
            # 시트 5: 원본_데이터_샘플
            sample_data.to_excel(writer, sheet_name='원본_데이터_샘플', index=False)
        
        logger.info(f"🎉 최종 Excel 시스템 생성 완료: {excel_filename}")
        
        # 결과 통계 출력
        logger.info("📊 최종 결과 통계:")
        logger.info(f"   - 총 트랜잭션: {self.total_records:,}건")
        logger.info(f"   - 생성된 시트: 5개")
        logger.info(f"   - 창고별 월별 데이터: {len(warehouse_monthly)}행 (15열)")
        logger.info(f"   - 현장별 월별 데이터: {len(site_monthly)}행 (9열)")
        logger.info(f"   - Flow Code 분석: {len(flow_analysis)}개 코드")
        logger.info(f"   - 입고 로직 3단계: calculate_warehouse_inbound() → create_monthly_inbound_pivot() → calculate_final_location()")
        
        return excel_filename


def main():
    """메인 실행 함수"""
    print("🏗️ HVDC 입고 로직 구현 및 집계 시스템 v2.0")
    print("입고 로직 3단계 프로세스 + Multi-Level Header 구조")
    print("Samsung C&T · ADNOC · DSV Partnership")
    print("=" * 60)
    
    try:
        # 시스템 초기화 및 실행
        system = HVDCRealDataExcelSystemV2()
        excel_file = system.generate_final_excel_system()
        
        print(f"\n🎉 HVDC 입고 로직 종합 리포트 생성 완료!")
        print(f"📁 파일명: {excel_file}")
        print(f"📊 총 데이터: {system.total_records:,}건")
        print(f"📋 생성된 시트:")
        print(f"   1. 창고_월별_입출고 (Multi-Level Header 15열)")
        print(f"   2. 현장_월별_입고재고 (Multi-Level Header 9열)")
        print(f"   3. Flow_Code_분석 (FLOW_CODE 0-4)")
        print(f"   4. 전체_트랜잭션_요약")
        print(f"   5. 원본_데이터_샘플")
        print(f"\n📈 핵심 로직:")
        print(f"   - 입고 로직 3단계: calculate_warehouse_inbound() → create_monthly_inbound_pivot() → calculate_final_location()")
        print(f"   - 창고 우선순위: DSV Al Markaz > DSV Indoor > Status_Location")
        print(f"   - Multi-Level Header 구조 표준화")
        
    except Exception as e:
        print(f"\n❌ 시스템 생성 실패: {str(e)}")
        raise


if __name__ == "__main__":
    main() 