#!/usr/bin/env python3
"""
트랜잭션 데이터 컬럼 구조 확인
"""
import pandas as pd
import sys
import os

# 현재 디렉토리를 시스템 패스에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_loader import DataLoader
from core.transaction_generator import TransactionGenerator

def debug_columns():
    print("📊 트랜잭션 데이터 컬럼 구조 분석")
    print("=" * 50)
    
    # 원본 파일 확인
    loader = DataLoader()
    files = loader.load_all_files()
    
    print("📁 원본 파일 컬럼 확인:")
    for vendor, df in files.items():
        print(f"  {vendor}:")
        print(f"    총 컬럼: {len(df.columns)}개")
        case_related = [c for c in df.columns if any(k in c.upper() for k in ['CASE', 'HVDC', 'SERIAL', 'CODE'])]
        print(f"    Case 관련: {case_related}")
    
    # 트랜잭션 변환 후 확인
    generator = TransactionGenerator(loader)
    transactions = generator.process_all_transactions()
    
    print(f"\n📊 트랜잭션 데이터:")
    print(f"  총 컬럼: {len(transactions.columns)}개")
    print(f"  컬럼 목록: {list(transactions.columns)}")
    
    # Case_ID 관련 컬럼 확인
    case_cols = [c for c in transactions.columns if 'case' in c.lower() or 'id' in c.lower()]
    print(f"  Case/ID 관련: {case_cols}")
    
    if 'Case_ID' in transactions.columns:
        sample_cases = transactions['Case_ID'].unique()[:5]
        print(f"  샘플 Case_ID: {list(sample_cases)}")
    
    return transactions

if __name__ == "__main__":
    transactions = debug_columns() 