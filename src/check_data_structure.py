#!/usr/bin/env python3
"""
실제 데이터 파일 구조 확인
"""

import pandas as pd
from pathlib import Path
import sys

# 프로젝트 루트 경로
project_root = Path(__file__).parent.parent
data_dir = project_root / 'hvdc_ontology_system' / 'data'

print("📊 실제 데이터 파일 구조 확인")
print("=" * 60)

# HITACHI 데이터 확인
hitachi_file = data_dir / 'HVDC WAREHOUSE_HITACHI(HE).xlsx'
if hitachi_file.exists():
    print(f"\n🔍 HITACHI 파일: {hitachi_file}")
    try:
        hitachi_df = pd.read_excel(hitachi_file)
        print(f"   행 수: {len(hitachi_df):,}")
        print(f"   컬럼 수: {len(hitachi_df.columns)}")
        print(f"   컬럼명:")
        for i, col in enumerate(hitachi_df.columns):
            print(f"     {i+1:2d}. {col}")
        
        print(f"\n   상위 3행 샘플:")
        print(hitachi_df.head(3))
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")

# SIMENSE 데이터 확인  
simense_file = data_dir / 'HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
if simense_file.exists():
    print(f"\n🔍 SIMENSE 파일: {simense_file}")
    try:
        simense_df = pd.read_excel(simense_file)
        print(f"   행 수: {len(simense_df):,}")
        print(f"   컬럼 수: {len(simense_df.columns)}")
        print(f"   컬럼명:")
        for i, col in enumerate(simense_df.columns):
            print(f"     {i+1:2d}. {col}")
            
        print(f"\n   상위 3행 샘플:")
        print(simense_df.head(3))
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")

print("\n✅ 데이터 구조 확인 완료") 