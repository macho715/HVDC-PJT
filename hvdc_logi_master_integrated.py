# hvdc_logi_master_integrated.py - HVDC 물류 마스터 통합 시스템
"""
HVDC 물류 마스터 통합 시스템 v3.4-mini
- 온톨로지 매핑 엔진 통합
- 창고_현장_월별_시트_구조 완전 지원
- MACHO-GPT 물류 도메인 전체 커버리지
- Samsung C&T · ADNOC · DSV 파트너십 대응
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
import re
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# RDF 온톨로지 지원
try:
    from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
    RDF_AVAILABLE = True
    # 온톨로지 네임스페이스 정의
    HVDC = Namespace("http://samsung.com/project-logistics#")
    EX = Namespace("http://example.org/hvdc#")
    MACHO = Namespace("http://macho-gpt.com/logistics#")
except ImportError:
    RDF_AVAILABLE = False
    print("⚠️ RDFLib 미설치 - RDF 기능 비활성화")

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Event-Based Outbound Logic 지원
try:
    from scripts.event_based_outbound import EventBasedOutboundResolver
    EVENT_OUTBOUND_AVAILABLE = True
    logger.info("✅ Event-Based Outbound Logic 모듈 로드 완료")
except ImportError:
    EVENT_OUTBOUND_AVAILABLE = False
    logger.warning("⚠️ Event-Based Outbound Logic 모듈 없음 - 기본 로직 사용")

# ===== 1. 핵심 데이터 클래스 정의 =====

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
    sqm: float = 0.0
    flow_code: int = 0
    
    def to_rdf(self, graph) -> 'URIRef':
        """RDF 트리플로 변환"""
        if not RDF_AVAILABLE:
            return None
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
        graph.add((item_uri, HVDC.sqm, Literal(self.sqm, datatype=XSD.decimal)))
        graph.add((item_uri, HVDC.flowCode, Literal(self.flow_code, datatype=XSD.integer)))
        
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
    
    def to_rdf(self, graph) -> 'URIRef':
        if not RDF_AVAILABLE:
            return None
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

@dataclass
class MonthlySiteReport:
    """창고_현장_월별_시트_구조 전용 리포트 클래스"""
    report_month: str
    warehouse_data: Dict[str, Dict[str, int]]  # warehouse_name -> {inbound, outbound}
    site_data: Dict[str, Dict[str, int]]       # site_name -> {inbound, inventory}
    total_transactions: int
    confidence_score: float

class ContainmentMode(Enum):
    """MACHO-GPT 컨테인먼트 모드"""
    PRIME = "PRIME"
    ORACLE = "ORACLE"
    ZERO = "ZERO"
    LATTICE = "LATTICE"
    RHYTHM = "RHYTHM"
    COST_GUARD = "COST_GUARD"

# ===== 2. 매핑 및 온톨로지 관리자 =====

class MappingManager:
    """통합 매핑 관리자 v3.4"""
    
    def __init__(self, mapping_file: str = "mapping_rules_v2.8.json"):
        self.mapping_file = mapping_file
        self.mapping_rules = self._load_mapping_rules()
        self.warehouse_classification = self.mapping_rules.get("warehouse_classification", {})
        self.logistics_flow_definition = self.mapping_rules.get("logistics_flow_definition", {})
        
        # 창고 위치 매핑
        self.location_columns = {
            'sites': ['AGI', 'DAS', 'MIR', 'SHU'],
            'warehouses': ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'MOSB', 'DSV MZP']
        }
        
    def _load_mapping_rules(self) -> Dict:
        """매핑 규칙 파일 로드"""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"매핑 규칙 파일 {self.mapping_file} 없음, 기본값 사용")
            return self._get_default_mapping_rules()
    
    def _get_default_mapping_rules(self) -> Dict:
        """기본 매핑 규칙"""
        return {
            "warehouse_classification": {
                "Indoor": ["DSV Indoor", "Hauler Indoor"],
                "Outdoor": ["DSV Outdoor"], 
                "Site": ["AGI", "DAS", "MIR", "SHU"],
                "OffshoreBase": ["MOSB"],
                "Others": ["DSV Al Markaz", "DSV MZP", "AAA Storage"]
            },
            "vendor_mappings": {
                "HE": "Hitachi",
                "SIM": "Siemens",
                "SCNT": "Samsung C&T"
            },
            "field_map": {
                "Case No.": "hasCaseNo",
                "Vendor": "hasVendor",
                "Category": "hasCategory",
                "Weight": "hasWeight",
                "CBM": "hasCBM",
                "SQM": "hasSQM",
                "FLOW_CODE": "hasFlowCode",
                "Status_Location_Date": "hasStatusLocationDate"
            }
        }
    
    def classify_storage_type(self, location: str) -> str:
        """Location → Storage Type 분류"""
        if not location or pd.isna(location):
            return "Unknown"
        
        loc = str(location).strip()
        
        # 정확한 매칭 확인
        for storage_type, locations in self.warehouse_classification.items():
            if loc in locations:
                return storage_type
        
        # 부분 매칭 확인
        loc_lower = loc.lower()
        for storage_type, locations in self.warehouse_classification.items():
            for pattern in locations:
                if pattern.lower() in loc_lower:
                    return storage_type
        
        return "Unknown"

class HVDCOntologyEngine:
    """HVDC 온톨로지 엔진 - 완전 통합"""
    
    def __init__(self, db_path: str = "hvdc_ontology.db"):
        self.graph = Graph() if RDF_AVAILABLE else None
        self.db_path = db_path
        self.init_database()
        if RDF_AVAILABLE:
            self.setup_ontology_schema()
        
    def init_database(self):
        """SQLite 데이터베이스 초기화"""
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
                sqm REAL,
                flow_code INTEGER,
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
                handling_fee REAL,
                monthly_inbound INTEGER DEFAULT 0,
                monthly_outbound INTEGER DEFAULT 0
            )
        ''')
        
        # 월별 집계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_aggregates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_month TEXT,
                location_name TEXT,
                location_type TEXT,
                inbound_count INTEGER,
                outbound_count INTEGER,
                inventory_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def setup_ontology_schema(self):
        """온톨로지 스키마 설정"""
        if not RDF_AVAILABLE:
            return
        
        # 네임스페이스 바인딩
        self.graph.bind("hvdc", HVDC)
        self.graph.bind("ex", EX)
        self.graph.bind("macho", MACHO)
        
        # 클래스 정의
        classes = [
            (HVDC.Item, "HVDC 아이템"),
            (HVDC.Warehouse, "창고"),
            (HVDC.IndoorWarehouse, "실내 창고"),
            (HVDC.OutdoorWarehouse, "실외 창고"),
            (HVDC.Site, "현장"),
            (HVDC.DangerousCargoWarehouse, "위험물 창고"),
            (HVDC.TransportEvent, "운송 이벤트"),
            (HVDC.MonthlySiteReport, "월별 현장 리포트"),
            (MACHO.LogiMaster, "물류 마스터"),
            (MACHO.ContainerStow, "컨테이너 적재"),
            (MACHO.WeatherTie, "날씨 연동")
        ]
        
        for class_uri, label in classes:
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(label, lang="ko")))
        
        # 속성 정의
        properties = [
            (HVDC.hvdcCode, "HVDC 코드"),
            (HVDC.vendor, "벤더"),
            (HVDC.category, "카테고리"),
            (HVDC.weight, "중량"),
            (HVDC.sqm, "면적"),
            (HVDC.flowCode, "플로우 코드"),
            (HVDC.currentLocation, "현재 위치"),
            (HVDC.statusLocationDate, "상태 위치 날짜"),
            (MACHO.containmentMode, "컨테인먼트 모드"),
            (MACHO.confidenceScore, "신뢰도 점수")
        ]
        
        for prop_uri, label in properties:
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(label, lang="ko")))
    
    def add_item(self, item: HVDCItem) -> bool:
        """아이템 추가"""
        try:
            # RDF 그래프에 추가
            if RDF_AVAILABLE:
                item_uri = item.to_rdf(self.graph)
            
            # SQLite에 저장
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO items 
                (hvdc_code, vendor, category, weight, location, status, risk_level, sqm, flow_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item.hvdc_code, item.vendor, item.category, item.weight, 
                  item.location, item.status, item.risk_level, item.sqm, item.flow_code))
            
            self.conn.commit()
            logger.info(f"아이템 {item.hvdc_code} 추가 완료")
            return True
            
        except Exception as e:
            logger.error(f"아이템 추가 실패: {e}")
            return False

# ===== 3. 메인 HVDC 물류 마스터 클래스 =====

class HVDCLogiMaster:
    """HVDC 물류 마스터 시스템 - 완전 통합"""
    
    def __init__(self, 
                 mode: ContainmentMode = ContainmentMode.PRIME,
                 enable_ontology: bool = True,
                 mapping_file: str = "mapping_rules_v2.8.json"):
        
        self.mode = mode
        self.confidence_threshold = 0.90
        self.success_rate_target = 0.95
        
        # 핵심 컴포넌트 초기화
        self.mapping_manager = MappingManager(mapping_file)
        self.ontology_engine = HVDCOntologyEngine() if enable_ontology else None
        
        # 위치 정보
        self.location_columns = {
            'sites': ['AGI', 'DAS', 'MIR', 'SHU'],
            'warehouses': ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'MOSB', 'DSV MZP']
        }
        
        # KPI 임계값
        self.kpi_thresholds = {
            'delta_rate_threshold': 10,  # % change
            'eta_delay_threshold': 24,   # hours
            'pressure_threshold': 4,     # t/m²
            'utilization_threshold': 85, # %
            'cert_expiry_days': 30       # days
        }
        
        logger.info(f"HVDC 물류 마스터 초기화 완료 - Mode: {mode.value}")
    
    def process_macho_data(self, 
                          source_file: str,
                          output_file: str = None) -> Dict[str, Any]:
        """MACHO 통합 데이터 처리"""
        try:
            print(f'📂 MACHO 데이터 로드: {source_file}')
            df = pd.read_excel(source_file, sheet_name=0)
            print(f'✅ 데이터 로드 완료: {len(df):,}건, {len(df.columns)}개 컬럼')
            
            # 데이터 전처리
            df = self._preprocess_data(df)
            
            # 온톨로지 매핑
            if self.ontology_engine:
                df = self._apply_ontology_mapping(df)
            
            # 월별 집계 생성
            monthly_report = self._create_monthly_site_report(df)
            
            # Excel 리포트 생성
            if output_file:
                self._create_excel_report(df, monthly_report, output_file)
            
            return {
                'status': 'SUCCESS',
                'confidence': self._calculate_confidence(df),
                'mode': self.mode.value,
                'processed_records': len(df),
                'monthly_report': monthly_report,
                'next_cmds': self._get_next_commands(df)
            }
            
        except Exception as e:
            logger.error(f"데이터 처리 실패: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'mode': self.mode.value
            }
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 전처리"""
        print('🔧 데이터 전처리 시작...')
        
        # 필수 컬럼 확인
        required_columns = ['Case No.', 'FLOW_CODE', 'Status_Current', 'Status_Location']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f'⚠️ 누락된 컬럼: {missing_columns}')
        
        # 위치 정보 처리
        for site in self.location_columns['sites']:
            if site in df.columns:
                df[site] = pd.to_datetime(df[site], errors='coerce')
        
        for warehouse in self.location_columns['warehouses']:
            if warehouse in df.columns:
                df[warehouse] = pd.to_datetime(df[warehouse], errors='coerce')
        
        # Event-Based Outbound Logic: Final_Location 재구성 (월별 집계 전 호출)
        if EVENT_OUTBOUND_AVAILABLE:
            try:
                print('🎯 Event-Based Final_Location 재구성 중...')
                resolver = EventBasedOutboundResolver(config_path='config/wh_priority.yaml')
                df = resolver.resolve_final_location(df)
                print(f'✅ Final_Location 재구성 완료 - {df["Final_Location"].value_counts().to_dict()}')
            except Exception as e:
                logger.warning(f"Final_Location 재구성 실패: {e}, 기본 로직 사용")
                # 기본 Final_Location 로직 (Status_Location 사용)
                df['Final_Location'] = df['Status_Location'].fillna('Unknown')
        else:
            # 기본 Final_Location 로직
            df['Final_Location'] = df['Status_Location'].fillna('Unknown')
        
        # Flow Code 검증
        if 'FLOW_CODE' in df.columns:
            df['FLOW_CODE'] = df['FLOW_CODE'].apply(self._validate_flow_code)
        
        # SQM 계산
        if 'CBM' in df.columns and 'SQM' not in df.columns:
            df['SQM'] = df['CBM'] / 0.5  # CBM to SQM conversion
        
        print(f'✅ 데이터 전처리 완료: {len(df)}건')
        return df
    
    def _apply_ontology_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """온톨로지 매핑 적용"""
        if not self.ontology_engine:
            return df
        
        print('🔗 온톨로지 매핑 적용 중...')
        
        # 각 행을 HVDCItem으로 변환 후 온톨로지에 추가
        for idx, row in df.iterrows():
            try:
                item = HVDCItem(
                    hvdc_code=str(row.get('Case No.', f'ITEM_{idx:05d}')),
                    vendor=str(row.get('Vendor', 'Unknown')),
                    category=str(row.get('Category', 'General')),
                    description=str(row.get('Description', '')),
                    weight=float(row.get('G.W(kgs)', 0)),
                    dimensions={'length': 0, 'width': 0, 'height': 0},
                    location=str(row.get('Status_Location', 'Unknown')),
                    status=str(row.get('Status_Current', 'warehouse')),
                    sqm=float(row.get('SQM', 0)),
                    flow_code=int(row.get('FLOW_CODE', 0))
                )
                
                self.ontology_engine.add_item(item)
                
            except Exception as e:
                logger.warning(f"행 {idx} 매핑 실패: {e}")
                continue
        
        print('✅ 온톨로지 매핑 완료')
        return df
    
    def _create_monthly_site_report(self, df: pd.DataFrame) -> MonthlySiteReport:
        """창고_현장_월별_시트_구조 리포트 생성"""
        print('📊 월별 현장 리포트 생성 중...')
        
        # 현재 월 계산
        current_month = datetime.now().strftime('%Y-%m')
        
        # 창고별 집계
        warehouse_data = {}
        for warehouse in self.location_columns['warehouses']:
            if warehouse in df.columns:
                inbound_count = df[warehouse].notna().sum()
                # 출고는 Status_Current가 'site'인 경우로 추정
                outbound_count = df[(df['Status_Current'] == 'site') & 
                                   (df[warehouse].notna())].shape[0]
                warehouse_data[warehouse] = {
                    'inbound': inbound_count,
                    'outbound': outbound_count
                }
        
        # 현장별 집계
        site_data = {}
        for site in self.location_columns['sites']:
            if site in df.columns:
                inbound_count = df[site].notna().sum()
                # 재고는 현재 해당 사이트에 있는 것으로 추정
                inventory_count = df[df['Status_Location'] == site].shape[0]
                site_data[site] = {
                    'inbound': inbound_count,
                    'inventory': inventory_count
                }
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(df)
        
        return MonthlySiteReport(
            report_month=current_month,
            warehouse_data=warehouse_data,
            site_data=site_data,
            total_transactions=len(df),
            confidence_score=confidence
        )
    
    def _create_excel_report(self, 
                            df: pd.DataFrame, 
                            monthly_report: MonthlySiteReport,
                            output_file: str):
        """창고_현장_월별_시트_구조.xlsx 동일한 Excel 리포트 생성"""
        print(f'📊 Excel 리포트 생성: {output_file}')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_output = f'HVDC_LogiMaster_Report_{timestamp}.xlsx'
        
        with pd.ExcelWriter(final_output, engine='openpyxl') as writer:
            
            # Sheet 1: 전체 트랜잭션 데이터
            df.to_excel(writer, sheet_name='전체_트랜잭션_FLOWCODE0-4', index=False)
            
            # Sheet 2: 창고별 월별 입출고
            warehouse_monthly = self._create_warehouse_monthly_sheet(monthly_report)
            warehouse_monthly.to_excel(writer, sheet_name='창고_월별_입출고', index=False)
            
            # Sheet 3: 현장별 월별 입고재고
            site_monthly = self._create_site_monthly_sheet(monthly_report)
            site_monthly.to_excel(writer, sheet_name='현장_월별_입고재고', index=False)
            
            # Sheet 4: 위치별 분포 통계
            location_stats = self._create_location_stats(df)
            location_stats.to_excel(writer, sheet_name='위치별_화물분포_통계', index=False)
            
            # Sheet 5: 요약 통계
            summary_stats = self._create_summary_stats(df, monthly_report)
            summary_stats.to_excel(writer, sheet_name='요약_통계', index=False)
        
        print(f'✅ Excel 리포트 생성 완료: {final_output}')
        return final_output
    
    def _create_warehouse_monthly_sheet(self, report: MonthlySiteReport) -> pd.DataFrame:
        """창고별 월별 입출고 시트 생성"""
        # Multi-level header 구조 생성
        warehouses = list(report.warehouse_data.keys())
        
        # 헤더 구성
        columns = ['Location']
        for warehouse in warehouses:
            columns.extend([f'입고_{warehouse}', f'출고_{warehouse}'])
        
        # 데이터 구성 (2023-02 ~ 2025-06 + Total)
        months = pd.date_range('2023-02', '2025-06', freq='MS').strftime('%Y-%m').tolist()
        months.append('Total')
        
        data = []
        for month in months:
            row = [month]
            for warehouse in warehouses:
                if month == 'Total':
                    # 총합 계산
                    inbound_total = report.warehouse_data[warehouse]['inbound']
                    outbound_total = report.warehouse_data[warehouse]['outbound']
                    row.extend([inbound_total, outbound_total])
                else:
                    # 현재는 최신 월만 데이터 있음
                    if month == report.report_month:
                        row.extend([
                            report.warehouse_data[warehouse]['inbound'],
                            report.warehouse_data[warehouse]['outbound']
                        ])
                    else:
                        row.extend([0, 0])
            data.append(row)
        
        return pd.DataFrame(data, columns=columns)
    
    def _create_site_monthly_sheet(self, report: MonthlySiteReport) -> pd.DataFrame:
        """현장별 월별 입고재고 시트 생성"""
        sites = list(report.site_data.keys())
        
        # 헤더 구성
        columns = ['Location']
        for site in sites:
            columns.extend([f'입고_{site}', f'재고_{site}'])
        
        # 데이터 구성 (2024-01 ~ 2025-06 + 합계)
        months = pd.date_range('2024-01', '2025-06', freq='MS').strftime('%Y-%m').tolist()
        months.append('합계')
        
        data = []
        for month in months:
            row = [month]
            for site in sites:
                if month == '합계':
                    # 총합 계산
                    inbound_total = report.site_data[site]['inbound']
                    inventory_total = report.site_data[site]['inventory']
                    row.extend([inbound_total, inventory_total])
                else:
                    # 현재는 최신 월만 데이터 있음
                    if month == report.report_month:
                        row.extend([
                            report.site_data[site]['inbound'],
                            report.site_data[site]['inventory']
                        ])
                    else:
                        row.extend([0, 0])
            data.append(row)
        
        return pd.DataFrame(data, columns=columns)
    
    def _create_location_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """위치별 분포 통계 생성"""
        stats_data = []
        
        all_locations = self.location_columns['sites'] + self.location_columns['warehouses']
        
        for location in all_locations:
            if location in df.columns:
                count = df[location].notna().sum()
                percentage = count / len(df) * 100
                
                location_type = '현장' if location in self.location_columns['sites'] else '창고'
                
                stats_data.append({
                    '위치': location,
                    '건수': count,
                    '비율(%)': round(percentage, 1),
                    '위치_유형': location_type,
                    '특징': self._get_location_feature(location)
                })
        
        return pd.DataFrame(stats_data).sort_values('건수', ascending=False)
    
    def _create_summary_stats(self, df: pd.DataFrame, report: MonthlySiteReport) -> pd.DataFrame:
        """요약 통계 생성"""
        summary_data = [
            {'구분': '총 화물 건수', '값': f'{len(df):,}건'},
            {'구분': '총 컬럼 수', '값': f'{len(df.columns)}개'},
            {'구분': '현장 위치 수', '값': f'{len(self.location_columns["sites"])}개'},
            {'구분': '창고 위치 수', '값': f'{len(self.location_columns["warehouses"])}개'},
            {'구분': '보고서 생성일시', '값': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'구분': '컨테인먼트 모드', '값': self.mode.value},
            {'구분': '신뢰도 점수', '값': f'{report.confidence_score:.2f}'},
            {'구분': 'Flow Code 범위', '값': f'{df["FLOW_CODE"].min()}-{df["FLOW_CODE"].max()}' if 'FLOW_CODE' in df.columns else 'N/A'}
        ]
        
        return pd.DataFrame(summary_data)
    
    def _get_location_feature(self, location: str) -> str:
        """위치별 특징 반환"""
        features = {
            'SHU': '최대 집중 현장 (용량 관리 필요)',
            'DSV Outdoor': '외부 창고 (날씨 영향 고려)',
            'DSV Indoor': '내부 창고 (안전 보관)',
            'DSV Al Markaz': 'Al Markaz 창고 (중간 경유)',
            'MIR': '주요 현장 (안정적 운영)',
            'DAS': '주요 현장 (효율적 운영)',
            'MOSB': 'MOSB 창고 (전문 보관)',
            'AGI': 'AGI 현장 (특수 장비)',
            'DSV MZP': '소규모 창고 (특수 용도)'
        }
        return features.get(location, '일반 운영')
    
    def _validate_flow_code(self, code: Any) -> int:
        """Flow Code 검증"""
        try:
            flow_code = int(code)
            return flow_code if 0 <= flow_code <= 4 else 0
        except:
            return 0
    
    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """신뢰도 계산"""
        total_fields = len(df.columns)
        valid_fields = sum(1 for col in df.columns if df[col].notna().sum() > 0)
        return (valid_fields / total_fields) * 100 if total_fields > 0 else 0.0
    
    def _get_next_commands(self, df: pd.DataFrame) -> List[str]:
        """다음 추천 명령어 생성"""
        commands = []
        
        # 데이터 품질 기반 추천
        if 'FLOW_CODE' in df.columns:
            commands.append('/flow_code_analysis [플로우 코드 분석]')
        
        if 'SQM' in df.columns:
            commands.append('/warehouse_capacity_check [창고 용량 확인]')
        
        commands.append('/generate_kpi_dashboard [KPI 대시보드 생성]')
        
        return commands

    def generate_kpi_dash(self) -> Dict[str, Any]:
        """KPI 대시보드를 생성합니다/Generate KPI dashboard."""
        kpi_data = {
            'confidence_threshold': round(self.confidence_threshold, 2),
            'success_rate_target': round(self.success_rate_target, 2),
            'kpi_thresholds': self.kpi_thresholds,
        }
        return {
            'status': 'SUCCESS',
            'confidence': round(self.confidence_threshold, 2),
            'mode': self.mode.value,
            'triggers': [],
            'next_cmds': self._get_next_commands(pd.DataFrame()),
            'data': kpi_data,
        }
    
    def switch_mode(self, new_mode: ContainmentMode, reason: str = "") -> Dict[str, Any]:
        """컨테인먼트 모드 전환"""
        old_mode = self.mode
        self.mode = new_mode
        
        logger.info(f"컨테인먼트 모드 전환: {old_mode.value} → {new_mode.value}")
        if reason:
            logger.info(f"전환 사유: {reason}")
        
        return {
            'status': 'SUCCESS',
            'old_mode': old_mode.value,
            'new_mode': new_mode.value,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터 품질 검증"""
        validation_results = {
            'total_records': len(df),
            'missing_data': {},
            'data_types': {},
            'quality_score': 0.0,
            'recommendations': []
        }
        
        # 누락 데이터 확인
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_percentage = (missing_count / len(df)) * 100
            validation_results['missing_data'][col] = {
                'count': missing_count,
                'percentage': round(missing_percentage, 2)
            }
            
            # 데이터 타입 확인
            validation_results['data_types'][col] = str(df[col].dtype)
        
        # 품질 점수 계산
        total_cells = len(df) * len(df.columns)
        filled_cells = total_cells - df.isna().sum().sum()
        validation_results['quality_score'] = (filled_cells / total_cells) * 100
        
        # 추천사항 생성
        if validation_results['quality_score'] < 80:
            validation_results['recommendations'].append('데이터 품질 개선 필요')
        
        return validation_results

# ===== 4. 사용 예시 및 테스트 =====

def main():
    """메인 실행 함수"""
    print("🚀 HVDC 물류 마스터 시스템 시작")
    
    # 물류 마스터 초기화
    logi_master = HVDCLogiMaster(
        mode=ContainmentMode.LATTICE,
        enable_ontology=True
    )
    
    # 샘플 데이터 처리
    source_file = 'MACHO_Final_Report_Complete_20250703_230904.xlsx'
    
    if Path(source_file).exists():
        result = logi_master.process_macho_data(source_file)
        print(f"처리 결과: {result}")
    else:
        print(f"⚠️ 소스 파일 없음: {source_file}")
    
    print("🎉 HVDC 물류 마스터 시스템 완료")

if __name__ == "__main__":
    main() 
