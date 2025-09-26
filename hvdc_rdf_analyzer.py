#!/usr/bin/env python3
"""
HVDC RDF Analyzer - Excel to RDF Conversion and SPARQL Analysis
통합 Excel → RDF 변환 및 SPARQL 분석 시스템

Features:
- Excel 파일 → RDF 변환
- SPARQL 쿼리 실행
- 창고별 CBM 분석
- 물류 데이터 의미론적 분석
"""

import pandas as pd
import numpy as np
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.plugins.sparql import prepareQuery
import json
import os
from pathlib import Path
from datetime import datetime
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
    "DHL Warehouse": "hasWarehouse",
    "DSV Indoor": "hasWarehouse",
    "DSV Al Markaz": "hasWarehouse",
    "DSV Outdoor": "hasWarehouse",
    "AAA  Storage": "hasWarehouse",
    "Hauler Indoor": "hasWarehouse",
    "DSV MZP": "hasWarehouse",
    "MOSB": "hasWarehouse",
    "Shifting": "hasWarehouse",
    "DAS": "hasSite",
    "AGI": "hasSite",
    "SHU": "hasSite",
    "MIR": "hasSite",
    "Logistics Flow Code": "hasLogisticsFlowCode",
    "Status": "hasStatus",
    "wh handling": "hasWHHandling"
}

class HVDCRDFConverter:
    """HVDC Excel to RDF Converter with SPARQL Analysis"""
    
    def __init__(self):
        self.graph = Graph()
        self.setup_namespaces()
        self.setup_ontology_schema()
        
    def setup_namespaces(self):
        """네임스페이스 설정"""
        for prefix, uri in ns.items():
            self.graph.bind(prefix, Namespace(uri))
    
    def setup_ontology_schema(self):
        """기본 온톨로지 스키마 설정"""
        # 기본 클래스 정의
        self.graph.add((EX.TransportEvent, RDF.type, OWL.Class))
        self.graph.add((EX.HitachiCargo, RDFS.subClassOf, EX.TransportEvent))
        self.graph.add((EX.SiemensCargo, RDFS.subClassOf, EX.TransportEvent))
        self.graph.add((EX.Warehouse, RDF.type, OWL.Class))
        self.graph.add((EX.Site, RDF.type, OWL.Class))
        
        # 기본 속성 정의
        for field, prop in FIELD_MAPPINGS.items():
            prop_uri = EX[prop]
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop_uri, RDFS.domain, EX.TransportEvent))
    
    def preprocess_dataframe(self, df, source_name=""):
        """데이터프레임 전처리"""
        print(f"🔄 데이터 전처리 시작: {source_name}")
        
        # 기본 전처리
        df = df.copy()
        
        # 날짜 컬럼 처리
        date_columns = ['ETA', 'ETD', 'Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 수치형 컬럼 처리
        numeric_columns = ['CBM', 'N.W(kgs)', 'G.W(kgs)', 'L(CM)', 'W(CM)', 'H(CM)', 'Pkg']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # CBM 양수 보정
        if 'CBM' in df.columns:
            cbm_mean = df['CBM'].mean()
            df.loc[df['CBM'] <= 0, 'CBM'] = cbm_mean
            print(f"   CBM 보정: ≤0 값 → 평균값 {cbm_mean:.2f} 대체")
        
        # 패키지 수 보정
        if 'Pkg' in df.columns:
            df['Pkg'] = df['Pkg'].fillna(1)
        
        # 벤더 필터링 (HE, SIM만 유지)
        if 'HVDC CODE 3' in df.columns:
            initial_count = len(df)
            df = df[df['HVDC CODE 3'].isin(['HE', 'SIM'])].copy()
            print(f"   벤더 필터링: {initial_count} → {len(df)} 레코드")
        
        # 중복 제거
        if 'Case No.' in df.columns:
            initial_count = len(df)
            df = df.drop_duplicates(subset=['Case No.'], keep='first')
            removed = initial_count - len(df)
            if removed > 0:
                print(f"   중복 제거: {removed}개 중복 케이스 제거")
        
        # 데이터 소스 추가
        df['data_source'] = source_name
        
        print(f"✅ 전처리 완료: {len(df)} 레코드")
        return df
    
    def convert_excel_to_rdf(self, excel_file, sheet_name='Case List'):
        """Excel 파일을 RDF로 변환"""
        print(f"🚀 Excel → RDF 변환 시작: {excel_file}")
        
        # Excel 파일 읽기
        if not Path(excel_file).exists():
            # data 디렉토리에서 찾기
            data_path = Path("data") / excel_file
            if data_path.exists():
                excel_file = str(data_path)
            else:
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {excel_file}")
        
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            print(f"📊 데이터 로드: {len(df)} 레코드")
        except Exception as e:
            print(f"❌ Excel 파일 읽기 실패: {e}")
            return None
        
        # 데이터 전처리
        df = self.preprocess_dataframe(df, Path(excel_file).stem)
        
        # RDF 변환
        self.create_rdf_from_dataframe(df, Path(excel_file).stem)
        
        print(f"✅ RDF 변환 완료: {len(self.graph)} 트리플 생성")
        return self.graph
    
    def create_rdf_from_dataframe(self, df, source_name):
        """DataFrame을 RDF로 변환"""
        print(f"🔗 RDF 그래프 생성 중: {source_name}")
        
        warehouse_columns = ['DHL Warehouse', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                           'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'Shifting']
        site_columns = ['DAS', 'AGI', 'SHU', 'MIR']
        
        for idx, row in df.iterrows():
            # TransportEvent URI 생성
            case_no = str(row.get('Case No.', f"case_{idx+1}")).replace(' ', '_')
            event_uri = EX[f"TransportEvent_{case_no}"]
            
            # 기본 클래스 추가
            self.graph.add((event_uri, RDF.type, EX.TransportEvent))
            
            # 벤더별 화물 클래스 추가
            if 'HVDC CODE 3' in row and pd.notna(row['HVDC CODE 3']):
                vendor = str(row['HVDC CODE 3']).strip().upper()
                if vendor == 'HE':
                    self.graph.add((event_uri, RDF.type, EX.HitachiCargo))
                elif vendor == 'SIM':
                    self.graph.add((event_uri, RDF.type, EX.SiemensCargo))
            
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
                
                self.graph.add((event_uri, property_uri, literal))
            
            # 창고 정보 추가 (날짜가 있는 창고들)
            warehouses = []
            for warehouse_col in warehouse_columns:
                if warehouse_col in row and pd.notna(row[warehouse_col]):
                    warehouses.append(warehouse_col)
            
            # 현장 정보 추가 (날짜가 있는 현장들)
            sites = []
            for site_col in site_columns:
                if site_col in row and pd.notna(row[site_col]):
                    sites.append(site_col)
            
            # 주요 창고 정보 추가
            if warehouses:
                primary_warehouse = warehouses[0]  # 첫 번째 창고를 주요 창고로
                self.graph.add((event_uri, EX.hasWarehouse, Literal(primary_warehouse)))
            
            # 주요 현장 정보 추가
            if sites:
                primary_site = sites[0]  # 첫 번째 현장을 주요 현장으로
                self.graph.add((event_uri, EX.hasSite, Literal(primary_site)))
    
    def query(self, sparql_query):
        """SPARQL 쿼리 실행"""
        try:
            # 네임스페이스 접두사 추가
            full_query = f"""
            PREFIX ex: <{EX}>
            PREFIX rdf: <{RDF}>
            PREFIX rdfs: <{RDFS}>
            PREFIX owl: <{OWL}>
            PREFIX xsd: <{XSD}>
            
            {sparql_query}
            """
            
            results = self.graph.query(full_query)
            return results
        except Exception as e:
            print(f"❌ SPARQL 쿼리 실행 실패: {e}")
            return None
    
    def analyze_warehouse_cbm(self):
        """창고별 CBM 분석"""
        print("📊 창고별 CBM 분석 시작")
        
        sparql_query = """
        SELECT ?warehouse (AVG(?cbm) as ?avg_cbm) (COUNT(?event) as ?count) (SUM(?cbm) as ?total_cbm) WHERE {
            ?event rdf:type ex:TransportEvent .
            ?event ex:hasWarehouse ?warehouse .
            ?event ex:hasCubicMeter ?cbm .
            FILTER(?cbm > 0)
        } GROUP BY ?warehouse
        ORDER BY DESC(?avg_cbm)
        """
        
        results = self.query(sparql_query)
        
        if results:
            print("\n📈 창고별 CBM 분석 결과:")
            print("-" * 70)
            print(f"{'창고명':<20} {'평균 CBM':<12} {'총 CBM':<12} {'건수':<8}")
            print("-" * 70)
            
            for row in results:
                warehouse = str(row.warehouse)
                avg_cbm = float(row.avg_cbm)
                total_cbm = float(row.total_cbm) if row.total_cbm else 0
                count = int(row.count)
                
                print(f"{warehouse:<20} {avg_cbm:<12.2f} {total_cbm:<12.2f} {count:<8}")
        
        return results
    
    def analyze_vendor_distribution(self):
        """벤더별 분포 분석"""
        print("\n📊 벤더별 분포 분석 시작")
        
        sparql_query = """
        SELECT ?vendor (COUNT(?event) as ?count) (AVG(?cbm) as ?avg_cbm) WHERE {
            ?event rdf:type ex:TransportEvent .
            ?event ex:hasHVDCCode3 ?vendor .
            ?event ex:hasCubicMeter ?cbm .
            FILTER(?cbm > 0)
        } GROUP BY ?vendor
        ORDER BY DESC(?count)
        """
        
        results = self.query(sparql_query)
        
        if results:
            print("\n📈 벤더별 분포 분석 결과:")
            print("-" * 50)
            print(f"{'벤더':<10} {'건수':<8} {'평균 CBM':<12}")
            print("-" * 50)
            
            for row in results:
                vendor = str(row.vendor)
                count = int(row.count)
                avg_cbm = float(row.avg_cbm) if row.avg_cbm else 0
                
                print(f"{vendor:<10} {count:<8} {avg_cbm:<12.2f}")
        
        return results
    
    def analyze_large_cargo(self, cbm_threshold=50):
        """대형 화물 분석"""
        print(f"\n📊 대형 화물 분석 (CBM > {cbm_threshold})")
        
        sparql_query = f"""
        SELECT ?event ?case ?cbm ?warehouse ?vendor WHERE {{
            ?event rdf:type ex:TransportEvent .
            ?event ex:hasCase ?case .
            ?event ex:hasCubicMeter ?cbm .
            ?event ex:hasWarehouse ?warehouse .
            ?event ex:hasHVDCCode3 ?vendor .
            FILTER(?cbm > {cbm_threshold})
        }} ORDER BY DESC(?cbm)
        """
        
        results = self.query(sparql_query)
        
        if results:
            print(f"\n📈 대형 화물 분석 결과 (CBM > {cbm_threshold}):")
            print("-" * 80)
            print(f"{'케이스 번호':<20} {'CBM':<8} {'창고':<15} {'벤더':<8}")
            print("-" * 80)
            
            for row in results:
                case = str(row.case)
                cbm = float(row.cbm)
                warehouse = str(row.warehouse)
                vendor = str(row.vendor)
                
                print(f"{case:<20} {cbm:<8.2f} {warehouse:<15} {vendor:<8}")
        
        return results
    
    def comprehensive_analysis(self):
        """종합 분석"""
        print("\n🔍 HVDC 데이터 종합 분석")
        print("=" * 60)
        
        # 기본 통계
        total_events = len(list(self.graph.subjects(RDF.type, EX.TransportEvent)))
        hitachi_events = len(list(self.graph.subjects(RDF.type, EX.HitachiCargo)))
        siemens_events = len(list(self.graph.subjects(RDF.type, EX.SiemensCargo)))
        
        print(f"📊 기본 통계:")
        print(f"   전체 이벤트: {total_events:,}개")
        print(f"   Hitachi 화물: {hitachi_events:,}개")
        print(f"   Siemens 화물: {siemens_events:,}개")
        
        # 창고별 CBM 분석
        warehouse_results = self.analyze_warehouse_cbm()
        
        # 벤더별 분포 분석
        vendor_results = self.analyze_vendor_distribution()
        
        # 대형 화물 분석
        large_cargo_results = self.analyze_large_cargo(50)
        
        return {
            'total_events': total_events,
            'hitachi_events': hitachi_events,
            'siemens_events': siemens_events,
            'warehouse_analysis': warehouse_results,
            'vendor_analysis': vendor_results,
            'large_cargo_analysis': large_cargo_results
        }
    
    def save_rdf(self, output_file):
        """RDF 파일 저장"""
        try:
            self.graph.serialize(destination=output_file, format='turtle')
            print(f"✅ RDF 파일 저장 완료: {output_file}")
            return True
        except Exception as e:
            print(f"❌ RDF 파일 저장 실패: {e}")
            return False


def main():
    """메인 실행 함수"""
    print("🚀 HVDC RDF Analyzer 시작")
    print("=" * 50)
    
    # RDF 변환기 초기화
    converter = HVDCRDFConverter()
    
    # 사용자 요청 코드 구현
    print("\n📝 사용자 요청 코드 실행:")
    print("# Excel 파일 → RDF 변환 → SPARQL 분석")
    
    try:
        # Excel 파일 → RDF 변환
        rdf_graph = converter.convert_excel_to_rdf("HVDC WAREHOUSE_HITACHI(HE).xlsx")
        
        if rdf_graph:
            # SPARQL 쿼리 실행
            print("\n🔍 SPARQL 쿼리 실행:")
            results = converter.query("""
                SELECT ?warehouse (AVG(?cbm) as ?avg_cbm) WHERE {
                    ?event ex:hasWarehouse ?warehouse .
                    ?event ex:hasCubicMeter ?cbm .
                } GROUP BY ?warehouse
            """)
            
            if results:
                print("\n📊 창고별 평균 CBM 결과:")
                print("-" * 40)
                for row in results:
                    warehouse = str(row.warehouse)
                    avg_cbm = float(row.avg_cbm) if row.avg_cbm else 0
                    print(f"{warehouse}: {avg_cbm:.2f} CBM")
            
            # 추가 분석
            print("\n🔍 추가 분석 수행:")
            analysis_results = converter.comprehensive_analysis()
            
            # RDF 파일 저장
            output_file = f"rdf_output/hvdc_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ttl"
            Path(output_file).parent.mkdir(exist_ok=True)
            converter.save_rdf(output_file)
            
            print(f"\n✅ 분석 완료! RDF 파일: {output_file}")
            
        else:
            print("❌ RDF 변환 실패")
            
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        # SIMENSE 파일로 대체 시도
        try:
            print("\n🔄 SIMENSE 파일로 재시도...")
            rdf_graph = converter.convert_excel_to_rdf("HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
            
            if rdf_graph:
                analysis_results = converter.comprehensive_analysis()
                print("✅ SIMENSE 파일 분석 완료")
                
        except Exception as e2:
            print(f"❌ 재시도 실패: {e2}")


if __name__ == "__main__":
    main() 