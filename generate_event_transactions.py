import pandas as pd
from datetime import datetime

print("🚀 MACHO-GPT v3.4-mini 가이드 무조건 준수 실행 시작!")
print("💡 입고 요약(SUMMARY) → 트랜잭션 → 잔여재고 자동 OUT 보정 파이프라인")

### 1. [입고 요약(SUMMARY) 데이터 → 트랜잭션(IN) 변환]

summary_df = pd.read_excel('data/flowcode_transaction_table.xlsx')
summary_df = summary_df.rename(columns={'Status_Location': 'Location', '합계: Pkg':'Pkg'})

trx_in = summary_df[['Location', 'Pkg']].copy()
trx_in['Event'] = 'IN'
trx_in['Date'] = datetime.now().strftime('%Y-%m-%d')
trx_in['Case_ID'] = trx_in['Location'] + '_IN'

print(f"✅ 입고 트랜잭션 생성 완료: {len(trx_in)}건")

trx_full = trx_in.copy()

### 2. [누적재고(잔여) 자동 OUT 이벤트 생성 파트]

trx_full['누적재고'] = trx_full.groupby(['Location'])['Pkg'].cumsum()
last_stock = trx_full.groupby(['Location'])['누적재고'].last().reset_index()

print(f"🔍 Location별 잔여재고 분석:")
print(f"   - 총 Location 수: {len(last_stock)}")
print(f"   - 잔여재고>0인 Location: {len(last_stock[last_stock['누적재고'] > 0])}")

auto_out_rows = []
for _, row in last_stock.iterrows():
    if row['누적재고'] > 0:
        auto_out_rows.append({
            'Location': row['Location'],
            'Pkg': -row['누적재고'],
            'Event': 'AUTO_OUT',
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Case_ID': row['Location'] + '_AUTO_OUT',
            '누적재고': 0
        })

print(f"🔧 AUTO_OUT 이벤트 생성: {len(auto_out_rows)}건")

if auto_out_rows:
    trx_full = pd.concat([trx_full, pd.DataFrame(auto_out_rows)], ignore_index=True)

trx_full = trx_full.sort_values(['Location', 'Date', 'Event'])

### 3. [결과 저장 및 요약]
trx_full.to_excel('output/최종_트랜잭션테이블_자동OUT포함.xlsx', index=False)
print('📊 잔여재고 자동 OUT 보정 후 전체합계(Pkg):', trx_full['Pkg'].sum())
print(f"📋 최종 이벤트 분포:")
print(trx_full['Event'].value_counts())

print("✅ 가이드 완전 준수 파이프라인 실행 완료!") 