import pandas as pd

# 기존 파일 불러오기
trx_df = pd.read_excel('output/정규화_트랜잭션테이블_상세.xlsx')

print("🔍 디버깅: AUTO_OUT 이벤트 생성")
print(f"원본 데이터 행수: {len(trx_df)}")
print(f"원본 이벤트 분포:\n{trx_df['Event'].value_counts()}")

# ===============================
# 가이드 코드 정확히 실행
# ===============================

# 1. Case_ID, Location별 누적재고 계산
last_stock = trx_df.groupby(['Case_ID', 'Location'])['누적재고'].last().reset_index()
print(f"\n1. Case_ID, Location별 최종 누적재고:")
print(f"   - 총 케이스 수: {len(last_stock)}")
print(f"   - 잔여재고>0인 케이스: {len(last_stock[last_stock['누적재고'] > 0])}")
print(f"   - 잔여재고=0인 케이스: {len(last_stock[last_stock['누적재고'] == 0])}")

# 2. 잔여재고>0인 경우 OUT 이벤트 자동 생성
auto_out_rows = []
for _, row in last_stock.iterrows():
    if row['누적재고'] > 0:
        # OUT Row 생성
        out_row = {
            'Case_ID': row['Case_ID'],
            'Date': pd.Timestamp.now(),       # 오늘 날짜로 기록 (또는 마지막 이동일자)
            'Location': row['Location'],
            'Event': 'AUTO_OUT',
            'Pkg': -row['누적재고'],
            'SQM': None,                      # 부가정보는 필요한 경우만
            'Stackable': None,
            'Flow_Code': None,
            'Vendor': None,
            '누적재고': 0
        }
        auto_out_rows.append(out_row)

print(f"\n2. AUTO_OUT 이벤트 생성:")
print(f"   - 생성된 AUTO_OUT 행수: {len(auto_out_rows)}")

if auto_out_rows:
    print("   - 생성된 AUTO_OUT 샘플 (상위 3개):")
    for i, row in enumerate(auto_out_rows[:3]):
        print(f"     [{i+1}] {row['Case_ID']} | {row['Location']} | Pkg: {row['Pkg']} | 누적재고: {row['누적재고']}")

# 3. OUT 이벤트를 기존 df에 추가
if auto_out_rows:
    trx_df = pd.concat([trx_df, pd.DataFrame(auto_out_rows)], ignore_index=True)

# 4. 검증: 전체 Pkg 합계
print(f"\n3. AUTO_OUT 추가 전후 비교:")
print(f"   - AUTO_OUT 추가 후 전체 합계(Pkg): {trx_df['Pkg'].sum()}")
print(f"   - AUTO_OUT 추가 후 이벤트 분포:")
print(trx_df['Event'].value_counts())

print(f"\n4. 최종 결과:")
print(f"   - 총 행수: {len(trx_df)}")
print(f"   - AUTO_OUT 이벤트 수: {len(trx_df[trx_df['Event'] == 'AUTO_OUT'])}") 