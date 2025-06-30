#!/usr/bin/env python3
"""
HVDC 온톨로지 매핑 실행 예제
Excel 데이터를 RDF로 변환하는 완전한 가이드
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

def step1_load_mapping_rules():
    """1단계: 매핑 규칙 로드"""
    print("📋 1단계: 매핑 규칙 로드")
    
    try:
        with open('mapping_rules_v2.6.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        print("✅ 매핑 규칙 로드 성공")
        return rules
    except FileNotFoundError:
        print("❌ mapping_rules_v2.6.json 파일을 찾을 수 없습니다.")
        return None

def step2_prepare_sample_data():
    """2단계: 샘플 데이터 준비"""
    print("\n📊 2단계: 샘플 데이터 준비")
    
    # 샘플 Excel 데이터 생성
    sample_data = {
        'Case_No': ['HVDC-HE-001', 'HVDC-SIM-002', 'HVDC-HE-003'],
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Qty': [100, 200, 150],
        'Location': ['DSV Indoor', 'DSV Outdoor', 'MOSB'],
        'Vendor': ['HITACHI', 'SIM', 'HITACHI'],
        'Amount': [1000.0, 2000.0, 1500.0],
        'Handling Fee': [50.0, 100.0, 75.0]
    }
    
    df = pd.DataFrame(sample_data)
    print(f"✅ 샘플 데이터 생성: {len(df)}행")
    print(df.head())
    return df

def step3_apply_mapping(df, rules):
    """3단계: 매핑 규칙 적용"""
    print("\n🔄 3단계: 매핑 규칙 적용")
    
    if not rules:
        print("❌ 매핑 규칙이 없습니다.")
        return None
    
    # 필드 매핑 적용
    field_map = rules.get('field_map', {})
    mapped_data = []
    
    for idx, row in df.iterrows():
        event = {}
        for excel_col, rdf_prop in field_map.items():
            if excel_col in row and pd.notna(row[excel_col]):
                event[rdf_prop] = row[excel_col]
        
        # 창고 분류 추가
        location = row.get('Location', '')
        warehouse_class = get_warehouse_class(location, rules)
        event['warehouse_class'] = warehouse_class
        
        mapped_data.append(event)
    
    print(f"✅ 매핑 완료: {len(mapped_data)}개 이벤트")
    return mapped_data

def get_warehouse_class(location, rules):
    """창고 분류 결정"""
    warehouse_classification = rules.get('warehouse_classification', {})
    
    for storage_type, warehouses in warehouse_classification.items():
        if location in warehouses:
            if storage_type == 'Indoor':
                return 'IndoorWarehouse'
            elif storage_type == 'Outdoor':
                return 'OutdoorWarehouse'
            elif storage_type == 'Site':
                return 'Site'
            elif storage_type == 'dangerous_cargo':
                return 'DangerousCargoWarehouse'
    
    return 'Warehouse'  # 기본값

def step4_generate_rdf(mapped_data, rules):
    """4단계: RDF/TTL 생성"""
    print("\n🔗 4단계: RDF/TTL 생성")
    
    if not mapped_data or not rules:
        print("❌ 매핑된 데이터 또는 규칙이 없습니다.")
        return None
    
    namespace = rules.get('namespace', 'http://samsung.com/project-logistics#')
    
    # TTL 헤더
    ttl_content = f"""# HVDC Warehouse Ontology RDF
# Generated: {datetime.now().isoformat()}

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <{namespace}> .

"""
    
    # 이벤트 데이터 변환
    for idx, event in enumerate(mapped_data, 1):
        event_id = f"TransportEvent_{idx:05d}"
        ttl_content += f"ex:{event_id} a ex:TransportEvent ;\n"
        
        for prop, value in event.items():
            if prop == 'warehouse_class':
                continue
                
            # 데이터 타입 결정
            if prop in ['hasQuantity']:
                ttl_content += f'    ex:{prop} "{value}"^^xsd:integer ;\n'
            elif prop in ['hasAmount', 'hasHandlingFee']:
                ttl_content += f'    ex:{prop} "{value}"^^xsd:decimal ;\n'
            elif prop in ['hasDate']:
                ttl_content += f'    ex:{prop} "{value}"^^xsd:date ;\n'
            else:
                ttl_content += f'    ex:{prop} "{value}" ;\n'
        
        ttl_content = ttl_content.rstrip(';\n') + ' .\n\n'
    
    # 창고 인스턴스 추가
    warehouse_classification = rules.get('warehouse_classification', {})
    for storage_type, warehouses in warehouse_classification.items():
        for warehouse in warehouses:
            warehouse_id = warehouse.replace(' ', '_')
            
            if storage_type == 'Indoor':
                class_type = 'IndoorWarehouse'
            elif storage_type == 'Outdoor':
                class_type = 'OutdoorWarehouse'
            elif storage_type == 'Site':
                class_type = 'Site'
            elif storage_type == 'dangerous_cargo':
                class_type = 'DangerousCargoWarehouse'
            else:
                class_type = 'Warehouse'
            
            ttl_content += f"""ex:{warehouse_id} a ex:{class_type} ;
    rdfs:label "{warehouse}" ;
    ex:hasStorageType "{storage_type}" .

"""
    
    return ttl_content

def step5_generate_sparql_queries(rules):
    """5단계: SPARQL 쿼리 생성"""
    print("\n🔍 5단계: SPARQL 쿼리 생성")
    
    if not rules:
        print("❌ 매핑 규칙이 없습니다.")
        return None
    
    namespace = rules.get('namespace', 'http://samsung.com/project-logistics#')
    
    queries = f"""# HVDC 온톨로지 SPARQL 쿼리 모음
# Generated: {datetime.now().isoformat()}

# 1. 월별 창고별 집계
PREFIX ex: <{namespace}>
SELECT ?month ?warehouse (SUM(?amount) AS ?totalAmount) (SUM(?qty) AS ?totalQty)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasLocation ?warehouse ;
           ex:hasDate ?date ;
           ex:hasAmount ?amount ;
           ex:hasQuantity ?qty .
    BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
}}
GROUP BY ?month ?warehouse
ORDER BY ?month ?warehouse

# 2. 벤더별 분석
PREFIX ex: <{namespace}>
SELECT ?vendor (SUM(?amount) AS ?totalAmount) (COUNT(?event) AS ?eventCount)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasVendor ?vendor ;
           ex:hasAmount ?amount .
}}
GROUP BY ?vendor
ORDER BY DESC(?totalAmount)

# 3. 창고 타입별 재고 현황
PREFIX ex: <{namespace}>
SELECT ?storageType ?warehouse (SUM(?qty) AS ?totalQty)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasLocation ?warehouse ;
           ex:hasQuantity ?qty .
    ?warehouse ex:hasStorageType ?storageType .
}}
GROUP BY ?storageType ?warehouse
ORDER BY ?storageType ?warehouse

# 4. Handling Fee 분석
PREFIX ex: <{namespace}>
SELECT ?warehouse (AVG(?handlingFee) AS ?avgHandlingFee) (SUM(?handlingFee) AS ?totalHandlingFee)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasLocation ?warehouse ;
           ex:hasHandlingFee ?handlingFee .
}}
GROUP BY ?warehouse
ORDER BY DESC(?totalHandlingFee)
"""
    
    return queries

def step6_save_outputs(ttl_content, sparql_queries):
    """6단계: 결과 파일 저장"""
    print("\n💾 6단계: 결과 파일 저장")
    
    # 출력 디렉토리 생성
    output_dir = Path('rdf_output')
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # TTL 파일 저장
    if ttl_content:
        ttl_file = output_dir / f'hvdc_ontology_{timestamp}.ttl'
        with open(ttl_file, 'w', encoding='utf-8') as f:
            f.write(ttl_content)
        print(f"✅ RDF/TTL 저장: {ttl_file}")
    
    # SPARQL 쿼리 저장
    if sparql_queries:
        sparql_file = output_dir / f'hvdc_queries_{timestamp}.sparql'
        with open(sparql_file, 'w', encoding='utf-8') as f:
            f.write(sparql_queries)
        print(f"✅ SPARQL 쿼리 저장: {sparql_file}")
    
    return ttl_file, sparql_file

def main():
    """메인 실행 함수"""
    print("🚀 HVDC 온톨로지 매핑 실행 예제")
    print("=" * 50)
    
    # 단계별 실행
    rules = step1_load_mapping_rules()
    df = step2_prepare_sample_data()
    mapped_data = step3_apply_mapping(df, rules)
    ttl_content = step4_generate_rdf(mapped_data, rules)
    sparql_queries = step5_generate_sparql_queries(rules)
    
    if ttl_content and sparql_queries:
        ttl_file, sparql_file = step6_save_outputs(ttl_content, sparql_queries)
        
        print("\n🎉 온톨로지 매핑 완료!")
        print("=" * 50)
        print("📁 생성된 파일:")
        print(f"   • RDF/TTL: {ttl_file}")
        print(f"   • SPARQL: {sparql_file}")
        print("\n🔧 추천 명령어:")
        print("   /cmd_ontology_query [온톨로지 쿼리 실행]")
        print("   /cmd_rdf_validate [RDF 검증]")
        print("   /cmd_sparql_test [SPARQL 테스트]")
    else:
        print("\n❌ 온톨로지 매핑 실패")

if __name__ == "__main__":
    main() 