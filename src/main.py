"""
HVDC Excel Reporter - Main Execution File
"""

from src.reporting.reporter import HVDCExcelReporter
from src.utils import setup_logging


def main():
    """
    Main function to generate the HVDC Excel report.
    """
    logger = setup_logging()

    print("📋 HVDC 입고 로직 구현 및 집계 시스템 종합 보고서")
    print("✅ Status_Location 기반 완벽한 입출고 재고 로직")
    print("Samsung C&T · ADNOC · DSV Partnership")
    print("=" * 80)

    try:
        reporter = HVDCExcelReporter()
        excel_file = reporter.generate_report()

        print(f"\n🎉 HVDC 입고 로직 종합 리포트 생성 완료! (SQM 확장판)")
        print(f"📁 파일명: {excel_file}")

        stats = reporter.stats
        if stats:
            print(f"📊 총 데이터: {len(stats['processed_data']):,}건")

            sqm_quality = stats.get("sqm_data_quality", {})
            if sqm_quality:
                actual_percentage = sqm_quality.get("actual_sqm_percentage", 0)
                estimated_percentage = sqm_quality.get("estimated_sqm_percentage", 0)
                print(f"\n🔍 SQM 데이터 품질 분석:")
                print(f"   ✅ 실제 SQM 데이터: {actual_percentage:.1f}%")
                print(f"   ❌ PKG 기반 추정: {estimated_percentage:.1f}%")

    except Exception as e:
        logger.error(f"❌ 시스템 생성 실패: {str(e)}")
        raise


if __name__ == "__main__":
    main()
