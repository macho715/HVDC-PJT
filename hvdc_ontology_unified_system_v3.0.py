#!/usr/bin/env python3
"""
HVDC 프로젝트 통합 온톨로지 매핑 시스템 v3.0.0
- 완전 통합된 온톨로지 스키마 및 매핑 규칙
- MACHO-GPT v3.4-mini 표준 준수
- Samsung C&T × ADNOC·DSV Partnership
- OFCO 매핑 규칙 완전 통합
- Status_Location_Date, DHL Warehouse, Stack_Status 지원
"""

import pandas as pd
import numpy as np
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import re
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')

# RDF 라이브러리
try:
    from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
    from rdflib.plugins.sparql import prepareQuery
    RDF_AVAILABLE = True
except ImportError:
    RDF_AVAILABLE = False
    print("⚠️ RDFLib 미설치 - RDF 기능 비활성화")

# 네임스페이스 정의
EX = Namespace("http://samsung.com/project-logistics#")

@dataclass
class OntologyConfig:
    """온톨로지 설정"""
    namespace: str = "http://samsung.com/project-logistics#"
    version: str = "3.0.0"
    schema_file: str = "hvdc_integrated_ontology_schema.ttl"
    mapping_rules_file: str = "hvdc_integrated_mapping_rules_v3.0.json"
    enable_rdf: bool = True
    enable_ofco_mapping: bool = True
    confidence_threshold: float = 0.90

@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence: float = 0.0
    processed_records: int = 0

class HVDCOntologyUnifiedSystem:
    """HVDC 프로젝트 통합 온톨로지 매핑 시스템"""
    
    def __init__(self, config: Optional[OntologyConfig] = None):
        self.config = config or OntologyConfig()
        self.mapping_rules = {}
        self.ofco_rules = {}
        self.graph = None
        self.logger = self._setup_logging()
        
        # 초기화
        self._load_mapping_rules()
        if self.config.enable_rdf and RDF_AVAILABLE:
            self._init_rdf_graph()
        
        # 데이터베이스 초기화
        self._init_database()
        
        self.logger.info(f"HVDC 통합 온톨로지 시스템 v{self.config.version} 초기화 완료")
    
    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger('HVDC_Ontology')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_mapping_rules(self):
        """매핑 규칙 로드"""
        try:
            mapping_file = Path(self.config.mapping_rules_file)
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self.mapping_rules = json.load(f)
                
                # OFCO 규칙 추출
                if 'ofco_mapping_rules' in self.mapping_rules:
                    self.ofco_rules = self.mapping_rules['ofco_mapping_rules']
                
                self.logger.info(f"매핑 규칙 로드 완료: {len(self.mapping_rules.get('field_mappings', {}))}개 필드")
            else:
                self.logger.warning(f"매핑 규칙 파일 미발견: {mapping_file}")
                self._create_default_mapping_rules()
        except Exception as e:
            self.logger.error(f"매핑 규칙 로드 실패: {e}")
            self._create_default_mapping_rules()
    
    def _create_default_mapping_rules(self):
        """기본 매핑 규칙 생성"""
        self.mapping_rules = {
            "namespace": self.config.namespace,
            "version": self.config.version,
            "field_mappings": {
                "Case_No": "hasCase",
                "Date": "hasDate",
                "Location": "hasLocation",
                "Qty": "hasQuantity",
                "Amount": "hasAmount",
                "Category": "hasCategory",
                "Vendor": "hasVendor"
            },
            "property_mappings": {
                "Case_No": {"predicate": "hasCase", "datatype": "xsd:string", "required": True},
                "Date": {"predicate": "hasDate", "datatype": "xsd:dateTime", "required": True},
                "Location": {"predicate": "hasLocation", "datatype": "xsd:string", "required": True},
                "Qty": {"predicate": "hasQuantity", "datatype": "xsd:integer", "required": True}
            }
        }
        self.logger.info("기본 매핑 규칙 생성 완료")
    
    def _init_rdf_graph(self):
        """RDF 그래프 초기화"""
        if not RDF_AVAILABLE:
            return
        
        try:
            self.graph = Graph()
            
            # 스키마 파일 로드
            schema_file = Path(self.config.schema_file)
            if schema_file.exists():
                self.graph.parse(schema_file, format='turtle')
                self.logger.info(f"온톨로지 스키마 로드 완료: {len(self.graph)} 트리플")
            else:
                self.logger.warning(f"스키마 파일 미발견: {schema_file}")
                self._create_default_schema()
        except Exception as e:
            self.logger.error(f"RDF 그래프 초기화 실패: {e}")
            self.graph = None
    
    def _create_default_schema(self):
        """기본 스키마 생성"""
        if not self.graph:
            return
        
        # 기본 클래스 추가
        classes = [
            (EX.TransportEvent, "운송 이벤트"),
            (EX.Warehouse, "창고"),
            (EX.Site, "현장")
        ]
        
        for class_uri, label in classes:
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(label, lang='ko')))
        
        # 기본 속성 추가
        properties = [
            (EX.hasCase, "케이스 번호"),
            (EX.hasDate, "날짜"),
            (EX.hasLocation, "위치"),
            (EX.hasQuantity, "수량")
        ]
        
        for prop_uri, label in properties:
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(label, lang='ko')))
        
        self.logger.info("기본 온톨로지 스키마 생성 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            self.db_path = "hvdc_ontology_unified_v3.db"
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # 통합 데이터 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ontology_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT,
                    case_no TEXT,
                    date_value TEXT,
                    location TEXT,
                    quantity INTEGER,
                    amount REAL,
                    category TEXT,
                    vendor TEXT,
                    flow_code INTEGER,
                    wh_handling INTEGER,
                    rdf_class TEXT,
                    rdf_properties TEXT,
                    validation_status TEXT,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # OFCO 매핑 결과 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ofco_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_text TEXT,
                    matched_pattern TEXT,
                    cost_center_a TEXT,
                    cost_center_b TEXT,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 검증 로그 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    validation_type TEXT,
                    record_count INTEGER,
                    success_count INTEGER,
                    error_count INTEGER,
                    confidence_avg REAL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            self.logger.info("데이터베이스 초기화 완료")
        except Exception as e:
            self.logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def process_excel_data(self, excel_file: str, sheet_name: Optional[str] = None) -> ValidationResult:
        """Excel 데이터 처리"""
        try:
            self.logger.info(f"Excel 파일 처리 시작: {excel_file}")
            
            # Excel 파일 읽기
            if sheet_name:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
            else:
                df = pd.read_excel(excel_file)
            
            self.logger.info(f"데이터 로드 완료: {len(df)}행, {len(df.columns)}열")
            
            # 데이터 전처리
            df = self._preprocess_data(df)
            
            # 온톨로지 매핑 수행
            result = self._map_to_ontology(df)
            
            # RDF 변환 (옵션)
            if self.config.enable_rdf and self.graph:
                self._convert_to_rdf(df)
            
            # OFCO 매핑 수행 (옵션)
            if self.config.enable_ofco_mapping:
                self._apply_ofco_mapping(df)
            
            # 결과 저장
            self._save_results(df, result)
            
            self.logger.info(f"처리 완료: {result.processed_records}건 처리")
            return result
            
        except Exception as e:
            self.logger.error(f"Excel 데이터 처리 실패: {e}")
            return ValidationResult(False, [str(e)])
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 전처리"""
        try:
            original_count = len(df)
            
            # 1. 기본 정규화
            df = df.copy()
            
            # 2. NULL PKG → 1 보정
            if 'pkg' in df.columns:
                df['pkg'] = df['pkg'].fillna(1)
                null_pkg_corrected = df['pkg'].isna().sum()
                if null_pkg_corrected > 0:
                    self.logger.info(f"NULL PKG 보정: {null_pkg_corrected}건")
            
            # 3. Flow Code 6 → 3 정규화
            if 'Logistics Flow Code' in df.columns:
                df.loc[df['Logistics Flow Code'] == 6, 'Logistics Flow Code'] = 3
                flow_6_corrected = (df['Logistics Flow Code'] == 6).sum()
                if flow_6_corrected > 0:
                    self.logger.info(f"Flow Code 6→3 정규화: {flow_6_corrected}건")
            
            # 4. 날짜 정규화
            date_columns = ['Date', 'Start', 'Finish', 'Status_Location_Date', 'Draft Invoice Date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # 5. 벤더 정규화
            if 'Vendor' in df.columns:
                vendor_mappings = self.mapping_rules.get('vendor_mappings', {}).get('normalization', {})
                df['Vendor'] = df['Vendor'].map(vendor_mappings).fillna(df['Vendor'])
            
            # 6. 중복 제거
            dedup_keys = ['Case_No', 'Location', 'Logistics Flow Code', 'pkg']
            available_keys = [key for key in dedup_keys if key in df.columns]
            if len(available_keys) >= 2:
                before_dedup = len(df)
                df = df.drop_duplicates(subset=available_keys, keep='last')
                after_dedup = len(df)
                if before_dedup != after_dedup:
                    self.logger.info(f"중복 제거: {before_dedup - after_dedup}건")
            
            self.logger.info(f"전처리 완료: {original_count}→{len(df)}건")
            return df
            
        except Exception as e:
            self.logger.error(f"데이터 전처리 실패: {e}")
            return df
    
    def _map_to_ontology(self, df: pd.DataFrame) -> ValidationResult:
        """온톨로지 매핑 수행"""
        try:
            errors = []
            warnings = []
            confidence_scores = []
            
            field_mappings = self.mapping_rules.get('field_mappings', {})
            property_mappings = self.mapping_rules.get('property_mappings', {})
            
            # 매핑된 컬럼 확인
            mapped_columns = []
            for col in df.columns:
                if col in field_mappings:
                    mapped_columns.append(col)
                else:
                    warnings.append(f"매핑되지 않은 컬럼: {col}")
            
            self.logger.info(f"매핑 가능한 컬럼: {len(mapped_columns)}개")
            
            # 필수 필드 검증
            required_fields = [
                field for field, props in property_mappings.items()
                if props.get('required', False) and field in df.columns
            ]
            
            for field in required_fields:
                null_count = df[field].isna().sum()
                if null_count > 0:
                    errors.append(f"필수 필드 {field}에 NULL 값 {null_count}개 발견")
            
            # 데이터 타입 검증
            for field, props in property_mappings.items():
                if field not in df.columns:
                    continue
                
                datatype = props.get('datatype', 'xsd:string')
                if datatype == 'xsd:integer':
                    non_numeric = df[~df[field].isna() & ~df[field].astype(str).str.isdigit()]
                    if len(non_numeric) > 0:
                        warnings.append(f"필드 {field}에 비정수 값 {len(non_numeric)}개 발견")
                elif datatype == 'xsd:decimal':
                    non_numeric = df[~df[field].isna() & ~pd.to_numeric(df[field], errors='coerce').notna()]
                    if len(non_numeric) > 0:
                        warnings.append(f"필드 {field}에 비수치 값 {len(non_numeric)}개 발견")
            
            # 신뢰도 계산
            mapped_ratio = len(mapped_columns) / len(df.columns) if df.columns else 0
            error_ratio = len(errors) / max(len(df), 1)
            confidence = (mapped_ratio * 0.7 + (1 - error_ratio) * 0.3)
            
            self.logger.info(f"온톨로지 매핑 완료 - 신뢰도: {confidence:.3f}")
            
            return ValidationResult(
                is_valid=(len(errors) == 0),
                errors=errors,
                warnings=warnings,
                confidence=confidence,
                processed_records=len(df)
            )
            
        except Exception as e:
            self.logger.error(f"온톨로지 매핑 실패: {e}")
            return ValidationResult(False, [str(e)])
    
    def _convert_to_rdf(self, df: pd.DataFrame) -> bool:
        """RDF 변환"""
        if not self.graph:
            return False
        
        try:
            field_mappings = self.mapping_rules.get('field_mappings', {})
            namespace = self.mapping_rules.get('namespace', self.config.namespace)
            
            for idx, row in df.iterrows():
                # 인스턴스 URI 생성
                instance_uri = URIRef(f"{namespace}TransportEvent_{idx:06d}")
                
                # 클래스 할당
                self.graph.add((instance_uri, RDF.type, EX.TransportEvent))
                
                # 속성 추가
                for col, value in row.items():
                    if col in field_mappings and pd.notna(value):
                        predicate_name = field_mappings[col]
                        predicate_uri = URIRef(f"{namespace}{predicate_name}")
                        
                        # 데이터 타입에 따른 리터럴 생성
                        if isinstance(value, (int, np.integer)):
                            literal = Literal(value, datatype=XSD.integer)
                        elif isinstance(value, (float, np.floating)):
                            literal = Literal(value, datatype=XSD.decimal)
                        elif isinstance(value, datetime):
                            literal = Literal(value, datatype=XSD.dateTime)
                        else:
                            literal = Literal(str(value))
                        
                        self.graph.add((instance_uri, predicate_uri, literal))
            
            self.logger.info(f"RDF 변환 완료: {len(df)}개 인스턴스")
            return True
            
        except Exception as e:
            self.logger.error(f"RDF 변환 실패: {e}")
            return False
    
    def _apply_ofco_mapping(self, df: pd.DataFrame) -> bool:
        """OFCO 매핑 규칙 적용"""
        if not self.ofco_rules:
            return False
        
        try:
            mapping_rules = self.ofco_rules.get('mapping_rules', [])
            
            # 비용 센터 매핑용 컬럼이 있는지 확인
            text_columns = ['Invoice Line Item', 'Description', 'Charge Description']
            available_text_columns = [col for col in text_columns if col in df.columns]
            
            if not available_text_columns:
                self.logger.warning("OFCO 매핑용 텍스트 컬럼을 찾을 수 없음")
                return False
            
            matched_count = 0
            
            for idx, row in df.iterrows():
                for text_col in available_text_columns:
                    text_value = str(row.get(text_col, ''))
                    if not text_value or text_value == 'nan':
                        continue
                    
                    # 매핑 규칙 적용
                    best_match = self._find_ofco_match(text_value, mapping_rules)
                    if best_match:
                        # 결과 저장
                        self._save_ofco_mapping(text_value, best_match)
                        matched_count += 1
                        break
            
            self.logger.info(f"OFCO 매핑 완료: {matched_count}건 매칭")
            return True
            
        except Exception as e:
            self.logger.error(f"OFCO 매핑 실패: {e}")
            return False
    
    def _find_ofco_match(self, text: str, mapping_rules: List[Dict]) -> Optional[Dict]:
        """OFCO 매핑 규칙에서 최적 매치 찾기"""
        best_match = None
        best_priority = float('inf')
        
        for rule in mapping_rules:
            pattern = rule.get('pattern', '')
            priority = rule.get('priority', 999)
            
            if re.search(pattern, text, re.IGNORECASE):
                if priority < best_priority:
                    best_priority = priority
                    best_match = rule
        
        return best_match
    
    def _save_ofco_mapping(self, text: str, match: Dict):
        """OFCO 매핑 결과 저장"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO ofco_mappings 
                (source_text, matched_pattern, cost_center_a, cost_center_b, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                text,
                match.get('pattern', ''),
                match.get('cost_center_a', ''),
                match.get('cost_center_b', ''),
                1.0 / match.get('priority', 999)
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"OFCO 매핑 저장 실패: {e}")
    
    def _save_results(self, df: pd.DataFrame, validation: ValidationResult):
        """결과 저장"""
        try:
            cursor = self.conn.cursor()
            
            # 검증 로그 저장
            cursor.execute('''
                INSERT INTO validation_logs 
                (validation_type, record_count, success_count, error_count, confidence_avg, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'ontology_mapping',
                validation.processed_records,
                validation.processed_records - len(validation.errors),
                len(validation.errors),
                validation.confidence,
                json.dumps({
                    'errors': validation.errors,
                    'warnings': validation.warnings
                }, ensure_ascii=False)
            ))
            
            # 온톨로지 데이터 저장 (샘플)
            for idx, row in df.head(100).iterrows():  # 처음 100건만 저장
                cursor.execute('''
                    INSERT INTO ontology_data 
                    (record_id, case_no, date_value, location, quantity, amount, 
                     category, vendor, validation_status, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"REC_{idx:06d}",
                    str(row.get('Case_No', '')),
                    str(row.get('Date', '')),
                    str(row.get('Location', '')),
                    row.get('Qty', 0) if pd.notna(row.get('Qty')) else 0,
                    row.get('Amount', 0.0) if pd.notna(row.get('Amount')) else 0.0,
                    str(row.get('Category', '')),
                    str(row.get('Vendor', '')),
                    'PROCESSED',
                    validation.confidence
                ))
            
            self.conn.commit()
            self.logger.info("결과 저장 완료")
            
        except Exception as e:
            self.logger.error(f"결과 저장 실패: {e}")
    
    def generate_sparql_queries(self) -> Dict[str, str]:
        """SPARQL 쿼리 생성"""
        if not self.graph:
            return {}
        
        try:
            templates = self.mapping_rules.get('sparql_templates', {})
            namespace = self.config.namespace
            
            queries = {}
            
            # 기본 쿼리들
            basic_queries = templates.get('basic_queries', {})
            for name, template in basic_queries.items():
                queries[name] = template.format(namespace=namespace)
            
            # 고급 쿼리들
            advanced_queries = templates.get('advanced_queries', {})
            for name, template in advanced_queries.items():
                queries[f"advanced_{name}"] = template.format(namespace=namespace)
            
            self.logger.info(f"SPARQL 쿼리 생성 완료: {len(queries)}개")
            return queries
            
        except Exception as e:
            self.logger.error(f"SPARQL 쿼리 생성 실패: {e}")
            return {}
    
    def execute_sparql_query(self, query: str) -> List[Dict]:
        """SPARQL 쿼리 실행"""
        if not self.graph:
            return []
        
        try:
            results = []
            qres = self.graph.query(query)
            
            for row in qres:
                result_dict = {}
                for i, var in enumerate(qres.vars):
                    result_dict[str(var)] = str(row[i]) if row[i] else None
                results.append(result_dict)
            
            self.logger.info(f"SPARQL 쿼리 실행 완료: {len(results)}건 결과")
            return results
            
        except Exception as e:
            self.logger.error(f"SPARQL 쿼리 실행 실패: {e}")
            return []
    
    def export_rdf(self, output_file: str, format: str = 'turtle') -> bool:
        """RDF 데이터 내보내기"""
        if not self.graph:
            return False
        
        try:
            self.graph.serialize(destination=output_file, format=format)
            self.logger.info(f"RDF 내보내기 완료: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"RDF 내보내기 실패: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """통합 리포트 생성"""
        try:
            cursor = self.conn.cursor()
            
            # 처리 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_records,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(DISTINCT validation_status) as status_types
                FROM ontology_data
            ''')
            processing_stats = cursor.fetchone()
            
            # OFCO 매핑 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_mappings,
                    COUNT(DISTINCT cost_center_a) as unique_cost_centers,
                    AVG(confidence_score) as avg_mapping_confidence
                FROM ofco_mappings
            ''')
            ofco_stats = cursor.fetchone()
            
            # 검증 로그 요약
            cursor.execute('''
                SELECT 
                    validation_type,
                    SUM(record_count) as total_processed,
                    AVG(confidence_avg) as avg_confidence,
                    SUM(error_count) as total_errors
                FROM validation_logs
                GROUP BY validation_type
            ''')
            validation_summary = cursor.fetchall()
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'system_version': self.config.version,
                'processing_statistics': {
                    'total_records': processing_stats[0] if processing_stats else 0,
                    'average_confidence': processing_stats[1] if processing_stats else 0,
                    'status_types': processing_stats[2] if processing_stats else 0
                },
                'ofco_mapping_statistics': {
                    'total_mappings': ofco_stats[0] if ofco_stats else 0,
                    'unique_cost_centers': ofco_stats[1] if ofco_stats else 0,
                    'average_confidence': ofco_stats[2] if ofco_stats else 0
                },
                'validation_summary': [
                    {
                        'type': row[0],
                        'processed': row[1],
                        'confidence': row[2],
                        'errors': row[3]
                    } for row in validation_summary
                ],
                'rdf_graph_size': len(self.graph) if self.graph else 0,
                'configuration': {
                    'namespace': self.config.namespace,
                    'enable_rdf': self.config.enable_rdf,
                    'enable_ofco_mapping': self.config.enable_ofco_mapping,
                    'confidence_threshold': self.config.confidence_threshold
                }
            }
            
            self.logger.info("통합 리포트 생성 완료")
            return report
            
        except Exception as e:
            self.logger.error(f"리포트 생성 실패: {e}")
            return {}
    
    def close(self):
        """시스템 종료"""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
            self.logger.info("HVDC 통합 온톨로지 시스템 종료")
        except Exception as e:
            self.logger.error(f"시스템 종료 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🔌 HVDC 프로젝트 통합 온톨로지 매핑 시스템 v3.0.0")
    print("=" * 60)
    
    # 시스템 초기화
    config = OntologyConfig()
    system = HVDCOntologyUnifiedSystem(config)
    
    try:
        # 테스트 데이터 처리 (예시)
        test_files = [
            "HVDC_실제데이터_완전통합_20250704_111552.xlsx",
            "창고_현장_월별_시트_구조_20250704_105737.xlsx"
        ]
        
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"\n📊 처리 중: {test_file}")
                result = system.process_excel_data(test_file)
                
                print(f"✅ 처리 완료 - 신뢰도: {result.confidence:.3f}")
                if result.errors:
                    print(f"❌ 오류: {len(result.errors)}개")
                if result.warnings:
                    print(f"⚠️ 경고: {len(result.warnings)}개")
            else:
                print(f"⚠️ 파일 미발견: {test_file}")
        
        # SPARQL 쿼리 생성 및 실행 (예시)
        queries = system.generate_sparql_queries()
        if queries:
            print(f"\n🔍 SPARQL 쿼리 {len(queries)}개 생성 완료")
            
            # 첫 번째 쿼리 실행 예시
            first_query_name = list(queries.keys())[0]
            first_query = queries[first_query_name]
            results = system.execute_sparql_query(first_query)
            print(f"   └ {first_query_name}: {len(results)}건 결과")
        
        # RDF 내보내기
        if system.graph:
            rdf_output = f"hvdc_unified_ontology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ttl"
            if system.export_rdf(rdf_output):
                print(f"📄 RDF 내보내기 완료: {rdf_output}")
        
        # 통합 리포트 생성
        report = system.generate_report()
        if report:
            report_file = f"hvdc_ontology_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"📋 통합 리포트 생성: {report_file}")
        
        print(f"\n🎯 처리 완료!")
        print(f"   └ 총 처리: {report.get('processing_statistics', {}).get('total_records', 0)}건")
        print(f"   └ 평균 신뢰도: {report.get('processing_statistics', {}).get('average_confidence', 0):.3f}")
        print(f"   └ OFCO 매핑: {report.get('ofco_mapping_statistics', {}).get('total_mappings', 0)}건")
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
    
    finally:
        system.close()

if __name__ == "__main__":
    main() 