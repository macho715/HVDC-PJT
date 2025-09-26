#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
복구 결과 확인 스크립트
"""

import pandas as pd

def verify_recovery():
    """복구 결과 확인"""
    
    print("✅ 복구 결과 확인 시작")
    print("=" * 40)
    
    # 복구된 파일 로드
    recovery_file = 'HVDC_Status_Location_Date_복구_20250704_120507.xlsx'
    df = pd.read_excel(recovery_file)
    
    print(f"📊 복구된 데이터: {df.shape[0]}행, {df.shape[1]}컬럼")
    print(f"📋 Status_Location_Date 컬럼 있음: {'Status_Location_Date' in df.columns}")
    
    if 'Status_Location_Date' in df.columns:
        valid_count = df['Status_Location_Date'].notna().sum()
        total_count = len(df)
        print(f"✅ Status_Location_Date 유효 데이터: {valid_count}개 ({valid_count/total_count*100:.1f}%)")
        
        # 샘플 데이터 확인
        print("\n📋 Status_Location_Date 샘플:")
        sample_data = df[['Status_Location', 'Status_Location_Date']].dropna().head(10)
        for idx, row in sample_data.iterrows():
            print(f"  {row['Status_Location']} -> {row['Status_Location_Date']}")
    else:
        print("❌ Status_Location_Date 컬럼이 없습니다.")

if __name__ == "__main__":
    verify_recovery() 