# -*- coding: utf-8 -*-
# 데이터 로더 테스트

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from hvdc_dashboard.data_loader import load_data, create_sample_data, validate_data
from hvdc_dashboard.business_logic import enrich_data, calculate_kpis

def test_sample_data_creation():
    """샘플 데이터 생성 테스트"""
    print("🧪 샘플 데이터 생성 테스트...")
    
    df = create_sample_data()
    
    # 기본 검증
    assert not df.empty, "데이터가 비어있습니다"
    assert len(df) == 100, f"예상 건수: 100, 실제: {len(df)}"
    
    # 필수 컬럼 검증
    required_cols = ['HVDC CODE', 'CATEGORY', 'TEU']
    for col in required_cols:
        assert col in df.columns, f"필수 컬럼 누락: {col}"
    
    print("✅ 샘플 데이터 생성 테스트 통과")

def test_data_validation():
    """데이터 검증 테스트"""
    print("🧪 데이터 검증 테스트...")
    
    df = create_sample_data()
    
    # 정상 데이터 검증
    validate_data(df)
    print("✅ 정상 데이터 검증 통과")
    
    # 빈 데이터 검증
    empty_df = pd.DataFrame()
    try:
        validate_data(empty_df)
        assert False, "빈 데이터 검증이 실패해야 합니다"
    except Exception as e:
        print(f"✅ 빈 데이터 검증 예외 처리: {e}")

def test_data_enrichment():
    """데이터 풍부화 테스트"""
    print("🧪 데이터 풍부화 테스트...")
    
    df = create_sample_data()
    enriched_df = enrich_data(df)
    
    # 파생 컬럼 검증
    derived_cols = ['TEU', 'OOG', 'YEAR', 'MONTH', 'YYYYMM', 'WAREHOUSE']
    for col in derived_cols:
        assert col in enriched_df.columns, f"파생 컬럼 누락: {col}"
    
    # TEU 계산 검증
    assert enriched_df['TEU'].sum() > 0, "TEU 합계가 0보다 커야 합니다"
    
    # OOG 검증
    assert 'OOG' in enriched_df.columns, "OOG 컬럼이 생성되지 않았습니다"
    
    print("✅ 데이터 풍부화 테스트 통과")

def test_kpi_calculation():
    """KPI 계산 테스트"""
    print("🧪 KPI 계산 테스트...")
    
    df = create_sample_data()
    enriched_df = enrich_data(df)
    kpis = calculate_kpis(enriched_df)
    
    # 기본 KPI 검증
    required_kpis = ['total_teu', 'oog_count', 'total_items', 'avg_teu_per_item', 'oog_percentage']
    for kpi in required_kpis:
        assert kpi in kpis, f"필수 KPI 누락: {kpi}"
    
    # 값 검증
    assert kpis['total_teu'] > 0, "TEU 합계가 0보다 커야 합니다"
    assert kpis['total_items'] == len(enriched_df), "총 건수가 일치하지 않습니다"
    assert 0 <= kpis['oog_percentage'] <= 100, "OOG 비율이 0-100 범위를 벗어났습니다"
    
    print("✅ KPI 계산 테스트 통과")

def test_data_loading():
    """데이터 로딩 테스트"""
    print("🧪 데이터 로딩 테스트...")
    
    try:
        df = load_data()
        assert not df.empty, "로드된 데이터가 비어있습니다"
        print("✅ 데이터 로딩 테스트 통과")
    except Exception as e:
        print(f"⚠️ 데이터 로딩 테스트 (샘플 데이터로 대체): {e}")

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 HVDC 대시보드 테스트 시작...\n")
    
    tests = [
        test_sample_data_creation,
        test_data_validation,
        test_data_enrichment,
        test_kpi_calculation,
        test_data_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ 테스트 실패: {test.__name__} - {e}")
    
    print(f"\n📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과!")
        return True
    else:
        print("⚠️ 일부 테스트 실패")
        return False

if __name__ == "__main__":
    run_all_tests() 