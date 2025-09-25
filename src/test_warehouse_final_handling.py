import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from status_calculator import StatusCalculator


class TestWarehouseFinalHandling:
    """
    final handling 로직 테스트
    - 최종 창고별/현장별 현재 재고 계산
    - warehouse 항목이 겹칠 경우 최종날짜가 있는 곳으로 카운트
    """
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 초기화"""
        self.calculator = StatusCalculator()
    
    def test_warehouse_overlap_final_date_priority(self):
        """warehouse 항목이 겹칠 경우 최종날짜 기준으로 카운트"""
        # Given: 여러 창고에 동시에 있는 화물 데이터
        test_data = pd.DataFrame({
            'DSV Indoor': [datetime(2024, 2, 1), datetime(2024, 3, 1), None],
            'DSV Outdoor': [datetime(2024, 4, 15), None, datetime(2024, 5, 1)],
            'DSV Al Markaz': [datetime(2024, 3, 10), datetime(2024, 4, 20), None],
            'MOSB': [None, datetime(2024, 2, 15), datetime(2024, 3, 20)],
            'MIR': [None, None, None],
            'SHU': [None, None, None], 
            'DAS': [None, None, None],
            'AGI': [None, None, None]
        })
        
        # When: Status 계산
        result_df = self.calculator.calculate_complete_status(test_data)
        
        # Then: 최종 날짜가 있는 위치로 카운트되어야 함
        # 첫 번째 화물: DSV Outdoor (2024-04-15)가 최신
        assert result_df.iloc[0]['Status_Current'] == 'warehouse'
        assert result_df.iloc[0]['Status_Location'] == 'DSV Outdoor'
        
        # 두 번째 화물: DSV Al Markaz (2024-04-20)가 최신
        assert result_df.iloc[1]['Status_Current'] == 'warehouse'
        assert result_df.iloc[1]['Status_Location'] == 'DSV Al Markaz'
        
        # 세 번째 화물: DSV Outdoor (2024-05-01)가 유일
        assert result_df.iloc[2]['Status_Current'] == 'warehouse'
        assert result_df.iloc[2]['Status_Location'] == 'DSV Outdoor'
        
        print("✅ warehouse 겹침 시 최종날짜 우선 확인됨")
    
    def test_site_overlap_final_date_priority(self):
        """site 항목이 겹칠 경우 최종날짜 기준으로 카운트"""
        # Given: 여러 현장에 동시에 있는 화물 데이터
        test_data = pd.DataFrame({
            'DSV Indoor': [None, None, None],
            'DSV Outdoor': [None, None, None],
            'DSV Al Markaz': [None, None, None],
            'MOSB': [None, None, None],
            'MIR': [datetime(2024, 2, 1), None, datetime(2024, 3, 1)],
            'SHU': [datetime(2024, 4, 15), datetime(2024, 5, 20), None],
            'DAS': [datetime(2024, 3, 10), datetime(2024, 4, 10), None],
            'AGI': [None, datetime(2024, 3, 15), datetime(2024, 6, 1)]
        })
        
        # When: Status 계산
        result_df = self.calculator.calculate_complete_status(test_data)
        
        # Then: 최종 날짜가 있는 위치로 카운트되어야 함
        # 첫 번째 화물: SHU (2024-04-15)가 최신
        assert result_df.iloc[0]['Status_Current'] == 'site'
        assert result_df.iloc[0]['Status_Location'] == 'SHU'
        
        # 두 번째 화물: SHU (2024-05-20)가 최신
        assert result_df.iloc[1]['Status_Current'] == 'site'
        assert result_df.iloc[1]['Status_Location'] == 'SHU'
        
        # 세 번째 화물: AGI (2024-06-01)가 최신
        assert result_df.iloc[2]['Status_Current'] == 'site'
        assert result_df.iloc[2]['Status_Location'] == 'AGI'
        
        print("✅ site 겹침 시 최종날짜 우선 확인됨")
    
    def test_final_handling_aggregate_by_location(self):
        """final handling 집계 테스트 - 위치별 현재 재고"""
        # Given: 다양한 상태의 화물 데이터 (각 상태별로 명확히 분리)
        test_data = pd.DataFrame({
            # Warehouse 상태들 (실제 warehouse 컬럼들)
            'DSV Indoor': [datetime(2024, 2, 1), None, None, None],
            'MOSB': [None, datetime(2024, 4, 15), None, None],
            'DSV MZP': [None, None, None, None],
            'AAA  Storage': [None, None, None, None],
            'Hauler Indoor': [None, None, None, None],
            'DHL Warehouse': [None, None, None, None],
            
            # Pre Arrival 상태들 (Pre Arrival 전용 컬럼들)
            'DSV Outdoor': [None, None, datetime(2024, 3, 10), None],
            'DSV Al Markaz': [None, None, None, None],
            
            # Site 상태들
            'MIR': [None, None, None, datetime(2024, 1, 1)],
            'SHU': [None, None, None, None],
            'DAS': [None, None, None, None],
            'AGI': [None, None, None, None]
        })
        
        # When: Status 계산 후 집계
        result_df = self.calculator.calculate_complete_status(test_data)
        
        # final handling 집계 (위치별 현재 재고)
        final_handling = result_df['Status_Location'].value_counts()
        
        # Then: 각 위치별로 올바르게 집계되어야 함
        expected_locations = ['DSV Indoor', 'MOSB', 'DSV Outdoor', 'MIR']
        for location in expected_locations:
            assert location in final_handling.index, f"{location} should be in final handling"
        
        print("📊 final handling 집계 결과:")
        for location, count in final_handling.items():
            print(f"   {location}: {count}건")
        
        # 상태별 분석
        print("\n📋 상태별 분석:")
        for i, row in result_df.iterrows():
            print(f"   Row {i}: {row['Status_Current']} - {row['Status_Location']}")
        
        # 총 건수 확인
        assert final_handling.sum() == len(test_data), "총 건수가 일치해야 함"
        
        print("✅ final handling 집계 확인됨")
    
    def test_final_handling_with_real_data_pattern(self):
        """실제 데이터 패턴으로 final handling 테스트"""
        # Given: 실제 패턴과 유사한 데이터
        test_data = pd.DataFrame({
            # Warehouse 컬럼들
            'DSV Indoor': [datetime(2024, 2, 1)] * 786 + [None] * 214,
            'DSV Outdoor': [None] * 212 + [datetime(2024, 3, 1)] * 788,
            'DSV Al Markaz': [None] * 744 + [datetime(2024, 2, 15)] * 256,
            'MOSB': [None] * 963 + [datetime(2024, 4, 1)] * 37,
            'AAA  Storage': [None] * 608 + [datetime(2024, 3, 10)] * 392,
            'DHL Warehouse': [None] * 881 + [datetime(2024, 5, 1)] * 119,
            'Hauler Indoor': [None] * 990 + [datetime(2024, 6, 1)] * 10,
            
            # Site 컬럼들
            'MIR': [None] * 247 + [datetime(2024, 4, 15)] * 753,
            'SHU': [None] * 696 + [datetime(2024, 5, 20)] * 304,  # 1304 -> 304로 조정
            'DAS': [None] * 35 + [datetime(2024, 3, 25)] * 965,
            'AGI': [None] * 960 + [datetime(2024, 6, 10)] * 40
        })
        
        # 총 1000건으로 맞추기 위해 데이터 조정
        test_data = test_data.head(1000)
        
        # When: Status 계산
        result_df = self.calculator.calculate_complete_status(test_data)
        
        # final handling 집계
        final_handling = result_df['Status_Location'].value_counts()
        
        # Then: 결과 확인
        print("📊 실제 패턴 기반 final handling:")
        for location, count in final_handling.items():
            print(f"   {location}: {count:,}건")
        
        # Status별 집계
        status_summary = result_df.groupby('Status_Current')['Status_Location'].value_counts()
        print("\n📋 Status별 위치 분포:")
        for (status, location), count in status_summary.items():
            print(f"   {status} - {location}: {count:,}건")
        
        # 총 건수 확인
        assert len(result_df) == 1000, "총 건수가 1000건이어야 함"
        assert final_handling.sum() == 1000, "final handling 총합이 1000건이어야 함"
        
        print("✅ 실제 패턴 기반 final handling 확인됨")
    
    def test_pre_arrival_dsv_al_markaz_priority(self):
        """Pre Arrival 상태에서 DSV Al Markaz 우선 선택 확인"""
        # Given: DSV Outdoor와 DSV Al Markaz만 있고 다른 warehouse/site는 없는 Pre Arrival 상태
        test_data = pd.DataFrame({
            'DSV Indoor': [None, None, None],
            'DSV Outdoor': [datetime(2024, 3, 15), datetime(2024, 3, 15), datetime(2024, 2, 1)],
            'DSV Al Markaz': [datetime(2024, 3, 15), datetime(2024, 5, 20), datetime(2024, 4, 1)],
            'DSV MZP': [None, None, None],
            'AAA  Storage': [None, None, None],
            'Hauler Indoor': [None, None, None],
            'MOSB': [None, None, None],
            'DHL Warehouse': [None, None, None],
            'MIR': [None, None, None],
            'SHU': [None, None, None],
            'DAS': [None, None, None],
            'AGI': [None, None, None]
        })
        
        # When: Status 계산
        result_df = self.calculator.calculate_complete_status(test_data)
        
        # Then: Pre Arrival 상태에서 올바른 우선순위 적용
        # 첫 번째: 동일값 → DSV Al Markaz 우선
        assert result_df.iloc[0]['Status_Current'] == 'Pre Arrival'
        assert result_df.iloc[0]['Status_Location'] == 'DSV Al Markaz'
        
        # 두 번째: 최대값 → DSV Al Markaz
        assert result_df.iloc[1]['Status_Current'] == 'Pre Arrival'
        assert result_df.iloc[1]['Status_Location'] == 'DSV Al Markaz'
        
        # 세 번째: 최대값 → DSV Al Markaz
        assert result_df.iloc[2]['Status_Current'] == 'Pre Arrival'
        assert result_df.iloc[2]['Status_Location'] == 'DSV Al Markaz'
        
        # final handling 집계
        final_handling = result_df['Status_Location'].value_counts()
        
        # DSV Al Markaz가 3건 모두 집계되어야 함
        assert final_handling['DSV Al Markaz'] == 3
        assert 'DSV Outdoor' not in final_handling.index
        
        print("✅ Pre Arrival 상태에서 DSV Al Markaz 우선 선택 및 집계 확인됨") 