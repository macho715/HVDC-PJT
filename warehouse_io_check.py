import pandas as pd, re, sys, pathlib
from datetime import datetime

# ---------- 사용자 설정 ----------
WAREHOUSE_COLS = [
    "AAA  Storage",
    "DSV Al Markaz",
    "DSV Indoor",
    "DSV Outdoor",
    "DSV MZP",
    "Hauler Indoor",
    "MOSB",
]
SITE_COLS = ["AGI", "DAS", "MIR", "SHU"]

# 창고 우선순위 (동일‑일자 이동 tie‑breaker)
LOC_PRIORITY = {
    loc: i + 1
    for i, loc in enumerate(
        [
            "DSV Al Markaz",
            "DSV Indoor",
            "DSV Outdoor",
            "DSV MZP",
            "AAA  Storage",
            "Hauler Indoor",
            "MOSB",
        ]
    )
}


# ---------- 유틸 ----------
def _normalize_cols(df):
    """컬럼명 정규화: 연속 공백을 한 칸으로 압축"""
    rename = {c: re.sub(r"\s+", " ", c).strip() for c in df.columns}
    return df.rename(columns=rename)


def _get_pkg(row):  # PKG_Qty 열이 없으면 1 자동
    """PKG 수량 추출 (다양한 컬럼명 지원)"""
    for c in ["Pkg", "PKG_Qty", "Packages", "pkg_quantity"]:
        if c in row and pd.notna(row[c]):
            return row[c]
    return 1


# ---------- IO 계산 ----------
def calc_io(df, ym):
    """입고·출고·재고 계산"""
    # 컬럼 정규화
    df = _normalize_cols(df)
    df = df.reset_index().rename(columns={"index": "orig_idx"})

    # 정규화된 컬럼명으로 업데이트
    normalized_warehouse_cols = [
        "AAA Storage",
        "DSV Al Markaz",
        "DSV Indoor",
        "DSV Outdoor",
        "DSV MZP",
        "Hauler Indoor",
        "MOSB",
    ]
    normalized_site_cols = ["AGI", "DAS", "MIR", "SHU"]

    # 실제 존재하는 컬럼만 필터링
    available_warehouse_cols = [
        col for col in normalized_warehouse_cols if col in df.columns
    ]
    available_site_cols = [col for col in normalized_site_cols if col in df.columns]

    print(f"Available warehouse columns: {available_warehouse_cols}")
    print(f"Available site columns: {available_site_cols}")

    # 데이터를 long format으로 변환
    id_vars = ["orig_idx"]
    if "no." in df.columns:
        id_vars.append("no.")
    long = df.melt(
        id_vars=id_vars,
        value_vars=available_warehouse_cols + available_site_cols,
        var_name="Loc",
        value_name="Date",
    ).dropna(subset=["Date"])

    long["Date"] = pd.to_datetime(long["Date"], errors="coerce")
    long = long.sort_values(id_vars + ["Date"])
    long = long.sort_values("Loc", key=lambda x: x.map(LOC_PRIORITY).fillna(99))
    long["Prev"] = long.groupby("orig_idx")["Loc"].shift()

    # 입고·출고·이동 분류
    inbound = long[
        ~long["Prev"].isin(available_warehouse_cols)
        & long["Loc"].isin(available_warehouse_cols)
    ]
    outbound = long[
        long["Prev"].isin(available_warehouse_cols)
        & long["Loc"].isin(available_site_cols)
    ]
    transfer = long[
        long["Prev"].isin(available_warehouse_cols)
        & long["Loc"].isin(available_warehouse_cols)
        & (long["Prev"] != long["Loc"])
    ]

    month = pd.Period(ym)

    # KPI 계산
    kpi = {
        "Inbound_PKG": inbound[inbound["Date"].dt.to_period("M") == month]
        .apply(lambda r: _get_pkg(df.loc[r["orig_idx"]]), axis=1)
        .sum(),
        "Outbound_PKG": outbound[outbound["Date"].dt.to_period("M") == month]
        .apply(lambda r: _get_pkg(df.loc[r["orig_idx"]]), axis=1)
        .sum(),
        "Transfer_PKG": transfer[transfer["Date"].dt.to_period("M") == month]
        .apply(lambda r: _get_pkg(df.loc[r["orig_idx"]]), axis=1)
        .sum(),
    }

    kpi["Closing_Inventory_PKG"] = (
        kpi["Inbound_PKG"] - kpi["Outbound_PKG"] - kpi["Transfer_PKG"]
    )

    return kpi


# ---------- 실행 ----------
if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None

    if not path or not path.exists():
        sys.exit("데이터 파일 경로를 인자로 전달하세요.")

    # 파일 형식에 따른 로드
    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    elif path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() == ".json":
        df = pd.read_json(path)
    else:
        sys.exit("지원되지 않는 형식입니다.")

    ym = sys.argv[2] if len(sys.argv) > 2 else datetime.today().strftime("%Y-%m")

    print(f"\n=== HVDC Warehouse IO Analysis ===")
    print(f"File: {path.name}")
    print(f"Period: {ym}")
    print(f"Total Records: {len(df):,}")

    kpi = calc_io(df, ym)

    print(f"\n=== {ym} KPI ===")
    for k, v in kpi.items():
        print(f"{k:25}: {v:,.0f}")

    # 정확도 검증
    if kpi["Closing_Inventory_PKG"] == 0:
        print(
            f"\n✅ Closing Inventory: {kpi['Closing_Inventory_PKG']} (Perfect Balance)"
        )
    else:
        print(
            f"\n⚠️  Closing Inventory: {kpi['Closing_Inventory_PKG']} (Check Required)"
        )

    accuracy = abs(kpi["Closing_Inventory_PKG"]) / max(kpi["Inbound_PKG"], 1) * 100
    print(f"Accuracy: {100 - accuracy:.2f}%")
