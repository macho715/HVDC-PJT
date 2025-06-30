#!/usr/bin/env python3
"""
SCNT SHIPMENT DRAFT INVOICE (APRIL 2025_CHA) 데이터 분석 및 매핑 도구 (개선 버전)
/cmd_scnt_invoice_mapping_fixed 명령어 구현
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import logging
from tqdm import tqdm
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_scnt_invoice_fixed():
    """SCNT SHIPMENT DRAFT INVOICE (APRIL 2025_CHA).xlsx 파일 구조 분석 (개선 버전)"""
    print("🚀 /cmd_scnt_invoice_mapping_fixed 실행")
    print("=" * 70)
    print("📈 SCNT SHIPMENT DRAFT INVOICE (APRIL 2025_CHA) 데이터 분석 및 매핑 (개선 버전)")
    print("=" * 70)
    
    try:
        # 파일 로드 (헤더를 5번째 행으로 설정)
        print("📋 SCNT INVOICE 파일 로드 중 (헤더: 5행)...")
        df = pd.read_excel('data/SCNT SHIPMENT DRAFT INVOICE (APRIL 2025_CHA).xlsx', header=5)
        
        # 빈 행 제거
        df = df.dropna(how='all')
        
        print(f"✅ SCNT INVOICE: {len(df):,}행 로드 완료")
        print(f"   📊 컬럼 수: {len(df.columns)}")
        print(f"   📊 메모리 사용량: {df.memory_usage(deep=True).sum() / 1024**2:.2f}MB")
        
        # 컬럼 정리 (Unnamed 컬럼 제거)
        original_cols = len(df.columns)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        print(f"   📊 정리 후 컬럼 수: {len(df.columns)} (제거: {original_cols - len(df.columns)}개)")
        
        # 컬럼 목록 출력
        print(f"\n📋 SCNT INVOICE 컬럼 목록 ({len(df.columns)}개):")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # 데이터 타입 분석
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        print(f"\n📊 데이터 타입 분석:")
        print(f"   📊 숫자형 컬럼: {len(numeric_cols)}개")
        print(f"   📊 날짜형 컬럼: {len(datetime_cols)}개")
        print(f"   📊 텍스트형 컬럼: {len(text_cols)}개")
        print(f"   📊 결측값 있는 컬럼: {df.isnull().any().sum()}개")
        
        # 샘플 데이터 출력 (컬럼명만)
        print(f"\n📝 주요 컬럼 샘플:")
        key_columns = ['S/No', 'Shpt Ref', 'Job #', 'Type', 'BL #', 'POL', 'POD', 'Mode', 'Volume', 'Quantity']
        available_key_cols = [col for col in key_columns if col in df.columns]
        if available_key_cols:
            print(df[available_key_cols].head(3).to_string())
        
        # 매핑 규칙 로드
        try:
            with open('mapping_rules_v2.6.json', 'r', encoding='utf-8') as f:
                mapping_rules = json.load(f)
            print("✅ 매핑 규칙 로드 성공")
        except FileNotFoundError:
            print("⚠️ 매핑 규칙 파일을 찾을 수 없습니다.")
            return
        
        # SCNT 특화 매핑 규칙 생성
        scnt_mapping = create_scnt_specific_mapping(df.columns)
        
        # 컬럼 매핑 분석
        print(f"\n🔗 SCNT INVOICE 컬럼 온톨로지 매핑")
        print("-" * 50)
        
        field_mappings = mapping_rules.get('field_mappings', {})
        field_mappings.update(scnt_mapping)  # SCNT 특화 매핑 추가
        
        mapped_columns = []
        unmapped_columns = []
        
        for col in df.columns:
            if col in field_mappings:
                mapped_columns.append((col, field_mappings[col]))
            else:
                unmapped_columns.append(col)
        
        print(f"📋 SCNT INVOICE 컬럼 매핑 결과:")
        print(f"   ✅ 매핑 성공: {len(mapped_columns)}개")
        print(f"   ❌ 매핑 실패: {len(unmapped_columns)}개")
        print(f"   📊 매핑 성공률: {len(mapped_columns)/len(df.columns)*100:.1f}%")
        
        if mapped_columns:
            print(f"\n✅ 성공적으로 매핑된 컬럼:")
            for original, mapped in mapped_columns:
                print(f"   {original} → {mapped}")
        
        if unmapped_columns:
            print(f"\n❌ 매핑되지 않은 컬럼:")
            for col in unmapped_columns[:15]:  # 처음 15개만 표시
                print(f"   • {col}")
            if len(unmapped_columns) > 15:
                print(f"   ... 및 {len(unmapped_columns) - 15}개 추가")
        
        # 데이터 품질 분석
        print(f"\n📊 데이터 품질 분석:")
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        data_completeness = ((total_cells - missing_cells) / total_cells) * 100
        print(f"   📊 데이터 완전성: {data_completeness:.1f}%")
        print(f"   📊 중복 행: {df.duplicated().sum()}개")
        
        # 비즈니스 인사이트
        print(f"\n💼 비즈니스 인사이트:")
        if 'Type' in df.columns:
            type_counts = df['Type'].value_counts()
            print(f"   📦 선적 타입 분포: {dict(type_counts)}")
        
        if 'POL' in df.columns and 'POD' in df.columns:
            routes = df.groupby(['POL', 'POD']).size().head(3)
            print(f"   🚢 주요 운송 경로 (상위 3개):")
            for (pol, pod), count in routes.items():
                print(f"      {pol} → {pod}: {count}건")
        
        # RDF 변환
        print(f"\n🔗 SCNT INVOICE 데이터를 RDF로 변환 중...")
        rdf_triples = generate_rdf_triples(df, mapped_columns, mapping_rules)
        print(f"✅ SCNT INVOICE RDF 변환 완료: {len(df)}개 이벤트")
        
        # SPARQL 쿼리 생성
        print(f"🔍 SCNT INVOICE 전용 SPARQL 쿼리 생성 중...")
        sparql_queries = generate_enhanced_sparql_queries(df, mapped_columns)
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("rdf_output")
        output_dir.mkdir(exist_ok=True)
        
        # TTL 파일 저장
        ttl_file = output_dir / f"scnt_invoice_fixed_{len(df)}records_{timestamp}.ttl"
        with open(ttl_file, 'w', encoding='utf-8') as f:
            f.write(rdf_triples)
        print(f"✅ SCNT INVOICE RDF/TTL 저장: {ttl_file}")
        print(f"   📊 파일 크기: {ttl_file.stat().st_size / 1024**2:.2f}MB")
        
        # SPARQL 쿼리 저장
        sparql_file = output_dir / f"scnt_invoice_fixed_queries_{len(df)}records_{timestamp}.sparql"
        with open(sparql_file, 'w', encoding='utf-8') as f:
            f.write(sparql_queries)
        print(f"✅ SCNT INVOICE SPARQL 쿼리 저장: {sparql_file}")
        
        # 통계 저장
        stats_content = generate_enhanced_stats_report(df, mapped_columns, unmapped_columns, data_completeness)
        stats_file = output_dir / f"scnt_invoice_fixed_stats_{timestamp}.md"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(stats_content)
        print(f"✅ SCNT INVOICE 통계 저장: {stats_file}")
        
        print(f"\n🎉 SCNT INVOICE 매핑 완료!")
        print("=" * 70)
        print(f"📊 최종 통계:")
        print(f"   • 총 레코드 수: {len(df):,}개")
        print(f"   • 유효 컬럼 수: {len(df.columns)}개")
        print(f"   • 매핑 성공: {len(mapped_columns)}개 컬럼 ({len(mapped_columns)/len(df.columns)*100:.1f}%)")
        print(f"   • 매핑 실패: {len(unmapped_columns)}개 컬럼")
        print(f"   • 데이터 완전성: {data_completeness:.1f}%")
        
        print(f"\n📁 생성된 파일:")
        print(f"   • RDF/TTL: {ttl_file.name}")
        print(f"   • SPARQL: {sparql_file.name}")
        print(f"   • 통계: {stats_file.name}")
        
        print(f"\n🔧 추천 명령어:")
        print(f"/cmd_scnt_query_fixed [개선된 SCNT INVOICE 쿼리 실행]")
        print(f"/cmd_scnt_route_analysis [운송 경로 분석]")
        print(f"/cmd_scnt_cost_analysis [비용 구조 분석]")
        print(f"/cmd_export_scnt_dashboard [대시보드 생성]")
        
    except Exception as e:
        logger.error(f"SCNT INVOICE 분석 중 오류 발생: {str(e)}")
        print(f"❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def create_scnt_specific_mapping(columns):
    """SCNT 특화 매핑 규칙 생성"""
    scnt_mapping = {
        'S/No': 'hasSerialNumber',
        'Shpt Ref': 'hasShipmentReference',
        'Job #': 'hasJobNumber',
        'Type': 'hasShipmentType',
        'BL #': 'hasBillOfLading',
        'POL': 'hasPortOfLoading',
        'POD': 'hasPortOfDischarge',
        'Mode': 'hasTransportMode',
        'No. Of CNTR': 'hasContainerCount',
        'Volume': 'hasVolume',
        'Quantity': 'hasQuantity',
        'BOE': 'hasBOE',
        'BOE Issued Date': 'hasBOEIssuedDate',
        '# Trips': 'hasTripCount',
        'MASTER DO\\nCHARGE': 'hasMasterDOCharge',
        'CUSTOMS\\nCLEARANCE\\nCHARGE': 'hasCustomsClearanceCharge',
        'HOUSE\\nDO\\nCHARGE': 'hasHouseDOCharge',
        'PORT HANDLING CHARGE': 'hasPortHandlingCharge',
        'TRANSPORTATION\\nCHARGE': 'hasTransportationCharge',
        'ADDITIONAL AMOUNT\\n(Please refer to the detail sheet)': 'hasAdditionalAmount',
        'AT COST AMOUNT': 'hasAtCostAmount',
        'GRAND TOTAL (USD)': 'hasGrandTotal',
        'Remarks': 'hasRemarks',
        'Reviewed by SCT': 'hasReviewedBySCT',
        'Difference': 'hasDifference'
    }
    
    # 실제 컬럼명과 매칭되는 것만 반환
    return {col: mapping for col, mapping in scnt_mapping.items() if col in columns}

def generate_rdf_triples(df, mapped_columns, mapping_rules):
    """RDF 트리플 생성 (개선 버전)"""
    namespace = mapping_rules.get('namespace', 'http://samsung.com/project-logistics#')
    
    rdf_content = f"""@prefix : <{namespace}> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# SCNT SHIPMENT DRAFT INVOICE (APRIL 2025_CHA) 온톨로지 데이터 (개선 버전)
# 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 총 레코드: {len(df):,}개
# 매핑된 속성: {len(mapped_columns)}개

"""
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="SCNT INVOICE 처리"):
        event_uri = f":SCNTInvoiceEvent_{idx+1:06d}"
        rdf_content += f"\n{event_uri} rdf:type :SCNTInvoiceEvent ;\n"
        rdf_content += f"    :hasRecordIndex {idx+1} ;\n"
        
        for original_col, rdf_property in mapped_columns:
            value = row[original_col]
            if pd.notna(value):
                if isinstance(value, (int, float)):
                    if not np.isnan(value):
                        rdf_content += f"    :{rdf_property} {value} ;\n"
                elif isinstance(value, str):
                    escaped_value = value.replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
                    rdf_content += f"    :{rdf_property} \"{escaped_value}\" ;\n"
                elif hasattr(value, 'strftime'):  # datetime
                    rdf_content += f"    :{rdf_property} \"{value.strftime('%Y-%m-%d')}\"^^xsd:date ;\n"
                else:
                    rdf_content += f"    :{rdf_property} \"{str(value)}\" ;\n"
        
        rdf_content = rdf_content.rstrip(' ;\n') + " .\n"
    
    return rdf_content

def generate_enhanced_sparql_queries(df, mapped_columns):
    """향상된 SPARQL 쿼리 생성"""
    queries = f"""# SCNT SHIPMENT DRAFT INVOICE (APRIL 2025_CHA) SPARQL 쿼리 (개선 버전)
# 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 총 레코드: {len(df):,}개
# 매핑된 속성: {len(mapped_columns)}개

PREFIX : <http://samsung.com/project-logistics#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# 1. 전체 SCNT 인보이스 이벤트 조회
SELECT ?event ?property ?value WHERE {{
    ?event rdf:type :SCNTInvoiceEvent .
    ?event ?property ?value .
}} LIMIT 100

# 2. SCNT 인보이스 이벤트 수 조회
SELECT (COUNT(?event) AS ?totalEvents) WHERE {{
    ?event rdf:type :SCNTInvoiceEvent .
}}

# 3. 운송 경로별 집계
SELECT ?pol ?pod (COUNT(?event) AS ?shipmentCount) WHERE {{
    ?event rdf:type :SCNTInvoiceEvent .
    ?event :hasPortOfLoading ?pol .
    ?event :hasPortOfDischarge ?pod .
}} GROUP BY ?pol ?pod
ORDER BY DESC(?shipmentCount)

# 4. 총 비용 분석
SELECT ?event ?grandTotal WHERE {{
    ?event rdf:type :SCNTInvoiceEvent .
    ?event :hasGrandTotal ?grandTotal .
    FILTER(?grandTotal > 0)
}} ORDER BY DESC(?grandTotal)

# 5. 컨테이너 타입별 분석
SELECT ?transportMode (COUNT(?event) AS ?count) WHERE {{
    ?event rdf:type :SCNTInvoiceEvent .
    ?event :hasTransportMode ?transportMode .
}} GROUP BY ?transportMode

"""
    
    # 매핑된 컬럼별 특화 쿼리 생성
    for i, (original_col, rdf_property) in enumerate(mapped_columns[:3], 6):
        queries += f"""
# {i}. {original_col} 기준 분석
SELECT ?event ?{rdf_property.lower()} WHERE {{
    ?event rdf:type :SCNTInvoiceEvent .
    ?event :{rdf_property} ?{rdf_property.lower()} .
    FILTER(?{rdf_property.lower()} != "")
}} LIMIT 50
"""
    
    return queries

def generate_enhanced_stats_report(df, mapped_columns, unmapped_columns, data_completeness):
    """향상된 통계 리포트 생성"""
    return f"""# SCNT SHIPMENT DRAFT INVOICE (APRIL 2025_CHA) 분석 리포트 (개선 버전)

## 📊 기본 통계
- **총 레코드 수**: {len(df):,}개
- **총 컬럼 수**: {len(df.columns)}개
- **매핑 성공**: {len(mapped_columns)}개 컬럼 ({len(mapped_columns)/len(df.columns)*100:.1f}%)
- **매핑 실패**: {len(unmapped_columns)}개 컬럼 ({len(unmapped_columns)/len(df.columns)*100:.1f}%)
- **메모리 사용량**: {df.memory_usage(deep=True).sum() / 1024**2:.2f}MB
- **데이터 완전성**: {data_completeness:.1f}%

## ✅ 매핑된 컬럼
{chr(10).join([f"- {orig} → {mapped}" for orig, mapped in mapped_columns])}

## ❌ 매핑되지 않은 컬럼
{chr(10).join([f"- {col}" for col in unmapped_columns[:20]])}
{f"... 및 {len(unmapped_columns) - 20}개 추가" if len(unmapped_columns) > 20 else ""}

## 📈 데이터 품질
- **결측값 있는 컬럼**: {df.isnull().any().sum()}개
- **완전한 컬럼**: {(~df.isnull().any()).sum()}개
- **중복 행**: {df.duplicated().sum()}개
- **전체 셀 수**: {len(df) * len(df.columns):,}개
- **결측 셀 수**: {df.isnull().sum().sum():,}개

## 💼 비즈니스 인사이트
{f"- **선적 타입 분포**: {dict(df['Type'].value_counts()) if 'Type' in df.columns else 'N/A'}"} 
{f"- **주요 운송 경로**: {dict(df.groupby(['POL', 'POD']).size().head(3)) if 'POL' in df.columns and 'POD' in df.columns else 'N/A'}"}
{f"- **평균 컨테이너 수**: {df['No. Of CNTR'].mean():.1f}개" if 'No. Of CNTR' in df.columns else ''}
{f"- **총 볼륨**: {df['Volume'].sum():.2f}" if 'Volume' in df.columns else ''}

생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

if __name__ == "__main__":
    analyze_scnt_invoice_fixed() 