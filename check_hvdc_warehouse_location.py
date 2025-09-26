#!/usr/bin/env python3
"""
HVDC 창고 위치 및 정보 확인
INVOICE 데이터에서 HVDC 창고의 실제 정보 분석
"""

import pandas as pd
import numpy as np

def check_hvdc_warehouse_location():
    """HVDC 창고 위치 확인"""
    
    print("🏢 HVDC 창고 위치 및 정보 확인")
    print("=" * 60)
    
    try:
        # INVOICE 데이터 로드
        invoice_df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx')
        print(f"📊 INVOICE 데이터 로드: {len(invoice_df)}건")
        
        print(f"\n=== 1. 전체 창고 목록 (HVDC CODE 1) ===")
        
        # HVDC CODE 1의 모든 값 확인 (창고 이름)
        warehouse_list = invoice_df['HVDC CODE 1'].value_counts().dropna()
        print("전체 창고 목록:")
        for warehouse, count in warehouse_list.items():
            print(f"  {warehouse}: {count}건")
        
        print(f"\n=== 2. HVDC 창고 상세 정보 ===")
        
        # HVDC 창고 관련 데이터만 필터링
        hvdc_data = invoice_df[invoice_df['HVDC CODE 1'] == 'HVDC'].copy()
        
        if len(hvdc_data) > 0:
            print(f"HVDC 창고 관련 레코드: {len(hvdc_data)}건")
            
            # HVDC 창고의 모든 컬럼 정보 확인
            print(f"\nHVDC 창고 상세 정보:")
            
            # 주요 컬럼들 확인
            key_columns = ['HVDC CODE 1', 'HVDC CODE 2', 'HVDC CODE 3', 'HVDC CODE 4', 
                          'Operation Month', 'PKG', 'Sqm', 'TOTAL', 'Description']
            
            for col in key_columns:
                if col in hvdc_data.columns:
                    unique_values = hvdc_data[col].dropna().unique()
                    if len(unique_values) <= 10:  # 값이 적으면 모두 표시
                        print(f"  {col}: {list(unique_values)}")
                    else:  # 값이 많으면 요약 정보만
                        print(f"  {col}: {len(unique_values)}개 고유값 (예시: {list(unique_values[:3])}...)")
            
            print(f"\n=== 3. HVDC 창고 운영 패턴 ===")
            
            # 운영 기간 확인
            if 'Operation Month' in hvdc_data.columns:
                hvdc_data['Operation Month'] = pd.to_datetime(hvdc_data['Operation Month'])
                operation_period = hvdc_data['Operation Month'].agg(['min', 'max'])
                print(f"운영 기간: {operation_period['min'].strftime('%Y-%m')} ~ {operation_period['max'].strftime('%Y-%m')}")
                
                # 월별 운영 패턴
                monthly_ops = hvdc_data.groupby(hvdc_data['Operation Month'].dt.strftime('%Y-%m')).size()
                print(f"월별 운영 건수:")
                for month, count in monthly_ops.items():
                    print(f"  {month}: {count}건")
            
            # SQM 및 비용 정보
            if 'Sqm' in hvdc_data.columns and 'TOTAL' in hvdc_data.columns:
                sqm_total = hvdc_data['Sqm'].sum()
                cost_total = hvdc_data['TOTAL'].sum()
                avg_cost_per_sqm = cost_total / sqm_total if sqm_total > 0 else 0
                
                print(f"\n=== 4. HVDC 창고 규모 및 비용 ===")
                print(f"총 면적: {sqm_total:,.0f} SQM")
                print(f"총 비용: ${cost_total:,.0f}")
                print(f"SQM당 평균 비용: ${avg_cost_per_sqm:.2f}/SQM")
            
            print(f"\n=== 5. HVDC 창고 상세 레코드 (첫 5건) ===")
            
            # 첫 5건의 상세 정보 표시
            display_columns = ['Operation Month', 'HVDC CODE 2', 'HVDC CODE 3', 'PKG', 'Sqm', 'TOTAL']
            available_columns = [col for col in display_columns if col in hvdc_data.columns]
            
            print(hvdc_data[available_columns].head().to_string(index=False))
            
        else:
            print("❌ HVDC 창고 관련 데이터를 찾을 수 없습니다!")
        
        print(f"\n=== 6. 다른 창고들과의 비교 ===")
        
        # SQM 필터링된 데이터로 창고별 비교
        sqm_data = invoice_df[invoice_df['HVDC CODE 2'] == 'SQM'].copy()
        
        if len(sqm_data) > 0:
            # 존재하는 컬럼만 집계
            agg_dict = {
                'Sqm': 'sum',
                'TOTAL': 'sum'
            }
            if 'PKG' in sqm_data.columns:
                agg_dict['PKG'] = 'sum'
            
            warehouse_comparison = sqm_data.groupby('HVDC CODE 1').agg(agg_dict).round(0)
            
            warehouse_comparison['Cost_per_SQM'] = (warehouse_comparison['TOTAL'] / warehouse_comparison['Sqm']).round(2)
            warehouse_comparison = warehouse_comparison.sort_values('Sqm', ascending=False)
            
            print("창고별 비교 (SQM 기준):")
            print(warehouse_comparison.to_string())
            
            # HVDC 창고가 다른 창고들과 어떻게 다른지 분석
            if 'HVDC' in warehouse_comparison.index:
                hvdc_rank_by_size = warehouse_comparison.index.get_loc('HVDC') + 1
                hvdc_rank_by_cost = warehouse_comparison.sort_values('Cost_per_SQM', ascending=False).index.get_loc('HVDC') + 1
                
                print(f"\nHVDC 창고 순위:")
                print(f"  면적 기준: {hvdc_rank_by_size}위 (총 {len(warehouse_comparison)}개 창고 중)")
                print(f"  단가 기준: {hvdc_rank_by_cost}위 (높은 순)")
        
        print(f"\n=== 7. HVDC 창고 위치 추정 ===")
        
        # HVDC CODE 3에서 위치 정보 찾기
        if len(hvdc_data) > 0 and 'HVDC CODE 3' in hvdc_data.columns:
            location_codes = hvdc_data['HVDC CODE 3'].dropna().unique()
            print(f"HVDC 창고 위치 코드: {list(location_codes)}")
            
            # 다른 창고들의 위치 코드와 비교
            all_location_codes = invoice_df['HVDC CODE 3'].value_counts().dropna()
            print(f"\n전체 위치 코드 분포:")
            for code, count in all_location_codes.head(10).items():
                is_hvdc = "← HVDC 창고" if code in location_codes else ""
                print(f"  {code}: {count}건 {is_hvdc}")
        
        # Description 컬럼에서 위치 정보 찾기
        if len(hvdc_data) > 0 and 'Description' in hvdc_data.columns:
            descriptions = hvdc_data['Description'].dropna().unique()
            print(f"\nHVDC 창고 설명:")
            for desc in descriptions[:5]:  # 처음 5개만 표시
                print(f"  {desc}")
        
        print(f"\n=== 8. HVDC CODE 3별 세부 분석 ===")
        if len(hvdc_data) > 0:
            # HVDC CODE 3별로 그룹화하여 분석
            code3_analysis = hvdc_data.groupby('HVDC CODE 3').agg({
                'Sqm': 'sum',
                'TOTAL': 'sum',
                'Operation Month': 'count'
            }).round(0)
            code3_analysis.rename(columns={'Operation Month': 'Records_Count'}, inplace=True)
            
            # 코드별 비중 계산
            total_sqm = code3_analysis['Sqm'].sum()
            code3_analysis['SQM_Percentage'] = (code3_analysis['Sqm'] / total_sqm * 100).round(1)
            
            print("HVDC CODE 3별 상세 분석:")
            print(code3_analysis.sort_values('Sqm', ascending=False).to_string())
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    check_hvdc_warehouse_location() 