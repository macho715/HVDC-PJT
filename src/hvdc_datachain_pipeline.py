"""
HVDC DataChain 통합 파이프라인
MACHO-GPT v3.4-mini for HVDC Project - Samsung C&T Logistics
DataChain을 활용한 물류 데이터 처리 및 분석 시스템
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# DataChain imports
import datachain as dc
from pathlib import Path
import pandas as pd
import numpy as np

# DataChain UDF 예외 처리
try:
    import datachain.sql.functions  # SIMD UDFs
except ImportError as e:
    logger.warning("DataChain UDF 확장 미로드: %s – KPI 일부 비활성화", e)

# HVDC specific imports
from logi_master_system import LogiMasterSystem
from warehouse_io_calculator import WarehouseIOCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("hvdc_datachain_pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """
    Returns the HVDC project root regardless of where the script is executed.
    Priority:
    1. ENV 'HVDC_ROOT'
    2. Locate 'HVDC_PJT/data' relative to this file
    3. Fallback to cwd() search upward
    """
    # ① 환경변수 우선
    env_root = os.getenv("HVDC_ROOT")
    if env_root:
        return Path(env_root).resolve()

    # ② 이 파일 기준 탐색
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "data").exists() and (parent / "src").exists():
            return parent

    # ③ CWD 부터 상위 탐색
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / "data").exists() and (parent / "src").exists():
            return parent

    raise FileNotFoundError("HVDC project root not found")


def get_data_dir() -> Path:
    root = get_project_root()
    return root / "data"


class HVDCDataChainPipeline:
    """
    HVDC 물류 데이터 처리 DataChain 파이프라인

    Features:
    - Excel 파일 자동 로드 및 전처리
    - 실시간 KPI 계산 및 모니터링
    - DataChain 기반 데이터 변환 및 분석
    - MACHO-GPT 통합 지원
    """

    def __init__(self, data_dir: str = "data", mode: str = "PRIME"):
        """
        HVDC DataChain 파이프라인 초기화

        Args:
            data_dir: 데이터 디렉토리 경로
            mode: MACHO-GPT containment mode (PRIME|ORACLE|ZERO|LATTICE|RHYTHM|COST-GUARD)
        """
        self.data_dir = Path(data_dir)
        self.mode = mode
        self.confidence_threshold = 0.90
        self.logi_master = LogiMasterSystem()
        self.warehouse_calculator = WarehouseIOCalculator()

        # DataChain 파이프라인 구성
        self.pipeline = self._build_pipeline()

        logger.info(f"HVDC DataChain Pipeline initialized in {mode} mode")

    def _build_pipeline(self) -> object:
        """
        DataChain 파이프라인 구축

        Returns:
            object: 구성된 데이터 파이프라인
        """
        try:
            # 1. Excel 파일 검색
            excel_files = list(self.data_dir.glob("*.xlsx"))

            if not excel_files:
                logger.warning(f"No Excel files found in {self.data_dir}")
                # 빈 DataChain 대신 None 반환하여 파이프라인 중단
                return None

            # 2. DataChain으로 Excel 파일들 읽기
            excel_source = dc.read_excel([str(f) for f in excel_files])

            # 3. 데이터 전처리 체인
            preprocess_chain = (
                excel_source.map(
                    self._validate_excel_structure, output=["valid", "data", "errors"]
                )
                .filter(lambda x: x[0])  # 유효한 데이터만 필터링
                .map(
                    self._extract_hvdc_data,
                    output=["warehouse_data", "invoice_data", "status_data"],
                )
                .map(
                    self._clean_and_validate_data,
                    output=["cleaned_data", "validation_report"],
                )
            )

            # 4. KPI 계산 체인
            kpi_chain = (
                preprocess_chain.map(
                    self._calculate_kpis, output=["kpi_results", "confidence_score"]
                )
                .filter(
                    lambda x: x[1] >= self.confidence_threshold
                )  # 신뢰도 임계값 필터링
                .map(self._generate_kpi_report, output=["kpi_report", "alerts"])
            )

            # 5. 물류 분석 체인
            logistics_chain = (
                kpi_chain.map(
                    self._analyze_logistics_metrics,
                    output=["logistics_analysis", "optimization_suggestions"],
                )
                .map(
                    self._apply_fanr_compliance,
                    output=["compliance_status", "compliance_report"],
                )
                .map(
                    self._generate_final_report, output=["final_report", "next_actions"]
                )
            )

            return logistics_chain

        except Exception as e:
            logger.error(f"Pipeline build failed: {e}")
            raise

    def _validate_excel_structure(self, file_path: str) -> Tuple[bool, Dict, List[str]]:
        """
        Excel 파일 구조 검증

        Args:
            file_path: Excel 파일 경로

        Returns:
            Tuple[bool, Dict, List[str]]: (유효성, 데이터, 오류목록)
        """
        try:
            # Excel 파일 읽기
            df = pd.read_excel(file_path)

            # HVDC 필수 컬럼 검증
            required_columns = {
                "warehouse": ["PKG", "QTY", "LOCATION", "STATUS"],
                "invoice": ["INVOICE_NO", "HS_CODE", "DESCRIPTION", "AMOUNT"],
                "status": ["DATE", "WAREHOUSE", "TOTAL_PKG", "UTILIZATION"],
            }

            errors = []
            data = {"file_path": file_path, "dataframe": df}

            # 파일 타입별 검증
            if "WAREHOUSE" in file_path.upper():
                missing_cols = [
                    col
                    for col in required_columns["warehouse"]
                    if col not in df.columns
                ]
                if missing_cols:
                    errors.append(f"Missing warehouse columns: {missing_cols}")

            elif "INVOICE" in file_path.upper():
                missing_cols = [
                    col for col in required_columns["invoice"] if col not in df.columns
                ]
                if missing_cols:
                    errors.append(f"Missing invoice columns: {missing_cols}")

            elif "STATUS" in file_path.upper():
                missing_cols = [
                    col for col in required_columns["status"] if col not in df.columns
                ]
                if missing_cols:
                    errors.append(f"Missing status columns: {missing_cols}")

            valid = len(errors) == 0
            logger.info(
                f"Excel validation for {file_path}: {'PASS' if valid else 'FAIL'}"
            )

            return valid, data, errors

        except Exception as e:
            logger.error(f"Excel validation error for {file_path}: {e}")
            return False, {}, [str(e)]

    def _extract_hvdc_data(self, data: Dict) -> Tuple[Dict, Dict, Dict]:
        """
        HVDC 데이터 추출 및 분류

        Args:
            data: 검증된 데이터

        Returns:
            Tuple[Dict, Dict, Dict]: (창고데이터, 송장데이터, 상태데이터)
        """
        try:
            file_path = data["file_path"]
            df = data["dataframe"]

            warehouse_data = {}
            invoice_data = {}
            status_data = {}

            # 파일 타입별 데이터 추출
            if "WAREHOUSE" in file_path.upper():
                if "HITACHI" in file_path.upper():
                    warehouse_data = {
                        "type": "HITACHI",
                        "data": df,
                        "timestamp": datetime.now().isoformat(),
                    }
                elif "SIMENSE" in file_path.upper():
                    warehouse_data = {
                        "type": "SIMENSE",
                        "data": df,
                        "timestamp": datetime.now().isoformat(),
                    }

            elif "INVOICE" in file_path.upper():
                invoice_data = {"data": df, "timestamp": datetime.now().isoformat()}

            elif "STATUS" in file_path.upper():
                status_data = {"data": df, "timestamp": datetime.now().isoformat()}

            logger.info(f"Data extraction completed for {file_path}")
            return warehouse_data, invoice_data, status_data

        except Exception as e:
            logger.error(f"Data extraction error: {e}")
            return {}, {}, {}

    def _clean_and_validate_data(self, data_tuple: Tuple) -> Tuple[Dict, Dict]:
        """
        데이터 정제 및 검증

        Args:
            data_tuple: (창고데이터, 송장데이터, 상태데이터)

        Returns:
            Tuple[Dict, Dict]: (정제된데이터, 검증보고서)
        """
        try:
            warehouse_data, invoice_data, status_data = data_tuple

            cleaned_data = {}
            validation_report = {
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "validation_results": {},
            }

            # 창고 데이터 정제
            if warehouse_data:
                df = warehouse_data["data"]
                # PKG 컬럼 숫자형 변환
                if "PKG" in df.columns:
                    df["PKG"] = pd.to_numeric(df["PKG"], errors="coerce")
                # QTY 컬럼 숫자형 변환
                if "QTY" in df.columns:
                    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce")

                cleaned_data["warehouse"] = {
                    "type": warehouse_data["type"],
                    "data": df,
                    "cleaned_at": datetime.now().isoformat(),
                }

                validation_report["validation_results"]["warehouse"] = {
                    "status": "CLEANED",
                    "rows": len(df),
                    "null_counts": df.isnull().sum().to_dict(),
                }

            # 송장 데이터 정제
            if invoice_data:
                df = invoice_data["data"]
                # HS_CODE 정규화
                if "HS_CODE" in df.columns:
                    df["HS_CODE"] = df["HS_CODE"].astype(str).str.strip()

                cleaned_data["invoice"] = {
                    "data": df,
                    "cleaned_at": datetime.now().isoformat(),
                }

                validation_report["validation_results"]["invoice"] = {
                    "status": "CLEANED",
                    "rows": len(df),
                    "null_counts": df.isnull().sum().to_dict(),
                }

            # 상태 데이터 정제
            if status_data:
                df = status_data["data"]
                # DATE 컬럼 날짜형 변환
                if "DATE" in df.columns:
                    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

                cleaned_data["status"] = {
                    "data": df,
                    "cleaned_at": datetime.now().isoformat(),
                }

                validation_report["validation_results"]["status"] = {
                    "status": "CLEANED",
                    "rows": len(df),
                    "null_counts": df.isnull().sum().to_dict(),
                }

            logger.info("Data cleaning and validation completed")
            return cleaned_data, validation_report

        except Exception as e:
            logger.error(f"Data cleaning error: {e}")
            return {}, {"error": str(e)}

    def _calculate_kpis(self, data_tuple: Tuple) -> Tuple[Dict, float]:
        """
        KPI 계산

        Args:
            data_tuple: (정제된데이터, 검증보고서)

        Returns:
            Tuple[Dict, float]: (KPI결과, 신뢰도점수)
        """
        try:
            cleaned_data, validation_report = data_tuple

            kpi_results = {
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "metrics": {},
            }

            confidence_score = 0.0

            # 창고 KPI 계산
            if "warehouse" in cleaned_data:
                warehouse_df = cleaned_data["warehouse"]["data"]

                # 총 PKG 수
                total_pkg = (
                    warehouse_df["PKG"].sum() if "PKG" in warehouse_df.columns else 0
                )

                # 총 QTY
                total_qty = (
                    warehouse_df["QTY"].sum() if "QTY" in warehouse_df.columns else 0
                )

                # 위치별 분포
                location_distribution = (
                    warehouse_df["LOCATION"].value_counts().to_dict()
                    if "LOCATION" in warehouse_df.columns
                    else {}
                )

                # 상태별 분포
                status_distribution = (
                    warehouse_df["STATUS"].value_counts().to_dict()
                    if "STATUS" in warehouse_df.columns
                    else {}
                )

                kpi_results["metrics"]["warehouse"] = {
                    "total_pkg": total_pkg,
                    "total_qty": total_qty,
                    "location_distribution": location_distribution,
                    "status_distribution": status_distribution,
                    "utilization_rate": self._calculate_utilization_rate(warehouse_df),
                }

                confidence_score += 0.4  # 창고 데이터 가중치

            # 송장 KPI 계산
            if "invoice" in cleaned_data:
                invoice_df = cleaned_data["invoice"]["data"]

                # 총 송장 수
                total_invoices = len(invoice_df)

                # 총 금액
                total_amount = (
                    invoice_df["AMOUNT"].sum() if "AMOUNT" in invoice_df.columns else 0
                )

                # HS 코드별 분포
                hs_distribution = (
                    invoice_df["HS_CODE"].value_counts().to_dict()
                    if "HS_CODE" in invoice_df.columns
                    else {}
                )

                kpi_results["metrics"]["invoice"] = {
                    "total_invoices": total_invoices,
                    "total_amount": total_amount,
                    "hs_distribution": hs_distribution,
                }

                confidence_score += 0.3  # 송장 데이터 가중치

            # 상태 KPI 계산
            if "status" in cleaned_data:
                status_df = cleaned_data["status"]["data"]

                # 최신 상태
                latest_status = (
                    status_df.iloc[-1].to_dict() if len(status_df) > 0 else {}
                )

                # 시계열 추세
                trend_analysis = self._analyze_trend(status_df)

                kpi_results["metrics"]["status"] = {
                    "latest_status": latest_status,
                    "trend_analysis": trend_analysis,
                }

                confidence_score += 0.3  # 상태 데이터 가중치

            # 최종 신뢰도 점수 계산
            final_confidence = min(confidence_score, 1.0)

            logger.info(
                f"KPI calculation completed with confidence: {final_confidence:.2f}"
            )
            return kpi_results, final_confidence

        except Exception as e:
            logger.error(f"KPI calculation error: {e}")
            return {}, 0.0

    def _calculate_utilization_rate(self, df: pd.DataFrame) -> float:
        """창고 활용률 계산"""
        try:
            if "QTY" in df.columns and "LOCATION" in df.columns:
                total_qty = df["QTY"].sum()
                # 가정: 각 위치의 최대 용량 (실제로는 설정에서 가져와야 함)
                max_capacity = 10000  # 예시 값
                return (total_qty / max_capacity) * 100 if max_capacity > 0 else 0
            return 0.0
        except Exception as e:
            logger.error(f"Utilization rate calculation error: {e}")
            return 0.0

    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """시계열 트렌드 분석"""
        try:
            if "DATE" in df.columns and len(df) > 1:
                df_sorted = df.sort_values("DATE")
                # 간단한 선형 트렌드 계산
                if "TOTAL_PKG" in df.columns:
                    x = np.arange(len(df_sorted))
                    y = df_sorted["TOTAL_PKG"].values
                    slope = np.polyfit(x, y, 1)[0] if len(y) > 1 else 0
                    return {
                        "trend_direction": "increasing" if slope > 0 else "decreasing",
                        "trend_slope": slope,
                        "data_points": len(df_sorted),
                    }
            return {"trend_direction": "unknown", "trend_slope": 0, "data_points": 0}
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {"trend_direction": "error", "trend_slope": 0, "data_points": 0}

    def _generate_kpi_report(self, data_tuple: Tuple) -> Tuple[Dict, List[str]]:
        """
        KPI 보고서 생성

        Args:
            data_tuple: (KPI결과, 신뢰도점수)

        Returns:
            Tuple[Dict, List[str]]: (KPI보고서, 알림목록)
        """
        try:
            kpi_results, confidence_score = data_tuple

            kpi_report = {
                "report_id": f"HVDC_KPI_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "confidence_score": confidence_score,
                "kpi_summary": kpi_results,
                "recommendations": [],
            }

            alerts = []

            # 알림 조건 검사
            if "warehouse" in kpi_results.get("metrics", {}):
                warehouse_metrics = kpi_results["metrics"]["warehouse"]

                # 활용률 알림
                if warehouse_metrics.get("utilization_rate", 0) > 85:
                    alerts.append("HIGH_UTILIZATION: 창고 활용률이 85%를 초과했습니다.")

                # PKG 수 알림
                if warehouse_metrics.get("total_pkg", 0) > 1000:
                    alerts.append("HIGH_PKG_COUNT: 총 PKG 수가 1000개를 초과했습니다.")

            # 신뢰도 알림
            if confidence_score < self.confidence_threshold:
                alerts.append(
                    f"LOW_CONFIDENCE: 신뢰도 점수가 {self.confidence_threshold} 미만입니다."
                )

            # 권장사항 생성
            if alerts:
                kpi_report["recommendations"].append(
                    "즉시 조치가 필요한 알림이 있습니다."
                )

            if confidence_score >= 0.95:
                kpi_report["recommendations"].append(
                    "데이터 품질이 우수합니다. 자동화된 처리를 진행할 수 있습니다."
                )

            logger.info(f"KPI report generated: {kpi_report['report_id']}")
            return kpi_report, alerts

        except Exception as e:
            logger.error(f"KPI report generation error: {e}")
            return {}, [f"Error: {str(e)}"]

    def _analyze_logistics_metrics(self, data_tuple: Tuple) -> Tuple[Dict, List[str]]:
        """
        물류 지표 분석

        Args:
            data_tuple: (KPI보고서, 알림목록)

        Returns:
            Tuple[Dict, List[str]]: (물류분석, 최적화제안)
        """
        try:
            kpi_report, alerts = data_tuple

            logistics_analysis = {
                "analysis_id": f"HVDC_LOGISTICS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "analysis_results": {},
                "performance_metrics": {},
            }

            optimization_suggestions = []

            # KPI 데이터에서 물류 분석 수행
            kpi_summary = kpi_report.get("kpi_summary", {})
            metrics = kpi_summary.get("metrics", {})

            # 창고 성능 분석
            if "warehouse" in metrics:
                warehouse_metrics = metrics["warehouse"]

                # 위치별 최적화 제안
                location_dist = warehouse_metrics.get("location_distribution", {})
                if location_dist:
                    max_location = max(location_dist.items(), key=lambda x: x[1])
                    min_location = min(location_dist.items(), key=lambda x: x[1])

                    optimization_suggestions.append(
                        f"위치 {max_location[0]}의 부하를 {min_location[0]}로 분산하는 것을 고려하세요."
                    )

                # 활용률 기반 제안
                utilization = warehouse_metrics.get("utilization_rate", 0)
                if utilization > 90:
                    optimization_suggestions.append(
                        "창고 용량 확장 또는 추가 창고 검토가 필요합니다."
                    )
                elif utilization < 50:
                    optimization_suggestions.append(
                        "창고 공간 최적화를 위한 재배치를 고려하세요."
                    )

            # 송장 분석
            if "invoice" in metrics:
                invoice_metrics = metrics["invoice"]

                # HS 코드별 분석
                hs_dist = invoice_metrics.get("hs_distribution", {})
                if hs_dist:
                    top_hs = max(hs_dist.items(), key=lambda x: x[1])
                    optimization_suggestions.append(
                        f"HS 코드 {top_hs[0]}의 물품이 가장 많습니다. 특별 관리가 필요할 수 있습니다."
                    )

            logistics_analysis["analysis_results"] = {
                "warehouse_analysis": metrics.get("warehouse", {}),
                "invoice_analysis": metrics.get("invoice", {}),
                "status_analysis": metrics.get("status", {}),
            }

            logistics_analysis["performance_metrics"] = {
                "overall_score": kpi_report.get("confidence_score", 0),
                "alert_count": len(alerts),
                "optimization_opportunities": len(optimization_suggestions),
            }

            logger.info(
                f"Logistics analysis completed: {logistics_analysis['analysis_id']}"
            )
            return logistics_analysis, optimization_suggestions

        except Exception as e:
            logger.error(f"Logistics analysis error: {e}")
            return {}, [f"Error: {str(e)}"]

    def _apply_fanr_compliance(self, data_tuple: Tuple) -> Tuple[Dict, Dict]:
        """
        FANR 규정 준수 검증

        Args:
            data_tuple: (물류분석, 최적화제안)

        Returns:
            Tuple[Dict, Dict]: (준수상태, 준수보고서)
        """
        try:
            logistics_analysis, optimization_suggestions = data_tuple

            compliance_status = {
                "compliance_id": f"HVDC_FANR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "overall_compliance": True,
                "compliance_checks": {},
            }

            compliance_report = {
                "report_id": f"FANR_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "compliance_details": {},
                "violations": [],
                "recommendations": [],
            }

            # FANR 규정 검증 (예시)
            analysis_results = logistics_analysis.get("analysis_results", {})

            # 창고 안전 규정 검증
            warehouse_analysis = analysis_results.get("warehouse_analysis", {})
            if warehouse_analysis.get("utilization_rate", 0) > 95:
                compliance_status["compliance_checks"]["warehouse_safety"] = False
                compliance_status["overall_compliance"] = False
                compliance_report["violations"].append(
                    "창고 활용률이 안전 한계를 초과했습니다."
                )
            else:
                compliance_status["compliance_checks"]["warehouse_safety"] = True

            # 송장 규정 검증
            invoice_analysis = analysis_results.get("invoice_analysis", {})
            if invoice_analysis.get("total_invoices", 0) > 0:
                compliance_status["compliance_checks"]["invoice_compliance"] = True
            else:
                compliance_status["compliance_checks"]["invoice_compliance"] = False
                compliance_report["violations"].append("송장 데이터가 누락되었습니다.")

            # 권장사항 추가
            if optimization_suggestions:
                compliance_report["recommendations"].extend(optimization_suggestions)

            logger.info(
                f"FANR compliance check completed: {compliance_status['compliance_id']}"
            )
            return compliance_status, compliance_report

        except Exception as e:
            logger.error(f"FANR compliance error: {e}")
            return {"error": str(e)}, {"error": str(e)}

    def _generate_final_report(self, data_tuple: Tuple) -> Tuple[Dict, List[str]]:
        """
        최종 보고서 생성

        Args:
            data_tuple: (준수상태, 준수보고서)

        Returns:
            Tuple[Dict, List[str]]: (최종보고서, 다음행동)
        """
        try:
            compliance_status, compliance_report = data_tuple

            final_report = {
                "report_id": f"HVDC_FINAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "executive_summary": {
                    "overall_status": (
                        "SUCCESS"
                        if compliance_status.get("overall_compliance", False)
                        else "ATTENTION_REQUIRED"
                    ),
                    "compliance_score": self._calculate_compliance_score(
                        compliance_status
                    ),
                    "data_quality_score": compliance_status.get(
                        "overall_compliance", False
                    )
                    * 100,
                },
                "detailed_analysis": {
                    "compliance_status": compliance_status,
                    "compliance_report": compliance_report,
                },
                "system_recommendations": [],
            }

            next_actions = []

            # 시스템 권장사항 생성
            if not compliance_status.get("overall_compliance", True):
                final_report["system_recommendations"].append(
                    "즉시 조치가 필요한 규정 위반이 발견되었습니다."
                )
                next_actions.append("IMMEDIATE_ACTION: 규정 위반 사항 즉시 조치")

            if compliance_status.get("overall_compliance", False):
                final_report["system_recommendations"].append(
                    "모든 규정을 준수하고 있습니다. 정기 모니터링을 계속하세요."
                )
                next_actions.append("CONTINUE_MONITORING: 정기 모니터링 유지")

            # MACHO-GPT 모드별 권장사항
            if self.mode == "LATTICE":
                next_actions.append("LATTICE_MODE: OCR 및 적재 최적화 분석 실행")
            elif self.mode == "RHYTHM":
                next_actions.append("RHYTHM_MODE: 실시간 KPI 대시보드 업데이트")
            elif self.mode == "COST-GUARD":
                next_actions.append("COST-GUARD_MODE: 비용 최적화 분석 실행")

            # 자동화 권장사항
            next_actions.append("AUTOMATE_PIPELINE: DataChain 파이프라인 자동화 설정")
            next_actions.append("INTEGRATE_MCP: MCP 서버 통합 완료")

            logger.info(f"Final report generated: {final_report['report_id']}")
            return final_report, next_actions

        except Exception as e:
            logger.error(f"Final report generation error: {e}")
            return {"error": str(e)}, [f"Error: {str(e)}"]

    def _calculate_compliance_score(self, compliance_status: Dict) -> float:
        """준수 점수 계산"""
        try:
            checks = compliance_status.get("compliance_checks", {})
            if not checks:
                return 0.0

            passed_checks = sum(1 for check in checks.values() if check)
            total_checks = len(checks)

            return (passed_checks / total_checks) * 100 if total_checks > 0 else 0.0
        except Exception as e:
            logger.error(f"Compliance score calculation error: {e}")
            return 0.0

    def run_pipeline(self) -> Dict:
        """
        DataChain 파이프라인 실행

        Returns:
            Dict: 실행 결과
        """
        try:
            logger.info(f"Starting HVDC DataChain pipeline in {self.mode} mode")

            # 파이프라인이 None이면 데이터 없음
            if self.pipeline is None:
                logger.warning("Pipeline not built - no data available")
                return {
                    "status": "WARNING",
                    "message": "No Excel files found in data directory",
                    "timestamp": datetime.now().isoformat(),
                    "mode": self.mode,
                }

            # 파이프라인 실행
            results = list(self.pipeline)

            if not results:
                logger.warning("Pipeline returned no results")
                return {
                    "status": "WARNING",
                    "message": "No data processed",
                    "timestamp": datetime.now().isoformat(),
                }

            # 최종 결과 추출
            final_result = results[-1]
            final_report, next_actions = final_result

            # 결과 저장
            self._save_results(final_report, next_actions)

            logger.info("HVDC DataChain pipeline completed successfully")

            return {
                "status": "SUCCESS",
                "mode": self.mode,
                "final_report": final_report,
                "next_actions": next_actions,
                "timestamp": datetime.now().isoformat(),
                "confidence": final_report.get("executive_summary", {}).get(
                    "data_quality_score", 0
                ),
            }

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return {
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _save_results(self, final_report: Dict, next_actions: List[str]):
        """결과 저장"""
        try:
            # JSON 파일로 저장
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 최종 보고서 저장
            report_file = output_dir / f"hvdc_datachain_report_{timestamp}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(final_report, f, ensure_ascii=False, indent=2)

            # 다음 행동 저장
            actions_file = output_dir / f"hvdc_next_actions_{timestamp}.json"
            with open(actions_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "mode": self.mode,
                        "actions": next_actions,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            logger.info(f"Results saved to {output_dir}")

        except Exception as e:
            logger.error(f"Result saving error: {e}")


def main() -> int:
    try:
        data_dir = get_data_dir()
        excel_files = sorted(data_dir.glob("*.xlsx"))
        if not excel_files:
            logger.warning("No Excel files found in %s – pipeline aborted.", data_dir)
            return 0  # graceful exit
        # 기존 파이프라인 객체 생성 및 실행 로직 유지
        pipeline = HVDCDataChainPipeline(data_dir=str(data_dir), mode="PRIME")
        result = pipeline.run_pipeline()
        print("=" * 60)
        print("HVDC DataChain Pipeline Execution Result")
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Mode: {result.get('mode', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 0):.2f}%")
        print(f"Timestamp: {result['timestamp']}")
        if result["status"] == "SUCCESS":
            print("\nNext Actions:")
            for action in result.get("next_actions", []):
                print(f"  - {action}")
        print("=" * 60)
        return 0
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
