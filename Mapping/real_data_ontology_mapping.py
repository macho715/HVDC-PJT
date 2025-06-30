#!/usr/bin/env python3
"""
실제 HVDC 데이터를 사용한 온톨로지 매핑
data 폴더의 Excel 파일들을 RDF로 변환
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_real_data():
    """실제 데이터 파일 로드"""
    print("📊 실제 데이터 파일 로드 중...")
    
    data_files = {
        'HITACHI': 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
        'SIMENSE': 'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx',
        'INVOICE': 'data/HVDC WAREHOUSE_INVOICE.xlsx'
    }
    
    loaded_data = {}
    
    for name, file_path in data_files.items():
        try:
            print(f"📋 {name} 파일 로드 중: {file_path}")
            df = pd.read_excel(file_path)
            loaded_data[name] = df
            print(f"✅ {name}: {len(df)}행 로드 완료")
            print(f"   컬럼: {list(df.columns)[:5]}...")  # 처음 5개 컬럼만 표시
        except Exception as e:
            print(f"❌ {name} 파일 로드 실패: {e}")
            continue
    
    return loaded_data

def analyze_data_structure(loaded_data):
    """데이터 구조 분석"""
    print("\n🔍 데이터 구조 분석")
    print("=" * 50)
    
    for name, df in loaded_data.items():
        print(f"\n📋 {name} 데이터 분석:")
        print(f"   행 수: {len(df)}")
        print(f"   컬럼 수: {len(df.columns)}")
        print(f"   컬럼 목록:")
        for i, col in enumerate(df.columns):
            print(f"     {i+1:2d}. {col}")
        
        # 샘플 데이터 표시
        print(f"   샘플 데이터 (처음 3행):")
        print(df.head(3).to_string(max_cols=5))
        print("-" * 30)

def load_mapping_rules():
    """매핑 규칙 로드"""
    try:
        with open('mapping_rules_v2.6.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        print("✅ 매핑 규칙 로드 성공")
        return rules
    except FileNotFoundError:
        print("❌ mapping_rules_v2.6.json 파일을 찾을 수 없습니다.")
        return None

def map_columns_to_ontology(df, rules, data_source):
    """컬럼을 온톨로지로 매핑"""
    if not rules:
        return df
    
    field_map = rules.get('field_map', {})
    
    # 컬럼명 매핑
    mapped_columns = {}
    for col in df.columns:
        # 정확한 매칭 시도
        if col in field_map:
            mapped_columns[col] = field_map[col]
        # 부분 매칭 시도 (대소문자 무시)
        else:
            for excel_col, rdf_prop in field_map.items():
                if col.lower().replace(' ', '').replace('_', '') == excel_col.lower().replace(' ', '').replace('_', ''):
                    mapped_columns[col] = rdf_prop
                    break
    
    print(f"📋 {data_source} 컬럼 매핑 결과:")
    for original, mapped in mapped_columns.items():
        print(f"   {original} → {mapped}")
    
    return mapped_columns

def convert_to_rdf(loaded_data, rules):
    """실제 데이터를 RDF로 변환"""
    print("\n🔗 실제 데이터를 RDF로 변환 중...")
    
    if not rules:
        print("❌ 매핑 규칙이 없습니다.")
        return None
    
    namespace = rules.get('namespace', 'http://samsung.com/project-logistics#')
    
    # TTL 헤더
    ttl_content = f"""# HVDC Real Data Ontology RDF
# Generated: {datetime.now().isoformat()}
# Source: HITACHI, SIMENSE, INVOICE Excel files

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ex: <{namespace}> .

# Ontology Declaration
ex: a owl:Ontology ;
    rdfs:label "HVDC Real Data Warehouse Ontology" ;
    rdfs:comment "Real warehouse data from HITACHI, SIMENSE, INVOICE" ;
    owl:versionInfo "2.6" .

"""
    
    event_counter = 1
    
    # 각 데이터셋 처리
    for data_source, df in loaded_data.items():
        print(f"🔄 {data_source} 데이터 처리 중... ({len(df)}행)")
        
        # 컬럼 매핑
        column_mapping = map_columns_to_ontology(df, rules, data_source)
        
        # 상위 100행만 처리 (테스트용)
        sample_df = df.head(100)
        
        for idx, row in sample_df.iterrows():
            event_id = f"TransportEvent_{event_counter:05d}"
            ttl_content += f"ex:{event_id} a ex:TransportEvent ;\n"
            ttl_content += f"    ex:hasDataSource \"{data_source}\" ;\n"
            
            # 매핑된 컬럼들 처리
            for original_col, rdf_prop in column_mapping.items():
                if original_col in row and pd.notna(row[original_col]):
                    value = row[original_col]
                    
                    # 데이터 타입에 따른 처리
                    if rdf_prop in ['hasQuantity', 'hasPackageCount']:
                        try:
                            int_value = int(float(str(value)))
                            ttl_content += f'    ex:{rdf_prop} "{int_value}"^^xsd:integer ;\n'
                        except:
                            continue
                    elif rdf_prop in ['hasAmount', 'hasTotalAmount', 'hasHandlingFee', 'hasCBM', 'hasWeight']:
                        try:
                            float_value = float(str(value))
                            ttl_content += f'    ex:{rdf_prop} "{float_value}"^^xsd:decimal ;\n'
                        except:
                            continue
                    elif rdf_prop in ['hasDate', 'hasStartDate', 'hasFinishDate', 'hasOperationMonth']:
                        try:
                            if isinstance(value, pd.Timestamp):
                                date_str = value.strftime('%Y-%m-%d')
                            else:
                                date_str = str(value)
                            ttl_content += f'    ex:{rdf_prop} "{date_str}"^^xsd:date ;\n'
                        except:
                            continue
                    else:
                        # 문자열 처리
                        clean_value = str(value).replace('"', '\\"').replace('\n', ' ').strip()
                        if clean_value:
                            ttl_content += f'    ex:{rdf_prop} "{clean_value}" ;\n'
            
            ttl_content = ttl_content.rstrip(';\n') + ' .\n\n'
            event_counter += 1
    
    # 창고 인스턴스 추가
    warehouse_classification = rules.get('warehouse_classification', {})
    for storage_type, warehouses in warehouse_classification.items():
        for warehouse in warehouses:
            warehouse_id = warehouse.replace(' ', '_').replace('(', '').replace(')', '')
            
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

def generate_real_data_sparql(rules):
    """실제 데이터용 SPARQL 쿼리 생성"""
    print("🔍 실제 데이터용 SPARQL 쿼리 생성 중...")
    
    if not rules:
        return None
    
    namespace = rules.get('namespace', 'http://samsung.com/project-logistics#')
    
    queries = f"""# HVDC 실제 데이터 SPARQL 쿼리 모음
# Generated: {datetime.now().isoformat()}

# 1. 데이터 소스별 집계
PREFIX ex: <{namespace}>
SELECT ?dataSource (COUNT(?event) AS ?eventCount) (SUM(?amount) AS ?totalAmount)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasDataSource ?dataSource .
    OPTIONAL {{ ?event ex:hasAmount ?amount }}
}}
GROUP BY ?dataSource
ORDER BY DESC(?eventCount)

# 2. 월별 트랜잭션 분석
PREFIX ex: <{namespace}>
SELECT ?month ?dataSource (COUNT(?event) AS ?eventCount)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasDataSource ?dataSource ;
           ex:hasDate ?date .
    BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
}}
GROUP BY ?month ?dataSource
ORDER BY ?month ?dataSource

# 3. 창고별 재고 현황
PREFIX ex: <{namespace}>
SELECT ?location (COUNT(?event) AS ?eventCount) (SUM(?qty) AS ?totalQty)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasLocation ?location .
    OPTIONAL {{ ?event ex:hasQuantity ?qty }}
}}
GROUP BY ?location
ORDER BY DESC(?eventCount)

# 4. 벤더별 분석 (HITACHI vs SIMENSE)
PREFIX ex: <{namespace}>
SELECT ?vendor (COUNT(?event) AS ?eventCount) (SUM(?amount) AS ?totalAmount)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasVendor ?vendor .
    OPTIONAL {{ ?event ex:hasAmount ?amount }}
}}
GROUP BY ?vendor
ORDER BY DESC(?totalAmount)

# 5. 케이스별 상세 정보
PREFIX ex: <{namespace}>
SELECT ?case ?dataSource ?location ?qty ?amount
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasCase ?case ;
           ex:hasDataSource ?dataSource .
    OPTIONAL {{ ?event ex:hasLocation ?location }}
    OPTIONAL {{ ?event ex:hasQuantity ?qty }}
    OPTIONAL {{ ?event ex:hasAmount ?amount }}
}}
ORDER BY ?case
LIMIT 20

# 6. 하역비 분석
PREFIX ex: <{namespace}>
SELECT ?location (AVG(?handlingFee) AS ?avgHandlingFee) (SUM(?handlingFee) AS ?totalHandlingFee)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasLocation ?location ;
           ex:hasHandlingFee ?handlingFee .
}}
GROUP BY ?location
ORDER BY DESC(?totalHandlingFee)
"""
    
    return queries

def save_real_data_outputs(ttl_content, sparql_queries):
    """실제 데이터 결과 저장"""
    print("\n💾 실제 데이터 결과 저장 중...")
    
    # 출력 디렉토리 생성
    output_dir = Path('rdf_output')
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    files_created = []
    
    # TTL 파일 저장
    if ttl_content:
        ttl_file = output_dir / f'hvdc_real_data_{timestamp}.ttl'
        with open(ttl_file, 'w', encoding='utf-8') as f:
            f.write(ttl_content)
        print(f"✅ 실제 데이터 RDF/TTL 저장: {ttl_file}")
        files_created.append(('RDF/TTL', ttl_file))
    
    # SPARQL 쿼리 저장
    if sparql_queries:
        sparql_file = output_dir / f'hvdc_real_queries_{timestamp}.sparql'
        with open(sparql_file, 'w', encoding='utf-8') as f:
            f.write(sparql_queries)
        print(f"✅ 실제 데이터 SPARQL 쿼리 저장: {sparql_file}")
        files_created.append(('SPARQL', sparql_file))
    
    return files_created

def main():
    """메인 실행 함수"""
    print("🚀 HVDC 실제 데이터 온톨로지 매핑")
    print("=" * 60)
    
    # 1단계: 실제 데이터 로드
    loaded_data = load_real_data()
    
    if not loaded_data:
        print("❌ 데이터 파일을 로드할 수 없습니다.")
        return
    
    # 2단계: 데이터 구조 분석
    analyze_data_structure(loaded_data)
    
    # 3단계: 매핑 규칙 로드
    rules = load_mapping_rules()
    
    # 4단계: RDF 변환
    ttl_content = convert_to_rdf(loaded_data, rules)
    
    # 5단계: SPARQL 쿼리 생성
    sparql_queries = generate_real_data_sparql(rules)
    
    # 6단계: 결과 저장
    if ttl_content and sparql_queries:
        files_created = save_real_data_outputs(ttl_content, sparql_queries)
        
        print("\n🎉 실제 데이터 온톨로지 매핑 완료!")
        print("=" * 60)
        print("📊 처리 통계:")
        for name, df in loaded_data.items():
            print(f"   • {name}: {len(df)}행 → 상위 100행 변환")
        
        print("\n📁 생성된 파일:")
        for file_type, file_path in files_created:
            print(f"   • {file_type}: {file_path}")
        
        print("\n🔧 추천 명령어:")
        print("   /cmd_real_data_query [실제 데이터 쿼리 실행]")
        print("   /cmd_data_validation [데이터 검증]")
        print("   /cmd_warehouse_analysis [창고 분석]")
    else:
        print("\n❌ 실제 데이터 온톨로지 매핑 실패")

if __name__ == "__main__":
    main() 