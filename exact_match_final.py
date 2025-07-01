#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC Flow Code 공식 기준 완전 일치 계산기 최종 버전
목표: 각 행을 개별 케이스로 처리하여 공식 기준과 100% 일치
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

def main():
    print("🎯 MACHO-GPT v3.4-mini 공식 기준 완전 일치 솔루션")
    print("=" * 60)
    
    # 공식 기준
    official_targets = {
        'HITACHI': {'total_rows': 5346, 'code_0': 163, 'code_1': 2062, 'code_2': 2842, 'code_3': 274, 'code_4': 5},
        'SIMENSE': {'total_rows': 2227, 'code_0': 384, 'code_1': 804, 'code_2': 805, 'code_3': 234, 'code_4': 1851}
    }
    
    files = {
        'HITACHI': 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
        'SIMENSE': 'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    }
    
    total_cases = 0
    all_results = []
    
    for vendor, file_path in files.items():
        if not Path(file_path).exists():
            print(f"❌ 파일 없음: {file_path}")
            continue
            
        print(f"\n📄 {vendor} 처리 중...")
        df = pd.read_excel(file_path)
        
        # Pre Arrival 필터링
        if 'Status' in df.columns:
            pre_count = len(df[df['Status'] == 'PRE ARRIVAL'])
            df_filtered = df[df['Status'] != 'PRE ARRIVAL']
            print(f"   🚫 Pre Arrival 제외: {pre_count:,}건")
        else:
            pre_count = 0
            df_filtered = df
        
        actual_cases = len(df_filtered)
        expected_cases = official_targets[vendor]['total_rows'] - official_targets[vendor]['code_0']
        
        print(f"   📊 실제 케이스: {actual_cases:,}개")
        print(f"   🎯 기대 케이스: {expected_cases:,}개")
        print(f"   ✅ 일치 여부: {'✅' if actual_cases == expected_cases else '❌'}")
        
        total_cases += actual_cases
        
        # 창고 컬럼 확인
        wh_cols = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP', 'DSV MZD', 'JDN MZD', 'AAA  Storage', 'Hauler Indoor']
        found_wh_cols = [col for col in wh_cols if col in df_filtered.columns]
        print(f"   🏢 발견된 창고 컬럼: {len(found_wh_cols)}개 - {found_wh_cols}")
        
        # 각 행에 대해 Flow Code 계산
        flow_codes = []
        
        for idx, row in df_filtered.iterrows():
            # 창고 방문 수 계산
            wh_visits = 0
            for col in found_wh_cols:
                if pd.notna(row.get(col)) and str(row.get(col)).strip():
                    wh_visits += 1
            
            # MOSB 확인
            has_mosb = pd.notna(row.get('MOSB')) and str(row.get('MOSB')).strip()
            
            # Flow Code 결정
            if wh_visits == 0:
                flow_code = 1  # Port → Site
            elif wh_visits == 1 and not has_mosb:
                flow_code = 2  # Port → WH → Site
            elif wh_visits == 1 and has_mosb:
                flow_code = 3  # Port → WH → MOSB → Site
            else:
                flow_code = 4  # Port → WH × 2+ → Site
            
            flow_codes.append(flow_code)
        
        # Flow Code 분포 계산
        distribution = Counter(flow_codes)
        
        print(f"   📊 Flow Code 분포:")
        total_match = True
        for code in range(1, 5):
            actual = distribution.get(code, 0)
            expected = official_targets[vendor].get(f'code_{code}', 0)
            status = "✅" if actual == expected else "❌"
            if actual != expected:
                total_match = False
            print(f"      Code {code}: {actual:,} (기대: {expected:,}) {status}")
        
        # 결과 저장
        vendor_results = []
        for i, flow_code in enumerate(flow_codes):
            vendor_results.append({
                'Vendor': vendor,
                'Row_Index': df_filtered.index[i],
                'Flow_Code': flow_code
            })
        
        all_results.extend(vendor_results)
        
        print(f"   🎯 벤더 일치 여부: {'✅ 완전 일치' if total_match else '❌ 불일치'}")
    
    print(f"\n🎯 **최종 결과:**")
    print(f"   총 케이스: {total_cases:,}개 (기대: 7,573개)")
    
    if all_results:
        # 통합 결과 생성
        results_df = pd.DataFrame(all_results)
        
        # 벤더별 요약
        summary = results_df.groupby(['Vendor', 'Flow_Code']).size().unstack(fill_value=0)
        print(f"\n📊 **통합 Flow Code 분포:**")
        print(summary)
        
        # 엑셀 저장
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"HVDC_ExactMatch_FlowCode_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file) as writer:
            results_df.to_excel(writer, sheet_name='Flow_Codes', index=False)
            summary.to_excel(writer, sheet_name='Summary')
        
        print(f"✅ 결과 저장: {output_file}")
    
    print(f"\n🔧 **추천 명령어:**")
    print("/validate_exact_match [정확도 검증]")
    print("/generate_flow_report [Flow Code 리포트 생성]")
    print("/debug_remaining_gaps [남은 차이 디버깅]")

if __name__ == "__main__":
    main() 