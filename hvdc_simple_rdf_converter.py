#!/usr/bin/env python3
"""
HVDC Simple RDF Converter (No rdflib dependency)
Excel 파일을 RDF/TTL 형식으로 변환하는 간단한 스크립트
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import warnings
warnings.filterwarnings('ignore')

# 네임스페이스 정의
PREFIXES = """@prefix ex: <http://samsung.com/project-logistics#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

# 필드 매핑 규칙
FIELD_MAPPINGS = {
    "Case No.": "hasCase",
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
    "Status": "hasStatus",
    "wh handling": "hasWHHandling"
}

def sanitize_uri(text):
    """URI에 안전한 문자열로 변환"""
    if pd.isna(text):
        return "unknown"
    
    # 문자열로 변환
    text = str(text)
    
    # 특수 문자 제거 및 변환
    text = re.sub(r'[^\w\-_.]', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    
    return text or "unknown"

def format_literal(value):
    """값을 RDF 리터럴로 포맷팅"""
    if pd.isna(value):
        return None
    
    if isinstance(value, (int, np.integer)):
        return f'"{int(value)}"^^xsd:integer'
    elif isinstance(value, (float, np.floating)):
        if np.isnan(value):
            return None
        return f'"{float(value)}"^^xsd:decimal'
    elif isinstance(value, datetime):
        return f'"{value.strftime("%Y-%m-%d")}"^^xsd:date'
    elif isinstance(value, pd.Timestamp):
        return f'"{value.strftime("%Y-%m-%d")}"^^xsd:date'
    else:
        # 문자열 처리
        text = str(value).replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
        return f'"{text}"'

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

def create_rdf_content(df, source_file):
    """DataFrame을 RDF TTL 내용으로 변환"""
    print(f"🔗 RDF 내용 생성 시작: {source_file}")
    
    rdf_content = [PREFIXES]
    
    # 온톨로지 클래스 정의
    rdf_content.append("# 온톨로지 클래스 정의\n")
    rdf_content.append("ex:TransportEvent rdf:type owl:Class ;\n")
    rdf_content.append('    rdfs:label "운송 이벤트"@ko .\n\n')
    
    rdf_content.append("ex:HitachiCargo rdf:type owl:Class ;\n")
    rdf_content.append('    rdfs:label "히타치 화물"@ko ;\n')
    rdf_content.append("    rdfs:subClassOf ex:TransportEvent .\n\n")
    
    rdf_content.append("ex:SiemensCargo rdf:type owl:Class ;\n")
    rdf_content.append('    rdfs:label "지멘스 화물"@ko ;\n')
    rdf_content.append("    rdfs:subClassOf ex:TransportEvent .\n\n")
    
    # 속성 정의
    rdf_content.append("# 속성 정의\n")
    for field, prop in FIELD_MAPPINGS.items():
        rdf_content.append(f"ex:{prop} rdf:type owl:DatatypeProperty ;\n")
        rdf_content.append(f'    rdfs:label "{field}"@ko .\n\n')
    
    # 인스턴스 데이터
    rdf_content.append("# 인스턴스 데이터\n")
    
    for idx, row in df.iterrows():
        case_no = sanitize_uri(row.get('Case No.', f"case_{idx+1}"))
        event_uri = f"ex:TransportEvent_{case_no}"
        
        rdf_content.append(f"{event_uri} rdf:type ex:TransportEvent")
        
        # 벤더별 클래스 추가
        if 'HVDC CODE 3' in row and pd.notna(row['HVDC CODE 3']):
            vendor = str(row['HVDC CODE 3']).strip().upper()
            if vendor == 'HE':
                rdf_content.append(f" , ex:HitachiCargo")
            elif vendor == 'SIM':
                rdf_content.append(f" , ex:SiemensCargo")
        
        rdf_content.append(" ;\n")
        
        # 데이터 소스 추가
        rdf_content.append(f'    ex:hasDataSource "{source_file}" ;\n')
        
        # 각 필드 처리
        properties = []
        for col, value in row.items():
            if col not in FIELD_MAPPINGS:
                continue
            
            formatted_value = format_literal(value)
            if formatted_value:
                prop = FIELD_MAPPINGS[col]
                properties.append(f"    ex:{prop} {formatted_value}")
        
        if properties:
            rdf_content.append(" ;\n".join(properties))
        
        rdf_content.append(" .\n\n")
    
    print(f"🔗 RDF 내용 생성 완료: {len(df)} 레코드")
    
    return "".join(rdf_content)

def save_rdf_file(content, output_file):
    """RDF 내용을 TTL 파일로 저장"""
    print(f"💾 RDF 파일 저장: {output_file}")
    
    # 출력 디렉토리 생성
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # TTL 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    file_size = Path(output_file).stat().st_size
    print(f"✅ RDF 파일 저장 완료: {file_size:,} bytes")

def create_summary_report(df_list, output_dir):
    """요약 보고서 생성"""
    total_records = sum(len(df) for df in df_list)
    
    report_content = f"""# HVDC RDF 변환 보고서

생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
총 처리 레코드: {total_records:,}

## 파일별 통계
"""
    
    for i, df in enumerate(df_list):
        if i == 0:
            filename = "HVDC WAREHOUSE_HITACHI(HE)"
        else:
            filename = "HVDC WAREHOUSE_SIMENSE(SIM)"
        
        report_content += f"### {filename}\n"
        report_content += f"- 레코드 수: {len(df):,}\n"
        
        # 벤더별 통계
        if 'HVDC CODE 3' in df.columns:
            vendor_stats = df['HVDC CODE 3'].value_counts()
            for vendor, count in vendor_stats.items():
                report_content += f"- {vendor}: {count:,}개\n"
        
        # CBM 통계
        if 'CBM' in df.columns:
            cbm_stats = df['CBM'].describe()
            report_content += f"- CBM 평균: {cbm_stats['mean']:.2f}\n"
            report_content += f"- CBM 최대: {cbm_stats['max']:.2f}\n"
        
        report_content += "\n"
    
    report_content += f"""## 생성된 파일
- HVDC WAREHOUSE_HITACHI(HE).ttl
- HVDC WAREHOUSE_SIMENSE(SIM).ttl
- HVDC_COMBINED.ttl

## 추천 명령어
- `/validate-data comprehensive --sparql-rules`
- `/semantic-search --query="RDF conversion"`
- `/warehouse-status --include-capacity`
"""
    
    # 보고서 저장
    report_file = output_dir / "conversion_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📋 보고서 생성: {report_file}")

def main():
    """메인 함수"""
    print("🚀 HVDC Excel to RDF 변환 시작 (Simple Version)")
    print("=" * 50)
    
    # 입력 파일 정의
    input_files = [
        "data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
    ]
    
    # 출력 디렉토리 생성
    output_dir = Path("rdf_output")
    output_dir.mkdir(exist_ok=True)
    
    # 통합 내용 저장용
    combined_content = [PREFIXES]
    processed_dfs = []
    
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
        processed_dfs.append(df)
        
        # RDF 내용 생성
        rdf_content = create_rdf_content(df, Path(input_file).stem)
        
        # 개별 파일 저장
        output_file = output_dir / f"{Path(input_file).stem}.ttl"
        save_rdf_file(rdf_content, str(output_file))
        
        # 통합 내용에 추가 (접두사 제외)
        content_without_prefix = rdf_content.replace(PREFIXES, "")
        combined_content.append(content_without_prefix)
        
        print(f"✅ {input_file} 처리 완료")
    
    # 통합 파일 저장
    if len(combined_content) > 1:
        combined_output = output_dir / "HVDC_COMBINED.ttl"
        save_rdf_file("".join(combined_content), str(combined_output))
        print(f"✅ 통합 파일 저장: {combined_output}")
    
    # 요약 보고서 생성
    if processed_dfs:
        create_summary_report(processed_dfs, output_dir)
    
    print(f"\n🎉 변환 완료!")
    print(f"📊 총 처리 레코드: {sum(len(df) for df in processed_dfs):,}")
    print(f"💾 출력 디렉토리: {output_dir}")
    
    print(f"\n🔧 추천 명령어:")
    print(f"  /validate-data comprehensive --sparql-rules")
    print(f"  /semantic-search --query='RDF conversion'")
    print(f"  /warehouse-status --include-capacity")

if __name__ == "__main__":
    main() 