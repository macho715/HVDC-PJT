#!/usr/bin/env python3
"""
HVDC Excel Reporter Fix v3.2 검증 스크립트
핵심 버그 수정: calculate_final_location() 함수 Status_Location 동적 값 처리
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

def main():
    """Fix v3.2 검증 실행"""
    logger.info("🔍 HVDC Excel Reporter Fix v3.2 검증 시작")
    
    try:
        # 1. 계산기 초기화
        calc = WarehouseIOCalculator()
        
        # 2. 실제 데이터 로드
        logger.info("📂 실제 데이터 로드")
        df_raw = calc.load_real_hvdc_data()
        
        # 3. 데이터 전처리
        logger.info("🔧 데이터 전처리")
        df_processed = calc.process_real_data()
        
        # 4. 핵심 수정: Final Location 계산
        logger.info("🎯 Fix v3.2: Final Location 계산")
        df_fixed = calc.calculate_final_location(df_processed)
        
        # 5. ① 최종 위치 sanity check
        logger.info("✅ 1. 최종 위치 sanity check")
        final_location_counts = df_fixed['Final_Location'].value_counts()
        print("\n📊 Final_Location 분포:")
        print(final_location_counts.head(10))
        
        # 6. ② 월별 재고 생성 및 검증
        logger.info("✅ 2. 월별 재고 생성 및 검증")
        inventory_result = calc.calculate_warehouse_inventory(df_fixed)
        
        print("\n📊 최근 3개월 재고 현황:")
        recent_months = sorted(inventory_result['inventory_by_month'].keys())[-3:]
        for month in recent_months:
            inventory = inventory_result['inventory_by_month'][month]
            print(f"  {month}: {inventory:,} 개")
        
        # 7. ③ 피벗 확인 (핵심 검증)
        logger.info("✅ 3. 피벗 확인 (핵심 검증)")
        
        # 간단한 그룹별 집계로 피벗 확인
        df_pivot_check = df_fixed.groupby(['Final_Location']).size().reset_index(name='Count')
        print("\n📊 Final_Location별 레코드 수:")
        print(df_pivot_check)
        
        # 8. 전체 요약 출력
        logger.info("✅ 4. 전체 요약")
        print("\n📋 검증 요약:")
        print(f"  - 총 레코드 수: {len(df_fixed):,}")
        print(f"  - Final_Location 유니크 값: {df_fixed['Final_Location'].nunique()}")
        print(f"  - Unknown 비율: {(df_fixed['Final_Location'] == 'Unknown').sum() / len(df_fixed) * 100:.1f}%")
        print(f"  - 총 재고 (2025-06): {inventory_result['inventory_by_month'].get('2025-06', 0):,}")
        
        # 9. 성공 여부 판단
        success_conditions = [
            df_fixed['Final_Location'].nunique() > 3,  # 최소 3개 이상 위치
            inventory_result['total_inventory'] > 0,    # 재고 존재
            (df_fixed['Final_Location'] == 'Unknown').sum() < len(df_fixed) * 0.5  # Unknown 50% 미만
        ]
        
        if all(success_conditions):
            logger.info("🎉 Fix v3.2 검증 성공!")
            print("\n✅ 모든 검증 조건 통과")
            return True
        else:
            logger.warning("⚠️ 일부 검증 조건 실패")
            print("\n❌ 검증 조건 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ 검증 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 