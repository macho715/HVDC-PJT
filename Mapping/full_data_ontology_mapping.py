#!/usr/bin/env python3
"""
HVDC 전체 데이터 온톨로지 매핑 (8,000+행)
/cmd_full_data_mapping 명령어 구현
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import logging
import time
from tqdm import tqdm

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_full_data():
    """전체 실제 데이터 파일 로드"""
    print("🚀 /cmd_full_data_mapping 실행 중...")
    print("📊 전체 실제 데이터 파일 로드 중...")
    
    data_files = {
        'HITACHI': 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
        'SIMENSE': 'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx',
        'INVOICE': 'data/HVDC WAREHOUSE_INVOICE.xlsx'
    }
    
    loaded_data = {}
    total_rows = 0
    
    for name, file_path in data_files.items():
        try:
            print(f"📋 {name} 파일 로드 중: {file_path}")
            start_time = time.time()
            df = pd.read_excel(file_path)
            load_time = time.time() - start_time
            
            loaded_data[name] = df
            total_rows += len(df)
            
            print(f"✅ {name}: {len(df):,}행 로드 완료 ({load_time:.2f}초)")
            print(f"   메모리 사용량: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB")
            
        except Exception as e:
            print(f"❌ {name} 파일 로드 실패: {e}")
            continue
    
    print(f"\n📈 전체 데이터 로드 완료: {total_rows:,}행")
    return loaded_data

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

def analyze_full_data_structure(loaded_data):
    """전체 데이터 구조 상세 분석"""
    print("\n🔍 전체 데이터 구조 상세 분석")
    print("=" * 60)
    
    total_rows = 0
    total_cols = 0
    
    for name, df in loaded_data.items():
        print(f"\n📋 {name} 데이터 상세 분석:")
        print(f"   📊 행 수: {len(df):,}")
        print(f"   📊 컬럼 수: {len(df.columns)}")
        print(f"   📊 메모리 사용량: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB")
        
        # 데이터 타입 분석
        numeric_cols = df.select_dtypes(include=['number']).columns
        date_cols = df.select_dtypes(include=['datetime']).columns
        text_cols = df.select_dtypes(include=['object']).columns
        
        print(f"   📊 숫자형 컬럼: {len(numeric_cols)}개")
        print(f"   📊 날짜형 컬럼: {len(date_cols)}개")
        print(f"   📊 텍스트형 컬럼: {len(text_cols)}개")
        
        # 결측값 분석
        missing_data = df.isnull().sum()
        missing_cols = missing_data[missing_data > 0]
        print(f"   📊 결측값 있는 컬럼: {len(missing_cols)}개")
        
        # 고유값 분석
        unique_counts = df.nunique()
        high_cardinality = unique_counts[unique_counts > 1000]
        print(f"   📊 고유값 1000+ 컬럼: {len(high_cardinality)}개")
        
        total_rows += len(df)
        total_cols += len(df.columns)
        
        print("-" * 40)
    
    print(f"\n📈 전체 통계:")
    print(f"   📊 총 행 수: {total_rows:,}")
    print(f"   📊 총 컬럼 수: {total_cols}")
    print(f"   📊 평균 행/파일: {total_rows/len(loaded_data):,.0f}")

def map_columns_to_ontology_full(df, rules, data_source):
    """전체 데이터용 컬럼 온톨로지 매핑"""
    if not rules:
        return {}
    
    field_map = rules.get('field_map', {})
    
    # 컬럼명 매핑 (정확 매칭 + 유사 매칭)
    mapped_columns = {}
    unmapped_columns = []
    
    for col in df.columns:
        mapped = False
        
        # 1. 정확한 매칭
        if col in field_map:
            mapped_columns[col] = field_map[col]
            mapped = True
        else:
            # 2. 유사 매칭 (대소문자, 공백, 특수문자 무시)
            col_normalized = col.lower().replace(' ', '').replace('_', '').replace('(', '').replace(')', '').replace('.', '')
            
            for excel_col, rdf_prop in field_map.items():
                excel_normalized = excel_col.lower().replace(' ', '').replace('_', '').replace('(', '').replace(')', '').replace('.', '')
                
                if col_normalized == excel_normalized:
                    mapped_columns[col] = rdf_prop
                    mapped = True
                    break
                
                # 3. 부분 매칭 (포함 관계)
                if col_normalized in excel_normalized or excel_normalized in col_normalized:
                    if len(col_normalized) > 3 and len(excel_normalized) > 3:  # 너무 짧은 매칭 방지
                        mapped_columns[col] = rdf_prop
                        mapped = True
                        break
        
        if not mapped:
            unmapped_columns.append(col)
    
    print(f"📋 {data_source} 컬럼 매핑 결과:")
    print(f"   ✅ 매핑 성공: {len(mapped_columns)}개")
    print(f"   ❌ 매핑 실패: {len(unmapped_columns)}개")
    
    # 매핑된 컬럼 표시
    for original, mapped in mapped_columns.items():
        print(f"   {original} → {mapped}")
    
    # 매핑되지 않은 중요 컬럼 표시
    if unmapped_columns:
        print(f"   📝 매핑되지 않은 컬럼 (처음 10개):")
        for col in unmapped_columns[:10]:
            print(f"      • {col}")
    
    return mapped_columns

def convert_full_data_to_rdf(loaded_data, rules, batch_size=1000):
    """전체 데이터를 배치 처리로 RDF 변환"""
    print(f"\n🔗 전체 데이터를 RDF로 변환 중... (배치 크기: {batch_size})")
    
    if not rules:
        print("❌ 매핑 규칙이 없습니다.")
        return None
    
    namespace = rules.get('namespace', 'http://samsung.com/project-logistics#')
    
    # TTL 헤더
    ttl_content = f"""# HVDC Full Data Ontology RDF
# Generated: {datetime.now().isoformat()}
# Source: Complete HITACHI, SIMENSE, INVOICE Excel files
# Total Records: {sum(len(df) for df in loaded_data.values()):,}

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ex: <{namespace}> .

# Ontology Declaration
ex: a owl:Ontology ;
    rdfs:label "HVDC Full Data Warehouse Ontology" ;
    rdfs:comment "Complete warehouse data from HITACHI ({len(loaded_data.get('HITACHI', pd.DataFrame())):,} records), SIMENSE ({len(loaded_data.get('SIMENSE', pd.DataFrame())):,} records), INVOICE ({len(loaded_data.get('INVOICE', pd.DataFrame())):,} records)" ;
    owl:versionInfo "2.6" ;
    owl:versionIRI <{namespace}v2.6> .

"""
    
    event_counter = 1
    total_events = sum(len(df) for df in loaded_data.values())
    
    # 각 데이터셋 처리
    for data_source, df in loaded_data.items():
        print(f"🔄 {data_source} 전체 데이터 처리 중... ({len(df):,}행)")
        
        # 컬럼 매핑
        column_mapping = map_columns_to_ontology_full(df, rules, data_source)
        
        # 배치 처리로 메모리 효율성 확보
        num_batches = (len(df) + batch_size - 1) // batch_size
        
        with tqdm(total=len(df), desc=f"{data_source} 처리", unit="행") as pbar:
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, len(df))
                batch_df = df.iloc[start_idx:end_idx]
                
                # 배치 내 각 행 처리
                for idx, row in batch_df.iterrows():
                    event_id = f"TransportEvent_{event_counter:06d}"
                    ttl_content += f"ex:{event_id} a ex:TransportEvent ;\n"
                    ttl_content += f"    ex:hasDataSource \"{data_source}\" ;\n"
                    ttl_content += f"    ex:hasRowIndex \"{idx}\"^^xsd:integer ;\n"
                    
                    # 매핑된 컬럼들 처리
                    for original_col, rdf_prop in column_mapping.items():
                        if original_col in row and pd.notna(row[original_col]):
                            value = row[original_col]
                            
                            # 데이터 타입별 정확한 처리
                            if rdf_prop in ['hasQuantity', 'hasPackageCount', 'has20FTContainer', 'has40FTContainer', 'has20FRContainer', 'has40FRContainer', 'hasContainerStuffing', 'hasContainerUnstuffing']:
                                try:
                                    int_value = int(float(str(value)))
                                    ttl_content += f'    ex:{rdf_prop} "{int_value}"^^xsd:integer ;\n'
                                except:
                                    continue
                            elif rdf_prop in ['hasAmount', 'hasTotalAmount', 'hasHandlingFee', 'hasCBM', 'hasWeight', 'hasHandlingIn', 'hasHandlingOut', 'hasUnstuffing', 'hasStuffing', 'hasForklift', 'hasCrane']:
                                try:
                                    float_value = float(str(value))
                                    ttl_content += f'    ex:{rdf_prop} "{float_value}"^^xsd:decimal ;\n'
                                except:
                                    continue
                            elif rdf_prop in ['hasDate', 'hasStartDate', 'hasFinishDate', 'hasOperationMonth']:
                                try:
                                    if isinstance(value, pd.Timestamp):
                                        date_str = value.strftime('%Y-%m-%d')
                                    elif pd.isna(pd.to_datetime(str(value), errors='coerce')):
                                        continue
                                    else:
                                        date_str = pd.to_datetime(str(value)).strftime('%Y-%m-%d')
                                    ttl_content += f'    ex:{rdf_prop} "{date_str}"^^xsd:date ;\n'
                                except:
                                    continue
                            else:
                                # 문자열 처리 (특수문자 이스케이프)
                                clean_value = str(value).replace('"', '\\"').replace('\n', ' ').replace('\r', ' ').strip()
                                if clean_value and clean_value != 'nan':
                                    # 너무 긴 문자열 제한 (1000자)
                                    if len(clean_value) > 1000:
                                        clean_value = clean_value[:1000] + "..."
                                    ttl_content += f'    ex:{rdf_prop} "{clean_value}" ;\n'
                    
                    ttl_content = ttl_content.rstrip(';\n') + ' .\n\n'
                    event_counter += 1
                    pbar.update(1)
                
                # 메모리 관리: 매 1000개 이벤트마다 가비지 컬렉션
                if event_counter % 1000 == 0:
                    import gc
                    gc.collect()
    
    # 창고 및 사이트 인스턴스 추가
    warehouse_classification = rules.get('warehouse_classification', {})
    ttl_content += "\n# Warehouse and Site Instances\n"
    
    for storage_type, warehouses in warehouse_classification.items():
        for warehouse in warehouses:
            warehouse_id = warehouse.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
            
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
    ex:hasStorageType "{storage_type}" ;
    ex:hasCapacity "unknown"^^xsd:string .

"""
    
    print(f"✅ 전체 RDF 변환 완료: {event_counter-1:,}개 이벤트")
    return ttl_content

def generate_full_data_sparql(rules, loaded_data):
    """전체 데이터용 고급 SPARQL 쿼리 생성"""
    print("🔍 전체 데이터용 고급 SPARQL 쿼리 생성 중...")
    
    if not rules:
        return None
    
    namespace = rules.get('namespace', 'http://samsung.com/project-logistics#')
    total_records = sum(len(df) for df in loaded_data.values())
    
    queries = f"""# HVDC 전체 데이터 고급 SPARQL 쿼리 모음
# Generated: {datetime.now().isoformat()}
# Total Records: {total_records:,}

# 1. 전체 데이터 통계 요약
PREFIX ex: <{namespace}>
SELECT 
    (COUNT(?event) AS ?totalEvents)
    (COUNT(DISTINCT ?dataSource) AS ?dataSources)
    (SUM(?amount) AS ?totalAmount)
    (AVG(?amount) AS ?avgAmount)
    (SUM(?qty) AS ?totalQuantity)
    (SUM(?cbm) AS ?totalCBM)
WHERE {{
    ?event rdf:type ex:TransportEvent .
    OPTIONAL {{ ?event ex:hasAmount ?amount }}
    OPTIONAL {{ ?event ex:hasQuantity ?qty }}
    OPTIONAL {{ ?event ex:hasCBM ?cbm }}
    OPTIONAL {{ ?event ex:hasDataSource ?dataSource }}
}}

# 2. 데이터 소스별 상세 분석
PREFIX ex: <{namespace}>
SELECT ?dataSource 
    (COUNT(?event) AS ?eventCount) 
    (SUM(?amount) AS ?totalAmount)
    (AVG(?amount) AS ?avgAmount)
    (SUM(?cbm) AS ?totalCBM)
    (AVG(?cbm) AS ?avgCBM)
    (SUM(?weight) AS ?totalWeight)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasDataSource ?dataSource .
    OPTIONAL {{ ?event ex:hasAmount ?amount }}
    OPTIONAL {{ ?event ex:hasCBM ?cbm }}
    OPTIONAL {{ ?event ex:hasWeight ?weight }}
}}
GROUP BY ?dataSource
ORDER BY DESC(?eventCount)

# 3. 월별 트렌드 분석 (Operation Month 기준)
PREFIX ex: <{namespace}>
SELECT ?month ?dataSource 
    (COUNT(?event) AS ?eventCount)
    (SUM(?amount) AS ?totalAmount)
    (SUM(?handlingFee) AS ?totalHandlingFee)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasDataSource ?dataSource ;
           ex:hasOperationMonth ?month .
    OPTIONAL {{ ?event ex:hasAmount ?amount }}
    OPTIONAL {{ ?event ex:hasHandlingFee ?handlingFee }}
}}
GROUP BY ?month ?dataSource
ORDER BY ?month ?dataSource

# 4. 컨테이너 타입별 분석
PREFIX ex: <{namespace}>
SELECT 
    (SUM(?container20) AS ?total20FT)
    (SUM(?container40) AS ?total40FT)
    (SUM(?container20FR) AS ?total20FR)
    (SUM(?container40FR) AS ?total40FR)
    (COUNT(?event) AS ?eventsWithContainers)
WHERE {{
    ?event rdf:type ex:TransportEvent .
    OPTIONAL {{ ?event ex:has20FTContainer ?container20 }}
    OPTIONAL {{ ?event ex:has40FTContainer ?container40 }}
    OPTIONAL {{ ?event ex:has20FRContainer ?container20FR }}
    OPTIONAL {{ ?event ex:has40FRContainer ?container40FR }}
    FILTER(BOUND(?container20) || BOUND(?container40) || BOUND(?container20FR) || BOUND(?container40FR))
}}

# 5. 하역 작업 분석
PREFIX ex: <{namespace}>
SELECT 
    (COUNT(?event) AS ?handlingEvents)
    (SUM(?handlingIn) AS ?totalHandlingIn)
    (SUM(?handlingOut) AS ?totalHandlingOut)
    (SUM(?unstuffing) AS ?totalUnstuffing)
    (SUM(?stuffing) AS ?totalStuffing)
    (SUM(?forklift) AS ?totalForklift)
    (SUM(?crane) AS ?totalCrane)
WHERE {{
    ?event rdf:type ex:TransportEvent .
    OPTIONAL {{ ?event ex:hasHandlingIn ?handlingIn }}
    OPTIONAL {{ ?event ex:hasHandlingOut ?handlingOut }}
    OPTIONAL {{ ?event ex:hasUnstuffing ?unstuffing }}
    OPTIONAL {{ ?event ex:hasStuffing ?stuffing }}
    OPTIONAL {{ ?event ex:hasForklift ?forklift }}
    OPTIONAL {{ ?event ex:hasCrane ?crane }}
}}

# 6. 카테고리별 분석 (INVOICE 데이터)
PREFIX ex: <{namespace}>
SELECT ?category 
    (COUNT(?event) AS ?eventCount)
    (SUM(?amount) AS ?totalAmount)
    (AVG(?amount) AS ?avgAmount)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasCategory ?category ;
           ex:hasAmount ?amount .
}}
GROUP BY ?category
ORDER BY DESC(?totalAmount)

# 7. CBM 및 무게 기준 대형 화물 분석
PREFIX ex: <{namespace}>
SELECT ?dataSource
    (COUNT(?event) AS ?largeCargoCount)
    (SUM(?cbm) AS ?totalCBM)
    (AVG(?cbm) AS ?avgCBM)
    (SUM(?weight) AS ?totalWeight)
    (AVG(?weight) AS ?avgWeight)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasDataSource ?dataSource ;
           ex:hasCBM ?cbm .
    OPTIONAL {{ ?event ex:hasWeight ?weight }}
    FILTER(?cbm > 10.0)  # 10 CBM 이상 대형 화물
}}
GROUP BY ?dataSource
ORDER BY DESC(?totalCBM)

# 8. 패키지 수량 분석
PREFIX ex: <{namespace}>
SELECT ?dataSource
    (COUNT(?event) AS ?eventCount)
    (SUM(?packages) AS ?totalPackages)
    (AVG(?packages) AS ?avgPackages)
    (MAX(?packages) AS ?maxPackages)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasDataSource ?dataSource ;
           ex:hasPackageCount ?packages .
}}
GROUP BY ?dataSource
ORDER BY DESC(?totalPackages)

# 9. 데이터 품질 분석 (결측값 체크)
PREFIX ex: <{namespace}>
SELECT ?dataSource
    (COUNT(?event) AS ?totalEvents)
    (COUNT(?amount) AS ?eventsWithAmount)
    (COUNT(?cbm) AS ?eventsWithCBM)
    (COUNT(?weight) AS ?eventsWithWeight)
    (COUNT(?packages) AS ?eventsWithPackages)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasDataSource ?dataSource .
    OPTIONAL {{ ?event ex:hasAmount ?amount }}
    OPTIONAL {{ ?event ex:hasCBM ?cbm }}
    OPTIONAL {{ ?event ex:hasWeight ?weight }}
    OPTIONAL {{ ?event ex:hasPackageCount ?packages }}
}}
GROUP BY ?dataSource
ORDER BY ?dataSource

# 10. 복합 분석: 월별 + 카테고리별 + 데이터소스별
PREFIX ex: <{namespace}>
SELECT ?month ?category ?dataSource
    (COUNT(?event) AS ?eventCount)
    (SUM(?amount) AS ?totalAmount)
    (SUM(?handlingFee) AS ?totalHandlingFee)
WHERE {{
    ?event rdf:type ex:TransportEvent ;
           ex:hasDataSource ?dataSource .
    OPTIONAL {{ ?event ex:hasOperationMonth ?month }}
    OPTIONAL {{ ?event ex:hasCategory ?category }}
    OPTIONAL {{ ?event ex:hasAmount ?amount }}
    OPTIONAL {{ ?event ex:hasHandlingFee ?handlingFee }}
    FILTER(BOUND(?month) && BOUND(?category))
}}
GROUP BY ?month ?category ?dataSource
ORDER BY ?month ?category ?dataSource
"""
    
    return queries

def save_full_data_outputs(ttl_content, sparql_queries, loaded_data):
    """전체 데이터 결과 저장"""
    print("\n💾 전체 데이터 결과 저장 중...")
    
    # 출력 디렉토리 생성
    output_dir = Path('rdf_output')
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total_records = sum(len(df) for df in loaded_data.values())
    
    files_created = []
    
    # TTL 파일 저장 (대용량 파일 처리)
    if ttl_content:
        ttl_file = output_dir / f'hvdc_full_data_{total_records}records_{timestamp}.ttl'
        
        print(f"📝 대용량 TTL 파일 저장 중... (예상 크기: {len(ttl_content) / 1024 / 1024:.1f}MB)")
        
        with open(ttl_file, 'w', encoding='utf-8') as f:
            f.write(ttl_content)
        
        file_size_mb = ttl_file.stat().st_size / 1024 / 1024
        print(f"✅ 전체 데이터 RDF/TTL 저장: {ttl_file}")
        print(f"   📊 파일 크기: {file_size_mb:.2f}MB")
        files_created.append(('RDF/TTL', ttl_file, f"{file_size_mb:.2f}MB"))
    
    # SPARQL 쿼리 저장
    if sparql_queries:
        sparql_file = output_dir / f'hvdc_full_queries_{total_records}records_{timestamp}.sparql'
        with open(sparql_file, 'w', encoding='utf-8') as f:
            f.write(sparql_queries)
        print(f"✅ 전체 데이터 SPARQL 쿼리 저장: {sparql_file}")
        files_created.append(('SPARQL', sparql_file, "고급 10개 쿼리"))
    
    # 통계 요약 파일 생성
    stats_file = output_dir / f'hvdc_full_stats_{timestamp}.md'
    stats_content = f"""# HVDC 전체 데이터 온톨로지 매핑 통계

## 📊 처리 통계
- **처리 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **총 레코드 수**: {total_records:,}개
- **데이터 소스**: {len(loaded_data)}개

## 📋 데이터 소스별 상세
"""
    
    for name, df in loaded_data.items():
        stats_content += f"""
### {name}
- **레코드 수**: {len(df):,}개
- **컬럼 수**: {len(df.columns)}개
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB
"""
    
    stats_content += f"""
## 📁 생성된 파일
"""
    
    for file_type, file_path, size_info in files_created:
        stats_content += f"- **{file_type}**: `{file_path.name}` ({size_info})\n"
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(stats_content)
    
    files_created.append(('통계', stats_file, "상세 통계"))
    
    return files_created

def main():
    """메인 실행 함수"""
    print("🚀 /cmd_full_data_mapping 실행")
    print("=" * 70)
    print("📈 HVDC 전체 데이터 온톨로지 매핑 (8,000+행)")
    print("=" * 70)
    
    start_time = time.time()
    
    # 1단계: 전체 데이터 로드
    loaded_data = load_full_data()
    
    if not loaded_data:
        print("❌ 데이터 파일을 로드할 수 없습니다.")
        return
    
    # 2단계: 데이터 구조 분석
    analyze_full_data_structure(loaded_data)
    
    # 3단계: 매핑 규칙 로드
    rules = load_mapping_rules()
    
    # 4단계: 전체 데이터 RDF 변환
    ttl_content = convert_full_data_to_rdf(loaded_data, rules, batch_size=500)
    
    # 5단계: 고급 SPARQL 쿼리 생성
    sparql_queries = generate_full_data_sparql(rules, loaded_data)
    
    # 6단계: 결과 저장
    if ttl_content and sparql_queries:
        files_created = save_full_data_outputs(ttl_content, sparql_queries, loaded_data)
        
        total_time = time.time() - start_time
        total_records = sum(len(df) for df in loaded_data.values())
        
        print("\n🎉 전체 데이터 온톨로지 매핑 완료!")
        print("=" * 70)
        print("📊 최종 통계:")
        print(f"   • 총 처리 시간: {total_time:.2f}초")
        print(f"   • 총 레코드 수: {total_records:,}개")
        print(f"   • 처리 속도: {total_records/total_time:.0f}개/초")
        
        for name, df in loaded_data.items():
            print(f"   • {name}: {len(df):,}행 → 완전 변환")
        
        print("\n📁 생성된 파일:")
        for file_type, file_path, size_info in files_created:
            print(f"   • {file_type}: {file_path.name} ({size_info})")
        
        print("\n🔧 추천 명령어:")
        print("   /cmd_ontology_query [전체 데이터 쿼리 실행]")
        print("   /cmd_data_validation [데이터 품질 검증]")
        print("   /cmd_warehouse_analysis [창고 분석]")
        print("   /cmd_performance_analysis [성능 분석]")
        print("   /cmd_export_excel [Excel 리포트 생성]")
    else:
        print("\n❌ 전체 데이터 온톨로지 매핑 실패")

if __name__ == "__main__":
    main() 