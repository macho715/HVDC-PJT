#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 컬럼 확인 스크립트
"""

import pandas as pd

def quick_check():
    """빠른 컬럼 확인"""
    
    # 원본 데이터 로드
    hitachi_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_HITACHI(HE).xlsx'
    simense_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    used_data_path = r'MACHO_통합관리_20250702_205301\01_원본파일\MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    
    print("📊 데이터 로드 중...")
    df_hitachi = pd.read_excel(hitachi_path)
    df_simense = pd.read_excel(simense_path)
    df_used = pd.read_excel(used_data_path)
    
    print(f"✅ HITACHI: {df_hitachi.shape[0]}행, {df_hitachi.shape[1]}컬럼")
    print(f"✅ SIMENSE: {df_simense.shape[0]}행, {df_simense.shape[1]}컬럼")
    print(f"✅ 사용된 데이터: {df_used.shape[0]}행, {df_used.shape[1]}컬럼")
    
    # Status/Location 관련 컬럼만 확인
    print("\n🔍 Status/Location 관련 컬럼:")
    
    h_status = [col for col in df_hitachi.columns if 'Status' in col or 'Location' in col]
    s_status = [col for col in df_simense.columns if 'Status' in col or 'Location' in col]
    u_status = [col for col in df_used.columns if 'Status' in col or 'Location' in col]
    
    print(f"HITACHI: {h_status}")
    print(f"SIMENSE: {s_status}")
    print(f"사용된 데이터: {u_status}")
    
    # 특별 확인
    target_cols = ['Status_Location', 'Status_Location_Date']
    
    print("\n🎯 특별 확인:")
    for col in target_cols:
        in_h = col in df_hitachi.columns
        in_s = col in df_simense.columns
        in_u = col in df_used.columns
        
        print(f"{col}: HITACHI({in_h}) SIMENSE({in_s}) 사용됨({in_u})")

if __name__ == "__main__":
    quick_check() 