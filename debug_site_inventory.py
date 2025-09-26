#!/usr/bin/env python3
"""
Debug script to understand site inventory overcounting issue
"""

from hvdc_excel_reporter_final import HVDCExcelReporterFinal
import pandas as pd

def debug_site_inventory():
    """Debug the site inventory calculation"""
    print("🔍 Debugging Site Inventory Overcounting Issue")
    print("=" * 60)
    
    # Initialize reporter and calculate statistics
    reporter = HVDCExcelReporterFinal()
    stats = reporter.calculate_warehouse_statistics()
    df = stats['processed_data'].copy()
    
    # Check Status_Location distribution
    print("📊 Status_Location Distribution (Expected values):")
    site_cols = ['AGI', 'DAS', 'MIR', 'SHU']
    for site in site_cols:
        count = len(df[df['Status_Location'] == site])
        print(f"  {site}: {count}개")
    
    print("\n🔍 Analyzing the issue...")
    
    # Check for duplicates in Status_Location
    print("\n📋 Checking for duplicates in Status_Location:")
    for site in site_cols:
        site_data = df[df['Status_Location'] == site]
        print(f"\n{site} Status_Location data:")
        print(f"  Total rows: {len(site_data)}")
        print(f"  Unique PKG_IDs: {site_data['PKG_ID'].nunique() if 'PKG_ID' in site_data.columns else 'N/A'}")
        
        # Check if there are multiple rows per PKG_ID
        if 'PKG_ID' in site_data.columns:
            duplicates = site_data.groupby('PKG_ID').size()
            if duplicates.max() > 1:
                print(f"  ⚠️ Found {len(duplicates[duplicates > 1])} PKG_IDs with multiple rows")
                print(f"  Max duplicates per PKG_ID: {duplicates.max()}")
    
    # Check the current site sheet calculation
    print("\n🔍 Current site sheet calculation:")
    site_sheet = reporter.create_site_monthly_sheet(stats)
    last = site_sheet.iloc[-1]
    
    print("Current results:")
    for site in site_cols:
        print(f"  {site}: {last[f'재고_{site}']} PKG")
    
    # Let's check what the inventory calculation is actually counting
    print("\n🔍 Detailed inventory calculation analysis:")
    for site in site_cols:
        site_data = df[df['Status_Location'] == site]
        print(f"\n{site} inventory calculation:")
        print(f"  Status_Location = {site}: {len(site_data)} rows")
        
        # Check the date condition
        if site in df.columns:
            with_date = site_data[site_data[site].notna()]
            print(f"  With {site} date: {len(with_date)} rows")
            
            # Check Pkg values
            if 'Pkg' in with_date.columns:
                total_pkg = with_date['Pkg'].sum()
                print(f"  Total Pkg: {total_pkg}")
                
                # Check for any Pkg > 1
                high_pkg = with_date[with_date['Pkg'] > 1]
                if len(high_pkg) > 0:
                    print(f"  ⚠️ Found {len(high_pkg)} rows with Pkg > 1")
                    print(f"  Max Pkg value: {high_pkg['Pkg'].max()}")
    
    return df

if __name__ == "__main__":
    debug_site_inventory() 