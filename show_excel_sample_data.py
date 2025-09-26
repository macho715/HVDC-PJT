#!/usr/bin/env python3
"""
Excel 파일 샘플 데이터 표시
"""

import pandas as pd
import os

def show_excel_samples():
    """Excel 파일의 샘플 데이터 표시"""
    
    # Excel 파일 찾기
    excel_files = [f for f in os.listdir('.') if f.startswith('MACHO_WH_HANDLING') and f.endswith('.xlsx')]
    if not excel_files:
        print("❌ Excel 파일을 찾을 수 없습니다.")
        return
    
    excel_file = excel_files[0]
    print(f"📊 Excel 파일 샘플 데이터: {excel_file}")
    print("=" * 80)
    
    try:
        # 1. 전체 트랜잭션 데이터 샘플
        print("\n🔸 1. 전체_트랜잭션데이터 (샘플 5행)")
        df_main = pd.read_excel(excel_file, sheet_name='전체_트랜잭션데이터')
        sample_cols = ['TRANSACTION_ID', 'VENDOR', 'WH_HANDLING', 'FLOW_CODE', 'FLOW_DESCRIPTION']
        print(df_main[sample_cols].head().to_string(index=False))
        
        # 2. Flow Code 요약
        print("\n🔸 2. Flow_Code_요약")
        df_flow = pd.read_excel(excel_file, sheet_name='Flow_Code_요약')
        print(df_flow.to_string())
        
        # 3. WH HANDLING 분석
        print("\n🔸 3. WH_HANDLING_분석")
        df_wh = pd.read_excel(excel_file, sheet_name='WH_HANDLING_분석')
        print(df_wh.to_string(index=False))
        
        # 4. 창고별 처리현황
        print("\n🔸 4. 창고별_처리현황")
        df_warehouse = pd.read_excel(excel_file, sheet_name='창고별_처리현황')
        print(df_warehouse.to_string())
        
        # 5. 검증 결과 (일부)
        print("\n🔸 5. 검증_결과 (상위 6행)")
        df_validation = pd.read_excel(excel_file, sheet_name='검증_결과')
        display_cols = ['VENDOR', 'FLOW_CODE', 'FLOW_DESCRIPTION', '실제_건수', '예상_건수', '차이']
        print(df_validation[display_cols].head(6).to_string(index=False))
        
        # 6. 전체 데이터 통계
        print(f"\n🔸 6. 전체 데이터 통계")
        print(f"   📊 총 트랜잭션: {len(df_main):,}건")
        print(f"   🏭 HITACHI: {len(df_main[df_main['VENDOR'] == 'HITACHI']):,}건")
        print(f"   🏭 SIMENSE: {len(df_main[df_main['VENDOR'] == 'SIMENSE']):,}건")
        
        flow_counts = df_main['FLOW_CODE'].value_counts().sort_index()
        print(f"\n   🚚 Flow Code 분포:")
        for code, count in flow_counts.items():
            percentage = count / len(df_main) * 100
            print(f"     Code {code}: {count:,}건 ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"❌ 데이터 읽기 실패: {e}")

if __name__ == "__main__":
    show_excel_samples() 