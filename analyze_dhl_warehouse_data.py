#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DHL Warehouse 데이터 분석 스크립트
매칭 실패 원인 분석
"""

import pandas as pd

def analyze_dhl_warehouse_data():
    """DHL Warehouse 데이터 분석"""
    
    print("🔍 DHL Warehouse 데이터 상세 분석")
    print("=" * 50)
    
    # 원본 데이터 로드
    hitachi_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_HITACHI(HE).xlsx'
    used_data_path = r'MACHO_통합관리_20250702_205301\01_원본파일\MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    
    df_hitachi = pd.read_excel(hitachi_path)
    df_used = pd.read_excel(used_data_path)
    
    print(f"✅ HITACHI 원본: {df_hitachi.shape[0]}행")
    print(f"✅ 사용된 데이터: {df_used.shape[0]}행")
    
    # DHL Warehouse가 있는 레코드만 필터링
    dhl_records = df_hitachi[df_hitachi['DHL Warehouse'].notna()]
    print(f"\n📊 DHL Warehouse 유효 레코드: {len(dhl_records)}개")
    
    # DHL Warehouse 날짜별 분포
    print("\n📋 DHL Warehouse 날짜별 분포:")
    date_distribution = dhl_records['DHL Warehouse'].value_counts()
    for date, count in date_distribution.items():
        print(f"  {date}: {count}개")
    
    # 매칭 키 확인
    matching_cols = ['no.', 'Shipment Invoice No.', 'HVDC CODE', 'HVDC CODE 1']
    
    print(f"\n🔍 DHL Warehouse 레코드의 매칭 키 샘플:")
    sample_records = dhl_records[matching_cols + ['DHL Warehouse']].head(10)
    for idx, row in sample_records.iterrows():
        print(f"  no.:{row['no.']} | Invoice:{row['Shipment Invoice No.']} | HVDC:{row['HVDC CODE']} | DHL:{row['DHL Warehouse']}")
    
    # 사용된 데이터에서 해당 키들 확인
    print(f"\n🔍 사용된 데이터에서 동일 키 검색:")
    
    for idx, row in sample_records.head(5).iterrows():
        condition = (
            (df_used['no.'] == row['no.']) &
            (df_used['Shipment Invoice No.'] == row['Shipment Invoice No.']) &
            (df_used['HVDC CODE'] == row['HVDC CODE']) &
            (df_used['HVDC CODE 1'] == row['HVDC CODE 1'])
        )
        matches = df_used[condition]
        print(f"  키 {row['no.']}번: {'매칭됨' if len(matches) > 0 else '매칭 실패'} ({len(matches)}개)")
    
    # Vendor 분포 확인
    if 'VENDOR' in df_used.columns:
        print(f"\n📊 사용된 데이터 Vendor 분포:")
        vendor_dist = df_used['VENDOR'].value_counts()
        for vendor, count in vendor_dist.items():
            print(f"  {vendor}: {count}개")
    
    # DHL Warehouse 레코드가 HITACHI인지 확인
    print(f"\n🔍 DHL Warehouse 레코드의 특성:")
    if 'Site' in dhl_records.columns:
        site_dist = dhl_records['Site'].value_counts()
        print(f"📋 Site 분포:")
        for site, count in site_dist.items():
            print(f"  {site}: {count}개")
    
    if 'HVDC CODE 1' in dhl_records.columns:
        code1_dist = dhl_records['HVDC CODE 1'].value_counts()
        print(f"📋 HVDC CODE 1 분포:")
        for code, count in code1_dist.items():
            print(f"  {code}: {count}개")

if __name__ == "__main__":
    analyze_dhl_warehouse_data() 