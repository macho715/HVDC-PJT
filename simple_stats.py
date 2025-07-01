import pandas as pd

try:
    df = pd.read_excel('flowcode_transaction_table.xlsx')
    print(f"행수: {len(df)}")
    print("컬럼:", list(df.columns))
    print("HITACHI:", len(df[df['Vendor']=='HITACHI']))
    print("SIMENSE:", len(df[df['Vendor']=='SIMENSE']))
    print("첫 5행:")
    print(df.head())
except Exception as e:
    print(f"오류: {e}") 