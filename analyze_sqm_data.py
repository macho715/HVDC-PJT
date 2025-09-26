#!/usr/bin/env python3
"""
INVOICE 파일에서 HVDC CODE 2 = "SQM" 필터링 데이터 분석
창고별 임대료 및 면적 정보 분석
"""

import pandas as pd
import numpy as np

def analyze_sqm_data():
    """SQM 필터링 데이터 분석"""
    
    print("🏢 INVOICE SQM 데이터 분석")
    print("=" * 60)
    
    try:
        df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx')
        
        print(f"✅ INVOICE 전체 데이터: {len(df)}건")
        print()
        
        # HVDC CODE 2의 모든 값 확인
        print("=== HVDC CODE 2 전체 값 분포 ===")
        code2_values = df['HVDC CODE 2'].value_counts().dropna()
        for value, count in code2_values.items():
            print(f'  "{value}": {count}건')
        print()
        
        # SQM으로 필터링
        sqm_data = df[df['HVDC CODE 2'] == 'SQM'].copy()
        print(f"=== HVDC CODE 2 = 'SQM' 필터링 결과: {len(sqm_data)}건 ===")
        
        if len(sqm_data) > 0:
            # 관련 컬럼들 확인
            relevant_cols = ['S No.', 'Operation Month', 'HVDC CODE', 'HVDC CODE 1', 
                           'HVDC CODE 2', 'HVDC CODE 3', 'pkg', 'Sqm', 'Amount', 'TOTAL']
            available_cols = [col for col in relevant_cols if col in sqm_data.columns]
            
            print("SQM 관련 데이터 샘플:")
            sample_data = sqm_data[available_cols].head(10)
            for idx, (_, row) in enumerate(sample_data.iterrows(), 1):
                print(f"\n  📋 케이스 {idx}:")
                for col in available_cols:
                    if pd.notna(row[col]):
                        print(f"    {col}: {row[col]}")
            
            print(f"\n=== SQM 데이터 통계 분석 ===")
            
            # 창고별 분석 (HVDC CODE 1)
            if 'HVDC CODE 1' in sqm_data.columns:
                print("\n창고별 분포 (HVDC CODE 1):")
                warehouse_dist = sqm_data['HVDC CODE 1'].value_counts().dropna()
                for warehouse, count in warehouse_dist.items():
                    print(f"  {warehouse}: {count}건")
            
            # 벤더별 분석 (HVDC CODE 3)
            if 'HVDC CODE 3' in sqm_data.columns:
                print("\n벤더별 분포 (HVDC CODE 3):")
                vendor_dist = sqm_data['HVDC CODE 3'].value_counts().dropna()
                for vendor, count in vendor_dist.items():
                    print(f"  {vendor}: {count}건")
            
            # Sqm 컬럼 분석
            if 'Sqm' in sqm_data.columns:
                sqm_stats = sqm_data['Sqm'].describe()
                print(f"\nSqm 면적 통계:")
                print(f"  총 면적: {sqm_data['Sqm'].sum():,.0f} sqm")
                print(f"  평균: {sqm_stats['mean']:.1f} sqm")
                print(f"  중간값: {sqm_stats['50%']:.0f} sqm")
                print(f"  범위: {sqm_stats['min']:.0f} ~ {sqm_stats['max']:.0f} sqm")
                print(f"  NULL: {sqm_data['Sqm'].isnull().sum()}개")
            
            # pkg 분석
            if 'pkg' in sqm_data.columns:
                pkg_stats = sqm_data['pkg'].describe()
                print(f"\npkg 패키지 통계:")
                print(f"  총 패키지: {sqm_data['pkg'].sum():,.0f}개")
                print(f"  평균: {pkg_stats['mean']:.1f}개")
                print(f"  범위: {pkg_stats['min']:.0f} ~ {pkg_stats['max']:.0f}개")
            
            # TOTAL 금액 분석
            if 'TOTAL' in sqm_data.columns:
                total_stats = sqm_data['TOTAL'].describe()
                print(f"\nTOTAL 금액 통계:")
                print(f"  총 금액: ${sqm_data['TOTAL'].sum():,.0f}")
                print(f"  평균: ${total_stats['mean']:,.0f}")
                print(f"  중간값: ${total_stats['50%']:,.0f}")
                print(f"  범위: ${total_stats['min']:,.0f} ~ ${total_stats['max']:,.0f}")
            
            # 창고별 상세 분석
            if 'HVDC CODE 1' in sqm_data.columns and 'Sqm' in sqm_data.columns:
                print(f"\n=== 창고별 SQM 상세 분석 ===")
                warehouse_analysis = sqm_data.groupby('HVDC CODE 1').agg({
                    'Sqm': ['sum', 'mean', 'count'],
                    'pkg': 'sum',
                    'TOTAL': 'sum'
                }).round(1)
                
                for warehouse in warehouse_analysis.index:
                    if pd.notna(warehouse):
                        row = warehouse_analysis.loc[warehouse]
                        print(f"\n📍 {warehouse}:")
                        print(f"  총 면적: {row[('Sqm', 'sum')]:,.0f} sqm")
                        print(f"  평균 면적: {row[('Sqm', 'mean')]:.1f} sqm")
                        print(f"  건수: {row[('Sqm', 'count')]:.0f}건")
                        if ('pkg', 'sum') in row.index:
                            print(f"  총 패키지: {row[('pkg', 'sum')]:,.0f}개")
                        if ('TOTAL', 'sum') in row.index:
                            print(f"  총 금액: ${row[('TOTAL', 'sum')]:,.0f}")
        
        else:
            print("❌ HVDC CODE 2 = 'SQM'인 데이터가 없습니다.")
            print("\n다른 HVDC CODE 2 값들을 확인해보세요:")
            for value in code2_values.index[:10]:
                print(f"  - '{value}'")
        
        print("\n" + "="*60)
        print("🎯 SQM 데이터 분석 완료")
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

if __name__ == "__main__":
    analyze_sqm_data() 