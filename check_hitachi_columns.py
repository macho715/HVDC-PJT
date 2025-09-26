#!/usr/bin/env python3
"""
HITACHI 파일 컬럼 구조 상세 확인
MACHO-GPT v3.4-mini | 모든 시트의 컬럼 구조 분석

목적:
1. 모든 시트의 컬럼 구조 확인
2. 데이터 샘플 출력
3. 통합 가능성 검토
"""

import pandas as pd
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_hitachi_columns():
    """HITACHI 파일의 모든 시트 컬럼 구조 확인"""
    file_path = "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
    
    logger.info("HITACHI 파일 컬럼 구조 분석 시작")
    
    # Excel 파일 로드
    excel_file = pd.ExcelFile(file_path)
    
    print("\n" + "="*80)
    print("HITACHI 파일 전체 시트 분석")
    print("="*80)
    
    all_sheets_data = {}
    
    for i, sheet_name in enumerate(excel_file.sheet_names):
        print(f"\n[시트 {i+1}] '{sheet_name}'")
        print("-" * 60)
        
        # 시트 데이터 로드
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        all_sheets_data[sheet_name] = df
        
        print(f"데이터 크기: {len(df):,}행 x {len(df.columns)}열")
        
        # 컬럼 목록 출력 (처음 20개만)
        print(f"컬럼 목록 ({len(df.columns)}개):")
        display_cols = df.columns[:20] if len(df.columns) > 20 else df.columns
        for j, col in enumerate(display_cols, 1):
            print(f"  {j:2d}. {col}")
        
        if len(df.columns) > 20:
            print(f"  ... 추가 {len(df.columns) - 20}개 컬럼")
        
        # 창고/현장 관련 컬럼 찾기
        warehouse_cols = [col for col in df.columns if any(wh in str(col) for wh in ['DSV', 'MOSB', 'AAA', 'Hauler', 'DHL'])]
        site_cols = [col for col in df.columns if any(site in str(col) for site in ['AGI', 'DAS', 'MIR', 'SHU', 'Site'])]
        
        if warehouse_cols:
            print(f"\n[창고 관련 컬럼]: {warehouse_cols}")
        if site_cols:
            print(f"[현장 관련 컬럼]: {site_cols}")
        
        print("-" * 60)
    
    # 시트별 컬럼 일치성 확인
    print(f"\n" + "="*80)
    print("시트별 컬럼 일치성 분석")
    print("="*80)
    
    sheet_columns = {name: set(df.columns) for name, df in all_sheets_data.items()}
    
    # 공통 컬럼 찾기
    if sheet_columns:
        common_columns = set.intersection(*sheet_columns.values())
        print(f"모든 시트 공통 컬럼 ({len(common_columns)}개):")
        for col in sorted(list(common_columns)[:10]):  # 처음 10개만 출력
            print(f"  - {col}")
        if len(common_columns) > 10:
            print(f"  ... 추가 {len(common_columns) - 10}개")
    
    # 통합 가능성 평가
    print(f"\n" + "="*80)
    print("통합 가능성 평가")
    print("="*80)
    
    total_rows = sum(len(df) for df in all_sheets_data.values())
    print(f"전체 데이터: {total_rows:,}건")
    
    # 컬럼 구조가 동일한 시트들
    column_groups = {}
    for sheet_name, columns in sheet_columns.items():
        col_signature = tuple(sorted(columns))
        if col_signature not in column_groups:
            column_groups[col_signature] = []
        column_groups[col_signature].append(sheet_name)
    
    print(f"\n컬럼 구조 그룹:")
    for i, (signature, sheets) in enumerate(column_groups.items(), 1):
        print(f"  그룹 {i} ({len(signature)}개 컬럼): {sheets}")
        if len(sheets) > 1:
            print(f"    -> 통합 가능한 시트들")
    
    return all_sheets_data, common_columns

if __name__ == "__main__":
    try:
        all_sheets_data, common_columns = check_hitachi_columns()
        
        print(f"\n" + "="*80)
        print("HITACHI 컬럼 구조 분석 완료!")
        print("="*80)
        print(f"총 시트: {len(all_sheets_data)}개")
        print(f"공통 컬럼: {len(common_columns)}개")
        print(f"총 데이터: {sum(len(df) for df in all_sheets_data.values()):,}건")
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}")
        print(f"오류: {e}") 