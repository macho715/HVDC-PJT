#!/usr/bin/env python3
"""
올바른 데이터 경로 확인 스크립트
"""
import pandas as pd
import os

def check_data_files():
    print("🔍 올바른 데이터 경로 확인: hvdc_ontology_system/data/")
    print("=" * 60)
    
    files = {
        'HITACHI': 'hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
        'SIMENSE': 'hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx',
        'INVOICE': 'hvdc_ontology_system/data/HVDC WAREHOUSE_INVOICE.xlsx'
    }
    
    total_records = 0
    for name, path in files.items():
        if os.path.exists(path):
            try:
                df = pd.read_excel(path)
                count = len(df)
                total_records += count
                print(f"✅ {name}: {count:,}건")
                
                # Status_Location 컬럼 확인
                if 'Status_Location' in df.columns:
                    pre_arrival = df['Status_Location'].str.contains('Pre Arrival', case=False, na=False).sum()
                    print(f"   └─ Pre Arrival: {pre_arrival}건")
                    
                    # 주요 현장 확인
                    sites = ['AGI', 'DAS', 'MIR', 'SHU']
                    site_total = 0
                    for site in sites:
                        site_count = df['Status_Location'].str.contains(site, case=False, na=False).sum()
                        site_total += site_count
                        if site_count > 0:
                            print(f"   └─ {site}: {site_count}건")
                    print(f"   └─ 현장 총합: {site_total}건")
                
            except Exception as e:
                print(f"❌ {name}: 오류 - {str(e)}")
        else:
            print(f"❌ {name}: 파일 없음 - {path}")
    
    print(f"\n📊 총 레코드: {total_records:,}건")
    print(f"💡 예상 레코드: 7,573건 (HITACHI 5,346 + SIMENSE 2,227)")
    
    if total_records >= 7000:
        print("✅ 완전한 데이터셋 발견!")
    else:
        print("⚠️  레코드 수가 부족합니다.")

if __name__ == "__main__":
    check_data_files() 