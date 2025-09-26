#!/usr/bin/env python3
"""
HVDC 실제 데이터 파일의 정확한 컬럼 구조 확인
"""

import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def check_data_columns():
    """데이터 파일의 컬럼 구조 확인"""
    
    data_files = [
        "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx", 
        "hvdc_ontology_system/data/HVDC WAREHOUSE_INVOICE.xlsx"
    ]
    
    print("🔍 HVDC 데이터 파일 컬럼 구조 확인")
    print("="*60)
    
    for file_path in data_files:
        if Path(file_path).exists():
            try:
                print(f"\n📁 파일: {Path(file_path).name}")
                df = pd.read_excel(file_path)
                print(f"   레코드 수: {len(df):,}건")
                print(f"   컬럼 수: {len(df.columns)}개")
                
                print("   📋 컬럼 목록:")
                for i, col in enumerate(df.columns, 1):
                    print(f"      {i:2d}. '{col}'")
                
                # 샘플 데이터 (첫 3행)
                print("\n   🔍 샘플 데이터 (첫 3행):")
                print(df.head(3).to_string())
                
                # 금액 관련 컬럼 찾기
                amount_cols = [col for col in df.columns if any(word in col.upper() for word in ['TOTAL', 'AMOUNT', 'AED', 'PRICE'])]
                if amount_cols:
                    print(f"\n   💰 금액 관련 컬럼: {amount_cols}")
                
                # 패키지 관련 컬럼 찾기
                package_cols = [col for col in df.columns if any(word in col.upper() for word in ['PACKAGE', 'PKG', 'NO.', 'NO'])]
                if package_cols:
                    print(f"   📦 패키지 관련 컬럼: {package_cols}")
                
                # 창고 관련 컬럼 찾기
                warehouse_cols = [col for col in df.columns if any(word in col.upper() for word in ['CATEGORY', 'WAREHOUSE', 'INDOOR', 'OUTDOOR', 'DSV', 'AAA'])]
                if warehouse_cols:
                    print(f"   🏢 창고 관련 컬럼: {warehouse_cols}")
                
                print("-" * 60)
                
            except Exception as e:
                print(f"❌ {file_path} 로드 실패: {e}")
        else:
            print(f"❌ 파일 없음: {file_path}")

if __name__ == "__main__":
    check_data_columns() 