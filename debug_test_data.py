"""
🔍 테스트 데이터 분석 및 디버깅 스크립트
"""

import pandas as pd
from datetime import datetime


def analyze_test_data():
    """테스트 데이터 분석"""
    # 실제 테스트 데이터 재생성
    test_data = {
        'Transaction_ID': ['T001', 'T002', 'T003', 'T004'],
        'DSV Indoor': [
            datetime(2024, 1, 15),
            datetime(2024, 1, 20),
            pd.NaT,
            datetime(2024, 2, 5)
        ],
        'DSV Outdoor': [
            pd.NaT,
            datetime(2024, 1, 25),
            datetime(2024, 1, 10),
            pd.NaT
        ],
        'MIR': [
            datetime(2024, 1, 20),
            datetime(2024, 2, 1),
            datetime(2024, 1, 15),
            datetime(2024, 2, 10)
        ],
        'SHU': [
            pd.NaT,
            pd.NaT,
            pd.NaT,
            pd.NaT
        ]
    }
    df = pd.DataFrame(test_data)
    
    print("📊 테스트 데이터 분석")
    print("=" * 50)
    print(df)
    print("\n")
    
    # DSV Indoor 방문 케이스 분석
    print("🏢 DSV Indoor 방문 케이스 분석")
    print("=" * 50)
    dsv_indoor_visited = df[df['DSV Indoor'].notna()].copy()
    
    for idx, row in dsv_indoor_visited.iterrows():
        print(f"Transaction: {row['Transaction_ID']}")
        print(f"DSV Indoor 도착: {row['DSV Indoor']}")
        print(f"DSV Outdoor: {row['DSV Outdoor']}")
        print(f"MIR: {row['MIR']}")
        print(f"SHU: {row['SHU']}")
        
        # 다음 단계 이동 날짜 찾기
        warehouse_date = row['DSV Indoor']
        next_dates = []
        
        # 다른 창고로 이동
        if pd.notna(row['DSV Outdoor']) and row['DSV Outdoor'] > warehouse_date:
            next_dates.append(('DSV Outdoor', row['DSV Outdoor']))
        
        # 현장으로 이동
        if pd.notna(row['MIR']) and row['MIR'] > warehouse_date:
            next_dates.append(('MIR', row['MIR']))
        if pd.notna(row['SHU']) and row['SHU'] > warehouse_date:
            next_dates.append(('SHU', row['SHU']))
        
        print(f"다음 단계 이동: {next_dates}")
        
        if next_dates:
            earliest = min(next_dates, key=lambda x: x[1])
            print(f"가장 빠른 다음 단계: {earliest[0]} ({earliest[1]})")
            print(f"출고 월: {earliest[1].to_period('M')}")
        else:
            print("다음 단계 이동 없음")
            
        print("-" * 30)
    
    # 월별 출고 분석
    print("\n📅 월별 출고 분석")
    print("=" * 50)
    
    periods = [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-02-01')]
    
    for period in periods:
        print(f"\n{period.strftime('%Y-%m')}월 DSV Indoor 출고 분석:")
        outbound_count = 0
        
        for idx, row in dsv_indoor_visited.iterrows():
            warehouse_date = row['DSV Indoor']
            next_dates = []
            
            # 다른 창고로 이동
            if pd.notna(row['DSV Outdoor']) and row['DSV Outdoor'] > warehouse_date:
                next_dates.append(row['DSV Outdoor'])
            
            # 현장으로 이동
            if pd.notna(row['MIR']) and row['MIR'] > warehouse_date:
                next_dates.append(row['MIR'])
            if pd.notna(row['SHU']) and row['SHU'] > warehouse_date:
                next_dates.append(row['SHU'])
            
            if next_dates:
                earliest_next_date = min(next_dates)
                if earliest_next_date.to_period('M') == period.to_period('M'):
                    outbound_count += 1
                    print(f"  {row['Transaction_ID']}: {warehouse_date} → {earliest_next_date} (출고)")
                else:
                    print(f"  {row['Transaction_ID']}: {warehouse_date} → {earliest_next_date} (다른 월)")
            else:
                print(f"  {row['Transaction_ID']}: {warehouse_date} → 이동 없음")
        
        print(f"총 출고 건수: {outbound_count}")


if __name__ == "__main__":
    analyze_test_data() 