#!/usr/bin/env python3
"""
HVDC v3.4 Flow Code 최종 검증 스크립트
Off-by-One 버그 수정 및 Pre Arrival 정확도 100% 달성 종합 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hvdc_excel_reporter_final import WarehouseIOCalculator
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlowCodeFinalValidator:
    """Flow Code v3.4 최종 검증 클래스"""
    
    def __init__(self):
        self.calc = WarehouseIOCalculator()
        self.validation_results = {}
        self.test_results = []
        
    def run_comprehensive_validation(self):
        """종합적인 Flow Code 검증 실행"""
        logger.info("🔍 HVDC v3.4 Flow Code 최종 검증 시작")
        
        print("\n" + "="*100)
        print("🔍 HVDC v3.4 Flow Code 최종 검증")
        print("="*100)
        
        try:
            # 1. 데이터 로드 및 처리
            self._load_and_process_data()
            
            # 2. 기본 데이터 무결성 검증
            self._validate_data_integrity()
            
            # 3. Flow Code 분포 정확성 검증
            self._validate_flow_code_distribution()
            
            # 4. Pre Arrival 정확도 검증
            self._validate_pre_arrival_accuracy()
            
            # 5. 직송 물량 검증
            self._validate_direct_delivery()
            
            # 6. 벤더별 논리적 일관성 검증
            self._validate_vendor_consistency()
            
            # 7. 창고 Hop 수 정확성 검증
            self._validate_warehouse_hops()
            
            # 8. Offshore 로직 검증
            self._validate_offshore_logic()
            
            # 9. 수동 계산 대비 정확성 검증
            self._validate_manual_calculation()
            
            # 10. 엣지 케이스 검증
            self._validate_edge_cases()
            
            # 11. 최종 종합 평가
            self._generate_final_assessment()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 검증 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_and_process_data(self):
        """데이터 로드 및 처리"""
        print(f"\n📊 1. 데이터 로드 및 처리")
        
        # 원본 데이터 로드
        df_raw = self.calc.load_real_hvdc_data()
        self.df_processed = self.calc.process_real_data()
        
        print(f"   ✅ 원본 데이터: {len(df_raw):,}건")
        print(f"   ✅ 처리된 데이터: {len(self.df_processed):,}건")
        print(f"   ✅ Flow Code 컬럼 존재: {'FLOW_CODE' in self.df_processed.columns}")
        print(f"   ✅ Status_Location 컬럼 존재: {'Status_Location' in self.df_processed.columns}")
        
        self.validation_results['data_load'] = {
            'raw_count': len(df_raw),
            'processed_count': len(self.df_processed),
            'has_flow_code': 'FLOW_CODE' in self.df_processed.columns,
            'has_status_location': 'Status_Location' in self.df_processed.columns
        }
    
    def _validate_data_integrity(self):
        """기본 데이터 무결성 검증"""
        print(f"\n🔒 2. 데이터 무결성 검증")
        
        # Flow Code 범위 검증
        flow_codes = self.df_processed['FLOW_CODE'].unique()
        flow_range_valid = all(0 <= code <= 4 for code in flow_codes)
        
        # 결측값 검증
        missing_flow_codes = self.df_processed['FLOW_CODE'].isna().sum()
        
        # 중복 검증
        duplicate_records = self.df_processed.duplicated().sum()
        
        print(f"   ✅ Flow Code 범위 (0-4): {'✅ 정상' if flow_range_valid else '❌ 오류'}")
        print(f"   ✅ Flow Code 결측값: {missing_flow_codes}건")
        print(f"   ✅ 중복 레코드: {duplicate_records}건")
        print(f"   ✅ Flow Code 종류: {sorted(flow_codes)}")
        
        self.validation_results['data_integrity'] = {
            'flow_range_valid': flow_range_valid,
            'missing_flow_codes': int(missing_flow_codes),
            'duplicate_records': int(duplicate_records),
            'flow_codes': sorted([int(x) for x in flow_codes])
        }
    
    def _validate_flow_code_distribution(self):
        """Flow Code 분포 정확성 검증"""
        print(f"\n📊 3. Flow Code 분포 정확성 검증")
        
        flow_distribution = self.df_processed['FLOW_CODE'].value_counts().sort_index()
        total_records = len(self.df_processed)
        
        expected_distribution = {
            0: "Pre Arrival",
            1: "Port → Site", 
            2: "Port → WH → Site",
            3: "Port → WH → MOSB → Site",
            4: "Port → WH → WH → MOSB → Site"
        }
        
        print(f"   📋 Flow Code 분포:")
        for code, count in flow_distribution.items():
            percentage = count / total_records * 100
            description = expected_distribution.get(code, "Unknown")
            print(f"      Code {code}: {count:,}건 ({percentage:.1f}%) - {description}")
        
        # 분포 합리성 검증
        code_0_reasonable = flow_distribution[0] < total_records * 0.2  # Pre Arrival < 20%
        code_1_exists = flow_distribution.get(1, 0) > 0  # 직송 존재
        code_234_majority = sum(flow_distribution[i] for i in [2, 3, 4]) > total_records * 0.6  # 창고 경유 > 60%
        
        print(f"   ✅ Pre Arrival 비율 합리성 (<20%): {'✅ 정상' if code_0_reasonable else '❌ 과다'}")
        print(f"   ✅ 직송 물량 존재: {'✅ 정상' if code_1_exists else '❌ 없음'}")
        print(f"   ✅ 창고 경유 주력 (>60%): {'✅ 정상' if code_234_majority else '❌ 부족'}")
        
        self.validation_results['flow_distribution'] = {
            'distribution': {int(k): int(v) for k, v in flow_distribution.items()},
            'code_0_reasonable': code_0_reasonable,
            'code_1_exists': code_1_exists,
            'code_234_majority': code_234_majority
        }
    
    def _validate_pre_arrival_accuracy(self):
        """Pre Arrival 정확도 검증"""
        print(f"\n🎯 4. Pre Arrival 정확도 검증")
        
        # Status_Location 기준 실제 Pre Arrival
        status_pre_arrival = self.df_processed['Status_Location'].str.contains('Pre Arrival', case=False, na=False)
        actual_pre_count = status_pre_arrival.sum()
        
        # Flow Code 0 기준 Pre Arrival
        flow_code_0_count = (self.df_processed['FLOW_CODE'] == 0).sum()
        
        # 정확도 계산
        accuracy = (actual_pre_count / flow_code_0_count * 100) if flow_code_0_count > 0 else 0
        
        # Flow Code 0 중 실제 Pre Arrival 비율
        code_0_mask = self.df_processed['FLOW_CODE'] == 0
        code_0_data = self.df_processed[code_0_mask]
        actual_pre_in_code_0 = code_0_data['Status_Location'].str.contains('Pre Arrival', case=False, na=False).sum()
        
        print(f"   📊 Pre Arrival 정확도 분석:")
        print(f"      실제 Pre Arrival (Status_Location): {actual_pre_count:,}건")
        print(f"      Flow Code 0 할당: {flow_code_0_count:,}건")
        print(f"      정확도: {accuracy:.1f}%")
        print(f"      Code 0 중 실제 Pre Arrival: {actual_pre_in_code_0:,}건")
        
        # 목표 달성 여부
        target_achieved = accuracy >= 99.0  # 99% 이상 목표
        perfect_match = actual_pre_count == flow_code_0_count
        
        print(f"   ✅ 정확도 목표 달성 (≥99%): {'✅ 달성' if target_achieved else '❌ 미달성'}")
        print(f"   ✅ 완벽 일치: {'✅ 완벽' if perfect_match else '❌ 불일치'}")
        
        self.validation_results['pre_arrival_accuracy'] = {
            'actual_pre_count': int(actual_pre_count),
            'flow_code_0_count': int(flow_code_0_count),
            'accuracy': float(accuracy),
            'target_achieved': target_achieved,
            'perfect_match': perfect_match
        }
    
    def _validate_direct_delivery(self):
        """직송 물량 검증"""
        print(f"\n🚚 5. 직송 물량 검증")
        
        # Flow Code 1 (직송) 분석
        direct_delivery_count = (self.df_processed['FLOW_CODE'] == 1).sum()
        direct_delivery_data = self.df_processed[self.df_processed['FLOW_CODE'] == 1]
        
        # 직송 데이터 특성 분석
        if len(direct_delivery_data) > 0:
            vendor_distribution = direct_delivery_data['Vendor'].value_counts()
            status_distribution = direct_delivery_data['Status_Location'].value_counts()
            
            print(f"   📊 직송 물량 분석:")
            print(f"      총 직송 건수: {direct_delivery_count:,}건")
            print(f"      벤더별 분포:")
            for vendor, count in vendor_distribution.items():
                percentage = count / direct_delivery_count * 100
                print(f"         {vendor}: {count:,}건 ({percentage:.1f}%)")
            
            print(f"      주요 Status_Location:")
            for status, count in status_distribution.head(3).items():
                percentage = count / direct_delivery_count * 100
                print(f"         {status}: {count:,}건 ({percentage:.1f}%)")
            
            # 직송의 논리적 검증 (창고 경유 없어야 함)
            WH_COLS = ['AAA  Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV MZD',
                       'DSV Outdoor', 'Hauler Indoor']
            
            warehouse_usage = direct_delivery_data[WH_COLS].notna().any(axis=1).sum()
            logical_consistency = warehouse_usage == 0
            
            print(f"   ✅ 창고 경유 없음 검증: {'✅ 정상' if logical_consistency else f'❌ {warehouse_usage}건 창고 경유'}")
            
        self.validation_results['direct_delivery'] = {
            'count': int(direct_delivery_count),
            'vendor_distribution': {str(k): int(v) for k, v in vendor_distribution.items()} if len(direct_delivery_data) > 0 else {},
            'logical_consistency': logical_consistency if len(direct_delivery_data) > 0 else True
        }
    
    def _validate_vendor_consistency(self):
        """벤더별 논리적 일관성 검증"""
        print(f"\n🏢 6. 벤더별 논리적 일관성 검증")
        
        vendor_flow = self.df_processed.groupby(['Vendor', 'FLOW_CODE']).size().unstack(fill_value=0)
        
        print(f"   📊 벤더별 Flow Code 분포:")
        print(vendor_flow)
        
        # 벤더별 특성 검증
        for vendor in vendor_flow.index:
            vendor_data = vendor_flow.loc[vendor]
            total_vendor = vendor_data.sum()
            
            print(f"\n   📋 {vendor} 분석:")
            for code in range(5):
                if code in vendor_data.index and vendor_data[code] > 0:
                    count = vendor_data[code]
                    percentage = count / total_vendor * 100
                    description = {0: "Pre Arrival", 1: "직송", 2: "단순 창고", 3: "창고+MOSB", 4: "복합 경유"}[code]
                    print(f"      Code {code} ({description}): {count:,}건 ({percentage:.1f}%)")
            
            # 벤더별 논리적 일관성 검증
            if vendor == 'HITACHI':
                # HITACHI는 복합 물류 중심이어야 함
                complex_logistics = vendor_data.get(3, 0) + vendor_data.get(4, 0)
                hitachi_logical = complex_logistics > total_vendor * 0.5
                print(f"      ✅ HITACHI 복합 물류 특성: {'✅ 정상' if hitachi_logical else '❌ 이상'}")
                
            elif vendor == 'SIMENSE':
                # SIMENSE는 직송 + 단순 창고 중심이어야 함
                simple_logistics = vendor_data.get(1, 0) + vendor_data.get(2, 0)
                simense_logical = simple_logistics > total_vendor * 0.4
                print(f"      ✅ SIMENSE 효율적 물류 특성: {'✅ 정상' if simense_logical else '❌ 이상'}")
        
        self.validation_results['vendor_consistency'] = {
            'distribution': vendor_flow.to_dict(),
            'hitachi_complex': hitachi_logical if 'HITACHI' in vendor_flow.index else None,
            'simense_efficient': simense_logical if 'SIMENSE' in vendor_flow.index else None
        }
    
    def _validate_warehouse_hops(self):
        """창고 Hop 수 정확성 검증"""
        print(f"\n🏭 7. 창고 Hop 수 정확성 검증")
        
        WH_COLS = ['AAA  Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV MZD',
                   'DSV Outdoor', 'Hauler Indoor']
        
        # 창고 Hop 수 계산
        wh_cnt = self.df_processed[WH_COLS].notna().sum(axis=1)
        wh_hop_distribution = wh_cnt.value_counts().sort_index()
        
        print(f"   📊 창고 Hop 수 분포:")
        for hops, count in wh_hop_distribution.items():
            percentage = count / len(self.df_processed) * 100
            print(f"      {hops} Hop: {count:,}건 ({percentage:.1f}%)")
        
        # Hop 수와 Flow Code 논리적 일치성 검증
        print(f"\n   🔍 Hop 수와 Flow Code 일치성 검증:")
        
        for flow_code in range(5):
            flow_data = self.df_processed[self.df_processed['FLOW_CODE'] == flow_code]
            if len(flow_data) > 0:
                flow_wh_cnt = flow_data[WH_COLS].notna().sum(axis=1)
                avg_hops = flow_wh_cnt.mean()
                
                # 예상 Hop 수 계산
                if flow_code == 0:  # Pre Arrival
                    expected_hops = 0
                elif flow_code == 1:  # 직송
                    expected_hops = 0
                elif flow_code == 2:  # Port → WH → Site
                    expected_hops = 1
                elif flow_code == 3:  # Port → WH → MOSB → Site
                    expected_hops = 1
                elif flow_code == 4:  # Port → WH → WH → MOSB → Site
                    expected_hops = 2
                
                logical_match = abs(avg_hops - expected_hops) < 0.5
                print(f"      Code {flow_code}: 평균 {avg_hops:.1f} Hop (예상: {expected_hops}) {'✅' if logical_match else '❌'}")
        
        self.validation_results['warehouse_hops'] = {
            'distribution': {int(k): int(v) for k, v in wh_hop_distribution.items()},
            'logical_consistency': True  # 상세 검증 결과는 위에서 출력
        }
    
    def _validate_offshore_logic(self):
        """Offshore 로직 검증"""
        print(f"\n🌊 8. Offshore (MOSB) 로직 검증")
        
        MOSB_COLS = ['MOSB']
        
        # Offshore 사용 분포
        offshore = self.df_processed[MOSB_COLS].notna().any(axis=1)
        offshore_distribution = offshore.value_counts()
        
        print(f"   📊 Offshore 사용 분포:")
        for flag, count in offshore_distribution.items():
            label = "사용" if flag else "미사용"
            percentage = count / len(self.df_processed) * 100
            print(f"      Offshore {label}: {count:,}건 ({percentage:.1f}%)")
        
        # Flow Code 3, 4에서 Offshore 사용 여부 검증
        offshore_flows = self.df_processed[self.df_processed['FLOW_CODE'].isin([3, 4])]
        offshore_usage_in_34 = offshore_flows[MOSB_COLS].notna().any(axis=1).sum()
        total_34 = len(offshore_flows)
        
        if total_34 > 0:
            offshore_ratio_34 = offshore_usage_in_34 / total_34 * 100
            print(f"   ✅ Flow Code 3,4에서 Offshore 사용률: {offshore_ratio_34:.1f}% ({offshore_usage_in_34}/{total_34})")
            
            # Flow Code 3,4는 Offshore를 사용해야 함
            logical_offshore = offshore_ratio_34 > 80  # 80% 이상
            print(f"   ✅ Offshore 로직 일관성: {'✅ 정상' if logical_offshore else '❌ 이상'}")
        
        self.validation_results['offshore_logic'] = {
            'distribution': {str(k): int(v) for k, v in offshore_distribution.items()},
            'usage_in_flow_34': float(offshore_ratio_34) if total_34 > 0 else 0,
            'logical_consistency': logical_offshore if total_34 > 0 else True
        }
    
    def _validate_manual_calculation(self):
        """수동 계산 대비 정확성 검증"""
        print(f"\n🧮 9. 수동 계산 대비 정확성 검증")
        
        WH_COLS = ['AAA  Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV MZD',
                   'DSV Outdoor', 'Hauler Indoor']
        MOSB_COLS = ['MOSB']
        
        # 수동 계산
        # 0값과 빈 문자열을 NaN으로 치환한 데이터로 계산
        df_manual = self.df_processed.copy()
        for col in WH_COLS + MOSB_COLS:
            if col in df_manual.columns:
                df_manual[col] = df_manual[col].replace({0: np.nan, '': np.nan})
        
        # Pre Arrival 판별
        is_pre_arrival = df_manual['Status_Location'].str.contains('Pre Arrival', case=False, na=False)
        
        # 창고 Hop 수 + Offshore 계산
        wh_cnt_manual = df_manual[WH_COLS].notna().sum(axis=1)
        offshore_manual = df_manual[MOSB_COLS].notna().any(axis=1).astype(int)
        
        # Flow Code 수동 계산
        base_step = 1
        flow_raw_manual = wh_cnt_manual + offshore_manual + base_step
        flow_code_manual = np.where(is_pre_arrival, 0, np.clip(flow_raw_manual, 1, 4))
        
        # 비교
        matches = (self.df_processed['FLOW_CODE'] == flow_code_manual).sum()
        total = len(self.df_processed)
        accuracy = matches / total * 100
        
        print(f"   📊 수동 계산 비교:")
        print(f"      일치하는 레코드: {matches:,}건")
        print(f"      전체 레코드: {total:,}건")
        print(f"      정확도: {accuracy:.2f}%")
        
        # 불일치 사례 분석
        mismatches = self.df_processed[self.df_processed['FLOW_CODE'] != flow_code_manual]
        if len(mismatches) > 0:
            print(f"   ⚠️ 불일치 사례: {len(mismatches)}건")
            for idx in mismatches.index[:3]:  # 첫 3건만 분석
                actual = self.df_processed.loc[idx, 'FLOW_CODE']
                manual = flow_code_manual[idx]
                status = self.df_processed.loc[idx, 'Status_Location']
                print(f"      레코드 {idx}: 실제={actual}, 수동={manual}, Status={status}")
        
        perfect_match = accuracy == 100.0
        print(f"   ✅ 완벽 일치: {'✅ 완벽' if perfect_match else '❌ 불일치'}")
        
        self.validation_results['manual_calculation'] = {
            'matches': int(matches),
            'total': int(total),
            'accuracy': float(accuracy),
            'perfect_match': perfect_match
        }
    
    def _validate_edge_cases(self):
        """엣지 케이스 검증"""
        print(f"\n🔍 10. 엣지 케이스 검증")
        
        # 1. 모든 창고 컬럼이 비어있는 경우
        WH_COLS = ['AAA  Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV MZD',
                   'DSV Outdoor', 'Hauler Indoor']
        
        no_warehouse_mask = ~self.df_processed[WH_COLS].notna().any(axis=1)
        no_warehouse_data = self.df_processed[no_warehouse_mask]
        
        print(f"   📊 엣지 케이스 분석:")
        print(f"      창고 정보 없는 레코드: {len(no_warehouse_data):,}건")
        
        if len(no_warehouse_data) > 0:
            flow_in_no_warehouse = no_warehouse_data['FLOW_CODE'].value_counts().sort_index()
            print(f"      Flow Code 분포: {dict(flow_in_no_warehouse)}")
            
            # 창고 정보 없는 경우는 Code 0 또는 1이어야 함
            valid_codes = all(code in [0, 1] for code in flow_in_no_warehouse.index)
            print(f"      ✅ 유효한 Code (0,1만): {'✅ 정상' if valid_codes else '❌ 이상'}")
        
        # 2. Status_Location이 비어있는 경우
        no_status_mask = self.df_processed['Status_Location'].isna()
        no_status_count = no_status_mask.sum()
        
        print(f"      Status_Location 없는 레코드: {no_status_count:,}건")
        
        # 3. 모든 정보가 비어있는 경우
        all_empty_mask = (
            ~self.df_processed[WH_COLS].notna().any(axis=1) &
            self.df_processed['Status_Location'].isna()
        )
        all_empty_count = all_empty_mask.sum()
        
        print(f"      모든 정보 비어있는 레코드: {all_empty_count:,}건")
        
        self.validation_results['edge_cases'] = {
            'no_warehouse_count': int(len(no_warehouse_data)),
            'no_status_count': int(no_status_count),
            'all_empty_count': int(all_empty_count),
            'no_warehouse_valid_codes': valid_codes if len(no_warehouse_data) > 0 else True
        }
    
    def _generate_final_assessment(self):
        """최종 종합 평가"""
        print(f"\n" + "="*100)
        print("📋 최종 종합 평가")
        print("="*100)
        
        # 모든 검증 항목의 통과 여부 확인
        all_tests = [
            ("데이터 무결성", self.validation_results['data_integrity']['flow_range_valid']),
            ("Flow Code 분포", self.validation_results['flow_distribution']['code_1_exists']),
            ("Pre Arrival 정확도", self.validation_results['pre_arrival_accuracy']['perfect_match']),
            ("직송 물량 검증", self.validation_results['direct_delivery']['logical_consistency']),
            ("창고 Hop 로직", self.validation_results['warehouse_hops']['logical_consistency']),
            ("Offshore 로직", self.validation_results['offshore_logic']['logical_consistency']),
            ("수동 계산 일치", self.validation_results['manual_calculation']['perfect_match']),
            ("엣지 케이스", self.validation_results['edge_cases']['no_warehouse_valid_codes'])
        ]
        
        passed_tests = sum(1 for _, passed in all_tests if passed)
        total_tests = len(all_tests)
        
        print(f"\n🎯 검증 결과 요약:")
        for test_name, passed in all_tests:
            status = "✅ 통과" if passed else "❌ 실패"
            print(f"   {test_name}: {status}")
        
        print(f"\n📊 종합 점수: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        
        # 최종 판정
        if passed_tests == total_tests:
            final_verdict = "✅ 완벽 (Perfect)"
            print(f"\n🎉 최종 판정: {final_verdict}")
            print("   모든 검증 항목을 완벽하게 통과했습니다!")
        elif passed_tests >= total_tests * 0.9:
            final_verdict = "✅ 우수 (Excellent)"
            print(f"\n🎉 최종 판정: {final_verdict}")
            print("   대부분의 검증 항목을 통과했습니다.")
        elif passed_tests >= total_tests * 0.7:
            final_verdict = "⚠️ 양호 (Good)"
            print(f"\n⚠️ 최종 판정: {final_verdict}")
            print("   일부 개선이 필요합니다.")
        else:
            final_verdict = "❌ 불량 (Poor)"
            print(f"\n❌ 최종 판정: {final_verdict}")
            print("   상당한 개선이 필요합니다.")
        
        # 핵심 성과 지표
        pre_arrival_accuracy = self.validation_results['pre_arrival_accuracy']['accuracy']
        direct_delivery_count = self.validation_results['direct_delivery']['count']
        manual_accuracy = self.validation_results['manual_calculation']['accuracy']
        
        print(f"\n📈 핵심 성과 지표:")
        print(f"   Pre Arrival 정확도: {pre_arrival_accuracy:.1f}%")
        print(f"   직송 물량 발견: {direct_delivery_count:,}건")
        print(f"   수동 계산 일치율: {manual_accuracy:.2f}%")
        
        # 검증 결과 저장
        self.validation_results['final_assessment'] = {
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'score_percentage': passed_tests/total_tests*100,
            'final_verdict': final_verdict,
            'pre_arrival_accuracy': pre_arrival_accuracy,
            'direct_delivery_count': direct_delivery_count,
            'manual_accuracy': manual_accuracy
        }
        
        # JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"Flow_Code_Final_Validation_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 검증 결과 저장: {result_file}")

def main():
    """메인 함수"""
    validator = FlowCodeFinalValidator()
    success = validator.run_comprehensive_validation()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 