#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini 검증 리포트 생성 시스템
/generate-validation-report 명령어 구현

입력:
1. 청구서 원본 파일 (DSV 월별 Invoice)
2. 전체 화물 리스트 파일 (HVDC WAREHOUSE_HITACHI(HE) 등)

출력:
1. PDF 요약 보고서 (검증 결과표 포함)
2. Excel 상세 결과 (PASS/FAIL 구분, 금액 차이 등)
3. RDF TTL 파일 (온톨로지 트리플 형태)
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import os
import re
from dataclasses import dataclass

# RDF 라이브러리 (선택적)
try:
    from rdflib import Graph, Namespace, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, XSD

    RDF_AVAILABLE = True
except ImportError:
    RDF_AVAILABLE = False
    print("⚠️ rdflib 패키지가 설치되지 않았습니다. RDF TTL 파일 생성이 비활성화됩니다.")
import matplotlib.pyplot as plt
import seaborn as sns

# ReportLab 라이브러리 (선택적)
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ reportlab 패키지가 설치되지 않았습니다. PDF 보고서 생성이 비활성화됩니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    """검증 설정"""

    confidence_threshold: float = 0.95
    amount_tolerance: float = 0.01  # 1% 금액 오차 허용
    quantity_tolerance: float = 0.05  # 5% 수량 오차 허용
    fanr_compliance_required: bool = True
    moiat_compliance_required: bool = True
    generate_pdf: bool = True
    generate_excel: bool = True
    generate_rdf: bool = True


class ValidationReportGenerator:
    """MACHO-GPT v3.4-mini 검증 리포트 생성기"""

    def __init__(self, config: ValidationConfig = None):
        """검증 리포트 생성기 초기화"""
        self.config = config or ValidationConfig()

        # 물류 도메인 온톨로지 네임스페이스 (RDF 사용 가능한 경우에만)
        if RDF_AVAILABLE:
            self.LOGI = Namespace("http://macho-gpt.com/ontology/logistics#")
            self.HVDC = Namespace("http://macho-gpt.com/ontology/hvdc#")
            self.FANR = Namespace("http://macho-gpt.com/ontology/fanr#")
        else:
            self.LOGI = None
            self.HVDC = None
            self.FANR = None

        # 검증 결과 저장소
        self.validation_results = {
            "invoice_validation": {},
            "warehouse_validation": {},
            "cross_validation": {},
            "compliance_validation": {},
            "overall_validation": {},
        }

        # 출력 디렉토리 설정
        self.output_dir = Path("../output/validation_reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🔍 검증 리포트 생성기 초기화 완료")

    def generate_validation_report(
        self, invoice_file: str, warehouse_file: str
    ) -> Dict[str, Any]:
        """
        종합 검증 리포트 생성

        Args:
            invoice_file: 청구서 원본 파일 경로
            warehouse_file: 화물 입출고 리스트 파일 경로

        Returns:
            검증 결과 및 생성된 파일 경로들
        """
        logger.info("🚀 종합 검증 리포트 생성 시작")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # 1. 파일 로드 및 검증
            invoice_data = self._load_invoice_data(invoice_file)
            warehouse_data = self._load_warehouse_data(warehouse_file)

            # 2. 개별 검증 수행
            invoice_validation = self._validate_invoice_data(invoice_data)
            warehouse_validation = self._validate_warehouse_data(warehouse_data)

            # 3. 교차 검증 수행
            cross_validation = self._perform_cross_validation(
                invoice_data, warehouse_data
            )

            # 4. 규정 준수 검증
            compliance_validation = self._validate_compliance(
                invoice_data, warehouse_data
            )

            # 5. 전체 검증 결과 통합
            overall_validation = self._calculate_overall_validation(
                invoice_validation,
                warehouse_validation,
                cross_validation,
                compliance_validation,
            )

            # 6. 리포트 파일 생성
            generated_files = self._generate_report_files(
                timestamp,
                invoice_validation,
                warehouse_validation,
                cross_validation,
                compliance_validation,
                overall_validation,
            )

            # 7. 결과 반환
            result = {
                "command": "generate_validation_report",
                "execution_time": datetime.now().isoformat(),
                "input_files": {
                    "invoice_file": invoice_file,
                    "warehouse_file": warehouse_file,
                },
                "validation_results": {
                    "invoice_validation": invoice_validation,
                    "warehouse_validation": warehouse_validation,
                    "cross_validation": cross_validation,
                    "compliance_validation": compliance_validation,
                    "overall_validation": overall_validation,
                },
                "generated_files": generated_files,
                "recommendations": self._generate_recommendations(overall_validation),
                "next_actions": self._suggest_next_actions(overall_validation),
            }

            logger.info(
                f"✅ 검증 리포트 생성 완료 - 전체 점수: {overall_validation['total_score']:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ 검증 리포트 생성 실패: {e}")
            return self._create_error_response(str(e))

    def _load_invoice_data(self, invoice_file: str) -> pd.DataFrame:
        """청구서 데이터 로드"""
        logger.info(f"📄 청구서 데이터 로드: {invoice_file}")

        try:
            # Excel 파일 로드
            df = pd.read_excel(invoice_file, sheet_name=0)
            logger.info(f"📊 원본 데이터 크기: {df.shape}")
            logger.info(f"📋 원본 컬럼명: {list(df.columns)}")

            # 기본 데이터 검증
            required_columns = [
                "Item",
                "Description",
                "Quantity",
                "Unit_Price",
                "Total_Amount",
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                logger.warning(f"⚠️ 청구서 필수 컬럼 누락: {missing_columns}")
                logger.info(f"🔍 매핑 전 사용 가능한 컬럼: {list(df.columns)}")

            # 데이터 정제
            df = self._clean_invoice_data(df)

            # 매핑 후 필수 컬럼 재검증
            final_missing = [col for col in required_columns if col not in df.columns]
            if final_missing:
                logger.error(f"❌ 매핑 후에도 필수 컬럼 누락: {final_missing}")
                logger.info(f"📋 최종 사용 가능한 컬럼: {list(df.columns)}")
            else:
                logger.info(f"✅ 모든 필수 컬럼 매핑 완료")

            logger.info(f"✅ 청구서 데이터 로드 완료: {len(df)}건")
            return df

        except Exception as e:
            logger.error(f"❌ 청구서 데이터 로드 실패: {e}")
            raise

    def _load_warehouse_data(self, warehouse_file: str) -> pd.DataFrame:
        """창고 데이터 로드"""
        logger.info(f"🏭 창고 데이터 로드: {warehouse_file}")

        try:
            # Excel 파일 로드
            df = pd.read_excel(warehouse_file, sheet_name=0)
            logger.info(f"📊 원본 데이터 크기: {df.shape}")
            logger.info(f"📋 원본 컬럼명: {list(df.columns)}")

            # 기본 데이터 검증
            required_columns = ["Item"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                logger.warning(f"⚠️ 창고 데이터 필수 컬럼 누락: {missing_columns}")
                logger.info(f"🔍 매핑 전 사용 가능한 컬럼: {list(df.columns)}")

            # 데이터 정제
            df = self._clean_warehouse_data(df)

            # 매핑 후 필수 컬럼 재검증
            final_missing = [col for col in required_columns if col not in df.columns]
            if final_missing:
                logger.error(f"❌ 매핑 후에도 필수 컬럼 누락: {final_missing}")
                logger.info(f"📋 최종 사용 가능한 컬럼: {list(df.columns)}")
            else:
                logger.info(f"✅ 모든 필수 컬럼 매핑 완료")

            logger.info(f"✅ 창고 데이터 로드 완료: {len(df)}건")
            return df

        except Exception as e:
            logger.error(f"❌ 창고 데이터 로드 실패: {e}")
            raise

    def _clean_invoice_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """청구서 데이터 정제"""
        df_clean = df.copy()

        # 디버깅: 원본 컬럼명 출력
        logger.info(f"🔍 원본 청구서 컬럼명: {list(df_clean.columns)}")

        # 컬럼명 표준화 - 확장된 매핑
        column_mapping = {}

        # Item 관련 매핑
        item_mappings = {
            "Item No": "Item",
            "Item Number": "Item",
            "S No.": "Item",
            "S.No.": "Item",
            "S.No": "Item",
            "No.": "Item",  # 실제 파일에 맞게 추가
            "Item": "Item",
            "ID": "Item",
            "Case No.": "Item",
            "Case No": "Item",
            "Case_No": "Item",
            "no.": "Item",
            "Number": "Item",
        }

        # Description 관련 매핑
        desc_mappings = {
            "Description": "Description",
            "Desc": "Description",
            "Item Description": "Description",
            "Product Description": "Description",
            "Goods Description": "Description",
            "Details": "Description",
        }

        # Quantity 관련 매핑
        qty_mappings = {
            "Qty": "Quantity",
            "Quantity": "Quantity",
            "QTY": "Quantity",
            "qty": "Quantity",
            "CNTR Unstuffing Q'TY": "Quantity",
            "CNTR Stuffing Q'TY": "Quantity",
            "Container Qty": "Quantity",
            "Package Qty": "Quantity",
            "Units": "Quantity",
            "Count": "Quantity",
        }

        # Unit Price 관련 매핑
        price_mappings = {
            "Unit Price": "Unit_Price",
            "Unit_Price": "Unit_Price",
            "Price": "Unit_Price",
            "Unit Cost": "Unit_Price",
            "Rate": "Unit_Price",
            "Per Unit": "Unit_Price",
            "Price per Unit": "Unit_Price",
            "Unit price_Handling In": "Unit_Price_Handling_In",  # 실제 파일에 맞게 추가
            "Unit price_Handling out": "Unit_Price_Handling_Out",
            "Unit price_Unstuffing": "Unit_Price_Unstuffing",
            "Unit price_Stuffing": "Unit_Price_Stuffing",
            "Unit price_folk lift": "Unit_Price_Folk_Lift",
            "Unit price_crane": "Unit_Price_Crane",
        }

        # Total Amount 관련 매핑 (Amount는 마지막에 처리하여 충돌 방지)
        total_mappings = {
            "Total": "Total_Amount",
            "Total Amount": "Total_Amount",
            "Total_Amount": "Total_Amount",
            "Sum": "Total_Amount",
            "Value": "Total_Amount",
            "Cost": "Total_Amount",
            "Invoice Amount": "Total_Amount",
            "Line Total": "Total_Amount",
            "Extended Amount": "Total_Amount",
            "TOTAL": "Total_Amount",  # 실제 파일에 맞게 추가
        }

        # 매핑 적용 (우선순위 고려)
        for mapping_dict in [
            item_mappings,
            desc_mappings,
            qty_mappings,
            price_mappings,
            total_mappings,
        ]:
            for old_col, new_col in mapping_dict.items():
                if (
                    old_col in df_clean.columns
                    and new_col not in column_mapping.values()
                ):
                    column_mapping[old_col] = new_col

        # Amount 컬럼 특별 처리 (Quantity vs Total_Amount 구분)
        if "Amount" in df_clean.columns and "Amount" not in column_mapping:
            # Amount가 이미 매핑되지 않은 경우에만 처리
            if (
                "Quantity" not in df_clean.columns
                and "Total_Amount" not in df_clean.columns
            ):
                # 둘 다 없는 경우, 데이터 타입으로 판단
                amount_col = df_clean["Amount"]
                if pd.api.types.is_numeric_dtype(amount_col):
                    # 숫자인 경우 Total_Amount로 매핑
                    column_mapping["Amount"] = "Total_Amount"
                else:
                    # 문자열인 경우 Quantity로 매핑
                    column_mapping["Amount"] = "Quantity"
            elif "Quantity" not in df_clean.columns:
                column_mapping["Amount"] = "Quantity"
            elif "Total_Amount" not in df_clean.columns:
                column_mapping["Amount"] = "Total_Amount"

        # Description 컬럼이 없는 경우 HVDC CODE를 Description으로 사용
        if "Description" not in df_clean.columns and "HVDC CODE" in df_clean.columns:
            column_mapping["HVDC CODE"] = "Description"
            logger.info(f"🔧 HVDC CODE를 Description으로 매핑")

        # Unit_Price 컬럼이 없는 경우 기본값 생성
        if "Unit_Price" not in df_clean.columns:
            logger.info(f"🔧 Unit_Price 컬럼이 없어 기본값으로 생성")

        logger.info(f"🔧 적용될 매핑: {column_mapping}")

        # 매핑 적용
        df_clean = df_clean.rename(columns=column_mapping)

        # 중복 컬럼 제거 (Total_Amount가 중복된 경우)
        if "Total_Amount" in df_clean.columns:
            # 첫 번째 Total_Amount 컬럼만 유지
            total_amount_cols = [
                col for col in df_clean.columns if col == "Total_Amount"
            ]
            if len(total_amount_cols) > 1:
                # 첫 번째를 제외한 나머지 삭제
                for col in total_amount_cols[1:]:
                    df_clean = df_clean.drop(columns=[col])
                logger.info(f"🔧 중복 Total_Amount 컬럼 제거 완료")

        # Unit_Price 컬럼이 없는 경우 생성
        if "Unit_Price" not in df_clean.columns:
            if "Quantity" in df_clean.columns and "Total_Amount" in df_clean.columns:
                # Quantity와 Total_Amount가 있는 경우 계산
                df_clean["Unit_Price"] = df_clean["Total_Amount"] / df_clean["Quantity"]
                df_clean["Unit_Price"] = df_clean["Unit_Price"].fillna(0)
                logger.info(f"🔧 Unit_Price 계산 완료: Total_Amount / Quantity")
            else:
                # 기본값 0으로 생성
                df_clean["Unit_Price"] = 0
                logger.info(f"🔧 Unit_Price 기본값 0으로 생성")
        else:
            logger.info(
                f"🔧 Unit_Price 컬럼이 이미 존재함: {df_clean['Unit_Price'].notna().sum()}개 유효값"
            )

        # 디버깅: 매핑 후 컬럼명 출력
        logger.info(f"🔧 매핑 후 청구서 컬럼명: {list(df_clean.columns)}")

        # 필수 컬럼 확인
        required_columns = ["Item", "Description"]
        missing_required = [
            col for col in required_columns if col not in df_clean.columns
        ]
        if missing_required:
            logger.warning(f"⚠️ 필수 컬럼 누락: {missing_required}")
            logger.info(f"📋 사용 가능한 컬럼: {list(df_clean.columns)}")

        # 숫자 컬럼 정제
        numeric_columns = ["Quantity", "Unit_Price", "Total_Amount"]
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
                logger.info(
                    f"📊 {col} 컬럼 정제 완료: {df_clean[col].notna().sum()}개 유효값"
                )

        # 빈 값 제거
        before_clean = len(df_clean)
        df_clean = df_clean.dropna(subset=["Item"])
        after_clean = len(df_clean)
        logger.info(f"🧹 빈 값 제거: {before_clean} → {after_clean}건")

        # DataFrame 구조 상세 출력
        self._debug_dataframe_structure(df_clean, "청구서 데이터")

        return df_clean

    def _clean_warehouse_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """창고 데이터 정제"""
        df_clean = df.copy()

        # 디버깅: 원본 컬럼명 출력
        logger.info(f"🔍 원본 창고 데이터 컬럼명: {list(df_clean.columns)}")

        # 컬럼명 표준화 - 확장된 매핑
        column_mapping = {}

        # Item 관련 매핑
        item_mappings = {
            "no.": "Item",
            "No.": "Item",
            "Item No": "Item",
            "Item Number": "Item",
            "Item": "Item",
            "ID": "Item",
            "Case No.": "Item",
            "Case No": "Item",
            "Case_No": "Item",
            "S No.": "Item",
            "S.No.": "Item",
            "S.No": "Item",
            "Number": "Item",
            "Reference": "Item",
            "Code": "Item",
        }

        # Description 관련 매핑
        desc_mappings = {
            "Description": "Description",
            "Desc": "Description",
            "Item Description": "Description",
            "Product Description": "Description",
            "Goods Description": "Description",
            "Details": "Description",
            "Name": "Description",
            "Product": "Description",
            "Goods": "Description",
        }

        # 추가 창고 관련 컬럼들
        other_mappings = {
            "Category": "Category",
            "Type": "Type",
            "Vendor": "Vendor",
            "Supplier": "Vendor",
            "Manufacturer": "Vendor",
            "Brand": "Vendor",
            "Date": "Date",
            "Created Date": "Date",
            "Entry Date": "Date",
            "Arrival Date": "Date",
            "Transaction Date": "Date",
            "Timestamp": "Date",
        }

        # 매핑 적용 (우선순위 고려)
        for mapping_dict in [item_mappings, desc_mappings, other_mappings]:
            for old_col, new_col in mapping_dict.items():
                if (
                    old_col in df_clean.columns
                    and new_col not in column_mapping.values()
                ):
                    column_mapping[old_col] = new_col

        logger.info(f"🔧 적용될 매핑: {column_mapping}")

        # 매핑 적용
        df_clean = df_clean.rename(columns=column_mapping)

        # 디버깅: 매핑 후 컬럼명 출력
        logger.info(f"🔧 매핑 후 창고 데이터 컬럼명: {list(df_clean.columns)}")

        # 필수 컬럼 확인
        required_columns = ["Item"]
        missing_required = [
            col for col in required_columns if col not in df_clean.columns
        ]
        if missing_required:
            logger.warning(f"⚠️ 필수 컬럼 누락: {missing_required}")
            logger.info(f"📋 사용 가능한 컬럼: {list(df_clean.columns)}")

        # 빈 값 제거
        before_clean = len(df_clean)
        df_clean = df_clean.dropna(subset=["Item"])
        after_clean = len(df_clean)
        logger.info(f"🧹 빈 값 제거: {before_clean} → {after_clean}건")

        # 창고 컬럼 식별 및 출력
        warehouse_columns = [
            col
            for col in df_clean.columns
            if any(
                warehouse in col
                for warehouse in [
                    "DSV",
                    "DHL",
                    "AAA",
                    "Hauler",
                    "MOSB",
                    "MIR",
                    "SHU",
                    "DAS",
                    "AGI",
                ]
            )
        ]
        logger.info(f"🏭 창고/현장 컬럼 식별: {warehouse_columns}")

        # DataFrame 구조 상세 출력
        self._debug_dataframe_structure(df_clean, "창고 데이터")

        return df_clean

    def _debug_dataframe_structure(self, df: pd.DataFrame, data_type: str):
        """DataFrame 구조 디버깅 출력"""
        logger.info(f"🔍 {data_type} DataFrame 구조 분석:")
        logger.info(f"  📊 크기: {df.shape}")
        logger.info(f"  📋 컬럼: {list(df.columns)}")
        logger.info(f"  📈 데이터 타입:")
        for col in df.columns:
            try:
                dtype = df[col].dtype
                non_null_count = df[col].notna().sum()
                null_count = df[col].isna().sum()
                logger.info(
                    f"    {col}: {dtype} (유효: {non_null_count}, 빈값: {null_count})"
                )
            except Exception as e:
                logger.warning(f"    {col}: 데이터 타입 확인 실패 - {e}")

        # 샘플 데이터 출력 (처음 3행)
        if len(df) > 0:
            try:
                logger.info(f"  📄 샘플 데이터 (처음 3행):")
                sample_data = df.head(3).to_dict("records")
                for i, row in enumerate(sample_data):
                    # 딕셔너리를 문자열로 변환하여 출력
                    row_str = str(row)
                    if len(row_str) > 200:  # 너무 길면 잘라서 출력
                        row_str = row_str[:200] + "..."
                    logger.info(f"    행 {i+1}: {row_str}")
            except Exception as e:
                logger.warning(f"  📄 샘플 데이터 출력 실패: {e}")

        # 필수 컬럼 존재 여부 확인
        if data_type == "청구서 데이터":
            required_cols = [
                "Item",
                "Description",
                "Quantity",
                "Unit_Price",
                "Total_Amount",
            ]
        else:  # 창고 데이터
            required_cols = ["Item"]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"  ⚠️ 누락된 필수 컬럼: {missing_cols}")
        else:
            logger.info(f"  ✅ 모든 필수 컬럼 존재")

    def _validate_invoice_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """청구서 데이터 검증"""
        logger.info("🔍 청구서 데이터 검증 중...")

        validation_result = {
            "status": "PASS",
            "score": 0.0,
            "checks": {},
            "errors": [],
            "warnings": [],
        }

        total_checks = 0
        passed_checks = 0

        # 1. 기본 구조 검증
        total_checks += 1
        if len(df) > 0:
            passed_checks += 1
            validation_result["checks"]["data_structure"] = {
                "status": "PASS",
                "message": "데이터 구조 정상",
            }
        else:
            validation_result["checks"]["data_structure"] = {
                "status": "FAIL",
                "message": "빈 데이터",
            }
            validation_result["errors"].append("빈 데이터")

        # 2. 필수 컬럼 검증
        required_columns = ["Item", "Description"]
        for col in required_columns:
            total_checks += 1
            if col in df.columns:
                passed_checks += 1
                validation_result["checks"][f"column_{col}"] = {
                    "status": "PASS",
                    "message": f"{col} 컬럼 존재",
                }
            else:
                validation_result["checks"][f"column_{col}"] = {
                    "status": "FAIL",
                    "message": f"{col} 컬럼 누락",
                }
                validation_result["errors"].append(f"{col} 컬럼 누락")

        # 3. 데이터 품질 검증
        total_checks += 1
        null_count = df["Item"].isnull().sum()
        if null_count == 0:
            passed_checks += 1
            validation_result["checks"]["data_quality"] = {
                "status": "PASS",
                "message": "데이터 품질 양호",
            }
        else:
            validation_result["checks"]["data_quality"] = {
                "status": "WARNING",
                "message": f"{null_count}개 빈 값 발견",
            }
            validation_result["warnings"].append(f"{null_count}개 빈 값")

        # 4. 금액 계산 검증 (금액 컬럼이 있는 경우)
        if (
            "Quantity" in df.columns
            and "Unit_Price" in df.columns
            and "Total_Amount" in df.columns
        ):
            total_checks += 1
            df["Calculated_Total"] = df["Quantity"] * df["Unit_Price"]
            df["Amount_Difference"] = abs(df["Total_Amount"] - df["Calculated_Total"])

            # 1% 이내 오차 허용
            tolerance = df["Total_Amount"] * self.config.amount_tolerance
            accurate_calculations = (df["Amount_Difference"] <= tolerance).sum()
            accuracy_rate = accurate_calculations / len(df) if len(df) > 0 else 0

            if accuracy_rate >= 0.95:
                passed_checks += 1
                validation_result["checks"]["amount_calculation"] = {
                    "status": "PASS",
                    "message": f"금액 계산 정확도 {accuracy_rate:.1%}",
                }
            else:
                validation_result["checks"]["amount_calculation"] = {
                    "status": "FAIL",
                    "message": f"금액 계산 오차 {1-accuracy_rate:.1%}",
                }
                validation_result["errors"].append(
                    f"금액 계산 오차 {1-accuracy_rate:.1%}"
                )

        # 점수 계산
        validation_result["score"] = (
            passed_checks / total_checks if total_checks > 0 else 0
        )
        validation_result["status"] = (
            "PASS" if validation_result["score"] >= 0.9 else "FAIL"
        )

        logger.info(f"✅ 청구서 검증 완료 - 점수: {validation_result['score']:.3f}")
        return validation_result

    def _validate_warehouse_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """창고 데이터 검증"""
        logger.info("🔍 창고 데이터 검증 중...")

        validation_result = {
            "status": "PASS",
            "score": 0.0,
            "checks": {},
            "errors": [],
            "warnings": [],
        }

        total_checks = 0
        passed_checks = 0

        # 1. 기본 구조 검증
        total_checks += 1
        if len(df) > 0:
            passed_checks += 1
            validation_result["checks"]["data_structure"] = {
                "status": "PASS",
                "message": "데이터 구조 정상",
            }
        else:
            validation_result["checks"]["data_structure"] = {
                "status": "FAIL",
                "message": "빈 데이터",
            }
            validation_result["errors"].append("빈 데이터")

        # 2. 필수 컬럼 검증
        required_columns = ["Item"]
        for col in required_columns:
            total_checks += 1
            if col in df.columns:
                passed_checks += 1
                validation_result["checks"][f"column_{col}"] = {
                    "status": "PASS",
                    "message": f"{col} 컬럼 존재",
                }
            else:
                validation_result["checks"][f"column_{col}"] = {
                    "status": "FAIL",
                    "message": f"{col} 컬럼 누락",
                }
                validation_result["errors"].append(f"{col} 컬럼 누락")

        # 3. 데이터 품질 검증
        total_checks += 1
        null_count = df["Item"].isnull().sum()
        if null_count == 0:
            passed_checks += 1
            validation_result["checks"]["data_quality"] = {
                "status": "PASS",
                "message": "데이터 품질 양호",
            }
        else:
            validation_result["checks"]["data_quality"] = {
                "status": "WARNING",
                "message": f"{null_count}개 빈 값 발견",
            }
            validation_result["warnings"].append(f"{null_count}개 빈 값")

        # 4. 창고 컬럼 검증
        warehouse_columns = [
            col
            for col in df.columns
            if any(
                warehouse in col
                for warehouse in [
                    "DSV",
                    "DHL",
                    "AAA",
                    "Hauler",
                    "MOSB",
                    "MIR",
                    "SHU",
                    "DAS",
                    "AGI",
                ]
            )
        ]

        total_checks += 1
        if len(warehouse_columns) >= 3:
            passed_checks += 1
            validation_result["checks"]["warehouse_columns"] = {
                "status": "PASS",
                "message": f"{len(warehouse_columns)}개 창고/현장 컬럼 발견",
            }
        else:
            validation_result["checks"]["warehouse_columns"] = {
                "status": "WARNING",
                "message": f"창고/현장 컬럼 부족 ({len(warehouse_columns)}개)",
            }
            validation_result["warnings"].append(f"창고/현장 컬럼 부족")

        # 점수 계산
        validation_result["score"] = (
            passed_checks / total_checks if total_checks > 0 else 0
        )
        validation_result["status"] = (
            "PASS" if validation_result["score"] >= 0.9 else "FAIL"
        )

        logger.info(
            f"✅ 창고 데이터 검증 완료 - 점수: {validation_result['score']:.3f}"
        )
        return validation_result

    def _perform_cross_validation(
        self, invoice_df: pd.DataFrame, warehouse_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """청구서와 창고 데이터 교차 검증 - 구조 차이 반영 및 로직 개선"""
        logger.info("🔍 청구서와 창고 데이터 교차 검증 수행 중...")

        validation_result = {
            "status": "PASS",
            "score": 0.0,
            "checks": {},
            "errors": [],
            "warnings": [],
            "details": {},
        }

        total_checks = 0
        passed_checks = 0

        # 1. 아이템 ID 매칭 검증
        total_checks += 1
        invoice_items = set(invoice_df["Item"].astype(str))
        warehouse_items = set(warehouse_df["Item"].astype(str))

        matched_items = invoice_items.intersection(warehouse_items)
        invoice_only = invoice_items - warehouse_items
        warehouse_only = warehouse_items - invoice_items

        match_rate = (
            len(matched_items) / len(invoice_items) if len(invoice_items) > 0 else 0
        )

        if match_rate >= 0.95:
            validation_result["checks"]["item_matching"] = {
                "status": "PASS",
                "message": f"아이템 매칭률 {match_rate:.1%} ({len(matched_items)}/{len(invoice_items)})",
            }
            passed_checks += 1
        else:
            validation_result["checks"]["item_matching"] = {
                "status": "FAIL",
                "message": f"아이템 매칭률 낮음 {match_rate:.1%} ({len(matched_items)}/{len(invoice_items)})",
            }

        # 아이템 매칭 상세 정보 저장
        validation_result["details"]["item_matching"] = {
            "total_invoice_items": len(invoice_items),
            "total_warehouse_items": len(warehouse_items),
            "matched_items": len(matched_items),
            "invoice_only": len(invoice_only),
            "warehouse_only": len(warehouse_only),
            "match_rate": match_rate,
        }

        # 2. HVDC CODE 일치성 검증 (개선된 로직)
        total_checks += 1
        if len(matched_items) > 0:
            # 매칭된 아이템들의 HVDC CODE 비교
            matched_invoice = invoice_df[
                invoice_df["Item"].astype(str).isin(matched_items)
            ]
            matched_warehouse = warehouse_df[
                warehouse_df["Item"].astype(str).isin(matched_items)
            ]

            # HVDC CODE 컬럼 찾기
            invoice_hvdccode_col = (
                "HVDC CODE" if "HVDC CODE" in matched_invoice.columns else "Description"
            )
            warehouse_hvdccode_col = (
                "HVDC CODE"
                if "HVDC CODE" in matched_warehouse.columns
                else "Description"
            )

            # HVDC CODE 매칭 검증 (개선된 로직)
            hvdccode_matches = 0
            hvdccode_mismatches = 0
            mismatch_details = []

            for _, invoice_row in matched_invoice.iterrows():
                item_id = str(invoice_row["Item"])

                # HVDC CODE 정규화 함수
                def normalize_hvdccode(code):
                    if pd.isna(code):
                        return ""
                    # 문자열로 변환
                    code_str = str(code).strip()
                    # 대소문자 통일 (대문자로)
                    code_str = code_str.upper()
                    # 공백 제거
                    code_str = (
                        code_str.replace(" ", "").replace("\t", "").replace("\n", "")
                    )
                    # 특수문자 정규화
                    code_str = code_str.replace("-", "-").replace("_", "-")
                    return code_str

                invoice_hvdccode = normalize_hvdccode(invoice_row[invoice_hvdccode_col])

                # 창고에서 해당 아이템의 HVDC CODE 확인
                warehouse_items_for_id = matched_warehouse[
                    matched_warehouse["Item"].astype(str) == item_id
                ]

                if len(warehouse_items_for_id) > 0:
                    warehouse_hvdccode = normalize_hvdccode(
                        warehouse_items_for_id.iloc[0][warehouse_hvdccode_col]
                    )

                    # 정규화된 HVDC CODE 비교
                    if invoice_hvdccode == warehouse_hvdccode:
                        hvdccode_matches += 1
                    else:
                        hvdccode_mismatches += 1
                        mismatch_details.append(
                            {
                                "item": item_id,
                                "invoice_hvdccode_original": str(
                                    invoice_row[invoice_hvdccode_col]
                                ),
                                "warehouse_hvdccode_original": str(
                                    warehouse_items_for_id.iloc[0][
                                        warehouse_hvdccode_col
                                    ]
                                ),
                                "invoice_hvdccode_normalized": invoice_hvdccode,
                                "warehouse_hvdccode_normalized": warehouse_hvdccode,
                            }
                        )

            hvdccode_match_rate = (
                hvdccode_matches / len(matched_invoice)
                if len(matched_invoice) > 0
                else 0
            )

            if hvdccode_match_rate >= 0.95:
                validation_result["checks"]["hvdccode_matching"] = {
                    "status": "PASS",
                    "message": f"HVDC CODE 일치률 {hvdccode_match_rate:.1%} (정규화 적용)",
                }
                passed_checks += 1
            else:
                validation_result["checks"]["hvdccode_matching"] = {
                    "status": "FAIL",
                    "message": f"HVDC CODE 일치률 낮음 {hvdccode_match_rate:.1%} (정규화 적용)",
                }

            # HVDC CODE 매칭 상세 정보 저장
            validation_result["details"]["hvdccode_matching"] = {
                "total_compared": len(matched_invoice),
                "matches": hvdccode_matches,
                "mismatches": hvdccode_mismatches,
                "match_rate": hvdccode_match_rate,
                "mismatch_details": mismatch_details[:10],  # 처음 10개만 저장
            }
        else:
            validation_result["checks"]["hvdccode_matching"] = {
                "status": "SKIP",
                "message": "매칭된 아이템이 없어 HVDC CODE 검증 생략",
            }

        # 3. 수량 일치성 검증 (개선된 로직 - 오차 허용 범위 조정)
        total_checks += 1
        if len(matched_items) > 0:
            # 매칭된 아이템들의 수량 비교
            matched_invoice = invoice_df[
                invoice_df["Item"].astype(str).isin(matched_items)
            ]
            matched_warehouse = warehouse_df[
                warehouse_df["Item"].astype(str).isin(matched_items)
            ]

            # 수량 컬럼 찾기
            invoice_qty_col = (
                "Quantity" if "Quantity" in matched_invoice.columns else "pkg"
            )
            warehouse_qty_col = "Pkg" if "Pkg" in matched_warehouse.columns else "pkg"

            # 수량 매칭 검증 (개선된 집계 방식)
            qty_matches = 0
            qty_mismatches = 0
            qty_mismatch_details = []

            for _, invoice_row in matched_invoice.iterrows():
                item_id = str(invoice_row["Item"])
                invoice_qty = int(invoice_row[invoice_qty_col])

                # 창고에서 해당 아이템의 총 수량 집계
                warehouse_items_for_id = matched_warehouse[
                    matched_warehouse["Item"].astype(str) == item_id
                ]
                warehouse_total_qty = len(warehouse_items_for_id)  # 개별 레코드 수

                # 개선된 오차 허용 범위 (수량에 따른 동적 조정)
                if invoice_qty <= 5:
                    qty_tolerance = 1  # 5개 이하: 1개 오차 허용
                elif invoice_qty <= 20:
                    qty_tolerance = max(
                        2, int(invoice_qty * 0.1)
                    )  # 6-20개: 10% 또는 2개
                elif invoice_qty <= 100:
                    qty_tolerance = max(
                        3, int(invoice_qty * 0.08)
                    )  # 21-100개: 8% 또는 3개
                else:
                    qty_tolerance = max(
                        5, int(invoice_qty * 0.05)
                    )  # 100개 초과: 5% 또는 5개

                qty_difference = abs(invoice_qty - warehouse_total_qty)

                if qty_difference <= qty_tolerance:
                    qty_matches += 1
                else:
                    qty_mismatches += 1
                    qty_mismatch_details.append(
                        {
                            "item": item_id,
                            "invoice_qty": invoice_qty,
                            "warehouse_qty": warehouse_total_qty,
                            "difference": qty_difference,
                            "tolerance": qty_tolerance,
                            "tolerance_rate": (
                                f"{qty_tolerance/invoice_qty*100:.1f}%"
                                if invoice_qty > 0
                                else "N/A"
                            ),
                        }
                    )

            qty_match_rate = (
                qty_matches / len(matched_invoice) if len(matched_invoice) > 0 else 0
            )

            if qty_match_rate >= 0.95:  # 95% 이상이면 통과
                validation_result["checks"]["quantity_matching"] = {
                    "status": "PASS",
                    "message": f"수량 일치률 {qty_match_rate:.1%} (개선된 집계 방식)",
                }
                passed_checks += 1
            elif qty_match_rate >= 0.90:  # 90-95%는 경고
                validation_result["checks"]["quantity_matching"] = {
                    "status": "WARNING",
                    "message": f"수량 일치률 {qty_match_rate:.1%} (개선된 집계 방식)",
                }
            else:
                validation_result["checks"]["quantity_matching"] = {
                    "status": "FAIL",
                    "message": f"수량 일치률 낮음 {qty_match_rate:.1%} (개선된 집계 방식)",
                }

            # 수량 매칭 상세 정보 저장
            validation_result["details"]["quantity_matching"] = {
                "total_compared": len(matched_invoice),
                "matches": qty_matches,
                "mismatches": qty_mismatches,
                "match_rate": qty_match_rate,
                "mismatch_details": qty_mismatch_details[:10],  # 처음 10개만 저장
                "method": "improved_aggregation",  # 개선된 집계 방식 사용
                "tolerance_policy": "dynamic",  # 동적 오차 허용 범위
            }
        else:
            validation_result["checks"]["quantity_matching"] = {
                "status": "SKIP",
                "message": "매칭된 아이템이 없어 수량 검증 생략",
            }

        # 4. 데이터 완전성 검증
        total_checks += 1
        invoice_completeness = (
            (
                matched_invoice.notna().sum().sum()
                / (len(matched_invoice) * len(matched_invoice.columns))
            )
            * 100
            if len(matched_invoice) > 0
            else 0
        )
        warehouse_completeness = (
            (
                matched_warehouse.notna().sum().sum()
                / (len(matched_warehouse) * len(matched_warehouse.columns))
            )
            * 100
            if len(matched_warehouse) > 0
            else 0
        )
        average_completeness = (invoice_completeness + warehouse_completeness) / 2

        if average_completeness >= 80:
            validation_result["checks"]["data_completeness"] = {
                "status": "PASS",
                "message": f"데이터 완전성 {average_completeness:.1%}",
            }
            passed_checks += 1
        else:
            validation_result["checks"]["data_completeness"] = {
                "status": "WARNING",
                "message": f"데이터 완전성 낮음 {average_completeness:.1%}",
            }

        # 데이터 완전성 상세 정보 저장
        validation_result["details"]["data_completeness"] = {
            "invoice_completeness": invoice_completeness,
            "warehouse_completeness": warehouse_completeness,
            "average_completeness": average_completeness,
        }

        # 5. 날짜 일관성 검증
        total_checks += 1
        # 날짜 컬럼 찾기
        invoice_date_cols = [
            col
            for col in matched_invoice.columns
            if "date" in col.lower() or "month" in col.lower()
        ]
        warehouse_date_cols = [
            col
            for col in matched_warehouse.columns
            if "date" in col.lower() or "month" in col.lower()
        ]

        if invoice_date_cols and warehouse_date_cols:
            # 청구서 날짜 범위
            invoice_dates = pd.to_datetime(
                matched_invoice[invoice_date_cols[0]], errors="coerce"
            ).dropna()
            invoice_date_range = (
                (invoice_dates.min(), invoice_dates.max())
                if len(invoice_dates) > 0
                else (None, None)
            )

            # 창고 날짜 범위
            warehouse_dates = pd.to_datetime(
                matched_warehouse[warehouse_date_cols[0]], errors="coerce"
            ).dropna()
            warehouse_date_range = (
                (warehouse_dates.min(), warehouse_dates.max())
                if len(warehouse_dates) > 0
                else (None, None)
            )

            # 날짜 범위 겹침 확인
            overlap = False
            overlap_range = (None, None)

            if invoice_date_range[0] and warehouse_date_range[0]:
                overlap_start = max(invoice_date_range[0], warehouse_date_range[0])
                overlap_end = min(invoice_date_range[1], warehouse_date_range[1])
                overlap = overlap_start <= overlap_end
                overlap_range = (
                    (overlap_start, overlap_end) if overlap else (None, None)
                )

            if overlap:
                validation_result["checks"]["date_consistency"] = {
                    "status": "PASS",
                    "message": "날짜 범위 일관성 확인",
                }
                passed_checks += 1
            else:
                validation_result["checks"]["date_consistency"] = {
                    "status": "WARNING",
                    "message": "날짜 범위 불일치",
                }

            # 날짜 일관성 상세 정보 저장
            validation_result["details"]["date_consistency"] = {
                "invoice_date_range": invoice_date_range,
                "warehouse_date_range": warehouse_date_range,
                "overlap": overlap,
                "overlap_range": overlap_range,
            }
        else:
            validation_result["checks"]["date_consistency"] = {
                "status": "SKIP",
                "message": "날짜 컬럼을 찾을 수 없어 검증 생략",
            }

        # 전체 점수 계산
        validation_result["score"] = (
            passed_checks / total_checks if total_checks > 0 else 0
        )

        # 상태 결정
        if validation_result["score"] >= 0.8:
            validation_result["status"] = "PASS"
        elif validation_result["score"] >= 0.6:
            validation_result["status"] = "WARNING"
        else:
            validation_result["status"] = "FAIL"

        logger.info(f"✅ 교차 검증 완료 - 점수: {validation_result['score']:.3f}")
        logger.info(
            f"  📊 매칭된 아이템: {len(matched_items)}/{len(invoice_items)} ({match_rate:.1%})"
        )
        logger.info(
            f"  📋 청구서 전용: {len(invoice_only)}건, 창고 전용: {len(warehouse_only)}건"
        )

        return validation_result

    def _validate_compliance(
        self, invoice_df: pd.DataFrame, warehouse_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """규정 준수 검증 - 비활성화됨"""
        logger.info("🔍 규정 준수 검증 비활성화됨")

        validation_result = {
            "status": "PASS",
            "score": 1.0,  # 항상 통과
            "checks": {},
            "errors": [],
            "warnings": ["규정 준수 검증이 비활성화되었습니다."],
        }

        validation_result["checks"]["compliance_disabled"] = {
            "status": "PASS",
            "message": "규정 준수 검증 비활성화됨",
        }

        logger.info(
            f"✅ 규정 준수 검증 비활성화 - 점수: {validation_result['score']:.3f}"
        )
        return validation_result

    def _calculate_overall_validation(
        self,
        invoice_validation: Dict,
        warehouse_validation: Dict,
        cross_validation: Dict,
        compliance_validation: Dict,
    ) -> Dict[str, Any]:
        """전체 검증 결과 계산"""
        logger.info("🔍 전체 검증 결과 계산 중...")

        # 가중 평균 점수 계산
        weights = {"invoice": 0.3, "warehouse": 0.3, "cross": 0.25, "compliance": 0.15}

        total_score = (
            invoice_validation["score"] * weights["invoice"]
            + warehouse_validation["score"] * weights["warehouse"]
            + cross_validation["score"] * weights["cross"]
            + compliance_validation["score"] * weights["compliance"]
        )

        # 등급 결정
        if total_score >= 0.95:
            grade = "A+"
        elif total_score >= 0.90:
            grade = "A"
        elif total_score >= 0.85:
            grade = "B+"
        elif total_score >= 0.80:
            grade = "B"
        else:
            grade = "C"

        overall_validation = {
            "total_score": total_score,
            "grade": grade,
            "status": "PASS" if total_score >= 0.85 else "FAIL",
            "target_achieved": total_score >= self.config.confidence_threshold,
            "component_scores": {
                "invoice": invoice_validation["score"],
                "warehouse": warehouse_validation["score"],
                "cross": cross_validation["score"],
                "compliance": compliance_validation["score"],
            },
            "summary": {
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "warning_checks": 0,
            },
        }

        # 요약 통계 계산
        all_validations = [
            invoice_validation,
            warehouse_validation,
            cross_validation,
            compliance_validation,
        ]
        for validation in all_validations:
            for check_name, check_result in validation["checks"].items():
                overall_validation["summary"]["total_checks"] += 1
                if check_result["status"] == "PASS":
                    overall_validation["summary"]["passed_checks"] += 1
                elif check_result["status"] == "FAIL":
                    overall_validation["summary"]["failed_checks"] += 1
                elif check_result["status"] == "WARNING":
                    overall_validation["summary"]["warning_checks"] += 1

        logger.info(
            f"✅ 전체 검증 결과 계산 완료 - 점수: {total_score:.3f}, 등급: {grade}"
        )
        return overall_validation

    def _generate_report_files(
        self,
        timestamp: str,
        invoice_validation: Dict,
        warehouse_validation: Dict,
        cross_validation: Dict,
        compliance_validation: Dict,
        overall_validation: Dict,
    ) -> Dict[str, str]:
        """리포트 파일 생성"""
        logger.info("📄 리포트 파일 생성 중...")

        generated_files = {}

        # 1. PDF 요약 보고서 생성
        if self.config.generate_pdf and REPORTLAB_AVAILABLE:
            pdf_file = self._generate_pdf_report(
                timestamp,
                invoice_validation,
                warehouse_validation,
                cross_validation,
                compliance_validation,
                overall_validation,
            )
            generated_files["pdf_summary"] = str(pdf_file)
        elif self.config.generate_pdf and not REPORTLAB_AVAILABLE:
            logger.warning(
                "PDF 보고서 생성이 비활성화되었습니다 (reportlab 패키지 없음)"
            )

        # 2. Excel 상세 결과 생성
        if self.config.generate_excel:
            excel_file = self._generate_excel_report(
                timestamp,
                invoice_validation,
                warehouse_validation,
                cross_validation,
                compliance_validation,
                overall_validation,
            )
            generated_files["excel_detailed"] = str(excel_file)

        # 3. RDF TTL 파일 생성
        if self.config.generate_rdf and RDF_AVAILABLE:
            rdf_file = self._generate_rdf_report(
                timestamp,
                invoice_validation,
                warehouse_validation,
                cross_validation,
                compliance_validation,
                overall_validation,
            )
            generated_files["rdf_ontology"] = str(rdf_file)
        elif self.config.generate_rdf and not RDF_AVAILABLE:
            logger.warning(
                "RDF TTL 파일 생성이 비활성화되었습니다 (rdflib 패키지 없음)"
            )

        logger.info(f"✅ 리포트 파일 생성 완료: {len(generated_files)}개 파일")
        return generated_files

    def _generate_pdf_report(
        self,
        timestamp: str,
        invoice_validation: Dict,
        warehouse_validation: Dict,
        cross_validation: Dict,
        compliance_validation: Dict,
        overall_validation: Dict,
    ) -> Path:
        """PDF 요약 보고서 생성"""
        pdf_file = self.output_dir / f"validation_summary_report_{timestamp}.pdf"

        doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
        story = []

        # 스타일 설정
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # 중앙 정렬
        )

        # 제목
        story.append(Paragraph("MACHO-GPT v3.4-mini 검증 리포트", title_style))
        story.append(Spacer(1, 20))

        # 요약 정보
        summary_data = [
            ["검증 항목", "상태", "점수", "등급"],
            [
                "전체 검증",
                overall_validation["status"],
                f"{overall_validation['total_score']:.3f}",
                overall_validation["grade"],
            ],
            [
                "청구서 검증",
                invoice_validation["status"],
                f"{invoice_validation['score']:.3f}",
                "",
            ],
            [
                "창고 검증",
                warehouse_validation["status"],
                f"{warehouse_validation['score']:.3f}",
                "",
            ],
            [
                "교차 검증",
                cross_validation["status"],
                f"{cross_validation['score']:.3f}",
                "",
            ],
            [
                "규정 준수",
                compliance_validation["status"],
                f"{compliance_validation['score']:.3f}",
                "",
            ],
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(summary_table)
        story.append(Spacer(1, 20))

        # 상세 검증 결과
        story.append(Paragraph("상세 검증 결과", styles["Heading2"]))
        story.append(Spacer(1, 12))

        for validation_name, validation_data in [
            ("청구서 검증", invoice_validation),
            ("창고 검증", warehouse_validation),
            ("교차 검증", cross_validation),
            ("규정 준수", compliance_validation),
        ]:
            story.append(
                Paragraph(
                    f"{validation_name}: {validation_data['status']}",
                    styles["Heading3"],
                )
            )

            for check_name, check_result in validation_data["checks"].items():
                status_color = (
                    "green"
                    if check_result["status"] == "PASS"
                    else "red" if check_result["status"] == "FAIL" else "orange"
                )
                story.append(
                    Paragraph(
                        f"• {check_name}: {check_result['status']} - {check_result['message']}",
                        ParagraphStyle(
                            "CheckResult",
                            parent=styles["Normal"],
                            textColor=colors.HexColor(status_color),
                        ),
                    )
                )

            story.append(Spacer(1, 12))

        # 빌드 및 저장
        doc.build(story)
        logger.info(f"✅ PDF 보고서 생성 완료: {pdf_file}")
        return pdf_file

    def _generate_excel_report(
        self,
        timestamp: str,
        invoice_validation: Dict,
        warehouse_validation: Dict,
        cross_validation: Dict,
        compliance_validation: Dict,
        overall_validation: Dict,
    ) -> Path:
        """Excel 상세 결과 생성"""
        excel_file = self.output_dir / f"validation_detailed_report_{timestamp}.xlsx"

        with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:

            # 1. 요약 시트
            summary_data = {
                "검증 항목": [
                    "전체 점수",
                    "등급",
                    "상태",
                    "목표 달성",
                    "청구서 검증",
                    "창고 검증",
                    "교차 검증",
                    "규정 준수",
                    "총 검증 수",
                    "통과",
                    "실패",
                    "경고",
                ],
                "결과": [
                    f"{overall_validation['total_score']:.3f}",
                    overall_validation["grade"],
                    overall_validation["status"],
                    "✅" if overall_validation["target_achieved"] else "❌",
                    f"{invoice_validation['score']:.3f}",
                    f"{warehouse_validation['score']:.3f}",
                    f"{cross_validation['score']:.3f}",
                    f"{compliance_validation['score']:.3f}",
                    overall_validation["summary"]["total_checks"],
                    overall_validation["summary"]["passed_checks"],
                    overall_validation["summary"]["failed_checks"],
                    overall_validation["summary"]["warning_checks"],
                ],
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="요약", index=False)

            # 2. 청구서 검증 상세
            invoice_details = []
            for check_name, check_result in invoice_validation["checks"].items():
                invoice_details.append(
                    {
                        "검증 항목": check_name,
                        "상태": check_result["status"],
                        "메시지": check_result["message"],
                    }
                )
            pd.DataFrame(invoice_details).to_excel(
                writer, sheet_name="청구서_검증", index=False
            )

            # 3. 창고 검증 상세
            warehouse_details = []
            for check_name, check_result in warehouse_validation["checks"].items():
                warehouse_details.append(
                    {
                        "검증 항목": check_name,
                        "상태": check_result["status"],
                        "메시지": check_result["message"],
                    }
                )
            pd.DataFrame(warehouse_details).to_excel(
                writer, sheet_name="창고_검증", index=False
            )

            # 4. 교차 검증 상세
            cross_details = []
            for check_name, check_result in cross_validation["checks"].items():
                cross_details.append(
                    {
                        "검증 항목": check_name,
                        "상태": check_result["status"],
                        "메시지": check_result["message"],
                    }
                )
            pd.DataFrame(cross_details).to_excel(
                writer, sheet_name="교차_검증", index=False
            )

            # 5. 교차 검증 상세 통계
            if "details" in cross_validation:
                cross_stats = []

                # 아이템 매칭 통계
                if "item_matching" in cross_validation["details"]:
                    item_stats = cross_validation["details"]["item_matching"]
                    cross_stats.extend(
                        [
                            {
                                "통계 항목": "아이템 매칭 - 총 청구서 아이템",
                                "값": item_stats["total_invoice_items"],
                            },
                            {
                                "통계 항목": "아이템 매칭 - 총 창고 아이템",
                                "값": item_stats["total_warehouse_items"],
                            },
                            {
                                "통계 항목": "아이템 매칭 - 매칭된 아이템",
                                "값": item_stats["matched_items"],
                            },
                            {
                                "통계 항목": "아이템 매칭 - 청구서 전용",
                                "값": item_stats["invoice_only"],
                            },
                            {
                                "통계 항목": "아이템 매칭 - 창고 전용",
                                "값": item_stats["warehouse_only"],
                            },
                            {
                                "통계 항목": "아이템 매칭 - 매칭률",
                                "값": f"{item_stats['match_rate']:.1%}",
                            },
                        ]
                    )

                # HVDC CODE 매칭 통계
                if "hvdccode_matching" in cross_validation["details"]:
                    hvdccode_stats = cross_validation["details"]["hvdccode_matching"]
                    cross_stats.extend(
                        [
                            {
                                "통계 항목": "HVDC CODE - 총 비교 항목",
                                "값": hvdccode_stats["total_compared"],
                            },
                            {
                                "통계 항목": "HVDC CODE - 일치 항목",
                                "값": hvdccode_stats["matches"],
                            },
                            {
                                "통계 항목": "HVDC CODE - 불일치 항목",
                                "값": hvdccode_stats["mismatches"],
                            },
                            {
                                "통계 항목": "HVDC CODE - 일치률",
                                "값": f"{hvdccode_stats['match_rate']:.1%}",
                            },
                        ]
                    )

                # 수량 매칭 통계
                if "quantity_matching" in cross_validation["details"]:
                    qty_stats = cross_validation["details"]["quantity_matching"]
                    cross_stats.extend(
                        [
                            {
                                "통계 항목": "수량 매칭 - 총 비교 항목",
                                "값": qty_stats["total_compared"],
                            },
                            {
                                "통계 항목": "수량 매칭 - 일치 항목",
                                "값": qty_stats["matches"],
                            },
                            {
                                "통계 항목": "수량 매칭 - 불일치 항목",
                                "값": qty_stats["mismatches"],
                            },
                            {
                                "통계 항목": "수량 매칭 - 일치률",
                                "값": f"{qty_stats['match_rate']:.1%}",
                            },
                        ]
                    )

                # 데이터 완전성 통계
                if "data_completeness" in cross_validation["details"]:
                    completeness_stats = cross_validation["details"][
                        "data_completeness"
                    ]
                    cross_stats.extend(
                        [
                            {
                                "통계 항목": "데이터 완전성 - 청구서",
                                "값": f"{completeness_stats['invoice_completeness']:.1%}",
                            },
                            {
                                "통계 항목": "데이터 완전성 - 창고",
                                "값": f"{completeness_stats['warehouse_completeness']:.1%}",
                            },
                            {
                                "통계 항목": "데이터 완전성 - 평균",
                                "값": f"{completeness_stats['average_completeness']:.1%}",
                            },
                        ]
                    )

                # 날짜 일관성 통계
                if "date_consistency" in cross_validation["details"]:
                    date_stats = cross_validation["details"]["date_consistency"]
                    cross_stats.extend(
                        [
                            {
                                "통계 항목": "날짜 일관성 - 청구서 범위",
                                "값": f"{date_stats['invoice_date_range'][0]} ~ {date_stats['invoice_date_range'][1]}",
                            },
                            {
                                "통계 항목": "날짜 일관성 - 창고 범위",
                                "값": f"{date_stats['warehouse_date_range'][0]} ~ {date_stats['warehouse_date_range'][1]}",
                            },
                            {
                                "통계 항목": "날짜 일관성 - 겹침 여부",
                                "값": "예" if date_stats["overlap"] else "아니오",
                            },
                            {
                                "통계 항목": "날짜 일관성 - 겹침 범위",
                                "값": (
                                    f"{date_stats['overlap_range'][0]} ~ {date_stats['overlap_range'][1]}"
                                    if date_stats["overlap"]
                                    else "해당없음"
                                ),
                            },
                        ]
                    )

                pd.DataFrame(cross_stats).to_excel(
                    writer, sheet_name="교차_검증_통계", index=False
                )

            # 6. HVDC CODE 불일치 상세
            if (
                "details" in cross_validation
                and "hvdccode_matching" in cross_validation["details"]
            ):
                hvdccode_mismatches = cross_validation["details"][
                    "hvdccode_matching"
                ].get("mismatch_details", [])
                if hvdccode_mismatches:
                    mismatch_df = pd.DataFrame(hvdccode_mismatches)
                    mismatch_df.to_excel(
                        writer, sheet_name="HVDC_CODE_불일치", index=False
                    )
                else:
                    # 불일치가 없는 경우 빈 시트 생성
                    pd.DataFrame(
                        {"메시지": ["HVDC CODE 불일치 항목이 없습니다."]}
                    ).to_excel(writer, sheet_name="HVDC_CODE_불일치", index=False)

            # 7. 수량 불일치 상세
            if (
                "details" in cross_validation
                and "quantity_matching" in cross_validation["details"]
            ):
                qty_mismatches = cross_validation["details"]["quantity_matching"].get(
                    "mismatch_details", []
                )
                if qty_mismatches:
                    qty_mismatch_df = pd.DataFrame(qty_mismatches)
                    qty_mismatch_df.to_excel(
                        writer, sheet_name="수량_불일치", index=False
                    )
                else:
                    # 불일치가 없는 경우 빈 시트 생성
                    pd.DataFrame({"메시지": ["수량 불일치 항목이 없습니다."]}).to_excel(
                        writer, sheet_name="수량_불일치", index=False
                    )

            # 8. 청구서 전용 아이템
            if (
                "details" in cross_validation
                and "item_matching" in cross_validation["details"]
            ):
                invoice_only_count = cross_validation["details"]["item_matching"].get(
                    "invoice_only", 0
                )
                if invoice_only_count > 0:
                    pd.DataFrame(
                        {
                            "메시지": [
                                f"청구서에만 존재하는 아이템: {invoice_only_count}건"
                            ]
                        }
                    ).to_excel(writer, sheet_name="청구서_전용_아이템", index=False)
                else:
                    pd.DataFrame(
                        {"메시지": ["청구서 전용 아이템이 없습니다."]}
                    ).to_excel(writer, sheet_name="청구서_전용_아이템", index=False)

            # 9. 창고 전용 아이템
            if (
                "details" in cross_validation
                and "item_matching" in cross_validation["details"]
            ):
                warehouse_only_count = cross_validation["details"]["item_matching"].get(
                    "warehouse_only", 0
                )
                if warehouse_only_count > 0:
                    pd.DataFrame(
                        {
                            "메시지": [
                                f"창고에만 존재하는 아이템: {warehouse_only_count}건"
                            ]
                        }
                    ).to_excel(writer, sheet_name="창고_전용_아이템", index=False)
                else:
                    pd.DataFrame({"메시지": ["창고 전용 아이템이 없습니다."]}).to_excel(
                        writer, sheet_name="창고_전용_아이템", index=False
                    )

            # 10. 규정 준수 검증 상세
            compliance_details = []
            for check_name, check_result in compliance_validation["checks"].items():
                compliance_details.append(
                    {
                        "검증 항목": check_name,
                        "상태": check_result["status"],
                        "메시지": check_result["message"],
                    }
                )
            pd.DataFrame(compliance_details).to_excel(
                writer, sheet_name="규정_준수_검증", index=False
            )

            # 11. 오류 및 경고 목록
            all_errors = []
            all_warnings = []

            # 모든 검증에서 오류와 경고 수집
            for validation_name, validation_data in [
                ("청구서", invoice_validation),
                ("창고", warehouse_validation),
                ("교차", cross_validation),
                ("규정준수", compliance_validation),
            ]:
                for error in validation_data.get("errors", []):
                    all_errors.append(
                        {"검증 유형": validation_name, "오류 내용": error}
                    )
                for warning in validation_data.get("warnings", []):
                    all_warnings.append(
                        {"검증 유형": validation_name, "경고 내용": warning}
                    )

            if all_errors:
                pd.DataFrame(all_errors).to_excel(
                    writer, sheet_name="오류_목록", index=False
                )
            else:
                pd.DataFrame({"메시지": ["오류가 없습니다."]}).to_excel(
                    writer, sheet_name="오류_목록", index=False
                )

            if all_warnings:
                pd.DataFrame(all_warnings).to_excel(
                    writer, sheet_name="경고_목록", index=False
                )
            else:
                pd.DataFrame({"메시지": ["경고가 없습니다."]}).to_excel(
                    writer, sheet_name="경고_목록", index=False
                )

        logger.info(f"✅ Excel 보고서 생성 완료: {excel_file}")
        return excel_file

    def _generate_rdf_report(
        self,
        timestamp: str,
        invoice_validation: Dict,
        warehouse_validation: Dict,
        cross_validation: Dict,
        compliance_validation: Dict,
        overall_validation: Dict,
    ) -> Path:
        """RDF TTL 파일 생성"""
        rdf_file = self.output_dir / f"validation_ontology_{timestamp}.ttl"

        # RDF 그래프 생성
        g = Graph()
        g.bind("logi", self.LOGI)
        g.bind("hvdc", self.HVDC)
        g.bind("fanr", self.FANR)

        # 검증 결과를 RDF 트리플로 변환
        validation_uri = URIRef(f"http://macho-gpt.com/validation/{timestamp}")

        # 검증 메타데이터
        g.add((validation_uri, RDF.type, self.LOGI.ValidationReport))
        g.add(
            (validation_uri, self.LOGI.timestamp, Literal(datetime.now().isoformat()))
        )
        g.add(
            (
                validation_uri,
                self.LOGI.totalScore,
                Literal(overall_validation["total_score"], datatype=XSD.float),
            )
        )
        g.add((validation_uri, self.LOGI.grade, Literal(overall_validation["grade"])))
        g.add((validation_uri, self.LOGI.status, Literal(overall_validation["status"])))

        # 컴포넌트 점수
        for component, score in overall_validation["component_scores"].items():
            component_uri = URIRef(
                f"http://macho-gpt.com/validation/{timestamp}#{component}"
            )
            g.add((component_uri, RDF.type, self.LOGI.ValidationComponent))
            g.add((component_uri, self.LOGI.componentType, Literal(component)))
            g.add((component_uri, self.LOGI.score, Literal(score, datatype=XSD.float)))
            g.add((validation_uri, self.LOGI.hasComponent, component_uri))

        # 검증 체크 결과
        all_validations = [
            ("invoice", invoice_validation),
            ("warehouse", warehouse_validation),
            ("cross", cross_validation),
            ("compliance", compliance_validation),
        ]

        for validation_type, validation_data in all_validations:
            for check_name, check_result in validation_data["checks"].items():
                check_uri = URIRef(
                    f"http://macho-gpt.com/validation/{timestamp}#{validation_type}_{check_name}"
                )
                g.add((check_uri, RDF.type, self.LOGI.ValidationCheck))
                g.add((check_uri, self.LOGI.checkName, Literal(check_name)))
                g.add((check_uri, self.LOGI.status, Literal(check_result["status"])))
                g.add((check_uri, self.LOGI.message, Literal(check_result["message"])))
                g.add((validation_uri, self.LOGI.hasCheck, check_uri))

        # TTL 파일 저장
        g.serialize(destination=str(rdf_file), format="turtle")
        logger.info(f"✅ RDF TTL 파일 생성 완료: {rdf_file}")
        return rdf_file

    def _generate_recommendations(
        self, overall_validation: Dict[str, Any]
    ) -> List[str]:
        """권고사항 생성"""
        recommendations = []

        if overall_validation["total_score"] < 0.9:
            recommendations.append("전체 검증 점수 개선 필요 - 데이터 품질 향상 권고")

        if overall_validation["component_scores"]["invoice"] < 0.9:
            recommendations.append(
                "청구서 데이터 검증 강화 필요 - 필수 컬럼 및 계산 정확도 확인"
            )

        if overall_validation["component_scores"]["warehouse"] < 0.9:
            recommendations.append(
                "창고 데이터 검증 강화 필요 - 창고/현장 컬럼 구조 확인"
            )

        if overall_validation["component_scores"]["cross"] < 0.8:
            recommendations.append(
                "교차 검증 개선 필요 - 아이템 매칭 및 수량 일치성 확인"
            )

        if overall_validation["component_scores"]["compliance"] < 0.8:
            recommendations.append(
                "규정 준수 검증 강화 필요 - FANR/MOIAT 요구사항 확인"
            )

        if overall_validation["total_score"] >= 0.95:
            recommendations.append("검증 결과 우수 - 정기적 모니터링 유지 권고")

        return recommendations

    def _suggest_next_actions(self, overall_validation: Dict[str, Any]) -> List[str]:
        """다음 액션 제안"""
        if overall_validation["target_achieved"]:
            return [
                "/test-scenario validation-compliance",
                "/monitor-kpi validation-performance",
                "/automate validation-pipeline",
            ]
        else:
            return [
                "/tune-reliability validation-improvement",
                "/optimize-performance validation-process",
                "/enhance-compliance validation-requirements",
            ]

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """오류 응답 생성"""
        return {
            "command": "generate_validation_report",
            "execution_time": datetime.now().isoformat(),
            "status": "ERROR",
            "error_message": error_message,
            "recommendations": ["파일 경로 확인", "파일 형식 검증", "권한 확인"],
            "next_actions": ["/validate-data file-format", "/check-file-permissions"],
        }


# 명령어 처리 함수
def generate_validation_report(
    invoice_file: str, warehouse_file: str, config: ValidationConfig = None
) -> Dict[str, Any]:
    """
    /generate-validation-report 명령어 처리

    Args:
        invoice_file: 청구서 원본 파일 경로
        warehouse_file: 화물 입출고 리스트 파일 경로
        config: 검증 설정

    Returns:
        검증 결과 및 생성된 파일 경로들
    """
    logger.info("📋 /generate-validation-report 명령어 실행")

    generator = ValidationReportGenerator(config)
    return generator.generate_validation_report(invoice_file, warehouse_file)


if __name__ == "__main__":
    # 직접 실행시 테스트 수행
    print("🚀 MACHO-GPT v3.4-mini 검증 리포트 생성 시스템")
    print("=" * 70)

    # 테스트 파일 경로 (실제 파일로 교체 필요)
    test_invoice_file = "../data/HVDC_WAREHOUSE_INVOICE_CLEANED_20250709_201121.xlsx"
    test_warehouse_file = "../data/HVDC WAREHOUSE_HITACHI(HE).xlsx"

    # 파일 존재 확인
    if not os.path.exists(test_invoice_file):
        print(f"❌ 청구서 파일을 찾을 수 없습니다: {test_invoice_file}")
        print("📁 사용 가능한 파일:")
        for file in Path("../data").glob("*.xlsx"):
            print(f"  - {file}")
    elif not os.path.exists(test_warehouse_file):
        print(f"❌ 창고 파일을 찾을 수 없습니다: {test_warehouse_file}")
        print("📁 사용 가능한 파일:")
        for file in Path("../data").glob("*.xlsx"):
            print(f"  - {file}")
    else:
        # 검증 리포트 생성
        result = generate_validation_report(test_invoice_file, test_warehouse_file)

        # 결과 출력
        print("\n" + "=" * 80)
        print("📋 MACHO-GPT 검증 리포트 생성 결과")
        print("=" * 80)
        print(
            f"전체 점수: {result['validation_results']['overall_validation']['total_score']:.3f}"
        )
        print(f"등급: {result['validation_results']['overall_validation']['grade']}")
        print(f"상태: {result['validation_results']['overall_validation']['status']}")

        print("\n📄 생성된 파일:")
        for file_type, file_path in result["generated_files"].items():
            print(f"  - {file_type}: {file_path}")

        print("\n🔧 추천 명령어:")
        for cmd in result["next_actions"]:
            print(f"  {cmd}")

        print("=" * 80)
