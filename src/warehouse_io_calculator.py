import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from status_calculator import StatusCalculator


class WarehouseIOCalculator:
    """
    Excel 수식 기반 창고 입출고 계산 클래스

    StatusCalculator를 활용하여 정확한 창고 입출고 집계 수행
    - 입고: warehouse 상태인 항목들의 월별 집계
    - 출고: warehouse → site 이동 또는 창고 타입별 출고율 적용
    - 재고: 현재 warehouse 상태 유지 항목들
    """

    def __init__(self):
        self.status_calculator = StatusCalculator()

        # 창고 타입별 출고율 설정
        self.outbound_rates = {
            "DSV Indoor": 0.80,  # 일반창고
            "DSV Outdoor": 0.60,  # Offshore
            "DSV Al Markaz": 0.90,  # Central
            "DSV MZP": 0.80,  # 일반창고
            "AAA  Storage": 0.80,  # 일반창고 (공백 주의)
            "AAA Storage": 0.80,  # 일반창고 (공백 없음)
            "Hauler Indoor": 0.80,  # 일반창고
            "MOSB": 0.60,  # Offshore
            "DHL Warehouse": 0.80,  # 일반창고
        }

        # 창고 컬럼명 매핑 (표준화)
        self.warehouse_columns = [
            "DSV Indoor",
            "DSV Outdoor",
            "DSV Al Markaz",
            "DSV MZP",
            "AAA  Storage",
            "AAA Storage",
            "Hauler Indoor",
            "MOSB",
            "DHL Warehouse",
        ]

        # 현장 컬럼명
        self.site_columns = ["MIR", "SHU", "DAS", "AGI"]

        # Final Location 계산을 위한 특별 컬럼 매핑
        self.special_location_columns = {
            "DSV Al Markaz": "Status_Location_DSV Al Markaz",  # AX
            "DSV Indoor": "Status_Location_DSV Indoor",  # AY
        }

    def calculate_final_location(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Final_Location 파생 로직 (np.select 사용)
        - DSV Al Markaz → AX 컬럼 우선 참조
        - DSV Indoor → AY 컬럼 우선 참조
        - 나머지 → Status_Location(AV) 컬럼 사용
        """
        result_df = df.copy()

        # 상태 계산이 안되어 있으면 먼저 계산
        if "Status_Location" not in result_df.columns:
            result_df = self.status_calculator.calculate_complete_status(result_df)

        # 열 매핑 (가정)
        COL_LOC_ALL = "Status_Location"  # AV
        COL_DSV_MARKAZ = "Status_Location_DSV Al Markaz"  # AX
        COL_DSV_INDOOR = "Status_Location_DSV Indoor"  # AY

        # AX, AY 컬럼이 없으면 생성 (임시)
        if COL_DSV_MARKAZ not in result_df.columns:
            result_df[COL_DSV_MARKAZ] = ""
        if COL_DSV_INDOOR not in result_df.columns:
            result_df[COL_DSV_INDOOR] = ""

        # 1) AL MARKAZ → AX, INDOOR → AY, 나머지 → AV
        result_df["Final_Location"] = np.select(
            [
                result_df[COL_DSV_MARKAZ].notna() & result_df[COL_DSV_MARKAZ].ne(""),
                result_df[COL_DSV_INDOOR].notna() & result_df[COL_DSV_INDOOR].ne(""),
            ],
            [
                result_df[COL_DSV_MARKAZ],  # AL MARKAZ
                result_df[COL_DSV_INDOOR],  # INDOOR
            ],
            default=result_df[COL_LOC_ALL],  # 그 외
        )

        # 2) 확인: 중복·공백 제거
        result_df["Final_Location"] = (
            result_df["Final_Location"].astype(str).str.strip()
        )
        result_df.loc[result_df["Final_Location"] == "", "Final_Location"] = "미정"

        return result_df

    def calculate_warehouse_inbound(self, df: pd.DataFrame) -> Dict:
        """
        창고 입고 계산 (Final_Location 기반 + 월별 피벗)
        - Final_Location 기준으로 정확한 위치 파악
        - 월별 입고량 피벗 테이블 생성

        Returns:
            Dict: {
                'total_inbound': int,
                'by_warehouse': Dict[str, int],
                'by_month': Dict[str, int],
                'by_warehouse_month': Dict[str, Dict[str, int]],
                'monthly_pivot': pd.DataFrame,
                'inbound_date_column': str
            }
        """
        # Final_Location 계산
        result_df = self.calculate_final_location(df)

        # warehouse 상태 항목만 필터링
        warehouse_items = result_df[result_df["Status_Current"] == "warehouse"]

        # 입고 날짜 컬럼 찾기 (가능한 후보들)
        inbound_date_candidates = [
            "Inbound_Date",
            "Arrival_Date",
            "Warehouse_In_Date",
            "Entry_Date",
            "Received_Date",
        ]

        inbound_date_col = None
        for col in inbound_date_candidates:
            if col in result_df.columns:
                inbound_date_col = col
                break

        # 입고 날짜가 없으면 Final_Location의 날짜 사용
        if inbound_date_col is None:
            # Final_Location에 해당하는 날짜 컬럼에서 추출
            warehouse_items = warehouse_items.copy()
            warehouse_items["Inbound_Date"] = warehouse_items.apply(
                lambda row: (
                    row.get(row["Final_Location"], None)
                    if row["Final_Location"] in row.index
                    else None
                ),
                axis=1,
            )
            inbound_date_col = "Inbound_Date"

        # 월별 계산을 위한 데이터 준비
        if inbound_date_col in warehouse_items.columns:
            warehouse_items = warehouse_items.copy()
            warehouse_items["Inbound_Month"] = pd.to_datetime(
                warehouse_items[inbound_date_col], errors="coerce"
            ).dt.to_period("M")
        else:
            warehouse_items["Inbound_Month"] = None

        # 집계 결과 초기화
        inbound_summary = {
            "total_inbound": len(warehouse_items),
            "by_warehouse": defaultdict(int),
            "by_month": defaultdict(int),
            "by_warehouse_month": defaultdict(lambda: defaultdict(int)),
            "inbound_date_column": inbound_date_col or "None",
        }

        # 창고별, 월별 집계
        for _, row in warehouse_items.iterrows():
            location = row["Final_Location"]
            month = row["Inbound_Month"]

            # 집계 업데이트
            inbound_summary["by_warehouse"][location] += 1

            if pd.notna(month):
                month_key = str(month)
                inbound_summary["by_month"][month_key] += 1
                inbound_summary["by_warehouse_month"][location][month_key] += 1

        # 월별 피벗 테이블 생성 (방식 1: pivot_table 권장)
        try:
            if inbound_date_col and "Inbound_Month" in warehouse_items.columns:
                monthly_pivot = warehouse_items.pivot_table(
                    index="Inbound_Month",
                    columns="Final_Location",
                    values=(
                        "Item"
                        if "Item" in warehouse_items.columns
                        else warehouse_items.columns[0]
                    ),
                    aggfunc="count",
                    fill_value=0,
                ).astype(int)
            else:
                monthly_pivot = pd.DataFrame()
        except Exception as e:
            print(f"피벗 테이블 생성 실패: {e}")
            monthly_pivot = pd.DataFrame()

        # defaultdict를 일반 dict로 변환
        inbound_summary["by_warehouse"] = dict(inbound_summary["by_warehouse"])
        inbound_summary["by_month"] = dict(inbound_summary["by_month"])
        inbound_summary["by_warehouse_month"] = {
            wh: dict(months)
            for wh, months in inbound_summary["by_warehouse_month"].items()
        }
        inbound_summary["monthly_pivot"] = monthly_pivot

        return inbound_summary

    def calculate_warehouse_outbound(self, df: pd.DataFrame) -> Dict:
        """
        창고 출고 계산 (가이드 문제점 2 해결: 이벤트 타임라인 방식)
        - 출고 이벤트 중복 제거
        - 실제 창고 → 현장 이동 이벤트만 카운트

        Returns:
            Dict: {
                'total_outbound': int,        # 실제 출고 이벤트 수
                'by_warehouse': Dict[str, int],
                'by_site': Dict[str, int]     # 현장별 출고 분포
            }
        """
        # 이벤트 타임라인 방식으로 출고 계산
        warehouse_cols = self.warehouse_columns
        site_cols = self.site_columns

        # 모든 날짜 컬럼 melt
        long_df = df.melt(
            id_vars=["Item"] if "Item" in df.columns else [df.columns[0]],
            value_vars=warehouse_cols + site_cols,
            var_name="Location",
            value_name="Date",
        ).dropna()

        if len(long_df) == 0:
            return {"total_outbound": 0, "by_warehouse": {}, "by_site": {}}

        # 날짜형 변환 및 정렬
        long_df["Date"] = pd.to_datetime(long_df["Date"], errors="coerce")
        long_df = long_df.dropna(subset=["Date"])
        long_df = long_df.sort_values(["Item", "Date"])

        # 이전 Location 대비 변화 시 출고 이벤트 마킹
        long_df["Prev_Location"] = long_df.groupby("Item")["Location"].shift()

        # 창고 → 현장 이동만 출고로 계산
        outbound_events = long_df[
            long_df["Prev_Location"].isin(warehouse_cols)
            & long_df["Location"].isin(site_cols)
        ]

        outbound_summary = {
            "total_outbound": len(outbound_events),
            "by_warehouse": defaultdict(int),
            "by_site": defaultdict(int),
        }

        # 창고별, 현장별 출고 분포
        for _, row in outbound_events.iterrows():
            warehouse = row["Prev_Location"]
            site = row["Location"]
            outbound_summary["by_warehouse"][warehouse] += 1
            outbound_summary["by_site"][site] += 1

        # 가이드 문제점 1 해결: 전역 변수 inbound_data 남용 제거
        # 출고 검증 로직 (지역 변수로 직접 호출)
        inbound_result = self.calculate_warehouse_inbound(df)

        # 출고가 입고보다 큰 경우 경고 및 조정
        if outbound_summary["total_outbound"] > inbound_result["total_inbound"]:
            print(
                f"⚠️  경고: 출고({outbound_summary['total_outbound']})가 입고({inbound_result['total_inbound']})보다 큽니다."
            )
            print(f"   출고를 입고 수준으로 조정합니다.")
            outbound_summary["total_outbound"] = inbound_result["total_inbound"]

        outbound_summary["by_warehouse"] = dict(outbound_summary["by_warehouse"])
        outbound_summary["by_site"] = dict(outbound_summary["by_site"])

        return outbound_summary

    def calculate_direct_delivery(self, df: pd.DataFrame) -> Dict:
        """
        부두→현장 직배송 계산
        - 창고를 거치지 않고 바로 현장으로 간 항목들
        - site 상태이면서 창고 컬럼에 날짜가 없는 경우

        Returns:
            Dict: {
                'total_direct': int,
                'by_site': Dict[str, int],
                'by_month': Dict[str, int],
                'direct_items': pd.DataFrame
            }
        """
        # Final_Location 계산
        result_df = self.calculate_final_location(df)

        # site 상태 항목들
        site_items = result_df[result_df["Status_Current"] == "site"].copy()

        if len(site_items) == 0:
            return {
                "total_direct": 0,
                "by_site": {},
                "by_month": {},
                "direct_items": pd.DataFrame(),
            }

        # 직배송 조건: 모든 창고 컬럼에 날짜가 없고 현장 컬럼에만 날짜가 있는 경우
        direct_mask = pd.Series(True, index=site_items.index)

        # 모든 창고 컬럼 체크 (Pre Arrival 전용 제외하지 않음)
        for col in self.warehouse_columns:
            if col in site_items.columns:
                # 해당 창고 컬럼에 날짜가 있으면 직배송이 아님
                has_warehouse_date = site_items[col].notna()
                direct_mask = direct_mask & ~has_warehouse_date

        # 직배송 항목 필터링
        direct_items = site_items[direct_mask].copy()

        direct_summary = {
            "total_direct": len(direct_items),
            "by_site": defaultdict(int),
            "by_month": defaultdict(int),
            "direct_items": direct_items,
        }

        # 현장별 집계
        if len(direct_items) > 0:
            for _, row in direct_items.iterrows():
                site_location = row["Status_Location"]
                direct_summary["by_site"][site_location] += 1

                # 월별 집계 (현장 도착 날짜 기준)
                site_date = row.get(site_location, None)
                if pd.notna(site_date):
                    try:
                        site_month = pd.to_datetime(site_date).to_period("M")
                        month_key = str(site_month)
                        direct_summary["by_month"][month_key] += 1
                    except:
                        pass

        # defaultdict를 일반 dict로 변환
        direct_summary["by_site"] = dict(direct_summary["by_site"])
        direct_summary["by_month"] = dict(direct_summary["by_month"])

        return direct_summary

    def calculate_warehouse_inventory(self, df: pd.DataFrame) -> Dict:
        """
        창고 재고 계산 (가이드 문제점 4 해결)
        - 현재 warehouse 상태 유지 항목들
        - 5% 소비율 가정치 제거, 실시간 Location 기반 계산

        Returns:
            Dict: {
                'total_inventory': int,
                'by_warehouse': Dict[str, int],
                'by_status': Dict[str, int]
            }
        """
        # 상태 계산
        result_df = self.status_calculator.calculate_complete_status(df)

        # 상태별 집계 (실시간 데이터 기반, 소비율 가정치 없음)
        status_counts = result_df["Status_Current"].value_counts()

        inventory_summary = {
            "total_inventory": status_counts.get("warehouse", 0),
            "by_warehouse": defaultdict(int),
            "by_status": {
                "warehouse": status_counts.get("warehouse", 0),
                "site": status_counts.get("site", 0),
                "pre_arrival": status_counts.get("Pre Arrival", 0),
            },
        }

        # 창고별 재고 집계 (실시간 Status_Location 기반)
        warehouse_items = result_df[result_df["Status_Current"] == "warehouse"]
        for _, row in warehouse_items.iterrows():
            location = row["Status_Location"]
            inventory_summary["by_warehouse"][location] += 1

        inventory_summary["by_warehouse"] = dict(inventory_summary["by_warehouse"])

        # 가이드 문제점 4: 5% 소비율 가정치 제거 완료
        # 기존: consumption = int(cumulative_inventory[site] * 0.05)
        # 수정: 실시간 Status_Current == 'warehouse' 기반 계산

        return inventory_summary

    def calculate_monthly_outbound(self, df: pd.DataFrame) -> Dict:
        """
        월별 출고 계산 (이벤트 타임라인 벡터화 방식)

        가이드 3-1: 출고 이벤트 재계산
        - melt→sort→groupby(Item)로 모든 이동을 시계열 정렬
        - 출고·입고 이벤트 1회만 카운트
        """
        # ① 모든 날짜 컬럼 melt
        warehouse_cols = self.warehouse_columns
        site_cols = self.site_columns

        long_df = df.melt(
            id_vars=["Item"] if "Item" in df.columns else [df.columns[0]],
            value_vars=warehouse_cols + site_cols,
            var_name="Location",
            value_name="Date",
        ).dropna()

        if len(long_df) == 0:
            return {}

        # ② 날짜형 변환 및 정렬
        long_df["Date"] = pd.to_datetime(long_df["Date"], errors="coerce")
        long_df = long_df.dropna(subset=["Date"])
        long_df = long_df.sort_values(["Item", "Date"])

        # ③ 이전 Location 대비 변화 시 출고 이벤트 마킹
        long_df["Prev_Location"] = long_df.groupby("Item")["Location"].shift()
        long_df["Outbound_Flag"] = long_df["Prev_Location"].where(
            long_df["Prev_Location"].isin(warehouse_cols)
            & (long_df["Location"] != long_df["Prev_Location"]),
            np.nan,
        )

        # ④ 월별·창고별 출고 카운트
        outbound_events = long_df.dropna(subset=["Outbound_Flag"])
        if len(outbound_events) == 0:
            return {}

        outbound_events = outbound_events.copy()
        outbound_events["Month"] = outbound_events["Date"].dt.to_period("M")
        monthly_outbound = outbound_events.groupby("Month").size().to_dict()

        # Period를 문자열로 변환
        return {str(month): count for month, count in monthly_outbound.items()}

    def calculate_monthly_site_inbound(self, df: pd.DataFrame) -> Dict:
        """
        월별 현장 입고 계산 (직송 포함)

        가이드 3-2: 직송 포함 - Location이 site인 최초 등장 = site Inbound Event
        """
        site_cols = self.site_columns

        # 모든 현장 컬럼 확인
        site_inbound_items = []

        for _, row in df.iterrows():
            item_id = row.get("Item", row.name)

            for site in site_cols:
                if site in row and pd.notna(row[site]):
                    try:
                        site_date = pd.to_datetime(row[site])
                        site_inbound_items.append(
                            {
                                "Item": item_id,
                                "Site": site,
                                "Date": site_date,
                                "Month": site_date.to_period("M"),
                            }
                        )
                    except:
                        continue

        if len(site_inbound_items) == 0:
            return {}

        # 월별 집계
        site_inbound_df = pd.DataFrame(site_inbound_items)
        monthly_site_inbound = site_inbound_df.groupby("Month").size().to_dict()

        # Period를 문자열로 변환
        return {str(month): count for month, count in monthly_site_inbound.items()}

    def calculate_monthly_warehouse_transfer(self, df: pd.DataFrame) -> Dict:
        """
        월별 창고간 이전 계산

        창고 → 창고 이동 이벤트 계산
        """
        warehouse_cols = self.warehouse_columns

        # 모든 날짜 컬럼 melt
        long_df = df.melt(
            id_vars=["Item"] if "Item" in df.columns else [df.columns[0]],
            value_vars=warehouse_cols,
            var_name="Location",
            value_name="Date",
        ).dropna()

        if len(long_df) == 0:
            return {}

        # 날짜형 변환 및 정렬
        long_df["Date"] = pd.to_datetime(long_df["Date"], errors="coerce")
        long_df = long_df.dropna(subset=["Date"])
        long_df = long_df.sort_values(["Item", "Date"])

        # 이전 Location 확인
        long_df["Prev_Location"] = long_df.groupby("Item")["Location"].shift()

        # 창고 → 창고 이동만 필터링
        warehouse_transfer = long_df[
            long_df["Prev_Location"].isin(warehouse_cols)
            & long_df["Location"].isin(warehouse_cols)
            & (long_df["Location"] != long_df["Prev_Location"])
        ]

        if len(warehouse_transfer) == 0:
            return {}

        # 월별 집계
        warehouse_transfer = warehouse_transfer.copy()
        warehouse_transfer["Month"] = warehouse_transfer["Date"].dt.to_period("M")
        monthly_transfer = warehouse_transfer.groupby("Month").size().to_dict()

        # Period를 문자열로 변환
        return {str(month): count for month, count in monthly_transfer.items()}

    def calculate_site_inbound(self, df: pd.DataFrame) -> Dict:
        """
        현장 입고 계산 (직송 포함)

        가이드 문제점 3 해결: direct_items가 site_inbound에 합산되도록 수정
        """
        # 직송 계산
        direct_delivery = self.calculate_direct_delivery(df)

        # 현장 입고 계산 (창고 경유)
        site_cols = self.site_columns
        site_inbound_items = []

        for _, row in df.iterrows():
            item_id = row.get("Item", row.name)

            for site in site_cols:
                if site in row and pd.notna(row[site]):
                    try:
                        site_date = pd.to_datetime(row[site])
                        site_inbound_items.append(
                            {"Item": item_id, "Site": site, "Date": site_date}
                        )
                    except:
                        continue

        # 직송 + 창고 경유 합산
        total_site_inbound = len(site_inbound_items) + direct_delivery["total_direct"]

        return {
            "total_site_inbound": total_site_inbound,
            "warehouse_routed": len(site_inbound_items),
            "direct_delivery": direct_delivery["total_direct"],
            "direct_items": direct_delivery["direct_items"],
        }

    def recommend_zero_mode(self, accuracy: float) -> Dict:
        """
        Fail-safe 모드 권장 시스템

        가이드 3-4: KPI 실패 시 /switch_mode ZERO로 Safety Lock
        """
        if accuracy < 0.99:
            return {
                "switch_to_zero": True,
                "reason": f"출고-입고 일치율 {accuracy:.3f} < 0.99",
                "recommended_action": "/switch_mode ZERO",
                "alert_channel": "#hvdc-alerts",
            }

        return {
            "switch_to_zero": False,
            "reason": f"출고-입고 일치율 {accuracy:.3f} ≥ 0.99 (정상)",
            "recommended_action": "PRIME/LATTICE 모드 유지",
            "alert_channel": None,
        }

    def generate_monthly_report(self, df: pd.DataFrame) -> Dict:
        """
        월별 입출고 종합 리포트 생성

        Returns:
            Dict: {
                'summary': Dict,
                'monthly_data': Dict[str, Dict],
                'warehouse_performance': Dict
            }
        """
        # 각 계산 수행
        inbound_data = self.calculate_warehouse_inbound(df)
        outbound_data = self.calculate_warehouse_outbound(df)
        inventory_data = self.calculate_warehouse_inventory(df)

        # 월별 데이터 구성
        monthly_data = {}
        all_months = set(inbound_data["by_month"].keys())

        for month in sorted(all_months):
            monthly_data[month] = {
                "inbound": inbound_data["by_month"].get(month, 0),
                "outbound": 0,  # 월별 출고는 별도 계산 필요
                "inventory": 0,  # 월별 재고는 별도 계산 필요
            }

        # 창고별 성과 분석
        warehouse_performance = {}
        for warehouse in inbound_data["by_warehouse"]:
            inbound_count = inbound_data["by_warehouse"][warehouse]
            outbound_count = outbound_data["by_warehouse"].get(warehouse, 0)
            inventory_count = inventory_data["by_warehouse"].get(warehouse, 0)

            outbound_rate = outbound_count / inbound_count if inbound_count > 0 else 0

            warehouse_performance[warehouse] = {
                "inbound": inbound_count,
                "outbound": outbound_count,
                "inventory": inventory_count,
                "outbound_rate": round(outbound_rate, 3),
                "utilization": (
                    round((outbound_count / inbound_count) * 100, 1)
                    if inbound_count > 0
                    else 0
                ),
            }

        return {
            "summary": {
                "total_inbound": inbound_data["total_inbound"],
                "total_outbound": outbound_data["total_outbound"],
                "total_inventory": inventory_data["total_inventory"],
                "active_warehouses": len(inbound_data["by_warehouse"]),
                "data_quality": self._calculate_data_quality(df),
            },
            "monthly_data": monthly_data,
            "warehouse_performance": warehouse_performance,
        }

    def _calculate_data_quality(self, df: pd.DataFrame) -> Dict:
        """
        데이터 품질 평가

        Returns:
            Dict: 데이터 품질 지표
        """
        total_rows = len(df)

        # 날짜 컬럼 유효성 확인
        date_columns = self.warehouse_columns + self.site_columns
        valid_dates = 0

        for col in date_columns:
            if col in df.columns:
                valid_dates += df[col].notna().sum()

        # 중복 제거된 항목 수
        unique_items = df["Item"].nunique() if "Item" in df.columns else total_rows

        return {
            "total_records": total_rows,
            "valid_date_entries": int(valid_dates),
            "unique_items": unique_items,
            "completeness": round(
                (valid_dates / (total_rows * len(date_columns))) * 100, 1
            ),
            "uniqueness": round((unique_items / total_rows) * 100, 1),
        }

    def export_to_excel_format(self, df: pd.DataFrame, output_path: str) -> str:
        """
        Excel 형식으로 결과 출력

        Returns:
            str: 생성된 파일 경로
        """
        # 상태 계산 추가
        result_df = self.status_calculator.calculate_complete_status(df)

        # 월별 리포트 생성
        monthly_report = self.generate_monthly_report(df)

        # Excel 파일 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_path = f"{output_path}_corrected_{timestamp}.xlsx"

        with pd.ExcelWriter(final_path, engine="openpyxl") as writer:
            # 메인 데이터
            result_df.to_excel(writer, sheet_name="Main_Data", index=False)

            # 월별 요약
            monthly_df = pd.DataFrame(monthly_report["monthly_data"]).T
            monthly_df.to_excel(writer, sheet_name="Monthly_Summary", index=True)

            # 창고별 성과
            performance_df = pd.DataFrame(monthly_report["warehouse_performance"]).T
            performance_df.to_excel(
                writer, sheet_name="Warehouse_Performance", index=True
            )

            # 전체 요약
            summary_df = pd.DataFrame([monthly_report["summary"]])
            summary_df.to_excel(writer, sheet_name="Overall_Summary", index=False)

        return final_path
