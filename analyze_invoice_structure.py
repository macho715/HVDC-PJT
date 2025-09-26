#!/usr/bin/env python3
"""
HVDC WAREHOUSE_INVOICE 파일 구조 상세 분석
PKG 컬럼과 벤더 정보 (HVDC CODE 3) 분석
"""

import pandas as pd
import numpy as np

def analyze_invoice_structure():
    """INVOICE 파일 구조 분석"""
    
    print("📊 HVDC WAREHOUSE_INVOICE 파일 구조 분석")
    print("=" * 60)
    
    try:
        df_invoice = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx')
        
        print(f"✅ INVOICE 데이터 로드: {len(df_invoice)}건")
        print(f"   컬럼 수: {len(df_invoice.columns)}개")
        print()
        
        # 전체 컬럼 목록
        print("=== 전체 컬럼 목록 ===")
        for i, col in enumerate(df_invoice.columns, 1):
            print(f"{i:2d}. {col}")
        print()
        
        # PKG 컬럼 분석 (소문자 'pkg' 확인)
        pkg_col = None
        if 'PKG' in df_invoice.columns:
            pkg_col = 'PKG'
        elif 'pkg' in df_invoice.columns:
            pkg_col = 'pkg'
        
        if pkg_col:
            print(f"=== {pkg_col} 컬럼 분석 ===")
            pkg_total = df_invoice[pkg_col].sum()
            pkg_stats = df_invoice[pkg_col].describe()
            
            print(f"{pkg_col} 총합: {pkg_total:,}개")
            print(f"{pkg_col} 평균: {pkg_stats['mean']:.1f}개")
            print(f"{pkg_col} 중간값: {pkg_stats['50%']:.0f}개")
            print(f"{pkg_col} 범위: {pkg_stats['min']:.0f} ~ {pkg_stats['max']:.0f}개")
            print(f"{pkg_col} NULL 값: {df_invoice[pkg_col].isnull().sum()}개")
            print()
            
            # PKG 분포
            print(f"{pkg_col} 값 분포:")
            pkg_dist = df_invoice[pkg_col].value_counts().sort_index()
            for pkg_val, count in pkg_dist.head(10).items():
                print(f"  {pkg_val}개: {count}건")
            print()
        
        # HVDC CODE 3 벤더 분석
        if 'HVDC CODE 3' in df_invoice.columns:
            print("=== HVDC CODE 3 벤더 분석 ===")
            vendor_codes = df_invoice['HVDC CODE 3'].value_counts().dropna()
            
            print("벤더 코드 분포:")
            for vendor, count in vendor_codes.items():
                print(f"  {vendor}: {count}건")
            print()
            
            # 벤더별 PKG 집계
            if pkg_col:
                print("=== 벤더별 PKG 집계 ===")
                vendor_pkg = df_invoice.groupby('HVDC CODE 3')[pkg_col].sum().sort_values(ascending=False)
                
                for vendor, pkg_count in vendor_pkg.items():
                    pct = pkg_count / vendor_pkg.sum() * 100
                    print(f"  {vendor}: {pkg_count:,}개 ({pct:.1f}%)")
                
                total_pkg = vendor_pkg.sum()
                print(f"  총합: {total_pkg:,}개")
                print()
                
                # HITACHI/SIMENSE 비교
                print("=== 실제 데이터와 비교 ===")
                hitachi_pkg = vendor_pkg.get('HE', 0)
                simense_pkg = vendor_pkg.get('SIM', 0)
                other_vendors = []
                other_pkg_total = 0
                
                for vendor, pkg_count in vendor_pkg.items():
                    if vendor not in ['HE', 'SIM']:
                        other_vendors.append(f"{vendor}({pkg_count})")
                        other_pkg_total += pkg_count
                
                print(f"INVOICE HE (HITACHI): {hitachi_pkg:,}개")
                print(f"실제 HITACHI 데이터: 5,346개")
                print(f"차이: {hitachi_pkg - 5346:+,}개")
                print()
                
                print(f"INVOICE SIM (SIMENSE): {simense_pkg:,}개")
                print(f"실제 SIMENSE 데이터: 2,227개") 
                print(f"차이: {simense_pkg - 2227:+,}개")
                print()
                
                print(f"기타 벤더 총 {len(other_vendors)}개: {other_pkg_total:,}개")
                print(f"  {', '.join(other_vendors)}")
                print()
                
                print(f"INVOICE 전체: {total_pkg:,}개")
                print(f"실제 데이터 전체: {7573:,}개 (HITACHI 5,346 + SIMENSE 2,227)")
                print(f"전체 차이: {total_pkg - 7573:+,}개")
        
        # HVDC CODE 컬럼들 비교
        print("\n=== HVDC CODE 컬럼들 비교 ===")
        hvdc_cols = [col for col in df_invoice.columns if 'HVDC CODE' in col]
        
        for col in hvdc_cols:
            unique_count = df_invoice[col].nunique()
            null_count = df_invoice[col].isnull().sum()
            print(f"{col}: {unique_count}개 고유값, {null_count}개 NULL")
            
            # 샘플 값들
            sample_values = df_invoice[col].dropna().unique()[:5]
            print(f"  샘플: {list(sample_values)}")
        
        print("\n" + "="*60)
        print("🎯 INVOICE 구조 분석 완료")
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

if __name__ == "__main__":
    analyze_invoice_structure() 