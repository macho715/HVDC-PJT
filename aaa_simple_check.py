import pandas as pd

# HITACHI 데이터 로드
he_df = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx')

# AAA Storage 컬럼 확인  
aaa_col = 'AAA  Storage'
aaa_data = he_df[he_df[aaa_col].notna()]

print(f'AAA Storage 원본 데이터: {len(aaa_data):,}건')
print(f'컬럼명: "{aaa_col}"')
print(f'Status_Location 분포:')
print(aaa_data['Status_Location'].value_counts())
print(f'\nAAA Storage 날짜 분포:')
print(aaa_data[aaa_col].value_counts().head(5))

# 월별 분포
print(f'\n월별 분포:')
monthly = aaa_data[aaa_col].dt.strftime('%Y-%m').value_counts().sort_index()
for month, count in monthly.items():
    print(f'  {month}: {count:,}건')

# 현장 배송 확인
print(f'\n현장 배송 확인:')
sites = ['AGI', 'DAS', 'MIR', 'SHU']
for site in sites:
    site_data = aaa_data[aaa_data[site].notna()]
    print(f'  {site}: {len(site_data):,}건') 