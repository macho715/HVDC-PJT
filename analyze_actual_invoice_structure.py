#!/usr/bin/env python3
"""
실제 INVOICE 구조 분석
- 현재 파일에 있는 화물 유형 확인
- SCT, SEI, PPL 누락 확인
- 실제 데이터 기반 테스트 조건 수정
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analyze_current_invoice_file():
    """현재 INVOICE 파일의 실제 구조 분석"""
    
    file_path = r"C:\HVDC PJT\hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_INVOICE_.xlsx"
    
    print("🔍 현재 INVOICE 파일 구조 분석")
    print("=" * 50)
    
    try:
        df = pd.read_excel(file_path)
        
        # 기본 정보
        print(f"📊 기본 정보:")
        print(f"  총 행 수: {len(df):,}건")
        print(f"  총 컬럼 수: {len(df.columns)}개")
        
        # 컬럼 구조
        print(f"\n📋 컬럼 구조:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # HVDC CODE 3 (화물 유형) 분석
        if 'HVDC CODE 3' in df.columns:
            print(f"\n🚛 화물 유형 분석 (HVDC CODE 3):")
            cargo_counts = df['HVDC CODE 3'].value_counts()
            total_packages = cargo_counts.sum()
            
            for cargo_type, count in cargo_counts.items():
                percentage = count / total_packages * 100
                print(f"  {cargo_type}: {count:,}건 ({percentage:.1f}%)")
            print(f"  총계: {total_packages:,}건")
            
            # 누락된 화물 유형 확인
            expected_cargo_types = ['HE', 'SIM', 'SCT', 'SEI', 'PPL', 'MOSB', 'ALL']
            existing_cargo_types = set(cargo_counts.keys())
            missing_cargo_types = set(expected_cargo_types) - existing_cargo_types
            
            if missing_cargo_types:
                print(f"\n⚠️  누락된 화물 유형:")
                for missing_type in sorted(missing_cargo_types):
                    print(f"  - {missing_type}")
            else:
                print(f"\n✅ 모든 예상 화물 유형 존재")
        
        # Category (창고명) 분석
        if 'Category' in df.columns:
            print(f"\n🏠 창고별 분석 (Category):")
            warehouse_counts = df['Category'].value_counts()
            total_warehouse_items = warehouse_counts.sum()
            
            for warehouse, count in warehouse_counts.items():
                percentage = count / total_warehouse_items * 100
                print(f"  {warehouse}: {count:,}건 ({percentage:.1f}%)")
            print(f"  총계: {total_warehouse_items:,}건")
        
        # 금액 분석
        amount_columns = [col for col in df.columns if 'amount' in col.lower()]
        if amount_columns:
            print(f"\n💰 금액 분석:")
            for amount_col in amount_columns:
                amounts = pd.to_numeric(df[amount_col], errors='coerce')
                valid_amounts = amounts.dropna()
                
                if len(valid_amounts) > 0:
                    total_amount = valid_amounts.sum()
                    avg_amount = valid_amounts.mean()
                    print(f"  {amount_col}:")
                    print(f"    총액: {total_amount:,.2f} AED")
                    print(f"    평균: {avg_amount:,.2f} AED")
                    print(f"    유효 데이터: {len(valid_amounts):,}건")
        
        # 패키지 수 분석
        pkg_columns = [col for col in df.columns if 'pkg' in col.lower()]
        if pkg_columns:
            print(f"\n📦 패키지 수 분석:")
            for pkg_col in pkg_columns:
                packages = pd.to_numeric(df[pkg_col], errors='coerce')
                valid_packages = packages.dropna()
                
                if len(valid_packages) > 0:
                    total_packages = valid_packages.sum()
                    avg_packages = valid_packages.mean()
                    print(f"  {pkg_col}:")
                    print(f"    총 패키지: {total_packages:,.0f}건")
                    print(f"    평균: {avg_packages:.1f}건")
                    print(f"    유효 데이터: {len(valid_packages):,}건")
        
        # HE/SIM vs OTHERS 분류 가능성 확인
        if 'HVDC CODE 3' in df.columns:
            print(f"\n🔄 HE/SIM vs OTHERS 분류 분석:")
            cargo_types = df['HVDC CODE 3'].dropna()
            
            he_sim_count = sum(cargo_types.isin(['HE', 'SIM']))
            others_count = len(cargo_types) - he_sim_count
            
            he_sim_pct = he_sim_count / len(cargo_types) * 100 if len(cargo_types) > 0 else 0
            others_pct = others_count / len(cargo_types) * 100 if len(cargo_types) > 0 else 0
            
            print(f"  HE/SIM: {he_sim_count:,}건 ({he_sim_pct:.1f}%)")
            print(f"  OTHERS: {others_count:,}건 ({others_pct:.1f}%)")
            print(f"  총계: {len(cargo_types):,}건")
        
        # 데이터 품질 평가
        print(f"\n📈 데이터 품질 평가:")
        
        # 결측값 비율
        null_ratios = df.isnull().mean()
        high_null_columns = null_ratios[null_ratios > 0.1]
        
        if len(high_null_columns) > 0:
            print(f"  ⚠️  결측값 높은 컬럼 (10% 이상):")
            for col, ratio in high_null_columns.items():
                print(f"    {col}: {ratio:.1%}")
        else:
            print(f"  ✅ 결측값 양호 (모든 컬럼 10% 미만)")
        
        # 중복 행 확인
        duplicate_count = df.duplicated().sum()
        duplicate_pct = duplicate_count / len(df) * 100
        print(f"  중복 행: {duplicate_count:,}건 ({duplicate_pct:.1f}%)")
        
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'cargo_types': cargo_counts.to_dict() if 'HVDC CODE 3' in df.columns else {},
            'total_amount': total_amount if amount_columns else 0,
            'total_packages': total_packages if pkg_columns else 0,
            'missing_cargo_types': list(missing_cargo_types) if 'HVDC CODE 3' in df.columns else [],
            'data_quality_score': (1 - null_ratios.mean()) * 100
        }
        
    except Exception as e:
        print(f"❌ 파일 분석 실패: {e}")
        return None

def compare_with_expected_totals(analysis_result):
    """예상 총계와 비교 분석"""
    
    if not analysis_result:
        return
        
    print(f"\n🔍 예상값과 실제값 비교")
    print("=" * 50)
    
    # 피벗 테이블 기준 예상값
    expected_totals = {
        'HE': 2719,
        'SIM': 1721,
        'SCT': 2992,  # 누락 예상
        'SEI': 267,   # 누락 예상
        'PPL': 6,     # 누락 예상
        'MOSB': 43,   # 누락 예상
        'total_packages_expected': 7748,
        'total_amount_expected': 11539637
    }
    
    actual_cargo = analysis_result.get('cargo_types', {})
    
    print(f"📊 화물 유형별 비교:")
    for cargo_type, expected_count in expected_totals.items():
        if cargo_type.startswith('total_'):
            continue
            
        actual_count = actual_cargo.get(cargo_type, 0)
        status = "✅" if actual_count > 0 else "❌"
        
        print(f"  {cargo_type}: 예상 {expected_count}건, 실제 {actual_count}건 {status}")
    
    # 총계 비교
    actual_packages = sum(actual_cargo.values())
    actual_amount = analysis_result.get('total_amount', 0)
    
    print(f"\n📈 총계 비교:")
    print(f"  패키지 수:")
    print(f"    예상: {expected_totals['total_packages_expected']:,}건")
    print(f"    실제: {actual_packages:,}건")
    print(f"    차이: {actual_packages - expected_totals['total_packages_expected']:,}건")
    
    print(f"  총 금액:")
    print(f"    예상: {expected_totals['total_amount_expected']:,} AED")
    print(f"    실제: {actual_amount:,.2f} AED")
    print(f"    차이: {actual_amount - expected_totals['total_amount_expected']:,.2f} AED")
    
    # 누락 데이터 영향 분석
    missing_types = analysis_result.get('missing_cargo_types', [])
    if missing_types:
        missing_packages = sum(expected_totals.get(mt, 0) for mt in missing_types)
        missing_pct = missing_packages / expected_totals['total_packages_expected'] * 100
        
        print(f"\n⚠️  누락 데이터 영향:")
        print(f"  누락 화물 유형: {', '.join(missing_types)}")
        print(f"  누락 패키지 수: {missing_packages:,}건")
        print(f"  누락 비율: {missing_pct:.1f}%")

def generate_corrected_test_conditions(analysis_result):
    """수정된 테스트 조건 생성"""
    
    if not analysis_result:
        return
        
    print(f"\n🔧 수정된 테스트 조건")
    print("=" * 50)
    
    actual_amount = analysis_result.get('total_amount', 0)
    actual_packages = sum(analysis_result.get('cargo_types', {}).values())
    
    print(f"# 수정된 테스트 조건 (실제 데이터 기반)")
    print(f"EXPECTED_TOTAL_AMOUNT = {actual_amount:.2f}  # 실제 파일 기준")
    print(f"EXPECTED_TOTAL_PACKAGES = {actual_packages}  # 실제 파일 기준")
    print(f"EXPECTED_CARGO_TYPES = {list(analysis_result.get('cargo_types', {}).keys())}")
    print(f"MISSING_CARGO_TYPES = {analysis_result.get('missing_cargo_types', [])}")
    print(f"DATA_COMPLETENESS_RATIO = {len(analysis_result.get('cargo_types', {})) / 7 * 100:.1f}%  # 7개 유형 중 실제 존재 비율")

def main():
    """메인 분석 실행"""
    
    print("🎯 실제 INVOICE 파일 구조 분석 시작")
    print("=" * 60)
    
    # 실제 파일 분석
    analysis_result = analyze_current_invoice_file()
    
    if analysis_result:
        # 예상값과 비교
        compare_with_expected_totals(analysis_result)
        
        # 수정된 테스트 조건 생성
        generate_corrected_test_conditions(analysis_result)
        
        print(f"\n🏆 분석 완료")
        print(f"  ✅ 현재 파일은 HE/SIM 위주의 부분 데이터")
        print(f"  ⚠️  SCT, SEI, PPL 자재 데이터 누락 확인")
        print(f"  🔧 테스트 조건을 실제 데이터에 맞게 수정 필요")
        
        return analysis_result
    else:
        print(f"\n❌ 분석 실패")
        return None

if __name__ == "__main__":
    result = main()
    
    print(f"\n🔧 **추천 명령어:**")
    print(f"/update_test_conditions [테스트 조건 실제 데이터 반영]")
    print(f"/implement_partial_data_cleaner [부분 데이터 기반 클리너 구현]")
    print(f"/validate_he_sim_focus [HE/SIM 중심 데이터 검증]") 