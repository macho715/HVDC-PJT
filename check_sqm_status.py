#!/usr/bin/env python3
"""
SQM 데이터 현황 확인 스크립트
"""
import pandas as pd

def check_sqm_status():
    """SQM 데이터 현황 확인"""
    print("=== 현재 SQM 데이터 현황 확인 ===")
    
    try:
        # 현재 통합시스템 확인
        df = pd.read_excel('output/화물이력관리_통합시스템_20250703_175306.xlsx')
        print(f"총 레코드: {len(df)}건")
        print(f"SQM 컬럼 존재: {'SQM' in df.columns}")
        
        if 'SQM' in df.columns:
            sqm_valid = len(df[df['SQM'].notna()])
            sqm_total = df['SQM'].sum()
            print(f"SQM 데이터 유효: {sqm_valid}건")
            print(f"SQM 총합: {sqm_total:.1f}")
            
            # SQM 데이터 상세 분석
            print(f"\n=== 통합시스템 SQM 상세 분석 ===")
            if sqm_valid > 0:
                sqm_stats = df['SQM'].describe()
                print(f"SQM 통계:")
                print(f"  - 평균: {sqm_stats['mean']:.2f}")
                print(f"  - 중간값: {sqm_stats['50%']:.2f}")
                print(f"  - 최대값: {sqm_stats['max']:.2f}")
                print(f"  - 최소값: {sqm_stats['min']:.2f}")
                
                # 벤더별 SQM 분포
                if 'VENDOR' in df.columns:
                    vendor_sqm = df.groupby('VENDOR')['SQM'].agg(['count', 'sum', 'mean']).round(2)
                    print(f"\n벤더별 SQM 분포:")
                    print(vendor_sqm)
            else:
                print("❌ SQM 데이터가 모두 NULL입니다!")
            
        else:
            print("❌ SQM 컬럼이 없습니다!")
            
        # Stack_Status 확인
        print(f"\n=== 통합시스템 Stack_Status 확인 ===")
        if 'Stack_Status' in df.columns:
            stack_valid = len(df[df['Stack_Status'].notna()])
            print(f"Stack_Status 컬럼 존재: True")
            print(f"Stack_Status 데이터 유효: {stack_valid}건")
            
            if stack_valid > 0:
                stack_dist = df['Stack_Status'].value_counts().dropna()
                print(f"Stack_Status 분포: {dict(stack_dist)}")
        else:
            print("❌ Stack_Status 컬럼이 없습니다!")
            
        # 원본 데이터 확인
        print("\n=== 원본 데이터 SQM 확인 ===")
        hitachi = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx')
        simense = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx')
        
        hitachi_sqm = 'SQM' in hitachi.columns
        simense_sqm = 'SQM' in simense.columns
        
        hitachi_valid = len(hitachi[hitachi['SQM'].notna()]) if hitachi_sqm else 0
        simense_valid = len(simense[simense['SQM'].notna()]) if simense_sqm else 0
        
        print(f"HITACHI SQM: {hitachi_sqm}, 유효 데이터: {hitachi_valid}건")
        print(f"SIMENSE SQM: {simense_sqm}, 유효 데이터: {simense_valid}건")
        
        if hitachi_sqm and simense_sqm:
            hitachi_total = hitachi['SQM'].sum()
            simense_total = simense['SQM'].sum()
            print(f"HITACHI SQM 총합: {hitachi_total:.1f}")
            print(f"SIMENSE SQM 총합: {simense_total:.1f}")
            print(f"원본 SQM 총합: {hitachi_total + simense_total:.1f}")
            
        # Stack_Status 확인
        print("\n=== 원본 Stack_Status 확인 ===")
        hitachi_stack = 'Stack_Status' in hitachi.columns
        simense_stack = 'Stack_Status' in simense.columns
        
        print(f"HITACHI Stack_Status: {hitachi_stack}")
        print(f"SIMENSE Stack_Status: {simense_stack}")
        
        if hitachi_stack:
            stack_dist = hitachi['Stack_Status'].value_counts().dropna()
            print(f"HITACHI Stack 분포: {dict(stack_dist)}")
            
        if simense_stack:
            stack_dist = simense['Stack_Status'].value_counts().dropna()
            print(f"SIMENSE Stack 분포: {dict(stack_dist)}")
            
        # 통합 vs 원본 비교
        print("\n=== 통합 vs 원본 데이터 비교 ===")
        if 'SQM' in df.columns and hitachi_sqm and simense_sqm:
            integrated_total = df['SQM'].sum()
            original_total = hitachi_total + simense_total
            
            print(f"통합시스템 SQM 총합: {integrated_total:.1f}")
            print(f"원본 데이터 SQM 총합: {original_total:.1f}")
            print(f"차이: {abs(integrated_total - original_total):.1f}")
            
            if abs(integrated_total - original_total) > 1.0:
                print("❌ SQM 데이터 불일치 발견!")
            else:
                print("✅ SQM 데이터 일치 확인")
            
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sqm_status() 