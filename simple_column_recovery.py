#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 Status_Location_Date 컬럼 복구 스크립트
"""

import pandas as pd
from datetime import datetime

def simple_recovery():
    """간단한 복구 방법"""
    
    print("🔧 Status_Location_Date 간단 복구 시작")
    print("=" * 50)
    
    # 1. 사용된 데이터 로드
    used_data_path = r'MACHO_통합관리_20250702_205301\01_원본파일\MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    df_used = pd.read_excel(used_data_path)
    
    print(f"📊 사용된 데이터: {df_used.shape[0]}행, {df_used.shape[1]}컬럼")
    print(f"📋 Status_Location_Date 있음: {'Status_Location_Date' in df_used.columns}")
    
    # 2. 원본 HITACHI 데이터 로드
    hitachi_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_HITACHI(HE).xlsx'
    df_hitachi = pd.read_excel(hitachi_path)
    
    print(f"📊 HITACHI 원본: {df_hitachi.shape[0]}행, {df_hitachi.shape[1]}컬럼")
    print(f"📋 Status_Location_Date 있음: {'Status_Location_Date' in df_hitachi.columns}")
    
    # 3. 매칭 가능한 컬럼 확인
    common_cols = []
    for col in ['no.', 'Shipment Invoice No.', 'HVDC CODE']:
        if col in df_used.columns and col in df_hitachi.columns:
            common_cols.append(col)
    
    print(f"📋 공통 컬럼: {common_cols}")
    
    if common_cols and 'Status_Location_Date' in df_hitachi.columns:
        # 4. Status_Location_Date 추출
        date_mapping = df_hitachi[common_cols + ['Status_Location_Date']].copy()
        date_mapping = date_mapping.drop_duplicates(subset=common_cols)
        
        print(f"📊 날짜 매핑 테이블: {date_mapping.shape[0]}행")
        
        # 5. 매칭 수행
        df_result = df_used.merge(date_mapping, on=common_cols, how='left')
        
        print(f"📊 결과 데이터: {df_result.shape[0]}행, {df_result.shape[1]}컬럼")
        
        # 6. 복구 성공 확인
        if 'Status_Location_Date' in df_result.columns:
            matched_count = df_result['Status_Location_Date'].notna().sum()
            print(f"✅ Status_Location_Date 복구 성공: {matched_count}개")
            
            # 7. 파일 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'HVDC_Status_Location_Date_복구_{timestamp}.xlsx'
            
            df_result.to_excel(output_file, index=False)
            print(f"📊 파일 저장: {output_file}")
            
            # 8. 샘플 데이터 확인
            print("\n📋 Status_Location_Date 샘플:")
            sample_data = df_result[['Status_Location', 'Status_Location_Date']].head(10)
            for idx, row in sample_data.iterrows():
                print(f"  {row['Status_Location']} -> {row['Status_Location_Date']}")
            
            return df_result, output_file
    
    return None, None

if __name__ == "__main__":
    result_df, output_file = simple_recovery()
    
    if result_df is not None:
        print("\n✅ 복구 완료!")
        print(f"📊 최종 결과: {result_df.shape[0]}행, {result_df.shape[1]}컬럼")
        print(f"📁 출력 파일: {output_file}")
    else:
        print("\n❌ 복구 실패") 