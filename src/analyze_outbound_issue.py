#!/usr/bin/env python3
"""
창고별 출고 계산 문제 분석 및 해결 방안
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_outbound_patterns():
    """창고별 출고 패턴 분석"""
    print('🔍 창고별 출고 계산 문제 분석')
    print('=' * 60)

    # 실제 데이터 로드
    hitachi_df = pd.read_excel('../data/HVDC WAREHOUSE_HITACHI(HE).xlsx', sheet_name='Case List')
    print(f'📊 HITACHI 데이터: {len(hitachi_df)} 건')

    # wh handling 컬럼 분석
    print('\n📋 wh handling 컬럼 분석:')
    print(f'   타입: {hitachi_df["wh handling"].dtype}')
    print(f'   값 분포: {hitachi_df["wh handling"].value_counts().sort_index()}')

    # Status_Storage 패턴 분석
    print('\n📋 Status_Storage 패턴 분석:')
    storage_counts = hitachi_df["Status_Storage"].value_counts()
    print(f'   값 분포: {storage_counts}')

    # 창고→현장 이동 패턴 
    print('\n📋 창고 vs 현장 분포:')
    warehouse_count = (hitachi_df['Status_Storage'] == 'warehouse').sum()
    site_count = (hitachi_df['Status_Storage'] == 'site').sum()
    pre_arrival_count = (hitachi_df['Status_Storage'] == 'Pre Arrival').sum()
    print(f'   Warehouse: {warehouse_count}건')
    print(f'   Site: {site_count}건') 
    print(f'   Pre Arrival: {pre_arrival_count}건')

    # 창고별 현재 위치 분석
    print('\n📋 창고별 Status_Location 분석:')
    warehouse_locations = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'AAA  Storage', 'Hauler Indoor', 'MOSB', 'DHL Warehouse']
    
    for wh in warehouse_locations:
        wh_location_count = (hitachi_df['Status_Location'] == wh).sum()
        if wh_location_count > 0:
            print(f'   {wh}: {wh_location_count}건 (현재 위치)')

    # 실제 출고 패턴 분석
    print('\n🎯 출고 계산 방안 분석:')
    
    # 방안 1: wh handling > 0인 경우를 출고로 계산
    wh_handling_positive = (hitachi_df['wh handling'] > 0).sum()
    print(f'1. wh handling > 0: {wh_handling_positive}건')
    
    # 방안 2: Status_Storage가 warehouse에서 site로 변경된 건수
    warehouse_to_site = site_count  # site에 있다는 것은 창고에서 나왔다는 의미
    print(f'2. Warehouse→Site 이동: {warehouse_to_site}건')
    
    # 방안 3: 창고 컬럼에 날짜가 있으면서 현재는 다른 위치에 있는 경우
    print('\n📋 창고별 출고 가능 건수 분석:')
    total_potential_outbound = 0
    
    for wh in warehouse_locations:
        if wh in hitachi_df.columns:
            # 해당 창고 컬럼에 날짜가 있는 건수 (입고)
            wh_inbound = hitachi_df[wh].notna().sum()
            
            # 현재 해당 창고에 있는 건수 (재고)
            wh_current = (hitachi_df['Status_Location'] == wh).sum()
            
            # 잠재적 출고 = 입고 - 현재재고
            potential_outbound = wh_inbound - wh_current
            
            if wh_inbound > 0:
                print(f'   {wh}: 입고 {wh_inbound}건, 현재 {wh_current}건, 잠재출고 {potential_outbound}건')
                total_potential_outbound += max(0, potential_outbound)
    
    print(f'\n📊 총 잠재적 출고: {total_potential_outbound}건')
    
    return {
        'warehouse_count': warehouse_count,
        'site_count': site_count,
        'total_potential_outbound': total_potential_outbound
    }

if __name__ == "__main__":
    results = analyze_outbound_patterns()
    
    print('\n🎯 권장 출고 계산 로직:')
    print('- 각 창고별 입고 건수에서 현재 재고를 뺀 값을 출고로 계산')
    print('- 월별 분산은 입고 패턴을 기반으로 비례 배분') 