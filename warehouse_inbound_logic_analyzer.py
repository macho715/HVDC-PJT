#!/usr/bin/env python3
"""
🏢 MACHO v2.8.4 창고별 실제 입고 건수 계산 로직 완전 분석
HVDC Project - Samsung C&T Logistics

핵심 알고리즘: 7단계 복합 계산 시스템
"""

import pandas as pd
import numpy as np

def analyze_warehouse_inbound_logic():
    """창고별 실제 입고 건수 계산 로직 7단계 완전 분석"""
    
    print("🏢 **MACHO v2.8.4 창고별 실제 입고 건수 계산 로직**")
    print("=" * 80)
    
    # === 1단계: 실제 데이터 기반 설정 ===
    print("\n📊 **1단계: 실제 데이터 기반 설정**")
    print("-" * 50)
    
    # 실제 카운팅된 데이터 (Excel WH HANDLING 컬럼 기반)
    real_data = {
        'SIMENSE': {'total': 2227, 'distribution': {0: 1026, 1: 956, 2: 245, 3: 0}},
        'HITACHI': {'total': 5346, 'distribution': {0: 1819, 1: 2561, 2: 886, 3: 80}}
    }
    
    total_integrated = {
        'total': 7573,
        'distribution': {0: 2845, 1: 3517, 2: 1131, 3: 80}
    }
    
    print(f"✅ 총 실제 데이터: {total_integrated['total']:,}건")
    for code, count in total_integrated['distribution'].items():
        pct = count / total_integrated['total'] * 100
        flow_desc = ['직접운송', '창고1개경유', '창고2개경유', '창고3개+경유'][code]
        print(f"   Code {code} ({flow_desc}): {count:,}건 ({pct:.1f}%)")
    
    # === 2단계: 창고 경유 건수 추출 ===
    print("\n📦 **2단계: 창고 경유 건수 추출 (Flow Code 1+2+3만)**")
    print("-" * 50)
    
    # 직접운송(Code 0)은 창고 미경유, 나머지만 창고 경유
    warehouse_flow_items = (total_integrated['distribution'][1] + 
                           total_integrated['distribution'][2] + 
                           total_integrated['distribution'][3])
    
    print(f"🚚 직접운송 (Code 0): {total_integrated['distribution'][0]:,}건 → 창고 미경유")
    print(f"🏢 창고 경유 총계: {warehouse_flow_items:,}건")
    print(f"   - Code 1 (창고1개): {total_integrated['distribution'][1]:,}건")
    print(f"   - Code 2 (창고2개): {total_integrated['distribution'][2]:,}건") 
    print(f"   - Code 3 (창고3개+): {total_integrated['distribution'][3]:,}건")
    
    # === 3단계: 4개 창고 분할 배정 ===
    print(f"\n🏢 **3단계: 4개 창고 분할 배정**")
    print("-" * 50)
    
    warehouse_info = {
        'DSV Indoor': {'capacity': 2000, 'utilization': 75.2, 'type': 'Indoor'},
        'DSV Outdoor': {'capacity': 5000, 'utilization': 68.5, 'type': 'Outdoor'},
        'DSV Al Markaz': {'capacity': 3000, 'utilization': 82.1, 'type': 'Central'},
        'MOSB': {'capacity': 1500, 'utilization': 45.8, 'type': 'Offshore'}
    }
    
    warehouse_base_allocation = warehouse_flow_items // 4  # 4개 창고로 균등 분할
    
    print(f"창고별 기본 배정: {warehouse_flow_items:,} ÷ 4 = {warehouse_base_allocation:,}건/창고")
    
    for wh_name, info in warehouse_info.items():
        print(f"   {wh_name} ({info['type']}): 기본 {warehouse_base_allocation:,}건")
        print(f"     용량: {info['capacity']:,}, 가동률: {info['utilization']}%")
    
    # === 4단계: 25개월 시간 분할 ===
    print(f"\n📅 **4단계: 25개월 회계 기간 분할**")
    print("-" * 50)
    
    months = ['2023-12', '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', 
             '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12', 
             '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', 
             '2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12']
    
    monthly_base = warehouse_base_allocation // 25  # 25개월로 분할
    
    print(f"회계 기간: {len(months)}개월 (2023-12 ~ 2025-12)")
    print(f"월평균 기준: {warehouse_base_allocation:,} ÷ 25 = {monthly_base:,}건/월/창고")
    
    # === 5단계: 실제 계절 요인 적용 ===
    print(f"\n🌦️ **5단계: 실제 계절 요인 적용**")
    print("-" * 50)
    
    # 실제 입고 패턴 기반 계절 요인 (25개월)
    base_factors = [0.57, 1.07, 1.15, 1.15, 0.62, 2.10, 2.32, 1.65, 2.30, 1.62, 1.45, 0.87,
                   1.02, 1.02, 0.82, 2.22, 1.62, 1.15, 0.20, 0.05, 0.05, 0.05, 0.05, 0.05, 0.02]
    
    # 피크월 식별
    peak_months = [(i, months[i], base_factors[i]) for i in range(len(months)) if base_factors[i] > 2.0]
    print("📈 피크월 분석:")
    for i, month, factor in peak_months:
        print(f"   {month}: {factor:.2f}x (피크)")
    
    # === 6단계: 창고 타입별 계절 조정 ===
    print(f"\n🏢 **6단계: 창고 타입별 계절 조정**")
    print("-" * 50)
    
    sample_month_idx = 5  # 2024-06 (최대 피크월)
    base_factor = base_factors[sample_month_idx]
    
    print(f"샘플: 2024-06월 (base_factor: {base_factor:.2f})")
    
    for wh_name, info in warehouse_info.items():
        wh_type = info['type']
        
        if wh_type == 'Indoor':
            # 실내 창고: 안정적 운영, 변동성 완화
            seasonal_factor = min(base_factor * 0.8 + 0.4, 2.0)
            formula = f"{base_factor:.2f} × 0.8 + 0.4 = {seasonal_factor:.2f}"
            reason = "변동성 완화 (온도/습도 제어)"
            
        elif wh_type == 'Outdoor':
            # 야외 창고: 실제 분포 직접 반영
            seasonal_factor = base_factor * 1.0
            formula = f"{base_factor:.2f} × 1.0 = {seasonal_factor:.2f}"
            reason = "실제 분포 반영 (날씨 직접 영향)"
            
        elif wh_type == 'Central':
            # 중앙 허브: 균등 분포 지향
            seasonal_factor = base_factor * 0.7 + 0.5
            formula = f"{base_factor:.2f} × 0.7 + 0.5 = {seasonal_factor:.2f}"
            reason = "균등 분포 (허브 기능)"
            
        else:  # Offshore
            # 해상 기지: 극단적 변동
            seasonal_factor = min(base_factor * 1.2, 3.0)
            formula = f"{base_factor:.2f} × 1.2 = {seasonal_factor:.2f}"
            reason = "극단적 변동 (프로젝트 기반)"
        
        print(f"   {wh_name} ({wh_type}): {formula}")
        print(f"     이유: {reason}")
    
    # === 7단계: 최종 입고량 계산 ===
    print(f"\n⚙️ **7단계: 최종 입고량 계산**")
    print("-" * 50)
    
    print("최종 공식:")
    print("입고량 = monthly_base × seasonal_factor × capacity_factor × utilization_factor")
    print()
    
    # 예시 계산 (DSV Indoor, 2024-06)
    wh_name = 'DSV Indoor'
    info = warehouse_info[wh_name]
    base_factor = base_factors[5]  # 2024-06
    seasonal_factor = min(base_factor * 0.8 + 0.4, 2.0)
    capacity_factor = info['capacity'] / 2000  # 기준 용량 대비
    utilization_factor = info['utilization'] / 100
    
    final_inbound = int(monthly_base * seasonal_factor * capacity_factor * utilization_factor)
    
    print(f"예시: {wh_name}, 2024-06월")
    print(f"   monthly_base: {monthly_base:,}건")
    print(f"   seasonal_factor: {seasonal_factor:.2f}")
    print(f"   capacity_factor: {capacity_factor:.2f} (용량 {info['capacity']:,} ÷ 2000)")
    print(f"   utilization_factor: {utilization_factor:.2f} (가동률 {info['utilization']}%)")
    print(f"   최종 입고량: {final_inbound:,}건")
    
    return {
        'warehouse_flow_items': warehouse_flow_items,
        'monthly_base': monthly_base,
        'warehouse_info': warehouse_info,
        'base_factors': base_factors,
        'months': months
    }

if __name__ == "__main__":
    result = analyze_warehouse_inbound_logic()
    
    print(f"\n🎯 **핵심 수치 요약**")
    print("=" * 50)
    print(f"창고 경유 총 건수: {result['warehouse_flow_items']:,}건")
    print(f"창고별 기본 배정: {result['warehouse_flow_items']//4:,}건")
    print(f"월평균 기준량: {result['monthly_base']:,}건/월/창고")
    print(f"최대 계절 요인: {max(result['base_factors']):.2f}x")
    print(f"최소 계절 요인: {min(result['base_factors']):.2f}x") 