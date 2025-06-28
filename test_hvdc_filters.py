#!/usr/bin/env python3
"""
HVDC 필터 기능 테스트 v2.6

가이드에 따른 코드 정규화, 벤더/창고 필터, 월 매칭, Handling IN/OUT 등 모든 기능 테스트
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import importlib.util

# 테스트할 모듈들 import
from mapping_utils import (
    normalize_code_num, codes_match, is_valid_hvdc_vendor, is_warehouse_code
)
from excel_reporter import apply_hvdc_filters

# 파일명에 점이 포함된 모듈들을 동적으로 import
spec = importlib.util.spec_from_file_location("hvdc_automation_pipeline", "hvdc_automation_pipeline_v2.6.py")
hvdc_automation_pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hvdc_automation_pipeline)

spec2 = importlib.util.spec_from_file_location("ontology_mapper", "ontology_mapper.py")
ontology_mapper = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(ontology_mapper)

def test_code_normalization():
    """A. HVDC CODE 정규화 테스트"""
    print("🧪 A. HVDC CODE 정규화 테스트")
    
    test_cases = [
        ("0014", 14),
        ("014", 14),
        ("14", 14),
        ("HE0014", 14),
        ("SIM014", 14),
        ("ABC123", 123),
        ("XYZ", "XYZ"),  # 숫자가 없으면 원본 반환
        ("", ""),
        (None, None)
    ]
    
    for input_code, expected in test_cases:
        result = normalize_code_num(input_code)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {input_code} → {result} (예상: {expected})")
    
    # 코드 매칭 테스트
    print("\n  🔍 코드 매칭 테스트:")
    match_tests = [
        ("0014", "14", True),
        ("HE0014", "SIM014", True),
        ("123", "456", False),
        ("ABC", "ABC", True)
    ]
    
    for code_a, code_b, expected in match_tests:
        result = codes_match(code_a, code_b)
        status = "✅" if result == expected else "❌"
        print(f"    {status} {code_a} == {code_b} → {result} (예상: {expected})")

def test_vendor_filter():
    """B. CODE 3 필터 테스트 (HE, SIM만 유효)"""
    print("\n🧪 B. 벤더 필터 테스트 (HE, SIM만 유효)")
    
    test_cases = [
        ("HE", True),
        ("SIM", True),
        ("HITACHI", False),
        ("SAMSUNG", False),
        ("he", True),  # 대소문자 무시
        ("sim", True),
        ("", False),
        (None, False)
    ]
    
    for vendor, expected in test_cases:
        result = is_valid_hvdc_vendor(vendor)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {vendor} → {result} (예상: {expected})")

def test_warehouse_filter():
    """C. 창고 코드 필터 테스트"""
    print("\n🧪 C. 창고 코드 필터 테스트")
    
    test_cases = [
        ("DSV Outdoor", True),
        ("DSV Indoor", True),
        ("DSV Al Markaz", True),
        ("DSV MZP", True),
        ("dsv outdoor", True),  # 대소문자 무시
        ("AGI", False),
        ("DAS", False),
        ("", False),
        (None, False)
    ]
    
    for warehouse, expected in test_cases:
        result = is_warehouse_code(warehouse)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {warehouse} → {result} (예상: {expected})")

def test_month_matching():
    """D. Operation Month(월) 매칭 테스트"""
    print("\n🧪 D. 월 매칭 테스트")
    
    # 테스트 데이터 생성
    test_data = {
        'Operation Month': ['2024-01-15', '2024-02-20', '2024-03-10', '2024-01-25'],
        'ETA': ['2024-01-20', '2024-02-15', '2024-03-05', '2024-02-01'],
        'HVDC CODE': ['HE0014', 'SIM0252', 'HE0014', 'SIM0252'],
        'HVDC CODE 3': ['HE', 'SIM', 'HE', 'SIM'],
        'HVDC CODE 4': ['0014', '0252', '0014', '0252'],
        'Qty': [10, 20, 15, 25],
        'Amount': [1000, 2000, 1500, 2500]
    }
    
    df = pd.DataFrame(test_data)
    print(f"  📊 원본 데이터: {len(df)}행")
    
    # 월 매칭 적용
    df['INVOICE_MONTH'] = pd.to_datetime(df['Operation Month'], errors='coerce').dt.strftime('%Y-%m')
    df['WAREHOUSE_MONTH'] = pd.to_datetime(df['ETA'], errors='coerce').dt.strftime('%Y-%m')
    
    original_count = len(df)
    df_matched = df[df['INVOICE_MONTH'] == df['WAREHOUSE_MONTH']]
    filtered_count = len(df_matched)
    
    print(f"  ✅ 월 매칭 결과: {original_count} → {filtered_count} (필터링: {original_count - filtered_count}건)")
    
    # 매칭된 데이터 출력
    for idx, row in df_matched.iterrows():
        print(f"    📅 {row['INVOICE_MONTH']} == {row['WAREHOUSE_MONTH']} → {row['HVDC CODE']}")

def test_handling_fields():
    """E. Handling IN/OUT 필드 집계 테스트"""
    print("\n🧪 E. Handling IN/OUT 필드 집계 테스트")
    
    # 테스트 데이터 생성
    test_data = {
        'Handling In freight ton': [10.5, 20.0, None, 'N/A', 15.5],
        'Handling out Freight Ton': [5.5, 12.0, 8.5, None, '0'],
        'HVDC CODE': ['HE0014', 'SIM0252', 'HE0014', 'SIM0252', 'HE0014'],
        'HVDC CODE 3': ['HE', 'SIM', 'HE', 'SIM', 'HE']
    }
    
    df = pd.DataFrame(test_data)
    print(f"  📊 원본 데이터: {len(df)}행")
    
    # Handling 필드 처리
    handling_fields = ['Handling In freight ton', 'Handling out Freight Ton']
    for field in handling_fields:
        if field in df.columns:
            df[field] = df[field].apply(lambda x: float(x) if pd.notna(x) and str(x).lower() != 'n/a' else 0)
            total = df[field].sum()
            print(f"  ✅ {field}: 총 {total} (처리 완료)")
    
    # 결과 출력
    for idx, row in df.iterrows():
        print(f"    📦 {row['HVDC CODE']}: IN={row['Handling In freight ton']}, OUT={row['Handling out Freight Ton']}")

def test_integrated_filters():
    """통합 필터 테스트 (모든 기능 조합)"""
    print("\n🧪 통합 필터 테스트 (모든 기능 조합)")
    
    # 종합 테스트 데이터 생성
    test_data = {
        'HVDC CODE': ['HE0014', 'SIM0252', 'HE0014', 'SAMSUNG0014', 'HE0252'],
        'HVDC CODE 3': ['HE', 'SIM', 'HE', 'SAMSUNG', 'HE'],
        'HVDC CODE 4': ['0014', '0252', '0014', '0014', '0252'],
        'Operation Month': ['2024-01-15', '2024-02-20', '2024-01-25', '2024-01-15', '2024-02-20'],
        'ETA': ['2024-01-20', '2024-02-15', '2024-01-30', '2024-01-20', '2024-02-25'],
        'Handling In freight ton': [10.5, 20.0, 15.5, 12.0, 18.5],
        'Handling out Freight Ton': [5.5, 12.0, 8.5, 6.0, 10.0],
        'SQM': [100, 200, 150, 120, 180],
        'Qty': [10, 20, 15, 12, 18],
        'Amount': [1000, 2000, 1500, 1200, 1800]
    }
    
    df = pd.DataFrame(test_data)
    print(f"  📊 원본 데이터: {len(df)}행")
    
    # 1. HVDC CODE 정규화 및 매칭
    df['HVDC_CODE_NORMALIZED'] = df['HVDC CODE'].apply(normalize_code_num)
    df['HVDC_CODE4_NORMALIZED'] = df['HVDC CODE 4'].apply(normalize_code_num)
    df['CODE_MATCH'] = df.apply(lambda row: codes_match(row['HVDC CODE'], row['HVDC CODE 4']), axis=1)
    
    # 2. 벤더 필터 (HE, SIM만)
    df = df[df['HVDC CODE 3'].apply(lambda x: is_valid_hvdc_vendor(x, ['HE', 'SIM']))]
    
    # 3. 월 매칭
    df['INVOICE_MONTH'] = pd.to_datetime(df['Operation Month'], errors='coerce').dt.strftime('%Y-%m')
    df['WAREHOUSE_MONTH'] = pd.to_datetime(df['ETA'], errors='coerce').dt.strftime('%Y-%m')
    df = df[df['INVOICE_MONTH'] == df['WAREHOUSE_MONTH']]
    
    # 4. Handling 필드 처리
    handling_fields = ['Handling In freight ton', 'Handling out Freight Ton']
    for field in handling_fields:
        if field in df.columns:
            df[field] = df[field].apply(lambda x: float(x) if pd.notna(x) else 0)
    
    print(f"  ✅ 필터링 후 데이터: {len(df)}행")
    
    # 결과 요약
    if not df.empty:
        total_handling_in = df['Handling In freight ton'].sum()
        total_handling_out = df['Handling out Freight Ton'].sum()
        total_amount = df['Amount'].sum()
        
        print(f"  📊 집계 결과:")
        print(f"    - 총 Handling In: {total_handling_in}")
        print(f"    - 총 Handling Out: {total_handling_out}")
        print(f"    - 총 금액: {total_amount}")
        
        # 벤더별 집계
        vendor_summary = df.groupby('HVDC CODE 3').agg({
            'Amount': 'sum',
            'Handling In freight ton': 'sum',
            'Handling out Freight Ton': 'sum'
        }).round(2)
        
        print(f"  🏢 벤더별 집계:")
        print(vendor_summary)
    else:
        print("  ⚠️ 필터링 후 데이터가 없습니다.")

def test_mapping_rules_integration():
    """매핑 규칙 통합 테스트"""
    print("\n🧪 매핑 규칙 통합 테스트")
    
    try:
        with open('mapping_rules_v2.6.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        # 새로운 설정들 확인
        required_fields = [
            'code_normalization',
            'hvdc_code3_valid', 
            'warehouse_codes',
            'month_matching'
        ]
        
        for field in required_fields:
            if field in rules:
                print(f"  ✅ {field}: {rules[field]}")
            else:
                print(f"  ❌ {field}: 누락됨")
        
        # property_mappings에서 새로운 필드 확인
        new_properties = ['SQM', 'Handling In freight ton', 'Handling out Freight Ton']
        for prop in new_properties:
            if prop in rules.get('property_mappings', {}):
                print(f"  ✅ property_mappings.{prop}: {rules['property_mappings'][prop]}")
            else:
                print(f"  ❌ property_mappings.{prop}: 누락됨")
                
    except Exception as e:
        print(f"  ❌ 매핑 규칙 로드 실패: {e}")

def main():
    """메인 테스트 실행"""
    print("🚀 HVDC 필터 기능 테스트 v2.6 시작")
    print("=" * 60)
    
    # 개별 테스트 실행
    test_code_normalization()
    test_vendor_filter()
    test_warehouse_filter()
    test_month_matching()
    test_handling_fields()
    test_integrated_filters()
    test_mapping_rules_integration()
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("\n🔧 추천 명령어:")
    print("  • /logi_master excel-reporter [HVDC Excel Reporter 실행]")
    print("  • /logi_master data-validation [데이터 검증 엔진 실행]")
    print("  • /logi_master warehouse-status [창고 상태 확인]")

if __name__ == "__main__":
    main() 