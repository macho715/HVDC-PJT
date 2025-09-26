#!/usr/bin/env python3
"""
HITACHI, SIMENSE 데이터의 스택 적재 기반 SQM 분석
Stack_Status에 따른 실제 창고 면적 계산
"""

import pandas as pd
import numpy as np

def analyze_stack_sqm():
    """스택 적재 기반 SQM 분석"""
    
    print("🏗️ 스택 적재 기반 SQM 분석")
    print("=" * 70)
    
    try:
        # HITACHI 데이터 로드
        print("📦 HITACHI 데이터 분석")
        hitachi_df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx')
        print(f"✅ HITACHI 총 {len(hitachi_df)}건")
        
        # 새로운 컬럼 확인
        hitachi_cols = hitachi_df.columns.tolist()
        print("HITACHI 컬럼:", [col for col in hitachi_cols if 'SQM' in str(col).upper() or 'STACK' in str(col).upper()])
        
        # SQM, Stack_Status 컬럼 찾기
        sqm_col = None
        stack_col = None
        
        for col in hitachi_cols:
            if 'SQM' in str(col).upper() and 'SQM' == str(col).upper():
                sqm_col = col
            elif 'STACK' in str(col).upper():
                stack_col = col
        
        print(f"SQM 컬럼: {sqm_col}")
        print(f"Stack_Status 컬럼: {stack_col}")
        
        if sqm_col and stack_col:
            # HITACHI 스택 분석
            analyze_stack_data(hitachi_df, sqm_col, stack_col, "HITACHI")
        
        print(f"\n" + "="*50)
        
        # SIMENSE 데이터 로드
        print("📦 SIMENSE 데이터 분석")
        simense_df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx')
        print(f"✅ SIMENSE 총 {len(simense_df)}건")
        
        # 새로운 컬럼 확인
        simense_cols = simense_df.columns.tolist()
        print("SIMENSE 컬럼:", [col for col in simense_cols if 'SQM' in str(col).upper() or 'STACK' in str(col).upper()])
        
        # SQM, Stack_Status 컬럼 찾기
        sqm_col_sim = None
        stack_col_sim = None
        
        for col in simense_cols:
            if 'SQM' in str(col).upper() and 'SQM' == str(col).upper():
                sqm_col_sim = col
            elif 'STACK' in str(col).upper():
                stack_col_sim = col
        
        print(f"SQM 컬럼: {sqm_col_sim}")
        print(f"Stack_Status 컬럼: {stack_col_sim}")
        
        if sqm_col_sim and stack_col_sim:
            # SIMENSE 스택 분석
            analyze_stack_data(simense_df, sqm_col_sim, stack_col_sim, "SIMENSE")
        
        # 통합 분석
        if sqm_col and stack_col and sqm_col_sim and stack_col_sim:
            print(f"\n=== 통합 스택 적재 분석 ===")
            combined_analysis(hitachi_df, simense_df, sqm_col, stack_col, sqm_col_sim, stack_col_sim)
        
        print("\n" + "="*70)
        print("🎯 스택 적재 SQM 분석 완료")
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        import traceback
        traceback.print_exc()

def analyze_stack_data(df, sqm_col, stack_col, vendor_name):
    """개별 벤더 스택 데이터 분석"""
    
    print(f"\n=== {vendor_name} 스택 적재 분석 ===")
    
    # NULL 값 확인
    sqm_null = df[sqm_col].isnull().sum()
    stack_null = df[stack_col].isnull().sum()
    print(f"SQM NULL: {sqm_null}개, Stack_Status NULL: {stack_null}개")
    
    # 유효한 데이터만 필터링
    valid_data = df[(df[sqm_col].notna()) & (df[stack_col].notna())].copy()
    print(f"유효한 데이터: {len(valid_data)}건")
    
    if len(valid_data) == 0:
        print("❌ 유효한 데이터가 없습니다.")
        return
    
    # Stack_Status 분포
    print(f"\nStack_Status 분포:")
    stack_dist = valid_data[stack_col].value_counts().sort_index()
    for stack, count in stack_dist.items():
        print(f"  {stack}단 적재: {count}건")
    
    # 실제 창고 면적 계산
    def calculate_actual_sqm(row):
        sqm_value = row[sqm_col]
        stack_value = row[stack_col]
        
        if pd.isna(sqm_value) or pd.isna(stack_value):
            return np.nan
        
        try:
            stack_num = int(stack_value)
            if stack_num >= 1:
                return sqm_value / stack_num
            else:
                return sqm_value
        except:
            return sqm_value
    
    valid_data['Actual_SQM'] = valid_data.apply(calculate_actual_sqm, axis=1)
    
    # 통계 분석
    print(f"\n개별화물 SQM 통계:")
    sqm_stats = valid_data[sqm_col].describe()
    print(f"  총합: {valid_data[sqm_col].sum():,.1f} SQM")
    print(f"  평균: {sqm_stats['mean']:.1f} SQM")
    print(f"  범위: {sqm_stats['min']:.1f} ~ {sqm_stats['max']:.1f} SQM")
    
    print(f"\n실제 창고 면적 통계:")
    actual_stats = valid_data['Actual_SQM'].describe()
    print(f"  총합: {valid_data['Actual_SQM'].sum():,.1f} SQM")
    print(f"  평균: {actual_stats['mean']:.1f} SQM")
    print(f"  범위: {actual_stats['min']:.1f} ~ {actual_stats['max']:.1f} SQM")
    
    print(f"\n면적 절약 효과:")
    original_total = valid_data[sqm_col].sum()
    actual_total = valid_data['Actual_SQM'].sum()
    saving = original_total - actual_total
    saving_rate = (saving / original_total) * 100
    print(f"  원본 면적: {original_total:,.1f} SQM")
    print(f"  실제 면적: {actual_total:,.1f} SQM")
    print(f"  절약 면적: {saving:,.1f} SQM ({saving_rate:.1f}%)")
    
    # 스택별 상세 분석
    print(f"\n스택별 상세 분석:")
    stack_analysis = valid_data.groupby(stack_col).agg({
        sqm_col: ['count', 'sum', 'mean'],
        'Actual_SQM': ['sum', 'mean']
    }).round(1)
    
    for stack_level in stack_analysis.index:
        print(f"\n  📋 {stack_level}단 적재:")
        row = stack_analysis.loc[stack_level]
        print(f"    건수: {row[(sqm_col, 'count')]:,.0f}건")
        print(f"    개별화물 SQM: {row[(sqm_col, 'sum')]:,.1f} SQM")
        print(f"    실제 창고 SQM: {row[('Actual_SQM', 'sum')]:,.1f} SQM")
        print(f"    평균 개별 SQM: {row[(sqm_col, 'mean')]:,.1f} SQM")
        print(f"    평균 실제 SQM: {row[('Actual_SQM', 'mean')]:,.1f} SQM")
    
    # 샘플 데이터 출력
    print(f"\n샘플 데이터 (상위 5건):")
    sample_cols = [sqm_col, stack_col, 'Actual_SQM']
    if 'HVDC CODE' in valid_data.columns:
        sample_cols = ['HVDC CODE'] + sample_cols
    
    sample_data = valid_data[sample_cols].head()
    for idx, (_, row) in enumerate(sample_data.iterrows(), 1):
        print(f"  케이스 {idx}:")
        for col in sample_cols:
            if col in row.index:
                print(f"    {col}: {row[col]}")

def combined_analysis(hitachi_df, simense_df, hitachi_sqm, hitachi_stack, simense_sqm, simense_stack):
    """통합 분석"""
    
    # HITACHI 처리
    hitachi_valid = hitachi_df[(hitachi_df[hitachi_sqm].notna()) & (hitachi_df[hitachi_stack].notna())].copy()
    hitachi_valid['Actual_SQM'] = hitachi_valid.apply(
        lambda row: row[hitachi_sqm] / max(1, int(row[hitachi_stack])) if pd.notna(row[hitachi_stack]) else row[hitachi_sqm], 
        axis=1
    )
    hitachi_valid['Vendor'] = 'HITACHI'
    
    # SIMENSE 처리
    simense_valid = simense_df[(simense_df[simense_sqm].notna()) & (simense_df[simense_stack].notna())].copy()
    simense_valid['Actual_SQM'] = simense_valid.apply(
        lambda row: row[simense_sqm] / max(1, int(row[simense_stack])) if pd.notna(row[simense_stack]) else row[simense_sqm], 
        axis=1
    )
    simense_valid['Vendor'] = 'SIMENSE'
    
    print(f"전체 통합 통계:")
    print(f"  HITACHI: {len(hitachi_valid)}건, 실제 SQM: {hitachi_valid['Actual_SQM'].sum():,.1f}")
    print(f"  SIMENSE: {len(simense_valid)}건, 실제 SQM: {simense_valid['Actual_SQM'].sum():,.1f}")
    print(f"  총계: {len(hitachi_valid) + len(simense_valid)}건, 실제 SQM: {hitachi_valid['Actual_SQM'].sum() + simense_valid['Actual_SQM'].sum():,.1f}")
    
    # 스택 레벨별 통합 분석
    print(f"\n통합 스택 레벨 분석:")
    hitachi_stack_summary = hitachi_valid.groupby(hitachi_stack)['Actual_SQM'].agg(['count', 'sum']).add_prefix('HITACHI_')
    simense_stack_summary = simense_valid.groupby(simense_stack)['Actual_SQM'].agg(['count', 'sum']).add_prefix('SIMENSE_')
    
    all_stack_levels = set(hitachi_stack_summary.index) | set(simense_stack_summary.index)
    for level in sorted(all_stack_levels):
        print(f"\n  {level}단 적재:")
        if level in hitachi_stack_summary.index:
            print(f"    HITACHI: {hitachi_stack_summary.loc[level, 'HITACHI_count']:.0f}건, {hitachi_stack_summary.loc[level, 'HITACHI_sum']:,.1f} SQM")
        if level in simense_stack_summary.index:
            print(f"    SIMENSE: {simense_stack_summary.loc[level, 'SIMENSE_count']:.0f}건, {simense_stack_summary.loc[level, 'SIMENSE_sum']:,.1f} SQM")

if __name__ == "__main__":
    analyze_stack_sqm() 