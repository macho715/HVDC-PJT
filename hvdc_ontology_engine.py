# hvdc_ontology_engine.py - 순수 Python 온톨로지 엔진
"""
HVDC 프로젝트 온톨로지 시스템 - Python Only 구현
Palantir 스타일 의미론적 레이어를 rdflib + pandas로 구현
"""

import json
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import sqlite3
from datetime import datetime
import logging

# 네임스페이스 정의
EX = Namespace("/hvdc#")
HVDC = Namespace("/hvdc/ontology#")

@dataclass
class HVDCItem:
    """HVDC 프로젝트 아이템 클래스"""
    hvdc_code: str
    vendor: str
    category: str
    description: str
    weight: float
    dimensions: Dict[str, float]
    location: str
    status: str
    risk_level: str = "NORMAL"
    
    def to_rdf(self, graph: Graph) -> URIRef:
        """RDF 트리플로 변환"""
        item_uri = EX[f"item_{self.hvdc_code}"]
        
        # 기본 클래스 선언
        graph.add((item_uri, RDF.type, HVDC.Item))
        
        # 속성 추가
        graph.add((item_uri, HVDC.hvdcCode, Literal(self.hvdc_code)))
        graph.add((item_uri, HVDC.vendor, Literal(self.vendor)))
        graph.add((item_uri, HVDC.category, Literal(self.category)))
        graph.add((item_uri, HVDC.description, Literal(self.description)))
        graph.add((item_uri, HVDC.weight, Literal(self.weight, datatype=XSD.decimal)))
        graph.add((item_uri, HVDC.currentLocation, Literal(self.location)))
        graph.add((item_uri, HVDC.status, Literal(self.status)))
        graph.add((item_uri, HVDC.riskLevel, Literal(self.risk_level)))
        
        # 중량 기반 자동 분류
        if self.weight > 25000:
            graph.add((item_uri, HVDC.isHeavyItem, Literal(True, datatype=XSD.boolean)))
            
        return item_uri

@dataclass 
class Warehouse:
    """창고 정보 클래스"""
    name: str
    warehouse_type: str  # Indoor, Outdoor, Site, Dangerous
    capacity_sqm: float
    current_utilization: float
    handling_fee: float
    
    def to_rdf(self, graph: Graph) -> URIRef:
        warehouse_uri = EX[f"warehouse_{self.name.replace(' ', '_')}"]
        
        # 창고 타입에 따른 클래스 분류
        if self.warehouse_type == "Indoor":
            graph.add((warehouse_uri, RDF.type, HVDC.IndoorWarehouse))
        elif self.warehouse_type == "Outdoor":
            graph.add((warehouse_uri, RDF.type, HVDC.OutdoorWarehouse))
        elif self.warehouse_type == "Site":
            graph.add((warehouse_uri, RDF.type, HVDC.Site))
        elif self.warehouse_type == "Dangerous":
            graph.add((warehouse_uri, RDF.type, HVDC.DangerousCargoWarehouse))
            
        graph.add((warehouse_uri, HVDC.name, Literal(self.name)))
        graph.add((warehouse_uri, HVDC.capacitySQM, Literal(self.capacity_sqm, datatype=XSD.decimal)))
        graph.add((warehouse_uri, HVDC.currentUtilization, Literal(self.current_utilization, datatype=XSD.decimal)))
        graph.add((warehouse_uri, HVDC.handlingFee, Literal(self.handling_fee, datatype=XSD.decimal)))
        
        return warehouse_uri

class HVDCOntologyEngine:
    """HVDC 온톨로지 엔진 - 순수 Python 구현"""
    
    def __init__(self, db_path: str = "hvdc_ontology.db"):
        self.graph = Graph()
        self.db_path = db_path
        self.init_database()
        self.setup_ontology_schema()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def init_database(self):
        """SQLite 데이터베이스 초기화 (빠른 검색용)"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # 아이템 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                hvdc_code TEXT PRIMARY KEY,
                vendor TEXT,
                category TEXT,
                weight REAL,
                location TEXT,
                status TEXT,
                risk_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 창고 테이블  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warehouses (
                name TEXT PRIMARY KEY,
                warehouse_type TEXT,
                capacity_sqm REAL,
                current_utilization REAL,
                handling_fee REAL
            )
        ''')
        
        # 검증 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT,
                validation_type TEXT,
                status TEXT,
                message TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def setup_ontology_schema(self):
        """온톨로지 스키마 정의"""
        # 클래스 정의
        self.graph.add((HVDC.Item, RDF.type, OWL.Class))
        self.graph.add((HVDC.Warehouse, RDF.type, OWL.Class))
        self.graph.add((HVDC.IndoorWarehouse, RDFS.subClassOf, HVDC.Warehouse))
        self.graph.add((HVDC.OutdoorWarehouse, RDFS.subClassOf, HVDC.Warehouse))
        self.graph.add((HVDC.Site, RDFS.subClassOf, HVDC.Warehouse))
        self.graph.add((HVDC.DangerousCargoWarehouse, RDFS.subClassOf, HVDC.Warehouse))
        
        # 프로퍼티 정의
        self.graph.add((HVDC.storedAt, RDF.type, OWL.ObjectProperty))
        self.graph.add((HVDC.storedAt, RDFS.domain, HVDC.Item))
        self.graph.add((HVDC.storedAt, RDFS.range, HVDC.Warehouse))
        
        self.logger.info("온톨로지 스키마 초기화 완료")
        
    def add_item(self, item: HVDCItem) -> bool:
        """아이템을 온톨로지에 추가"""
        try:
            # RDF 그래프에 추가
            item_uri = item.to_rdf(self.graph)
            
            # SQLite에도 저장 (빠른 검색용)
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO items 
                (hvdc_code, vendor, category, weight, location, status, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (item.hvdc_code, item.vendor, item.category, item.weight, 
                  item.location, item.status, item.risk_level))
            
            self.conn.commit()
            self.logger.info(f"아이템 {item.hvdc_code} 추가 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"아이템 추가 실패: {e}")
            return False
            
    def add_warehouse(self, warehouse: Warehouse) -> bool:
        """창고를 온톨로지에 추가"""
        try:
            warehouse_uri = warehouse.to_rdf(self.graph)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO warehouses 
                (name, warehouse_type, capacity_sqm, current_utilization, handling_fee)
                VALUES (?, ?, ?, ?, ?)
            ''', (warehouse.name, warehouse.warehouse_type, warehouse.capacity_sqm,
                  warehouse.current_utilization, warehouse.handling_fee))
            
            self.conn.commit()
            self.logger.info(f"창고 {warehouse.name} 추가 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"창고 추가 실패: {e}")
            return False
    
    def sparql_query(self, query: str) -> List[Dict]:
        """SPARQL 쿼리 실행 (rdflib 사용)"""
        try:
            results = []
            for row in self.graph.query(query):
                result_dict = {}
                for i, var in enumerate(row.labels):
                    result_dict[str(var)] = str(row[i])
                results.append(result_dict)
            return results
        except Exception as e:
            self.logger.error(f"SPARQL 쿼리 실패: {e}")
            return []
            
    def validate_weight_consistency(self, hvdc_code: str) -> Dict[str, Any]:
        """중량 일관성 검증"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT weight FROM items WHERE hvdc_code = ?', (hvdc_code,))
        result = cursor.fetchone()
        
        if not result:
            return {"status": "NOT_FOUND", "message": "아이템을 찾을 수 없습니다"}
            
        weight = result[0]
        confidence_score = 0.95  # 기본값
        
        # 중량 기반 위험도 평가
        if weight > 25000:
            risk_level = "HIGH"
            message = "중량물 특수 취급 필요"
        elif weight > 10000:
            risk_level = "MEDIUM"  
            message = "일반 중량물"
        else:
            risk_level = "LOW"
            message = "표준 중량"
            
        # 검증 결과 저장
        cursor.execute('''
            INSERT INTO validation_results 
            (item_code, validation_type, status, message, confidence_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (hvdc_code, "WEIGHT_CHECK", risk_level, message, confidence_score))
        
        self.conn.commit()
        
        return {
            "status": "SUCCESS",
            "risk_level": risk_level,
            "message": message,
            "weight": weight,
            "confidence_score": confidence_score
        }
        
    def get_warehouse_utilization(self) -> pd.DataFrame:
        """창고 사용률 분석"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT name, warehouse_type, capacity_sqm, current_utilization,
                   (current_utilization / capacity_sqm * 100) as utilization_percent
            FROM warehouses
            ORDER BY utilization_percent DESC
        ''')
        
        columns = ['name', 'warehouse_type', 'capacity_sqm', 'current_utilization', 'utilization_percent']
        df = pd.DataFrame(cursor.fetchall(), columns=columns)
        
        return df
        
    def semantic_search(self, query_text: str) -> List[Dict]:
        """간단한 시맨틱 검색 (키워드 기반)"""
        keywords = query_text.lower().split()
        
        # SQL 검색 (빠른 텍스트 매칭)
        cursor = self.conn.cursor()
        where_clauses = []
        params = []
        
        for keyword in keywords:
            where_clauses.append('''
                (LOWER(hvdc_code) LIKE ? OR 
                 LOWER(vendor) LIKE ? OR 
                 LOWER(category) LIKE ? OR
                 LOWER(location) LIKE ?)
            ''')
            param = f'%{keyword}%'
            params.extend([param, param, param, param])
            
        query = f'''
            SELECT hvdc_code, vendor, category, location, weight, status
            FROM items 
            WHERE {' AND '.join(where_clauses)}
            LIMIT 20
        '''
        
        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            results.append({
                'hvdc_code': row[0],
                'vendor': row[1], 
                'category': row[2],
                'location': row[3],
                'weight': row[4],
                'status': row[5]
            })
            
        return results
        
    def export_to_turtle(self, filepath: str = "hvdc_ontology.ttl"):
        """온톨로지를 Turtle 형식으로 내보내기"""
        try:
            self.graph.serialize(destination=filepath, format='turtle')
            self.logger.info(f"온톨로지 내보내기 완료: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"내보내기 실패: {e}")
            return False
            
    def load_from_excel(self, filepath: str, sheet_name: str = 'Sheet1') -> int:
        """Excel 파일에서 데이터 로드"""
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            count = 0
            
            for _, row in df.iterrows():
                item = HVDCItem(
                    hvdc_code=str(row.get('HVDC Code', f'ITEM_{count:04d}')),
                    vendor=str(row.get('Vendor', 'Unknown')),
                    category=str(row.get('Category', 'General')),
                    description=str(row.get('Description', '')),
                    weight=float(row.get('Weight', 0)),
                    dimensions={'length': 0, 'width': 0, 'height': 0},
                    location=str(row.get('Location', 'Unknown')),
                    status=str(row.get('Status', 'warehouse'))
                )
                
                if self.add_item(item):
                    count += 1
                    
            self.logger.info(f"Excel에서 {count}개 아이템 로드 완료")
            return count
            
        except Exception as e:
            self.logger.error(f"Excel 로드 실패: {e}")
            return 0

# 사용 예시 및 테스트
if __name__ == "__main__":
    # 온톨로지 엔진 초기화
    engine = HVDCOntologyEngine()
    
    # 샘플 데이터 추가
    sample_item = HVDCItem(
        hvdc_code="HVDC-ADOPT-HE-0001",
        vendor="Hitachi",
        category="Elec",
        description="Main Converter Unit",
        weight=35000.0,
        dimensions={"length": 12.0, "width": 3.0, "height": 2.5},
        location="DSV Indoor",
        status="warehouse"
    )
    
    sample_warehouse = Warehouse(
        name="DSV Indoor",
        warehouse_type="Indoor",
        capacity_sqm=10000.0,
        current_utilization=8500.0,
        handling_fee=50.0
    )
    
    # 데이터 추가
    engine.add_item(sample_item)
    engine.add_warehouse(sample_warehouse)
    
    # 검증 실행
    validation_result = engine.validate_weight_consistency("HVDC-ADOPT-HE-0001")
    print("검증 결과:", validation_result)
    
    # 창고 사용률 분석
    utilization_df = engine.get_warehouse_utilization()
    print("\n창고 사용률:")
    print(utilization_df)
    
    # 시맨틱 검색
    search_results = engine.semantic_search("Hitachi converter")
    print("\n검색 결과:")
    for result in search_results:
        print(result)
    
    # 온톨로지 내보내기
    engine.export_to_turtle("sample_hvdc.ttl")
    
    print("\n✅ HVDC 온톨로지 엔진 테스트 완료")