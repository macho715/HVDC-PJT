#!/usr/bin/env python3
"""
HVDC 프로젝트 상세 창고-화물 매핑 분석
HVDC CODE 1 (창고) × HVDC CODE 3 (화물 유형) 매트릭스 분석
"""

import pandas as pd
import numpy as np

def analyze_detailed_warehouse_mapping():
    """상세 창고-화물 매핑 분석"""
    
    print("🏢 HVDC 상세 창고-화물 매핑 분석")
    print("=" * 60)
    
    # 사용자 제공 데이터를 DataFrame으로 구성
    data = [
        ['AAA Storage', 'Dg Warehouse', 54701, 0, 54701],
        ['DSV Al Markaz', 'ALL', 7000, 1966800, 1973800],
        ['DSV Al Markaz', 'HE', 1188, 0, 1188],
        ['DSV Indoor', 'ALL', 22422, 2114850, 2137272],
        ['DSV Indoor', 'HE', 1032040, 646435, 1678475],
        ['DSV Indoor', 'HE_LOCAL', 2748, 0, 2748],
        ['DSV Indoor', 'MOSB', 315, 0, 315],
        ['DSV Indoor', 'PPL', 2570, 0, 2570],
        ['DSV Indoor', 'SCT', 34468, 0, 34468],
        ['DSV Indoor', 'SIM', 16571, 141874, 158445],
        ['DSV Indoor', 'SKM', 921, 0, 921],
        ['DSV MZP', 'ALL', 3672, 429000, 432672],
        ['DSV Outdoor', 'ALL', 18383, 2491308, 2509692],
        ['DSV Outdoor', 'ALM', 9390, 0, 9390],
        ['DSV Outdoor', 'HE', 537886, 249053, 786939],
        ['DSV Outdoor', 'MOSB', 12015, 0, 12015],
        ['DSV Outdoor', 'NIE', 4112, 0, 4112],
        ['DSV Outdoor', 'SCT', 878463, 0, 878463],
        ['DSV Outdoor', 'SEI', 33448, 0, 33448],
        ['DSV Outdoor', 'SIM', 690351, 0, 690351],
        ['(비어 있음)', 'ALL', 136805, 0, 136805],
        ['(비어 있음)', 'SCT', 327, 0, 327],
        ['(비어 있음)', 'SIM', 519, 0, 519]
    ]
    
    df = pd.DataFrame(data, columns=['Warehouse', 'Cargo_Type', 'Handling', 'Rent', 'Total'])
    
    print("=== 1. 화물 유형별 전체 분석 ===")
    
    cargo_analysis = df.groupby('Cargo_Type').agg({
        'Handling': 'sum',
        'Rent': 'sum', 
        'Total': 'sum',
        'Warehouse': 'count'
    }).round(0)
    cargo_analysis.rename(columns={'Warehouse': 'Warehouse_Count'}, inplace=True)
    cargo_analysis = cargo_analysis.sort_values('Total', ascending=False)
    
    # 비중 계산
    cargo_analysis['Percentage'] = (cargo_analysis['Total'] / cargo_analysis['Total'].sum() * 100).round(1)
    
    print("🚛 **화물 유형별 집계:**")
    print(cargo_analysis.to_string())
    
    print(f"\n=== 2. 창고별 화물 유형 분포 ===")
    
    warehouse_analysis = df.groupby('Warehouse').agg({
        'Handling': 'sum',
        'Rent': 'sum',
        'Total': 'sum',
        'Cargo_Type': 'count'
    }).round(0)
    warehouse_analysis.rename(columns={'Cargo_Type': 'Cargo_Types_Count'}, inplace=True)
    warehouse_analysis = warehouse_analysis.sort_values('Total', ascending=False)
    
    print("🏪 **창고별 집계:**")
    print(warehouse_analysis.to_string())
    
    print(f"\n=== 3. 브랜드별 창고 분산도 ===")
    
    # 주요 브랜드별 창고 이용 패턴
    major_brands = ['HE', 'SIM', 'SCT', 'ALL']
    
    for brand in major_brands:
        brand_data = df[df['Cargo_Type'] == brand]
        if len(brand_data) > 0:
            print(f"\n📦 **{brand} ({get_brand_name(brand)})**")
            print(f"  총 비용: {brand_data['Total'].sum():,.0f} AED")
            print(f"  이용 창고: {len(brand_data)}개")
            
            # 창고별 비중
            brand_warehouses = brand_data.groupby('Warehouse')['Total'].sum().sort_values(ascending=False)
            for warehouse, cost in brand_warehouses.items():
                percentage = cost / brand_data['Total'].sum() * 100
                print(f"    - {warehouse}: {cost:,.0f} AED ({percentage:.1f}%)")
    
    print(f"\n=== 4. 비용 구조 분석 ===")
    
    # HANDLING vs RENT 비율 분석
    total_handling = df['Handling'].sum()
    total_rent = df['Rent'].sum()
    total_cost = df['Total'].sum()
    
    print(f"💰 **전체 비용 구조:**")
    print(f"  HANDLING: {total_handling:,.0f} AED ({total_handling/total_cost*100:.1f}%)")
    print(f"  RENT: {total_rent:,.0f} AED ({total_rent/total_cost*100:.1f}%)")
    print(f"  총합: {total_cost:,.0f} AED")
    
    # 화물 유형별 비용 구조
    print(f"\n📊 **화물 유형별 비용 구조:**")
    for cargo_type in ['ALL', 'HE', 'SIM', 'SCT']:
        cargo_data = df[df['Cargo_Type'] == cargo_type]
        if len(cargo_data) > 0:
            handling_sum = cargo_data['Handling'].sum()
            rent_sum = cargo_data['Rent'].sum()
            total_sum = cargo_data['Total'].sum()
            
            handling_pct = handling_sum / total_sum * 100 if total_sum > 0 else 0
            rent_pct = rent_sum / total_sum * 100 if total_sum > 0 else 0
            
            print(f"  {cargo_type}: HANDLING {handling_pct:.1f}% / RENT {rent_pct:.1f}%")
    
    print(f"\n=== 5. 특수 케이스 분석 ===")
    
    # HANDLING만 있는 케이스 (일회성 작업)
    handling_only = df[(df['Rent'] == 0) & (df['Handling'] > 0)]
    print(f"🔧 **HANDLING만 있는 케이스 ({len(handling_only)}건):**")
    handling_only_sorted = handling_only.sort_values('Handling', ascending=False)
    for _, row in handling_only_sorted.head(10).iterrows():
        print(f"  {row['Warehouse']} - {row['Cargo_Type']}: {row['Handling']:,.0f} AED")
    
    # RENT만 있는 케이스 (순수 보관)
    rent_only = df[(df['Handling'] == 0) & (df['Rent'] > 0)]
    print(f"\n🏬 **RENT만 있는 케이스 ({len(rent_only)}건):**")
    for _, row in rent_only.iterrows():
        print(f"  {row['Warehouse']} - {row['Cargo_Type']}: {row['Rent']:,.0f} AED")
    
    print(f"\n=== 6. 위험물 및 특수 화물 ===")
    
    # 위험물 창고 (AAA Storage - Dg Warehouse)
    dangerous_goods = df[df['Cargo_Type'] == 'Dg Warehouse']
    if len(dangerous_goods) > 0:
        print(f"⚠️ **위험물 창고 (Dangerous Goods):**")
        for _, row in dangerous_goods.iterrows():
            print(f"  {row['Warehouse']}: {row['Total']:,.0f} AED (HANDLING만)")
    
    # 현지 화물 (HE_LOCAL)
    local_cargo = df[df['Cargo_Type'] == 'HE_LOCAL']
    if len(local_cargo) > 0:
        print(f"\n🏠 **현지 화물 (HE_LOCAL):**")
        for _, row in local_cargo.iterrows():
            print(f"  {row['Warehouse']}: {row['Total']:,.0f} AED")
    
    print(f"\n=== 7. 창고 전문화 분석 ===")
    
    # 각 창고의 주력 화물 유형
    print(f"🎯 **창고별 주력 화물:**")
    for warehouse in df['Warehouse'].unique():
        if warehouse != '(비어 있음)':
            wh_data = df[df['Warehouse'] == warehouse].sort_values('Total', ascending=False)
            main_cargo = wh_data.iloc[0]
            total_wh = wh_data['Total'].sum()
            main_pct = main_cargo['Total'] / total_wh * 100
            
            print(f"  {warehouse}: {main_cargo['Cargo_Type']} ({main_pct:.1f}%)")

def get_brand_name(code):
    """브랜드 코드를 실제 이름으로 변환"""
    brand_names = {
        'HE': 'Hitachi Energy',
        'SIM': 'Siemens', 
        'SCT': 'Samsung C&T',
        'ALL': '일반/전체',
        'HE_LOCAL': 'Hitachi Local',
        'MOSB': 'MOSB',
        'PPL': 'PPL',
        'SKM': 'SKM',
        'NIE': 'NIE',
        'ALM': 'ALM',
        'SEI': 'SEI',
        'Dg Warehouse': 'Dangerous Goods'
    }
    return brand_names.get(code, code)

if __name__ == "__main__":
    analyze_detailed_warehouse_mapping() 