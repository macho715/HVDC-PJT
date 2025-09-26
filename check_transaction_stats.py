import pandas as pd

# 트랜잭션 테이블 로드
df = pd.read_excel('flowcode_transaction_table.xlsx')

print("📊 MACHO Flow Code 검증 Rev - 트랜잭션 테이블 통계")
print("=" * 60)
print(f"총 행수: {len(df):,}")
print(f"총 컬럼수: {len(df.columns)}")

print("\n📋 벤더별 분포:")
print(df['Vendor'].value_counts())

print("\n🔄 Flow Code 분포:")
print(df['Flow_Code'].value_counts().sort_index())

print("\n📅 날짜 범위:")
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
print(f"시작일: {df['Date'].min()}")
print(f"종료일: {df['Date'].max()}")

print("\n🏢 Location 분포 (상위 10개):")
print(df['Location'].value_counts().head(10))

print("\n📦 Pkg 수량 통계:")
print(f"총 Pkg 수량: {df['Pkg'].sum():,}")
print(f"평균 Pkg: {df['Pkg'].mean():.2f}")
print(f"최대 Pkg: {df['Pkg'].max()}")
print(f"최소 Pkg: {df['Pkg'].min()}")

print("\n🔍 MOSB 여부:")
mosb_count = df['MOSB'].notna().sum()
print(f"MOSB 데이터 있음: {mosb_count}건")
print(f"MOSB 데이터 없음: {len(df) - mosb_count}건")

print("\n📊 Vendor별 Flow Code 분포:")
pivot = pd.crosstab(df['Vendor'], df['Flow_Code'], margins=True)
print(pivot) 