import pandas as pd
from datetime import datetime

### 1. [입고 요약(SUMMARY) 데이터 → 트랜잭션(IN) 변환]

# 예시: summary_df = pd.read_excel('SUMMARY.xlsx')
summary_df = pd.read_excel('data/flowcode_transaction_table.xlsx')  # 파일명/시트명 맞게 수정

# 필드명 통일: 'Status_Location' → 'Location', 'Pkg' 등
summary_df = summary_df.rename(columns={'Status_Location': 'Location', '합계: Pkg':'Pkg'})

# IN 트랜잭션 이벤트 생성 (입고만 있는 경우)
trx_in = summary_df[['Location', 'Pkg']].copy()
trx_in['Event'] = 'IN'
trx_in['Date'] = datetime.now().strftime('%Y-%m-%d')   # 입고일자 일괄 적용(수정 가능)
trx_in['Case_ID'] = trx_in['Location'] + '_IN'         # 케이스ID 생성(임시)

### (선택) 출고/이동/반품 등 추가 이벤트 직접 입력(아래 예시 참고)
# 예시: OUT, MOVE_IN, MOVE_OUT, RETURN 등 이벤트 행 추가/병합

# df_out = pd.DataFrame({
#     'Location': [...],
#     'Pkg': [-수량],      # 출고는 반드시 음수
#     'Event': 'OUT',
#     'Date': ...,
#     'Case_ID': ...
# })

# trx_full = pd.concat([trx_in, df_out, ...], ignore_index=True)

trx_full = trx_in.copy()   # 추가 이벤트가 없으면 입고만 반영

### 2. [누적재고(잔여) 자동 OUT 이벤트 생성 파트]

# Case_ID+Location별 누적재고 계산
trx_full['누적재고'] = trx_full.groupby(['Location'])['Pkg'].cumsum()

# 마지막 잔여재고 추출
last_stock = trx_full.groupby(['Location'])['누적재고'].last().reset_index()

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

# 자동 OUT Row 추가
if auto_out_rows:
    trx_full = pd.concat([trx_full, pd.DataFrame(auto_out_rows)], ignore_index=True)

# (필요 시) Case_ID/누적재고 재계산/정렬
trx_full = trx_full.sort_values(['Location', 'Date', 'Event'])

### 3. [결과 저장 및 요약]
trx_full.to_excel('output/최종_트랜잭션테이블_자동OUT포함.xlsx', index=False)
print('잔여재고 자동 OUT 보정 후 전체합계(Pkg):', trx_full['Pkg'].sum())

### 4. [실무형 피벗테이블 검증/보고]
# location_event = pd.pivot_table(trx_full, index='Location', columns='Event', values='Pkg', aggfunc='sum', fill_value=0)
# location_event['잔여재고'] = location_event.sum(axis=1)
# print(location_event) 