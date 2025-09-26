#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
누락된 컬럼 확인 스크립트
Status_Location과 Status_Location_Date 컬럼 분석
"""

import pandas as pd

def check_missing_columns():
    """누락된 컬럼들 확인"""
    
    print("🔍 누락된 컬럼 확인 시작")
    print("=" * 50)
    
    # 원본 데이터 로드
    hitachi_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_HITACHI(HE).xlsx'
    simense_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    used_data_path = r'MACHO_통합관리_20250702_205301\01_원본파일\MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    
    df_hitachi = pd.read_excel(hitachi_path)
    df_simense = pd.read_excel(simense_path)
    df_used = pd.read_excel(used_data_path)
    
    print(f"📊 HITACHI 총 컬럼수: {len(df_hitachi.columns)}")
    print(f"📊 SIMENSE 총 컬럼수: {len(df_simense.columns)}")
    print(f"📊 사용된 데이터 총 컬럼수: {len(df_used.columns)}")
    
    # Status/Location 관련 컬럼 찾기
    hitachi_status_cols = [col for col in df_hitachi.columns if 'Status' in col or 'Location' in col]
    simense_status_cols = [col for col in df_simense.columns if 'Status' in col or 'Location' in col]
    used_status_cols = [col for col in df_used.columns if 'Status' in col or 'Location' in col]
    
    print("\n🔍 Status/Location 관련 컬럼 확인")
    print("=" * 40)
    print(f"📋 HITACHI Status/Location 컬럼: {hitachi_status_cols}")
    print(f"📋 SIMENSE Status/Location 컬럼: {simense_status_cols}")
    print(f"📋 사용된 데이터 Status/Location 컬럼: {used_status_cols}")
    
    # 전체 컬럼 리스트 출력
    print("\n📋 HITACHI 전체 컬럼 리스트:")
    for i, col in enumerate(df_hitachi.columns, 1):
        print(f"{i:2d}. {col}")
    
    print("\n📋 SIMENSE 전체 컬럼 리스트:")
    for i, col in enumerate(df_simense.columns, 1):
        print(f"{i:2d}. {col}")
    
    # 누락된 컬럼 확인
    print("\n🚨 누락된 컬럼 분석")
    print("=" * 30)
    
    # 원본에 있지만 사용된 데이터에 없는 컬럼
    hitachi_missing = set(df_hitachi.columns) - set(df_used.columns)
    simense_missing = set(df_simense.columns) - set(df_used.columns)
    
    print(f"📋 HITACHI에서 누락된 컬럼 ({len(hitachi_missing)}개):")
    for col in sorted(hitachi_missing):
        print(f"  - {col}")
    
    print(f"\n📋 SIMENSE에서 누락된 컬럼 ({len(simense_missing)}개):")
    for col in sorted(simense_missing):
        print(f"  - {col}")
    
    # Status_Location과 Status_Location_Date 특별 확인
    target_cols = ['Status_Location', 'Status_Location_Date']
    
    print("\n🎯 특별 확인: Status_Location, Status_Location_Date")
    print("=" * 45)
    
    for col in target_cols:
        print(f"\n📋 {col} 컬럼:")
        print(f"  - HITACHI: {'✅ 있음' if col in df_hitachi.columns else '❌ 없음'}")
        print(f"  - SIMENSE: {'✅ 있음' if col in df_simense.columns else '❌ 없음'}")
        print(f"  - 사용된 데이터: {'✅ 있음' if col in df_used.columns else '❌ 없음'}")
        
        # 있다면 샘플 데이터 확인
        if col in df_hitachi.columns:
            print(f"  - HITACHI 샘플: {df_hitachi[col].head(3).tolist()}")
        if col in df_simense.columns:
            print(f"  - SIMENSE 샘플: {df_simense[col].head(3).tolist()}")
        if col in df_used.columns:
            print(f"  - 사용된 데이터 샘플: {df_used[col].head(3).tolist()}")

if __name__ == "__main__":
    check_missing_columns() 