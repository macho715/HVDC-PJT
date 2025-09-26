#!/usr/bin/env python3
"""
Excel 창고별 월별 입고재고 데이터 확인
"""

import pandas as pd

def check_excel_data():
    file_path = 'reports/MACHO_v2.8.4_실제데이터_종합물류리포트_20250702_071422.xlsx'
    
    print("📊 **창고별월별입고재고 실제 데이터 확인**")
    print("=" * 60)
    
    try:
        df = pd.read_excel(file_path, sheet_name='창고별월별입고재고')
        
        print(f"📈 **데이터 요약**")
        print(f"   총 행수: {len(df):,}행")
        print(f"   총 컬럼수: {len(df.columns)}개")
        print(f"   창고수: {df['warehouse'].nunique()}개")
        print(f"   월수: {df['month'].nunique()}개월")
        
        print(f"\n🏢 **창고별 현황 (25개월 누적)**")
        # Set display options to show all rows
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        
        warehouse_summary = df.groupby('warehouse').agg({
            'in_qty': 'sum',
            'out_qty': 'sum',
            'stock_qty': 'sum',
            'efficiency_score': 'mean'
        }).round(1)
        
        for warehouse in warehouse_summary.index:
            data = warehouse_summary.loc[warehouse]
            print(f"   {warehouse}:")
            print(f"      입고: {data['in_qty']:,}건, 출고: {data['out_qty']:,}건")
            print(f"      재고: {data['stock_qty']:,}건, 효율성: {data['efficiency_score']:.1f}점")
        
        print(f"\n📅 **피크월 데이터 (2024-06)**")
        peak_data = df[df['month'] == '2024-06'][['warehouse', 'in_qty', 'out_qty', 'stock_qty', 'seasonal_factor']]
        for _, row in peak_data.iterrows():
            print(f"   {row['warehouse']}: 입고 {row['in_qty']}건, 출고 {row['out_qty']}건, 재고 {row['stock_qty']}건 (계절요인: {row['seasonal_factor']})")
        
        print(f"\n🔄 **창고 타입별 특성**")
        type_summary = df.groupby('type').agg({
            'stock_ratio': 'mean',
            'efficiency_score': 'mean',
            'capacity_utilization': 'mean'
        }).round(1)
        
        for wh_type in type_summary.index:
            data = type_summary.loc[wh_type]
            print(f"   {wh_type}: 재고율 {data['stock_ratio']}%, 효율성 {data['efficiency_score']:.1f}점, 가동률 {data['capacity_utilization']}%")
        
        print(f"\n📊 **월별 전체 처리량 (상위 5개월)**")
        monthly_total = df.groupby('month').agg({
            'in_qty': 'sum',
            'out_qty': 'sum',
            'stock_qty': 'sum'
        }).sort_values('in_qty', ascending=False).head()
        
        for month in monthly_total.index:
            data = monthly_total.loc[month]
            print(f"   {month}: 입고 {data['in_qty']:,}건, 출고 {data['out_qty']:,}건, 재고 {data['stock_qty']:,}건")
        
    except FileNotFoundError:
        print("❌ Excel 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_excel_data() 