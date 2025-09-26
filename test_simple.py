import pandas as pd

print("🚀 테스트 시작!")

# 기존 파일 불러오기
trx_df = pd.read_excel('output/정규화_트랜잭션테이블_상세.xlsx')
print(f"파일 로드 완료: {len(trx_df)}행")

# 1. Case_ID, Location별 누적재고 계산
last_stock = trx_df.groupby(['Case_ID', 'Location'])['누적재고'].last().reset_index()
print(f"Case_ID+Location 총 그룹: {len(last_stock)}")
print(f"잔여재고>0인 케이스: {len(last_stock[last_stock['누적재고'] > 0])}")

# 2. 잔여재고>0인 경우 OUT 이벤트 자동 생성
auto_out_rows = []
for _, row in last_stock.iterrows():
    if row['누적재고'] > 0:
        out_row = {
            'Case_ID': row['Case_ID'],
            'Date': pd.Timestamp.now(),
            'Location': row['Location'],
            'Event': 'AUTO_OUT',
            'Pkg': -row['누적재고'],
            'SQM': None,
            'Stackable': None,
            'Flow_Code': None,
            'Vendor': None,
            '누적재고': 0
        }
        auto_out_rows.append(out_row)

print(f"생성된 AUTO_OUT 행수: {len(auto_out_rows)}")

# 3. OUT 이벤트를 기존 df에 추가
if auto_out_rows:
    trx_df = pd.concat([trx_df, pd.DataFrame(auto_out_rows)], ignore_index=True)

print(f"AUTO_OUT 추가 후 전체 합계(Pkg): {trx_df['Pkg'].sum()}")
print("AUTO_OUT 추가 후 이벤트 분포:")
print(trx_df['Event'].value_counts())

print("🔥 테스트 완료!") 