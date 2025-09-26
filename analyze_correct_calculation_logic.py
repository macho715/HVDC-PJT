#!/usr/bin/env python3
"""
올바른 계산 로직 분석 및 구현
창고_월별_입출고, 현장_월별_입고재고 정확한 계산
HVDC 물류 마스터 시스템 v3.4-mini
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def analyze_correct_logic():
    """올바른 계산 로직 분석"""
    print("🔍 올바른 계산 로직 분석 시작")
    print("=" * 60)
    
    # 데이터 로드
    main_source = "MACHO_통합관리_20250702_205301/MACHO_Final_Report_Complete_20250703_230904.xlsx"
    
    try:
        df = pd.read_excel(main_source, engine='openpyxl')
        print(f"✅ 데이터 로드 성공: {len(df)}건, {len(df.columns)}개 컬럼")
        
        # 날짜 컬럼 전처리
        date_columns = ['ETD/ATD', 'ETA/ATA', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                       'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'MIR', 'SHU', 'DAS', 'AGI']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        print("\n📊 데이터 흐름 분석:")
        
        # 1. 창고별 데이터 분석
        print("\n🏭 창고별 실제 데이터 분석:")
        warehouse_cols = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB']
        
        for warehouse in warehouse_cols:
            if warehouse in df.columns:
                total_entries = df[warehouse].notna().sum()
                if total_entries > 0:
                    date_range = f"{df[warehouse].min()} ~ {df[warehouse].max()}"
                    print(f"  {warehouse}: {total_entries}건 ({date_range})")
        
        # 2. 현장별 데이터 분석
        print("\n🏗️ 현장별 실제 데이터 분석:")
        site_cols = ['MIR', 'SHU', 'DAS', 'AGI']
        
        for site in site_cols:
            if site in df.columns:
                total_entries = df[site].notna().sum()
                if total_entries > 0:
                    date_range = f"{df[site].min()} ~ {df[site].max()}"
                    print(f"  {site}: {total_entries}건 ({date_range})")
        
        # 3. 실제 물류 흐름 분석
        print("\n🚚 물류 흐름 분석:")
        
        # 샘플 데이터로 물류 흐름 추적
        sample_data = df.head(10)
        print("샘플 10건의 물류 흐름:")
        
        for idx, row in sample_data.iterrows():
            print(f"\n케이스 {idx+1}: {row['Case No.']}")
            print(f"  현재 위치: {row['Status_Location']}")
            print(f"  목적지: {row['Site']}")
            
            # 창고별 날짜 확인
            warehouse_dates = []
            for warehouse in warehouse_cols:
                if warehouse in row and pd.notna(row[warehouse]):
                    warehouse_dates.append(f"{warehouse}: {row[warehouse]}")
            
            if warehouse_dates:
                print(f"  창고 경유: {', '.join(warehouse_dates)}")
            
            # 현장별 날짜 확인
            site_dates = []
            for site in site_cols:
                if site in row and pd.notna(row[site]):
                    site_dates.append(f"{site}: {row[site]}")
            
            if site_dates:
                print(f"  현장 도착: {', '.join(site_dates)}")
        
        # 4. 올바른 계산 로직 제안
        print("\n💡 올바른 계산 로직:")
        print("=" * 50)
        
        print("\n🏭 창고_월별_입출고 계산:")
        print("1. 입고: 해당 월에 해당 창고에 도착한 건수")
        print("   - 각 창고별 날짜 컬럼에서 해당 월에 해당하는 건수")
        print("2. 출고: 해당 창고에서 다음 단계로 이동한 건수")
        print("   - 창고 → 현장 또는 창고 → 다른 창고")
        print("   - 창고 날짜 이후에 다른 위치 날짜가 있는 건수")
        
        print("\n🏗️ 현장_월별_입고재고 계산:")
        print("1. 입고: 해당 월에 해당 현장에 도착한 건수")
        print("   - 각 현장별 날짜 컬럼에서 해당 월에 해당하는 건수")
        print("2. 재고: 해당 월 말 기준 해당 현장에 있는 총 건수")
        print("   - 해당 현장에 도착했지만 아직 다른 곳으로 이동하지 않은 건수")
        print("   - Status_Location이 해당 현장인 건수")
        
        return df
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return None

def test_correct_calculation(df):
    """올바른 계산 로직 테스트"""
    print("\n🧪 올바른 계산 로직 테스트")
    print("=" * 50)
    
    # 테스트 기간: 2024-01
    test_period = pd.Timestamp('2024-01-01')
    
    print(f"테스트 기간: {test_period.strftime('%Y-%m')}")
    
    # 1. 창고별 입고 계산 테스트
    print("\n🏭 창고별 입고 계산 테스트:")
    
    warehouse_cols = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB']
    
    for warehouse in warehouse_cols:
        if warehouse in df.columns:
            # 해당 월에 해당 창고에 입고된 건수
            warehouse_dates = df[warehouse].dropna()
            month_mask = warehouse_dates.dt.to_period('M') == test_period.to_period('M')
            inbound_count = month_mask.sum()
            
            if inbound_count > 0:
                print(f"  {warehouse}: {inbound_count}건")
    
    # 2. 현장별 입고 계산 테스트
    print("\n🏗️ 현장별 입고 계산 테스트:")
    
    site_cols = ['MIR', 'SHU', 'DAS', 'AGI']
    
    for site in site_cols:
        if site in df.columns:
            # 해당 월에 해당 현장에 입고된 건수
            site_dates = df[site].dropna()
            month_mask = site_dates.dt.to_period('M') == test_period.to_period('M')
            inbound_count = month_mask.sum()
            
            if inbound_count > 0:
                print(f"  {site}: {inbound_count}건")
    
    # 3. 현장별 재고 계산 테스트
    print("\n📦 현장별 재고 계산 테스트:")
    
    for site in site_cols:
        if 'Status_Location' in df.columns:
            # 현재 해당 현장에 있는 총 건수
            current_inventory = (df['Status_Location'] == site).sum()
            
            if current_inventory > 0:
                print(f"  {site}: {current_inventory}건 (현재 재고)")

def implement_correct_calculation():
    """올바른 계산 로직 구현"""
    print("\n🔧 올바른 계산 로직 구현")
    print("=" * 50)
    
    # 데이터 로드
    main_source = "MACHO_통합관리_20250702_205301/MACHO_Final_Report_Complete_20250703_230904.xlsx"
    df = pd.read_excel(main_source, engine='openpyxl')
    
    # 날짜 컬럼 전처리
    date_columns = ['ETD/ATD', 'ETA/ATA', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                   'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'MIR', 'SHU', 'DAS', 'AGI']
    
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 1. 창고_월별_입출고 올바른 계산
    print("\n🏭 창고_월별_입출고 올바른 계산:")
    
    warehouse_cols = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB']
    site_cols = ['MIR', 'SHU', 'DAS', 'AGI']
    
    # 월별 기간 설정
    periods = pd.date_range(start='2024-01-01', end='2025-06-01', freq='MS')
    
    warehouse_results = []
    
    for period in periods:
        month_str = period.strftime('%Y-%m')
        row_data = {'Month': month_str}
        
        for warehouse in warehouse_cols:
            if warehouse in df.columns:
                # 입고: 해당 월에 해당 창고에 도착한 건수
                warehouse_dates = df[warehouse].dropna()
                month_mask = warehouse_dates.dt.to_period('M') == period.to_period('M')
                inbound_count = month_mask.sum()
                
                # 출고: 해당 창고에서 다음 단계로 이동한 건수
                # 창고 방문 후 현장으로 이동한 건수 계산
                warehouse_visited = df[warehouse].notna()
                outbound_count = 0
                
                if warehouse_visited.any():
                    # 해당 창고를 방문한 건들 중에서 현장으로 이동한 건수
                    for site in site_cols:
                        if site in df.columns:
                            # 창고 방문 후 현장에 도착한 건수
                            warehouse_then_site = warehouse_visited & df[site].notna()
                            # 해당 월에 창고에서 현장으로 이동한 건수
                            site_dates = df[df[warehouse].notna()][site].dropna()
                            if len(site_dates) > 0:
                                site_month_mask = site_dates.dt.to_period('M') == period.to_period('M')
                                outbound_count += site_month_mask.sum()
                
                row_data[f'{warehouse}_입고'] = inbound_count
                row_data[f'{warehouse}_출고'] = outbound_count
        
        warehouse_results.append(row_data)
    
    # 결과 출력 (처음 5개월)
    print("처음 5개월 결과:")
    for i, result in enumerate(warehouse_results[:5]):
        print(f"\n{result['Month']}:")
        for key, value in result.items():
            if key != 'Month' and value > 0:
                print(f"  {key}: {value}")
    
    # 2. 현장_월별_입고재고 올바른 계산
    print("\n🏗️ 현장_월별_입고재고 올바른 계산:")
    
    site_results = []
    
    for period in periods:
        month_str = period.strftime('%Y-%m')
        row_data = {'Month': month_str}
        
        for site in site_cols:
            if site in df.columns:
                # 입고: 해당 월에 해당 현장에 도착한 건수
                site_dates = df[site].dropna()
                month_mask = site_dates.dt.to_period('M') == period.to_period('M')
                inbound_count = month_mask.sum()
                
                # 재고: 해당 월 말 기준 해당 현장에 있는 총 건수
                # 현재 Status_Location이 해당 현장인 건수
                if 'Status_Location' in df.columns:
                    current_inventory = (df['Status_Location'] == site).sum()
                else:
                    current_inventory = 0
                
                row_data[f'{site}_입고'] = inbound_count
                row_data[f'{site}_재고'] = current_inventory
        
        site_results.append(row_data)
    
    # 결과 출력 (처음 5개월)
    print("처음 5개월 결과:")
    for i, result in enumerate(site_results[:5]):
        print(f"\n{result['Month']}:")
        for key, value in result.items():
            if key != 'Month' and value > 0:
                print(f"  {key}: {value}")
    
    return warehouse_results, site_results

def main():
    """메인 실행 함수"""
    print("🏗️ 올바른 계산 로직 분석 및 구현")
    print("Samsung C&T · ADNOC · DSV Partnership")
    print("=" * 60)
    
    # 1. 데이터 구조 분석
    df = analyze_correct_logic()
    
    if df is not None:
        # 2. 계산 로직 테스트
        test_correct_calculation(df)
        
        # 3. 올바른 계산 구현
        warehouse_results, site_results = implement_correct_calculation()
        
        print(f"\n🎯 다음 단계:")
        print("1. 올바른 계산 로직을 새로운 보고서 생성기에 적용")
        print("2. 수정된 Excel 파일 재생성")
        print("3. 결과 검증")

if __name__ == "__main__":
    main() 