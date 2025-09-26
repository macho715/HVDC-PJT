#!/usr/bin/env python3
"""
현재 데이터의 Status_Location 분포 상세 분석
- Pre Arrival 정확한 개수 확인 (대소문자 구분 없음)
- NaN 값 확인
- 현장별/창고별 분포 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_status_location_distribution():
    """Status_Location 분포 상세 분석"""
    print("📊 Status_Location 분포 상세 분석 시작...")
    print("=" * 80)
    
    # 데이터 로딩
    data_paths = [
        "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
    ]
    
    dfs = []
    for path in data_paths:
        if os.path.exists(path):
            df = pd.read_excel(path)
            fname = os.path.basename(path)
            print(f"✅ 로드 완료: {fname}, {len(df)}건")
            dfs.append(df)
    
    if not dfs:
        print("❌ 데이터 파일을 찾을 수 없습니다.")
        return
    
    # 데이터 병합
    df = pd.concat(dfs, ignore_index=True)
    print(f"\n📊 총 데이터: {len(df)}건")
    
    # Status_Location 컬럼 확인
    if 'Status_Location' not in df.columns:
        print("❌ Status_Location 컬럼이 없습니다.")
        print("📋 사용 가능한 컬럼:")
        for col in df.columns:
            print(f"   - {col}")
        return
    
    print(f"\n🔍 Status_Location 분석:")
    print("=" * 60)
    
    # 1. 전체 분포
    status_counts = df['Status_Location'].value_counts()
    print(f"📈 Status_Location 분포 (총 {len(df)}건):")
    for status, count in status_counts.head(15).items():
        percentage = (count / len(df)) * 100
        print(f"   {status:<25} {count:>6}건 ({percentage:>5.1f}%)")
    
    # 2. Pre Arrival 정확한 확인 (대소문자 구분 없음)
    print(f"\n🔍 Pre Arrival 상세 분석:")
    pre_arrival_mask = df['Status_Location'].str.contains('pre arrival', case=False, na=False)
    pre_arrival_count = pre_arrival_mask.sum()
    pre_arrival_exact = df[df['Status_Location'].str.lower() == 'pre arrival']['Status_Location'].value_counts()
    
    print(f"   - Pre Arrival (대소문자 무관): {pre_arrival_count}건")
    if len(pre_arrival_exact) > 0:
        print(f"   - 정확한 표기:")
        for exact_text, count in pre_arrival_exact.items():
            print(f"     '{exact_text}': {count}건")
    
    # 3. NaN 값 확인
    nan_count = df['Status_Location'].isna().sum()
    print(f"\n🔍 빈 값(NaN) 분석:")
    print(f"   - NaN 개수: {nan_count}건")
    
    # 4. 현장별 분류
    site_locations = ['AGI', 'DAS', 'MIR', 'SHU']
    site_counts = {}
    total_site_count = 0
    
    print(f"\n🏗️ 현장별 분포:")
    for site in site_locations:
        site_mask = df['Status_Location'].str.contains(site, case=False, na=False)
        site_count = site_mask.sum()
        site_counts[site] = site_count
        total_site_count += site_count
        percentage = (site_count / len(df)) * 100
        print(f"   - {site}: {site_count}건 ({percentage:.1f}%)")
    
    print(f"   🎯 현장 총합: {total_site_count}건")
    
    # 5. 창고별 분류
    warehouse_keywords = ['DSV', 'Indoor', 'Outdoor', 'Al Markaz', 'AAA Storage', 'HALUER', 'DHL', 'MOSB']
    warehouse_counts = {}
    total_warehouse_count = 0
    
    print(f"\n🏭 창고별 분포:")
    for keyword in warehouse_keywords:
        warehouse_mask = df['Status_Location'].str.contains(keyword, case=False, na=False)
        warehouse_count = warehouse_mask.sum()
        if warehouse_count > 0:
            warehouse_counts[keyword] = warehouse_count
            total_warehouse_count += warehouse_count
            percentage = (warehouse_count / len(df)) * 100
            print(f"   - {keyword} 포함: {warehouse_count}건 ({percentage:.1f}%)")
    
    print(f"   🎯 창고 관련 총합: {total_warehouse_count}건")
    
    # 6. 기타 분류
    other_count = len(df) - pre_arrival_count - nan_count - total_site_count - total_warehouse_count
    print(f"\n📦 기타/중복 제외: {other_count}건")
    
    # 7. 요약
    print(f"\n📋 Status_Location 요약:")
    print("=" * 50)
    print(f"   Pre Arrival: {pre_arrival_count}건")
    print(f"   NaN (빈 값): {nan_count}건")
    print(f"   현장 관련: {total_site_count}건")
    print(f"   창고 관련: {total_warehouse_count}건")
    print(f"   기타: {other_count}건")
    print(f"   ─────────────────────")
    print(f"   총계: {len(df)}건")
    
    # 8. Flow Code 0 후보 계산
    flow_code_0_candidates = pre_arrival_count + nan_count
    print(f"\n🎯 Flow Code 0 후보: {flow_code_0_candidates}건 (Pre Arrival + NaN)")
    
    return {
        'total_records': len(df),
        'pre_arrival_count': pre_arrival_count,
        'nan_count': nan_count,
        'site_counts': site_counts,
        'warehouse_counts': warehouse_counts,
        'flow_code_0_candidates': flow_code_0_candidates
    }

def main():
    """메인 실행 함수"""
    print("🔍 HVDC 프로젝트 Status_Location 분포 분석")
    print("📅", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    result = analyze_status_location_distribution()
    
    if result:
        print(f"\n✅ 분석 완료!")
        print(f"📊 주요 발견사항:")
        print(f"   - Pre Arrival: {result['pre_arrival_count']}건")
        print(f"   - Flow Code 0 후보: {result['flow_code_0_candidates']}건")
        
        # 사용자 언급 수치와 비교
        expected_pre_arrival = 486
        expected_sites = 4496
        
        print(f"\n🔍 예상 수치와 비교:")
        print(f"   - Pre Arrival 예상: {expected_pre_arrival}건 vs 실제: {result['pre_arrival_count']}건")
        print(f"   - 현장 예상: {expected_sites}건 vs 실제: {sum(result['site_counts'].values())}건")
        
        if result['pre_arrival_count'] != expected_pre_arrival:
            print(f"   ⚠️ Pre Arrival 수치 차이 발견!")
        
        if sum(result['site_counts'].values()) != expected_sites:
            print(f"   ⚠️ 현장 수치 차이 발견!")

if __name__ == "__main__":
    main() 