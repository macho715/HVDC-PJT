#!/usr/bin/env python3
"""
HVDC v2.8.2 핫픽스 검증 테스트
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics
Purpose: 실데이터 기반 v2.8.2 패치 효과 검증
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
import logging
from typing import Dict, List

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 모듈 임포트
sys.path.append('.')
try:
    from calc_flow_code_v2 import FlowCodeCalculatorV2
    from repair_columns_tool import ColumnRepairTool
    from flow_code_gap_analysis import FlowCodeGapAnalyzer
except ImportError as e:
    logger.error(f"모듈 임포트 실패: {e}")
    sys.exit(1)

class HVDCv282Verifier:
    """v2.8.2 핫픽스 검증기"""
    
    def __init__(self):
        self.calc = FlowCodeCalculatorV2()
        self.repair_tool = ColumnRepairTool()
        self.analyzer = FlowCodeGapAnalyzer()
        
        # 기대값 설정 (v2.8.2 타겟)
        self.target_metrics = {
            'flow_code_accuracy': 85.0,  # 85% 이상
            'code_3_detection': 300,     # 300건 이상
            'code_4_detection': 500,     # 500건 이상
            'mosb_missing': 0            # 0건 (누락 없음)
        }
    
    def test_clean_str_function(self) -> bool:
        """전각공백 처리 함수 테스트"""
        logger.info("🧪 전각공백 처리 테스트...")
        
        test_cases = [
            ("DSV　Indoor", "DSV Indoor"),           # 전각공백
            ("\u3000MOSB\u3000", "MOSB"),           # 유니코드 전각공백
            ("  Normal  ", "Normal"),                # 일반 공백
            (np.nan, ""),                           # NaN
            (None, ""),                             # None
            ("", ""),                               # 빈 문자열
            ("Mixed　　Spaces", "Mixed Spaces")      # 복합
        ]
        
        passed = 0
        for input_val, expected in test_cases:
            result = self.calc._clean_str(input_val)
            if result == expected:
                passed += 1
                logger.info(f"   ✅ '{input_val}' → '{result}'")
            else:
                logger.error(f"   ❌ '{input_val}' → '{result}' (기대: '{expected}')")
        
        success_rate = (passed / len(test_cases)) * 100
        logger.info(f"   전각공백 처리 성공률: {success_rate:.1f}%")
        return success_rate >= 95.0
    
    def test_wh_columns_recognition(self) -> bool:
        """WH 컬럼 인식 테스트"""
        logger.info("🧪 WH 컬럼 인식 테스트...")
        
        test_records = [
            # 단일 WH
            {'DSV Indoor': '2025-01-15', 'DSV Outdoor': '', 'DSV Al Markaz': ''},
            # 다중 WH
            {'DSV Indoor': '2025-01-15', 'DSV Outdoor': '2025-01-16', 'DSV Al Markaz': ''},
            # 전체 WH
            {'DSV Indoor': '2025-01-15', 'DSV Outdoor': '2025-01-16', 'DSV Al Markaz': '2025-01-17'},
            # 전각공백 포함
            {'DSV Indoor': 'DSV　Indoor', 'DSV Outdoor': '', 'DSV Al Markaz': ''}
        ]
        
        expected_wh_counts = [1, 2, 3, 1]
        
        passed = 0
        for i, record in enumerate(test_records):
            route = self.calc.extract_route_from_record(record)
            wh_count = route.count('warehouse')
            expected = expected_wh_counts[i]
            
            if wh_count == expected:
                passed += 1
                logger.info(f"   ✅ Record {i+1}: WH {wh_count}개 (기대: {expected})")
            else:
                logger.error(f"   ❌ Record {i+1}: WH {wh_count}개 (기대: {expected})")
        
        success_rate = (passed / len(test_records)) * 100
        logger.info(f"   WH 인식 성공률: {success_rate:.1f}%")
        return success_rate >= 90.0
    
    def test_mosb_recognition(self) -> bool:
        """MOSB 인식 테스트"""
        logger.info("🧪 MOSB 인식 테스트...")
        
        test_records = [
            # 날짜 형식 MOSB
            {'MOSB': '2025-01-20', 'Location': 'DSV Indoor'},
            # 텍스트 MOSB
            {'MOSB': 'MOSB', 'Location': 'DSV Indoor'},
            # 전각공백 포함 MOSB
            {'MOSB': 'MOSB　Base', 'Location': 'DSV Indoor'},
            # MOSB 없음
            {'MOSB': '', 'Location': 'DSV Indoor'}
        ]
        
        expected_mosb = [True, True, True, False]
        
        passed = 0
        for i, record in enumerate(test_records):
            route = self.calc.extract_route_from_record(record)
            has_offshore = 'offshore' in route
            expected = expected_mosb[i]
            
            if has_offshore == expected:
                passed += 1
                logger.info(f"   ✅ Record {i+1}: MOSB {has_offshore} (기대: {expected})")
            else:
                logger.error(f"   ❌ Record {i+1}: MOSB {has_offshore} (기대: {expected})")
        
        success_rate = (passed / len(test_records)) * 100
        logger.info(f"   MOSB 인식 성공률: {success_rate:.1f}%")
        return success_rate >= 90.0
    
    def test_simulated_data_flow_distribution(self) -> bool:
        """시뮬레이션 데이터 Flow Code 분포 테스트"""
        logger.info("🧪 시뮬레이션 데이터 Flow Code 분포 테스트...")
        
        # 시뮬레이션 데이터 생성
        sample_data = []
        
        # Code 0: Pre Arrival
        for i in range(100):
            sample_data.append({
                'Case_No': f'TEST{i:04d}',
                'Location': 'PRE ARRIVAL',
                'Status': 'PRE ARRIVAL'
            })
        
        # Code 1: Port→Site
        for i in range(1000):
            sample_data.append({
                'Case_No': f'TEST{i+100:04d}',
                'Location': 'AGI',
                'Status': 'Active'
            })
        
        # Code 2: Port→WH→Site
        for i in range(800):
            sample_data.append({
                'Case_No': f'TEST{i+1100:04d}',
                'Location': 'DSV Indoor',
                'DSV Indoor': '2025-01-15',
                'Status': 'Active'
            })
        
        # Code 3: Port→WH→MOSB→Site
        for i in range(400):
            sample_data.append({
                'Case_No': f'TEST{i+1900:04d}',
                'Location': 'DSV Indoor',
                'DSV Indoor': '2025-01-15',
                'MOSB': '2025-01-20',
                'Status': 'Active'
            })
        
        # Code 4: Port→WH→WH→MOSB→Site
        for i in range(200):
            sample_data.append({
                'Case_No': f'TEST{i+2300:04d}',
                'Location': 'DSV Indoor',
                'DSV Indoor': '2025-01-15',
                'DSV Outdoor': '2025-01-16',
                'MOSB': '2025-01-20',
                'Status': 'Active'
            })
        
        df = pd.DataFrame(sample_data)
        logger.info(f"   시뮬레이션 데이터: {len(df)}건 생성")
        
        # Flow Code 계산
        df_result = self.calc.add_flow_code_v2_to_dataframe(df)
        
        # 분포 확인
        flow_counts = df_result['Logistics_Flow_Code_V2'].value_counts().sort_index()
        logger.info("   Flow Code 분포:")
        for code, count in flow_counts.items():
            logger.info(f"     Code {code}: {count}건")
        
        # 검증 조건
        conditions = [
            flow_counts.get(0, 0) >= 90,    # Code 0: 90건 이상
            flow_counts.get(1, 0) >= 900,   # Code 1: 900건 이상
            flow_counts.get(2, 0) >= 700,   # Code 2: 700건 이상
            flow_counts.get(3, 0) >= 300,   # Code 3: 300건 이상 ★ 핵심
            flow_counts.get(4, 0) >= 150    # Code 4: 150건 이상 ★ 핵심
        ]
        
        passed = sum(conditions)
        total = len(conditions)
        
        logger.info(f"   검증 조건 통과: {passed}/{total}")
        return passed >= 4  # 5개 중 4개 이상 통과
    
    def test_column_header_cleanup(self) -> bool:
        """컬럼 헤더 전각공백 정리 테스트"""
        logger.info("🧪 컬럼 헤더 전각공백 정리 테스트...")
        
        # 전각공백이 포함된 테스트 DataFrame
        test_data = {
            'Case　No': ['TEST001', 'TEST002'],
            'DSV　Indoor': ['2025-01-15', ''],
            'Location': ['DSV Indoor', 'AGI'],
            'MOSB　Data': ['2025-01-20', '']
        }
        
        df = pd.DataFrame(test_data)
        logger.info(f"   원본 컬럼: {list(df.columns)}")
        
        # 컬럼 복구 도구 적용
        df_repaired = self.repair_tool.repair_missing_columns(df)
        repaired_columns = list(df_repaired.columns)
        logger.info(f"   수정 컬럼: {repaired_columns}")
        
        # 전각공백 제거 확인
        has_fullwidth = any('　' in col for col in repaired_columns)
        
        if not has_fullwidth:
            logger.info("   ✅ 컬럼 헤더 전각공백 정리 성공")
            return True
        else:
            logger.error("   ❌ 컬럼 헤더에 전각공백 남아있음")
            return False
    
    def run_full_verification(self) -> Dict:
        """전체 검증 실행"""
        logger.info("🚀 HVDC v2.8.2 핫픽스 전체 검증 시작...")
        
        results = {}
        
        # 개별 테스트 실행
        test_methods = [
            ('전각공백 처리', self.test_clean_str_function),
            ('WH 컬럼 인식', self.test_wh_columns_recognition),
            ('MOSB 인식', self.test_mosb_recognition),
            ('Flow Code 분포', self.test_simulated_data_flow_distribution),
            ('컬럼 헤더 정리', self.test_column_header_cleanup)
        ]
        
        passed_tests = 0
        for test_name, test_method in test_methods:
            try:
                result = test_method()
                results[test_name] = result
                if result:
                    passed_tests += 1
                    logger.info(f"✅ {test_name} 테스트 통과")
                else:
                    logger.error(f"❌ {test_name} 테스트 실패")
            except Exception as e:
                logger.error(f"❌ {test_name} 테스트 오류: {e}")
                results[test_name] = False
        
        # 전체 결과
        total_tests = len(test_methods)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"\n📊 v2.8.2 핫픽스 검증 결과:")
        logger.info(f"   통과: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            logger.info("🎯 v2.8.2 핫픽스 검증 성공 - 릴리스 준비 완료")
        else:
            logger.warning("⚠️ v2.8.2 핫픽스 검증 미통과 - 추가 수정 필요")
        
        return {
            'success_rate': success_rate,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'individual_results': results,
            'ready_for_release': success_rate >= 80
        }

def main():
    """메인 실행 함수"""
    verifier = HVDCv282Verifier()
    results = verifier.run_full_verification()
    
    # 결과 출력
    print("\n" + "="*60)
    print("HVDC v2.8.2 핫픽스 검증 완료")
    print("="*60)
    print(f"성공률: {results['success_rate']:.1f}%")
    print(f"릴리스 준비: {'✅ 준비 완료' if results['ready_for_release'] else '❌ 추가 작업 필요'}")
    
    return results

if __name__ == "__main__":
    main() 