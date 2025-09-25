#!/usr/bin/env python3
"""
v3.3-flow override 패치 검증 스크립트
wh handling 우회 + Hop 기준 Flow Code 재계산 확인
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

def test_flow_override():
    """v3.3-flow override 패치 검증"""
    logger.info("🔍 v3.3-flow override 패치 검증 시작")
    
    try:
        # 1. 계산기 초기화
        calc = WarehouseIOCalculator()
        
        # 2. 실제 데이터 로드
        logger.info("📂 실제 데이터 로드")
        df_raw = calc.load_real_hvdc_data()
        
        # 3. 기존 wh handling 분포 확인 (패치 적용 전)
        if 'wh handling' in df_raw.columns:
            original_wh_counts = df_raw['wh handling'].value_counts().sort_index()
            print("\n📊 기존 wh handling 분포:")
            print(original_wh_counts)
        
        # 4. 데이터 전처리 (패치 적용)
        logger.info("🔧 데이터 전처리 (v3.3-flow override 적용)")
        df_processed = calc.process_real_data()
        
        # 5. 새로운 FLOW_CODE 분포 확인
        logger.info("✅ 새로운 FLOW_CODE 분포 확인")
        new_flow_counts = df_processed['FLOW_CODE'].value_counts().sort_index()
        print("\n📊 새로운 FLOW_CODE 분포:")
        for code, count in new_flow_counts.items():
            description = calc.flow_codes.get(code, 'Unknown')
            print(f"  Code {code}: {count:,}건 ({description})")
        
        # 6. wh_handling_legacy 컬럼 확인
        if 'wh_handling_legacy' in df_processed.columns:
            logger.info("✅ wh_handling_legacy 컬럼 보존 확인")
            legacy_counts = df_processed['wh_handling_legacy'].value_counts().sort_index()
            print("\n📊 wh_handling_legacy 분포:")
            print(legacy_counts)
        
        # 7. 검증 기준 확인
        logger.info("✅ 검증 기준 확인")
        code_0_count = new_flow_counts.get(0, 0)
        code_4_count = new_flow_counts.get(4, 0)
        
        # 8. 검증 결과 출력
        print("\n📋 검증 결과:")
        print(f"  - 총 레코드 수: {len(df_processed):,}")
        print(f"  - Code 0 (Pre Arrival): {code_0_count:,}건")
        print(f"  - Code 4 (Multi-hop): {code_4_count:,}건")
        print(f"  - wh_handling_legacy 보존: {'✅' if 'wh_handling_legacy' in df_processed.columns else '❌'}")
        
        # 9. 기대값과 비교 (실제 데이터 기준 조정)
        expected_conditions = [
            code_0_count > 0,     # Pre Arrival 존재
            code_4_count >= 5,    # Multi-hop 5건 이상
            'wh_handling_legacy' in df_processed.columns  # Legacy 컬럼 보존
        ]
        
        if all(expected_conditions):
            logger.info("🎉 v3.3-flow override 패치 검증 성공!")
            print("\n✅ 모든 검증 조건 통과")
            return True
        else:
            logger.warning("⚠️ 일부 검증 조건 실패")
            print("\n❌ 검증 조건 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ 검증 중 오류 발생: {str(e)}")
        return False

def analyze_flow_distribution():
    """Flow Code 분포 상세 분석"""
    logger.info("🔍 Flow Code 분포 상세 분석")
    
    calc = WarehouseIOCalculator()
    df_raw = calc.load_real_hvdc_data()
    df_processed = calc.process_real_data()
    
    # 창고별 Hop 수 분석 (실제 데이터 기준)
    WH_COLS = ['AAA  Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP', 'DSV MZD',
               'DSV Outdoor', 'Hauler Indoor']
    MOSB_COLS = ['MOSB']
    
    wh_cnt = df_processed[WH_COLS].notna().sum(axis=1)
    offshore = df_processed[MOSB_COLS].notna().any(axis=1).astype(int)
    
    print("\n📊 창고 Hop 수 분포:")
    print(wh_cnt.value_counts().sort_index())
    
    print("\n📊 Offshore (MOSB) 분포:")
    print(offshore.value_counts().sort_index())
    
    print("\n📊 최종 FLOW_CODE 계산 검증:")
    calculated_flow = (wh_cnt + offshore).clip(0, 4)
    print(calculated_flow.value_counts().sort_index())
    
    # 실제 FLOW_CODE와 비교
    print("\n📊 실제 FLOW_CODE와 일치 여부:")
    match_count = (calculated_flow == df_processed['FLOW_CODE']).sum()
    print(f"  - 일치 레코드: {match_count:,}/{len(df_processed):,}")
    print(f"  - 일치율: {match_count/len(df_processed)*100:.2f}%")

if __name__ == "__main__":
    success = test_flow_override()
    if success:
        analyze_flow_distribution()
    sys.exit(0 if success else 1) 