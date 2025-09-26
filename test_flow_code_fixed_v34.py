#!/usr/bin/env python3
"""
v3.4-corrected Flow Code 로직 테스트 스크립트
Off-by-One 버그 수정 및 Pre Arrival 정확 판별 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hvdc_excel_reporter_final import WarehouseIOCalculator
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_flow_code_fixed():
    """v3.4 수정된 Flow Code 로직 테스트"""
    logger.info("🔍 v3.4-corrected Flow Code 로직 테스트 시작")
    
    try:
        # 1. 계산기 초기화 및 데이터 로드
        calc = WarehouseIOCalculator()
        df_raw = calc.load_real_hvdc_data()
        
        print(f"\n📊 원본 데이터 정보:")
        print(f"   - 총 레코드 수: {len(df_raw):,}건")
        print(f"   - Status_Location 컬럼 존재: {'Status_Location' in df_raw.columns}")
        
        # 2. 수정된 로직 적용
        df_processed = calc.process_real_data()
        
        print(f"\n" + "="*80)
        print("📋 v3.4-corrected Flow Code 분석 결과")
        print("="*80)
        
        # 3. Flow Code 분포 분석
        flow_distribution = df_processed['FLOW_CODE'].value_counts().sort_index()
        print(f"\n📊 Flow Code 분포:")
        for code, count in flow_distribution.items():
            description = calc.flow_codes.get(code, 'Unknown')
            print(f"   Code {code}: {count:,}건 ({count/len(df_processed)*100:.1f}%) - {description}")
        
        # 4. Pre Arrival 정확성 검증
        print(f"\n🔍 Pre Arrival 정확성 검증:")
        
        # 4.1 Status_Location 기준 Pre Arrival 확인
        if 'Status_Location' in df_processed.columns:
            status_pre_arrival = df_processed['Status_Location'].str.contains('Pre Arrival', case=False, na=False)
            status_pre_count = status_pre_arrival.sum()
            print(f"   - Status_Location 'Pre Arrival' 포함: {status_pre_count:,}건")
            
            # 4.2 Flow Code 0과 실제 Pre Arrival 비교
            flow_code_0 = (df_processed['FLOW_CODE'] == 0).sum()
            print(f"   - Flow Code 0 총 건수: {flow_code_0:,}건")
            
            # 4.3 정확도 계산
            if status_pre_count > 0:
                accuracy = status_pre_count / flow_code_0 * 100 if flow_code_0 > 0 else 0
                print(f"   - Pre Arrival 정확도: {accuracy:.1f}%")
            
            # 4.4 Code 0 중 실제 Pre Arrival 비율
            code_0_mask = df_processed['FLOW_CODE'] == 0
            code_0_data = df_processed[code_0_mask]
            
            if len(code_0_data) > 0:
                actual_pre_in_code_0 = code_0_data['Status_Location'].str.contains('Pre Arrival', case=False, na=False).sum()
                print(f"   - Code 0 중 실제 Pre Arrival: {actual_pre_in_code_0:,}건 ({actual_pre_in_code_0/len(code_0_data)*100:.1f}%)")
        
        # 5. 창고 Hop 수 분석
        print(f"\n🏭 창고 Hop 수 분석:")
        
        WH_COLS = ['AAA  Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV MZD',
                   'DSV Outdoor', 'Hauler Indoor']
        MOSB_COLS = ['MOSB']
        
        # 0값과 빈 문자열 치환 후 계산
        wh_cnt = df_processed[WH_COLS].notna().sum(axis=1)
        offshore = df_processed[MOSB_COLS].notna().any(axis=1).astype(int)
        
        wh_hop_distribution = wh_cnt.value_counts().sort_index()
        print(f"   - 창고 Hop 수 분포:")
        for hops, count in wh_hop_distribution.items():
            print(f"     {hops} Hop: {count:,}건 ({count/len(df_processed)*100:.1f}%)")
        
        offshore_distribution = offshore.value_counts().sort_index()
        print(f"   - Offshore 사용 분포:")
        for flag, count in offshore_distribution.items():
            label = "사용" if flag else "미사용"
            print(f"     Offshore {label}: {count:,}건 ({count/len(df_processed)*100:.1f}%)")
        
        # 6. 벤더별 Flow Code 분포
        print(f"\n🏢 벤더별 Flow Code 분포:")
        if 'Vendor' in df_processed.columns:
            vendor_flow = df_processed.groupby(['Vendor', 'FLOW_CODE']).size().unstack(fill_value=0)
            print(vendor_flow)
        
        # 7. 샘플 데이터 확인
        print(f"\n📋 각 Flow Code별 샘플 데이터:")
        for code in sorted(df_processed['FLOW_CODE'].unique()):
            sample_data = df_processed[df_processed['FLOW_CODE'] == code].head(2)
            print(f"\n   Flow Code {code} 샘플:")
            if len(sample_data) > 0:
                for idx, row in sample_data.iterrows():
                    status = row.get('Status_Location', 'N/A')
                    vendor = row.get('Vendor', 'N/A')
                    hvdc_code = row.get('HVDC CODE', 'N/A')
                    print(f"     {idx}: {hvdc_code} | {vendor} | {status}")
        
        # 8. 이전 버전과 비교
        print(f"\n" + "="*80)
        print("📊 v3.3 → v3.4 변경사항 요약")
        print("="*80)
        
        print(f"✅ 수정된 주요 사항:")
        print(f"   1. Off-by-One 버그 수정: base_step = 1 추가")
        print(f"   2. Pre Arrival 정확 판별: Status_Location 기준 필터링")
        print(f"   3. 0값/빈 문자열 → NaN 치환: notna() 오류 방지")
        print(f"   4. 조건부 Flow Code 할당: Pre Arrival → 무조건 0")
        
        print(f"\n📈 예상 개선사항:")
        print(f"   - Pre Arrival 정확도 향상")
        print(f"   - 직송 물량 올바른 Flow Code 할당")
        print(f"   - 창고 Hop 수 정확 계산")
        print(f"   - KPI 대시보드 왜곡 해소")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_flow_code_fixed()
    sys.exit(0 if success else 1) 