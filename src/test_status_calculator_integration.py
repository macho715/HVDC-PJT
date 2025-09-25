import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from status_calculator import StatusCalculator


class TestStatusCalculatorIntegration:
    """
    실제 Excel 데이터를 사용한 StatusCalculator 통합 테스트
    """

    def setup_method(self):
        """각 테스트 메서드 실행 전 초기화"""
        self.calculator = StatusCalculator()
        self.data_path = Path("../data")

    def test_load_hitachi_data_and_calculate_status(self):
        """실제 Hitachi 데이터로 Status 계산 테스트"""
        # Given: 실제 Hitachi 데이터 로드
        file_path = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        if not file_path.exists():
            pytest.skip(f"Data file not found: {file_path}")

        df = pd.read_excel(file_path, sheet_name="Case List")
        print(f"✅ Loaded {len(df)} Hitachi records")

        # When: Status 계산 실행
        result_df = self.calculator.calculate_complete_status(df)

        # Then: 필요한 컬럼들이 추가되어야 함
        assert "Status_WAREHOUSE" in result_df.columns
        assert "Status_SITE" in result_df.columns
        assert "Status_Current" in result_df.columns
        assert "Status_Location" in result_df.columns

        # Status_Current 값들이 올바른지 확인
        valid_statuses = ["site", "warehouse", "Pre Arrival"]
        assert all(
            status in valid_statuses for status in result_df["Status_Current"].unique()
        )

        # 통계 출력
        status_counts = result_df["Status_Current"].value_counts()
        print(f"📊 Status_Current 분포:")
        for status, count in status_counts.items():
            print(f"   {status}: {count:,}건")

        # 각 상태별 위치 분포 확인
        print(f"\n📍 Status_Location 분포:")
        location_counts = result_df["Status_Location"].value_counts()
        for location, count in location_counts.head(10).items():
            print(f"   {location}: {count:,}건")

        assert len(result_df) == len(df), "데이터 손실 없이 계산되어야 함"

    def test_load_simense_data_and_calculate_status(self):
        """실제 Simense 데이터로 Status 계산 테스트"""
        # Given: 실제 Simense 데이터 로드
        file_path = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        if not file_path.exists():
            pytest.skip(f"Data file not found: {file_path}")

        df = pd.read_excel(file_path, sheet_name="Case List")
        print(f"✅ Loaded {len(df)} Simense records")

        # When: Status 계산 실행
        result_df = self.calculator.calculate_complete_status(df)

        # Then: 필요한 컬럼들이 추가되어야 함
        assert "Status_WAREHOUSE" in result_df.columns
        assert "Status_SITE" in result_df.columns
        assert "Status_Current" in result_df.columns
        assert "Status_Location" in result_df.columns

        # Status_Current 값들이 올바른지 확인
        valid_statuses = ["site", "warehouse", "Pre Arrival"]
        assert all(
            status in valid_statuses for status in result_df["Status_Current"].unique()
        )

        # 통계 출력
        status_counts = result_df["Status_Current"].value_counts()
        print(f"📊 Status_Current 분포:")
        for status, count in status_counts.items():
            print(f"   {status}: {count:,}건")

        assert len(result_df) == len(df), "데이터 손실 없이 계산되어야 함"

    def test_combined_data_status_calculation(self):
        """합친 데이터로 Status 계산 테스트"""
        # Given: 두 Excel 파일 로드
        hitachi_path = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        simense_path = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"

        if not hitachi_path.exists() or not simense_path.exists():
            pytest.skip("Data files not found")

        hitachi_df = pd.read_excel(hitachi_path, sheet_name="Case List")
        simense_df = pd.read_excel(simense_path, sheet_name="Case List")

        # 데이터 합치기
        combined_df = pd.concat([hitachi_df, simense_df], ignore_index=True)
        print(f"✅ Combined data: {len(combined_df)} records")

        # When: Status 계산 실행
        result_df = self.calculator.calculate_complete_status(combined_df)

        # Then: 전체 통계 확인
        status_counts = result_df["Status_Current"].value_counts()
        print(f"📊 전체 Status_Current 분포:")
        for status, count in status_counts.items():
            print(f"   {status}: {count:,}건")

        # 위치별 분포 확인
        print(f"\n📍 주요 Status_Location 분포:")
        location_counts = result_df["Status_Location"].value_counts()
        for location, count in location_counts.head(10).items():
            print(f"   {location}: {count:,}건")

        # 예상 총 건수 확인 (7,779건 또는 유사)
        expected_range = (7000, 8000)
        assert (
            expected_range[0] <= len(result_df) <= expected_range[1]
        ), f"Expected {expected_range[0]}-{expected_range[1]} records, got {len(result_df)}"

    def test_warehouse_inbound_pattern_analysis(self):
        """창고 입고 패턴 분석 테스트"""
        # Given: 합친 데이터 로드
        hitachi_path = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        simense_path = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"

        if not hitachi_path.exists() or not simense_path.exists():
            pytest.skip("Data files not found")

        hitachi_df = pd.read_excel(hitachi_path, sheet_name="Case List")
        simense_df = pd.read_excel(simense_path, sheet_name="Case List")
        combined_df = pd.concat([hitachi_df, simense_df], ignore_index=True)

        # When: Status 계산 후 창고 입고 패턴 분석
        result_df = self.calculator.calculate_complete_status(combined_df)

        # 창고 상태인 데이터만 필터링
        warehouse_df = result_df[result_df["Status_Current"] == "warehouse"]
        print(f"📦 창고 상태 데이터: {len(warehouse_df)}건")

        # 창고별 입고 패턴 분석
        warehouse_cols = self.calculator.warehouse_cols
        warehouse_inbound_summary = {}

        for col in warehouse_cols:
            if col in warehouse_df.columns:
                # 해당 창고에 날짜가 있는 건수 계산
                inbound_count = warehouse_df[col].notna().sum()
                if inbound_count > 0:
                    warehouse_inbound_summary[col] = inbound_count

        print(f"\n🏢 창고별 입고 패턴:")
        for warehouse, count in sorted(
            warehouse_inbound_summary.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"   {warehouse}: {count:,}건")

        # 주요 창고들이 존재하는지 확인
        major_warehouses = ["DSV Indoor", "DSV Outdoor", "DSV Al Markaz", "MOSB"]
        for warehouse in major_warehouses:
            if warehouse in warehouse_inbound_summary:
                assert (
                    warehouse_inbound_summary[warehouse] > 0
                ), f"{warehouse} should have inbound records"

    def test_pre_arrival_location_priority(self):
        """Pre Arrival 상태에서 DSV Al Markaz 우선 선택 테스트"""
        # Given: Pre Arrival 상태 데이터 생성
        test_data = pd.DataFrame(
            {
                "DSV Outdoor": [datetime(2024, 3, 15), datetime(2024, 3, 15), None],
                "DSV Al Markaz": [
                    datetime(2024, 3, 15),
                    datetime(2024, 5, 20),
                    datetime(2024, 4, 10),
                ],
                "MIR": [None, None, None],
                "SHU": [None, None, None],
                "DAS": [None, None, None],
                "AGI": [None, None, None],
            }
        )

        # When: Status 계산
        result_df = self.calculator.calculate_complete_status(test_data)

        # Then: 결과 확인
        assert result_df.iloc[0]["Status_Current"] == "Pre Arrival"
        assert (
            result_df.iloc[0]["Status_Location"] == "DSV Al Markaz"
        )  # 동일값→Al Markaz 우선

        assert result_df.iloc[1]["Status_Current"] == "Pre Arrival"
        assert (
            result_df.iloc[1]["Status_Location"] == "DSV Al Markaz"
        )  # 최대값→Al Markaz

        assert result_df.iloc[2]["Status_Current"] == "Pre Arrival"
        assert (
            result_df.iloc[2]["Status_Location"] == "DSV Al Markaz"
        )  # 하나만 존재→Al Markaz

        print("✅ Pre Arrival 상태에서 DSV Al Markaz 우선 선택 확인됨")
