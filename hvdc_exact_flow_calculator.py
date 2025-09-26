#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC Flow Code 공식 기준 완전 일치 계산기
MACHO-GPT v3.4-mini | Samsung C&T × ADNOC·DSV Partnership

목표: 공식 보고서와 100% 일치
- SIMENSE Code 4: 1,851건
- HITACHI Code 3: 274건, Code 4: 5건
- 총 케이스: 7,573개
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowCodeExactCalculator:
    """공식 기준 완전 일치 Flow Code 계산기"""
    
    def __init__(self):
        # 공식 기준 타겟
        self.official_targets = {
            'HITACHI': {'total': 5346, 'code_0': 163, 'code_1': 2062, 'code_2': 2842, 'code_3': 274, 'code_4': 5},
            'SIMENSE': {'total': 2227, 'code_0': 384, 'code_1': 804, 'code_2': 805, 'code_3': 234, 'code_4': 1851}
        }
        
    def detect_case_column(self, df, vendor_hint=None):
        """케이스 컬럼 감지"""
        if vendor_hint == 'HITACHI':
            candidates = ['HVDC CODE', 'Case No.']
        elif vendor_hint == 'SIMENSE':
            candidates = ['SERIAL NO.', 'HVDC CODE']
        else:
            candidates = ['HVDC CODE', 'SERIAL NO.', 'Case No.']
        
        for col in candidates:
            if col in df.columns:
                unique_count = df[col].nunique()
                logger.info(f"✅ Case 컬럼 발견: {col} ({unique_count:,}개)")
                return col
        
        # 패턴 매칭
        for col in df.columns:
            if re.search(r'(HVDC|SERIAL|Case)', col, re.I):
                unique_count = df[col].nunique()
                if unique_count > 1000:
                    logger.info(f"✅ 패턴 매칭: {col} ({unique_count:,}개)")
                    return col
        
        raise ValueError("적절한 Case 컬럼을 찾을 수 없습니다.")
    
    def detect_warehouse_columns(self, df):
        """창고 컬럼 감지"""
        wh_cols = []
        
        # 정확한 컬럼명들
        exact_names = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz',
            'DSV MZP', 'DSV MZD', 'JDN MZD',
            'AAA  Storage', 'AAA Storage',
            'Hauler Indoor'
        ]
        
        for col in exact_names:
            if col in df.columns:
                wh_cols.append(col)
                logger.info(f"✅ WH 컬럼 발견: {col}")
        
        logger.info(f"📋 총 WH 컬럼: {len(wh_cols)}개")
        return wh_cols
    
    def calculate_flow_code_for_case(self, case_data, wh_cols):
        """개별 케이스의 Flow Code 계산"""
        
        # 방문한 창고 수 계산
        visited_warehouses = 0
        has_mosb = False
        
        for _, row in case_data.iterrows():
            for wh_col in wh_cols:
                if pd.notna(row.get(wh_col)) and str(row.get(wh_col)).strip():
                    visited_warehouses += 1
                    break  # 해당 행에서 창고 방문 확인됨
            
            # MOSB 확인
            if pd.notna(row.get('MOSB')) and str(row.get('MOSB')).strip():
                has_mosb = True
        
        # Flow Code 결정
        if visited_warehouses == 0:
            return 1  # Port → Site 직송
        elif visited_warehouses == 1 and not has_mosb:
            return 2  # Port → WH → Site
        elif visited_warehouses == 1 and has_mosb:
            return 3  # Port → WH → MOSB → Site
        elif visited_warehouses >= 2:
            return 4  # Port → WH × 2+ → MOSB → Site
        else:
            return 1  # 기본값
    
    def process_file(self, file_path, vendor_hint=None):
        """파일 처리"""
        logger.info(f"📄 처리 중: {file_path}")
        
        df = pd.read_excel(file_path)
        logger.info(f"📊 원본 데이터: {len(df):,}행")
        
        # Pre Arrival 필터링
        if 'Status' in df.columns:
            pre_arrival_count = len(df[df['Status'] == 'PRE ARRIVAL'])
            df = df[df['Status'] != 'PRE ARRIVAL']
            logger.info(f"🚫 Pre Arrival 제외: {pre_arrival_count}건")
        
        logger.info(f"✅ 필터링 후: {len(df):,}행")
        
        # 컬럼 감지
        case_col = self.detect_case_column(df, vendor_hint)
        wh_cols = self.detect_warehouse_columns(df)
        
        # 케이스별 Flow Code 계산
        results = []
        
        for case_id in df[case_col].unique():
            if pd.notna(case_id):
                case_data = df[df[case_col] == case_id]
                flow_code = self.calculate_flow_code_for_case(case_data, wh_cols)
                results.append({
                    'Case_ID': case_id,
                    'Vendor': vendor_hint,
                    'Flow_Code': flow_code
                })
        
        result_df = pd.DataFrame(results)
        logger.info(f"✅ 케이스 처리 완료: {len(result_df):,}개")
        
        return result_df
    
    def validate_results(self, df, vendor_hint):
        """결과 검증"""
        distribution = df['Flow_Code'].value_counts().sort_index()
        logger.info(f"📊 {vendor_hint} Flow Code 분포:")
        for code in range(5):
            count = distribution.get(code, 0)
            expected = self.official_targets[vendor_hint][f'code_{code}']
            status = "✅" if count == expected else "❌"
            logger.info(f"   Code {code}: {count:,}건 (기대: {expected:,}) {status}")
        
        total = len(df)
        expected_total = self.official_targets[vendor_hint]['total']
        total_status = "✅" if total == expected_total else "❌"
        logger.info(f"📦 총 케이스: {total:,}개 (기대: {expected_total:,}) {total_status}")

def main():
    """메인 실행 함수"""
    calculator = FlowCodeExactCalculator()
    
    # 파일 경로
    files = {
        'HITACHI': 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
        'SIMENSE': 'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    }
    
    all_results = []
    
    for vendor, file_path in files.items():
        if Path(file_path).exists():
            try:
                result = calculator.process_file(file_path, vendor)
                calculator.validate_results(result, vendor)
                all_results.append(result)
            except Exception as e:
                logger.error(f"❌ {vendor} 처리 실패: {e}")
        else:
            logger.warning(f"⚠️ 파일 없음: {file_path}")
    
    if all_results:
        # 통합 결과
        combined = pd.concat(all_results, ignore_index=True)
        
        # 요약 생성
        summary = combined.groupby(['Vendor', 'Flow_Code']).size().unstack(fill_value=0)
        print("\n📊 **최종 Flow Code 분포:**")
        print(summary)
        
        # 엑셀 저장
        output_file = f"HVDC_ExactMatch_FlowCode_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with pd.ExcelWriter(output_file) as writer:
            combined.to_excel(writer, sheet_name='Flow_Codes', index=False)
            summary.to_excel(writer, sheet_name='Summary')
        
        logger.info(f"✅ 결과 저장: {output_file}")

if __name__ == "__main__":
    main() 