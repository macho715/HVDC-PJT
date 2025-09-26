#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DHL warehouse 관련 컬럼 확인 스크립트
원본 raw data 전체 컬럼 분석
"""

import pandas as pd

def check_dhl_warehouse_columns():
    """DHL warehouse 관련 컬럼 확인"""
    
    print("🔍 DHL warehouse 컬럼 누락 확인 시작")
    print("=" * 60)
    
    # 원본 데이터 경로
    hitachi_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_HITACHI(HE).xlsx'
    simense_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    used_data_path = r'MACHO_통합관리_20250702_205301\01_원본파일\MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    
    print("📊 원본 데이터 로드 중...")
    df_hitachi = pd.read_excel(hitachi_path)
    df_simense = pd.read_excel(simense_path)
    df_used = pd.read_excel(used_data_path)
    
    print(f"✅ HITACHI 원본: {df_hitachi.shape[0]}행, {df_hitachi.shape[1]}컬럼")
    print(f"✅ SIMENSE 원본: {df_simense.shape[0]}행, {df_simense.shape[1]}컬럼")
    print(f"✅ 사용된 데이터: {df_used.shape[0]}행, {df_used.shape[1]}컬럼")
    
    # 1. HITACHI 원본 전체 컬럼 분석
    print("\n📋 HITACHI 원본 전체 컬럼 리스트:")
    print("=" * 50)
    for i, col in enumerate(df_hitachi.columns, 1):
        print(f"{i:2d}. {col}")
    
    # 2. DHL 관련 컬럼 찾기
    print("\n🔍 DHL 관련 컬럼 검색:")
    print("=" * 30)
    
    # DHL 관련 키워드로 검색
    dhl_keywords = ['DHL', 'dhl', 'Dhl', 'warehouse', 'Warehouse', 'WAREHOUSE']
    
    hitachi_dhl_cols = []
    simense_dhl_cols = []
    used_dhl_cols = []
    
    for col in df_hitachi.columns:
        for keyword in dhl_keywords:
            if keyword in col:
                hitachi_dhl_cols.append(col)
                break
    
    for col in df_simense.columns:
        for keyword in dhl_keywords:
            if keyword in col:
                simense_dhl_cols.append(col)
                break
    
    for col in df_used.columns:
        for keyword in dhl_keywords:
            if keyword in col:
                used_dhl_cols.append(col)
                break
    
    print(f"📋 HITACHI DHL 관련 컬럼 ({len(hitachi_dhl_cols)}개):")
    for col in hitachi_dhl_cols:
        print(f"  - {col}")
    
    print(f"\n📋 SIMENSE DHL 관련 컬럼 ({len(simense_dhl_cols)}개):")
    for col in simense_dhl_cols:
        print(f"  - {col}")
    
    print(f"\n📋 사용된 데이터 DHL 관련 컬럼 ({len(used_dhl_cols)}개):")
    for col in used_dhl_cols:
        print(f"  - {col}")
    
    # 3. 누락된 컬럼 확인
    print("\n🚨 누락된 DHL 컬럼 분석:")
    print("=" * 35)
    
    # 원본에는 있지만 사용된 데이터에 없는 컬럼
    hitachi_missing = set(hitachi_dhl_cols) - set(used_dhl_cols)
    simense_missing = set(simense_dhl_cols) - set(used_dhl_cols)
    
    print(f"📋 HITACHI에서 누락된 DHL 컬럼 ({len(hitachi_missing)}개):")
    for col in sorted(hitachi_missing):
        print(f"  ❌ {col}")
    
    print(f"\n📋 SIMENSE에서 누락된 DHL 컬럼 ({len(simense_missing)}개):")
    for col in sorted(simense_missing):
        print(f"  ❌ {col}")
    
    # 4. 전체 누락 컬럼 분석
    print("\n📊 전체 누락 컬럼 분석:")
    print("=" * 30)
    
    all_hitachi_missing = set(df_hitachi.columns) - set(df_used.columns)
    all_simense_missing = set(df_simense.columns) - set(df_used.columns)
    
    print(f"📋 HITACHI 전체 누락 컬럼 ({len(all_hitachi_missing)}개):")
    for col in sorted(all_hitachi_missing):
        print(f"  - {col}")
    
    print(f"\n📋 SIMENSE 전체 누락 컬럼 ({len(all_simense_missing)}개):")
    for col in sorted(all_simense_missing):
        print(f"  - {col}")
    
    # 5. 샘플 데이터 확인
    if hitachi_dhl_cols:
        print(f"\n📋 HITACHI DHL 컬럼 샘플 데이터:")
        for col in hitachi_dhl_cols[:3]:  # 처음 3개 컬럼만
            print(f"  {col}: {df_hitachi[col].head(5).tolist()}")
    
    if simense_dhl_cols:
        print(f"\n📋 SIMENSE DHL 컬럼 샘플 데이터:")
        for col in simense_dhl_cols[:3]:  # 처음 3개 컬럼만
            print(f"  {col}: {df_simense[col].head(5).tolist()}")
    
    return {
        'hitachi_dhl_cols': hitachi_dhl_cols,
        'simense_dhl_cols': simense_dhl_cols,
        'used_dhl_cols': used_dhl_cols,
        'hitachi_missing': list(hitachi_missing),
        'simense_missing': list(simense_missing),
        'all_hitachi_missing': list(all_hitachi_missing),
        'all_simense_missing': list(all_simense_missing)
    }

if __name__ == "__main__":
    result = check_dhl_warehouse_columns()
    
    print("\n✅ DHL warehouse 컬럼 분석 완료!")
    print("=" * 50)
    
    if result['hitachi_missing'] or result['simense_missing']:
        print("🚨 누락된 DHL 컬럼이 발견되었습니다!")
        print("🔧 복구 작업이 필요합니다.")
    else:
        print("✅ DHL 관련 컬럼은 모두 정상적으로 포함되어 있습니다.") 