#!/usr/bin/env python3
"""
창고별 월별 입고재고 로직 상세 분석
MACHO v2.8.4 - Step-by-step analysis
"""

import pandas as pd
import numpy as np

def analyze_warehouse_monthly_logic():
    """창고별 월별 입고재고 로직 단계별 분석"""
    
    print("🏢 **창고별 월별 입고재고 로직 상세 분석**")
    print("=" * 60)
    
    # 1단계: 기본 설정
    print("\n📊 **1단계: 기본 설정**")
    print("-" * 40)
    
    warehouse_info = {
        'DSV Indoor': {'capacity': 2000, 'utilization': 75.2, 'type': 'Indoor'},
        'DSV Outdoor': {'capacity': 5000, 'utilization': 68.5, 'type': 'Outdoor'},
        'DSV Al Markaz': {'capacity': 3000, 'utilization': 82.1, 'type': 'Central'},
        'MOSB': {'capacity': 1500, 'utilization': 45.8, 'type': 'Offshore'}
    }
    
    for name, info in warehouse_info.items():
        print(f"   {name} ({info['type']}): 용량 {info['capacity']:,}, 가동률 {info['utilization']}%")
    
    # 2단계: Flow Code 기반 창고 경유 건수
    print("\n📦 **2단계: Flow Code 기반 창고 경유 건수**")
    print("-" * 40)
    
    total_integrated = {'distribution': {0: 2845, 1: 3517, 2: 1131, 3: 80}}
    warehouse_flow_items = (total_integrated['distribution'][1] + 
                           total_integrated['distribution'][2] + 
                           total_integrated['distribution'][3]) / 4
    
    print(f"   Code 1 (창고1개경유): {total_integrated['distribution'][1]:,}건")
    print(f"   Code 2 (창고2개경유): {total_integrated['distribution'][2]:,}건")
    print(f"   Code 3 (창고3개+경유): {total_integrated['distribution'][3]:,}건")
    print(f"   창고 경유 총합: {3517+1131+80:,}건")
    print(f"   창고별 배정 (÷4): {warehouse_flow_items:,.0f}건")
    print(f"   월평균 기준 (÷25): {warehouse_flow_items/25:,.0f}건")
    
    # 3단계: 실제 계절 요인 (25개월)
    print("\n📅 **3단계: 실제 계절 요인 (25개월)**")
    print("-" * 40)
    
    months = ['2023-12', '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', 
              '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12', 
              '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', 
              '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12']
    
    base_factors = [0.57, 1.07, 1.15, 1.15, 0.62, 2.10, 2.32, 1.65, 2.30, 1.62, 1.45, 0.87,
                   1.02, 1.02, 0.82, 2.22, 1.62, 1.15, 0.20, 0.05, 0.05, 0.05, 0.05, 0.05, 0.02]
    
    peak_months = []
    for i, (month, factor) in enumerate(zip(months, base_factors)):
        if factor > 2.0:
            peak_months.append((month, factor))
    
    print("   실제 입고 패턴 피크월:")
    for month, factor in peak_months:
        print(f"   {month}: {factor:.2f}")
    
    print(f"   평균 계절 요인: {np.mean(base_factors):.2f}")
    print(f"   최대 계절 요인: {max(base_factors):.2f} ({months[base_factors.index(max(base_factors))]})")
    print(f"   최소 계절 요인: {min(base_factors):.2f} ({months[base_factors.index(min(base_factors))]})")
    
    # 4단계: 창고 타입별 계절 요인 조정
    print("\n🏭 **4단계: 창고 타입별 계절 요인 조정**")
    print("-" * 40)
    
    sample_month_idx = 6  # 2024-06 (피크월)
    sample_factor = base_factors[sample_month_idx]
    
    adjustments = {
        'Indoor': min(sample_factor * 0.8 + 0.4, 2.0),
        'Outdoor': sample_factor,
        'Central': sample_factor * 0.7 + 0.5,
        'Offshore': min(sample_factor * 1.2, 3.0)
    }
    
    print(f"   기준월 ({months[sample_month_idx]}) 계절요인: {sample_factor:.2f}")
    for wh_type, adjusted in adjustments.items():
        print(f"   {wh_type:8}: {adjusted:.2f} (조정률: {adjusted/sample_factor:.1%})")
    
    # 5단계: 샘플 계산 (DSV Indoor, 2024-06)
    print("\n⚙️ **5단계: 샘플 계산 (DSV Indoor, 2024-06)**")
    print("-" * 40)
    
    wh_name = 'DSV Indoor'
    wh_info = warehouse_info[wh_name]
    monthly_base = warehouse_flow_items / 25
    seasonal_factor = adjustments['Indoor']
    monthly_adjusted = monthly_base * seasonal_factor
    
    capacity_factor = wh_info['capacity'] / 2000  # 기준 용량 대비
    utilization_factor = wh_info['utilization'] / 100
    
    in_qty = int(monthly_adjusted * capacity_factor * utilization_factor)
    
    print(f"   월평균 기준량: {monthly_base:.0f}건")
    print(f"   계절 조정: {monthly_base:.0f} × {seasonal_factor:.2f} = {monthly_adjusted:.0f}건")
    print(f"   용량 계수: {capacity_factor:.1f} (용량 {wh_info['capacity']:,} ÷ 2000)")
    print(f"   가동률 계수: {utilization_factor:.3f} ({wh_info['utilization']}%)")
    print(f"   최종 입고량: {in_qty:,}건")
    
    # 6단계: 재고 회전율 적용
    print("\n🔄 **6단계: 재고 회전율 적용 (DSV Indoor)**")
    print("-" * 40)
    
    stock_ratio = 0.20  # Indoor: 높은 재고율 (보관 중심)
    out_ratio = 0.75    # Indoor: 안정적인 출고
    
    out_qty = int(in_qty * out_ratio)
    stock_qty = int(in_qty * stock_ratio)
    net_change = in_qty - out_qty
    
    print(f"   재고 보관율: {stock_ratio:.1%} (보관 중심)")
    print(f"   출고 비율: {out_ratio:.1%} (안정적 출고)")
    print(f"   입고량: {in_qty:,}건")
    print(f"   출고량: {out_qty:,}건 ({in_qty} × {out_ratio:.1%})")
    print(f"   재고량: {stock_qty:,}건 ({in_qty} × {stock_ratio:.1%})")
    print(f"   순증감: {net_change:+,}건")
    
    # 7단계: 효율성 점수 계산
    print("\n📈 **7단계: 효율성 점수 계산**")
    print("-" * 40)
    
    efficiency_score = round(
        (out_ratio * 40) +              # 출고율 40%
        ((1 - stock_ratio) * 30) +      # 재고 회전율 30%
        (utilization_factor * 30), 1    # 가동률 30%
    )
    
    print(f"   출고율 기여: {out_ratio:.1%} × 40% = {out_ratio * 40:.1f}점")
    print(f"   회전율 기여: {(1-stock_ratio):.1%} × 30% = {(1-stock_ratio) * 30:.1f}점")
    print(f"   가동률 기여: {utilization_factor:.1%} × 30% = {utilization_factor * 30:.1f}점")
    print(f"   총 효율성 점수: {efficiency_score:.1f}점")
    
    # 최종 결과 구조
    print("\n📊 **최종 결과 구조**")
    print("-" * 40)
    print("   Excel 출력 컬럼 (17개):")
    columns = ['warehouse', 'type', 'location', 'month', 'capacity', 'base_utilization',
               'in_qty', 'out_qty', 'stock_qty', 'net_change', 'stock_ratio', 
               'turnover_ratio', 'efficiency_score', 'seasonal_factor', 'capacity_utilization']
    
    for i, col in enumerate(columns, 1):
        print(f"   {i:2d}. {col}")
    
    print(f"\n   총 데이터 행수: {len(warehouse_info)} 창고 × {len(months)} 개월 = {len(warehouse_info) * len(months):,}행")

if __name__ == "__main__":
    analyze_warehouse_monthly_logic() 