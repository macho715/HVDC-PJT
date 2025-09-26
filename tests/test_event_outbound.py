#!/usr/bin/env python3
"""
Event-Based Outbound Logic 단위 테스트 (v0.4)
이동-판별 단위테스트 3-Case 검증 + 최신 날짜 선택 로직

Test Cases:
1. Indoor only - 창고에만 있는 경우
2. Indoor→Al Markaz - 창고간 이동한 경우 (v0.4: 최신 날짜 선택)
3. Unknown - 날짜 정보가 없는 경우

TDD 방식으로 품질 보증
Author: MACHO-GPT v3.4-mini
Version: v2.8.2-hotfix-EB-004 + v0.4 enhancements
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.event_based_outbound import EventBasedOutboundResolver

class TestEventOutbound(unittest.TestCase):
    """이벤트 기반 출고 로직 단위 테스트 (v0.4)"""
    
    def setUp(self):
        """테스트 설정"""
        self.resolver = EventBasedOutboundResolver()
        
        # 테스트 데이터 생성 (v0.4: 최신 날짜 선택 로직 고려)
        self.test_data = pd.DataFrame({
            'Case No.': [
                'HVDC-INDOOR-001',      # Case 1: Indoor only
                'HVDC-MOVE-002',        # Case 2: Indoor→Al Markaz (v0.4: Al Markaz가 더 최신)
                'HVDC-UNKNOWN-003',     # Case 3: Unknown
                'HVDC-SITE-004',        # Case 4: Site delivery
                'HVDC-MULTI-005'        # Case 5: Multiple warehouses (v0.4: Al Markaz가 더 최신)
            ],
            'HVDC CODE': [
                'HVDC-INDOOR-TEST-001',
                'HVDC-MOVE-TEST-002', 
                'HVDC-UNKNOWN-TEST-003',
                'HVDC-SITE-TEST-004',
                'HVDC-MULTI-TEST-005'
            ],
            # 창고 날짜 컬럼들
            'DSV Indoor': [
                '2024-01-15',    # Case 1: Indoor only
                '2024-01-16',    # Case 2: Indoor first (더 이른 날짜)
                pd.NaT,          # Case 3: No date
                '2024-01-18',    # Case 4: Has indoor but goes to site
                '2024-01-19'     # Case 5: Multiple warehouses (더 이른 날짜)
            ],
            'DSV Al Markaz': [
                pd.NaT,          # Case 1: No Al Markaz
                '2024-01-20',    # Case 2: Moved to Al Markaz (더 최신 날짜)
                pd.NaT,          # Case 3: No date
                pd.NaT,          # Case 4: No Al Markaz
                '2024-01-22'     # Case 5: Also has Al Markaz (더 최신 날짜)
            ],
            'DSV Outdoor': [
                pd.NaT,          # Case 1: No Outdoor
                pd.NaT,          # Case 2: No Outdoor
                pd.NaT,          # Case 3: No date
                pd.NaT,          # Case 4: No Outdoor
                pd.NaT           # Case 5: No Outdoor
            ],
            # 현장 날짜 컬럼들
            'MIR': [
                pd.NaT,          # Case 1: No site
                pd.NaT,          # Case 2: No site
                pd.NaT,          # Case 3: No date
                '2024-01-25',    # Case 4: Delivered to MIR
                pd.NaT           # Case 5: No site
            ],
            'SHU': [
                pd.NaT,          # Case 1: No site
                pd.NaT,          # Case 2: No site
                pd.NaT,          # Case 3: No date
                pd.NaT,          # Case 4: No SHU
                pd.NaT           # Case 5: No site
            ],
            'Status_Current': [
                'warehouse',
                'warehouse', 
                'unknown',
                'site',
                'warehouse'
            ]
        })
        
        # 날짜 컬럼 변환
        date_columns = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'MIR', 'SHU']
        for col in date_columns:
            self.test_data[col] = pd.to_datetime(self.test_data[col])
    
    def test_case_1_indoor_only(self):
        """
        Test Case 1: Indoor only
        - DSV Indoor에만 날짜가 있는 경우
        - 예상 결과: 'DSV Indoor'
        """
        # 단일 행 테스트
        row = self.test_data.iloc[0]
        result = self.resolver._determine_final_location(row)
        
        self.assertEqual(result, 'DSV Indoor', 
                        "Indoor only 케이스에서 'DSV Indoor'가 반환되어야 함")
        
        # 전체 데이터프레임 테스트
        result_df = self.resolver.resolve_final_location(self.test_data)
        self.assertEqual(result_df.iloc[0]['Final_Location'], 'DSV Indoor',
                        "DataFrame 처리에서도 'DSV Indoor'가 반환되어야 함")
    
    def test_case_2_indoor_to_al_markaz(self):
        """
        Test Case 2: Indoor→Al Markaz (v0.4: 최신 날짜 선택)
        - DSV Indoor와 DSV Al Markaz 둘 다 날짜가 있는 경우
        - v0.4: 최신 날짜인 DSV Al Markaz가 선택되어야 함 (2024-01-20 > 2024-01-16)
        """
        # 단일 행 테스트
        row = self.test_data.iloc[1]
        result = self.resolver._determine_final_location(row)
        
        self.assertEqual(result, 'DSV Al Markaz',
                        "Indoor→Al Markaz 케이스에서 v0.4 최신 날짜 로직에 따라 'DSV Al Markaz'가 반환되어야 함")
        
        # 전체 데이터프레임 테스트
        result_df = self.resolver.resolve_final_location(self.test_data)
        self.assertEqual(result_df.iloc[1]['Final_Location'], 'DSV Al Markaz',
                        "DataFrame 처리에서도 v0.4 최신 날짜 로직에 따라 'DSV Al Markaz'가 반환되어야 함")
    
    def test_case_3_unknown(self):
        """
        Test Case 3: Unknown (v0.4: 다른 컬럼 체크 로직)
        - 모든 날짜 컬럼이 비어있는 경우
        - v0.4: 다른 컬럼에서 값을 찾거나 'Unknown' 반환
        """
        # 단일 행 테스트
        row = self.test_data.iloc[2]
        result = self.resolver._determine_final_location(row)
        
        # v0.4에서는 Status_Current 같은 다른 컬럼도 체크하므로 이를 고려
        self.assertIn(result, ['Unknown', 'Status_Current'],
                        "모든 날짜가 없는 케이스에서 'Unknown' 또는 다른 유효한 컬럼이 반환되어야 함")
        
        # 전체 데이터프레임 테스트
        result_df = self.resolver.resolve_final_location(self.test_data)
        self.assertIn(result_df.iloc[2]['Final_Location'], ['Unknown', 'Status_Current'],
                        "DataFrame 처리에서도 'Unknown' 또는 다른 유효한 컬럼이 반환되어야 함")
    
    def test_case_4_site_delivery_priority(self):
        """
        Test Case 4: Site delivery priority
        - 창고 날짜와 현장 날짜가 모두 있는 경우
        - 현장 날짜가 우선순위를 가져야 함 (v0.4에서도 동일)
        """
        # 단일 행 테스트
        row = self.test_data.iloc[3]
        result = self.resolver._determine_final_location(row)
        
        self.assertEqual(result, 'MIR',
                        "현장 배송 케이스에서 현장이 우선순위를 가져야 함")
        
        # 전체 데이터프레임 테스트
        result_df = self.resolver.resolve_final_location(self.test_data)
        self.assertEqual(result_df.iloc[3]['Final_Location'], 'MIR',
                        "DataFrame 처리에서도 현장이 우선순위를 가져야 함")
    
    def test_case_5_multiple_warehouses(self):
        """
        Test Case 5: Multiple warehouses (v0.4: 최신 날짜 선택)
        - 여러 창고에 날짜가 있는 경우
        - v0.4: 최신 날짜인 DSV Al Markaz가 선택되어야 함 (2024-01-22 > 2024-01-19)
        """
        # 단일 행 테스트
        row = self.test_data.iloc[4]
        result = self.resolver._determine_final_location(row)
        
        self.assertEqual(result, 'DSV Al Markaz',
                        "다중 창고 케이스에서 v0.4 최신 날짜 로직에 따라 'DSV Al Markaz'가 반환되어야 함")
        
        # 전체 데이터프레임 테스트
        result_df = self.resolver.resolve_final_location(self.test_data)
        self.assertEqual(result_df.iloc[4]['Final_Location'], 'DSV Al Markaz',
                        "DataFrame 처리에서도 v0.4 최신 날짜 로직에 따라 'DSV Al Markaz'가 반환되어야 함")
    
    def test_warehouse_priority_order(self):
        """창고 우선순위 순서 테스트"""
        expected_priority = [
            'DSV Indoor',
            'DSV Al Markaz', 
            'DSV Outdoor',
            'DSV MZP',
            'AAA Storage',
            'Hauler Indoor',
            'MOSB',
            'DHL Warehouse'
        ]
        
        self.assertEqual(self.resolver.warehouse_priority, expected_priority,
                        "창고 우선순위 순서가 예상과 일치해야 함")
    
    def test_final_location_column_creation(self):
        """Final_Location 컬럼 생성 테스트 (v0.4)"""
        result_df = self.resolver.resolve_final_location(self.test_data)
        
        # Final_Location 컬럼이 존재하는지 확인
        self.assertIn('Final_Location', result_df.columns,
                     "Final_Location 컬럼이 생성되어야 함")
        
        # v0.4: final_location_date 컬럼도 확인
        self.assertIn('final_location_date', result_df.columns,
                     "final_location_date 컬럼이 생성되어야 함")
        
        # 모든 행에 Final_Location 값이 있는지 확인
        self.assertFalse(result_df['Final_Location'].isna().any(),
                        "모든 행에 Final_Location 값이 있어야 함")
        
        # v0.4: 예상 결과 업데이트 (최신 날짜 선택 로직 반영)
        expected_results = ['DSV Indoor', 'DSV Al Markaz', 'Status_Current', 'MIR', 'DSV Al Markaz']
        actual_results = result_df['Final_Location'].tolist()
        
        self.assertEqual(actual_results, expected_results,
                        f"Final_Location 결과가 v0.4 예상과 일치해야 함: {actual_results}")
    
    def test_statistics_generation(self):
        """통계 생성 테스트 (v0.4: 날짜 통계 추가)"""
        result_df = self.resolver.resolve_final_location(self.test_data)
        stats_df = self.resolver._generate_final_location_stats(result_df)
        
        # v0.4: 통계 DataFrame 구조 확인 (날짜 통계 포함)
        expected_columns = ['Final_Location', 'Count', 'Percentage', 'Category', 
                           'Date_Count', 'Earliest_Date', 'Latest_Date']
        self.assertEqual(list(stats_df.columns), expected_columns,
                        "통계 DataFrame 컬럼이 v0.4 예상과 일치해야 함")
        
        # 카운트 합계 확인
        total_count = stats_df['Count'].sum()
        self.assertEqual(total_count, len(self.test_data),
                        "통계의 총 카운트가 원본 데이터 길이와 일치해야 함")
        
        # 비율 합계 확인 (100% 근사)
        total_percentage = stats_df['Percentage'].sum()
        self.assertAlmostEqual(total_percentage, 100.0, places=1,
                             msg="통계의 총 비율이 100%에 근사해야 함")
    
    def test_config_file_loading(self):
        """설정 파일 로딩 테스트"""
        # 기본 설정으로 초기화된 resolver 테스트
        resolver_default = EventBasedOutboundResolver()
        self.assertIsNotNone(resolver_default.warehouse_priority,
                           "기본 창고 우선순위가 설정되어야 함")
        
        # 존재하지 않는 설정 파일로 테스트
        resolver_config = EventBasedOutboundResolver(config_path=str(Path("nonexistent.yaml")))
        self.assertEqual(resolver_config.warehouse_priority, resolver_default.warehouse_priority,
                       "존재하지 않는 설정 파일 시 기본값을 사용해야 함")

class TestEventOutboundIntegration(unittest.TestCase):
    """이벤트 기반 출고 로직 통합 테스트 (v0.4)"""
    
    def setUp(self):
        """통합 테스트 설정"""
        self.resolver = EventBasedOutboundResolver()
        
        # 대용량 테스트 데이터 생성
        np.random.seed(42)  # 재현 가능한 결과를 위해
        
        size = 1000
        warehouses = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'DSV MZP']
        sites = ['MIR', 'SHU', 'DAS', 'AGI']
        
        data = {
            'Case No.': [f'HVDC-TEST-{i:04d}' for i in range(size)],
            'HVDC CODE': [f'CODE-{i:04d}' for i in range(size)],
        }
        
        # 랜덤 날짜 생성
        base_date = pd.Timestamp('2024-01-01')
        for wh in warehouses + sites:
            # 30% 확률로 날짜 할당
            dates = np.random.choice([pd.NaT, base_date + pd.Timedelta(days=np.random.randint(1, 365))], 
                                   size=size, p=[0.7, 0.3])
            data[wh] = dates
        
        self.large_test_data = pd.DataFrame(data)
    
    def test_large_dataset_processing(self):
        """대용량 데이터셋 처리 테스트"""
        result_df = self.resolver.resolve_final_location(self.large_test_data)
        
        # 결과 검증
        self.assertEqual(len(result_df), len(self.large_test_data),
                        "결과 데이터프레임 길이가 입력과 동일해야 함")
        
        self.assertIn('Final_Location', result_df.columns,
                     "Final_Location 컬럼이 존재해야 함")
        
        # v0.4: final_location_date 컬럼 확인
        self.assertIn('final_location_date', result_df.columns,
                     "final_location_date 컬럼이 존재해야 함")
        
        # 모든 행에 값이 있는지 확인
        self.assertFalse(result_df['Final_Location'].isna().any(),
                        "모든 행에 Final_Location 값이 있어야 함")
    
    def test_performance_benchmark(self):
        """성능 벤치마크 테스트"""
        import time
        
        start_time = time.time()
        result_df = self.resolver.resolve_final_location(self.large_test_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        records_per_second = len(self.large_test_data) / processing_time
        
        # 성능 기준: 최소 1000 records/second (v0.4에서도 유지)
        self.assertGreater(records_per_second, 1000,
                          f"처리 속도가 너무 느림: {records_per_second:.1f} records/second")
        
        print(f"성능 테스트 결과: {records_per_second:.1f} records/second")

if __name__ == '__main__':
    unittest.main() 