"""
입고/출고 마스크 생성 과정 검증 테스트
"""

import pandas as pd
import numpy as np
from datetime import datetime

def test_mask_generation():
    """입고/출고 마스크 생성 과정 검증"""
    
    # 테스트 데이터 생성
    test_data = pd.DataFrame({
        'Item_ID': range(1, 11),
        'Pkg': [1, 2, 3, 1, 5, 1, 2, 1, 3, 1],
        'DSV Indoor': [
            '2024-06-15',  # 6월 입고
            '2024-06-20',  # 6월 입고
            '2024-05-10',  # 5월 입고
            '2024-06-01',  # 6월 입고
            '2024-07-05',  # 7월 입고
            '2024-06-30',  # 6월 입고
            '2024-05-25',  # 5월 입고
            '2024-06-10',  # 6월 입고
            '2024-06-25',  # 6월 입고
            '2024-06-05',  # 6월 입고
        ],
        'Out_Date_DSV Indoor': [
            '2024-06-25',  # 6월 출고
            '2024-07-10',  # 7월 출고
            '2024-06-15',  # 6월 출고
            '2024-06-20',  # 6월 출고
            '2024-07-20',  # 7월 출고
            '2024-07-05',  # 7월 출고
            '2024-06-30',  # 6월 출고
            '2024-06-15',  # 6월 출고
            '2024-07-01',  # 7월 출고
            '2024-06-10',  # 6월 출고
        ]
    })
    
    # 날짜 컬럼 변환
    test_data['DSV Indoor'] = pd.to_datetime(test_data['DSV Indoor'])
    test_data['Out_Date_DSV Indoor'] = pd.to_datetime(test_data['Out_Date_DSV Indoor'])
    
    print("=== 테스트 데이터 ===")
    print(test_data[['Item_ID', 'DSV Indoor', 'Out_Date_DSV Indoor', 'Pkg']])
    print()
    
    # 2024-06월 기준 마스크 생성
    month_end = pd.Timestamp('2024-06-30')
    wh = 'DSV Indoor'
    
    print(f"=== 2024-06월 마스크 생성 검증 ===")
    print(f"월말 기준: {month_end}")
    print()
    
    # 1. 입고 마스크 생성
    print("1. 입고 마스크 생성:")
    in_mask = (
        test_data[wh].notna()
        & (pd.to_datetime(test_data[wh], errors="coerce").dt.to_period("M") == month_end.to_period("M"))
    )
    
    print("입고 마스크 조건:")
    print(f"  - 조건1 (notna): {test_data[wh].notna().tolist()}")
    print(f"  - 조건2 (월 비교): {(pd.to_datetime(test_data[wh], errors='coerce').dt.to_period('M') == month_end.to_period('M')).tolist()}")
    print(f"  - 최종 입고 마스크: {in_mask.tolist()}")
    print(f"  - 입고 대상 행: {test_data[in_mask]['Item_ID'].tolist()}")
    print()
    
    # 2. 출고 마스크 생성
    print("2. 출고 마스크 생성:")
    out_col = f"Out_Date_{wh}"
    
    if out_col in test_data.columns:
        out_mask = (
            test_data[out_col].notna()
            & (pd.to_datetime(test_data[out_col], errors="coerce").dt.to_period("M") == month_end.to_period("M"))
        )
    else:
        out_mask = pd.Series([False] * len(test_data), index=test_data.index)
    
    print("출고 마스크 조건:")
    print(f"  - 조건1 (notna): {test_data[out_col].notna().tolist()}")
    print(f"  - 조건2 (월 비교): {(pd.to_datetime(test_data[out_col], errors='coerce').dt.to_period('M') == month_end.to_period('M')).tolist()}")
    print(f"  - 최종 출고 마스크: {out_mask.tolist()}")
    print(f"  - 출고 대상 행: {test_data[out_mask]['Item_ID'].tolist()}")
    print()
    
    # 3. 수량 계산
    print("3. 수량 계산:")
    
    # 입고 수량
    if "Pkg" in test_data.columns:
        in_qty = test_data.loc[in_mask, "Pkg"].fillna(1).sum()
        print(f"  - 입고 수량 (Pkg 합계): {in_qty}")
    else:
        in_qty = in_mask.sum()
        print(f"  - 입고 수량 (레코드 수): {in_qty}")
    
    # 출고 수량
    if "Pkg" in test_data.columns:
        out_qty = test_data.loc[out_mask, "Pkg"].fillna(1).sum()
        print(f"  - 출고 수량 (Pkg 합계): {out_qty}")
    else:
        out_qty = out_mask.sum()
        print(f"  - 출고 수량 (레코드 수): {out_qty}")
    
    print()
    
    # 4. 상세 분석
    print("4. 상세 분석:")
    print("입고 대상 상세:")
    inbound_items = test_data[in_mask]
    for _, row in inbound_items.iterrows():
        print(f"  - Item {row['Item_ID']}: {row[wh].strftime('%Y-%m-%d')} (Pkg: {row['Pkg']})")
    
    print("\n출고 대상 상세:")
    outbound_items = test_data[out_mask]
    for _, row in outbound_items.iterrows():
        print(f"  - Item {row['Item_ID']}: {row[out_col].strftime('%Y-%m-%d')} (Pkg: {row['Pkg']})")
    
    print()
    
    # 5. 수동 검증
    print("5. 수동 검증:")
    
    # 6월 입고 수동 계산
    june_inbound = []
    for idx, row in test_data.iterrows():
        if row[wh].month == 6 and row[wh].year == 2024:
            june_inbound.append(row['Item_ID'])
    
    # 6월 출고 수동 계산
    june_outbound = []
    for idx, row in test_data.iterrows():
        if row[out_col].month == 6 and row[out_col].year == 2024:
            june_outbound.append(row['Item_ID'])
    
    print(f"수동 계산 - 6월 입고: {june_inbound}")
    print(f"수동 계산 - 6월 출고: {june_outbound}")
    print(f"마스크 계산 - 6월 입고: {test_data[in_mask]['Item_ID'].tolist()}")
    print(f"마스크 계산 - 6월 출고: {test_data[out_mask]['Item_ID'].tolist()}")
    
    # 6. 검증 결과
    print("\n6. 검증 결과:")
    print(f"✅ 입고 마스크: {in_mask.sum()}건 (수동 계산: {len(june_inbound)}건)")
    print(f"✅ 출고 마스크: {out_mask.sum()}건 (수동 계산: {len(june_outbound)}건)")
    print(f"✅ 입고 수량: {in_qty}개")
    print(f"✅ 출고 수량: {out_qty}개")
    
    # 정확도 검증
    inbound_accuracy = set(test_data[in_mask]['Item_ID'].tolist()) == set(june_inbound)
    outbound_accuracy = set(test_data[out_mask]['Item_ID'].tolist()) == set(june_outbound)
    
    print(f"\n최종 검증 결과:")
    print(f"  - 입고 마스크 정확도: {inbound_accuracy}")
    print(f"  - 출고 마스크 정확도: {outbound_accuracy}")
    
    if inbound_accuracy and outbound_accuracy:
        print("🎉 모든 마스크 생성이 정확합니다!")
    else:
        print("⚠️ 마스크 생성에 문제가 있습니다.")

if __name__ == "__main__":
    test_mask_generation() 