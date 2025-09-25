#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC 프로젝트 올바른 입고/출고 계산 분석
실제 데이터 기반 정확한 물류 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
from collections import defaultdict

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class CorrectHVDCCalculator:
    """올바른 HVDC 계산 클래스"""

    def __init__(self):
        self.data_file = project_root / "HVDC_complete_data_original.xlsx"
        self.df = None
        self.analysis_results = {}

        # 실제 HVDC 프로젝트 창고 컬럼 (정확한 매핑)
        self.warehouse_columns = [
            "DHL Warehouse",
            "DSV Indoor",
            "DSV Al Markaz",
            "DSV Outdoor",
            "AAA  Storage",
            "Hauler Indoor",
            "DSV MZP",
        ]

        # 실제 현장 컬럼
        self.site_columns = ["MOSB", "MIR", "SHU", "DAS", "AGI"]

    def load_real_data(self):
        """실제 HVDC 데이터 로드"""
        print("📊 실제 HVDC 데이터 로드 중...")

        try:
            # Excel 파일 읽기
            self.df = pd.read_excel(self.data_file, sheet_name=0)
            print(f"✅ 데이터 로드 완료: {len(self.df):,}건")

            # 기본 정보 출력
            print(f"📋 컬럼 수: {len(self.df.columns)}")
            print(f"🔍 주요 컬럼: {list(self.df.columns[:10])}")

            # 실제 창고 컬럼 확인
            actual_warehouse_cols = [
                col for col in self.warehouse_columns if col in self.df.columns
            ]
            print(f"🏭 발견된 창고 컬럼: {actual_warehouse_cols}")

            # 실제 현장 컬럼 확인
            actual_site_cols = [
                col for col in self.site_columns if col in self.df.columns
            ]
            print(f"🏗️  발견된 현장 컬럼: {actual_site_cols}")

            return True

        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False

    def calculate_correct_inbound(self):
        """올바른 입고 계산"""
        print("\n📥 올바른 입고 계산 중...")

        inbound_data = []
        total_inbound = 0
        by_warehouse = defaultdict(int)
        by_month = defaultdict(int)

        for idx, row in self.df.iterrows():
            for warehouse in self.warehouse_columns:
                if warehouse in row.index and pd.notna(row[warehouse]):
                    try:
                        warehouse_date = pd.to_datetime(row[warehouse], errors="coerce")
                        if pd.notna(warehouse_date):
                            # PKG 수량 추출 (있는 경우)
                            pkg_quantity = self._get_pkg_quantity(row)

                            inbound_data.append(
                                {
                                    "Item_ID": idx,
                                    "Warehouse": warehouse,
                                    "Inbound_Date": warehouse_date,
                                    "Year_Month": warehouse_date.strftime("%Y-%m"),
                                    "PKG_Quantity": pkg_quantity,
                                }
                            )
                            total_inbound += pkg_quantity
                            by_warehouse[warehouse] += pkg_quantity
                            by_month[warehouse_date.strftime("%Y-%m")] += pkg_quantity
                    except Exception as e:
                        print(f"⚠️  입고 계산 오류 (행 {idx}, 창고 {warehouse}): {e}")
                        continue

        result = {
            "total_inbound": total_inbound,
            "by_warehouse": dict(by_warehouse),
            "by_month": dict(by_month),
            "inbound_items": inbound_data,
        }

        print(f"✅ 입고 계산 완료: {total_inbound:,}건")
        print(f"🏭 창고별 입고: {dict(by_warehouse)}")

        return result

    def calculate_correct_outbound(self):
        """올바른 출고 계산 (이벤트 타임라인 방식)"""
        print("\n📤 올바른 출고 계산 중...")

        if not self.warehouse_columns or not self.site_columns:
            print("⚠️  창고 또는 현장 컬럼을 찾을 수 없음")
            return {"total_outbound": 0, "by_warehouse": {}, "by_site": {}}

        # 실제 존재하는 컬럼만 필터링
        existing_warehouse_cols = [
            col for col in self.warehouse_columns if col in self.df.columns
        ]
        existing_site_cols = [
            col for col in self.site_columns if col in self.df.columns
        ]

        if not existing_warehouse_cols or not existing_site_cols:
            print("⚠️  창고 또는 현장 컬럼을 찾을 수 없음")
            return {"total_outbound": 0, "by_warehouse": {}, "by_site": {}}

        # 모든 날짜 컬럼 melt
        all_location_cols = existing_warehouse_cols + existing_site_cols
        id_col = self.df.columns[0]  # 첫 번째 컬럼을 ID로 사용

        long_df = self.df.melt(
            id_vars=[id_col],
            value_vars=all_location_cols,
            var_name="Location",
            value_name="Date",
        ).dropna()

        # 날짜형 변환 및 정렬
        long_df["Date"] = pd.to_datetime(long_df["Date"], errors="coerce")
        long_df = long_df.dropna(subset=["Date"])
        long_df = long_df.sort_values([id_col, "Date"])

        # 이전 Location 대비 변화 시 출고 이벤트 마킹
        long_df["Prev_Location"] = long_df.groupby(id_col)["Location"].shift()

        # 창고 → 현장 이동만 출고로 계산
        outbound_events = long_df[
            long_df["Prev_Location"].isin(existing_warehouse_cols)
            & long_df["Location"].isin(existing_site_cols)
        ]

        # PKG 수량 반영
        outbound_with_pkg = []
        for _, event in outbound_events.iterrows():
            item_id = event[id_col]
            original_row = self.df.iloc[item_id] if item_id < len(self.df) else None

            if original_row is not None:
                pkg_quantity = self._get_pkg_quantity(original_row)
                outbound_with_pkg.append(
                    {
                        "Item_ID": item_id,
                        "From_Warehouse": event["Prev_Location"],
                        "To_Site": event["Location"],
                        "Outbound_Date": event["Date"],
                        "PKG_Quantity": pkg_quantity,
                    }
                )

        # 집계
        by_warehouse = defaultdict(int)
        by_site = defaultdict(int)

        for event in outbound_with_pkg:
            by_warehouse[event["From_Warehouse"]] += event["PKG_Quantity"]
            by_site[event["To_Site"]] += event["PKG_Quantity"]

        total_outbound = sum(event["PKG_Quantity"] for event in outbound_with_pkg)

        result = {
            "total_outbound": total_outbound,
            "by_warehouse": dict(by_warehouse),
            "by_site": dict(by_site),
            "outbound_events": outbound_with_pkg,
        }

        print(f"✅ 출고 계산 완료: {total_outbound:,}건")
        print(f"🏭 창고별 출고: {dict(by_warehouse)}")
        print(f"🏗️  현장별 출고: {dict(by_site)}")

        return result

    def calculate_correct_inventory(self):
        """올바른 재고 계산 (Status_Location 기반)"""
        print("\n📦 올바른 재고 계산 중...")

        warehouse_items = []
        by_warehouse = defaultdict(int)

        for idx, row in self.df.iterrows():
            # Status_Location 컬럼 확인
            if "Status_Location" in row.index and pd.notna(row["Status_Location"]):
                status_location = str(row["Status_Location"]).strip()

                # 창고에 있는 항목들
                if any(
                    wh.lower() in status_location.lower()
                    for wh in self.warehouse_columns
                ):
                    pkg_quantity = self._get_pkg_quantity(row)

                    warehouse_items.append(
                        {
                            "Item_ID": idx,
                            "Warehouse": status_location,
                            "Status": "warehouse",
                            "PKG_Quantity": pkg_quantity,
                        }
                    )
                    by_warehouse[status_location] += pkg_quantity

        total_inventory = sum(item["PKG_Quantity"] for item in warehouse_items)

        result = {
            "total_inventory": total_inventory,
            "by_warehouse": dict(by_warehouse),
            "warehouse_items": warehouse_items,
        }

        print(f"✅ 재고 계산 완료: {total_inventory:,}건")
        print(f"🏭 창고별 재고: {dict(by_warehouse)}")

        return result

    def calculate_correct_site_inbound(self):
        """올바른 현장 입고 계산"""
        print("\n🏗️  올바른 현장 입고 계산 중...")

        site_inbound_items = []
        by_site = defaultdict(int)
        by_month = defaultdict(int)

        for idx, row in self.df.iterrows():
            for site in self.site_columns:
                if site in row.index and pd.notna(row[site]):
                    try:
                        site_date = pd.to_datetime(row[site], errors="coerce")
                        if pd.notna(site_date):
                            pkg_quantity = self._get_pkg_quantity(row)

                            site_inbound_items.append(
                                {
                                    "Item_ID": idx,
                                    "Site": site,
                                    "Date": site_date,
                                    "Year_Month": site_date.strftime("%Y-%m"),
                                    "PKG_Quantity": pkg_quantity,
                                }
                            )
                            by_site[site] += pkg_quantity
                            by_month[site_date.strftime("%Y-%m")] += pkg_quantity
                    except Exception as e:
                        print(f"⚠️  현장 입고 계산 오류 (행 {idx}, 현장 {site}): {e}")
                        continue

        total_site_inbound = sum(item["PKG_Quantity"] for item in site_inbound_items)

        result = {
            "total_site_inbound": total_site_inbound,
            "by_site": dict(by_site),
            "by_month": dict(by_month),
            "site_items": site_inbound_items,
        }

        print(f"✅ 현장 입고 계산 완료: {total_site_inbound:,}건")
        print(f"🏗️  현장별 입고: {dict(by_site)}")

        return result

    def calculate_correct_direct_delivery(self):
        """올바른 직배송 계산"""
        print("\n🚚 올바른 직배송 계산 중...")

        direct_items = []
        by_site = defaultdict(int)
        by_month = defaultdict(int)

        for idx, row in self.df.iterrows():
            # 현장에 있는 항목들 확인
            if "Status_Location" in row.index and pd.notna(row["Status_Location"]):
                status_location = str(row["Status_Location"]).strip()

                # 현장에 있는 항목
                if any(
                    site.lower() in status_location.lower()
                    for site in self.site_columns
                ):
                    # 모든 창고 컬럼에 날짜가 없는지 확인
                    has_warehouse_date = False
                    for warehouse in self.warehouse_columns:
                        if warehouse in row.index and pd.notna(row[warehouse]):
                            has_warehouse_date = True
                            break

                    # 창고를 거치지 않고 바로 현장으로 간 경우
                    if not has_warehouse_date:
                        # 현장 도착 날짜 찾기
                        site_date = None
                        for site in self.site_columns:
                            if site in row.index and pd.notna(row[site]):
                                site_date = pd.to_datetime(row[site], errors="coerce")
                                if pd.notna(site_date):
                                    break

                        if site_date:
                            pkg_quantity = self._get_pkg_quantity(row)

                            direct_items.append(
                                {
                                    "Item_ID": idx,
                                    "Site": status_location,
                                    "Date": site_date,
                                    "Year_Month": site_date.strftime("%Y-%m"),
                                    "PKG_Quantity": pkg_quantity,
                                }
                            )
                            by_site[status_location] += pkg_quantity
                            by_month[site_date.strftime("%Y-%m")] += pkg_quantity

        total_direct = sum(item["PKG_Quantity"] for item in direct_items)

        result = {
            "total_direct": total_direct,
            "by_site": dict(by_site),
            "by_month": dict(by_month),
            "direct_items": direct_items,
        }

        print(f"✅ 직배송 계산 완료: {total_direct:,}건")
        print(f"🏗️  현장별 직배송: {dict(by_site)}")

        return result

    def _get_pkg_quantity(self, row):
        """PKG 수량 안전 추출"""
        # PKG 관련 컬럼들 확인
        pkg_columns = ["Pkg", "PKG", "Quantity", "Qty", "Amount"]

        for col in pkg_columns:
            if col in row.index and pd.notna(row[col]):
                try:
                    pkg_value = row[col]
                    if isinstance(pkg_value, (int, float)) and pkg_value > 0:
                        return int(pkg_value)
                    elif isinstance(pkg_value, str):
                        # 숫자만 추출
                        import re

                        numbers = re.findall(r"\d+", pkg_value)
                        if numbers:
                            return int(numbers[0])
                except:
                    continue

        # 기본값 1 반환
        return 1

    def generate_monthly_pivot(self):
        """월별 피벗 테이블 생성"""
        print("\n📊 월별 피벗 테이블 생성 중...")

        # 입고 데이터로 피벗 생성
        inbound_result = self.analysis_results.get("inbound", {})
        inbound_items = inbound_result.get("inbound_items", [])

        if not inbound_items:
            print("⚠️  입고 데이터가 없어 피벗 생성 불가")
            return None

        # DataFrame 생성
        inbound_df = pd.DataFrame(inbound_items)

        # 피벗 테이블 생성
        pivot_df = inbound_df.pivot_table(
            index="Year_Month",
            columns="Warehouse",
            values="PKG_Quantity",
            aggfunc="sum",
            fill_value=0,
        )

        print("✅ 월별 피벗 테이블 생성 완료")
        print(pivot_df.head())

        return pivot_df

    def run_correct_analysis(self):
        """올바른 전체 분석 실행"""
        print("🚀 HVDC 올바른 데이터 분석 시작")
        print("=" * 60)

        # 1. 데이터 로드
        if not self.load_real_data():
            return False

        # 2. 각종 계산 수행 (PKG 수량 반영)
        self.analysis_results["inbound"] = self.calculate_correct_inbound()
        self.analysis_results["outbound"] = self.calculate_correct_outbound()
        self.analysis_results["inventory"] = self.calculate_correct_inventory()
        self.analysis_results["site_inbound"] = self.calculate_correct_site_inbound()
        self.analysis_results["direct_delivery"] = (
            self.calculate_correct_direct_delivery()
        )

        # 3. 월별 피벗 생성
        pivot_df = self.generate_monthly_pivot()
        if pivot_df is not None:
            self.analysis_results["monthly_pivot"] = pivot_df

        # 4. 결과 출력
        self.print_correct_summary()

        # 5. 결과 내보내기
        output_file = self.export_correct_results()

        if output_file:
            print(f"\n✅ 올바른 분석 완료! 결과 파일: {output_file}")
        else:
            print("\n⚠️  결과 내보내기 실패")

        return True

    def print_correct_summary(self):
        """올바른 분석 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 HVDC 올바른 데이터 분석 결과 요약")
        print("=" * 60)

        print(f"📊 총 데이터 건수: {len(self.df):,}건")

        if "inbound" in self.analysis_results:
            inbound = self.analysis_results["inbound"]
            print(f"\n📥 입고 분석 (PKG 수량 반영):")
            print(f"  총 입고: {inbound.get('total_inbound', 0):,}건")
            print(f"  창고별 입고: {inbound.get('by_warehouse', {})}")

        if "outbound" in self.analysis_results:
            outbound = self.analysis_results["outbound"]
            print(f"\n📤 출고 분석 (PKG 수량 반영):")
            print(f"  총 출고: {outbound.get('total_outbound', 0):,}건")
            print(f"  창고별 출고: {outbound.get('by_warehouse', {})}")
            print(f"  현장별 출고: {outbound.get('by_site', {})}")

        if "inventory" in self.analysis_results:
            inventory = self.analysis_results["inventory"]
            print(f"\n📦 재고 분석 (PKG 수량 반영):")
            print(f"  총 재고: {inventory.get('total_inventory', 0):,}건")
            print(f"  창고별 재고: {inventory.get('by_warehouse', {})}")

        if "site_inbound" in self.analysis_results:
            site_inbound = self.analysis_results["site_inbound"]
            print(f"\n🏗️  현장 입고 분석 (PKG 수량 반영):")
            print(f"  총 현장 입고: {site_inbound.get('total_site_inbound', 0):,}건")
            print(f"  현장별 입고: {site_inbound.get('by_site', {})}")

        if "direct_delivery" in self.analysis_results:
            direct = self.analysis_results["direct_delivery"]
            print(f"\n🚚 직배송 분석 (PKG 수량 반영):")
            print(f"  총 직배송: {direct.get('total_direct', 0):,}건")
            print(f"  현장별 직배송: {direct.get('by_site', {})}")

        print("\n" + "=" * 60)

    def export_correct_results(self):
        """올바른 분석 결과 내보내기"""
        print("\n💾 올바른 분석 결과 내보내기 중...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = project_root / f"correct_hvdc_analysis_{timestamp}.xlsx"

        try:
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                # 원본 데이터
                self.df.to_excel(writer, sheet_name="원본데이터", index=False)

                # 분석 결과 요약
                summary_data = []
                for key, value in self.analysis_results.items():
                    if key == "monthly_pivot":
                        continue
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key not in [
                                "inbound_items",
                                "site_items",
                                "direct_items",
                                "warehouse_items",
                                "outbound_events",
                            ]:
                                summary_data.append(
                                    {"분석항목": f"{key}_{sub_key}", "값": sub_value}
                                )
                    else:
                        summary_data.append({"분석항목": key, "값": value})

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="분석결과", index=False)

                # 월별 피벗 테이블
                if "monthly_pivot" in self.analysis_results:
                    self.analysis_results["monthly_pivot"].to_excel(
                        writer, sheet_name="월별입고피벗"
                    )

                # 입고 상세 데이터
                if (
                    "inbound" in self.analysis_results
                    and "inbound_items" in self.analysis_results["inbound"]
                ):
                    inbound_df = pd.DataFrame(
                        self.analysis_results["inbound"]["inbound_items"]
                    )
                    inbound_df.to_excel(writer, sheet_name="입고상세", index=False)

                # 출고 상세 데이터
                if (
                    "outbound" in self.analysis_results
                    and "outbound_events" in self.analysis_results["outbound"]
                ):
                    outbound_df = pd.DataFrame(
                        self.analysis_results["outbound"]["outbound_events"]
                    )
                    outbound_df.to_excel(writer, sheet_name="출고상세", index=False)

            print(f"✅ 올바른 분석 결과 저장 완료: {output_file}")
            return str(output_file)

        except Exception as e:
            print(f"❌ 결과 내보내기 실패: {e}")
            return None


def main():
    """메인 실행 함수"""
    calculator = CorrectHVDCCalculator()
    success = calculator.run_correct_analysis()

    if success:
        print("\n🔧 **추천 명령어:**")
        print("/logi_master analyze_correct_data [올바른 데이터 분석 - PKG 수량 반영]")
        print("/switch_mode LATTICE [창고 최적화 모드 - 정확한 입출고 로직]")
        print(
            "/validate_data warehouse_operations [창고 운영 데이터 검증 - 정확도 확인]"
        )
        print("/automate test-pipeline [전체 테스트 파이프라인 실행 - 시스템 검증]")
    else:
        print("\n❌ 분석 실패")


if __name__ == "__main__":
    main()
