#!/usr/bin/env python3
"""
HVDC CODE 1~4 매칭 기반 생성된 트랜잭션 데이터 검증
"""

import pandas as pd
import numpy as np
from datetime import datetime

def validate_transaction_data():
    """생성된 트랜잭션 데이터 검증"""
    
    print("🔍 HVDC CODE 1~4 매칭 기반 트랜잭션 데이터 검증")
    print("=" * 60)
    
    # 생성된 파일 로드
    filename = 'HVDC_실제데이터기반_월별트랜잭션_20250702_100737.xlsx'
    
    try:
        df = pd.read_excel(filename, sheet_name='전체_트랜잭션')
        print(f"✅ 파일 로드 성공: {filename}")
        print(f"   데이터 크기: {len(df):,}행 × {len(df.columns)}열")
        print()
        
        # 기본 통계
        print("=== 기본 통계 ===")
        print(f"총 트랜잭션: {len(df):,}건")
        print(f"고유 케이스: {df['Case_No'].nunique():,}개")
        print(f"기간: {df['Date'].min()} ~ {df['Date'].max()}")
        print(f"총 처리량: {df['Qty'].sum():,}개")
        print(f"총 금액: ${df['Amount'].sum():,.0f}")
        print(f"총 핸들링비: ${df['Handling_Fee'].sum():,.0f}")
        print()
        
        # 새 컬럼 확인
        print("=== 새로 추가된 컬럼 확인 ===")
        new_columns = ['Invoice_Matched', 'Base_Amount', 'Seasonal_Factor']
        for col in new_columns:
            if col in df.columns:
                if col == 'Invoice_Matched':
                    matched_count = df[col].sum()
                    print(f"✅ {col}: {matched_count:,}건 ({matched_count/len(df)*100:.1f}%)")
                elif col == 'Base_Amount':
                    print(f"✅ {col}: 평균 ${df[col].mean():,.0f}")
                elif col == 'Seasonal_Factor':
                    print(f"✅ {col}: {df[col].min():.2f} ~ {df[col].max():.2f}")
            else:
                print(f"❌ {col}: 컬럼 없음")
        print()
        
        # INVOICE 기반 금액 분포
        print("=== INVOICE 기반 금액 분포 ===")
        amount_stats = df['Amount'].describe()
        print(f"최소값: ${amount_stats['min']:,.0f}")
        print(f"Q25: ${amount_stats['25%']:,.0f}")
        print(f"중간값: ${amount_stats['50%']:,.0f}")
        print(f"평균값: ${amount_stats['mean']::.0f}")
        print(f"Q75: ${amount_stats['75%']:,.0f}")
        print(f"최대값: ${amount_stats['max']:,.0f}")
        print(f"표준편차: ${amount_stats['std']:,.0f}")
        print()
        
        # 트랜잭션 타입별 분포
        print("=== 트랜잭션 타입별 분포 ===")
        tx_distribution = df['TxType_Refined'].value_counts()
        for tx_type, count in tx_distribution.items():
            pct = count / len(df) * 100
            avg_amount = df[df['TxType_Refined'] == tx_type]['Amount'].mean()
            print(f"{tx_type}: {count:,}건 ({pct:.1f}%) - 평균 ${avg_amount:,.0f}")
        print()
        
        # 창고별 분포
        print("=== 창고별 분포 ===")
        warehouse_distribution = df['Location'].value_counts()
        for warehouse, count in warehouse_distribution.items():
            pct = count / len(df) * 100
            print(f"{warehouse}: {count:,}건 ({pct:.1f}%)")
        print()
        
        # 벤더별 분포
        print("=== 벤더별 분포 ===")
        vendor_distribution = df['Vendor'].value_counts()
        for vendor, count in vendor_distribution.items():
            pct = count / len(df) * 100
            avg_amount = df[df['Vendor'] == vendor]['Amount'].mean()
            print(f"{vendor}: {count:,}건 ({pct:.1f}%) - 평균 ${avg_amount:,.0f}")
        print()
        
        # 월별 요약
        print("=== 월별 트랜잭션 요약 (TOP 10) ===")
        monthly_summary = df.groupby('Month').agg({
            'Case_No': 'nunique',
            'Qty': 'sum',
            'Amount': 'sum'
        }).round(0)
        monthly_summary.columns = ['케이스수', '총수량', '총금액']
        monthly_summary = monthly_summary.sort_values('총금액', ascending=False)
        
        for month, row in monthly_summary.head(10).iterrows():
            print(f"{month}: {row['케이스수']:.0f}개 케이스, {row['총수량']:.0f}개, ${row['총금액']:,.0f}")
        print()
        
        # INVOICE 매칭률 상세 분석
        if 'Invoice_Matched' in df.columns:
            print("=== INVOICE 매칭 상세 분석 ===")
            matched_df = df[df['Invoice_Matched'] == True]
            unmatched_df = df[df['Invoice_Matched'] == False]
            
            print(f"매칭된 트랜잭션: {len(matched_df):,}건")
            print(f"  - 평균 금액: ${matched_df['Amount'].mean():,.0f}")
            print(f"  - 총 금액: ${matched_df['Amount'].sum():,.0f}")
            
            print(f"미매칭 트랜잭션: {len(unmatched_df):,}건")
            print(f"  - 평균 금액: ${unmatched_df['Amount'].mean():,.0f}")
            print(f"  - 총 금액: ${unmatched_df['Amount'].sum():,.0f}")
            print()
        
        # 데이터 품질 검증
        print("=== 데이터 품질 검증 ===")
        quality_checks = []
        
        # 1. 필수 컬럼 존재
        required_cols = ['Case_No', 'Date', 'Location', 'TxType_Refined', 'Qty', 'Amount']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if not missing_cols:
            quality_checks.append("✅ 필수 컬럼 모두 존재")
        else:
            quality_checks.append(f"❌ 누락 컬럼: {missing_cols}")
        
        # 2. NULL 값 확인
        null_counts = df.isnull().sum()
        critical_nulls = null_counts[null_counts > 0]
        if len(critical_nulls) == 0:
            quality_checks.append("✅ NULL 값 없음")
        else:
            quality_checks.append(f"⚠️ NULL 값 존재: {dict(critical_nulls)}")
        
        # 3. 금액 범위 검증
        negative_amounts = (df['Amount'] < 0).sum()
        if negative_amounts == 0:
            quality_checks.append("✅ 음수 금액 없음")
        else:
            quality_checks.append(f"❌ 음수 금액: {negative_amounts}건")
        
        # 4. 케이스 ID 형식 검증
        case_pattern_hit = df['Case_No'].str.contains('HIT_', na=False).sum()
        case_pattern_sim = df['Case_No'].str.contains('SIM_', na=False).sum()
        total_cases = case_pattern_hit + case_pattern_sim
        if total_cases == len(df):
            quality_checks.append("✅ 케이스 ID 형식 정확")
        else:
            quality_checks.append(f"⚠️ 케이스 ID 형식 이상: {total_cases}/{len(df)}")
        
        for check in quality_checks:
            print(f"  {check}")
        
        print("\n" + "="*60)
        print("🎯 HVDC CODE 1~4 매칭 기반 트랜잭션 생성 검증 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 검증 실패: {e}")
        return False

if __name__ == "__main__":
    validate_transaction_data() 