#!/usr/bin/env python3
"""
실제 Excel 결과에서 창고별 입고량 확인
"""

import pandas as pd

def check_warehouse_results():
    file_path = 'reports/MACHO_v2.8.4_실제데이터_종합물류리포트_20250702_071422.xlsx'
    
    print('🏢 **실제 Excel 결과 - 창고별월별입고재고**')
    print('='*80)
    
    try:
        # 창고별월별입고재고 시트 로드
        df = pd.read_excel(file_path, sheet_name='창고별월별입고재고')
        
        print(f'총 데이터: {len(df):,}행')
        print(f'창고 수: {df["warehouse"].nunique()}개')
        print(f'월 수: {df["month"].nunique()}개월')
        
        # 창고별 입고량 합계
        print('\n📊 **창고별 25개월 입고량 합계**')
        warehouse_summary = df.groupby('warehouse')['in_qty'].sum().sort_values(ascending=False)
        for wh, qty in warehouse_summary.items():
            print(f'   {wh}: {qty:,}건')
        
        # 월별 전체 입고량 (피크월 확인)
        print('\n📈 **월별 전체 입고량 (상위 10개월)**')
        monthly_summary = df.groupby('month')['in_qty'].sum().sort_values(ascending=False).head(10)
        for month, qty in monthly_summary.items():
            print(f'   {month}: {qty:,}건')
        
        # 피크월 실제 계절 요인 확인
        print('\n🌦️ **피크월 실제 계절 요인 확인**')
        peak_months = ['2024-06', '2024-08', '2025-03']
        peak_data = df[df['month'].isin(peak_months)]
        
        for month in peak_months:
            month_data = peak_data[peak_data['month'] == month]
            if not month_data.empty:
                print(f'\n   {month}월:')
                for _, row in month_data.iterrows():
                    print(f'     {row["warehouse"]}: 입고 {row["in_qty"]:,}건, 계절요인 {row["seasonal_factor"]}')
        
        # 최대/최소 입고량 확인
        print('\n🎯 **극값 분석**')
        max_row = df.loc[df['in_qty'].idxmax()]
        min_row = df.loc[df['in_qty'].idxmin()]
        
        print(f'최대 입고량: {max_row["warehouse"]} - {max_row["month"]} ({max_row["in_qty"]:,}건)')
        print(f'최소 입고량: {min_row["warehouse"]} - {min_row["month"]} ({min_row["in_qty"]:,}건)')
        
        # 창고별 평균 입고량
        print('\n📊 **창고별 월평균 입고량**')
        avg_summary = df.groupby('warehouse')['in_qty'].mean().sort_values(ascending=False)
        for wh, avg in avg_summary.items():
            print(f'   {wh}: {avg:.1f}건/월')
        
    except Exception as e:
        print(f'❌ 오류 발생: {e}')

if __name__ == "__main__":
    check_warehouse_results() 