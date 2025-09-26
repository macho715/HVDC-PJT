#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC 케이스 수 차이 검증 스크립트
목표: 7,573개 vs 현재 1,917개 차이 원인 파악
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_case_counts():
    """케이스 수 차이 분석"""
    
    print("🎯 MACHO-GPT v3.4-mini 케이스 수 차이 검증")
    print("=" * 60)
    
    # 공식 기준
    official_targets = {
        'HITACHI': 5346,
        'SIMENSE': 2227,
        'TOTAL': 7573
    }
    
    files = {
        'HITACHI': 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
        'SIMENSE': 'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    }
    
    total_found = 0
    
    for vendor, file_path in files.items():
        print(f"\n📄 {vendor} 분석: {file_path}")
        
        if not Path(file_path).exists():
            print(f"   ❌ 파일 없음")
            continue
            
        try:
            # 원본 로드
            df = pd.read_excel(file_path)
            print(f"   📊 원본 행 수: {len(df):,}")
            
            # Pre Arrival 확인
            if 'Status' in df.columns:
                pre_arrival = df[df['Status'] == 'PRE ARRIVAL']
                pre_count = len(pre_arrival)
                print(f"   🚫 Pre Arrival: {pre_count:,}건")
                
                # 필터링 후
                df_filtered = df[df['Status'] != 'PRE ARRIVAL']
                print(f"   ✅ 필터링 후: {len(df_filtered):,}행")
            else:
                df_filtered = df
                print(f"   ⚠️ Status 컬럼 없음")
            
            # 케이스 컬럼 감지
            case_cols = []
            if vendor == 'HITACHI':
                candidates = ['HVDC CODE', 'Case No.', 'HVDC_CODE']
            else:
                candidates = ['SERIAL NO.', 'HVDC CODE', 'SERIAL_NO']
            
            for col in candidates:
                if col in df_filtered.columns:
                    unique_count = df_filtered[col].nunique()
                    non_null_count = df_filtered[col].notna().sum()
                    case_cols.append((col, unique_count, non_null_count))
                    print(f"   📦 {col}: {unique_count:,}개 고유값 ({non_null_count:,}개 비어있지 않음)")
            
            if case_cols:
                # 가장 적절한 컬럼 선택
                best_col = max(case_cols, key=lambda x: x[1])
                case_col, unique_count, non_null = best_col
                print(f"   ✅ 선택된 케이스 컬럼: {case_col}")
                
                # 공식 기준과 비교
                expected = official_targets[vendor]
                diff = unique_count - expected
                status = "✅" if diff == 0 else "❌"
                
                print(f"   🎯 케이스 수 검증:")
                print(f"      발견: {unique_count:,}개")
                print(f"      기대: {expected:,}개")
                print(f"      차이: {diff:+,}개 {status}")
                
                total_found += unique_count
                
                # 샘플 케이스 확인
                sample_cases = df_filtered[case_col].dropna().head(5).tolist()
                print(f"   📋 샘플 케이스: {sample_cases}")
                
            else:
                print(f"   ❌ 적절한 케이스 컬럼을 찾을 수 없음")
            
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print(f"\n📊 **총 결과 요약:**")
    print(f"   발견된 총 케이스: {total_found:,}개")
    print(f"   공식 기준 총계: {official_targets['TOTAL']:,}개")
    print(f"   차이: {total_found - official_targets['TOTAL']:+,}개")
    
    if total_found != official_targets['TOTAL']:
        print(f"\n🔍 **차이 원인 분석:**")
        if total_found < official_targets['TOTAL']:
            print("   - 데이터 누락 가능성")
            print("   - 필터링 과정에서 케이스 손실")
            print("   - 잘못된 케이스 컬럼 선택")
        else:
            print("   - 중복 케이스 존재")
            print("   - 다른 케이스 컬럼 사용 필요")
    
    print(f"\n🔧 **추천 명령어:**")
    print("/validate_exact_case_columns [정확한 케이스 컬럼 검증]")
    print("/check_pre_arrival_impact [Pre Arrival 영향 분석]")
    print("/debug_case_filtering [케이스 필터링 디버깅]")

if __name__ == "__main__":
    analyze_case_counts() 