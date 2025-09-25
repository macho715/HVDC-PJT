#!/usr/bin/env python3
"""
실제 HVDC 데이터 기반 창고 입출고 계산 및 품질 검증
Real-world HVDC data validation and warehouse I/O calculation
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 테스트 모듈 임포트
from test_warehouse_io_validation import (
    WarehouseIOCalculator,
    DataQualityValidator,
    ComprehensiveWarehouseValidator,
)


def load_hvdc_data():
    """실제 HVDC 데이터 로드"""
    data_files = [
        "../data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "../data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx",
        "../data_cleaned/HVDC_WAREHOUSE_HITACHI_CLEANED_20250709_201121.xlsx",
        "../data_cleaned/HVDC_WAREHOUSE_SIMENSE_CLEANED_20250709_201121.xlsx",
    ]

    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"📁 데이터 파일 로드: {file_path}")
            try:
                df = pd.read_excel(file_path)
                print(f"✅ 데이터 로드 성공: {len(df)} 행, {len(df.columns)} 컬럼")
                return df
            except Exception as e:
                print(f"❌ 데이터 로드 실패: {e}")
                continue

    print("⚠️ 실제 데이터 파일을 찾을 수 없습니다.")
    return None


def test_hvdc_warehouse_validation():
    """실제 HVDC 데이터 검증 테스트"""
    print("🏭 실제 HVDC 데이터 기반 창고 입출고 계산 및 품질 검증")
    print("=" * 70)

    # 1. 실제 데이터 로드
    df = load_hvdc_data()
    if df is None:
        print("❌ 테스트 중단: 데이터를 로드할 수 없습니다.")
        return

    # 2. 창고 입출고 계산기 테스트
    print("\n📊 창고 입출고 계산 테스트")
    print("-" * 40)

    calculator = WarehouseIOCalculator()

    # Final Location 계산
    result_df = calculator.calculate_final_location(df)
    print(f"✅ Final_Location 계산 완료: {len(result_df)} 행")

    # 창고 입고 계산
    inbound_result = calculator.calculate_warehouse_inbound(result_df)
    print(f"📥 총 입고: {inbound_result['total_inbound']} 건")
    print(
        f"📥 창고별 입고: {dict(list(inbound_result['by_warehouse'].items())[:3])}..."
    )

    # 창고 출고 계산
    outbound_result = calculator.calculate_warehouse_outbound(result_df)
    print(f"📤 총 출고: {outbound_result['total_outbound']} 건")

    # 창고 재고 계산
    inventory_result = calculator.calculate_warehouse_inventory(result_df)
    print(f"📦 현재 재고: {inventory_result['current_inventory']} 건")

    # 3. 데이터 품질 검증 테스트
    print("\n🔍 데이터 품질 검증 테스트")
    print("-" * 40)

    validator = DataQualityValidator()

    # Excel 피벗 테이블 대조
    excel_validation = validator.validate_against_excel(result_df)
    print(f"📊 Excel 대조 검증: {excel_validation['validation_status']}")
    print(f"📊 정확도 점수: {excel_validation['accuracy_score']:.2%}")

    # WH_HANDLING 검증
    wh_validation = validator.validate_wh_handling_counts(result_df)
    print(
        f"🔢 WH_HANDLING 검증: {'통과' if wh_validation['validation_passed'] else '실패'}"
    )
    print(
        f"🔢 허용 오차 초과: {'예' if wh_validation['tolerance_exceeded'] else '아니오'}"
    )

    # 4. 종합 검증
    print("\n🎯 종합 검증 결과")
    print("-" * 40)

    comprehensive_validator = ComprehensiveWarehouseValidator()
    comprehensive_result = (
        comprehensive_validator.validate_comprehensive_warehouse_data(result_df)
    )

    print(f"🏆 전체 상태: {comprehensive_result['overall_status']}")
    print(f"📈 컴포넌트 점수:")
    for component, score in comprehensive_result["component_scores"].items():
        print(f"   - {component}: {score:.2%}")

    # 5. 상세 결과 출력
    if excel_validation["validation_status"] != "PASS":
        print("\n⚠️ Excel 검증 상세 결과:")
        error_details = excel_validation["error_details"]
        if isinstance(error_details, dict):
            for level, details in error_details.items():
                if isinstance(details, dict):
                    print(
                        f"   Level {level}: 우리={details['our_count']}, Excel={details['excel_count']}, 차이={details['difference']}"
                    )
        elif isinstance(error_details, list):
            for error in error_details:
                print(f"   - {error}")

    # 6. 권장사항 출력
    print(f"\n💡 권장사항:")
    for recommendation in comprehensive_result["recommendations"]:
        print(f"   - {recommendation}")

    return {
        "inbound_result": inbound_result,
        "outbound_result": outbound_result,
        "inventory_result": inventory_result,
        "excel_validation": excel_validation,
        "wh_validation": wh_validation,
        "comprehensive_result": comprehensive_result,
    }


def generate_validation_report(results):
    """검증 결과 리포트 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"HVDC_Warehouse_Validation_Report_{timestamp}.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("🏭 HVDC 창고 입출고 계산 및 품질 검증 리포트\n")
        f.write("=" * 60 + "\n")
        f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 입출고 결과
        f.write("📊 창고 입출고 계산 결과\n")
        f.write("-" * 30 + "\n")
        f.write(f"총 입고: {results['inbound_result']['total_inbound']} 건\n")
        f.write(f"총 출고: {results['outbound_result']['total_outbound']} 건\n")
        f.write(f"현재 재고: {results['inventory_result']['current_inventory']} 건\n\n")

        # 품질 검증 결과
        f.write("🔍 데이터 품질 검증 결과\n")
        f.write("-" * 30 + "\n")
        f.write(
            f"Excel 대조 검증: {results['excel_validation']['validation_status']}\n"
        )
        f.write(f"정확도 점수: {results['excel_validation']['accuracy_score']:.2%}\n")
        f.write(
            f"WH_HANDLING 검증: {'통과' if results['wh_validation']['validation_passed'] else '실패'}\n\n"
        )

        # 종합 결과
        f.write("🎯 종합 검증 결과\n")
        f.write("-" * 30 + "\n")
        f.write(f"전체 상태: {results['comprehensive_result']['overall_status']}\n")
        f.write("컴포넌트 점수:\n")
        for component, score in results["comprehensive_result"][
            "component_scores"
        ].items():
            f.write(f"  - {component}: {score:.2%}\n")

    print(f"📄 검증 리포트 생성: {report_file}")
    return report_file


if __name__ == "__main__":
    # 실제 HVDC 데이터 검증 실행
    results = test_hvdc_warehouse_validation()

    if results:
        # 리포트 생성
        report_file = generate_validation_report(results)

        print(f"\n🎉 HVDC 창고 입출고 계산 및 품질 검증 완료!")
        print(f"📄 상세 리포트: {report_file}")

    print("\n🔧 추천 명령어:")
    print("/automate test-pipeline [전체 검증 자동화]")
    print("/validate-data code-quality [품질 검증 로직 점검]")
    print("/visualize_data --type=warehouse-io [창고 입출고 시각화]")
