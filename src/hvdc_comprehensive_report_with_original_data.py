#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC 입고로직 종합리포트 (원본 데이터 포함)
MACHO-GPT v3.4-mini for HVDC Project
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, Reference, PieChart


class HVDCComprehensiveReportGenerator:
    """HVDC 종합 리포트 생성 클래스 (원본 데이터 포함)"""

    def __init__(self):
        self.data_dir = Path("data")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def load_original_data(self) -> tuple:
        """원본 데이터 로드"""
        print("📊 원본 데이터 로드 중...")

        # HITACHI 데이터 로드
        hitachi_file = self.data_dir / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        hitachi_df = pd.read_excel(hitachi_file)
        print(f"✅ HITACHI 데이터 로드: {len(hitachi_df)}행")

        # SIEMENS 데이터 로드
        siemens_file = self.data_dir / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        siemens_df = pd.read_excel(siemens_file)
        print(f"✅ SIEMENS 데이터 로드: {len(siemens_df)}행")

        return hitachi_df, siemens_df

    def create_warehouse_io_calculator(
        self, hitachi_df: pd.DataFrame, siemens_df: pd.DataFrame
    ):
        """입고/출고/재고 계산기 생성"""
        print("🔧 입고/출고/재고 계산기 생성 중...")

        # 데이터 통합
        combined_df = pd.concat([hitachi_df, siemens_df], ignore_index=True)

        # Status_Location 기준으로 입고/출고/재고 계산
        warehouse_stats = {}

        for location in combined_df["Status_Location"].unique():
            if pd.isna(location):
                continue

            location_data = combined_df[combined_df["Status_Location"] == location]

            # 입고: 해당 위치에 도착한 모든 항목
            inbound = len(location_data)

            # 출고: 다른 위치로 이동한 항목 (현재 위치가 아닌 경우)
            outbound = len(
                combined_df[
                    (combined_df["Status_Location"] != location)
                    & (combined_df["Status_Location"].notna())
                ]
            )

            # 재고: 입고 - 출고
            inventory = inbound - outbound

            warehouse_stats[location] = {
                "Inbound": inbound,
                "Outbound": outbound,
                "Inventory": inventory,
                "Total_Items": len(location_data),
            }

        return (
            pd.DataFrame(warehouse_stats)
            .T.reset_index()
            .rename(columns={"index": "Warehouse"})
        )

    def create_monthly_report(self, hitachi_df: pd.DataFrame, siemens_df: pd.DataFrame):
        """월별 리포트 생성"""
        print("📅 월별 리포트 생성 중...")

        # 날짜 컬럼 처리
        combined_df = pd.concat([hitachi_df, siemens_df], ignore_index=True)

        # Status_Location_Date를 datetime으로 변환
        combined_df["Status_Location_Date"] = pd.to_datetime(
            combined_df["Status_Location_Date"], errors="coerce"
        )

        # 월별 집계
        monthly_stats = []

        for year in [2024, 2025]:
            for month in range(1, 13):
                if year == 2025 and month > 6:  # 2025년 6월까지만
                    break

                month_data = combined_df[
                    (combined_df["Status_Location_Date"].dt.year == year)
                    & (combined_df["Status_Location_Date"].dt.month == month)
                ]

                if len(month_data) > 0:
                    monthly_stats.append(
                        {
                            "Year": year,
                            "Month": month,
                            "Total_Items": len(month_data),
                            "Unique_Warehouses": month_data[
                                "Status_Location"
                            ].nunique(),
                            "Total_CBM": month_data["CBM"].sum(),
                            "Total_SQM": month_data["SQM"].sum(),
                            "Avg_Handling": month_data["total handling"].mean(),
                        }
                    )

        return pd.DataFrame(monthly_stats)

    def create_flow_code_analysis(
        self, hitachi_df: pd.DataFrame, siemens_df: pd.DataFrame
    ):
        """Flow Code 분석"""
        print("🔄 Flow Code 분석 중...")

        combined_df = pd.concat([hitachi_df, siemens_df], ignore_index=True)

        # Flow Code 분포 분석
        flow_stats = combined_df["wh handling"].value_counts().reset_index()
        flow_stats.columns = ["Flow_Code", "Count"]
        flow_stats["Percentage"] = (
            flow_stats["Count"] / flow_stats["Count"].sum() * 100
        ).round(2)

        return flow_stats

    def create_warehouse_performance_analysis(
        self, hitachi_df: pd.DataFrame, siemens_df: pd.DataFrame
    ):
        """창고별 성능 분석"""
        print("📊 창고별 성능 분석 중...")

        combined_df = pd.concat([hitachi_df, siemens_df], ignore_index=True)

        warehouse_performance = []

        for warehouse in combined_df["Status_Location"].unique():
            if pd.isna(warehouse):
                continue

            warehouse_data = combined_df[combined_df["Status_Location"] == warehouse]

            performance = {
                "Warehouse": warehouse,
                "Total_Items": len(warehouse_data),
                "Total_CBM": warehouse_data["CBM"].sum(),
                "Total_SQM": warehouse_data["SQM"].sum(),
                "Avg_Handling": warehouse_data["total handling"].mean(),
                "Max_Handling": warehouse_data["total handling"].max(),
                "Min_Handling": warehouse_data["total handling"].min(),
                "Stackable_Items": len(
                    warehouse_data[warehouse_data["Stack"] == "Stackable"]
                ),
                "Non_Stackable_Items": len(
                    warehouse_data[warehouse_data["Stack"] == "Non Stackable"]
                ),
                "Indoor_Items": len(
                    warehouse_data[warehouse_data["Storage"] == "Indoor"]
                ),
                "Outdoor_Items": len(
                    warehouse_data[warehouse_data["Storage"] == "Outdoor"]
                ),
            }

            warehouse_performance.append(performance)

        return pd.DataFrame(warehouse_performance)

    def create_excel_report(self, hitachi_df: pd.DataFrame, siemens_df: pd.DataFrame):
        """Excel 리포트 생성"""
        print("📋 Excel 리포트 생성 중...")

        # 파일명 생성
        filename = f"HVDC_입고로직_종합리포트_원본데이터포함_{self.timestamp}.xlsx"
        filepath = self.output_dir / filename

        # Excel 워크북 생성
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:

            # 1. 원본 HITACHI 데이터
            print("  📄 HITACHI 원본 데이터 시트 생성...")
            hitachi_df.to_excel(writer, sheet_name="01_HITACHI_원본데이터", index=False)

            # 2. 원본 SIEMENS 데이터
            print("  📄 SIEMENS 원본 데이터 시트 생성...")
            siemens_df.to_excel(writer, sheet_name="02_SIEMENS_원본데이터", index=False)

            # 3. 통합 데이터
            print("  📄 통합 데이터 시트 생성...")
            combined_df = pd.concat([hitachi_df, siemens_df], ignore_index=True)
            combined_df.to_excel(writer, sheet_name="03_통합_원본데이터", index=False)

            # 4. 입고/출고/재고 분석
            print("  📄 입고/출고/재고 분석 시트 생성...")
            io_analysis = self.create_warehouse_io_calculator(hitachi_df, siemens_df)
            io_analysis.to_excel(writer, sheet_name="04_입고출고재고_분석", index=False)

            # 5. 월별 리포트
            print("  📄 월별 리포트 시트 생성...")
            monthly_report = self.create_monthly_report(hitachi_df, siemens_df)
            monthly_report.to_excel(writer, sheet_name="05_월별_리포트", index=False)

            # 6. Flow Code 분석
            print("  📄 Flow Code 분석 시트 생성...")
            flow_analysis = self.create_flow_code_analysis(hitachi_df, siemens_df)
            flow_analysis.to_excel(writer, sheet_name="06_Flow_Code_분석", index=False)

            # 7. 창고별 성능 분석
            print("  📄 창고별 성능 분석 시트 생성...")
            performance_analysis = self.create_warehouse_performance_analysis(
                hitachi_df, siemens_df
            )
            performance_analysis.to_excel(
                writer, sheet_name="07_창고별_성능분석", index=False
            )

            # 8. 요약 통계
            print("  📄 요약 통계 시트 생성...")
            summary_stats = self.create_summary_statistics(hitachi_df, siemens_df)
            summary_stats.to_excel(writer, sheet_name="08_요약_통계", index=False)

            # 9. 데이터 품질 리포트
            print("  📄 데이터 품질 리포트 시트 생성...")
            quality_report = self.create_data_quality_report(hitachi_df, siemens_df)
            quality_report.to_excel(
                writer, sheet_name="09_데이터_품질리포트", index=False
            )

        print(f"✅ Excel 리포트 생성 완료: {filepath}")
        return filepath

    def create_summary_statistics(
        self, hitachi_df: pd.DataFrame, siemens_df: pd.DataFrame
    ):
        """요약 통계 생성"""
        print("📊 요약 통계 생성 중...")

        combined_df = pd.concat([hitachi_df, siemens_df], ignore_index=True)

        summary_data = []

        # 전체 통계
        summary_data.append(
            {
                "Category": "전체",
                "Total_Records": len(combined_df),
                "HITACHI_Records": len(hitachi_df),
                "SIEMENS_Records": len(siemens_df),
                "Total_CBM": combined_df["CBM"].sum(),
                "Total_SQM": combined_df["SQM"].sum(),
                "Unique_Warehouses": combined_df["Status_Location"].nunique(),
                "Avg_Handling": combined_df["total handling"].mean(),
            }
        )

        # HITACHI 통계
        summary_data.append(
            {
                "Category": "HITACHI",
                "Total_Records": len(hitachi_df),
                "HITACHI_Records": len(hitachi_df),
                "SIEMENS_Records": 0,
                "Total_CBM": hitachi_df["CBM"].sum(),
                "Total_SQM": hitachi_df["SQM"].sum(),
                "Unique_Warehouses": hitachi_df["Status_Location"].nunique(),
                "Avg_Handling": hitachi_df["total handling"].mean(),
            }
        )

        # SIEMENS 통계
        summary_data.append(
            {
                "Category": "SIEMENS",
                "Total_Records": len(siemens_df),
                "HITACHI_Records": 0,
                "SIEMENS_Records": len(siemens_df),
                "Total_CBM": siemens_df["CBM"].sum(),
                "Total_SQM": siemens_df["SQM"].sum(),
                "Unique_Warehouses": siemens_df["Status_Location"].nunique(),
                "Avg_Handling": siemens_df["total handling"].mean(),
            }
        )

        return pd.DataFrame(summary_data)

    def create_data_quality_report(
        self, hitachi_df: pd.DataFrame, siemens_df: pd.DataFrame
    ):
        """데이터 품질 리포트 생성"""
        print("🔍 데이터 품질 리포트 생성 중...")

        quality_data = []

        # HITACHI 데이터 품질
        hitachi_quality = {
            "Dataset": "HITACHI",
            "Total_Records": len(hitachi_df),
            "Total_Columns": len(hitachi_df.columns),
            "Null_Records": hitachi_df.isnull().sum().sum(),
            "Duplicate_Records": hitachi_df.duplicated().sum(),
            "Unique_Warehouses": hitachi_df["Status_Location"].nunique(),
            "Date_Range_Start": (
                str(hitachi_df["Status_Location_Date"].min())
                if pd.notna(hitachi_df["Status_Location_Date"].min())
                else "N/A"
            ),
            "Date_Range_End": (
                str(hitachi_df["Status_Location_Date"].max())
                if pd.notna(hitachi_df["Status_Location_Date"].max())
                else "N/A"
            ),
            "CBM_Range_Min": hitachi_df["CBM"].min(),
            "CBM_Range_Max": hitachi_df["CBM"].max(),
            "SQM_Range_Min": hitachi_df["SQM"].min(),
            "SQM_Range_Max": hitachi_df["SQM"].max(),
        }
        quality_data.append(hitachi_quality)

        # SIEMENS 데이터 품질
        siemens_quality = {
            "Dataset": "SIEMENS",
            "Total_Records": len(siemens_df),
            "Total_Columns": len(siemens_df.columns),
            "Null_Records": siemens_df.isnull().sum().sum(),
            "Duplicate_Records": siemens_df.duplicated().sum(),
            "Unique_Warehouses": siemens_df["Status_Location"].nunique(),
            "Date_Range_Start": (
                str(siemens_df["Status_Location_Date"].min())
                if pd.notna(siemens_df["Status_Location_Date"].min())
                else "N/A"
            ),
            "Date_Range_End": (
                str(siemens_df["Status_Location_Date"].max())
                if pd.notna(siemens_df["Status_Location_Date"].max())
                else "N/A"
            ),
            "CBM_Range_Min": siemens_df["CBM"].min(),
            "CBM_Range_Max": siemens_df["CBM"].max(),
            "SQM_Range_Min": siemens_df["SQM"].min(),
            "SQM_Range_Max": siemens_df["SQM"].max(),
        }
        quality_data.append(siemens_quality)

        return pd.DataFrame(quality_data)

    def generate_report(self):
        """전체 리포트 생성"""
        print("🚀 HVDC 종합 리포트 생성 시작 (원본 데이터 포함)")
        print("=" * 80)

        try:
            # 원본 데이터 로드
            hitachi_df, siemens_df = self.load_original_data()

            # Excel 리포트 생성
            report_file = self.create_excel_report(hitachi_df, siemens_df)

            # 생성된 리포트 정보 출력
            print(f"\n📋 리포트 생성 완료!")
            print(f"📁 파일 위치: {report_file}")
            print(f"📊 포함된 시트:")
            print(f"  1. 01_HITACHI_원본데이터 ({len(hitachi_df)}행)")
            print(f"  2. 02_SIEMENS_원본데이터 ({len(siemens_df)}행)")
            print(f"  3. 03_통합_원본데이터 ({len(hitachi_df) + len(siemens_df)}행)")
            print(f"  4. 04_입고출고재고_분석")
            print(f"  5. 05_월별_리포트")
            print(f"  6. 06_Flow_Code_분석")
            print(f"  7. 07_창고별_성능분석")
            print(f"  8. 08_요약_통계")
            print(f"  9. 09_데이터_품질리포트")

            return report_file

        except Exception as e:
            print(f"❌ 리포트 생성 실패: {e}")
            return None


def main():
    """메인 함수"""
    generator = HVDCComprehensiveReportGenerator()
    report_file = generator.generate_report()

    if report_file:
        print(f"\n✅ HVDC 종합 리포트 생성 완료!")
        print(f"📁 파일: {report_file}")
    else:
        print(f"\n❌ 리포트 생성 실패")


if __name__ == "__main__":
    main()
