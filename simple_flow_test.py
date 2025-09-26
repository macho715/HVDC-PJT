#!/usr/bin/env python3
"""
🔧 간단한 Flow Code 테스트
수정된 정규식으로 창고 컬럼 인식 및 Flow Code 계산 확인
"""

import pandas as pd
from calc_flow_code_v2 import get_warehouse_columns, add_case_level_flow_code, get_unified_case_column

def simple_flow_test():
    """간단한 Flow Code 테스트"""
    
    print("🔧 간단한 Flow Code 테스트")
    print("=" * 50)
    
    # 1. HITACHI 파일 로드
    print("📄 HITACHI 파일 로드 중...")
    df_hitachi = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx')
    print(f"   📊 행 수: {len(df_hitachi)}")
    
    # 2. 창고 컬럼 인식 테스트
    print("\n🔍 창고 컬럼 인식 테스트:")
    wh_cols = get_warehouse_columns(df_hitachi)
    print(f"   ✅ 인식된 창고 컬럼 ({len(wh_cols)}개): {wh_cols}")
    
    # 3. Case 컬럼 확인
    print("\n🔍 Case 컬럼 확인:")
    case_col = get_unified_case_column(df_hitachi)
    print(f"   ✅ Case 컬럼: '{case_col}'")
    
    # 4. 샘플 데이터로 Flow Code 계산
    print("\n🔧 샘플 데이터 Flow Code 계산:")
    sample_df = df_hitachi.head(100).copy()  # 처음 100행만
    
    try:
        result_df = add_case_level_flow_code(sample_df)
        flow_counts = result_df['Flow_Code'].value_counts().sort_index()
        print(f"   ✅ Flow Code 분포: {dict(flow_counts)}")
        
        # WH 컬럼별 데이터 확인
        print(f"\n📊 창고 컬럼별 비어있지 않은 행 수:")
        for col in wh_cols:
            non_null_count = result_df[col].notna().sum()
            print(f"   {col}: {non_null_count}행")
            
    except Exception as e:
        print(f"   ❌ Flow Code 계산 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_flow_test() 