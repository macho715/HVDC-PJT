#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC 프로젝트 전체 5552건 실제 데이터 입고/출고 계산 분석 (Enhanced)
MACHO-GPT LATTICE 모드 - 창고 최적화 및 물류 분석
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


class EnhancedHVDCAnalyzer:
    """향상된 HVDC 데이터 분석 클래스"""

    def __init__(self):
        self.data_file = project_root / "HVDC_complete_data_original.xlsx"
        self.df = None
        self.analysis_results = {}

        # HVDC 프로젝트 창고 및 현장 컬럼 정의
        self.warehouse_columns = {
            "DSV Al Markaz": "DSV Al Markaz",
            "DSV Indoor": "DSV Indoor",
            "AAA Storage": "AAA Storage",
            "DSV Outdoor": "DSV Outdoor",
        }

        self.site_columns = {"DAS": "DAS", "SAS": "SAS", "PRL": "PRL"}

    def load_complete_data(self):
        """전체 5552건 데이터 로드"""
        print("📊 전체 HVDC 데이터 로드 중...")

        try:
            # Excel 파일 읽기
            self.df = pd.read_excel(self.data_file, sheet_name=0)
            print(f"✅ 데이터 로드 완료: {len(self.df):,}건")

            # 기본 정보 출력
            print(f"📋 컬럼 수: {len(self.df.columns)}")

            # 컬럼명 확인
            print(f"🔍 주요 컬럼: {list(self.df.columns[:10])}")

            # 데이터 타입 확인
            print(f"📊 데이터 타입: {self.df.dtypes.value_counts()}")

            return True

        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False

    def identify_columns(self):
        """컬럼 식별 및 매핑"""
        print("\n🔍 컬럼 식별 중...")

        actual_warehouse_cols = []
        actual_site_cols = []
        date_cols = []

        for col in self.df.columns:
            col_lower = col.lower()

            # 창고 컬럼 식별
            if any(
                wh in col_lower for wh in ["warehouse", "wh", "storage", "dsv", "aaa"]
            ):
                actual_warehouse_cols.append(col)

            # 현장 컬럼 식별
            if any(site in col_lower for site in ["site", "das", "sas", "prl", "현장"]):
                actual_site_cols.append(col)

            # 날짜 컬럼 식별
            if any(
                date_word in col_lower
                for date_word in ["date", "arrival", "inbound", "outbound"]
            ):
                date_cols.append(col)

        print(f"🏭 발견된 창고 컬럼: {actual_warehouse_cols}")
        print(f"🏗️  발견된 현장 컬럼: {actual_site_cols}")
        print(f"📅 발견된 날짜 컬럼: {date_cols}")

        return actual_warehouse_cols, actual_site_cols, date_cols

    def calculate_warehouse_inbound(self):
        """창고 입고 계산"""
        print("\n📥 창고 입고 계산 중...")

        warehouse_cols, _, _ = self.identify_columns()

        inbound_data = []
        total_inbound = 0
        by_warehouse = defaultdict(int)
        by_month = defaultdict(int)

        for idx, row in self.df.iterrows():
            for warehouse in warehouse_cols:
                if warehouse in row.index and pd.notna(row[warehouse]):
                    try:
                        warehouse_date = pd.to_datetime(row[warehouse], errors="coerce")
                        if pd.notna(warehouse_date):
                            inbound_data.append(
                                {
                                    "Item_ID": idx,
                                    "Warehouse": warehouse,
                                    "Inbound_Date": warehouse_date,
                                    "Year_Month": warehouse_date.strftime("%Y-%m"),
                                }
                            )
                            total_inbound += 1
                            by_warehouse[warehouse] += 1
                            by_month[warehouse_date.strftime("%Y-%m")] += 1
                    except:
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

    def calculate_warehouse_outbound(self):
        """창고 출고 계산"""
        print("\n📤 창고 출고 계산 중...")

        warehouse_cols, site_cols, _ = self.identify_columns()

        if not warehouse_cols or not site_cols:
            print("⚠️  창고 또는 현장 컬럼을 찾을 수 없음")
            return {"total_outbound": 0, "by_warehouse": {}, "by_site": {}}

        # 모든 날짜 컬럼 melt
        all_location_cols = warehouse_cols + site_cols
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
            long_df["Prev_Location"].isin(warehouse_cols)
            & long_df["Location"].isin(site_cols)
        ]

        # 집계
        by_warehouse = outbound_events["Prev_Location"].value_counts().to_dict()
        by_site = outbound_events["Location"].value_counts().to_dict()

        result = {
            "total_outbound": len(outbound_events),
            "by_warehouse": by_warehouse,
            "by_site": by_site,
        }

        print(f"✅ 출고 계산 완료: {len(outbound_events):,}건")
        print(f"🏭 창고별 출고: {by_warehouse}")
        print(f"🏗️  현장별 출고: {by_site}")

        return result

    def calculate_warehouse_inventory(self):
        """창고 재고 계산"""
        print("\n📦 창고 재고 계산 중...")

        # 현재 warehouse 상태 유지 항목들 계산
        warehouse_cols, _, _ = self.identify_columns()

        warehouse_items = []
        by_warehouse = defaultdict(int)

        for idx, row in self.df.iterrows():
            # Status_Location 컬럼 확인
            if "Status_Location" in row.index and pd.notna(row["Status_Location"]):
                status_location = str(row["Status_Location"]).strip()

                # 창고에 있는 항목들
                if any(wh.lower() in status_location.lower() for wh in warehouse_cols):
                    warehouse_items.append(
                        {
                            "Item_ID": idx,
                            "Warehouse": status_location,
                            "Status": "warehouse",
                        }
                    )
                    by_warehouse[status_location] += 1

        total_inventory = len(warehouse_items)

        result = {
            "total_inventory": total_inventory,
            "by_warehouse": dict(by_warehouse),
            "warehouse_items": warehouse_items,
        }

        print(f"✅ 재고 계산 완료: {total_inventory:,}건")
        print(f"🏭 창고별 재고: {dict(by_warehouse)}")

        return result

    def calculate_site_inbound(self):
        """현장 입고 계산"""
        print("\n🏗️  현장 입고 계산 중...")

        _, site_cols, _ = self.identify_columns()

        site_inbound_items = []
        by_site = defaultdict(int)
        by_month = defaultdict(int)

        for idx, row in self.df.iterrows():
            for site in site_cols:
                if site in row.index and pd.notna(row[site]):
                    try:
                        site_date = pd.to_datetime(row[site], errors="coerce")
                        if pd.notna(site_date):
                            site_inbound_items.append(
                                {
                                    "Item_ID": idx,
                                    "Site": site,
                                    "Date": site_date,
                                    "Year_Month": site_date.strftime("%Y-%m"),
                                }
                            )
                            by_site[site] += 1
                            by_month[site_date.strftime("%Y-%m")] += 1
                    except:
                        continue

        total_site_inbound = len(site_inbound_items)

        result = {
            "total_site_inbound": total_site_inbound,
            "by_site": dict(by_site),
            "by_month": dict(by_month),
            "site_items": site_inbound_items,
        }

        print(f"✅ 현장 입고 계산 완료: {total_site_inbound:,}건")
        print(f"🏗️  현장별 입고: {dict(by_site)}")

        return result

    def calculate_direct_delivery(self):
        """직배송 계산"""
        print("\n🚚 직배송 계산 중...")

        warehouse_cols, site_cols, _ = self.identify_columns()

        direct_items = []
        by_site = defaultdict(int)
        by_month = defaultdict(int)

        for idx, row in self.df.iterrows():
            # 현장에 있는 항목들 확인
            if "Status_Location" in row.index and pd.notna(row["Status_Location"]):
                status_location = str(row["Status_Location"]).strip()

                # 현장에 있는 항목
                if any(site.lower() in status_location.lower() for site in site_cols):
                    # 모든 창고 컬럼에 날짜가 없는지 확인
                    has_warehouse_date = False
                    for warehouse in warehouse_cols:
                        if warehouse in row.index and pd.notna(row[warehouse]):
                            has_warehouse_date = True
                            break

                    # 창고를 거치지 않고 바로 현장으로 간 경우
                    if not has_warehouse_date:
                        # 현장 도착 날짜 찾기
                        site_date = None
                        for site in site_cols:
                            if site in row.index and pd.notna(row[site]):
                                site_date = pd.to_datetime(row[site], errors="coerce")
                                if pd.notna(site_date):
                                    break

                        if site_date:
                            direct_items.append(
                                {
                                    "Item_ID": idx,
                                    "Site": status_location,
                                    "Date": site_date,
                                    "Year_Month": site_date.strftime("%Y-%m"),
                                }
                            )
                            by_site[status_location] += 1
                            by_month[site_date.strftime("%Y-%m")] += 1

        total_direct = len(direct_items)

        result = {
            "total_direct": total_direct,
            "by_site": dict(by_site),
            "by_month": dict(by_month),
            "direct_items": direct_items,
        }

        print(f"✅ 직배송 계산 완료: {total_direct:,}건")
        print(f"🏗️  현장별 직배송: {dict(by_site)}")

        return result

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
            values="Item_ID",
            aggfunc="count",
            fill_value=0,
        )

        print("✅ 월별 피벗 테이블 생성 완료")
        print(pivot_df.head())

        return pivot_df

    def run_complete_analysis(self):
        """전체 분석 실행"""
        print("🚀 HVDC 전체 데이터 분석 시작")
        print("=" * 60)

        # 1. 데이터 로드
        if not self.load_complete_data():
            return False

        # 2. 컬럼 식별
        self.identify_columns()

        # 3. 각종 계산 수행
        self.analysis_results["inbound"] = self.calculate_warehouse_inbound()
        self.analysis_results["outbound"] = self.calculate_warehouse_outbound()
        self.analysis_results["inventory"] = self.calculate_warehouse_inventory()
        self.analysis_results["site_inbound"] = self.calculate_site_inbound()
        self.analysis_results["direct_delivery"] = self.calculate_direct_delivery()

        # 4. 월별 피벗 생성
        pivot_df = self.generate_monthly_pivot()
        if pivot_df is not None:
            self.analysis_results["monthly_pivot"] = pivot_df

        # 5. 결과 출력
        self.print_summary()

        # 6. 결과 내보내기
        output_file = self.export_analysis_results()

        if output_file:
            print(f"\n✅ 분석 완료! 결과 파일: {output_file}")
        else:
            print("\n⚠️  결과 내보내기 실패")

        return True

    def print_summary(self):
        """분석 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 HVDC 전체 데이터 분석 결과 요약")
        print("=" * 60)

        print(f"📊 총 데이터 건수: {len(self.df):,}건")

        if "inbound" in self.analysis_results:
            inbound = self.analysis_results["inbound"]
            print(f"\n📥 입고 분석:")
            print(f"  총 입고: {inbound.get('total_inbound', 0):,}건")
            print(f"  창고별 입고: {inbound.get('by_warehouse', {})}")

        if "outbound" in self.analysis_results:
            outbound = self.analysis_results["outbound"]
            print(f"\n📤 출고 분석:")
            print(f"  총 출고: {outbound.get('total_outbound', 0):,}건")
            print(f"  창고별 출고: {outbound.get('by_warehouse', {})}")
            print(f"  현장별 출고: {outbound.get('by_site', {})}")

        if "inventory" in self.analysis_results:
            inventory = self.analysis_results["inventory"]
            print(f"\n📦 재고 분석:")
            print(f"  총 재고: {inventory.get('total_inventory', 0):,}건")
            print(f"  창고별 재고: {inventory.get('by_warehouse', {})}")

        if "site_inbound" in self.analysis_results:
            site_inbound = self.analysis_results["site_inbound"]
            print(f"\n🏗️  현장 입고 분석:")
            print(f"  총 현장 입고: {site_inbound.get('total_site_inbound', 0):,}건")
            print(f"  현장별 입고: {site_inbound.get('by_site', {})}")

        if "direct_delivery" in self.analysis_results:
            direct = self.analysis_results["direct_delivery"]
            print(f"\n🚚 직배송 분석:")
            print(f"  총 직배송: {direct.get('total_direct', 0):,}건")
            print(f"  현장별 직배송: {direct.get('by_site', {})}")

        print("\n" + "=" * 60)

    def export_analysis_results(self):
        """분석 결과 내보내기"""
        print("\n💾 분석 결과 내보내기 중...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = project_root / f"enhanced_hvdc_analysis_{timestamp}.xlsx"

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
                if "outbound" in self.analysis_results:
                    outbound_df = pd.DataFrame(self.analysis_results["outbound"])
                    outbound_df.to_excel(writer, sheet_name="출고상세", index=False)

            print(f"✅ 분석 결과 저장 완료: {output_file}")
            return str(output_file)

        except Exception as e:
            print(f"❌ 결과 내보내기 실패: {e}")
            return None


def main():
    """메인 실행 함수"""
    analyzer = EnhancedHVDCAnalyzer()
    success = analyzer.run_complete_analysis()

    if success:
        print("\n🔧 **추천 명령어:**")
        print("/logi_master analyze_complete_data [전체 데이터 분석 - 상세 결과 확인]")
        print("/switch_mode LATTICE [창고 최적화 모드 - 입출고 로직 검증]")
        print(
            "/validate_data warehouse_operations [창고 운영 데이터 검증 - 정확도 확인]"
        )
        print("/automate test-pipeline [전체 테스트 파이프라인 실행 - 시스템 검증]")
    else:
        print("\n❌ 분석 실패")


if __name__ == "__main__":
    main()
