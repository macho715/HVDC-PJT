#!/usr/bin/env python3
"""
창고 입고/출고 집계 문제 분석 스크립트
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_warehouse_data():
    """실제 데이터의 창고 관련 컬럼들을 분석"""
    print('🔍 창고 입고/출고 집계 문제 분석')
    print('=' * 60)

    # HITACHI 데이터 분석
    hitachi_df = pd.read_excel('../data/HVDC WAREHOUSE_HITACHI(HE).xlsx', sheet_name='Case List')
    print(f'📊 HITACHI 데이터: {len(hitachi_df)} 건')

    # 창고 관련 컬럼들 확인
    warehouse_cols = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB']
    print(f'\n📋 창고 컬럼 데이터 타입:')
    
    for col in warehouse_cols:
        if col in hitachi_df.columns:
            print(f'   {col}: {hitachi_df[col].dtype}')
            non_null_count = hitachi_df[col].notna().sum()
            print(f'      Non-null 값: {non_null_count}개')
            if non_null_count > 0:
                sample_values = hitachi_df[col].dropna().head(3).tolist()
                print(f'      샘플 값: {sample_values}')
        else:
            print(f'   {col}: 컬럼 없음')
        print()

    # Status 컬럼 분석
    print('\n📋 Status 컬럼 분석:')
    status_cols = ['Status_Storage', 'Status_Location', 'Status_Current']
    for col in status_cols:
        if col in hitachi_df.columns:
            print(f'   {col}: {hitachi_df[col].dtype}')
            print(f'      값 분포: {hitachi_df[col].value_counts().head(5).to_dict()}')
        else:
            print(f'   {col}: 컬럼 없음')
        print()

    # 실제 창고 데이터가 있는 컬럼들 찾기
    print('\n📋 실제 창고 데이터가 있는 컬럼들:')
    for col in hitachi_df.columns:
        if any(wh in str(col) for wh in ['DSV', 'MOSB', 'AAA', 'Hauler']):
            non_null_count = hitachi_df[col].notna().sum()
            if non_null_count > 0:
                print(f'   {col}: {non_null_count}개 non-null 값')
                if hitachi_df[col].dtype == 'object':
                    unique_vals = hitachi_df[col].dropna().unique()[:5]
                    print(f'      샘플 값: {unique_vals}')
                elif pd.api.types.is_numeric_dtype(hitachi_df[col]):
                    non_zero_count = (hitachi_df[col] > 0).sum()
                    print(f'      0보다 큰 값: {non_zero_count}개')
                    if non_zero_count > 0:
                        print(f'      최대값: {hitachi_df[col].max()}')
                        print(f'      최소값: {hitachi_df[col].min()}')
                print()

    # 날짜 컬럼 분석
    print('\n📋 날짜 컬럼 분석:')
    date_cols = [col for col in hitachi_df.columns if 'Date' in str(col)]
    for col in date_cols:
        print(f'   {col}: {hitachi_df[col].dtype}')
        non_null_count = hitachi_df[col].notna().sum()
        print(f'      Non-null 값: {non_null_count}개')
        if non_null_count > 0:
            print(f'      날짜 범위: {hitachi_df[col].min()} ~ {hitachi_df[col].max()}')
        print()

if __name__ == "__main__":
    analyze_warehouse_data() 