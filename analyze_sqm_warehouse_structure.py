#!/usr/bin/env python3
"""
HVDC WAREHOUSE_INVOICE 파일에서 SQM 필터링 기반 창고 구조 분석
HVDC CODE 2 = 'SQM' 필터링 → HVDC CODE 1 = 실제 창고 이름
"""

import pandas as pd
import numpy as np

def analyze_sqm_warehouse_structure():
    """SQM 필터링 기반 창고 구조 분석"""
    
    print("🏢 SQM 필터링 기반 창고 구조 분석")
    print("=" * 60)
    
    try:
        # INVOICE 데이터 로드
        invoice_df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx')
        print(f"📊 INVOICE 전체 데이터: {len(invoice_df)}건")
        
        print(f"\n=== 1. HVDC CODE 2 전체 분포 ===")
        code2_dist = invoice_df['HVDC CODE 2'].value_counts().dropna()
        print("HVDC CODE 2 분포:")
        for code, count in code2_dist.items():
            print(f"  {code}: {count}건")
        
        print(f"\n=== 2. SQM 필터링 결과 ===")
        
        # HVDC CODE 2 = 'SQM'으로 필터링
        sqm_data = invoice_df[invoice_df['HVDC CODE 2'] == 'SQM'].copy()
        print(f"SQM 필터링 결과: {len(sqm_data)}건 ({len(sqm_data)/len(invoice_df)*100:.1f}%)")
        
        print(f"\n=== 3. SQM 필터링된 창고 목록 (HVDC CODE 1) ===")
        
        # SQM 데이터에서 창고별 집계
        warehouse_summary = sqm_data.groupby('HVDC CODE 1').agg({
            'Sqm': ['sum', 'count', 'mean'],
            'TOTAL': ['sum', 'mean'],
            'Operation Month': ['min', 'max']
        }).round(2)
        
        # 컬럼명 정리
        warehouse_summary.columns = ['Total_SQM', 'Record_Count', 'Avg_SQM_per_Record', 
                                   'Total_Cost', 'Avg_Cost_per_Record', 'Start_Date', 'End_Date']
        
        # 비용/면적 효율성 계산
        warehouse_summary['Cost_per_SQM'] = (warehouse_summary['Total_Cost'] / warehouse_summary['Total_SQM']).round(2)
        
        # 면적 기준 정렬
        warehouse_summary = warehouse_summary.sort_values('Total_SQM', ascending=False)
        
        print("🏪 **실제 창고 목록 및 상세 정보:**")
        print(warehouse_summary.to_string())
        
        print(f"\n=== 4. 창고별 운영 패턴 분석 ===")
        
        for warehouse in warehouse_summary.index:
            wh_data = sqm_data[sqm_data['HVDC CODE 1'] == warehouse]
            
            print(f"\n📍 **{warehouse}**")
            print(f"  • 총 면적: {warehouse_summary.loc[warehouse, 'Total_SQM']:,.0f} SQM")
            print(f"  • 총 비용: ${warehouse_summary.loc[warehouse, 'Total_Cost']:,.0f}")
            print(f"  • 단가: ${warehouse_summary.loc[warehouse, 'Cost_per_SQM']}/SQM")
            print(f"  • 운영기간: {warehouse_summary.loc[warehouse, 'Start_Date']:%Y-%m} ~ {warehouse_summary.loc[warehouse, 'End_Date']:%Y-%m}")
            
            # 월별 패턴 (상위 5개월만)
            monthly_pattern = wh_data.groupby(wh_data['Operation Month'].dt.strftime('%Y-%m'))['Sqm'].sum().sort_values(ascending=False).head(5)
            print(f"  • 월별 최대 사용량 TOP 5:")
            for month, sqm in monthly_pattern.items():
                print(f"    - {month}: {sqm:,.0f} SQM")
        
        print(f"\n=== 5. 창고 규모 및 비용 순위 ===")
        
        # 면적 순위
        print("📊 **면적 기준 순위:**")
        for i, (warehouse, data) in enumerate(warehouse_summary.iterrows(), 1):
            percentage = data['Total_SQM'] / warehouse_summary['Total_SQM'].sum() * 100
            print(f"  {i}위. {warehouse}: {data['Total_SQM']:,.0f} SQM ({percentage:.1f}%)")
        
        # 비용 효율성 순위 (낮은 단가가 좋음)
        print(f"\n💰 **비용 효율성 순위 (단가 기준):**")
        cost_ranking = warehouse_summary.sort_values('Cost_per_SQM')
        for i, (warehouse, data) in enumerate(cost_ranking.iterrows(), 1):
            print(f"  {i}위. {warehouse}: ${data['Cost_per_SQM']}/SQM")
        
        print(f"\n=== 6. 전체 시장 점유율 ===")
        
        total_sqm = warehouse_summary['Total_SQM'].sum()
        total_cost = warehouse_summary['Total_Cost'].sum()
        
        print(f"전체 창고 시장:")
        print(f"  • 총 면적: {total_sqm:,.0f} SQM")
        print(f"  • 총 비용: ${total_cost:,.0f}")
        print(f"  • 평균 단가: ${total_cost/total_sqm:.2f}/SQM")
        print(f"  • 창고 수: {len(warehouse_summary)}개")
        
        # HVDC 창고의 시장 점유율
        if 'HVDC' in warehouse_summary.index:
            hvdc_sqm = warehouse_summary.loc['HVDC', 'Total_SQM']
            hvdc_cost = warehouse_summary.loc['HVDC', 'Total_Cost']
            hvdc_share_sqm = hvdc_sqm / total_sqm * 100
            hvdc_share_cost = hvdc_cost / total_cost * 100
            
            print(f"\n🎯 **HVDC 창고 시장 점유율:**")
            print(f"  • 면적 점유율: {hvdc_share_sqm:.1f}%")
            print(f"  • 비용 점유율: {hvdc_share_cost:.1f}%")
            print(f"  • 평균 대비 단가: {(warehouse_summary.loc['HVDC', 'Cost_per_SQM'] / (total_cost/total_sqm) - 1) * 100:+.1f}%")
        
        print(f"\n=== 7. 데이터 품질 검증 ===")
        
        # SQM과 TOTAL이 모두 있는 레코드만 확인
        valid_records = sqm_data[(sqm_data['Sqm'].notna()) & (sqm_data['TOTAL'].notna())]
        print(f"유효한 SQM+비용 레코드: {len(valid_records)}/{len(sqm_data)}건 ({len(valid_records)/len(sqm_data)*100:.1f}%)")
        
        # 이상치 확인
        if len(valid_records) > 0:
            cost_per_sqm_series = valid_records['TOTAL'] / valid_records['Sqm']
            q1 = cost_per_sqm_series.quantile(0.25)
            q3 = cost_per_sqm_series.quantile(0.75)
            iqr = q3 - q1
            outlier_threshold = q3 + 1.5 * iqr
            
            outliers = valid_records[cost_per_sqm_series > outlier_threshold]
            
            print(f"비용/면적 통계:")
            print(f"  • 평균: ${cost_per_sqm_series.mean():.2f}/SQM")
            print(f"  • 중앙값: ${cost_per_sqm_series.median():.2f}/SQM") 
            print(f"  • 표준편차: ${cost_per_sqm_series.std():.2f}")
            print(f"  • 이상치: {len(outliers)}건 (>${outlier_threshold:.2f}/SQM)")
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_sqm_warehouse_structure() 