#!/usr/bin/env python3
"""
INVOICE 파일에서 월별 창고별 SQM 사용량 분석
Operation Month별로 각 창고(HVDC CODE 1)의 SQM 사용량 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analyze_monthly_sqm():
    """월별 창고별 SQM 사용량 분석"""
    
    print("📅 월별 창고 SQM 사용량 분석")
    print("=" * 70)
    
    try:
        df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx')
        
        # SQM으로 필터링
        sqm_data = df[df['HVDC CODE 2'] == 'SQM'].copy()
        print(f"✅ SQM 데이터: {len(sqm_data)}건")
        
        # Operation Month를 datetime으로 변환
        sqm_data['Operation Month'] = pd.to_datetime(sqm_data['Operation Month'])
        sqm_data['Year_Month'] = sqm_data['Operation Month'].dt.strftime('%Y-%m')
        
        print(f"\n=== 월별 창고별 SQM 사용량 ===")
        
        # 월별 창고별 SQM 사용량 집계
        monthly_sqm = sqm_data.groupby(['Year_Month', 'HVDC CODE 1'])['Sqm'].sum().reset_index()
        monthly_sqm_pivot = monthly_sqm.pivot(index='Year_Month', columns='HVDC CODE 1', values='Sqm')
        monthly_sqm_pivot = monthly_sqm_pivot.fillna(0)
        
        # 월별로 출력
        for month in sorted(monthly_sqm_pivot.index):
            print(f"\n📅 {month}:")
            month_data = monthly_sqm_pivot.loc[month]
            total_sqm = 0
            
            for warehouse in month_data.index:
                if month_data[warehouse] > 0:
                    sqm_value = month_data[warehouse]
                    total_sqm += sqm_value
                    
                    # 2024-03 DSV Outdoor 체크
                    if month == '2024-03' and 'Outdoor' in str(warehouse):
                        status = f" ✅ 기준값 {sqm_value:,.0f} SQM" if sqm_value == 2500 else f" ❓ 기준값과 다름 (기준: 2500)"
                    else:
                        status = ""
                        
                    print(f"  {warehouse}: {sqm_value:,.0f} SQM{status}")
            
            print(f"  📊 월 총계: {total_sqm:,.0f} SQM")
        
        print(f"\n=== 창고별 월평균 SQM 사용량 ===")
        warehouse_avg = monthly_sqm_pivot.mean()
        for warehouse in warehouse_avg.index:
            if warehouse_avg[warehouse] > 0:
                print(f"  {warehouse}: {warehouse_avg[warehouse]:,.0f} SQM/월")
        
        print(f"\n=== 특정 월 상세 확인 ===")
        # 2024-03 상세 확인
        march_2024 = sqm_data[sqm_data['Year_Month'] == '2024-03']
        if len(march_2024) > 0:
            print(f"\n📍 2024년 3월 상세:")
            march_detail = march_2024.groupby('HVDC CODE 1').agg({
                'Sqm': 'sum',
                'Amount': 'sum',
                'pkg': 'sum',
                'HVDC CODE': 'count'
            }).round(0)
            
            for warehouse in march_detail.index:
                if pd.notna(warehouse):
                    row = march_detail.loc[warehouse]
                    print(f"  🏢 {warehouse}:")
                    print(f"    SQM: {row['Sqm']:,.0f}")
                    print(f"    임대료: ${row['Amount']:,.0f}")
                    print(f"    패키지: {row['pkg']:,.0f}개")
                    print(f"    건수: {row['HVDC CODE']:,.0f}건")
                    
                    # 단가 계산
                    if row['Sqm'] > 0:
                        price_per_sqm = row['Amount'] / row['Sqm']
                        print(f"    단가: ${price_per_sqm:.1f}/SQM")
        
        # 전체 기간 통계
        print(f"\n=== 전체 기간 통계 ===")
        total_stats = sqm_data.groupby('HVDC CODE 1').agg({
            'Sqm': ['sum', 'mean', 'count'],
            'Amount': 'sum',
            'Operation Month': ['min', 'max']
        })
        
        for warehouse in total_stats.index:
            if pd.notna(warehouse):
                print(f"\n🏢 {warehouse}:")
                print(f"  총 SQM: {total_stats.loc[warehouse, ('Sqm', 'sum')]:,.0f}")
                print(f"  평균 SQM/월: {total_stats.loc[warehouse, ('Sqm', 'mean')]:,.0f}")
                print(f"  총 건수: {total_stats.loc[warehouse, ('Sqm', 'count')]:,.0f}")
                print(f"  총 임대료: ${total_stats.loc[warehouse, ('Amount', 'sum')]:,.0f}")
                print(f"  기간: {total_stats.loc[warehouse, ('Operation Month', 'min')].strftime('%Y-%m')} ~ {total_stats.loc[warehouse, ('Operation Month', 'max')].strftime('%Y-%m')}")
        
        print("\n" + "="*70)
        print("🎯 월별 SQM 사용량 분석 완료")
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_monthly_sqm() 