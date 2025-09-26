"""
🔍 _calc_monthly_records 함수 상세 디버깅
"""

import pandas as pd
import numpy as np
from pathlib import Path
from hvdc_excel_reporter_final_rev import (
    unify_warehouse_columns,
    get_active_warehouse_list,
    convert_warehouse_dates,
    _calc_monthly_records,
    _safe_to_int
)

def debug_calc_monthly_records():
    """_calc_monthly_records 함수 상세 디버깅"""
    
    # 데이터 로드 및 전처리
    data_path = Path("data")
    hitachi_file = data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
    simense_file = data_path / "HVDC WAREHOUSE_SIMENSE(SIM)_FIXED.xlsx"
    
    combined_dfs = []
    
    # HITACHI 데이터 로드
    if hitachi_file.exists():
        hitachi_data = pd.read_excel(hitachi_file, engine="openpyxl")
        hitachi_data["Vendor"] = "HITACHI"
        combined_dfs.append(hitachi_data)
    
    # SIMENSE 데이터 로드
    if simense_file.exists():
        simense_data = pd.read_excel(simense_file, engine="openpyxl")
        simense_data["Vendor"] = "SIMENSE"
        combined_dfs.append(simense_data)
    
    df = pd.concat(combined_dfs, ignore_index=True, sort=False)
    
    # 컬럼 정규화 및 날짜 변환
    df = unify_warehouse_columns(df)
    WAREHOUSE_LIST = get_active_warehouse_list(df)
    SITE_LIST = ["AGI", "DAS", "MIR", "SHU"]

    # 중복 컬럼 진단 및 제거
    from collections import Counter
    col_counts = Counter(df.columns)
    for col, cnt in col_counts.items():
        if cnt > 1:
            print(f"중복 컬럼: {col} ({cnt}회)")
    df = df.loc[:, ~df.columns.duplicated()]

    # 중복 제거 후 날짜 변환
    unique_cols = list(dict.fromkeys(WAREHOUSE_LIST + SITE_LIST))  # 중복 제거
    df = convert_warehouse_dates(df, unique_cols)
    
    # Inbound/Outbound 날짜 강제 재계산
    df.drop(["Inbound_Date", "Outbound_Date"], axis=1, errors="ignore", inplace=True)
    df["Inbound_Date"] = df[WAREHOUSE_LIST].min(axis=1)
    df["Outbound_Date"] = df[WAREHOUSE_LIST].max(axis=1)
    
    # 월별 기간 생성
    min_date = df["Inbound_Date"].min()
    max_date = df["Inbound_Date"].max()
    months = pd.date_range(
        min_date.date().replace(day=1), 
        max_date.date().replace(day=1), 
        freq="MS"
    )
    
    print("=== _calc_monthly_records 상세 디버깅 ===")
    print(f"입력 데이터 shape: {df.shape}")
    print(f"WAREHOUSE_LIST: {WAREHOUSE_LIST}")
    print(f"집계 월 수: {len(months)}개")
    print(f"집계 기간: {months[0]} ~ {months[-1]}")
    
    # prev_stock 계산 디버깅
    print("\n=== prev_stock 계산 디버깅 ===")
    for wh in WAREHOUSE_LIST:
        if wh not in df.columns:
            print(f"{wh}: 컬럼 없음")
            continue
            
        in_before = (pd.to_datetime(df[wh], errors="coerce") < months[0])
        out_col = f"Out_Date_{wh}"
        
        if out_col in df.columns:
            after_start = pd.to_datetime(df[out_col], errors="coerce") >= months[0]
            out_na = df[out_col].isna()
            valid_row = in_before & (out_na | after_start)
        else:
            valid_row = in_before
            
        pkg_sum = df.loc[valid_row, "Pkg"].fillna(1) if "Pkg" in df.columns else valid_row
        prev_stock_val = _safe_to_int(pkg_sum)
        
        print(f"{wh}: in_before={in_before.sum()}, valid_row={valid_row.sum()}, prev_stock={prev_stock_val}")
    
    # 월별 집계 디버깅 (첫 번째 월만)
    print("\n=== 첫 번째 월 집계 디버깅 ===")
    first_month = months[0]
    month_end = first_month + pd.offsets.MonthEnd(0)
    month_key = month_end.strftime("%Y-%m")
    
    print(f"첫 번째 월: {month_key}")
    
    for wh in WAREHOUSE_LIST:
        if wh not in df.columns:
            print(f"{wh}: 컬럼 없음")
            continue
            
        # 입고 mask
        in_mask = (
            df[wh].notna() & 
            (pd.to_datetime(df[wh], errors="coerce").dt.to_period("M") == month_end.to_period("M"))
        )
        
        # 출고 mask (컬럼 존재 여부 체크)
        out_col = f"Out_Date_{wh}"
        if out_col in df.columns:
            out_mask = (
                df[out_col].notna() &
                (pd.to_datetime(df[out_col], errors="coerce").dt.to_period("M") == month_end.to_period("M"))
            )
        else:
            out_mask = pd.Series([False] * len(df), index=df.index)

        in_qty = _safe_to_int(df.loc[in_mask, "Pkg"].fillna(1)) if "Pkg" in df.columns else in_mask.sum()
        out_qty = _safe_to_int(df.loc[out_mask, "Pkg"].fillna(1)) if "Pkg" in df.columns else out_mask.sum()

        print(f"{wh}: in_mask={in_mask.sum()}, out_mask={out_mask.sum()}, in_qty={in_qty}, out_qty={out_qty}")
    
    # 실제 함수 실행
    print("\n=== 실제 _calc_monthly_records 실행 ===")
    result = _calc_monthly_records(df, months, WAREHOUSE_LIST)
    
    print(f"결과 shape: {result.shape}")
    print(f"결과 컬럼: {result.columns.tolist()}")
    
    # 첫 번째 월 결과 확인
    if len(result) > 0:
        first_row = result.iloc[0]
        print(f"\n첫 번째 월 ({first_row['입고월']}) 결과:")
        for col in result.columns:
            if col != '입고월':
                print(f"  {col}: {first_row[col]}")
    
    # 전체 결과 요약
    print(f"\n=== 전체 결과 요약 ===")
    for col in result.columns:
        if col != '입고월':
            total = result[col].sum()
            non_zero = (result[col] != 0).sum()
            print(f"{col}: total={total}, non_zero_months={non_zero}/{len(result)}")

if __name__ == "__main__":
    debug_calc_monthly_records() 