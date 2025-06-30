#!/usr/bin/env python3
"""
HVDC v2.8.1 패치 대량 샘플 테스트
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics
Purpose: 전각공백 처리 및 Code 3-4 인식 테스트
"""

import pandas as pd
import numpy as np
import pytest
from typing import Dict, List
import sys
import os

# 상위 디렉토리에서 모듈 임포트
sys.path.append('.')
try:
    from calc_flow_code_v2 import FlowCodeCalculatorV2, add_flow_code_v2_to_dataframe
    from mapping_utils import clean_value, is_valid_data
except ImportError as e:
    print(f"모듈 임포트 실패: {e}")

class TestV281Patch:
    """v2.8.1 패치 테스트 클래스"""
    
    def test_clean_value_function(self):
        """전각공백 처리 함수 테스트"""
        # 전각공백 테스트
        assert clean_value("DSV　Indoor") == "DSV Indoor"
        assert clean_value("\u3000MOSB\u3000") == "MOSB"
        
        # NaN 처리 테스트
        assert clean_value(np.nan) == ""
        assert clean_value(None) == ""
        assert clean_value(pd.NA) == ""
        
        # 일반 문자열
        assert clean_value("  Normal Text  ") == "Normal Text"
        
    def test_is_valid_data_function(self):
        """유효 데이터 검사 함수 테스트"""
        # 유효한 데이터
        assert is_valid_data("MOSB") == True
        assert is_valid_data("2025-06-29") == True
        assert is_valid_data("DSV Indoor") == True
        
        # 무효한 데이터
        assert is_valid_data("") == False
        assert is_valid_data("  ") == False
        assert is_valid_data("\u3000") == False  # 전각공백
        assert is_valid_data("nan") == False
        assert is_valid_data("NaN") == False
        assert is_valid_data(np.nan) == False
        assert is_valid_data(None) == False
        
    def test_mosb_date_recognition(self):
        """MOSB 날짜 인식 테스트"""
        calculator = FlowCodeCalculatorV2()
        
        # 날짜 형식 MOSB 데이터
        test_records = [
            {
                'Status': 'Active',
                'Location': 'DSV Indoor',
                'MOSB': '2025-06-29',  # 날짜 형식
                'DSV Indoor': 'Active'
            },
            {
                'Status': 'Active', 
                'Location': 'DSV Indoor',
                'MOSB': '2025-03-15 10:30:00',  # Timestamp 형식
                'DSV Indoor': 'Active'
            },
            {
                'Status': 'Active',
                'Location': 'DSV Indoor', 
                'MOSB': 'MOSB',  # 문자열 형식
                'DSV Indoor': 'Active'
            }
        ]
        
        for record in test_records:
            result = calculator.calc_flow_code_v2(record)
            # MOSB가 있으면 Code 3 이상이어야 함
            assert result['flow_code'] >= 3, f"MOSB 인식 실패: {record}, 결과: {result}"
            
    def test_double_space_in_simense_data(self):
        """SIMENSE 전각공백 이슈 테스트"""
        calculator = FlowCodeCalculatorV2()
        
        # SIMENSE 파일의 실제 전각공백 케이스 시뮬레이션
        test_record = {
            'Status': 'Active',
            'Location': 'DSV Indoor',
            'MOSB': '\u3000',  # 전각공백만 있는 경우
            'DSV Indoor': 'Active'
        }
        
        result = calculator.calc_flow_code_v2(test_record)
        # 전각공백은 유효하지 않으므로 Code 2여야 함
        assert result['flow_code'] == 2, f"전각공백 처리 실패: {result}"
        
        # 전각공백이 포함된 유효한 데이터
        test_record2 = {
            'Status': 'Active',
            'Location': 'DSV Indoor',
            'MOSB': '\u30002025-06-29\u3000',  # 전각공백 + 날짜
            'DSV Indoor': 'Active'
        }
        
        result2 = calculator.calc_flow_code_v2(test_record2)
        # 정리된 날짜가 인식되어 Code 3이어야 함
        assert result2['flow_code'] == 3, f"전각공백+날짜 처리 실패: {result2}"
        
    def test_multiple_warehouse_detection(self):
        """다중 창고 감지 테스트"""
        calculator = FlowCodeCalculatorV2()
        
        # 2개 창고 + MOSB = Code 4
        test_record = {
            'Status': 'Active',
            'Location': 'DSV Indoor',
            'MOSB': '2025-06-29',
            'DSV Indoor': 'Active',
            'DSV Outdoor': 'Active'
        }
        
        result = calculator.calc_flow_code_v2(test_record)
        assert result['flow_code'] == 4, f"Code 4 미인식: {result}"
        
    def generate_large_sample_data(self, size: int = 5000) -> pd.DataFrame:
        """대량 샘플 데이터 생성"""
        data = []
        
        # Code 0: Pre Arrival (163개)
        for i in range(163):
            data.append({
                'Case_No': f'SIM{i:04d}',
                'Status': 'PRE ARRIVAL',
                'Location': 'PRE ARRIVAL',
                'MOSB': '',
                'DSV Indoor': '',
                'DSV Outdoor': ''
            })
        
        # Code 1: Port→Site (2000개)
        for i in range(163, 2163):
            data.append({
                'Case_No': f'SIM{i:04d}',
                'Status': 'Active',
                'Location': np.random.choice(['AGI', 'DAS', 'MIR', 'SHU']),
                'MOSB': '',
                'DSV Indoor': '',
                'DSV Outdoor': ''
            })
        
        # Code 2: Port→WH→Site (1500개)
        for i in range(2163, 3663):
            data.append({
                'Case_No': f'SIM{i:04d}',
                'Status': 'Active',
                'Location': np.random.choice(['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz']),
                'MOSB': '',
                'DSV Indoor': 'Active' if np.random.random() > 0.5 else '',
                'DSV Outdoor': ''
            })
        
        # Code 3: Port→WH→MOSB→Site (400개)
        for i in range(3663, 4063):
            mosb_formats = ['2025-06-29', '2025-03-15 10:30:00', 'MOSB']
            # 일부는 전각공백 포함하여 실제 상황 재현
            if i % 10 == 0:  # 10%는 전각공백 포함
                mosb_value = f'\u3000{np.random.choice(mosb_formats)}\u3000'
            else:
                mosb_value = np.random.choice(mosb_formats)
                
            data.append({
                'Case_No': f'SIM{i:04d}',
                'Status': 'Active',
                'Location': np.random.choice(['DSV Indoor', 'DSV Outdoor']),
                'MOSB': mosb_value,
                'DSV Indoor': 'Active',
                'DSV Outdoor': ''
            })
        
        # Code 4: Port→WH→wh→MOSB→Site (500개)
        for i in range(4063, 4563):
            mosb_formats = ['2025-06-29', '2025-03-15 10:30:00']
            data.append({
                'Case_No': f'SIM{i:04d}',
                'Status': 'Active', 
                'Location': 'DSV Indoor',
                'MOSB': np.random.choice(mosb_formats),
                'DSV Indoor': 'Active',
                'DSV Outdoor': 'Active'  # 2개 창고
            })
        
        # 나머지는 Code 2로 채움
        remaining = size - len(data)
        for i in range(len(data), len(data) + remaining):
            data.append({
                'Case_No': f'SIM{i:04d}',
                'Status': 'Active',
                'Location': 'DSV Indoor',
                'MOSB': '',
                'DSV Indoor': 'Active',
                'DSV Outdoor': ''
            })
        
        return pd.DataFrame(data)
        
    def test_large_sample_flow_distribution(self):
        """대량 샘플 Flow 분포 테스트"""
        # 5000개 샘플 생성
        sample_df = self.generate_large_sample_data(5000)
        
        # Flow Code 계산
        calc = FlowCodeCalculatorV2()
        df_result = calc.add_flow_code_v2_to_dataframe(sample_df)
        
        # 분포 확인
        flow_counts = df_result['Logistics_Flow_Code_V2'].value_counts().sort_index().to_dict()
        
        print(f"📊 대량 샘플 테스트 결과:")
        print(f"   총 샘플: {len(df_result)}개")
        print(f"   Flow 분포: {flow_counts}")
        print(f"   평균 신뢰도: {df_result['Flow_Confidence'].mean():.3f}")
        
        # 검증
        assert set(df_result["Logistics_Flow_Code_V2"].unique()) <= {0,1,2,3,4}, "잘못된 Flow Code 발견"
        assert flow_counts.get(3, 0) >= 300, f"Code 3 인식 부족: {flow_counts.get(3, 0)}개"
        assert flow_counts.get(4, 0) >= 400, f"Code 4 인식 부족: {flow_counts.get(4, 0)}개"
        
        print("✅ 대량 샘플 테스트 통과")
        
    def test_performance_benchmark(self):
        """성능 벤치마크 테스트"""
        import time
        
        # 10,000개 샘플로 성능 테스트
        sample_df = self.generate_large_sample_data(10000)
        
        start_time = time.time()
        
        calc = FlowCodeCalculatorV2()
        df_result = calc.add_flow_code_v2_to_dataframe(sample_df)
        
        end_time = time.time()
        processing_time = end_time - start_time
        throughput = len(sample_df) / processing_time
        
        print(f"⚡ 성능 벤치마크:")
        print(f"   처리 시간: {processing_time:.2f}초")
        print(f"   처리량: {throughput:.0f}개/초")
        print(f"   평균 신뢰도: {df_result['Flow_Confidence'].mean():.3f}")
        
        # 성능 기준: 최소 500개/초
        assert throughput >= 500, f"성능 기준 미달: {throughput:.0f}개/초"
        
        print("✅ 성능 테스트 통과")

def run_all_tests():
    """모든 테스트 실행"""
    print("🧪 HVDC v2.8.1 패치 테스트 시작")
    print("=" * 60)
    
    test_instance = TestV281Patch()
    
    # 기본 함수 테스트
    print("1️⃣ 전각공백 처리 함수 테스트...")
    test_instance.test_clean_value_function()
    test_instance.test_is_valid_data_function()
    print("✅ 기본 함수 테스트 통과")
    
    # MOSB 인식 테스트
    print("\n2️⃣ MOSB 날짜 인식 테스트...")
    test_instance.test_mosb_date_recognition()
    test_instance.test_double_space_in_simense_data()
    test_instance.test_multiple_warehouse_detection()
    print("✅ MOSB 인식 테스트 통과")
    
    # 대량 샘플 테스트
    print("\n3️⃣ 대량 샘플 테스트...")
    test_instance.test_large_sample_flow_distribution()
    print("✅ 대량 샘플 테스트 통과")
    
    # 성능 테스트
    print("\n4️⃣ 성능 테스트...")
    test_instance.test_performance_benchmark()
    print("✅ 성능 테스트 통과")
    
    print("\n🎉 모든 테스트 완료!")
    print("v2.8.1 패치가 성공적으로 적용되었습니다.")

if __name__ == "__main__":
    run_all_tests() 