"""
🔌 HVDC Excel Recreator v2.8.4
Samsung C&T × ADNOC·DSV Partnership | 실제 RAW DATA 100% 활용

Based on HVDC_Real_Data_Excel_System_REV.MD specifications:
- 5개 시트 구조: 전체 트랜잭션, 분석요약, Pre-Arrival, 창고별, 현장별
- 7,405 total records (HITACHI 5,552 + SIMENSE 1,853)
- Multi-Level Headers
- Flow Code 0-4 classification

Author: MACHO-GPT v3.5
Date: 2025-01-06
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HVDCExcelRecreator:
    """HVDC Excel 보고서 재생성기 - REV.MD 구조 기반"""

    def __init__(self):
        self.data_dir = Path("data")
        self.output_dir = Path("src")

        # MACHO-GPT v3.5 compliance attributes
        self.confidence_threshold = 0.95
        self.containment_mode = "LATTICE"  # Default mode for logistics

        # 실제 창고 컬럼 매핑 (REV.MD 기반)
        self.warehouse_columns = {
            "DSV Indoor": "DSV Indoor",
            "DSV Outdoor": "DSV Outdoor",
            "DSV Al Markaz": "DSV Al Markaz",
            "DSV MZP": "DSV MZP",
            "AAA Storage": "AAA Storage",
            "Hauler Indoor": "Hauler Indoor",
            "MOSB": "MOSB",
        }

        # 실제 현장 컬럼 매핑 (REV.MD 기반)
        self.site_columns = {"AGI": "AGI", "DAS": "DAS", "MIR": "MIR", "SHU": "SHU"}

        self.df_combined = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def standardize_case_list(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        헤더 정규화 및 표준화 (REV.MD 규격)
        - 헤더 공백·대/소문자 정비
        - total handling → FLOW_0…4 매핑
        """
        # 헤더 정규화
        df.columns = df.columns.str.strip().str.lower()

        # total handling 컬럼을 wh handling으로 매핑
        if "total handling" in df.columns:
            df["wh handling"] = df["total handling"]

        return df

    def load_raw_data(self) -> pd.DataFrame:
        """실제 RAW DATA 로드 및 통합 (REV.MD 규격: 7,405건)"""
        logger.info("🔍 실제 RAW DATA 로딩 시작...")

        # HITACHI 파일 로드
        hitachi_path = self.data_dir / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        df_hitachi = pd.read_excel(hitachi_path, sheet_name="Case List")
        df_hitachi = self.standardize_case_list(df_hitachi)
        df_hitachi["VENDOR"] = "HITACHI"
        logger.info(f"✅ HITACHI 데이터 로드 완료: {len(df_hitachi)}건")

        # SIMENSE 파일 로드
        simense_path = self.data_dir / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        df_simense = pd.read_excel(simense_path, sheet_name="Case List")
        df_simense = self.standardize_case_list(df_simense)
        df_simense["VENDOR"] = "SIMENSE"
        logger.info(f"✅ SIMENSE 데이터 로드 완료: {len(df_simense)}건")

        # 데이터 통합
        self.df_combined = pd.concat([df_hitachi, df_simense], ignore_index=True)

        # Status_Location이 'ALL'인 집계행 제거 (REV.MD 트러블슈팅 참조)
        if "status_location" in self.df_combined.columns:
            self.df_combined = self.df_combined[
                self.df_combined["status_location"] != "ALL"
            ]

        logger.info(f"✅ 통합 데이터 완료: {len(self.df_combined)}건")

        # 날짜 컬럼 변환
        self._convert_date_columns()

        # Flow Code 계산
        self._calculate_flow_codes()

        return self.df_combined

    def _convert_date_columns(self):
        """날짜 컬럼 변환"""
        date_columns = []

        # 창고 관련 날짜 컬럼 변환
        for col in self.warehouse_columns.values():
            if col.lower() in self.df_combined.columns:
                self.df_combined[col] = pd.to_datetime(
                    self.df_combined[col.lower()], errors="coerce"
                )
                date_columns.append(col)

        # 현장 관련 날짜 컬럼 변환
        for col in self.site_columns.values():
            if col.lower() in self.df_combined.columns:
                self.df_combined[col] = pd.to_datetime(
                    self.df_combined[col.lower()], errors="coerce"
                )
                date_columns.append(col)

        logger.info(f"📅 날짜 컬럼 변환 완료: {len(date_columns)}개")

    def _calculate_flow_codes(self):
        """Flow Code 0-4 계산 (REV.MD 규격)"""
        logger.info("📊 Flow Code 계산 시작...")

        if "wh handling" in self.df_combined.columns:
            # wh handling 컬럼 기반 Flow Code 계산
            self.df_combined["FLOW_CODE"] = (
                self.df_combined["wh handling"].fillna(0).astype(int)
            )

            # Flow Code 범위 제한 (0-4)
            self.df_combined["FLOW_CODE"] = self.df_combined["FLOW_CODE"].clip(0, 4)
        else:
            # 대안: 창고 경유 횟수 기반 계산
            self.df_combined["FLOW_CODE"] = 0
            for idx, row in self.df_combined.iterrows():
                warehouse_count = 0
                for col in self.warehouse_columns.values():
                    if col.lower() in self.df_combined.columns and pd.notna(
                        row[col.lower()]
                    ):
                        warehouse_count += 1
                self.df_combined.loc[idx, "FLOW_CODE"] = min(warehouse_count, 4)

        # Flow Code 분포 로깅
        flow_distribution = self.df_combined["FLOW_CODE"].value_counts().sort_index()
        for code, count in flow_distribution.items():
            logger.info(f"  Flow Code {code}: {count}건")

        logger.info("📊 Flow Code 계산 완료")

    def create_sheet1_transaction_data(self) -> pd.DataFrame:
        """Sheet 1: 전체_트랜잭션_FLOWCODE0-4"""
        logger.info("📋 Sheet 1: 전체 트랜잭션 데이터 생성 중...")

        # 핵심 컬럼 선택
        core_columns = ["VENDOR", "FLOW_CODE"]

        # 창고 컬럼 추가
        for col in self.warehouse_columns.values():
            if col.lower() in self.df_combined.columns:
                core_columns.append(col)

        # 현장 컬럼 추가
        for col in self.site_columns.values():
            if col.lower() in self.df_combined.columns:
                core_columns.append(col)

        # 기타 중요 컬럼 추가
        other_columns = ["status_location", "wh handling"]
        for col in other_columns:
            if col in self.df_combined.columns:
                core_columns.append(col)

        # 사용 가능한 컬럼만 선택
        available_columns = [
            col for col in core_columns if col in self.df_combined.columns
        ]

        sheet1_data = self.df_combined[available_columns].copy()

        logger.info(
            f"✅ Sheet 1 생성 완료: {len(sheet1_data)}건, {len(available_columns)}개 컬럼"
        )
        return sheet1_data

    def create_sheet2_flowcode_analysis(self) -> pd.DataFrame:
        """Sheet 2: FLOWCODE0-4_분석요약"""
        logger.info("📊 Sheet 2: Flow Code 분석 생성 중...")

        # Flow Code별 분포 계산
        flowcode_stats = (
            self.df_combined.groupby("FLOW_CODE")
            .agg({"VENDOR": "count"})
            .rename(columns={"VENDOR": "Count"})
        )

        # 백분율 계산
        total_count = len(self.df_combined)
        flowcode_stats["Percentage"] = (
            flowcode_stats["Count"] / total_count * 100
        ).round(2)

        # 설명 추가
        flowcode_descriptions = {
            0: "Pre-Arrival (항구 도착 전)",
            1: "Port → Site (직접 이동)",
            2: "Port → WH → Site (창고 1개 경유)",
            3: "Port → WH → MOSB → Site (창고 2개 경유)",
            4: "Port → WH → WH → MOSB → Site (창고 3개+ 경유)",
        }

        flowcode_stats["Description"] = flowcode_stats.index.map(flowcode_descriptions)

        # 전체 5개 Flow Code가 모두 있도록 보장
        for code in range(5):
            if code not in flowcode_stats.index:
                flowcode_stats.loc[code] = [0, 0.0, flowcode_descriptions[code]]

        flowcode_stats = flowcode_stats.sort_index()

        logger.info(f"✅ Sheet 2 생성 완료: {len(flowcode_stats)}개 Flow Code 분석")
        return flowcode_stats

    def create_sheet3_pre_arrival_analysis(self) -> pd.DataFrame:
        """Sheet 3: Pre_Arrival_상세분석"""
        logger.info("🚢 Sheet 3: Pre-Arrival 상세 분석 생성 중...")

        # FLOW_CODE = 0인 데이터 필터링
        pre_arrival_data = self.df_combined[self.df_combined["FLOW_CODE"] == 0].copy()

        if len(pre_arrival_data) == 0:
            logger.warning("⚠️ Pre-Arrival 데이터가 없습니다.")
            return pd.DataFrame({"Message": ["Pre-Arrival 데이터가 없습니다."]})

        logger.info(f"✅ Sheet 3 생성 완료: {len(pre_arrival_data)}건 Pre-Arrival 분석")
        return pre_arrival_data

    def create_sheet4_warehouse_multilevel(self) -> pd.DataFrame:
        """Sheet 4: 창고별_월별_입출고_완전체계 (Multi-Level Header)"""
        logger.info("🏭 Sheet 4: 창고별 월별 입출고 Multi-Level Header 생성 중...")

        # 날짜 범위 추출
        all_dates = []
        for col in self.warehouse_columns.values():
            if col in self.df_combined.columns:
                dates = self.df_combined[col].dropna()
                all_dates.extend(dates.tolist())
            elif col.lower() in self.df_combined.columns:
                dates = self.df_combined[col.lower()].dropna()
                all_dates.extend(dates.tolist())

        if not all_dates:
            logger.warning("⚠️ 창고 날짜 데이터가 없습니다.")
            return pd.DataFrame({"Message": ["창고 날짜 데이터가 없습니다."]})

        min_date = min(all_dates)
        max_date = max(all_dates)

        # 월별 기간 생성
        periods = pd.date_range(
            start=min_date.replace(day=1), end=max_date.replace(day=1), freq="MS"
        )

        # Multi-Level Header 구성
        level_0 = ["Month"]
        level_1 = [""]

        for warehouse_name in self.warehouse_columns.keys():
            level_0.extend(["입고", "출고"])
            level_1.extend([warehouse_name, warehouse_name])

        multi_columns = pd.MultiIndex.from_arrays(
            [level_0, level_1], names=["구분", "Warehouse"]
        )

        # 데이터 계산
        warehouse_data = []
        for period in periods:
            row_data = [period.strftime("%Y-%m")]

            for warehouse_name, warehouse_col in self.warehouse_columns.items():
                # 입고 계산
                inbound = self._calculate_warehouse_inbound(warehouse_col, period)
                # 출고 계산
                outbound = self._calculate_warehouse_outbound(warehouse_col, period)

                row_data.extend([inbound, outbound])

            warehouse_data.append(row_data)

        # DataFrame 생성
        result = pd.DataFrame(warehouse_data, columns=multi_columns)

        logger.info(
            f"✅ Sheet 4 생성 완료: {len(result)}개월 × {len(self.warehouse_columns)}개 창고"
        )
        return result

    def create_sheet5_site_multilevel(self) -> pd.DataFrame:
        """Sheet 5: 현장별_월별_입고재고_완전체계 (Multi-Level Header)"""
        logger.info("🏗️ Sheet 5: 현장별 월별 입고재고 Multi-Level Header 생성 중...")

        # 날짜 범위 추출
        all_dates = []
        for col in self.site_columns.values():
            if col in self.df_combined.columns:
                dates = self.df_combined[col].dropna()
                all_dates.extend(dates.tolist())
            elif col.lower() in self.df_combined.columns:
                dates = self.df_combined[col.lower()].dropna()
                all_dates.extend(dates.tolist())

        if not all_dates:
            logger.warning("⚠️ 현장 날짜 데이터가 없습니다.")
            return pd.DataFrame({"Message": ["현장 날짜 데이터가 없습니다."]})

        min_date = min(all_dates)
        max_date = max(all_dates)

        # 월별 기간 생성
        periods = pd.date_range(
            start=min_date.replace(day=1), end=max_date.replace(day=1), freq="MS"
        )

        # Multi-Level Header 구성
        level_0 = ["Month"]
        level_1 = [""]

        for site_name in self.site_columns.keys():
            level_0.extend(["입고", "재고"])
            level_1.extend([site_name, site_name])

        multi_columns = pd.MultiIndex.from_arrays(
            [level_0, level_1], names=["구분", "Site"]
        )

        # 데이터 계산
        site_data = []
        for period in periods:
            row_data = [period.strftime("%Y-%m")]

            for site_name, site_col in self.site_columns.items():
                # 입고 계산
                inbound = self._calculate_site_inbound(site_col, period)
                # 재고 계산
                inventory = self._calculate_site_inventory(site_col, period)

                row_data.extend([inbound, inventory])

            site_data.append(row_data)

        # DataFrame 생성
        result = pd.DataFrame(site_data, columns=multi_columns)

        logger.info(
            f"✅ Sheet 5 생성 완료: {len(result)}개월 × {len(self.site_columns)}개 현장"
        )
        return result

    def _calculate_warehouse_inbound(
        self, warehouse_col: str, period: pd.Timestamp
    ) -> int:
        """창고별 월별 입고 계산 (REV.MD calculate_warehouse_inbound_correct 기반)"""
        col_name = (
            warehouse_col
            if warehouse_col in self.df_combined.columns
            else warehouse_col.lower()
        )

        if col_name not in self.df_combined.columns:
            return 0

        warehouse_dates = self.df_combined[col_name].dropna()
        month_mask = warehouse_dates.dt.to_period("M") == period.to_period("M")
        return month_mask.sum()

    def _calculate_warehouse_outbound(
        self, warehouse_col: str, period: pd.Timestamp
    ) -> int:
        """창고별 월별 출고 계산 (REV.MD calculate_warehouse_outbound_real 기반)"""
        col_name = (
            warehouse_col
            if warehouse_col in self.df_combined.columns
            else warehouse_col.lower()
        )

        if col_name not in self.df_combined.columns:
            return 0

        warehouse_visited = self.df_combined[self.df_combined[col_name].notna()].copy()
        outbound_count = 0

        for _, row in warehouse_visited.iterrows():
            warehouse_date = row[col_name]
            if pd.isna(warehouse_date):
                continue

            # 다음 단계 이동 날짜 탐색
            next_dates = []

            # 다른 창고로 이동 확인
            for other_col in self.warehouse_columns.values():
                other_col_name = (
                    other_col
                    if other_col in self.df_combined.columns
                    else other_col.lower()
                )
                if (
                    other_col_name != col_name
                    and other_col_name in self.df_combined.columns
                ):
                    other_date = row[other_col_name]
                    if pd.notna(other_date) and other_date > warehouse_date:
                        next_dates.append(other_date)

            # 현장으로 이동 확인
            for site_col in self.site_columns.values():
                site_col_name = (
                    site_col
                    if site_col in self.df_combined.columns
                    else site_col.lower()
                )
                if site_col_name in self.df_combined.columns:
                    site_date = row[site_col_name]
                    if pd.notna(site_date) and site_date > warehouse_date:
                        next_dates.append(site_date)

            # 가장 빠른 다음 단계로 출고 시점 결정
            if next_dates:
                earliest_next_date = min(next_dates)
                if earliest_next_date.to_period("M") == period.to_period("M"):
                    outbound_count += 1

        return outbound_count

    def _calculate_site_inbound(self, site_col: str, period: pd.Timestamp) -> int:
        """현장별 월별 입고 계산"""
        col_name = (
            site_col if site_col in self.df_combined.columns else site_col.lower()
        )

        if col_name not in self.df_combined.columns:
            return 0

        site_dates = self.df_combined[col_name].dropna()
        month_mask = site_dates.dt.to_period("M") == period.to_period("M")
        return month_mask.sum()

    def _calculate_site_inventory(self, site_col: str, period: pd.Timestamp) -> int:
        """현장별 월별 재고 계산 (누적 개념)"""
        col_name = (
            site_col if site_col in self.df_combined.columns else site_col.lower()
        )

        if col_name not in self.df_combined.columns:
            return 0

        site_dates = self.df_combined[col_name].dropna()

        # 해당 월 말까지 누적 도착 건수
        month_end = period + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        arrived_by_month_end = (site_dates <= month_end).sum()

        # 현재 위치 상태 확인 (보수적 접근)
        if "status_location" in self.df_combined.columns:
            site_name = [k for k, v in self.site_columns.items() if v == site_col][0]
            current_at_site = (self.df_combined["status_location"] == site_name).sum()
            return (
                min(arrived_by_month_end, current_at_site)
                if current_at_site > 0
                else arrived_by_month_end
            )

        return arrived_by_month_end

    def create_excel_report(self) -> str:
        """5개 시트 Excel 보고서 생성 (REV.MD 규격)"""
        logger.info("📊 5개 시트 Excel 보고서 생성 시작...")

        # 데이터 로드
        self.load_raw_data()

        # 출력 파일명 (REV.MD 형식 따라)
        output_filename = f"HVDC_Real_Data_Excel_System_{self.timestamp}.xlsx"
        output_path = self.output_dir / output_filename

        # Excel Writer 생성
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

            # Sheet 1: 전체 트랜잭션 데이터
            sheet1_data = self.create_sheet1_transaction_data()
            sheet1_data.to_excel(
                writer, sheet_name="전체_트랜잭션_FLOWCODE0-4", index=False
            )

            # Sheet 2: Flow Code 분석
            sheet2_data = self.create_sheet2_flowcode_analysis()
            sheet2_data.to_excel(writer, sheet_name="FLOWCODE0-4_분석요약")

            # Sheet 3: Pre-Arrival 상세 분석
            sheet3_data = self.create_sheet3_pre_arrival_analysis()
            sheet3_data.to_excel(writer, sheet_name="Pre_Arrival_상세분석", index=False)

            # Sheet 4: 창고별 월별 입출고 (Multi-Level Header)
            sheet4_data = self.create_sheet4_warehouse_multilevel()
            if not sheet4_data.empty and "Message" not in sheet4_data.columns:
                sheet4_data.to_excel(writer, sheet_name="창고별_월별_입출고_완전체계")
            else:
                sheet4_data.to_excel(
                    writer, sheet_name="창고별_월별_입출고_완전체계", index=False
                )

            # Sheet 5: 현장별 월별 입고재고 (Multi-Level Header)
            sheet5_data = self.create_sheet5_site_multilevel()
            if not sheet5_data.empty and "Message" not in sheet5_data.columns:
                sheet5_data.to_excel(writer, sheet_name="현장별_월별_입고재고_완전체계")
            else:
                sheet5_data.to_excel(
                    writer, sheet_name="현장별_월별_입고재고_완전체계", index=False
                )

        logger.info(f"✅ Excel 보고서 생성 완료: {output_path}")

        # 통계 정보 출력
        self._print_summary_statistics()

        return str(output_path)

    def get_recommended_commands(self) -> List[str]:
        """MACHO-GPT 통합을 위한 추천 명령어 반환"""
        return [
            "/logi_master analyze-warehouse-performance",
            "/validate-data flow-code-accuracy",
            "/visualize-data multi-level-dashboard",
        ]

    def _print_summary_statistics(self):
        """요약 통계 출력 (REV.MD 규격)"""
        logger.info("📊 === HVDC 5개 시트 Excel 보고서 요약 ===")
        logger.info(f"📋 총 트랜잭션 건수: {len(self.df_combined):,}건")

        # 벤더별 분포
        vendor_counts = self.df_combined["VENDOR"].value_counts()
        for vendor, count in vendor_counts.items():
            percentage = (count / len(self.df_combined)) * 100
            logger.info(f"🏭 {vendor}: {count:,}건 ({percentage:.1f}%)")

        # Flow Code 분포
        flowcode_counts = self.df_combined["FLOW_CODE"].value_counts().sort_index()
        logger.info("📊 Flow Code 분포:")
        for code, count in flowcode_counts.items():
            percentage = (count / len(self.df_combined)) * 100
            logger.info(f"   Code {code}: {count:,}건 ({percentage:.1f}%)")

        logger.info("🎉 보고서 생성 완료!")


def main():
    """메인 실행 함수"""
    print("🔌 HVDC Excel Recreator v2.8.4")
    print("=" * 50)

    try:
        # 보고서 생성기 초기화
        recreator = HVDCExcelRecreator()

        # Excel 보고서 생성
        output_path = recreator.create_excel_report()

        print(f"\n✅ 성공적으로 생성되었습니다!")
        print(f"📁 파일 위치: {output_path}")
        print(f"📊 파일 크기: {os.path.getsize(output_path) / 1024:.1f} KB")

        return output_path

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        logger.error(f"오류 발생: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    main()
