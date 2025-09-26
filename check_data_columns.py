#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터 컬럼명 확인 스크립트
"""

import pandas as pd

def check_data_columns():
    """데이터 컬럼명 확인"""
    try:
        # 데이터 로드
        df = pd.read_excel('output/창고_현장_월별_보고서_올바른계산_20250704_014217.xlsx')
        
        print("📊 데이터 컬럼명 확인")
        print("=" * 50)
        print(f"총 행 수: {len(df)}")
        print(f"총 컬럼 수: {len(df.columns)}")
        print("\n📋 컬럼명 목록:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print("\n📄 처음 5행 데이터:")
        print(df.head())
        
        print("\n📈 데이터 타입:")
        print(df.dtypes)
        
        return df.columns.tolist()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    check_data_columns() 