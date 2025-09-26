#!/usr/bin/env python3
"""
최종 생성된 트랜잭션 데이터 검증
실제 데이터 요구사항 충족 여부 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime

def validate_final_generated_data():
    """최종 생성 데이터 검증"""
    
    print("🔍 최종 생성 트랜잭션 데이터 검증")
    print("=" * 60)
    
    # 가장 최근 생성된 파일 찾기
    import glob
    files = glob.glob('HVDC_최종실제데이터_트랜잭션_*.xlsx')
    if not files:
        print("❌ 생성된 트랜잭션 파일을 찾을 수 없습니다!")
        return
    
    latest_file = max(files)
    print(f"📁 검증 대상 파일: {latest_file}")
    
    try:
        # 트랜잭션 데이터 로드
        df = pd.read_excel(latest_file, sheet_name='Transactions')
        print(f"✅ 데이터 로드 성공: {len(df):,}건")
        
        print(f"\n=== 1. 기본 데이터 구조 검증 ===")
        
        # 필수 컬럼 확인
        required_columns = [
            'Case_No', 'Date', 'Location', 'TxType_Refined', 'Qty', 
            'Amount', 'Handling_Fee', 'SQM_Individual', 'SQM_Actual',
            'Stack_Status', 'Vendor', 'HVDC_CODE', 'Seasonal_Factor'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ 누락된 필수 컬럼: {missing_columns}")
        else:
            print(f"✅ 모든 필수 컬럼 존재 ({len(required_columns)}개)")
        
        print(f"\n=== 2. 케이스 수 검증 ===")
        
        # 케이스 수 확인
        unique_cases = df['Case_No'].nunique()
        expected_cases = 7573  # HITACHI 5,346 + SIMENSE 2,227
        
        print(f"생성된 케이스 수: {unique_cases:,}건")
        print(f"예상 케이스 수: {expected_cases:,}건")
        
        if unique_cases == expected_cases:
            print("✅ 케이스 수 일치!")
        else:
            print(f"⚠️ 케이스 수 차이: {abs(unique_cases - expected_cases):,}건")
        
        print(f"\n=== 3. 벤더별 분포 검증 ===")
        
        vendor_dist = df['Vendor'].value_counts()
        print("벤더별 트랜잭션 수:")
        for vendor, count in vendor_dist.items():
            print(f"  {vendor}: {count:,}건")
        
        # 벤더별 케이스 수
        vendor_cases = df.groupby('Vendor')['Case_No'].nunique()
        print("벤더별 케이스 수:")
        for vendor, count in vendor_cases.items():
            print(f"  {vendor}: {count:,}건")
            
        # 예상값과 비교
        expected_hitachi = 5346
        expected_simense = 2227
        
        hitachi_cases = vendor_cases.get('HITACHI', 0)
        simense_cases = vendor_cases.get('SIMENSE', 0)
        
        print(f"HITACHI 일치 여부: {hitachi_cases == expected_hitachi} ({hitachi_cases}/{expected_hitachi})")
        print(f"SIMENSE 일치 여부: {simense_cases == expected_simense} ({simense_cases}/{expected_simense})")
        
        print(f"\n=== 4. 트랜잭션 타입 검증 ===")
        
        tx_type_dist = df['TxType_Refined'].value_counts()
        print("트랜잭션 타입별 분포:")
        for tx_type, count in tx_type_dist.items():
            percentage = (count / len(df)) * 100
            print(f"  {tx_type}: {count:,}건 ({percentage:.1f}%)")
        
        # 기본적으로 각 케이스당 최소 IN + OUT 트랜잭션이 있어야 함
        min_expected_tx = unique_cases * 2  # 최소 IN + OUT
        print(f"최소 예상 트랜잭션: {min_expected_tx:,}건")
        print(f"실제 생성 트랜잭션: {len(df):,}건")
        
        if len(df) >= min_expected_tx:
            print("✅ 최소 트랜잭션 수 충족")
        else:
            print("❌ 최소 트랜잭션 수 미달")
        
        print(f"\n=== 5. 금액 및 비용 검증 ===")
        
        amount_stats = df['Amount'].describe()
        handling_fee_stats = df['Handling_Fee'].describe()
        
        print("금액 통계:")
        print(f"  총 금액: ${df['Amount'].sum():,.0f}")
        print(f"  평균 금액: ${amount_stats['mean']:,.0f}")
        print(f"  중간값: ${amount_stats['50%']:,.0f}")
        print(f"  범위: ${amount_stats['min']:,.0f} ~ ${amount_stats['max']:,.0f}")
        
        print("핸들링 수수료 통계:")
        print(f"  총 수수료: ${df['Handling_Fee'].sum():,.0f}")
        print(f"  평균 수수료: ${handling_fee_stats['mean']:,.0f}")
        
        # 수수료가 금액의 3-10% 범위인지 확인
        fee_percentage = (df['Handling_Fee'] / df['Amount']).mean() * 100
        print(f"  평균 수수료율: {fee_percentage:.1f}%")
        
        if 3 <= fee_percentage <= 10:
            print("✅ 수수료율 적정 범위 (3-10%)")
        else:
            print("⚠️ 수수료율 범위 확인 필요")
        
        print(f"\n=== 6. SQM 및 스택 효율성 검증 ===")
        
        sqm_individual_total = df['SQM_Individual'].sum()
        sqm_actual_total = df['SQM_Actual'].sum()
        
        if sqm_individual_total > 0:
            efficiency = (1 - sqm_actual_total / sqm_individual_total) * 100
            print(f"개별 SQM 총계: {sqm_individual_total:,.0f}")
            print(f"실제 SQM 총계: {sqm_actual_total:,.0f}")
            print(f"스택 적재 효율성: {efficiency:.1f}%")
            
            if efficiency > 0:
                print("✅ 스택 적재로 인한 공간 절약 확인")
            else:
                print("⚠️ 스택 적재 효과 미확인")
        
        print(f"\n=== 7. 시간적 분포 검증 ===")
        
        # 날짜 범위 확인
        df['Date'] = pd.to_datetime(df['Date'])
        date_range = (df['Date'].min(), df['Date'].max())
        print(f"날짜 범위: {date_range[0].strftime('%Y-%m-%d')} ~ {date_range[1].strftime('%Y-%m-%d')}")
        
        # 월별 분포
        df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')
        monthly_dist = df['Year_Month'].value_counts().sort_index()
        
        print("월별 트랜잭션 분포 (상위 5개월):")
        for month, count in monthly_dist.head().items():
            print(f"  {month}: {count:,}건")
        
        print(f"\n=== 8. 창고별 분포 검증 ===")
        
        location_dist = df['Location'].value_counts()
        print("창고별 트랜잭션 분포:")
        for location, count in location_dist.items():
            percentage = (count / len(df)) * 100
            print(f"  {location}: {count:,}건 ({percentage:.1f}%)")
        
        # 주요 창고 확인
        expected_warehouses = ['DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'HVDC']
        missing_warehouses = [w for w in expected_warehouses if w not in location_dist.index]
        
        if missing_warehouses:
            print(f"⚠️ 누락된 창고: {missing_warehouses}")
        else:
            print("✅ 모든 주요 창고 사용 확인")
        
        print(f"\n=== 9. 계절적 패턴 검증 ===")
        
        seasonal_factors = df['Seasonal_Factor'].describe()
        print("계절적 변동 팩터:")
        print(f"  평균: {seasonal_factors['mean']:.2f}")
        print(f"  범위: {seasonal_factors['min']:.2f} ~ {seasonal_factors['max']:.2f}")
        
        # 피크 시즌 확인
        peak_months = df[df['Seasonal_Factor'] > 2.0]['Year_Month'].value_counts()
        if len(peak_months) > 0:
            print("피크 시즌 (계절 팩터 > 2.0):")
            for month, count in peak_months.head().items():
                print(f"  {month}: {count:,}건")
            print("✅ 계절적 변동 패턴 적용 확인")
        
        print(f"\n=== 10. 데이터 품질 종합 평가 ===")
        
        # 품질 점수 계산
        quality_checks = []
        
        # 1. 필수 컬럼 존재 여부
        quality_checks.append(len(missing_columns) == 0)
        
        # 2. 케이스 수 일치 여부
        quality_checks.append(abs(unique_cases - expected_cases) <= 100)  # 100개 이내 오차 허용
        
        # 3. 최소 트랜잭션 수 충족
        quality_checks.append(len(df) >= min_expected_tx)
        
        # 4. 적정 수수료율
        quality_checks.append(3 <= fee_percentage <= 10)
        
        # 5. 모든 주요 창고 사용
        quality_checks.append(len(missing_warehouses) == 0)
        
        passed_checks = sum(quality_checks)
        total_checks = len(quality_checks)
        quality_score = (passed_checks / total_checks) * 100
        
        print(f"품질 검증 결과: {passed_checks}/{total_checks} 통과")
        print(f"품질 점수: {quality_score:.1f}%")
        
        if quality_score >= 80:
            print("✅ 고품질 데이터 생성 성공!")
        elif quality_score >= 60:
            print("⚠️ 양호한 품질, 일부 개선 필요")
        else:
            print("❌ 품질 개선 필요")
            
        print(f"\n🎯 최종 검증 완료!")
        print(f"파일: {latest_file}")
        print(f"품질 점수: {quality_score:.1f}%")
        
    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    validate_final_generated_data() 