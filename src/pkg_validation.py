"""
PKG 수량 검증 시스템
HVDC 프로젝트 - 송장, 창고, 현장 데이터의 PKG 수량 일치 여부 자동 검증
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging


class PKGValidationSystem:
    """PKG 수량 검증 시스템"""

    def __init__(
        self, confidence_threshold: float = 0.95, critical_threshold: int = 50
    ):
        """
        PKG 검증 시스템 초기화

        Args:
            confidence_threshold: 신뢰도 임계값 (기본값: 0.95)
            critical_threshold: 중요 불일치 임계값 (기본값: 50)
        """
        self.confidence_threshold = confidence_threshold
        self.critical_threshold = critical_threshold
        self.setup_logging()

    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("pkg_validation.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def validate_pkg_count_match(
        self,
        data1: pd.DataFrame,
        data2: pd.DataFrame,
        data1_name: str = "invoice",
        data2_name: str = "warehouse",
    ) -> Dict[str, Any]:
        """
        PKG 수량 일치 검증

        Args:
            data1: 첫 번째 데이터프레임 (예: 송장 데이터)
            data2: 두 번째 데이터프레임 (예: 창고 데이터)
            data1_name: 첫 번째 데이터 이름
            data2_name: 두 번째 데이터 이름

        Returns:
            검증 결과 딕셔너리
        """
        result = {
            "is_match": False,
            "invoice_total": 0,
            "warehouse_total": 0,
            "site_total": 0,
            "difference": 0,
            "confidence": 0.0,
            "alerts": [],
            "errors": [],
            "report": {
                "timestamp": datetime.now().isoformat(),
                "summary": "",
                "details": {},
                "recommendations": [],
            },
        }

        try:
            # 1. 데이터 유효성 검사
            validation_result = self._validate_data_integrity(data1, data2)
            if not validation_result["is_valid"]:
                result["errors"].extend(validation_result["errors"])
                return result

            # 2. PKG 수량 집계
            total1 = data1["pkg_count"].sum()
            total2 = data2["pkg_count"].sum()

            result[f"{data1_name}_total"] = total1
            result[f"{data2_name}_total"] = total2
            # site_total, warehouse_total 등도 동적으로 할당
            if "site" in data2_name:
                result["site_total"] = total2
            if "warehouse" in data2_name:
                result["warehouse_total"] = total2
            if "invoice" in data1_name:
                result["invoice_total"] = total1

            # 3. 차이 계산
            difference = abs(total1 - total2)
            result["difference"] = difference

            # 4. 일치 여부 판단
            result["is_match"] = difference == 0

            # 5. 신뢰도 계산
            result["confidence"] = self._calculate_confidence(
                total1, total2, difference
            )

            # 6. 알림 생성
            self._generate_alerts(result, difference)

            # 7. 리포트 생성
            self._generate_report(
                result, data1_name, data2_name, total1, total2, difference
            )

            self.logger.info(
                f"PKG 검증 완료: {data1_name} vs {data2_name}, 일치: {result['is_match']}, 차이: {difference}"
            )

        except Exception as e:
            self.logger.error(f"PKG 검증 중 오류 발생: {str(e)}")
            result["errors"].append(f"validation_error: {str(e)}")
            result["confidence"] = 0.0

        return result

    def _validate_data_integrity(
        self, data1: pd.DataFrame, data2: pd.DataFrame
    ) -> Dict[str, Any]:
        """데이터 무결성 검사"""
        result = {"is_valid": True, "errors": []}

        # 빈 데이터 체크
        if data1.empty or data2.empty:
            result["is_valid"] = False
            result["errors"].append("empty_data")

        # pkg_count 컬럼 존재 체크
        if "pkg_count" not in data1.columns or "pkg_count" not in data2.columns:
            result["is_valid"] = False
            result["errors"].append("missing_pkg_count_column")

        # 데이터 타입 체크
        if not data1.empty and "pkg_count" in data1.columns:
            if not pd.api.types.is_numeric_dtype(data1["pkg_count"]):
                result["is_valid"] = False
                result["errors"].append("invalid_pkg_count_data_type")

        if not data2.empty and "pkg_count" in data2.columns:
            if not pd.api.types.is_numeric_dtype(data2["pkg_count"]):
                result["is_valid"] = False
                result["errors"].append("invalid_pkg_count_data_type")

        return result

    def _calculate_confidence(
        self, total1: float, total2: float, difference: float
    ) -> float:
        """신뢰도 점수 계산"""
        if difference == 0:
            return self.confidence_threshold
        else:
            # 차이가 클수록 신뢰도 감소
            base_confidence = self.confidence_threshold
            penalty = min(0.5, (difference / max(total1, total2)) * 2)
            return max(0.0, base_confidence - penalty)

    def _generate_alerts(self, result: Dict[str, Any], difference: float):
        """알림 생성"""
        if not result["is_match"]:
            result["alerts"].append("discrepancy_detected")

            if difference > self.critical_threshold:
                result["alerts"].append("critical_discrepancy")

            if difference > self.critical_threshold * 2:
                result["alerts"].append("severe_discrepancy")

    def _generate_report(
        self,
        result: Dict[str, Any],
        data1_name: str,
        data2_name: str,
        total1: float,
        total2: float,
        difference: float,
    ):
        """상세 리포트 생성"""
        result["report"][
            "summary"
        ] = f"PKG 수량 검증: {'일치' if result['is_match'] else '불일치'}"
        result["report"]["details"] = {
            f"{data1_name}_total": total1,
            f"{data2_name}_total": total2,
            "difference": difference,
            "difference_percentage": (
                round((difference / max(total1, total2)) * 100, 2)
                if max(total1, total2) > 0
                else 0
            ),
        }

        # 권장사항 생성
        recommendations = []
        if result["is_match"]:
            recommendations.append("PKG 수량이 정확히 일치합니다.")
        else:
            recommendations.append("불일치 발견 시 즉시 조사 필요")
            if difference > self.critical_threshold:
                recommendations.append("중요 불일치로 인한 긴급 조치 필요")
            recommendations.append("정기적인 PKG 수량 검증 권장")
            recommendations.append("데이터 입력 과정 재검토 필요")

        result["report"]["recommendations"] = recommendations

    def validate_multiple_sources(
        self, data_sources: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """
        여러 데이터 소스 간 PKG 수량 검증

        Args:
            data_sources: 데이터 소스 딕셔너리 (예: {'invoice': df1, 'warehouse': df2, 'site': df3})

        Returns:
            통합 검증 결과
        """
        if len(data_sources) < 2:
            return {"error": "최소 2개의 데이터 소스가 필요합니다.", "confidence": 0.0}

        results = {}
        source_names = list(data_sources.keys())

        # 모든 조합에 대해 검증 수행
        for i in range(len(source_names)):
            for j in range(i + 1, len(source_names)):
                source1 = source_names[i]
                source2 = source_names[j]

                comparison_key = f"{source1}_vs_{source2}"
                results[comparison_key] = self.validate_pkg_count_match(
                    data_sources[source1], data_sources[source2], source1, source2
                )

        # 통합 결과 생성
        all_match = all(result["is_match"] for result in results.values())
        avg_confidence = sum(result["confidence"] for result in results.values()) / len(
            results
        )
        all_alerts = []
        all_errors = []

        for result in results.values():
            all_alerts.extend(result["alerts"])
            all_errors.extend(result["errors"])

        return {
            "overall_match": all_match,
            "average_confidence": round(avg_confidence, 3),
            "total_comparisons": len(results),
            "all_alerts": list(set(all_alerts)),
            "all_errors": list(set(all_errors)),
            "detailed_results": results,
        }


def main():
    """메인 실행 함수"""
    print("📦 PKG 수량 검증 시스템")
    print("=" * 50)

    # 시스템 초기화
    pkg_validator = PKGValidationSystem()

    # 샘플 데이터 생성
    invoice_data = pd.DataFrame(
        {
            "invoice_number": ["INV-001", "INV-002", "INV-003"],
            "pkg_count": [100, 150, 200],
            "amount": [15000.0, 22500.0, 30000.0],
        }
    )

    warehouse_data = pd.DataFrame(
        {
            "warehouse_code": ["DSV-OUT", "DSV-IN", "DSV-OUT"],
            "invoice_number": ["INV-001", "INV-002", "INV-003"],
            "pkg_count": [100, 150, 200],
        }
    )

    # 검증 실행
    result = pkg_validator.validate_pkg_count_match(invoice_data, warehouse_data)

    print(f"✅ 검증 완료!")
    print(f"📊 일치 여부: {'일치' if result['is_match'] else '불일치'}")
    print(f"📈 신뢰도: {result['confidence']:.3f}")
    print(f"📋 알림: {result['alerts']}")
    print(f"📝 오류: {result['errors']}")

    print("\n🔧 추천 명령어:")
    print("/pkg_validation run_tests - PKG 검증 테스트 실행")
    print("/pkg_validation generate_report - 검증 리포트 생성")
    print("/task_manager update_task <task_id> - 태스크 상태 업데이트")


if __name__ == "__main__":
    main()
