#!/usr/bin/env python3
"""
HITACHI 월별 피벗 테이블 분석 스크립트
HITACHI_월별_피벗 시트의 의미와 구조를 상세히 설명
"""

import pandas as pd
import numpy as np
import os

def analyze_hitachi_monthly_pivot():
    """HITACHI 월별 피벗 테이블 분석"""
    
    # 가장 최근 HITACHI 분석 보고서 파일 찾기
    hitachi_files = [f for f in os.listdir('.') if f.startswith('HITACHI_Analysis_Report_') and f.endswith('.xlsx')]
    
    if not hitachi_files:
        print("❌ HITACHI 분석 보고서가 없습니다.")
        return
    
    # 가장 최근 파일 사용
    latest_file = max(hitachi_files, key=lambda x: os.path.getmtime(x))
    print(f"📁 분석할 파일: {latest_file}")
    
    try:
        # HITACHI 월별 피벗 시트 로드
        hitachi_pivot = pd.read_excel(latest_file, sheet_name='HITACHI_월별_피벗', index_col=0)
        
        print("\n" + "="*80)
        print("🔍 HITACHI_월별_피벗 시트 분석 결과")
        print("="*80)
        
        # 1. 기본 구조 정보
        print(f"\n📊 기본 구조:")
        print(f"   크기: {hitachi_pivot.shape[0]}행 × {hitachi_pivot.shape[1]}열")
        print(f"   행(월): {hitachi_pivot.index.min()} ~ {hitachi_pivot.index.max()}")
        print(f"   열(Final_Location): {hitachi_pivot.shape[1]}개")
        
        # 2. 열(Final_Location) 목록
        print(f"\n🏢 Final_Location 목록:")
        for i, location in enumerate(hitachi_pivot.columns, 1):
            print(f"   {i:2d}. {location}")
        
        # 3. 월별 총 입고량 (행별 합계)
        print(f"\n📈 월별 HITACHI 입고 총량:")
        monthly_totals = hitachi_pivot.sum(axis=1)
        for month, total in monthly_totals.items():
            print(f"   {month}: {total:,}건")
        
        # 4. Final_Location별 총 입고량 (열별 합계)
        print(f"\n🏢 Final_Location별 HITACHI 입고 총량:")
        location_totals = hitachi_pivot.sum(axis=0).sort_values(ascending=False)
        for location, total in location_totals.items():
            print(f"   {location}: {total:,}건")
        
        # 5. 상위 5개 월별 세부 분석
        print(f"\n📊 상위 5개 월별 세부 분석:")
        top_5_months = monthly_totals.sort_values(ascending=False).head(5)
        for month, total in top_5_months.items():
            print(f"\n   📅 {month} (총 {total:,}건):")
            month_data = hitachi_pivot.loc[month]
            month_data_sorted = month_data[month_data > 0].sort_values(ascending=False)
            for location, count in month_data_sorted.head(5).items():
                percentage = (count / total) * 100
                print(f"      {location}: {count:,}건 ({percentage:.1f}%)")
        
        # 6. 샘플 데이터 표시 (처음 5개월, 상위 5개 Location)
        print(f"\n📋 샘플 데이터 (처음 5개월 × 상위 5개 Final_Location):")
        top_5_locations = location_totals.head(5).index
        first_5_months = hitachi_pivot.head(5)
        sample_data = first_5_months[top_5_locations]
        
        print(f"\n{sample_data.to_string()}")
        
        # 7. 데이터 해석
        print(f"\n" + "="*80)
        print("📖 HITACHI_월별_피벗 시트의 의미")
        print("="*80)
        
        print(f"""
🎯 **피벗 테이블 구조 설명:**

📊 **행(Index)**: 월별 기간 (2023-02 ~ 2025-07)
   - 각 행은 특정 월을 나타냄
   - 총 {hitachi_pivot.shape[0]}개월의 데이터

🏢 **열(Columns)**: Final_Location (최종 위치)
   - 각 열은 HITACHI 장비의 최종 보관/설치 위치
   - 총 {hitachi_pivot.shape[1]}개의 다른 위치

📈 **값(Values)**: 입고 건수
   - 각 셀은 특정 월에 특정 Final_Location에 입고된 HITACHI 장비 건수
   - 0은 해당 월에 해당 위치로 입고가 없었음을 의미

🔍 **활용 방법:**
   1. 월별 트렌드 분석: 행별 합계로 월별 총 입고량 파악
   2. 위치별 분석: 열별 합계로 각 Final_Location별 총 입고량 파악
   3. 계절성 분석: 특정 월들의 패턴 비교
   4. 위치 선호도: 어떤 위치가 가장 많이 사용되는지 분석

📋 **실제 데이터 예시:**
   - 2025-05월에 DSV Al Markaz로 입고된 HITACHI 장비 건수
   - 2024-12월에 DSV Outdoor로 입고된 HITACHI 장비 건수
   - 각 월별, 각 위치별 정확한 입고 수량 추적 가능
""")
        
        # 8. 주요 인사이트
        print(f"\n🔍 **주요 인사이트:**")
        
        # 최대 입고 월
        max_month = monthly_totals.idxmax()
        max_count = monthly_totals.max()
        print(f"   📊 최대 입고 월: {max_month} ({max_count:,}건)")
        
        # 최대 입고 위치
        max_location = location_totals.idxmax()
        max_location_count = location_totals.max()
        print(f"   🏢 최대 입고 위치: {max_location} ({max_location_count:,}건)")
        
        # 월별 평균
        avg_monthly = monthly_totals.mean()
        print(f"   📈 월별 평균 입고: {avg_monthly:.1f}건")
        
        # 위치별 평균
        avg_per_location = location_totals.mean()
        print(f"   🏢 위치별 평균 입고: {avg_per_location:.1f}건")
        
        # 데이터 집중도 분석
        total_entries = hitachi_pivot.sum().sum()
        non_zero_entries = (hitachi_pivot > 0).sum().sum()
        sparsity = (1 - non_zero_entries / (hitachi_pivot.shape[0] * hitachi_pivot.shape[1])) * 100
        
        print(f"   📊 총 입고 건수: {total_entries:,}건")
        print(f"   📊 활성 데이터 셀: {non_zero_entries:,}개")
        print(f"   📊 데이터 희소성: {sparsity:.1f}% (빈 셀 비율)")
        
        return hitachi_pivot
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return None

if __name__ == "__main__":
    analyze_hitachi_monthly_pivot() 