# ---------------------------------------------------------------------------
# 📦 PATCH v2.9.8 – Warehouse Column Normalization & Dynamic List Fix
#   * 모든 창고 컬럼명을 단일 공백 표기로 통합 → _calc_monthly_records() 의 0 집계 해결
#   * WAREHOUSE_LIST 를 **데이터에 실제 존재하는 표준명**으로 동적 생성
# ---------------------------------------------------------------------------

import pandas as pd
import re
from typing import List

# ---------------------------------------------------------------------------
# 1. 표준 창고명 & Alias 매핑
# ---------------------------------------------------------------------------
STANDARD_WAREHOUSES: List[str] = [
    "AAA  Storage",    # 표준은 이중 공백(   )
    "DSV Al Markaz",
    "DSV Indoor",
    "DSV MZP",
    "DSV Outdoor",
    "Hauler Indoor",
    "MOSB",
]

WAREHOUSE_ALIASES = {
    # AAA Storage
    r"^AAA\s+Storage$": "AAA  Storage",   # 단/다중 공백 모두 표준화
    # DSV Al Markaz
    r"^DSV\s+Al\s+Markaz$": "DSV Al Markaz",
    r"^Dsv\s+Al\s+Markaz$": "DSV Al Markaz",
    r"^DSV\s+AL\s+MARKAZ$": "DSV Al Markaz",
    # DSV Indoor
    r"^DSV\s+Indoor$": "DSV Indoor",
    r"^Dsv\s+Indoor$": "DSV Indoor",
    # 기타 (필요 시 추가)
}


def unify_warehouse_columns(df: pd.DataFrame) -> pd.DataFrame:
    """창고 컬럼명의 공백·대소문자·Alias 를 표준화한다."""

    df = df.copy()

    # 1) 다중 공백 → 단일 공백, 양끝 공백 제거
    df.columns = df.columns.str.replace(r"\s+", " ", regex=True).str.strip()

    # 2) 정규표현식 기반 Alias 매핑
    col_map = {}
    for col in df.columns:
        for pattern, std_name in WAREHOUSE_ALIASES.items():
            if re.match(pattern, col, flags=re.IGNORECASE):
                col_map[col] = std_name
                break
    if col_map:
        df.rename(columns=col_map, inplace=True)

    return df


# ---------------------------------------------------------------------------
# 2. 동적 WAREHOUSE_LIST 생성 헬퍼
# ---------------------------------------------------------------------------

def get_active_warehouse_list(df: pd.DataFrame) -> List[str]:
    """df 에 실제 존재하는 표준 창고 컬럼만 반환"""
    return [wh for wh in STANDARD_WAREHOUSES if wh in df.columns]


# ---------------------------------------------------------------------------
# 3. create_warehouse_monthly_sheet() 패치 예시
# ---------------------------------------------------------------------------
#   기존 코드에서 ↓ 부분만 교체하면 됩니다.
#
#   df  = unify_warehouse_columns(df)
#   WAREHOUSE_LIST = get_active_warehouse_list(df)
#   warehouse_monthly = _calc_monthly_records(df, months, WAREHOUSE_LIST)
# ---------------------------------------------------------------------------

# (아래는 통합 테스트용 예제 Stub – 실제 프로젝트에서는 기존 함수 내부에 삽입)
if __name__ == "__main__":
    # 간단한 Demo
    raw = pd.DataFrame({
        "AAA Storage": ["2024-01-15"],
        "DSV Al  Markaz": ["2024-02-10"],  # 이중 공백
        "Pkg": [10],
        "SQM": [20],
    })
    print("\n[BEFORE] columns :", list(raw.columns))

    norm = unify_warehouse_columns(raw)
    print("[AFTER ] columns :", list(norm.columns))

    active_list = get_active_warehouse_list(norm)
    print("Active WAREHOUSE_LIST →", active_list) 