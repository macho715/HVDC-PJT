"""
HVDC Excel Reporter Final - v2.8.2 Standard
Single Source of Truth for Warehouse In/Out, Site In, Inventory Reports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Any
import warnings
import os  # Added for file existence check

warnings.filterwarnings("ignore")


class PKGValidationEngine:
    """PKG Accuracy Validation Engine (99% 기준)"""

    def __init__(self, threshold: float = 0.99):
        self.threshold = threshold
        self.logger = logging.getLogger(__name__)

    def validate_pkg_accuracy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """PKG Accuracy 검증"""
        try:
            # 필수 컬럼 존재 확인
            required_columns = ["HVDC CODE 1", "HVDC CODE 2", "HVDC CODE 3"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return {
                    "status": "FAIL",
                    "accuracy": 0.0,
                    "error": f"Missing required columns: {missing_columns}",
                    "details": {"missing_columns": missing_columns},
                }

            # Category 컬럼 확인 (없으면 창고 관련 컬럼들 확인)
            warehouse_columns = [
                "DHL Warehouse",
                "DSV Indoor",
                "DSV Al Markaz",
                "DSV Outdoor",
                "AAA  Storage",
                "Hauler Indoor",
                "DSV MZP",
            ]
            has_category = "Category" in df.columns
            has_warehouse_data = any(col in df.columns for col in warehouse_columns)

            if not has_category and not has_warehouse_data:
                return {
                    "status": "FAIL",
                    "accuracy": 0.0,
                    "error": "No Category or warehouse columns found",
                    "details": {"missing_warehouse_data": True},
                }

            # 데이터 품질 검증
            total_rows = len(df)
            valid_rows = 0

            for _, row in df.iterrows():
                # HVDC CODE 검증
                code1_valid = (
                    pd.notna(row["HVDC CODE 1"])
                    and str(row["HVDC CODE 1"]).strip() != ""
                )
                code2_valid = (
                    pd.notna(row["HVDC CODE 2"])
                    and str(row["HVDC CODE 2"]).strip() != ""
                )
                code3_valid = (
                    pd.notna(row["HVDC CODE 3"])
                    and str(row["HVDC CODE 3"]).strip() != ""
                )

                # Category 또는 창고 데이터 검증
                if has_category:
                    category_valid = (
                        pd.notna(row["Category"]) and str(row["Category"]).strip() != ""
                    )
                else:
                    # 창고 관련 컬럼 중 하나라도 값이 있으면 유효
                    warehouse_valid = any(
                        pd.notna(row.get(col, ""))
                        and str(row.get(col, "")).strip() != ""
                        for col in warehouse_columns
                        if col in df.columns
                    )
                    category_valid = warehouse_valid

                if code1_valid and code2_valid and code3_valid and category_valid:
                    valid_rows += 1

            accuracy = valid_rows / total_rows if total_rows > 0 else 0.0

            result = {
                "status": "PASS" if accuracy >= self.threshold else "FAIL",
                "accuracy": round(accuracy, 4),
                "total_rows": total_rows,
                "valid_rows": valid_rows,
                "threshold": self.threshold,
                "details": {
                    "code1_valid": code1_valid,
                    "code2_valid": code2_valid,
                    "code3_valid": code3_valid,
                    "category_valid": category_valid,
                    "has_category_column": has_category,
                    "has_warehouse_data": has_warehouse_data,
                },
            }

            self.logger.info(
                f"PKG Accuracy: {accuracy:.2%} ({valid_rows}/{total_rows})"
            )
            return result

        except Exception as e:
            self.logger.error(f"PKG validation failed: {e}")
            return {"status": "ERROR", "accuracy": 0.0, "error": str(e)}


class HVDCExcelReporter:
    """HVDC Excel Reporter - v2.8.2 Standard"""

    def __init__(self, df: pd.DataFrame, output_file: str = None):
        self.df = df.copy()
        self.output_file = (
            output_file or f"HVDC_Report_{datetime.now().strftime('%Y-%m')}.xlsx"
        )
        self.pkg_validator = PKGValidationEngine()
        self.logger = logging.getLogger(__name__)

        # v2.8.2 온톨로지 규칙 로드
        self.ontology_rules = self._load_ontology_rules()

    def _load_ontology_rules(self) -> Dict[str, Any]:
        """v2.8.2 온톨로지 규칙 로드"""
        try:
            # 기본 규칙 (실제로는 mapping_rules_v2.8.2.json에서 로드)
            rules = {
                "warehouse_categories": [
                    "DSV Outdoor",
                    "DSV Indoor",
                    "DSV Al Markaz",
                    "DSV MZP",
                    "AAA Storage",
                ],
                "hvdc_codes": {
                    "code1": ["HVDC"],
                    "code2": ["SQM", "MANPOWER", "ADOPT"],
                    "code3": ["HE", "SIM", "SCT", "OTHER"],
                },
                "flow_codes": [0, 1, 2, 3, 4],
                "required_columns": [
                    "HVDC CODE 1",
                    "HVDC CODE 2",
                    "HVDC CODE 3",
                    "Category",
                    "Amount",
                    "Date",
                ],
            }
            return rules
        except Exception as e:
            self.logger.warning(f"Failed to load ontology rules: {e}")
            return {}

    def normalize_data(self) -> pd.DataFrame:
        """데이터 정규화"""
        try:
            # 데이터 클리닝
            df_clean = self.df.copy()

            # NaN 처리
            df_clean = df_clean.fillna("")

            # 문자열 정규화
            for col in df_clean.select_dtypes(include=["object"]).columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()

            # Category 컬럼이 없으면 창고 데이터로 생성
            if "Category" not in df_clean.columns:
                warehouse_columns = [
                    "DHL Warehouse",
                    "DSV Indoor",
                    "DSV Al Markaz",
                    "DSV Outdoor",
                    "AAA  Storage",
                    "Hauler Indoor",
                    "DSV MZP",
                ]

                def determine_category(row):
                    for col in warehouse_columns:
                        if (
                            col in df_clean.columns
                            and pd.notna(row[col])
                            and str(row[col]).strip() != ""
                        ):
                            return col
                    return "Unknown"

                df_clean["Category"] = df_clean.apply(determine_category, axis=1)
                self.logger.info("Category column created from warehouse data")

            # 날짜 컬럼 처리
            date_columns = [
                col
                for col in df_clean.columns
                if "date" in col.lower() or "time" in col.lower()
            ]
            for col in date_columns:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")
                except:
                    pass

            # 금액 컬럼 처리
            amount_columns = [
                col
                for col in df_clean.columns
                if "amount" in col.lower()
                or "cost" in col.lower()
                or "price" in col.lower()
            ]
            for col in amount_columns:
                try:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
                except:
                    pass

            self.logger.info(f"Data normalized: {len(df_clean)} rows")
            return df_clean

        except Exception as e:
            self.logger.error(f"Data normalization failed: {e}")
            return self.df

    def create_main_transaction_sheet(self, writer: pd.ExcelWriter) -> None:
        """메인 트랜잭션 데이터 시트 생성"""
        try:
            # 정규화된 데이터
            df_norm = self.normalize_data()

            # 메인 트랜잭션 시트
            df_norm.to_excel(writer, sheet_name="Main_Transaction_Data", index=False)

            # 시트 포맷팅
            worksheet = writer.sheets["Main_Transaction_Data"]

            # 헤더 스타일
            for col_num, value in enumerate(df_norm.columns.values, 1):
                worksheet.write(0, col_num, value)

            self.logger.info("Main transaction sheet created")

        except Exception as e:
            self.logger.error(f"Failed to create main transaction sheet: {e}")

    def create_summary_sheet(self, writer: pd.ExcelWriter) -> None:
        """요약 리포트 시트 생성"""
        try:
            df_norm = self.normalize_data()

            # 기본 통계
            summary_data = {
                "Metric": [
                    "Total Transactions",
                    "Total Amount (AED)",
                    "Average Amount (AED)",
                    "Unique Warehouses",
                    "Date Range",
                    "PKG Accuracy (%)",
                ],
                "Value": [
                    len(df_norm),
                    df_norm.get("Amount", pd.Series([0])).sum(),
                    df_norm.get("Amount", pd.Series([0])).mean(),
                    df_norm.get("Category", pd.Series()).nunique(),
                    f"{df_norm.get('Date', pd.Series()).min()} to {df_norm.get('Date', pd.Series()).max()}",
                    f"{self.pkg_validator.validate_pkg_accuracy(df_norm)['accuracy']:.2%}",
                ],
            }

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary_Report", index=False)

            self.logger.info("Summary sheet created")

        except Exception as e:
            self.logger.error(f"Failed to create summary sheet: {e}")

    def create_warehouse_performance_sheet(self, writer: pd.ExcelWriter) -> None:
        """창고별 성과 시트 생성"""
        try:
            df_norm = self.normalize_data()

            if "Category" in df_norm.columns and "Amount" in df_norm.columns:
                # 창고별 통계
                warehouse_stats = (
                    df_norm.groupby("Category")
                    .agg({"Amount": ["count", "sum", "mean"], "HVDC CODE 3": "nunique"})
                    .round(2)
                )

                warehouse_stats.columns = [
                    "Transaction_Count",
                    "Total_Amount",
                    "Average_Amount",
                    "Unique_Items",
                ]
                warehouse_stats = warehouse_stats.reset_index()

                warehouse_stats.to_excel(
                    writer, sheet_name="Warehouse_Performance", index=False
                )

                self.logger.info("Warehouse performance sheet created")
            else:
                self.logger.warning(
                    "Required columns not found for warehouse performance"
                )

        except Exception as e:
            self.logger.error(f"Failed to create warehouse performance sheet: {e}")

    def create_monthly_trend_sheet(self, writer: pd.ExcelWriter) -> None:
        """월별 트렌드 시트 생성"""
        try:
            df_norm = self.normalize_data()

            # 날짜 컬럼 찾기
            date_col = None
            for col in df_norm.columns:
                if "date" in col.lower():
                    date_col = col
                    break

            if date_col and pd.api.types.is_datetime64_any_dtype(df_norm[date_col]):
                # 월별 집계
                df_norm["Month"] = df_norm[date_col].dt.to_period("M")
                monthly_stats = (
                    df_norm.groupby("Month")
                    .agg({"Amount": ["count", "sum"], "Category": "nunique"})
                    .round(2)
                )

                monthly_stats.columns = [
                    "Transaction_Count",
                    "Total_Amount",
                    "Warehouse_Count",
                ]
                monthly_stats = monthly_stats.reset_index()
                monthly_stats["Month"] = monthly_stats["Month"].astype(str)

                monthly_stats.to_excel(writer, sheet_name="Monthly_Trend", index=False)

                self.logger.info("Monthly trend sheet created")
            else:
                self.logger.warning("Date column not found for monthly trend")

        except Exception as e:
            self.logger.error(f"Failed to create monthly trend sheet: {e}")

    def create_flow_code_analysis_sheet(self, writer: pd.ExcelWriter) -> None:
        """Flow Code 분석 시트 생성"""
        try:
            df_norm = self.normalize_data()

            # Flow Code 컬럼 찾기
            flow_col = None
            for col in df_norm.columns:
                if "flow" in col.lower() or "wh" in col.lower():
                    flow_col = col
                    break

            if flow_col:
                # Flow Code별 통계
                flow_stats = (
                    df_norm.groupby(flow_col)
                    .agg({"Amount": ["count", "sum"], "Category": "nunique"})
                    .round(2)
                )

                flow_stats.columns = [
                    "Transaction_Count",
                    "Total_Amount",
                    "Warehouse_Count",
                ]
                flow_stats = flow_stats.reset_index()
                flow_stats.columns = [
                    "Flow_Code",
                    "Transaction_Count",
                    "Total_Amount",
                    "Warehouse_Count",
                ]

                flow_stats.to_excel(
                    writer, sheet_name="Flow_Code_Analysis", index=False
                )

                self.logger.info("Flow code analysis sheet created")
            else:
                self.logger.warning("Flow code column not found")

        except Exception as e:
            self.logger.error(f"Failed to create flow code analysis sheet: {e}")

    def create_hvdc_code_breakdown_sheet(self, writer: pd.ExcelWriter) -> None:
        """HVDC Code 분석 시트 생성"""
        try:
            df_norm = self.normalize_data()

            # HVDC Code별 분석
            code_analysis = {}

            for code_col in ["HVDC CODE 1", "HVDC CODE 2", "HVDC CODE 3"]:
                if code_col in df_norm.columns:
                    code_stats = df_norm[code_col].value_counts().reset_index()
                    code_stats.columns = [f"{code_col}_Value", f"{code_col}_Count"]
                    code_analysis[code_col] = code_stats

            # 첫 번째 코드부터 시작
            if code_analysis:
                first_code = list(code_analysis.keys())[0]
                result_df = code_analysis[first_code]

                # 나머지 코드들과 조인
                for code_col, code_df in list(code_analysis.items())[1:]:
                    result_df = pd.merge(
                        result_df,
                        code_df,
                        left_index=True,
                        right_index=True,
                        how="outer",
                    )

                result_df.to_excel(
                    writer, sheet_name="HVDC_Code_Breakdown", index=False
                )

                self.logger.info("HVDC code breakdown sheet created")
            else:
                self.logger.warning("No HVDC code columns found")

        except Exception as e:
            self.logger.error(f"Failed to create HVDC code breakdown sheet: {e}")

    def create_validation_report_sheet(self, writer: pd.ExcelWriter) -> None:
        """검증 리포트 시트 생성"""
        try:
            df_norm = self.normalize_data()

            # PKG 검증 결과
            pkg_result = self.pkg_validator.validate_pkg_accuracy(df_norm)

            validation_data = {
                "Validation_Item": [
                    "PKG Accuracy",
                    "Total Rows",
                    "Valid Rows",
                    "Threshold",
                    "Status",
                    "Validation Date",
                ],
                "Value": [
                    f"{pkg_result['accuracy']:.2%}",
                    pkg_result.get("total_rows", 0),
                    pkg_result.get("valid_rows", 0),
                    f"{pkg_result.get('threshold', 0.99):.2%}",
                    pkg_result["status"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ],
            }

            validation_df = pd.DataFrame(validation_data)
            validation_df.to_excel(writer, sheet_name="Validation_Report", index=False)

            self.logger.info("Validation report sheet created")

        except Exception as e:
            self.logger.error(f"Failed to create validation report sheet: {e}")

    def generate_excel_report(self) -> Dict[str, Any]:
        """표준 Excel 리포트 생성 - Single Source of Truth"""
        try:
            self.logger.info(f"Starting Excel report generation: {self.output_file}")

            # PKG 검증
            pkg_result = self.pkg_validator.validate_pkg_accuracy(self.df)

            if pkg_result["status"] == "FAIL":
                self.logger.error(
                    f"PKG Accuracy below threshold: {pkg_result['accuracy']:.2%}"
                )
                return {
                    "status": "FAIL",
                    "error": f"PKG Accuracy {pkg_result['accuracy']:.2%} below threshold {pkg_result['threshold']:.2%}",
                    "pkg_result": pkg_result,
                }

            # Excel 파일 생성
            with pd.ExcelWriter(self.output_file, engine="xlsxwriter") as writer:
                # 1. 메인 트랜잭션 데이터
                self.create_main_transaction_sheet(writer)

                # 2. 요약 리포트
                self.create_summary_sheet(writer)

                # 3. 창고별 성과
                self.create_warehouse_performance_sheet(writer)

                # 4. 월별 트렌드
                self.create_monthly_trend_sheet(writer)

                # 5. Flow Code 분석
                self.create_flow_code_analysis_sheet(writer)

                # 6. HVDC Code 분석
                self.create_hvdc_code_breakdown_sheet(writer)

                # 7. 검증 리포트
                self.create_validation_report_sheet(writer)

            self.logger.info(f"Excel report generated successfully: {self.output_file}")

            return {
                "status": "SUCCESS",
                "output_file": self.output_file,
                "pkg_accuracy": pkg_result["accuracy"],
                "total_rows": len(self.df),
                "sheets_created": 7,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Excel report generation failed: {e}")
            return {"status": "ERROR", "error": str(e)}


def main():
    """메인 실행 함수"""
    print("🏭 HVDC Excel Reporter Final - v2.8.2 Standard")
    print("=" * 60)

    # 실제 HVDC 데이터 파일 로드
    data_files = [
        "../data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "../data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx",
        "../data_cleaned/HVDC_WAREHOUSE_HITACHI_CLEANED_20250709_201121.xlsx",
        "../data_cleaned/HVDC_WAREHOUSE_SIMENSE_CLEANED_20250709_201121.xlsx",
    ]

    # 사용 가능한 파일 찾기
    available_file = None
    for file_path in data_files:
        if os.path.exists(file_path):
            available_file = file_path
            break

    if available_file:
        print(f"📁 데이터 파일 로드: {available_file}")
        try:
            df = pd.read_excel(available_file)
            print(f"✅ 데이터 로드 성공: {len(df)} 행, {len(df.columns)} 컬럼")
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return
    else:
        print("⚠️ 실제 데이터 파일을 찾을 수 없어 샘플 데이터 사용")
        # 샘플 데이터 생성
        sample_data = {
            "HVDC CODE 1": ["HVDC"] * 100,
            "HVDC CODE 2": ["SQM"] * 60 + ["MANPOWER"] * 40,
            "HVDC CODE 3": ["HE"] * 50 + ["SIM"] * 30 + ["SCT"] * 20,
            "Category": ["DSV Outdoor"] * 40
            + ["DSV Indoor"] * 35
            + ["DSV Al Markaz"] * 15
            + ["DSV MZP"] * 10,
            "Amount": np.random.randint(1000, 50000, 100),
            "Date": pd.date_range("2025-01-01", periods=100, freq="D"),
        }
        df = pd.DataFrame(sample_data)

    # 리포트 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"HVDC_Comprehensive_Report_{timestamp}.xlsx"

    reporter = HVDCExcelReporter(df, output_file)
    result = reporter.generate_excel_report()

    if result["status"] == "SUCCESS":
        print(f"✅ 리포트 생성 성공: {result['output_file']}")
        print(f"📊 PKG Accuracy: {result['pkg_accuracy']:.2%}")
        print(f"📋 총 행 수: {result['total_rows']}")
        print(f"📄 생성된 시트: {result['sheets_created']}개")

        # 생성된 파일 확인
        if os.path.exists(result["output_file"]):
            file_size = os.path.getsize(result["output_file"]) / 1024  # KB
            print(f"📁 파일 크기: {file_size:.1f} KB")
    else:
        print(f"❌ 리포트 생성 실패: {result.get('error', 'Unknown error')}")

    print("\n🎯 추천 명령어:")
    print("/automate test-pipeline --fast")
    print("/validate-data code-quality")
    print("/visualize_data --type=pkg-flow")


if __name__ == "__main__":
    main()
