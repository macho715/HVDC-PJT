#!/usr/bin/env python3
"""
HVDC 온톨로지 통합 시스템 테스터 v3.0.0
- 통합된 온톨로지 스키마 및 매핑 규칙 검증
- MACHO-GPT v3.4-mini 표준 준수 테스트
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_integrated_ontology_system():
    """통합 온톨로지 시스템 테스트"""
    print("🔌 HVDC 온톨로지 통합 시스템 테스트 v3.0.0")
    print("=" * 60)
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'summary': {}
    }
    
    # 1. 스키마 파일 검증
    print("\n📋 1. 온톨로지 스키마 파일 검증")
    schema_result = test_schema_file()
    test_results['tests']['schema_validation'] = schema_result
    print(f"   ✅ 스키마 검증: {'PASS' if schema_result['success'] else 'FAIL'}")
    
    # 2. 매핑 규칙 검증
    print("\n🔄 2. 매핑 규칙 검증")
    mapping_result = test_mapping_rules()
    test_results['tests']['mapping_validation'] = mapping_result
    print(f"   ✅ 매핑 규칙: {'PASS' if mapping_result['success'] else 'FAIL'}")
    
    # 3. 데이터 통합 테스트
    print("\n📊 3. 데이터 통합 테스트")
    integration_result = test_data_integration()
    test_results['tests']['data_integration'] = integration_result
    print(f"   ✅ 데이터 통합: {'PASS' if integration_result['success'] else 'FAIL'}")
    
    # 4. OFCO 매핑 테스트
    print("\n💰 4. OFCO 매핑 테스트")
    ofco_result = test_ofco_mapping()
    test_results['tests']['ofco_mapping'] = ofco_result
    print(f"   ✅ OFCO 매핑: {'PASS' if ofco_result['success'] else 'FAIL'}")
    
    # 5. 검증 요약
    print("\n📈 5. 검증 요약")
    summary = generate_test_summary(test_results)
    test_results['summary'] = summary
    
    print(f"   🎯 전체 성공률: {summary['success_rate']:.1f}%")
    print(f"   ✅ 성공한 테스트: {summary['passed_tests']}/{summary['total_tests']}")
    
    # 결과 저장 (JSON 직렬화 문제 해결)
    output_file = f"hvdc_ontology_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # JSON 직렬화 가능한 형태로 변환
    json_safe_results = convert_to_json_serializable(test_results)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_safe_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 테스트 결과 저장: {output_file}")
    return test_results

def test_schema_file():
    """온톨로지 스키마 파일 테스트"""
    result = {
        'success': False,
        'details': {},
        'errors': []
    }
    
    try:
        schema_file = Path("hvdc_integrated_ontology_schema.ttl")
        
        if not schema_file.exists():
            result['errors'].append("스키마 파일이 존재하지 않음")
            return result
        
        # 파일 읽기
        with open(schema_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 기본 검증
        checks = {
            'has_namespace_declaration': '@prefix ex:' in content,
            'has_ontology_declaration': 'a owl:Ontology' in content,
            'has_transport_event_class': 'TransportEvent a owl:Class' in content,
            'has_warehouse_class': 'Warehouse a owl:Class' in content,
            'has_basic_properties': 'hasCase a owl:DatatypeProperty' in content,
            'has_korean_labels': '@ko' in content,
            'has_class_hierarchy': 'rdfs:subClassOf' in content
        }
        
        result['details'] = checks
        result['success'] = all(checks.values())
        
        if not result['success']:
            failed_checks = [k for k, v in checks.items() if not v]
            result['errors'] = [f"실패한 검증: {', '.join(failed_checks)}"]
        
    except Exception as e:
        result['errors'].append(f"스키마 파일 검증 중 오류: {str(e)}")
    
    return result

def test_mapping_rules():
    """매핑 규칙 파일 테스트"""
    result = {
        'success': False,
        'details': {},
        'errors': []
    }
    
    try:
        mapping_file = Path("hvdc_integrated_mapping_rules_v3.0.json")
        
        if not mapping_file.exists():
            result['errors'].append("매핑 규칙 파일이 존재하지 않음")
            return result
        
        # JSON 파일 로드
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)
        
        # 기본 구조 검증
        required_sections = [
            'namespace', 'version', 'field_mappings', 'property_mappings',
            'class_mappings', 'warehouse_classification', 'logistics_flow_definition',
            'ofco_mapping_rules', 'sparql_templates', 'validation_rules'
        ]
        
        checks = {}
        for section in required_sections:
            checks[f'has_{section}'] = section in mapping_data
        
        # 필드 매핑 검증
        field_mappings = mapping_data.get('field_mappings', {})
        checks['has_case_mapping'] = 'Case_No' in field_mappings
        checks['has_date_mapping'] = 'Date' in field_mappings
        checks['has_location_mapping'] = 'Location' in field_mappings
        checks['has_quantity_mapping'] = 'Qty' in field_mappings
        
        # OFCO 규칙 검증
        ofco_rules = mapping_data.get('ofco_mapping_rules', {})
        checks['has_ofco_cost_centers'] = 'cost_centers' in ofco_rules
        checks['has_ofco_mapping_rules'] = 'mapping_rules' in ofco_rules
        
        # 버전 검증
        checks['correct_version'] = mapping_data.get('version') == '3.0.0'
        
        result['details'] = checks
        result['success'] = all(checks.values())
        
        if not result['success']:
            failed_checks = [k for k, v in checks.items() if not v]
            result['errors'] = [f"실패한 검증: {', '.join(failed_checks)}"]
        
    except Exception as e:
        result['errors'].append(f"매핑 규칙 검증 중 오류: {str(e)}")
    
    return result

def test_data_integration():
    """데이터 통합 테스트"""
    result = {
        'success': False,
        'details': {},
        'errors': []
    }
    
    try:
        # 테스트 데이터 생성
        test_data = create_test_dataset()
        
        # 매핑 규칙 로드
        mapping_file = Path("hvdc_integrated_mapping_rules_v3.0.json")
        if not mapping_file.exists():
            result['errors'].append("매핑 규칙 파일 없음")
            return result
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_rules = json.load(f)
        
        field_mappings = mapping_rules.get('field_mappings', {})
        
        # 통합 테스트
        checks = {
            'test_data_created': len(test_data) > 0,
            'has_required_columns': all(col in test_data.columns for col in ['Case_No', 'Date', 'Location', 'Qty']),
            'mapping_coverage': len([col for col in test_data.columns if col in field_mappings]) / len(test_data.columns) >= 0.8,
            'data_types_valid': validate_data_types(test_data),
            'no_critical_nulls': test_data['Case_No'].notna().all()
        }
        
        result['details'] = checks
        result['success'] = all(checks.values())
        
        if not result['success']:
            failed_checks = [k for k, v in checks.items() if not v]
            result['errors'] = [f"실패한 검증: {', '.join(failed_checks)}"]
        
    except Exception as e:
        result['errors'].append(f"데이터 통합 테스트 중 오류: {str(e)}")
    
    return result

def test_ofco_mapping():
    """OFCO 매핑 테스트"""
    result = {
        'success': False,
        'details': {},
        'errors': []
    }
    
    try:
        # 매핑 규칙 로드
        mapping_file = Path("hvdc_integrated_mapping_rules_v3.0.json")
        if not mapping_file.exists():
            result['errors'].append("매핑 규칙 파일 없음")
            return result
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_rules = json.load(f)
        
        ofco_rules = mapping_rules.get('ofco_mapping_rules', {})
        
        # OFCO 테스트 텍스트
        test_texts = [
            "Berthing and Pilot Arrangement",
            "Cargo Clearance Service",
            "OFCO 10% Handling Fee",
            "Forklift charges",
            "Yard Storage Monthly Rental"
        ]
        
        mapping_rules_list = ofco_rules.get('mapping_rules', [])
        
        checks = {
            'has_mapping_rules': len(mapping_rules_list) > 0,
            'has_cost_centers': len(ofco_rules.get('cost_centers', {})) > 0,
            'rules_have_patterns': all('pattern' in rule for rule in mapping_rules_list),
            'rules_have_priorities': all('priority' in rule for rule in mapping_rules_list),
            'rules_have_cost_centers': all('cost_center_a' in rule and 'cost_center_b' in rule for rule in mapping_rules_list)
        }
        
        # 매핑 테스트
        matched_count = 0
        for text in test_texts:
            if find_matching_rule(text, mapping_rules_list):
                matched_count += 1
        
        checks['mapping_success_rate'] = matched_count / len(test_texts) >= 0.8
        
        result['details'] = checks
        result['details']['matched_texts'] = matched_count
        result['details']['total_test_texts'] = len(test_texts)
        
        result['success'] = all(checks.values())
        
        if not result['success']:
            failed_checks = [k for k, v in checks.items() if not v]
            result['errors'] = [f"실패한 검증: {', '.join(failed_checks)}"]
        
    except Exception as e:
        result['errors'].append(f"OFCO 매핑 테스트 중 오류: {str(e)}")
    
    return result

def create_test_dataset():
    """테스트 데이터셋 생성"""
    return pd.DataFrame({
        'Case_No': ['HVDC-TEST-001', 'HVDC-TEST-002', 'HVDC-TEST-003'],
        'Date': pd.to_datetime(['2024-01-15', '2024-01-16', '2024-01-17']),
        'Location': ['DSV Indoor', 'DSV Outdoor', 'AGI Site'],
        'Qty': [10, 20, 15],
        'Amount': [1000.0, 2000.0, 1500.0],
        'Category': ['HE', 'SIM', 'HE'],
        'Vendor': ['HITACHI', 'SIMENSE', 'HITACHI'],
        'Logistics Flow Code': [1, 2, 3],
        'wh handling': [0, 1, 2]
    })

def validate_data_types(df):
    """데이터 타입 검증"""
    try:
        # 기본 데이터 타입 검증
        checks = [
            str(df['Qty'].dtype) in ['int64', 'float64'],
            str(df['Amount'].dtype) in ['float64'],
            pd.api.types.is_datetime64_any_dtype(df['Date'])
        ]
        return bool(all(checks))
    except:
        return False

def find_matching_rule(text, rules):
    """매칭 규칙 찾기"""
    import re
    for rule in rules:
        pattern = rule.get('pattern', '')
        if pattern and re.search(pattern, text, re.IGNORECASE):
            return rule
    return None

def generate_test_summary(test_results):
    """테스트 요약 생성"""
    tests = test_results.get('tests', {})
    
    total_tests = len(tests)
    passed_tests = sum(1 for result in tests.values() if result.get('success', False))
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
        'test_details': {
            name: {
                'status': 'PASS' if result.get('success', False) else 'FAIL',
                'error_count': len(result.get('errors', []))
            }
            for name, result in tests.items()
        }
    }

def convert_to_json_serializable(obj):
    """JSON 직렬화 가능한 형태로 변환"""
    import numpy as np
    
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    elif isinstance(obj, (bool, int, float, str, type(None))):
        return obj
    else:
        return str(obj)

if __name__ == "__main__":
    test_results = test_integrated_ontology_system()
    
    # 성공률에 따른 종료 코드
    success_rate = test_results.get('summary', {}).get('success_rate', 0)
    if success_rate >= 80:
        print(f"\n🎉 테스트 성공! (성공률: {success_rate:.1f}%)")
        exit(0)
    else:
        print(f"\n❌ 테스트 실패! (성공률: {success_rate:.1f}%)")
        exit(1) 