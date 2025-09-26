"""
📋 HVDC 개선된 창고 입출고 계산 로직 테스트
TDD Red → Green → Refactor 사이클 적용
"""

import pandas as pd
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestImprovedWarehouseLogic:
    """개선된 창고 입출고 계산 로직 테스트"""
    
    def setup_method(self):
        """테스트 데이터 준비"""
        # 실제 HVDC 데이터 구조 시뮬레이션
        self.test_data = {
            'Transaction_ID': ['T001', 'T002', 'T003', 'T004'],
            'DSV Indoor': [
                datetime(2024, 1, 15),
                datetime(2024, 1, 20),
                pd.NaT,
                datetime(2024, 2, 5)
            ],
            'DSV Outdoor': [
                pd.NaT,
                datetime(2024, 1, 25),
                datetime(2024, 1, 10),
                pd.NaT
            ],
            'MIR': [
                datetime(2024, 1, 20),
                datetime(2024, 2, 1),
                datetime(2024, 1, 15),
                datetime(2024, 2, 10)
            ],
            'SHU': [
                pd.NaT,
                pd.NaT,
                pd.NaT,
                pd.NaT
            ]
        }
        self.df = pd.DataFrame(self.test_data)
    
    def test_warehouse_inbound_correct_should_count_monthly_arrivals(self):
        """창고 입고 계산이 해당 월 도착 건수를 정확히 계산해야 함"""
        # Given: 2024년 1월 기간과 DSV Indoor 창고
        period = pd.Timestamp('2024-01-01')
        warehouse_name = 'DSV Indoor'
        
        # When: 입고 계산 실행 (아직 구현되지 않음 - RED)
        calculator = ImprovedWarehouseCalculator()
        result = calculator.calculate_warehouse_inbound_correct(
            self.df, warehouse_name, period
        )
        
        # Then: 2024년 1월 DSV Indoor 도착 건수 = 2건
        assert result == 2, f"Expected 2 inbound items, got {result}"
    
    def test_warehouse_outbound_real_should_track_time_sequence(self):
        """출고 계산이 시간 순서를 정확히 추적해야 함"""
        # Given: 2024년 1월 기간과 DSV Indoor 창고
        period = pd.Timestamp('2024-01-01')
        warehouse_name = 'DSV Indoor'
        
        # When: 출고 계산 실행 (아직 구현되지 않음 - RED)
        calculator = ImprovedWarehouseCalculator()
        result = calculator.calculate_warehouse_outbound_real(
            self.df, warehouse_name, period
        )
        
        # Then: DSV Indoor에서 다음 단계로 이동한 건수 = 2건 (T001: 1/15→1/20 MIR, T002: 1/20→1/25 DSV Outdoor)
        assert result == 2, f"Expected 2 outbound items in January, got {result}"
    
    def test_warehouse_outbound_should_count_same_month_movements(self):
        """출고 계산이 같은 월 내 이동도 정확히 계산해야 함"""
        # Given: 2024년 2월 기간과 DSV Indoor 창고
        period = pd.Timestamp('2024-02-01')
        warehouse_name = 'DSV Indoor'
        
        # When: 출고 계산 실행
        calculator = ImprovedWarehouseCalculator()
        result = calculator.calculate_warehouse_outbound_real(
            self.df, warehouse_name, period
        )
        
        # Then: 2월에 DSV Indoor에서 출고된 건수 = 1건 (T004: 2/5 입고 → 2/10 MIR 출고)
        assert result == 1, f"Expected 1 outbound item in February, got {result}"
    
    def test_warehouse_outbound_should_handle_warehouse_to_warehouse_movement(self):
        """출고 계산이 창고 간 이동을 정확히 처리해야 함"""
        # Given: 창고 간 이동 데이터
        complex_data = {
            'Transaction_ID': ['T005'],
            'DSV Indoor': [datetime(2024, 1, 10)],
            'DSV Outdoor': [datetime(2024, 1, 15)],
            'MIR': [datetime(2024, 1, 20)]
        }
        complex_df = pd.DataFrame(complex_data)
        period = pd.Timestamp('2024-01-01')
        
        # When: DSV Indoor 출고 계산
        calculator = ImprovedWarehouseCalculator()
        result = calculator.calculate_warehouse_outbound_real(
            complex_df, 'DSV Indoor', period
        )
        
        # Then: DSV Indoor → DSV Outdoor 이동 = 1건
        assert result == 1, f"Expected 1 warehouse-to-warehouse movement, got {result}"
    
    def test_warehouse_calculations_should_maintain_consistency(self):
        """창고 계산이 논리적 일관성을 유지해야 함"""
        # Given: 전체 데이터와 계산기
        calculator = ImprovedWarehouseCalculator()
        period = pd.Timestamp('2024-01-01')
        
        # When: 모든 창고의 입출고 계산
        warehouses = ['DSV Indoor', 'DSV Outdoor']
        inbound_total = 0
        outbound_total = 0
        
        for warehouse in warehouses:
            inbound = calculator.calculate_warehouse_inbound_correct(
                self.df, warehouse, period
            )
            outbound = calculator.calculate_warehouse_outbound_real(
                self.df, warehouse, period
            )
            inbound_total += inbound
            outbound_total += outbound
        
        # Then: 입고 총합 >= 출고 총합 (논리적 일관성)
        assert inbound_total >= outbound_total, \
            f"Inbound ({inbound_total}) should be >= Outbound ({outbound_total})"
    
    def test_warehouse_calculator_should_handle_empty_data(self):
        """창고 계산기가 빈 데이터를 안전하게 처리해야 함"""
        # Given: 빈 DataFrame
        empty_df = pd.DataFrame()
        period = pd.Timestamp('2024-01-01')
        
        # When: 계산 실행
        calculator = ImprovedWarehouseCalculator()
        
        # Then: 예외 없이 0 반환
        assert calculator.calculate_warehouse_inbound_correct(
            empty_df, 'DSV Indoor', period
        ) == 0
        assert calculator.calculate_warehouse_outbound_real(
            empty_df, 'DSV Indoor', period
        ) == 0
    
    def test_warehouse_calculator_should_validate_period_format(self):
        """창고 계산기가 기간 형식을 검증해야 함"""
        # Given: 잘못된 기간 형식
        invalid_period = "2024-01-01"  # 문자열 (pandas.Timestamp 아님)
        
        # When & Then: 타입 오류 발생 예상
        calculator = ImprovedWarehouseCalculator()
        with pytest.raises(AttributeError):
            calculator.calculate_warehouse_inbound_correct(
                self.df, 'DSV Indoor', invalid_period
            )


class ImprovedWarehouseCalculator:
    """개선된 창고 입출고 계산기 (구현 예정)"""
    
    def __init__(self):
        """계산기 초기화"""
        self.real_warehouse_columns = {
            'DSV Indoor': 'DSV_Indoor',
            'DSV Outdoor': 'DSV_Outdoor',
            'DSV Al Markaz': 'DSV_Al_Markaz',
            'AAA  Storage': 'AAA_Storage',
            'Hauler Indoor': 'Hauler_Indoor',
            'DSV MZP': 'DSV_MZP',
            'MOSB': 'MOSB'
        }
        
        self.real_site_columns = {
            'MIR': 'MIR',
            'SHU': 'SHU',
            'DAS': 'DAS',
            'AGI': 'AGI'
        }
    
    def calculate_warehouse_inbound_correct(self, df, warehouse_name, period):
        """창고 입고 계산 (개선된 로직 구현)"""
        # 빈 DataFrame 처리
        if df.empty or warehouse_name not in df.columns:
            return 0
        
        # 해당 창고의 도착 날짜 추출
        warehouse_dates = df[warehouse_name].dropna()
        
        # 해당 월에 도착한 건수 계산
        month_mask = warehouse_dates.dt.to_period('M') == period.to_period('M')
        return month_mask.sum()
    
    def calculate_warehouse_outbound_real(self, df, warehouse_name, period):
        """🔍 시간 순서 기반 정확한 출고 계산"""
        # 빈 DataFrame 처리
        if df.empty or warehouse_name not in df.columns:
            return 0
        
        outbound_count = 0
        
        # Step 1: 해당 창고 방문 케이스 필터링
        warehouse_visited = df[df[warehouse_name].notna()].copy()
        
        if len(warehouse_visited) == 0:
            return 0
        
        # Step 2: 각 케이스별 개별 추적
        for idx, row in warehouse_visited.iterrows():
            warehouse_date = row[warehouse_name]  # 창고 도착 시점
            
            # Step 3: 다음 단계 이동 날짜 탐색
            next_dates = []
            
            # 3-1: 다른 창고로 이동 확인
            for other_wh in self.real_warehouse_columns.keys():
                if other_wh != warehouse_name and other_wh in row.index:
                    other_date = row[other_wh]
                    if pd.notna(other_date) and other_date > warehouse_date:
                        next_dates.append(other_date)
            
            # 3-2: 현장으로 이동 확인
            for site_name in self.real_site_columns.keys():
                if site_name in row.index:
                    site_date = row[site_name]
                    if pd.notna(site_date) and site_date > warehouse_date:
                        next_dates.append(site_date)
            
            # Step 4: 가장 빠른 다음 단계로 출고 시점 결정
            if next_dates:
                earliest_next_date = min(next_dates)
                if earliest_next_date.to_period('M') == period.to_period('M'):
                    outbound_count += 1
                    
        return outbound_count


if __name__ == "__main__":
    """테스트 실행"""
    print("🔴 TDD Red Phase: 실패 테스트 실행")
    print("테스트가 실패할 것으로 예상됩니다 (아직 구현되지 않음)")
    
    # 테스트 실행
    pytest.main([__file__, "-v"]) 