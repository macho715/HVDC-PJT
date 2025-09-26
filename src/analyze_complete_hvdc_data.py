#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC 프로젝트 전체 5552건 실제 데이터 입고/출고 계산 분석
MACHO-GPT LATTICE 모드 - 창고 최적화 및 물류 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# HVDC 관련 모듈 import
try:
    from src.warehouse_io_calculator import WarehouseIOCalculator
    from hvdc_excel_reporter_final import HVDCExcelReporterFinal
except ImportError:
    print("⚠️  HVDC 모듈 import 실패, 기본 계산 로직으로 진행")


class CompleteHVDCAnalyzer:
    """전체 HVDC 데이터 분석 클래스"""

    def __init__(self):
        self.data_file = project_root / "HVDC_complete_data_original.xlsx"
        self.calculator = None
        self.reporter = None
        self.df = None
        self.analysis_results = {}

    def load_complete_data(self):
        """전체 5552건 데이터 로드"""
        print("📊 전체 HVDC 데이터 로드 중...")

        try:
            # Excel 파일 읽기
            self.df = pd.read_excel(self.data_file, sheet_name=0)
            print(f"✅ 데이터 로드 완료: {len(self.df):,}건")

            # 기본 정보 출력
            print(f"📋 컬럼 수: {len(self.df.columns)}")
            print(
                f"📅 데이터 기간: {self.df.iloc[:, 1].min()} ~ {self.df.iloc[:, 1].max()}"
            )

            # 컬럼명 확인
            print(f"🔍 주요 컬럼: {list(self.df.columns[:10])}")

            return True

        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False

    def initialize_calculators(self):
        """계산기 초기화"""
        try:
            self.calculator = WarehouseIOCalculator()
            self.reporter = HVDCExcelReporterFinal()
            print("✅ 계산기 초기화 완료")
            return True
        except Exception as e:
            print(f"⚠️  계산기 초기화 실패: {e}")
            return False

    def analyze_warehouse_operations(self):
        """창고 운영 분석"""
        print("\n🏭 창고 운영 분석 시작...")

        if self.calculator is None:
            print("⚠️  기본 계산 로직으로 진행")
            return self.basic_warehouse_analysis()

        try:
            # 입고 분석
            print("📥 입고 분석 중...")
            inbound_result = self.calculator.calculate_warehouse_inbound(self.df)

            # 출고 분석
            print("📤 출고 분석 중...")
            outbound_result = self.calculator.calculate_warehouse_outbound(self.df)

            # 재고 분석
            print("📦 재고 분석 중...")
            inventory_result = self.calculator.calculate_warehouse_inventory(self.df)

            # 현장 입고 분석
            print("🏗️  현장 입고 분석 중...")
            site_inbound_result = self.calculator.calculate_site_inbound(self.df)

            # 직배송 분석
            print("🚚 직배송 분석 중...")
            direct_delivery_result = self.calculator.calculate_direct_delivery(self.df)

            self.analysis_results = {
                "inbound": inbound_result,
                "outbound": outbound_result,
                "inventory": inventory_result,
                "site_inbound": site_inbound_result,
                "direct_delivery": direct_delivery_result,
            }

            return True

        except Exception as e:
            print(f"❌ 창고 운영 분석 실패: {e}")
            return False

    def basic_warehouse_analysis(self):
        """기본 창고 분석 (모듈 없이)"""
        print("🔧 기본 창고 분석 수행...")

        # 날짜 컬럼 찾기
        date_columns = []
        warehouse_columns = []
        site_columns = []

        for col in self.df.columns:
            col_lower = col.lower()
            if any(
                date_word in col_lower
                for date_word in ["date", "arrival", "inbound", "outbound"]
            ):
                date_columns.append(col)
            elif any(wh_word in col_lower for wh_word in ["warehouse", "wh", "창고"]):
                warehouse_columns.append(col)
            elif any(
                site_word in col_lower for site_word in ["site", "현장", "project"]
            ):
                site_columns.append(col)

        print(f"📅 날짜 컬럼: {date_columns}")
        print(f"🏭 창고 컬럼: {warehouse_columns}")
        print(f"🏗️  현장 컬럼: {site_columns}")

        # 기본 통계
        total_records = len(self.df)
        non_null_dates = sum(self.df[date_columns].notna().any(axis=1))

        self.analysis_results = {
            "total_records": total_records,
            "date_columns": date_columns,
            "warehouse_columns": warehouse_columns,
            "site_columns": site_columns,
            "records_with_dates": non_null_dates,
            "date_coverage": non_null_dates / total_records * 100,
        }

        return True

    def generate_monthly_analysis(self):
        """월별 분석 생성"""
        print("\n📊 월별 분석 생성 중...")

        if self.df is None:
            print("❌ 데이터가 로드되지 않음")
            return False

        try:
            # 날짜 컬럼 찾기
            date_cols = [
                col
                for col in self.df.columns
                if "date" in col.lower() or "arrival" in col.lower()
            ]

            if not date_cols:
                print("⚠️  날짜 컬럼을 찾을 수 없음")
                return False

            # 첫 번째 날짜 컬럼 사용
            date_col = date_cols[0]
            print(f"📅 사용할 날짜 컬럼: {date_col}")

            # 날짜 변환
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors="coerce")

            # 월별 집계
            monthly_data = self.df.groupby(self.df[date_col].dt.to_period("M")).size()

            print(f"📈 월별 데이터 분포:")
            for month, count in monthly_data.items():
                print(f"  {month}: {count:,}건")

            return True

        except Exception as e:
            print(f"❌ 월별 분석 실패: {e}")
            return False

    def export_analysis_results(self):
        """분석 결과 내보내기"""
        print("\n💾 분석 결과 내보내기 중...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Excel 파일로 내보내기
        output_file = project_root / f"complete_hvdc_analysis_{timestamp}.xlsx"

        try:
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                # 원본 데이터
                self.df.to_excel(writer, sheet_name="원본데이터", index=False)

                # 분석 결과 요약
                summary_data = []
                for key, value in self.analysis_results.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            summary_data.append(
                                {"분석항목": f"{key}_{sub_key}", "값": sub_value}
                            )
                    else:
                        summary_data.append({"분석항목": key, "값": value})

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="분석결과", index=False)

                # 월별 분석 (가능한 경우)
                try:
                    if 'monthly_data' in locals() and monthly_data is not None:
                        monthly_data.to_frame("건수").to_excel(
                            writer, sheet_name="월별분석"
                        )
                except NameError:
                    # monthly_data가 정의되지 않은 경우 스킵
                    pass

            print(f"✅ 분석 결과 저장 완료: {output_file}")
            return str(output_file)

        except Exception as e:
            print(f"❌ 결과 내보내기 실패: {e}")
            return None

    def print_summary(self):
        """분석 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 HVDC 전체 데이터 분석 결과 요약")
        print("=" * 60)

        if "total_records" in self.analysis_results:
            print(f"📊 총 데이터 건수: {self.analysis_results['total_records']:,}건")
            print(
                f"📅 날짜 데이터 포함: {self.analysis_results['records_with_dates']:,}건"
            )
            print(f"📈 데이터 커버리지: {self.analysis_results['date_coverage']:.1f}%")

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

        if "inventory" in self.analysis_results:
            inventory = self.analysis_results["inventory"]
            print(f"\n📦 재고 분석:")
            print(f"  총 재고: {inventory.get('total_inventory', 0):,}건")
            print(f"  창고별 재고: {inventory.get('by_warehouse', {})}")

        if "direct_delivery" in self.analysis_results:
            direct = self.analysis_results["direct_delivery"]
            print(f"\n🚚 직배송 분석:")
            print(f"  총 직배송: {direct.get('total_direct', 0):,}건")

        print("\n" + "=" * 60)


def main():
    """메인 실행 함수"""
    print("🚀 HVDC 전체 데이터 분석 시작")
    print("=" * 60)

    analyzer = CompleteHVDCAnalyzer()

    # 1. 데이터 로드
    if not analyzer.load_complete_data():
        return

    # 2. 계산기 초기화
    analyzer.initialize_calculators()

    # 3. 창고 운영 분석
    if not analyzer.analyze_warehouse_operations():
        print("⚠️  창고 운영 분석 실패, 기본 분석으로 진행")

    # 4. 월별 분석
    analyzer.generate_monthly_analysis()

    # 5. 결과 출력
    analyzer.print_summary()

    # 6. 결과 내보내기
    output_file = analyzer.export_analysis_results()

    if output_file:
        print(f"\n✅ 분석 완료! 결과 파일: {output_file}")
    else:
        print("\n⚠️  결과 내보내기 실패")

    print("\n🔧 **추천 명령어:**")
    print("/logi_master analyze_complete_data [전체 데이터 분석 - 상세 결과 확인]")
    print("/switch_mode LATTICE [창고 최적화 모드 - 입출고 로직 검증]")
    print("/validate_data warehouse_operations [창고 운영 데이터 검증 - 정확도 확인]")
    print("/automate test-pipeline [전체 테스트 파이프라인 실행 - 시스템 검증]")


if __name__ == "__main__":
    main()
