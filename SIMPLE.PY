#!/usr/bin/env python3
"""
HVDC 프로젝트 정확한 재고 계산 함수
제공된 정확한 숫자들과 일치하는 로직 구현

목표 결과:
HITACHI: 5,126개, Simense: 1,853개, Total: 6,979개
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class CorrectInventoryCalculator:
    """
    정확한 재고 계산기
    복잡한 날짜 추적 대신 현재 상태 기반 단순 집계
    """
    
    def __init__(self):
        # 위치 매핑 정의
        self.location_mappings = {
            'sites': ['AGI', 'DAS', 'MIR', 'SHU'],
            'warehouses': [
                'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP',
                'MOSB', 'AAA Storage', 'Hauler Indoor', 'DHL Warehouse'
            ],
            'special': ['Pre Arrival']
        }
        
        # 벤더 매핑 정의 (정확한 분류를 위해)
        self.vendor_mappings = {
            'HITACHI': ['HITACHI', 'HE', 'Hitachi'],
            'SIMENSE': ['SIMENSE', 'SIM', 'Siemens', 'SIEMENS']
        }
    
    def calculate_current_inventory_snapshot(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        현재 시점 기준 정확한 재고 계산
        
        핵심 원리:
        1. 각 아이템의 현재 위치만 중요함
        2. 벤더별 정확한 분류
        3. 단순 카운트 (날짜 무관)
        
        Args:
            df: HVDC 데이터프레임
            
        Returns:
            위치별/벤더별 재고 현황 딕셔너리
        """
        
        # Step 1: 데이터 정제 및 준비
        df_clean = self._prepare_data(df)
        
        # Step 2: 현재 위치 정확히 계산
        df_clean = self._calculate_current_location(df_clean)
        
        # Step 3: 벤더 정확히 분류
        df_clean = self._classify_vendor_correctly(df_clean)
        
        # Step 4: 위치별/벤더별 집계
        inventory_result = self._aggregate_by_location_vendor(df_clean)
        
        return inventory_result
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 정제 및 준비 (온톨로지 매핑 기준 적용)
        """
        df_clean = df.copy()

        # 1. Vendor 컬럼 생성: 'HVDC CODE 3' → vendor_mappings 적용
        vendor_map = {
            'HE': 'HITACHI', 'HITACHI': 'HITACHI',
            'SIM': 'SIMENSE', 'SIMENSE': 'SIMENSE', 'SIEMENS': 'SIMENSE',
            'SCT': 'SAMSUNG', 'SAMSUNG': 'SAMSUNG',
            'ZEN': 'ZENER', 'ZENER': 'ZENER', 'ETC': 'ETC'
        }
        if 'HVDC CODE 3' in df_clean.columns:
            df_clean['Vendor'] = df_clean['HVDC CODE 3'].map(lambda x: vendor_map.get(str(x).strip().upper(), 'Other'))
        else:
            df_clean['Vendor'] = 'Unknown'

        # 2. Location 컬럼 생성: 여러 위치 컬럼 중 가장 최근 날짜가 있는 컬럼명
        location_candidates = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP',
            'MOSB', 'AAA  Storage', 'Hauler Indoor'
        ]
        def find_latest_location(row):
            latest_date = None
            latest_loc = 'Unknown'
            for loc in location_candidates:
                if loc in row and pd.notna(row[loc]):
                    try:
                        d = pd.to_datetime(row[loc], errors='coerce')
                        if pd.notna(d) and (latest_date is None or d > latest_date):
                            latest_date = d
                            latest_loc = loc
                    except Exception:
                        continue
            return latest_loc
        df_clean['Location'] = df_clean.apply(find_latest_location, axis=1)

        # 3. 필수 컬럼 기본값 보완
        required_cols = ['Case No.', 'Vendor', 'Location']
        for col in required_cols:
            if col not in df_clean.columns:
                print(f"경고: {col} 컬럼이 없습니다. 기본값으로 설정합니다.")
                if col == 'Case No.':
                    df_clean[col] = df_clean.index.astype(str)
                elif col == 'Vendor':
                    df_clean[col] = 'Unknown'
                elif col == 'Location':
                    df_clean[col] = 'Unknown'

        return df_clean
    
    def _calculate_current_location(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        현재 위치 정확히 계산
        
        우선순위 로직:
        1. Status_Location이 명확하면 그것 사용
        2. 그렇지 않으면 최신 날짜 컬럼 기준으로 위치 결정
        3. Pre Arrival 상태 정확히 식별
        """
        
        def determine_current_location(row):
            # 1. Status_Location이 유효한 경우
            if pd.notna(row.get('Status_Location')) and row['Status_Location'] != 'Unknown':
                return row['Status_Location']
            
            # 2. Status_Current가 'Pre Arrival'인 경우
            if row.get('Status_Current') == 'Pre Arrival' or row.get('Status_Current') == 'pre_arrival':
                return 'Pre Arrival'
            
            # 3. 날짜 컬럼들 중 가장 최신 위치 찾기
            latest_date = None
            latest_location = 'Unknown'
            
            # 모든 위치 컬럼 체크
            all_locations = (self.location_mappings['sites'] + 
                           self.location_mappings['warehouses'])
            
            for location in all_locations:
                if location in row.index and pd.notna(row[location]):
                    try:
                        location_date = pd.to_datetime(row[location])
                        if latest_date is None or location_date > latest_date:
                            latest_date = location_date
                            latest_location = location
                    except:
                        continue
            
            return latest_location if latest_location != 'Unknown' else 'DSV Indoor'
        
        # 현재 위치 계산 적용
        df['Current_Location'] = df.apply(determine_current_location, axis=1)
        
        return df
    
    def _classify_vendor_correctly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        벤더 정확히 분류
        """
        
        def classify_vendor(vendor_str):
            if pd.isna(vendor_str):
                return 'Unknown'
            
            vendor_upper = str(vendor_str).upper().strip()
            
            # HITACHI 계열 확인
            for hitachi_variant in self.vendor_mappings['HITACHI']:
                if hitachi_variant.upper() in vendor_upper:
                    return 'HITACHI'
            
            # SIMENSE 계열 확인
            for simense_variant in self.vendor_mappings['SIMENSE']:
                if simense_variant.upper() in vendor_upper:
                    return 'SIMENSE'
            
            return 'Other'
        
        df['Vendor_Clean'] = df['Vendor'].apply(classify_vendor)
        
        return df
    
    def _aggregate_by_location_vendor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        위치별/벤더별 집계
        """
        
        # 기본 집계
        location_vendor_counts = df.groupby(['Current_Location', 'Vendor_Clean']).size().unstack(fill_value=0)
        
        # 결과 구조화
        result = {
            'by_location_vendor': {},
            'totals_by_vendor': {},
            'totals_by_location': {},
            'grand_total': len(df)
        }
        
        # 모든 벤더 타입 수집 (HITACHI, SIMENSE, Unknown, Other 등)
        all_vendors = set()
        if not location_vendor_counts.empty:
            all_vendors = set(location_vendor_counts.columns)
        
        # 기본 벤더들 추가
        all_vendors.update(['HITACHI', 'SIMENSE', 'Unknown', 'Other'])
        
        # 위치별/벤더별 상세 집계
        for location in location_vendor_counts.index:
            result['by_location_vendor'][location] = {}
            
            # 모든 벤더에 대해 카운트 설정
            for vendor in all_vendors:
                if vendor in location_vendor_counts.columns:
                    result['by_location_vendor'][location][vendor] = int(location_vendor_counts.loc[location, vendor])
                else:
                    result['by_location_vendor'][location][vendor] = 0
                
            # 위치별 총합 (HITACHI + SIMENSE만)
            result['totals_by_location'][location] = (
                result['by_location_vendor'][location].get('HITACHI', 0) + 
                result['by_location_vendor'][location].get('SIMENSE', 0)
            )
        
        # 벤더별 총합
        for vendor in all_vendors:
            if vendor in location_vendor_counts.columns:
                result['totals_by_vendor'][vendor] = int(location_vendor_counts[vendor].sum())
            else:
                result['totals_by_vendor'][vendor] = 0
        
        return result
    
    def print_inventory_report(self, result: Dict[str, Any]):
        """
        재고 현황 리포트 출력 (제공된 형식과 동일)
        """
        print("\n" + "="*60)
        print("📊 HVDC 프로젝트 현재 재고 현황")
        print("="*60)
        print(f"{'위치':<20} {'HITACHI':<10} {'Simense':<10} {'Total':<10}")
        print("-"*60)
        
        # 각 위치별 출력
        for location, counts in result['by_location_vendor'].items():
            hitachi_count = counts['HITACHI']
            simense_count = counts['SIMENSE'] 
            total_count = hitachi_count + simense_count
            
            print(f"{location:<20} {hitachi_count:<10} {simense_count:<10} {total_count:<10}")
        
        print("-"*60)
        print(f"{'총합':<20} {result['totals_by_vendor']['HITACHI']:<10} {result['totals_by_vendor']['SIMENSE']:<10} {result['grand_total']:<10}")
        print("="*60)
    
    def validate_against_target(self, result: Dict[str, Any]) -> Dict[str, bool]:
        """
        제공된 목표 숫자와 비교 검증
        """
        target_totals = {
            'HITACHI': 5126,
            'SIMENSE': 1853,
            'Total': 6979
        }
        
        validation = {
            'hitachi_match': result['totals_by_vendor']['HITACHI'] == target_totals['HITACHI'],
            'simense_match': result['totals_by_vendor']['SIMENSE'] == target_totals['SIMENSE'],
            'total_match': result['grand_total'] == target_totals['Total']
        }
        
        print(f"\n🔍 목표 숫자와 비교 검증:")
        print(f"HITACHI: {result['totals_by_vendor']['HITACHI']} vs {target_totals['HITACHI']} {'✅' if validation['hitachi_match'] else '❌'}")
        print(f"SIMENSE: {result['totals_by_vendor']['SIMENSE']} vs {target_totals['SIMENSE']} {'✅' if validation['simense_match'] else '❌'}")
        print(f"Total: {result['grand_total']} vs {target_totals['Total']} {'✅' if validation['total_match'] else '❌'}")
        
        return validation


# 사용 예시
def run_correct_inventory_calculation(excel_file_path: str):
    """
    정확한 재고 계산 실행
    """
    
    # 데이터 로드
    df = pd.read_excel(excel_file_path)
    
    # 정확한 재고 계산기 초기화
    calculator = CorrectInventoryCalculator()
    
    # 현재 재고 현황 계산
    result = calculator.calculate_current_inventory_snapshot(df)
    
    # 결과 출력
    calculator.print_inventory_report(result)
    
    # 목표 숫자와 검증
    validation = calculator.validate_against_target(result)
    
    return result, validation


if __name__ == "__main__":
    # 실행 예시 - 벤더별 파일 통합 처리
    hitachi_file = "data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
    simense_file = "data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
    
    # 벤더별 파일 로드 및 통합
    try:
        df_hitachi = pd.read_excel(hitachi_file)
        df_hitachi['Vendor'] = 'HITACHI'  # 명시적 벤더 지정
        print(f"✅ HITACHI 파일 로드: {len(df_hitachi)}건")
    except Exception as e:
        print(f"❌ HITACHI 파일 로드 실패: {e}")
        df_hitachi = pd.DataFrame()
    
    try:
        df_simense = pd.read_excel(simense_file)
        df_simense['Vendor'] = 'SIMENSE'  # 명시적 벤더 지정
        print(f"✅ SIMENSE 파일 로드: {len(df_simense)}건")
    except Exception as e:
        print(f"❌ SIMENSE 파일 로드 실패: {e}")
        df_simense = pd.DataFrame()
    
    # 데이터 통합
    if not df_hitachi.empty and not df_simense.empty:
        df_combined = pd.concat([df_hitachi, df_simense], ignore_index=True)
        print(f"✅ 통합 데이터: {len(df_combined)}건")
        
        # 정확한 재고 계산기 초기화
        calculator = CorrectInventoryCalculator()
        
        # 현재 재고 현황 계산
        result = calculator.calculate_current_inventory_snapshot(df_combined)
        
        # 결과 출력
        calculator.print_inventory_report(result)
        
        # 목표 숫자와 검증
        validation = calculator.validate_against_target(result)
    else:
        print("❌ 데이터 파일 로드 실패로 계산을 수행할 수 없습니다.")