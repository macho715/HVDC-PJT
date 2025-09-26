#!/usr/bin/env python3
"""
AAA Storage 원본 데이터 확인 스크립트
"""

import pandas as pd
import numpy as np

def show_aaa_raw_data():
    """AAA Storage 원본 데이터 보기"""
    
    print("=" * 60)
    print("🔍 AAA Storage 원본 데이터 분석")
    print("=" * 60)
    
    # HITACHI 데이터 로드
    he_df = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx')
    print(f"HITACHI 데이터: {len(he_df):,}건")
    
    # AAA Storage 컬럼 확인
    aaa_col = 'AAA  Storage'
    if aaa_col in he_df.columns:
        print(f"\n📊 AAA Storage 컬럼 분석:")
        print(f"   컬럼명: \"{aaa_col}\"")
        print(f"   전체 레코드: {len(he_df):,}건")
        print(f"   non-null 레코드: {he_df[aaa_col].notna().sum():,}건")
        print(f"   null 레코드: {he_df[aaa_col].isna().sum():,}건")
        print(f"   데이터 타입: {he_df[aaa_col].dtype}")
        
        # AAA Storage 데이터가 있는 행들 확인
        aaa_data = he_df[he_df[aaa_col].notna()]
        print(f"\n📋 AAA Storage 데이터 샘플 (처음 20개):")
        print(f"{'Index':>5} | {'AAA Storage':>19} | {'Status_Location':>15} | {'ETD/ATD':>19} | {'AGI':>19} | {'DAS':>19} | {'MIR':>19} | {'SHU':>19}")
        print("-" * 140)
        
        for i, (idx, row) in enumerate(aaa_data.head(20).iterrows()):
            aaa_val = str(row[aaa_col])
            status = str(row.get('Status_Location', 'N/A'))
            etd = str(row.get('ETD/ATD', 'N/A'))
            agi = str(row.get('AGI', 'N/A'))
            das = str(row.get('DAS', 'N/A'))
            mir = str(row.get('MIR', 'N/A'))
            shu = str(row.get('SHU', 'N/A'))
            
            print(f"{idx:5d} | {aaa_val:>19} | {status:>15} | {etd:>19} | {agi:>19} | {das:>19} | {mir:>19} | {shu:>19}")
        
        # 월별 분포 확인
        print(f"\n📅 AAA Storage 월별 분포:")
        if len(aaa_data) > 0:
            monthly_dist = aaa_data[aaa_col].dt.strftime('%Y-%m').value_counts().sort_index()
            for month, count in monthly_dist.items():
                print(f"   {month}: {count:,}건")
        
        # 값 분포 확인
        print(f"\n📊 AAA Storage 값 분포:")
        value_counts = aaa_data[aaa_col].value_counts().head(10)
        for val, count in value_counts.items():
            print(f"   {val}: {count:,}건")
            
        # Status_Location과의 관계 확인
        print(f"\n🔗 AAA Storage와 Status_Location 관계:")
        status_dist = aaa_data['Status_Location'].value_counts()
        for status, count in status_dist.items():
            print(f"   {status}: {count:,}건")
        
        # 현장 배송 데이터 확인
        print(f"\n🏗️ AAA Storage에서 현장 배송된 데이터:")
        sites = ['AGI', 'DAS', 'MIR', 'SHU']
        for site in sites:
            if site in aaa_data.columns:
                site_data = aaa_data[aaa_data[site].notna()]
                print(f"   {site}: {len(site_data):,}건")
                
                # 샘플 데이터 보기
                if len(site_data) > 0:
                    print(f"      샘플 배송 날짜: {site_data[site].head(3).tolist()}")
                    
    else:
        print(f"❌ AAA Storage 컬럼을 찾을 수 없습니다.")
        print(f"   사용 가능한 컬럼: {list(he_df.columns)}")

if __name__ == "__main__":
    show_aaa_raw_data() 