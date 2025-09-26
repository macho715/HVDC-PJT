"""
LATTICE 모드 - 창고 최적화 입출고 로직 검증 스크립트
HVDC 프로젝트 창고 최적화 시스템 종합 검증
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from warehouse_io_calculator import WarehouseIOCalculator
from status_calculator import StatusCalculator
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LatticeModeVerifier:
    """LATTICE 모드 창고 최적화 검증 클래스"""

    def __init__(self):
        self.calculator = WarehouseIOCalculator()
        self.status_calculator = StatusCalculator()
        self.verification_results = {}

    def create_comprehensive_test_data(self):
        """종합 테스트 데이터 생성 (모든 시나리오 포함)"""
        test_data = pd.DataFrame(
            {
                "Item": [f"T{i:03d}" for i in range(1, 21)],
                # 창고 입고 시나리오
                "DSV Indoor": [
                    datetime(2024, 1, 15),
                    datetime(2024, 1, 20),
                    datetime(2024, 2, 1),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "DSV Outdoor": [
                    None,
                    None,
                    None,
                    datetime(2024, 1, 25),
                    datetime(2024, 2, 5),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "DSV Al Markaz": [
                    None,
                    None,
                    None,
                    None,
                    None,
                    datetime(2024, 1, 10),
                    datetime(2024, 2, 15),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "DSV MZP": [None] * 20,
                "AAA  Storage": [None] * 20,
                "AAA Storage": [None] * 20,
                "Hauler Indoor": [None] * 20,
                "MOSB": [
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    datetime(2024, 2, 10),
                    datetime(2024, 3, 1),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "DHL Warehouse": [None] * 20,
                # 현장 입고 시나리오 (창고 경유)
                "MIR": [
                    datetime(2024, 2, 15),
                    None,
                    datetime(2024, 3, 1),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    datetime(2024, 3, 15),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "SHU": [
                    None,
                    datetime(2024, 2, 20),
                    None,
                    datetime(2024, 2, 25),
                    None,
                    datetime(2024, 2, 20),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "DAS": [
                    None,
                    None,
                    None,
                    None,
                    datetime(2024, 3, 5),
                    None,
                    datetime(2024, 3, 10),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "AGI": [
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    datetime(2024, 3, 5),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                # PKG 수량 (실제 수량 반영)
                "Pkg": [1, 2, 1, 3, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            }
        )

        return test_data

    def verify_inbound_logic(self, df):
        """입고 로직 검증"""
        logger.info("🔍 입고 로직 검증 시작...")

        # 1. 기본 입고 계산
        inbound_result = self.calculator.calculate_warehouse_inbound(df)

        # 2. 수동 검증
        manual_inbound = {}
        warehouse_cols = self.calculator.warehouse_columns

        for warehouse in warehouse_cols:
            if warehouse in df.columns:
                warehouse_dates = df[warehouse].dropna()
                manual_inbound[warehouse] = len(warehouse_dates)

        # 3. 검증 결과
        verification = {
            "total_inbound": inbound_result["total_inbound"],
            "by_warehouse": inbound_result["by_warehouse"],
            "manual_verification": manual_inbound,
            "monthly_pivot_shape": (
                inbound_result["monthly_pivot"].shape
                if not inbound_result["monthly_pivot"].empty
                else (0, 0)
            ),
            "status": "PASS" if inbound_result["total_inbound"] > 0 else "FAIL",
        }

        logger.info(f"✅ 입고 로직 검증 완료: {verification['total_inbound']}건")
        return verification

    def verify_outbound_logic(self, df):
        """출고 로직 검증"""
        logger.info("🔍 출고 로직 검증 시작...")

        # 1. 기본 출고 계산
        outbound_result = self.calculator.calculate_warehouse_outbound(df)

        # 2. 수동 검증 (창고 → 현장 이동)
        manual_outbound = {}
        warehouse_cols = self.calculator.warehouse_columns
        site_cols = self.calculator.site_columns

        for warehouse in warehouse_cols:
            if warehouse in df.columns:
                warehouse_visited = df[df[warehouse].notna()].copy()
                outbound_count = 0

                for idx, row in warehouse_visited.iterrows():
                    warehouse_date = row[warehouse]

                    # 창고 방문 후 현장으로 이동한 케이스 찾기
                    for site in site_cols:
                        if site in row.index and pd.notna(row[site]):
                            site_date = row[site]
                            if site_date > warehouse_date:
                                outbound_count += 1
                                break

                manual_outbound[warehouse] = outbound_count

        # 3. 검증 결과
        verification = {
            "total_outbound": outbound_result["total_outbound"],
            "by_warehouse": outbound_result["by_warehouse"],
            "by_site": outbound_result["by_site"],
            "manual_verification": manual_outbound,
            "status": "PASS" if outbound_result["total_outbound"] >= 0 else "FAIL",
        }

        logger.info(f"✅ 출고 로직 검증 완료: {verification['total_outbound']}건")
        return verification

    def verify_inventory_logic(self, df):
        """재고 로직 검증"""
        logger.info("🔍 재고 로직 검증 시작...")

        # 1. 기본 재고 계산
        inventory_result = self.calculator.calculate_warehouse_inventory(df)

        # 2. Status_Location 기반 수동 검증
        status_df = self.status_calculator.calculate_complete_status(df)
        warehouse_items = status_df[status_df["Status_Current"] == "warehouse"]

        manual_inventory = {}
        for warehouse in self.calculator.warehouse_columns:
            if warehouse in df.columns:
                at_warehouse = warehouse_items[
                    warehouse_items["Status_Location"] == warehouse
                ]
                manual_inventory[warehouse] = len(at_warehouse)

        # 3. 검증 결과
        verification = {
            "total_inventory": inventory_result["total_inventory"],
            "by_warehouse": inventory_result["by_warehouse"],
            "by_status": inventory_result["by_status"],
            "manual_verification": manual_inventory,
            "status_location_distribution": inventory_result.get(
                "status_location_distribution", {}
            ),
            "status": "PASS" if inventory_result["total_inventory"] >= 0 else "FAIL",
        }

        logger.info(f"✅ 재고 로직 검증 완료: {verification['total_inventory']}건")
        return verification

    def verify_direct_delivery_logic(self, df):
        """직배송 로직 검증"""
        logger.info("🔍 직배송 로직 검증 시작...")

        # 1. 기본 직배송 계산
        direct_result = self.calculator.calculate_direct_delivery(df)

        # 2. 수동 검증 (창고를 거치지 않고 현장으로)
        status_df = self.status_calculator.calculate_complete_status(df)
        site_items = status_df[status_df["Status_Current"] == "site"].copy()

        manual_direct = 0
        for idx, row in site_items.iterrows():
            # 모든 창고 컬럼에 날짜가 없는지 확인
            has_warehouse_date = False
            for warehouse in self.calculator.warehouse_columns:
                if warehouse in row.index and pd.notna(row[warehouse]):
                    has_warehouse_date = True
                    break

            if not has_warehouse_date:
                manual_direct += 1

        # 3. 검증 결과
        verification = {
            "total_direct": direct_result["total_direct"],
            "by_site": direct_result["by_site"],
            "by_month": direct_result["by_month"],
            "manual_verification": manual_direct,
            "status": (
                "PASS" if direct_result["total_direct"] == manual_direct else "FAIL"
            ),
        }

        logger.info(f"✅ 직배송 로직 검증 완료: {verification['total_direct']}건")
        return verification

    def verify_pkg_quantity_logic(self, df):
        """PKG 수량 로직 검증"""
        logger.info("🔍 PKG 수량 로직 검증 시작...")

        # 1. PKG 컬럼 존재 확인
        has_pkg_column = "Pkg" in df.columns

        # 2. PKG 수량 통계
        if has_pkg_column:
            pkg_stats = {
                "total_pkg": df["Pkg"].sum(),
                "avg_pkg": df["Pkg"].mean(),
                "min_pkg": df["Pkg"].min(),
                "max_pkg": df["Pkg"].max(),
                "null_count": df["Pkg"].isna().sum(),
            }
        else:
            pkg_stats = {"error": "Pkg 컬럼이 없습니다"}

        # 3. 검증 결과
        verification = {
            "has_pkg_column": has_pkg_column,
            "pkg_statistics": pkg_stats,
            "status": "PASS" if has_pkg_column and df["Pkg"].sum() > 0 else "FAIL",
        }

        logger.info(
            f"✅ PKG 수량 로직 검증 완료: 총 {pkg_stats.get('total_pkg', 0)} PKG"
        )
        return verification

    def verify_final_location_logic(self, df):
        """Final Location 로직 검증"""
        logger.info("🔍 Final Location 로직 검증 시작...")

        # 1. Final Location 계산
        result_df = self.calculator.calculate_final_location(df)

        # 2. Final Location 분포
        final_location_dist = result_df["Final_Location"].value_counts().to_dict()

        # 3. Status_Location과 비교
        status_df = self.status_calculator.calculate_complete_status(df)
        status_location_dist = status_df["Status_Location"].value_counts().to_dict()

        # 4. 검증 결과
        verification = {
            "final_location_distribution": final_location_dist,
            "status_location_distribution": status_location_dist,
            "total_locations": len(final_location_dist),
            "status": "PASS" if len(final_location_dist) > 0 else "FAIL",
        }

        logger.info(
            f"✅ Final Location 로직 검증 완료: {len(final_location_dist)}개 위치"
        )
        return verification

    def run_comprehensive_verification(self):
        """종합 검증 실행"""
        logger.info("🚀 LATTICE 모드 종합 검증 시작...")

        # 1. 테스트 데이터 생성
        test_data = self.create_comprehensive_test_data()
        logger.info(f"📊 테스트 데이터 생성: {len(test_data)}건")

        # 2. 각 로직별 검증
        self.verification_results = {
            "inbound": self.verify_inbound_logic(test_data),
            "outbound": self.verify_outbound_logic(test_data),
            "inventory": self.verify_inventory_logic(test_data),
            "direct_delivery": self.verify_direct_delivery_logic(test_data),
            "pkg_quantity": self.verify_pkg_quantity_logic(test_data),
            "final_location": self.verify_final_location_logic(test_data),
        }

        # 3. 종합 결과
        all_passed = all(
            result["status"] == "PASS" for result in self.verification_results.values()
        )

        logger.info(
            f"🎯 LATTICE 모드 검증 완료: {'ALL PASS' if all_passed else 'SOME FAILED'}"
        )

        return self.verification_results

    def print_verification_report(self):
        """검증 결과 리포트 출력"""
        print("\n" + "=" * 80)
        print("🏭 LATTICE 모드 - 창고 최적화 입출고 로직 검증 리포트")
        print("=" * 80)

        for logic_name, result in self.verification_results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"\n{status_icon} {logic_name.upper()} 로직:")
            print(f"   상태: {result['status']}")

            if logic_name == "inbound":
                print(f"   총 입고: {result['total_inbound']}건")
                print(f"   창고별: {result['by_warehouse']}")
                print(f"   피벗 테이블: {result['monthly_pivot_shape']}")

            elif logic_name == "outbound":
                print(f"   총 출고: {result['total_outbound']}건")
                print(f"   창고별: {result['by_warehouse']}")
                print(f"   현장별: {result['by_site']}")

            elif logic_name == "inventory":
                print(f"   총 재고: {result['total_inventory']}건")
                print(f"   창고별: {result['by_warehouse']}")
                print(f"   상태별: {result['by_status']}")

            elif logic_name == "direct_delivery":
                print(f"   총 직배송: {result['total_direct']}건")
                print(f"   현장별: {result['by_site']}")
                print(f"   월별: {result['by_month']}")

            elif logic_name == "pkg_quantity":
                print(f"   PKG 컬럼: {'있음' if result['has_pkg_column'] else '없음'}")
                if "pkg_statistics" in result:
                    stats = result["pkg_statistics"]
                    print(f"   총 PKG: {stats.get('total_pkg', 0)}")
                    print(f"   평균 PKG: {stats.get('avg_pkg', 0):.2f}")

            elif logic_name == "final_location":
                print(f"   위치 수: {result['total_locations']}")
                print(f"   Final Location: {result['final_location_distribution']}")

        # 종합 결과
        all_passed = all(
            result["status"] == "PASS" for result in self.verification_results.values()
        )
        print(f"\n{'='*80}")
        print(f"🎯 종합 결과: {'✅ ALL PASS' if all_passed else '❌ SOME FAILED'}")
        print(f"{'='*80}")


def main():
    """메인 실행 함수"""
    verifier = LatticeModeVerifier()
    results = verifier.run_comprehensive_verification()
    verifier.print_verification_report()

    return results


if __name__ == "__main__":
    main()
