import pandas as pd

# HITACHI 파일 컬럼 확인
print("🔍 HITACHI 파일 컬럼 분석:")
df_h = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx')
print(f"   총 컬럼 수: {len(df_h.columns)}")
print(f"   처음 10개 컬럼: {list(df_h.columns)[:10]}")

# Date 관련 컬럼 검색
date_cols = [col for col in df_h.columns if 'date' in col.lower() or 'time' in col.lower()]
print(f"   Date 관련 컬럼: {date_cols}")

print("\n🔍 SIMENSE 파일 컬럼 분석:")
df_s = pd.read_excel('data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx')
print(f"   총 컬럼 수: {len(df_s.columns)}")
print(f"   처음 10개 컬럼: {list(df_s.columns)[:10]}")

# Date 관련 컬럼 검색
date_cols_s = [col for col in df_s.columns if 'date' in col.lower() or 'time' in col.lower()]
print(f"   Date 관련 컬럼: {date_cols_s}")

# 창고 관련 컬럼 확인
wh_cols = [col for col in df_h.columns if any(x in col.upper() for x in ['DSV', 'AGI', 'DAS', 'MIR', 'SHU'])]
print(f"\n🏢 창고/현장 컬럼: {wh_cols[:5]}...") 