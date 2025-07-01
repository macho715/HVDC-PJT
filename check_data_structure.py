#!/usr/bin/env python3
"""
실제 데이터 구조 및 Case ID, WH 컬럼 사용 현황 분석
"""
import pandas as pd
import numpy as np

def analyze_data_structure():
    """실제 데이터 구조 분석"""
    
    # HITACHI 파일 분석
    print('🔍 HITACHI 파일 샘플 데이터 분석')
    df_he = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx', nrows=100)
    
    print(f'   📋 총 행 수: {len(df_he)}')
    print(f'   📋 고유 HVDC CODE 수: {df_he["HVDC CODE"].nunique()}')
    if "Case No." in df_he.columns:
        print(f'   📋 고유 Case No. 수: {df_he["Case No."].nunique()}')
    
    # HVDC CODE 샘플
    hvdc_codes = df_he['HVDC CODE'].dropna().unique()[:5]
    print(f'   🎯 HVDC CODE 샘플: {list(hvdc_codes)}')
    
    # WH 컬럼 데이터 확인
    wh_cols_he = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP']
    print('   🏢 HITACHI WH 컬럼 데이터 존재 현황:')
    for col in wh_cols_he:
        if col in df_he.columns:
            non_null = df_he[col].notna().sum()
            print(f'      {col}: {non_null}건 데이터 존재')
    
    # 한 케이스의 WH 데이터 패턴 확인
    sample_case = df_he['HVDC CODE'].dropna().iloc[0]
    case_data = df_he[df_he['HVDC CODE'] == sample_case]
    print(f'   📦 샘플 케이스 {sample_case}의 WH 패턴:')
    for col in wh_cols_he:
        if col in case_data.columns:
            values = case_data[col].dropna().unique()
            if len(values) > 0:
                print(f'      {col}: {list(values)[:3]}')
    
    print('')
    print('🔍 SIMENSE 파일 샘플 데이터 분석')
    df_sim = pd.read_excel('data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx', nrows=100)
    
    print(f'   📋 총 행 수: {len(df_sim)}')
    print(f'   📋 고유 SERIAL NO. 수: {df_sim["SERIAL NO."].nunique()}')
    
    # SERIAL NO. 샘플
    serial_nos = df_sim['SERIAL NO.'].dropna().unique()[:5]
    print(f'   🎯 SERIAL NO. 샘플: {list(serial_nos)}')
    
    # WH 컬럼 데이터 확인
    wh_cols_sim = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'DSV MZD', 'JDN MZD', 'AAA  Storage']
    print('   🏢 SIMENSE WH 컬럼 데이터 존재 현황:')
    for col in wh_cols_sim:
        if col in df_sim.columns:
            non_null = df_sim[col].notna().sum()
            print(f'      {col}: {non_null}건 데이터 존재')
    
    # MOSB 데이터 확인
    print('')
    print('🌊 MOSB 컬럼 데이터 확인:')
    for df_name, df in [('HITACHI', df_he), ('SIMENSE', df_sim)]:
        if 'MOSB' in df.columns:
            mosb_count = df['MOSB'].notna().sum()
            print(f'   {df_name}: MOSB 데이터 {mosb_count}건 존재')
            if mosb_count > 0:
                mosb_values = df['MOSB'].dropna().unique()[:3]
                print(f'      샘플 값: {list(mosb_values)}')

def analyze_wh_pattern():
    """WH 컬럼 패턴 분석 - 중복 처리 방식 확인"""
    print('')
    print('🔍 WH 중복 패턴 분석')
    
    # 첫 번째 파일에서 샘플 케이스 분석
    df_he = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx', nrows=500)
    
    # 하나의 케이스에서 여러 WH 컬럼에 데이터가 있는 경우 찾기
    wh_cols = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP']
    
    for case in df_he['HVDC CODE'].dropna().unique()[:10]:
        case_data = df_he[df_he['HVDC CODE'] == case]
        wh_count = 0
        wh_list = []
        
        for col in wh_cols:
            if col in case_data.columns and case_data[col].notna().any():
                wh_count += 1
                wh_list.append(col)
        
        if wh_count >= 2:
            print(f'   📦 케이스 {case}: {wh_count}개 WH 사용 → {wh_list}')
            
            # 같은 WH에 중복 데이터가 있는지 확인
            for col in wh_list:
                values = case_data[col].dropna()
                if len(values) > 1:
                    print(f'      {col}: {len(values)}개 중복 데이터 → {list(values.unique())}')
            break

if __name__ == "__main__":
    analyze_data_structure()
    analyze_wh_pattern() 