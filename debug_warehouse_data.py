"""
🔍 HVDC Warehouse Data Debugging Script
가이드에 따른 단계별 디버깅 코드
"""

import pandas as pd
import numpy as np
from pathlib import Path
from hvdc_excel_reporter_final_rev import (
    unify_warehouse_columns,
    get_active_warehouse_list,
    convert_warehouse_dates,
    debug_warehouse_nonnull_dates
)

def load_and_debug_data():
    """데이터 로드 및 단계별 디버깅"""
    
    # 데이터 로드
    data_path = Path("data")
    hitachi_file = data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
    simense_file = data_path / "HVDC WAREHOUSE_SIMENSE(SIM)_FIXED.xlsx"
    
    print("=== 데이터 로드 시작 ===")
    
    combined_dfs = []
    
    # HITACHI 데이터 로드
    if hitachi_file.exists():
        print(f"📊 HITACHI 데이터 로드: {hitachi_file}")
        hitachi_data = pd.read_excel(hitachi_file, engine="openpyxl")
        hitachi_data["Vendor"] = "HITACHI"
        combined_dfs.append(hitachi_data)
        print(f"✅ HITACHI 데이터 로드 완료: {len(hitachi_data)}건")
    else:
        print("❌ HITACHI 파일 없음")
    
    # SIMENSE 데이터 로드
    if simense_file.exists():
        print(f"📊 SIMENSE 데이터 로드: {simense_file}")
        simense_data = pd.read_excel(simense_file, engine="openpyxl")
        simense_data["Vendor"] = "SIMENSE"
        combined_dfs.append(simense_data)
        print(f"✅ SIMENSE 데이터 로드 완료: {len(simense_data)}건")
    else:
        print("❌ SIMENSE 파일 없음")
    
    if not combined_dfs:
        print("❌ 로드할 데이터 파일이 없습니다.")
        return None
    
    # 데이터 결합
    df = pd.concat(combined_dfs, ignore_index=True, sort=False)
    print(f"🔗 데이터 결합 완료: {len(df)}건")
    
    return df

def debug_step1_original_data(df):
    """1차 점검: 원본 Raw Data 창고 날짜 값 분포"""
    print("\n" + "="*60)
    print("1차 점검: 원본 Raw Data 창고 날짜 값 분포")
    print("="*60)
    
    # 표준 창고 리스트
    WAREHOUSE_LIST = [
        "AAA  Storage",
        "DSV Al Markaz", 
        "DSV Indoor",
        "DSV MZP",
        "DSV Outdoor",
        "Hauler Indoor",
        "MOSB",
    ]
    
    print("==== 원본 Raw Data 창고 날짜 값 분포 ====")
    for wh in WAREHOUSE_LIST:
        if wh in df.columns:
            notna_count = df[wh].notna().sum()
            unique_count = df[wh].nunique()
            sample_values = df[wh].dropna().unique()[:3]
            print(f"{wh}: notna={notna_count}, unique={unique_count}, sample={sample_values}")
        else:
            print(f"{wh}: 컬럼 없음")
    
    # 실제 존재하는 창고 컬럼들 확인
    print("\n==== 실제 존재하는 창고 컬럼들 ====")
    warehouse_cols = [col for col in df.columns if any(wh in col for wh in WAREHOUSE_LIST)]
    for col in warehouse_cols:
        notna_count = df[col].notna().sum()
        print(f"{col}: notna={notna_count}")

def debug_step2_after_normalization(df):
    """2차 점검: 정규화 후 Inbound/Outbound 산출 결과 확인"""
    print("\n" + "="*60)
    print("2차 점검: 정규화 후 Inbound/Outbound 산출 결과 확인")
    print("="*60)
    
    # 컬럼 정규화
    df = unify_warehouse_columns(df)
    WAREHOUSE_LIST = get_active_warehouse_list(df)
    SITE_LIST = ["AGI", "DAS", "MIR", "SHU"]
    
    print(f"정규화 후 WAREHOUSE_LIST: {WAREHOUSE_LIST}")
    
    # 날짜 변환
    df = convert_warehouse_dates(df, WAREHOUSE_LIST + SITE_LIST)
    
    # Inbound/Outbound 날짜 강제 재계산
    df.drop(["Inbound_Date", "Outbound_Date"], axis=1, errors="ignore", inplace=True)
    df["Inbound_Date"] = df[WAREHOUSE_LIST].min(axis=1)
    df["Outbound_Date"] = df[WAREHOUSE_LIST].max(axis=1)
    
    print("Inbound_Date notna:", df["Inbound_Date"].notna().sum())
    print("Outbound_Date notna:", df["Outbound_Date"].notna().sum())
    
    print("\nInbound/Outbound 날짜 샘플:")
    print(df[["Inbound_Date", "Outbound_Date"]].dropna().head())
    
    # 창고별 유효 날짜 수 확인
    debug_warehouse_nonnull_dates(df, WAREHOUSE_LIST)
    
    return df, WAREHOUSE_LIST

def debug_step3_calc_input(df, WAREHOUSE_LIST):
    """3차 점검: _calc_monthly_records 입력/출력 값 확인"""
    print("\n" + "="*60)
    print("3차 점검: _calc_monthly_records 입력/출력 값 확인")
    print("="*60)
    
    # 월별 기간 생성
    if "Inbound_Date" in df.columns:
        min_date = df["Inbound_Date"].min()
        max_date = df["Inbound_Date"].max()
    else:
        min_date = pd.Timestamp("2023-02-01")
        max_date = pd.Timestamp("2025-06-01")
    
    print(f"집계 기간: {min_date} ~ {max_date}")
    
    months = pd.date_range(
        min_date.date().replace(day=1), 
        max_date.date().replace(day=1), 
        freq="MS"
    )
    
    print(f"집계 월 수: {len(months)}개")
    print(f"월별 기간: {months[0]} ~ {months[-1]}")
    
    # 입력 데이터 샘플 확인
    print("\n입력 데이터 샘플 (처음 5행):")
    sample_cols = WAREHOUSE_LIST + ["Inbound_Date", "Outbound_Date", "Pkg", "SQM"]
    available_cols = [col for col in sample_cols if col in df.columns]
    print(df[available_cols].head())
    
    # 창고별 데이터 존재 여부 확인
    print("\n창고별 데이터 존재 여부:")
    for wh in WAREHOUSE_LIST:
        if wh in df.columns:
            notna_count = df[wh].notna().sum()
            print(f"{wh}: {notna_count}건")
        else:
            print(f"{wh}: 컬럼 없음")

def main():
    """메인 디버깅 실행"""
    print("🔍 HVDC Warehouse Data Debugging 시작")
    
    # 데이터 로드
    df = load_and_debug_data()
    if df is None:
        return
    
    # 1차 점검: 원본 데이터
    debug_step1_original_data(df)
    
    # 2차 점검: 정규화 후
    df, WAREHOUSE_LIST = debug_step2_after_normalization(df)
    
    # 3차 점검: 집계 입력값
    debug_step3_calc_input(df, WAREHOUSE_LIST)
    
    print("\n" + "="*60)
    print("디버깅 완료")
    print("="*60)

if __name__ == "__main__":
    main() 