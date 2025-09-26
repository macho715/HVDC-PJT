#!/usr/bin/env python3
"""
HVDC 온톨로지 통합 시스템 실제 사용 데모 v3.0.0
- 실제 데이터로 시스템 동작 검증
- MACHO-GPT v3.4-mini 표준 준수
- 완전 통합 온톨로지 시스템 시연
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """온톨로지 통합 시스템 실제 사용 데모"""
    print("🔌 HVDC 온톨로지 통합 시스템 실제 사용 데모 v3.0.0")
    print("=" * 70)
    
    demo_results = {
        'timestamp': datetime.now().isoformat(),
        'system_version': '3.0.0',
        'demos': {},
        'summary': {}
    }
    
    # 1. 매핑 규칙 시스템 데모
    print("\n📋 1. 매핑 규칙 시스템 데모")
    mapping_demo = demo_mapping_rules()
    demo_results['demos']['mapping_rules'] = mapping_demo
    
    # 2. 온톨로지 스키마 데모
    print("\n🏗️ 2. 온톨로지 스키마 데모")
    schema_demo = demo_ontology_schema()
    demo_results['demos']['ontology_schema'] = schema_demo
    
    # 3. OFCO 매핑 데모
    print("\n💰 3. OFCO 매핑 데모")
    ofco_demo = demo_ofco_mapping()
    demo_results['demos']['ofco_mapping'] = ofco_demo
    
    # 4. 데이터 처리 파이프라인 데모
    print("\n🔄 4. 데이터 처리 파이프라인 데모")
    pipeline_demo = demo_data_pipeline()
    demo_results['demos']['data_pipeline'] = pipeline_demo
    
    # 5. SPARQL 쿼리 데모
    print("\n🔍 5. SPARQL 쿼리 데모")
    sparql_demo = demo_sparql_queries()
    demo_results['demos']['sparql_queries'] = sparql_demo
    
    # 6. 통합 요약
    print("\n📊 6. 통합 요약")
    summary = generate_demo_summary(demo_results)
    demo_results['summary'] = summary
    
    # 결과 저장
    save_demo_results(demo_results)
    
    print(f"\n🎉 데모 완료! 총 {len(demo_results['demos'])}개 데모 실행")
    print(f"   📄 결과 파일: hvdc_ontology_demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    return demo_results

def demo_mapping_rules():
    """매핑 규칙 시스템 데모"""
    print("   🔄 매핑 규칙 로드 중...")
    
    try:
        # 매핑 규칙 로드
        mapping_file = Path("hvdc_integrated_mapping_rules_v3.0.json")
        if not mapping_file.exists():
            return {'success': False, 'error': '매핑 규칙 파일 없음'}
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_rules = json.load(f)
        
        field_mappings = mapping_rules.get('field_mappings', {})
        property_mappings = mapping_rules.get('property_mappings', {})
        
        # 주요 매핑 예시
        key_mappings = {
            'Case_No': field_mappings.get('Case_No', 'N/A'),
            'Date': field_mappings.get('Date', 'N/A'),
            'Location': field_mappings.get('Location', 'N/A'),
            'Qty': field_mappings.get('Qty', 'N/A'),
            'Amount': field_mappings.get('Amount', 'N/A')
        }
        
        print("   ✅ 핵심 필드 매핑:")
        for field, predicate in key_mappings.items():
            print(f"      {field} → {predicate}")
        
        # 속성 매핑 정보
        required_fields = [
            field for field, props in property_mappings.items()
            if props.get('required', False)
        ]
        
        print(f"   ✅ 필수 필드: {len(required_fields)}개")
        print(f"   ✅ 전체 매핑: {len(field_mappings)}개")
        
        return {
            'success': True,
            'field_mappings_count': len(field_mappings),
            'property_mappings_count': len(property_mappings),
            'required_fields_count': len(required_fields),
            'key_mappings': key_mappings
        }
        
    except Exception as e:
        logger.error(f"매핑 규칙 데모 실패: {e}")
        return {'success': False, 'error': str(e)}

def demo_ontology_schema():
    """온톨로지 스키마 데모"""
    print("   🏗️ 온톨로지 스키마 분석 중...")
    
    try:
        schema_file = Path("hvdc_integrated_ontology_schema.ttl")
        if not schema_file.exists():
            return {'success': False, 'error': '스키마 파일 없음'}
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        # 스키마 구성 요소 분석
        components = {
            'classes': schema_content.count('a owl:Class'),
            'properties': schema_content.count('a owl:DatatypeProperty') + schema_content.count('a owl:ObjectProperty'),
            'korean_labels': schema_content.count('@ko'),
            'hierarchy_relations': schema_content.count('rdfs:subClassOf'),
            'instances': schema_content.count('a ex:')
        }
        
        print("   ✅ 스키마 구성 요소:")
        for component, count in components.items():
            print(f"      {component}: {count}개")
        
        # 핵심 클래스 확인
        key_classes = [
            'TransportEvent', 'Warehouse', 'Site', 'Invoice', 
            'Case', 'StockSnapshot', 'CostCenter'
        ]
        
        found_classes = []
        for cls in key_classes:
            if f'ex:{cls}' in schema_content:
                found_classes.append(cls)
        
        print(f"   ✅ 핵심 클래스: {len(found_classes)}/{len(key_classes)}개 확인")
        
        return {
            'success': True,
            'schema_components': components,
            'key_classes_found': len(found_classes),
            'key_classes_total': len(key_classes),
            'found_classes': found_classes
        }
        
    except Exception as e:
        logger.error(f"온톨로지 스키마 데모 실패: {e}")
        return {'success': False, 'error': str(e)}

def demo_ofco_mapping():
    """OFCO 매핑 데모"""
    print("   💰 OFCO 매핑 규칙 시연 중...")
    
    try:
        # 매핑 규칙 로드
        mapping_file = Path("hvdc_integrated_mapping_rules_v3.0.json")
        if not mapping_file.exists():
            return {'success': False, 'error': '매핑 규칙 파일 없음'}
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_rules = json.load(f)
        
        ofco_rules = mapping_rules.get('ofco_mapping_rules', {})
        cost_centers = ofco_rules.get('cost_centers', {})
        mapping_rules_list = ofco_rules.get('mapping_rules', [])
        
        # 테스트 텍스트로 매핑 시연
        test_invoices = [
            "Berthing and Pilot Arrangement - Port Services",
            "Cargo Clearance and Documentation",
            "OFCO 10% Handling Fee for Container",
            "Forklift Operation Charges",
            "Yard Storage Monthly Rental Fee",
            "MGO Fuel Supply for Vessel",
            "Fresh Water Supply Services",
            "Port Transit Channel Charges"
        ]
        
        print("   ✅ OFCO 매핑 시연:")
        mapped_count = 0
        
        for invoice_text in test_invoices:
            matched_rule = find_best_ofco_match(invoice_text, mapping_rules_list)
            if matched_rule:
                cost_center = matched_rule.get('cost_center_a', 'N/A')
                print(f"      '{invoice_text[:30]}...' → {cost_center}")
                mapped_count += 1
            else:
                print(f"      '{invoice_text[:30]}...' → 매핑 실패")
        
        print(f"   ✅ 매핑 성공률: {mapped_count}/{len(test_invoices)} ({mapped_count/len(test_invoices)*100:.1f}%)")
        print(f"   ✅ 비용 센터: {len(cost_centers)}개")
        print(f"   ✅ 매핑 규칙: {len(mapping_rules_list)}개")
        
        return {
            'success': True,
            'cost_centers_count': len(cost_centers),
            'mapping_rules_count': len(mapping_rules_list),
            'test_invoices_count': len(test_invoices),
            'mapped_count': mapped_count,
            'success_rate': mapped_count / len(test_invoices) * 100
        }
        
    except Exception as e:
        logger.error(f"OFCO 매핑 데모 실패: {e}")
        return {'success': False, 'error': str(e)}

def demo_data_pipeline():
    """데이터 처리 파이프라인 데모"""
    print("   🔄 데이터 처리 파이프라인 시연 중...")
    
    try:
        # 샘플 데이터 생성
        sample_data = pd.DataFrame({
            'Case_No': ['HVDC-DEMO-001', 'HVDC-DEMO-002', 'HVDC-DEMO-003'],
            'Date': pd.to_datetime(['2024-01-15', '2024-01-16', '2024-01-17']),
            'Location': ['DSV Indoor', 'DSV Outdoor', 'AGI Site'],
            'Qty': [10, 20, 15],
            'Amount': [1000.0, 2000.0, 1500.0],
            'Category': ['HE', 'SIM', 'HE'],
            'Vendor': ['HITACHI', 'SIMENSE', 'HITACHI'],
            'Logistics Flow Code': [1, 2, 3],
            'wh handling': [0, 1, 2],
            'pkg': [1, 2, 1],
            'Status_Location_Date': pd.to_datetime(['2024-01-15', None, '2024-01-17']),
            'Stack_Status': ['STACKED', None, 'READY']
        })
        
        print("   ✅ 샘플 데이터 생성:")
        print(f"      행: {len(sample_data)}")
        print(f"      열: {len(sample_data.columns)}")
        
        # 데이터 정규화 시연
        original_data = sample_data.copy()
        
        # 1. NULL PKG 보정
        sample_data['pkg'] = sample_data['pkg'].fillna(1)
        
        # 2. Flow Code 정규화 (6 → 3)
        sample_data.loc[sample_data['Logistics Flow Code'] == 6, 'Logistics Flow Code'] = 3
        
        # 3. 벤더 정규화
        vendor_mapping = {'SIMENSE': 'SIM', 'HITACHI': 'HE'}
        sample_data['Vendor'] = sample_data['Vendor'].map(vendor_mapping).fillna(sample_data['Vendor'])
        
        # 4. 결측값 처리
        null_status_location = sample_data['Status_Location_Date'].isna().sum()
        null_stack_status = sample_data['Stack_Status'].isna().sum()
        
        print("   ✅ 데이터 정규화 완료:")
        print(f"      NULL Status_Location_Date: {null_status_location}개")
        print(f"      NULL Stack_Status: {null_stack_status}개")
        print(f"      벤더 정규화: SIMENSE → SIM, HITACHI → HE")
        
        # 5. 온톨로지 매핑 시연
        mapping_file = Path("hvdc_integrated_mapping_rules_v3.0.json")
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_rules = json.load(f)
            
            field_mappings = mapping_rules.get('field_mappings', {})
            mapped_fields = []
            
            for col in sample_data.columns:
                if col in field_mappings:
                    mapped_fields.append(col)
            
            print(f"   ✅ 온톨로지 매핑: {len(mapped_fields)}/{len(sample_data.columns)}개 필드")
        
        return {
            'success': True,
            'sample_data_rows': len(sample_data),
            'sample_data_columns': len(sample_data.columns),
            'null_status_location_date': null_status_location,
            'null_stack_status': null_stack_status,
            'mapped_fields': len(mapped_fields) if 'mapped_fields' in locals() else 0
        }
        
    except Exception as e:
        logger.error(f"데이터 파이프라인 데모 실패: {e}")
        return {'success': False, 'error': str(e)}

def demo_sparql_queries():
    """SPARQL 쿼리 데모"""
    print("   🔍 SPARQL 쿼리 시연 중...")
    
    try:
        # 매핑 규칙에서 SPARQL 템플릿 로드
        mapping_file = Path("hvdc_integrated_mapping_rules_v3.0.json")
        if not mapping_file.exists():
            return {'success': False, 'error': '매핑 규칙 파일 없음'}
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_rules = json.load(f)
        
        sparql_templates = mapping_rules.get('sparql_templates', {})
        
        # 기본 쿼리 템플릿 시연
        basic_queries = sparql_templates.get('basic_queries', {})
        advanced_queries = sparql_templates.get('advanced_queries', {})
        
        print("   ✅ SPARQL 쿼리 템플릿:")
        print(f"      기본 쿼리: {len(basic_queries)}개")
        print(f"      고급 쿼리: {len(advanced_queries)}개")
        
        # 샘플 쿼리 생성
        namespace = mapping_rules.get('namespace', 'http://samsung.com/project-logistics#')
        
        sample_queries = {}
        
        # 월별 요약 쿼리
        monthly_summary_query = f"""
        PREFIX ex: <{namespace}>
        SELECT ?month ?warehouse (COUNT(?event) AS ?eventCount) (SUM(?amount) AS ?totalAmount)
        WHERE {{
          ?event rdf:type ex:TransportEvent ;
                 ex:hasDate ?date ;
                 ex:hasLocation ?warehouse ;
                 ex:hasAmount ?amount .
          BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
        }}
        GROUP BY ?month ?warehouse
        ORDER BY ?month ?warehouse
        """
        
        sample_queries['monthly_summary'] = monthly_summary_query
        
        # 창고별 통계 쿼리
        warehouse_stats_query = f"""
        PREFIX ex: <{namespace}>
        SELECT ?warehouse (COUNT(?event) AS ?totalEvents) (AVG(?quantity) AS ?avgQuantity)
        WHERE {{
          ?event rdf:type ex:TransportEvent ;
                 ex:hasLocation ?warehouse ;
                 ex:hasQuantity ?quantity .
        }}
        GROUP BY ?warehouse
        ORDER BY DESC(?totalEvents)
        """
        
        sample_queries['warehouse_statistics'] = warehouse_stats_query
        
        print("   ✅ 생성된 샘플 쿼리:")
        for query_name, query in sample_queries.items():
            print(f"      {query_name}: {len(query.split('\\n'))}줄")
        
        return {
            'success': True,
            'basic_queries_count': len(basic_queries),
            'advanced_queries_count': len(advanced_queries),
            'sample_queries_count': len(sample_queries),
            'namespace': namespace
        }
        
    except Exception as e:
        logger.error(f"SPARQL 쿼리 데모 실패: {e}")
        return {'success': False, 'error': str(e)}

def find_best_ofco_match(text, rules):
    """OFCO 매핑 규칙에서 최적 매치 찾기"""
    import re
    
    best_match = None
    best_priority = float('inf')
    
    for rule in rules:
        pattern = rule.get('pattern', '')
        priority = rule.get('priority', 999)
        
        if pattern and re.search(pattern, text, re.IGNORECASE):
            if priority < best_priority:
                best_priority = priority
                best_match = rule
    
    return best_match

def generate_demo_summary(demo_results):
    """데모 요약 생성"""
    demos = demo_results.get('demos', {})
    
    total_demos = len(demos)
    successful_demos = sum(1 for demo in demos.values() if demo.get('success', False))
    
    return {
        'total_demos': total_demos,
        'successful_demos': successful_demos,
        'failed_demos': total_demos - successful_demos,
        'success_rate': (successful_demos / total_demos * 100) if total_demos > 0 else 0,
        'demo_details': {
            name: {
                'status': 'SUCCESS' if demo.get('success', False) else 'FAILED',
                'has_error': 'error' in demo
            }
            for name, demo in demos.items()
        }
    }

def save_demo_results(demo_results):
    """데모 결과 저장"""
    try:
        output_file = f"hvdc_ontology_demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(demo_results, f, ensure_ascii=False, indent=2)
        
        print(f"   💾 데모 결과 저장: {output_file}")
        
    except Exception as e:
        logger.error(f"데모 결과 저장 실패: {e}")

if __name__ == "__main__":
    demo_results = main()
    
    # 성공률에 따른 종료
    success_rate = demo_results.get('summary', {}).get('success_rate', 0)
    if success_rate >= 80:
        print(f"✅ 데모 성공! (성공률: {success_rate:.1f}%)")
        exit(0)
    else:
        print(f"❌ 데모 실패! (성공률: {success_rate:.1f}%)")
        exit(1) 