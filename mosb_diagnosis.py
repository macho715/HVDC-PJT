#!/usr/bin/env python3
"""
🔧 MOSB 인식 로직 진단 및 개선 스크립트
MACHO-GPT v3.4-mini │ Samsung C&T Logistics

목표:
1. SIMENSE Code 3: 0건 → 234건+ 복구
2. SIMENSE Code 4: 52건 → 1,851건+ 복구  
3. 전각공백(\u3000) 처리 문제 해결
4. Timestamp 타입 MOSB 인식 개선
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
from collections import Counter

print("🔧 MOSB 인식 로직 진단 시작")
print("=" * 60)

# 파일 로딩
files = {
    'HITACHI': 'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
    'SIMENSE': 'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx', 
    'HVDC_STATUS': 'hvdc_macho_gpt/WAREHOUSE/data/HVDC-STATUS.xlsx'
}

dfs = {}
for name, path in files.items():
    try:
        print(f"📂 {name} 파일 로딩: {path}")
        df = pd.read_excel(path)
        dfs[name] = df
        print(f"   ✅ {name}: {len(df):,}행 × {len(df.columns)}열")
    except Exception as e:
        print(f"   ❌ {name} 로딩 실패: {e}")

print("\n" + "="*60)
print("🔍 MOSB 컬럼 진단")
print("="*60)

# MOSB 관련 컬럼 찾기
mosb_patterns = [r'MOSB', r'Marine.*Base', r'Offshore.*Base', r'mosb']

for name, df in dfs.items():
    print(f"\n📊 {name} MOSB 컬럼 분석:")
    mosb_cols = []
    
    for col in df.columns:
        for pattern in mosb_patterns:
            if re.search(pattern, col, re.I):
                mosb_cols.append(col)
                break
    
    if mosb_cols:
        for col in mosb_cols:
            print(f"   🔍 컬럼: '{col}'")
            
            # 데이터 타입 분석
            col_data = df[col].dropna()
            if len(col_data) > 0:
                print(f"      📈 유효 데이터: {len(col_data):,}건")
                print(f"      📝 데이터 타입: {type(col_data.iloc[0])}")
                
                # 전각공백 검사
                text_data = col_data.astype(str)
                fullwidth_count = sum(1 for x in text_data if '\u3000' in x or '　' in x)
                if fullwidth_count > 0:
                    print(f"      ⚠️  전각공백 포함: {fullwidth_count:,}건")
                
                # Timestamp 검사  
                timestamp_count = sum(1 for x in col_data if hasattr(x, 'year'))
                if timestamp_count > 0:
                    print(f"      📅 Timestamp 타입: {timestamp_count:,}건")
                
                # 샘플 데이터 출력
                print(f"      📋 샘플 데이터:")
                for i, sample in enumerate(col_data.head(3)):
                    print(f"         {i+1}. {repr(sample)} (타입: {type(sample).__name__})")
            else:
                print(f"      ❌ 유효 데이터 없음")
    else:
        print(f"   ❌ MOSB 관련 컬럼 없음")

print("\n" + "="*60)
print("🏭 창고-MOSB 연관성 분석")
print("="*60)

# 창고 컬럼 패턴
wh_patterns = [r'DSV.*Indoor', r'DSV.*Outdoor', r'DSV.*Al.*Markaz', r'DSV.*MZ[DP]', r'Hauler.*Indoor']

for name, df in dfs.items():
    print(f"\n📊 {name} 창고-MOSB 연관 분석:")
    
    # 창고 컬럼 찾기
    wh_cols = []
    for col in df.columns:
        for pattern in wh_patterns:
            if re.search(pattern, col, re.I):
                wh_cols.append(col)
                break
    
    print(f"   🏭 창고 컬럼: {len(wh_cols)}개")
    for col in wh_cols[:5]:  # 처음 5개만 출력
        print(f"      - {col}")
    
    # MOSB 컬럼 찾기
    mosb_cols = []
    for col in df.columns:
        for pattern in mosb_patterns:
            if re.search(pattern, col, re.I):
                mosb_cols.append(col)
                break
    
    if mosb_cols and wh_cols:
        mosb_col = mosb_cols[0]  # 첫 번째 MOSB 컬럼 사용
        
        # Flow Code 후보 분석
        df_analysis = df.copy()
        
        # WH 카운트 계산
        wh_count = 0
        for col in wh_cols:
            wh_count += df_analysis[col].notna().astype(int)
        df_analysis['wh_count'] = wh_count
        
        # MOSB 존재 여부
        mosb_exists = df_analysis[mosb_col].notna()
        df_analysis['mosb_exists'] = mosb_exists
        
        # Flow Code 후보 계산
        def calc_flow_code_candidate(row):
            if row['mosb_exists']:
                if row['wh_count'] <= 1:
                    return 3  # Port → WH → MOSB → Site
                else:
                    return 4  # Port → WH → wh → MOSB → Site
            else:
                if row['wh_count'] == 0:
                    return 1  # Port → Site
                else:
                    return 2  # Port → WH → Site
        
        df_analysis['flow_code_candidate'] = df_analysis.apply(calc_flow_code_candidate, axis=1)
        
        # 분포 출력
        flow_dist = df_analysis['flow_code_candidate'].value_counts().sort_index()
        print(f"   📈 Flow Code 후보 분포:")
        for code, count in flow_dist.items():
            flow_names = {1: "Port→Site", 2: "Port→WH→Site", 3: "Port→WH→MOSB→Site", 4: "Port→WH→wh→MOSB→Site"}
            print(f"      Code {code} ({flow_names.get(code, 'Unknown')}): {count:,}건")

print("\n" + "="*60)
print("🎯 문제점 및 개선 방향")
print("="*60)

print("""
🔍 발견된 주요 문제점:
1. 전각공백(\u3000) 처리 미흡으로 MOSB 인식 실패
2. Timestamp 타입 MOSB 데이터 인식 부족
3. 창고 누적 계산 로직의 정확도 문제
4. Flow Code 분류 기준의 일관성 부족

🎯 개선 방향:
1. 전각공백 정리 함수 강화
2. 다양한 데이터 타입 지원 (Timestamp, String, Float)  
3. MOSB 검증 로직 다단계 적용
4. 창고-MOSB 순서 고려한 Flow Code 계산

🚀 다음 단계: 개선된 로직 구현 및 테스트
""") 