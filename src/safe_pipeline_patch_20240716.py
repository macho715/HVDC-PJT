import pandas as pd
import numpy as np

# 1. Robust 날짜 변환(중복키/이상 방지)
def safe_to_datetime(series: pd.Series) -> pd.Series:
    s = series.copy()
    s.name = None
    return pd.to_datetime(s, errors="coerce")

# 2. 컬럼 표준화 + 중복/매핑 진단
def normalize_and_debug_columns(df: pd.DataFrame, standard_cols: list) -> pd.DataFrame:
    col_map = {}
    for std in standard_cols:
        for col in df.columns:
            if col.strip().lower().replace(" ", "") == std.lower().replace(" ", ""):
                col_map[col] = std
    df = df.rename(columns=col_map)
    print("컬럼 매핑 결과:", col_map)
    dups = df.columns[df.columns.duplicated()]
    if len(dups) > 0:
        print("⚠️ 중복 컬럼:", list(dups))
    return df.loc[:, ~df.columns.duplicated()]

# 3. 집계/누계 컬럼 자동 동기화(없으면 0으로 보장)
def ensure_totals(df: pd.DataFrame, totals: list) -> pd.DataFrame:
    for col in totals:
        if col not in df.columns:
            df[col] = 0
    return df

# 4. 전체 파이프라인 자동화 예시
def run_full_pipeline(raw_df: pd.DataFrame):
    # 표준 창고 컬럼명(실제 프로젝트용 리스트로 교체)
    WAREHOUSE_LIST = [
        "AAA  Storage", "AAA Storage", "DSV Al Markaz", "DSV Indoor", "DSV MZP", "DSV MZD", "DSV Outdoor", "Hauler Indoor", "MOSB"
    ]
    SITE_LIST = ["AGI", "DAS", "MIR", "SHU"]

    # 1. 컬럼 표준화 및 중복 제거/진단
    df = normalize_and_debug_columns(raw_df, WAREHOUSE_LIST + SITE_LIST)

    # 2. 날짜 컬럼 robust 변환 (safe_to_datetime만 사용)
    for col in WAREHOUSE_LIST + SITE_LIST:
        if col in df.columns:
            df[col] = safe_to_datetime(df[col])
    # 기타 날짜형 컬럼도 동일하게 적용(예시)
    for date_col in ["Inbound_Date", "Outbound_Date", "Status_Location_Date"]:
        if date_col in df.columns:
            df[date_col] = safe_to_datetime(df[date_col])

    # 3. 집계/누계/월별 표 생성 (예: _calc_monthly_records 등 직접 호출)
    # 여기는 프로젝트 실제 집계 함수 호출로 치환
    # result_df = _calc_monthly_records(df, months, WAREHOUSE_LIST)
    # 아래는 예시 누계 자동 생성
    # result_df = ensure_totals(result_df, ["누계_입고", "누계_출고", "누계_재고", "누계_재고_sqm"])

    # 예시로 현재 데이터프레임의 컬럼명과 notna 개수 진단
    print("최종 집계표 컬럼:", list(df.columns))
    for col in WAREHOUSE_LIST:
        if col in df.columns:
            print(f"{col} notna: {df[col].notna().sum()}")
    return df

# 실제 파일/데이터로 일괄 적용 실행 예시
if __name__ == "__main__":
    # 원본 데이터 예시: pd.read_excel, pd.read_csv 등
    # df = pd.read_excel('yourfile.xlsx')
    # 아래는 빈 예시
    df = pd.DataFrame({
        "AAA  Storage": ["2024-01-01", np.nan, "2024-02-05"],
        "DSV Indoor": [np.nan, "2024-03-15", "2024-03-20"],
        "AGI": ["2024-04-01", np.nan, np.nan],
    })
    # 전체 자동화 파이프라인 실행
    out_df = run_full_pipeline(df) 