#!/usr/bin/env python3
"""
HVDC-STATUS 데이터 분석 및 매핑 도구
/cmd_status_mapping 명령어 구현
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_hvdc_status():
    """HVDC-STATUS.xlsx 파일 구조 분석"""
    print("🚀 /cmd_status_mapping 실행")
    print("=" * 70)
    print("📈 HVDC-STATUS 데이터 분석 및 매핑")
    print("=" * 70)
    
    try:
        # 파일 로드
        print("📋 HVDC-STATUS 파일 로드 중...")
        df = pd.read_excel('data/HVDC-STATUS.xlsx')
        
        print(f"✅ HVDC-STATUS: {len(df):,}행 로드 완료")
        print(f"   📊 컬럼 수: {len(df.columns)}")
        print(f"   📊 메모리 사용량: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB")
        
        # 컬럼 구조 분석
        print(f"\n📋 HVDC-STATUS 컬럼 목록 ({len(df.columns)}개):")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # 데이터 타입 분석
        numeric_cols = df.select_dtypes(include=['number']).columns
        date_cols = df.select_dtypes(include=['datetime']).columns
        text_cols = df.select_dtypes(include=['object']).columns
        
        print(f"\n📊 데이터 타입 분석:")
        print(f"   📊 숫자형 컬럼: {len(numeric_cols)}개")
        print(f"   📊 날짜형 컬럼: {len(date_cols)}개")
        print(f"   📊 텍스트형 컬럼: {len(text_cols)}개")
        
        # 결측값 분석
        missing_data = df.isnull().sum()
        missing_cols = missing_data[missing_data > 0]
        print(f"   📊 결측값 있는 컬럼: {len(missing_cols)}개")
        
        # 샘플 데이터 표시
        print(f"\n📝 샘플 데이터 (처음 3행):")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ HVDC-STATUS 파일 로드 실패: {e}")
        return None

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

def map_hvdc_status_columns(df, rules):
    """HVDC-STATUS 컬럼을 온톨로지에 매핑"""
    if not rules or df is None:
        return {}
    
    print(f"\n🔗 HVDC-STATUS 컬럼 온톨로지 매핑")
    print("-" * 50)
    
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
    
    print(f"📋 HVDC-STATUS 컬럼 매핑 결과:")
    print(f"   ✅ 매핑 성공: {len(mapped_columns)}개")
    print(f"   ❌ 매핑 실패: {len(unmapped_columns)}개")
    
    # 매핑된 컬럼 표시
    if mapped_columns:
        print(f"\n✅ 성공적으로 매핑된 컬럼:")
        for original, mapped in mapped_columns.items():
            print(f"   {original} → {mapped}")
    
    # 매핑되지 않은 컬럼 표시
    if unmapped_columns:
        print(f"\n❌ 매핑되지 않은 컬럼:")
        for col in unmapped_columns:
            print(f"   • {col}")
    
    return mapped_columns

def convert_hvdc_status_to_rdf(df, rules, mapped_columns):
    """HVDC-STATUS 데이터를 RDF로 변환"""
    if df is None or not rules or not mapped_columns:
        print("❌ RDF 변환을 위한 데이터가 부족합니다.")
        return None
    
    print(f"\n🔗 HVDC-STATUS 데이터를 RDF로 변환 중...")
    
    namespace = rules.get('namespace', 'http://samsung.com/project-logistics#')
    
    # TTL 헤더
    ttl_content = f"""# HVDC-STATUS Data Ontology RDF
# Generated: {datetime.now().isoformat()}
# Source: HVDC-STATUS.xlsx
# Total Records: {len(df):,}

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ex: <{namespace}> .

# Ontology Declaration
ex: a owl:Ontology ;
    rdfs:label "HVDC Status Data Ontology" ;
    rdfs:comment "Status data from HVDC-STATUS.xlsx ({len(df):,} records)" ;
    owl:versionInfo "2.6" ;
    owl:versionIRI <{namespace}v2.6> .

"""
    
    # 데이터 변환
    event_counter = 1
    
    for index, row in df.iterrows():
        event_uri = f"ex:StatusEvent_{event_counter:06d}"
        ttl_content += f"\n# Status Event {event_counter}\n"
        ttl_content += f"{event_uri} rdf:type ex:StatusEvent ;\n"
        ttl_content += f"    ex:hasDataSource \"HVDC-STATUS\" ;\n"
        
        # 매핑된 컬럼들을 RDF 속성으로 변환
        for excel_col, rdf_property in mapped_columns.items():
            value = row[excel_col]
            
            if pd.notna(value):
                # 데이터 타입에 따른 처리
                if isinstance(value, (int, float)):
                    ttl_content += f"    {rdf_property} {value} ;\n"
                elif isinstance(value, str):
                    # 문자열 이스케이프 처리
                    escaped_value = value.replace('"', '\\"').replace('\n', '\\n')
                    ttl_content += f"    {rdf_property} \"{escaped_value}\" ;\n"
                else:
                    ttl_content += f"    {rdf_property} \"{str(value)}\" ;\n"
        
        ttl_content = ttl_content.rstrip(' ;\n') + " .\n"
        event_counter += 1
    
    print(f"✅ HVDC-STATUS RDF 변환 완료: {len(df):,}개 이벤트")
    return ttl_content

def generate_hvdc_status_sparql(rules, df):
    """HVDC-STATUS 전용 SPARQL 쿼리 생성"""
    if not rules or df is None:
        return ""
    
    print(f"🔍 HVDC-STATUS 전용 SPARQL 쿼리 생성 중...")
    
    namespace = rules.get('namespace', 'http://samsung.com/project-logistics#')
    
    sparql_queries = f"""# HVDC-STATUS 전용 SPARQL 쿼리 모음
# Generated: {datetime.now().isoformat()}
# Total Records: {len(df):,}

# 1. HVDC-STATUS 전체 통계
PREFIX ex: <{namespace}>
SELECT 
    (COUNT(?event) AS ?totalStatusEvents)
    (COUNT(DISTINCT ?location) AS ?uniqueLocations)
    (COUNT(DISTINCT ?vendor) AS ?uniqueVendors)
WHERE {{
    ?event rdf:type ex:StatusEvent .
    OPTIONAL {{ ?event ex:hasLocation ?location }}
    OPTIONAL {{ ?event ex:hasVendor ?vendor }}
}}

# 2. 상태별 분석
PREFIX ex: <{namespace}>
SELECT ?status 
    (COUNT(?event) AS ?eventCount)
WHERE {{
    ?event rdf:type ex:StatusEvent ;
           ex:hasStatus ?status .
}}
GROUP BY ?status
ORDER BY DESC(?eventCount)

# 3. 위치별 상태 분석
PREFIX ex: <{namespace}>
SELECT ?location ?status
    (COUNT(?event) AS ?eventCount)
WHERE {{
    ?event rdf:type ex:StatusEvent ;
           ex:hasLocation ?location ;
           ex:hasStatus ?status .
}}
GROUP BY ?location ?status
ORDER BY ?location ?status

# 4. 데이터 품질 분석
PREFIX ex: <{namespace}>
SELECT 
    (COUNT(?event) AS ?totalEvents)
    (COUNT(?location) AS ?eventsWithLocation)
    (COUNT(?status) AS ?eventsWithStatus)
    (COUNT(?date) AS ?eventsWithDate)
WHERE {{
    ?event rdf:type ex:StatusEvent .
    OPTIONAL {{ ?event ex:hasLocation ?location }}
    OPTIONAL {{ ?event ex:hasStatus ?status }}
    OPTIONAL {{ ?event ex:hasDate ?date }}
}}

"""
    
    return sparql_queries

def save_hvdc_status_outputs(ttl_content, sparql_queries, df):
    """HVDC-STATUS 결과 파일 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # RDF/TTL 파일 저장
    ttl_filename = f"rdf_output/hvdc_status_{len(df)}records_{timestamp}.ttl"
    Path("rdf_output").mkdir(exist_ok=True)
    
    with open(ttl_filename, "w", encoding="utf-8") as f:
        f.write(ttl_content)
    
    ttl_size = Path(ttl_filename).stat().st_size / 1024 / 1024
    print(f"✅ HVDC-STATUS RDF/TTL 저장: {ttl_filename}")
    print(f"   📊 파일 크기: {ttl_size:.2f}MB")
    
    # SPARQL 쿼리 파일 저장
    sparql_filename = f"rdf_output/hvdc_status_queries_{len(df)}records_{timestamp}.sparql"
    with open(sparql_filename, "w", encoding="utf-8") as f:
        f.write(sparql_queries)
    
    print(f"✅ HVDC-STATUS SPARQL 쿼리 저장: {sparql_filename}")
    
    # 통계 파일 저장
    stats_filename = f"rdf_output/hvdc_status_stats_{timestamp}.md"
    stats_content = f"""# HVDC-STATUS 데이터 매핑 통계

## 📊 처리 통계
- **처리 일시**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **총 레코드 수**: {len(df):,}개
- **컬럼 수**: {len(df.columns)}개

## 📁 생성된 파일
- **RDF/TTL**: `{ttl_filename}` ({ttl_size:.2f}MB)
- **SPARQL**: `{sparql_filename}` (전용 쿼리)

"""
    
    with open(stats_filename, "w", encoding="utf-8") as f:
        f.write(stats_content)
    
    print(f"✅ HVDC-STATUS 통계 저장: {stats_filename}")
    
    return ttl_filename, sparql_filename, stats_filename

def main():
    """메인 실행 함수"""
    start_time = datetime.now()
    
    # 1. HVDC-STATUS 파일 분석
    df = analyze_hvdc_status()
    if df is None:
        return
    
    # 2. 매핑 규칙 로드
    rules = load_mapping_rules()
    if not rules:
        return
    
    # 3. 컬럼 매핑
    mapped_columns = map_hvdc_status_columns(df, rules)
    
    # 4. RDF 변환
    ttl_content = convert_hvdc_status_to_rdf(df, rules, mapped_columns)
    
    # 5. SPARQL 쿼리 생성
    sparql_queries = generate_hvdc_status_sparql(rules, df)
    
    # 6. 결과 저장
    if ttl_content:
        ttl_file, sparql_file, stats_file = save_hvdc_status_outputs(ttl_content, sparql_queries, df)
    
    # 7. 최종 결과
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    print(f"\n🎉 HVDC-STATUS 매핑 완료!")
    print("=" * 70)
    print(f"📊 최종 통계:")
    print(f"   • 총 처리 시간: {processing_time:.2f}초")
    print(f"   • 총 레코드 수: {len(df):,}개")
    print(f"   • 처리 속도: {len(df)/processing_time:.0f}개/초")
    print(f"   • 매핑 성공: {len(mapped_columns)}개 컬럼")
    print(f"   • 매핑 실패: {len(df.columns) - len(mapped_columns)}개 컬럼")
    
    if ttl_content:
        print(f"\n📁 생성된 파일:")
        print(f"   • RDF/TTL: {Path(ttl_file).name}")
        print(f"   • SPARQL: {Path(sparql_file).name}")
        print(f"   • 통계: {Path(stats_file).name}")
    
    print(f"\n🔧 추천 명령어:")
    print(f"   /cmd_status_query [HVDC-STATUS 쿼리 실행]")
    print(f"   /cmd_status_validation [상태 데이터 검증]")
    print(f"   /cmd_status_analysis [상태 분석]")
    print(f"   /cmd_export_status_excel [Excel 리포트 생성]")

if __name__ == "__main__":
    main() 