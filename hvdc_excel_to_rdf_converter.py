#!/usr/bin/env python3
"""
HVDC Excel to RDF Converter
Excel 파일을 RDF/TTL 형식으로 변환하는 스크립트
"""

import pandas as pd
import numpy as np
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.plugins.sparql import prepareQuery
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 네임스페이스 정의
EX = Namespace("http://samsung.com/project-logistics#")
ns = {
    "ex": "http://samsung.com/project-logistics#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
}

# 매핑 규칙 정의
FIELD_MAPPINGS = {
    "Case No.": "hasCase",
    "Case_No": "hasCase",
    "no.": "hasSequenceNumber",
    "Shipment Invoice No.": "hasShipmentInvoiceNumber",
    "HVDC CODE": "hasHVDCCode",
    "HVDC CODE 1": "hasHVDCCode1",
    "HVDC CODE 2": "hasHVDCCode2",
    "HVDC CODE 3": "hasHVDCCode3",
    "HVDC CODE 4": "hasHVDCCode4",
    "HVDC CODE 5": "hasHVDCCode5",
    "EQ No": "hasEquipmentNumber",
    "Pkg": "hasPackageCount",
    "Storage": "hasStorageType",
    "Description": "hasDescription",
    "L(CM)": "hasLength",
    "W(CM)": "hasWidth",
    "H(CM)": "hasHeight",
    "CBM": "hasCubicMeter",
    "N.W(kgs)": "hasNetWeight",
    "G.W(kgs)": "hasGrossWeight",
    "Stack": "hasStackInfo",
    "ETA": "hasETA",
    "ETD": "hasETD",
    "Date": "hasDate",
    "Operation Month": "hasOperationMonth",
    "DHL Warehouse": "hasDHLWarehouse",
    "DSV Indoor": "hasDSVIndoor",
    "DSV Al Markaz": "hasDSVAlMarkaz",
    "DSV Outdoor": "hasDSVOutdoor",
    "AAA  Storage": "hasAAAStorage",
    "Hauler Indoor": "hasHaulerIndoor",
    "DSV MZP": "hasDSVMZP",
    "MOSB": "hasMOSB",
    "Shifting": "hasShifting",
    "DAS": "hasDAS",
    "AGI": "hasAGI",
    "SHU": "hasSHU",
    "MIR": "hasMIR",
    "Logistics Flow Code": "hasLogisticsFlowCode",
    "Flow_Code": "hasFlowCode",
    "Status": "hasStatus",
    "Status_Location": "hasStatusLocation",
    "Status_Location_Date": "hasStatusLocationDate",
    "Status_Current": "hasCurrentStatus",
    "Status_Storage": "hasStorageStatus",
    "wh handling": "hasWHHandling"
}

def load_ontology_schema():
    """온톨로지 스키마 로드"""
    g = Graph()
    
    # 네임스페이스 바인딩
    for prefix, uri in ns.items():
        g.bind(prefix, Namespace(uri))
    
    # 스키마 파일이 있다면 로드
    if Path("hvdc_integrated_ontology_schema.ttl").exists():
        try:
            g.parse("hvdc_integrated_ontology_schema.ttl", format="turtle")
            print(f"✅ 온톨로지 스키마 로드 완료: {len(g)} 트리플")
        except Exception as e:
            print(f"⚠️ 스키마 로드 실패: {e}")
    else:
        print("⚠️ 스키마 파일 없음, 기본 스키마 생성")
        create_default_schema(g)
    
    return g

def create_default_schema(g):
    """기본 온톨로지 스키마 생성"""
    # 기본 클래스 정의
    classes = [
        (EX.TransportEvent, "운송 이벤트"),
        (EX.Warehouse, "창고"),
        (EX.Site, "현장"),
        (EX.HitachiCargo, "히타치 화물"),
        (EX.SiemensCargo, "지멘스 화물"),
        (EX.Case, "케이스"),
        (EX.Item, "아이템")
    ]
    
    for class_uri, label in classes:
        g.add((class_uri, RDF.type, OWL.Class))
        g.add((class_uri, RDFS.label, Literal(label, lang='ko')))
    
    # 기본 속성 정의
    properties = [
        (EX.hasCase, "케이스 번호"),
        (EX.hasDate, "날짜"),
        (EX.hasLocation, "위치"),
        (EX.hasQuantity, "수량"),
        (EX.hasAmount, "금액"),
        (EX.hasCubicMeter, "체적"),
        (EX.hasWeight, "중량"),
        (EX.hasHVDCCode, "HVDC 코드"),
        (EX.hasDescription, "설명")
    ]
    
    for prop_uri, label in properties:
        g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        g.add((prop_uri, RDFS.label, Literal(label, lang='ko')))

def normalize_code_num(code):
    """코드 번호 정규화"""
    if pd.isna(code):
        return None
    return str(code).strip().lstrip('0') or '0'

def is_valid_hvdc_vendor(code, valid_codes=['HE', 'SIM']):
    """유효한 HVDC 벤더 코드인지 확인"""
    if pd.isna(code):
        return False
    return str(code).strip().upper() in valid_codes

def preprocess_dataframe(df, source_file):
    """데이터프레임 전처리"""
    print(f"📊 데이터 전처리 시작: {source_file}")
    
    original_count = len(df)
    
    # 1. 열 이름 정규화
    df.columns = df.columns.str.strip()
    
    # 2. 날짜 컬럼 변환
    date_columns = [col for col in df.columns if 'Date' in col or 'ETA' in col or 'ETD' in col]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 3. 수치형 컬럼 변환
    numeric_columns = ['CBM', 'N.W(kgs)', 'G.W(kgs)', 'L(CM)', 'W(CM)', 'H(CM)', 'Pkg']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 4. CBM 양수 보정
    if 'CBM' in df.columns:
        cbm_violations = (df['CBM'] <= 0).sum()
        if cbm_violations > 0:
            mean_cbm = df[df['CBM'] > 0]['CBM'].mean()
            df.loc[df['CBM'] <= 0, 'CBM'] = mean_cbm
            print(f"  ✅ CBM 위반 {cbm_violations}건 → 평균값 {mean_cbm:.2f}로 보정")
    
    # 5. 패키지 수 보정
    if 'Pkg' in df.columns:
        df['Pkg'] = df['Pkg'].fillna(1)
        df.loc[df['Pkg'] <= 0, 'Pkg'] = 1
    
    # 6. HVDC CODE 3 필터링
    if 'HVDC CODE 3' in df.columns:
        valid_vendor_mask = df['HVDC CODE 3'].apply(is_valid_hvdc_vendor)
        df = df[valid_vendor_mask]
        filtered_count = len(df)
        print(f"  ✅ 벤더 필터링: {original_count} → {filtered_count}")
    
    # 7. 중복 제거
    if 'Case No.' in df.columns:
        df = df.drop_duplicates(subset=['Case No.'])
        final_count = len(df)
        print(f"  ✅ 중복 제거: {filtered_count if 'HVDC CODE 3' in df.columns else original_count} → {final_count}")
    
    # 8. 데이터 소스 추가
    df['data_source'] = source_file.replace('.xlsx', '')
    
    print(f"📊 전처리 완료: {original_count} → {len(df)} ({len(df)/original_count*100:.1f}%)")
    
    return df

def create_rdf_graph(df, source_file):
    """DataFrame을 RDF 그래프로 변환"""
    print(f"🔗 RDF 그래프 생성 시작: {source_file}")
    
    # 온톨로지 스키마 로드
    g = load_ontology_schema()
    
    # 데이터 변환
    for idx, row in df.iterrows():
        # TransportEvent URI 생성
        case_no = str(row.get('Case No.', f"case_{idx+1}")).replace(' ', '_')
        event_uri = EX[f"TransportEvent_{case_no}"]
        
        # 기본 클래스 추가
        g.add((event_uri, RDF.type, EX.TransportEvent))
        
        # 벤더별 화물 클래스 추가
        if 'HVDC CODE 3' in row and pd.notna(row['HVDC CODE 3']):
            vendor = str(row['HVDC CODE 3']).strip().upper()
            if vendor == 'HE':
                g.add((event_uri, RDF.type, EX.HitachiCargo))
            elif vendor == 'SIM':
                g.add((event_uri, RDF.type, EX.SiemensCargo))
        
        # 데이터 소스 추가
        g.add((event_uri, EX.hasDataSource, Literal(source_file)))
        
        # 각 컬럼을 RDF 속성으로 변환
        for col, value in row.items():
            if pd.isna(value) or col not in FIELD_MAPPINGS:
                continue
            
            property_uri = EX[FIELD_MAPPINGS[col]]
            
            # 데이터 타입에 따른 Literal 생성
            if isinstance(value, (int, np.integer)):
                literal = Literal(int(value), datatype=XSD.integer)
            elif isinstance(value, (float, np.floating)):
                literal = Literal(float(value), datatype=XSD.decimal)
            elif isinstance(value, datetime):
                literal = Literal(value.date(), datatype=XSD.date)
            elif isinstance(value, pd.Timestamp):
                literal = Literal(value.date(), datatype=XSD.date)
            else:
                literal = Literal(str(value))
            
            g.add((event_uri, property_uri, literal))
    
    print(f"🔗 RDF 그래프 생성 완료: {len(df)} 레코드, {len(g)} 트리플")
    
    return g

def save_rdf_file(graph, output_file):
    """RDF 그래프를 TTL 파일로 저장"""
    print(f"💾 RDF 파일 저장: {output_file}")
    
    # 출력 디렉토리 생성
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # TTL 파일로 저장
    graph.serialize(destination=output_file, format="turtle")
    
    file_size = Path(output_file).stat().st_size
    print(f"✅ RDF 파일 저장 완료: {file_size:,} bytes")

def validate_rdf_graph(graph):
    """RDF 그래프 유효성 검증"""
    print("🔍 RDF 그래프 검증 시작...")
    
    # 기본 통계
    total_triples = len(graph)
    
    # 클래스별 인스턴스 수
    query = """
    SELECT ?class (COUNT(?instance) AS ?count)
    WHERE {
        ?instance rdf:type ?class .
        FILTER(STRSTARTS(STR(?class), "http://samsung.com/project-logistics#"))
    }
    GROUP BY ?class
    ORDER BY DESC(?count)
    """
    
    results = graph.query(query)
    
    print(f"📊 검증 결과:")
    print(f"  - 총 트리플 수: {total_triples:,}")
    print(f"  - 클래스별 인스턴스:")
    
    for row in results:
        class_name = str(row[0]).split('#')[-1]
        count = int(row[1])
        print(f"    • {class_name}: {count:,}개")
    
    # 데이터 품질 검증
    quality_checks = [
        ("CBM > 0", "?event ex:hasCubicMeter ?cbm . FILTER(?cbm > 0)"),
        ("패키지 수 > 0", "?event ex:hasPackageCount ?pkg . FILTER(?pkg > 0)"),
        ("케이스 번호 존재", "?event ex:hasCase ?case . FILTER(STRLEN(?case) > 0)"),
        ("데이터 소스 존재", "?event ex:hasDataSource ?source . FILTER(STRLEN(?source) > 0)")
    ]
    
    print(f"  - 품질 검증:")
    for check_name, check_query in quality_checks:
        count_query = f"SELECT (COUNT(*) AS ?count) WHERE {{ {check_query} }}"
        result = list(graph.query(count_query))
        if result:
            count = int(result[0][0])
            print(f"    • {check_name}: {count:,}개")
    
    return total_triples

def main():
    """메인 함수"""
    print("🚀 HVDC Excel to RDF 변환 시작")
    print("=" * 50)
    
    # 입력 파일 정의
    input_files = [
        "data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
    ]
    
    # 출력 디렉토리 생성
    output_dir = Path("rdf_output")
    output_dir.mkdir(exist_ok=True)
    
    # 통합 그래프 생성
    combined_graph = Graph()
    
    # 네임스페이스 바인딩
    for prefix, uri in ns.items():
        combined_graph.bind(prefix, Namespace(uri))
    
    total_records = 0
    
    # 각 파일 처리
    for input_file in input_files:
        if not Path(input_file).exists():
            print(f"❌ 파일 없음: {input_file}")
            continue
        
        print(f"\n📁 파일 처리: {input_file}")
        
        # Excel 파일 읽기
        try:
            df = pd.read_excel(input_file, sheet_name='Case List')
            print(f"📊 데이터 로드: {len(df)} 레코드")
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {e}")
            continue
        
        # 데이터 전처리
        df = preprocess_dataframe(df, Path(input_file).stem)
        
        # RDF 그래프 생성
        graph = create_rdf_graph(df, Path(input_file).stem)
        
        # 개별 파일 저장
        output_file = output_dir / f"{Path(input_file).stem}.ttl"
        save_rdf_file(graph, str(output_file))
        
        # 통합 그래프에 추가
        combined_graph += graph
        
        total_records += len(df)
        
        print(f"✅ {input_file} 처리 완료")
    
    # 통합 파일 저장
    combined_output = output_dir / "HVDC_COMBINED.ttl"
    save_rdf_file(combined_graph, str(combined_output))
    
    # 최종 검증
    print(f"\n🔍 최종 검증")
    print("=" * 50)
    validate_rdf_graph(combined_graph)
    
    print(f"\n🎉 변환 완료!")
    print(f"📊 총 처리 레코드: {total_records:,}")
    print(f"💾 출력 파일:")
    print(f"  - 통합 파일: {combined_output}")
    for input_file in input_files:
        if Path(input_file).exists():
            output_file = output_dir / f"{Path(input_file).stem}.ttl"
            print(f"  - 개별 파일: {output_file}")
    
    print(f"\n🔧 추천 명령어:")
    print(f"  /validate-data comprehensive --sparql-rules")
    print(f"  /semantic-search --query='RDF conversion'")

if __name__ == "__main__":
    main() 