#!/usr/bin/env python3
"""
Test script to verify the patched site inventory calculation
"""

from hvdc_excel_reporter_final import HVDCExcelReporterFinal
import numpy as np
import pandas as pd

def test_site_inventory():
    """Test the patched site inventory calculation"""
    print("🧪 Testing Patched Site Inventory Calculation")
    print("=" * 50)
    
    # Initialize reporter and calculate statistics
    reporter = HVDCExcelReporterFinal()
    stats = reporter.calculate_warehouse_statistics()
    
    # Get the site sheet
    site_sheet = reporter.create_site_monthly_sheet(stats)
    
    # Get the last row (Total row)
    last_row = site_sheet.iloc[-1]
    
    print("📊 현장 재고 결과 (패치 적용):")
    print(f"  AGI: {last_row['재고_AGI']} PKG")
    print(f"  DAS: {last_row['재고_DAS']} PKG")
    print(f"  MIR: {last_row['재고_MIR']} PKG")
    print(f"  SHU: {last_row['재고_SHU']} PKG")
    
    total = last_row['재고_AGI'] + last_row['재고_DAS'] + last_row['재고_MIR'] + last_row['재고_SHU']
    print(f"  총계: {total} PKG")
    
    # Expected values
    expected = {
        'AGI': 85,
        'DAS': 1233,
        'MIR': 1254,
        'SHU': 1905,
        'TOTAL': 4477
    }
    
    print("\n🎯 기대값:")
    print(f"  AGI: {expected['AGI']} PKG")
    print(f"  DAS: {expected['DAS']} PKG")
    print(f"  MIR: {expected['MIR']} PKG")
    print(f"  SHU: {expected['SHU']} PKG")
    print(f"  총계: {expected['TOTAL']} PKG")
    
    # Check if results match expected values
    print("\n✅ 검증 결과:")
    agi_match = last_row['재고_AGI'] == expected['AGI']
    das_match = last_row['재고_DAS'] == expected['DAS']
    mir_match = last_row['재고_MIR'] == expected['MIR']
    shu_match = last_row['재고_SHU'] == expected['SHU']
    total_match = total == expected['TOTAL']
    
    print(f"  AGI: {'✅ 일치' if agi_match else '❌ 불일치'}")
    print(f"  DAS: {'✅ 일치' if das_match else '❌ 불일치'}")
    print(f"  MIR: {'✅ 일치' if mir_match else '❌ 불일치'}")
    print(f"  SHU: {'✅ 일치' if shu_match else '❌ 불일치'}")
    print(f"  총계: {'✅ 일치' if total_match else '❌ 불일치'}")
    
    all_match = agi_match and das_match and mir_match and shu_match and total_match
    print(f"\n🎉 전체 결과: {'✅ 모든 값 일치' if all_match else '❌ 일부 값 불일치'}")
    
    # --- 추가: latest DataFrame의 Pkg 합계와 count 출력 ---
    # create_site_monthly_sheet 내부 로직 복제
    df = stats['processed_data'].copy()
    if "PKG_ID" not in df.columns:
        df["PKG_ID"] = df.index.astype(str)
    site_cols = ['AGI', 'DAS', 'MIR', 'SHU']
    month_end = pd.Timestamp('2025-06-30')
    site_mask = df['Status_Location'].isin(site_cols)
    site_rows = df[site_mask].copy()
    row_idx = np.arange(len(site_rows))
    col_idx = site_rows.columns.get_indexer(site_rows['Status_Location'])
    date_vals = site_rows.to_numpy()[row_idx, col_idx]
    site_rows['InvDate'] = pd.to_datetime(date_vals, errors='coerce')
    site_rows = site_rows[site_rows['InvDate'] <= month_end]
    latest = (site_rows.sort_values('InvDate').drop_duplicates('PKG_ID', keep='last'))
    print("\n--- [DEBUG] latest DataFrame ---")
    print(f"latest['Pkg'].sum(): {latest['Pkg'].sum()}")
    print(f"latest['Pkg'].count(): {latest['Pkg'].count()}")
    print(f"latest.shape: {latest.shape}")

    return all_match

if __name__ == "__main__":
    test_site_inventory() 