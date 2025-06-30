#!/usr/bin/env python3
"""
HVDC Warehouse 통합 매핑 유틸리티 v2.8.2 (2025-06-29)
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics

매핑 규칙 파일을 기반으로 일관된 Storage Type 분류를 제공합니다.
v2.8.2 신규 기능: 호환성 fallback, lru_cache, circular import 방지
최신 실전 예제 및 확장 자동화 기능 포함.
"""

import json
import pandas as pd
import numpy as np
import re
from pathlib import Path
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 🔧 v2.8.2 패치: 신규 유틸 - 값 정규화 & 유효성 검사
# ──────────────────────────────────────────────
_DOUBLE_SPACE = "\u3000"          # 전각 공백

# v2.8.2 패치: 규칙 파일 경로 상수 정의
DEFAULT_RULE = "mapping_rules_v2.8.json"
FALLBACK_RULE = "mapping_rules_v2.6.json"

def clean_value(val) -> str:
    """
    NaN / None / 전각공백 / 앞뒤 스페이스를 모두 제거한 문자열을 반환
    v2.8.1 패치: 전각공백(\u3000) 처리 추가
    """
    if val is None or (isinstance(val, float) and np.isnan(val)) or pd.isna(val):
        return ""
    return str(val).replace(_DOUBLE_SPACE, "").strip()

def is_valid_data(val) -> bool:
    """
    유효한(비어 있지 않고 'nan'·'none'이 아닌) 데이터 여부 확인
    v2.8.1 패치: 전각공백 처리 및 NaN 안전 검사
    """
    cleaned = clean_value(val).lower()
    return cleaned not in ("", "nan", "none")

@lru_cache(maxsize=2)
def load_rules(rule_file: str = None) -> dict:
    """
    매핑 규칙 파일 로드 (캐시 적용)
    v2.8.2 패치: 호환성 fallback + lru_cache 최적화
    
    Args:
        rule_file: 규칙 파일 경로 (None이면 DEFAULT_RULE 사용)
    
    Returns:
        dict: 로드된 매핑 규칙
    """
    if rule_file is None:
        rule_file = DEFAULT_RULE
    
    # 1. 기본 규칙 파일 시도
    try:
        with open(rule_file, encoding='utf-8') as f:
            rules = json.load(f)
            logger.info(f"✅ 매핑 규칙 로드 완료: {rule_file}")
            return rules
    except Exception as e:
        logger.warning(f"기본 규칙 파일 로드 실패 ({rule_file}): {e}")
    
    # 2. Fallback 규칙 파일 시도
    if rule_file != FALLBACK_RULE:
        try:
            with open(FALLBACK_RULE, encoding='utf-8') as f:
                rules = json.load(f)
                logger.info(f"✅ Fallback 규칙 파일 로드 완료: {FALLBACK_RULE}")
                return rules
        except Exception as e:
            logger.warning(f"Fallback 규칙 파일 로드 실패 ({FALLBACK_RULE}): {e}")
    
    # 3. 최종 fallback: 기본값 반환
    logger.error("모든 매핑 규칙 파일 로드 실패, 기본값 사용")
    return {
        'vendor_mappings': {},
        'container_column_groups': {},
        'warehouse_classification': {},
        'field_map': {},
        'property_mappings': {},
        'logistics_flow_definition': {}
    }

# 전역 규칙 로드 (캐시 적용)
RULES = load_rules()

VENDOR_MAP = RULES.get('vendor_mappings', {})
CONTAINER_GROUPS = RULES.get('container_column_groups', {})
WAREHOUSE_CLASS = RULES.get('warehouse_classification', {})
FIELD_MAP = RULES.get('field_map', {})
PROPERTY_MAPPINGS = RULES.get('property_mappings', {})
LOGISTICS_FLOW_DEF = RULES.get('logistics_flow_definition', {})

def normalize_code_num(code):
    """HVDC CODE 숫자 부분 0제거 정규화(예: 0014, 014, 14 모두 → 14)"""
    if not isinstance(code, str): 
        code = str(code)
    m = re.search(r'(\d+)$', code)
    return int(m.group(1)) if m else code

def codes_match(code_a, code_b):
    """코드 비교 함수 (정규화 적용)"""
    return normalize_code_num(code_a) == normalize_code_num(code_b)

def is_valid_hvdc_vendor(code3, valid_list=None):
    """벤더 필터 함수 (HE, SIM만 유효)"""
    if valid_list is None:
        valid_list = ["HE", "SIM"]
    return str(code3).strip().upper() in valid_list

def is_warehouse_code(code, wh_list=None):
    """창고 코드 필터 함수"""
    if wh_list is None:
        wh_list = ["DSV OUTDOOR", "DSV INDOOR", "DSV AL MARKAZ", "DSV MZP"]
    return str(code).strip().upper() in [x.upper() for x in wh_list]

class MappingManager:
    """통합 매핑 관리자 v2.8.2"""
    
    def __init__(self, mapping_file: str = None):
        """
        v2.8.2 패치: mapping_file=None이면 DEFAULT_RULE 사용
        """
        self.mapping_file = mapping_file or DEFAULT_RULE
        self.mapping_rules = self._load_mapping_rules()
        self.warehouse_classification = self.mapping_rules.get("warehouse_classification", {})
        self.logistics_flow_definition = self.mapping_rules.get("logistics_flow_definition", {})
        
    def _load_mapping_rules(self):
        """
        매핑 규칙 파일 로드 (호환성 fallback 포함)
        v2.8.2 패치: 캐시된 load_rules() 함수 재사용
        """
        return load_rules(self.mapping_file)
    
    def classify_storage_type(self, location: str) -> str:
        """Location → Storage Type (Indoor, Outdoor, Site, Pre_Arrival, OffshoreBase)"""
        if not location or pd.isna(location):
            return "Unknown"

        loc = str(location).strip()

        # ① Exact match against rule list
        for stype, locs in self.warehouse_classification.items():
            if loc in locs:
                return stype

        # ② Substring match (case-insensitive)
        loc_lower = loc.lower()
        for stype, locs in self.warehouse_classification.items():
            for pattern in locs:
                if pattern.lower() in loc_lower:
                    return stype

        # ③ NEW: fallback heuristics
        if loc_lower in {"pre arrival", "inbound_pending", "not_yet_received"}:
            return "Pre_Arrival"
        if "mosb" in loc_lower or "offshore" in loc_lower:
            return "OffshoreBase"

        return "Unknown"
    
    def add_storage_type_to_dataframe(self, df: pd.DataFrame, location_col: str = "Location") -> pd.DataFrame:
        """
        DataFrame에 Storage_Type 컬럼 추가
        
        Args:
            df: 대상 DataFrame
            location_col: Location 컬럼명
            
        Returns:
            pd.DataFrame: Storage_Type 컬럼이 추가된 DataFrame
        """
        if location_col not in df.columns:
            logger.error(f"Location 컬럼 없음: {location_col}")
            df['Storage_Type'] = 'Unknown'
            return df
            
        # ✅ Location 기준으로 Storage_Type 새로 생성 (기존 값 무시)
        df['Storage_Type'] = df[location_col].apply(self.classify_storage_type)
        
        # 검증 로그
        storage_counts = df['Storage_Type'].value_counts()
        logger.info(f"🏷️ Storage Type 분류 결과: {dict(storage_counts)}")
        
        return df
    
    def validate_mapping(self, df: pd.DataFrame, location_col: str = "Location") -> dict:
        """
        매핑 검증 및 통계
        
        Args:
            df: 검증할 DataFrame
            location_col: Location 컬럼명
            
        Returns:
            dict: 검증 결과
        """
        if location_col not in df.columns:
            return {"error": f"Location 컬럼 없음: {location_col}"}
            
        # Storage Type별 고유 Location 목록
        validation_result = {}
        
        for storage_type in self.warehouse_classification.keys():
            locations = df[df['Storage_Type'] == storage_type][location_col].unique()
            validation_result[storage_type] = {
                'count': len(df[df['Storage_Type'] == storage_type]),
                'locations': sorted(locations.tolist())
            }
        
        # Unknown 타입 검증
        unknown_locations = df[df['Storage_Type'] == 'Unknown'][location_col].unique()
        validation_result['Unknown'] = {
            'count': len(df[df['Storage_Type'] == 'Unknown']),
            'locations': sorted(unknown_locations.tolist())
        }
        
        return validation_result
    
    def get_warehouse_locations(self) -> list:
        """창고 Location 목록 반환"""
        warehouse_types = ['Indoor', 'Outdoor', 'dangerous_cargo']
        warehouse_locations = []
        
        for storage_type in warehouse_types:
            if storage_type in self.warehouse_classification:
                warehouse_locations.extend(self.warehouse_classification[storage_type])
                
        return warehouse_locations
    
    def get_site_locations(self) -> list:
        """현장 Location 목록 반환"""
        return self.warehouse_classification.get('Site', [])

# ── 3️⃣ New Utility: calc_flow_code ────────────────────────────────────────────────
# Insert into logistics_flow_utils.py (new) or mapping_utils.py.
# Calculates 0-4 code per HVDC_Logistics_Flow_Report.md definitions.

def calc_flow_code(record: dict) -> int:
    """Return logistics flow code (int 0-4)."""
    # Code 0: Pre Arrival flag
    status_flag = record.get("Status", "").lower()
    if status_flag in {"pre arrival", "inbound_pending", "not_yet_received"}:
        return 0

    # Start from direct Port→Site
    steps = 1  # Port and Site implicitly present

    # Each intermediate node +1
    if record.get("Warehouse"):
        steps += 1  # WH
    if record.get("OffshoreBase"):
        steps += 1  # MOSB / Offshore Base
    if record.get("ExtraWH"):
        steps += 1  # Additional WH layer

    # Ensure within 1-4
    return min(max(steps, 1), 4)

def add_logistics_flow_code_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame에 Logistics_Flow_Code 컬럼 추가
    v2.8.2 패치: Circular import 방지를 위한 지연 import 패턴
    """
    def calculate_flow_code(row):
        # v2.8.2 패치: FlowCodeCalculatorV2 지연 import (필요시)
        try:
            # from .calc_flow_code_v2 import FlowCodeCalculatorV2
            # calculator = FlowCodeCalculatorV2()
            # return calculator.calculate_route_from_record(dict(row))
            pass
        except ImportError:
            # Fallback to legacy calc_flow_code
            pass
        
        record = {
            "Status": row.get("Status", ""),
            "Warehouse": row.get("Location", "") if classify_storage_type(row.get("Location", "")) in ["Indoor", "Outdoor"] else None,
            "OffshoreBase": row.get("Location", "") if classify_storage_type(row.get("Location", "")) == "OffshoreBase" else None,
            "ExtraWH": None  # 추후 확장 가능
        }
        return calc_flow_code(record)
    
    df['Logistics_Flow_Code'] = df.apply(calculate_flow_code, axis=1)
    
    # 통계 로그
    flow_counts = df['Logistics_Flow_Code'].value_counts().sort_index()
    logger.info(f"🚀 물류 흐름 코드 분포: {dict(flow_counts)}")
    
    return df

# 전역 매핑 매니저 인스턴스
mapping_manager = MappingManager()

def classify_storage_type(location: str) -> str:
    """편의 함수: Location을 Storage Type으로 분류"""
    return mapping_manager.classify_storage_type(location)

def add_storage_type_to_dataframe(df: pd.DataFrame, location_col: str = "Location") -> pd.DataFrame:
    """편의 함수: DataFrame에 Storage_Type 컬럼 추가"""
    return mapping_manager.add_storage_type_to_dataframe(df, location_col)

def normalize_vendor(vendor_name):
    """
    벤더명 정규화 (mapping_rules의 vendor_mappings 적용)
    
    Args:
        vendor_name: 원본 벤더명
        
    Returns:
        str: 정규화된 벤더명
    """
    if pd.isna(vendor_name) or not vendor_name:
        return 'UNKNOWN'
    
    vendor_mappings = mapping_manager.mapping_rules.get('vendor_mappings', {})
    vendor_str = str(vendor_name).strip().upper()
    
    # 매핑 규칙에 따른 정규화
    for original, normalized in vendor_mappings.items():
        if vendor_str == original.upper() or vendor_str in original.upper():
            return normalized
    
    return vendor_str

def standardize_container_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    컨테이너 컬럼 표준화 (mapping_rules의 container_column_groups 적용)
    
    Args:
        df: 대상 DataFrame
        
    Returns:
        pd.DataFrame: 표준화된 DataFrame
    """
    container_groups = mapping_manager.mapping_rules.get('container_column_groups', {})
    
    # 각 컨테이너 그룹별로 표준화
    for standard_name, variations in container_groups.items():
        # 해당 그룹의 모든 변형을 찾아서 표준명으로 통합
        for variation in variations:
            if variation in df.columns:
                # 표준명 컬럼이 없으면 생성
                if standard_name not in df.columns:
                    df[standard_name] = 0
                
                # 기존 값들을 표준명 컬럼에 추가
                df[standard_name] = df[standard_name] + df[variation].fillna(0)
                
                # 원본 컬럼 삭제 (선택사항)
                # df = df.drop(columns=[variation])
    
    return df

# 최신 실전 예제 함수들 추가
def normalize_vendor_enhanced(val):
    """벤더명 표준화: SIMENSE→SIM 등 (최신 실전 예제)"""
    if pd.isna(val): 
        return 'Unknown'
    sval = str(val).upper()
    return VENDOR_MAP.get(sval, sval)

def standardize_container_columns_enhanced(df):
    """컨테이너 컬럼(20FT/40FT 등) 그룹화 (최신 실전 예제)"""
    for std_col, variants in CONTAINER_GROUPS.items():
        df[std_col] = 0
        for var in variants:
            for col in df.columns:
                if col.replace(" ", "").replace("-", "").upper() == var.replace(" ", "").replace("-", "").upper():
                    df[std_col] += pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def add_storage_type_to_dataframe_enhanced(df, col="Category"):
    """창고/현장/위험물 자동 분류 (Storage_Type 부여) (최신 실전 예제)"""
    def map_type(loc):
        for k, vlist in WAREHOUSE_CLASS.items():
            if str(loc).strip() in vlist:
                return k
        return "Unknown"
    df["Storage_Type"] = df[col].apply(map_type)
    return df

def normalize_location_column(df, location_col='Location'):
    """Location 컬럼 정규화 (최신 실전 예제)"""
    df[location_col] = df[location_col].astype(str).str.strip()
    return df

def get_numeric_fields_from_mapping():
    """mapping_rules에서 숫자형 필드 목록 반환"""
    numeric_fields = []
    for field, props in PROPERTY_MAPPINGS.items():
        if props.get('datatype') in ['xsd:decimal', 'xsd:integer']:
            numeric_fields.append(field)
    return numeric_fields

def get_field_predicate(field_name):
    """필드명에 해당하는 predicate 반환"""
    return FIELD_MAP.get(field_name, f"has{field_name.replace(' ', '')}")

def validate_dataframe_against_mapping(df):
    """DataFrame이 mapping_rules와 일치하는지 검증"""
    missing_fields = []
    extra_fields = []
    
    # mapping_rules에 정의된 필드가 DataFrame에 없는지 확인
    for field in FIELD_MAP.keys():
        if field not in df.columns:
            missing_fields.append(field)
    
    # DataFrame에 있지만 mapping_rules에 정의되지 않은 필드 확인
    for col in df.columns:
        if col not in FIELD_MAP:
            extra_fields.append(col)
    
    return {
        'missing_fields': missing_fields,
        'extra_fields': extra_fields,
        'is_valid': len(missing_fields) == 0
    }

def normalize_flow_code(code):
    """
    Flow Code 정규화 함수 (v2.8.3 신규)
    비표준 Flow Code 6 → 3으로 자동 매핑
    
    Args:
        code: 원본 Flow Code (int 또는 str)
        
    Returns:
        int: 정규화된 Flow Code
    """
    try:
        code_int = int(code)
        if code_int == 6:  # 🆕 패치: 비표준 코드 6 → 표준 3으로 매핑
            logger.info(f"Flow Code 정규화: {code} → 3")
            return 3
        return code_int
    except (ValueError, TypeError):
        logger.warning(f"Flow Code 변환 실패: {code}, 기본값 0 사용")
        return 0

def apply_validation_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    매핑 규칙의 validation_rules를 DataFrame에 적용 (v2.8.3 신규)
    
    Args:
        df: 대상 DataFrame
        
    Returns:
        pd.DataFrame: validation_rules 적용된 DataFrame
    """
    df_processed = df.copy()
    validation_rules = RULES.get('automation_features', {}).get('validation_rules', {})
    
    # 🆕 패치: NULL Pkg → 1 보정
    if validation_rules.get('null_pkg_to_one', False) and 'Pkg' in df_processed.columns:
        null_count = df_processed['Pkg'].isna().sum()
        if null_count > 0:
            df_processed['Pkg'] = df_processed['Pkg'].fillna(1)
            logger.info(f"NULL Pkg 보정: {null_count}건 → 1 PKG로 설정")
    
    # 🆕 패치: 중복 제거
    dedup_keys = validation_rules.get('dedup_keys', [])
    if dedup_keys and all(key in df_processed.columns for key in dedup_keys):
        original_count = len(df_processed)
        df_processed = df_processed.drop_duplicates(subset=dedup_keys, keep='last')
        removed_count = original_count - len(df_processed)
        if removed_count > 0:
            logger.info(f"중복 제거: {removed_count}건 제거 (기준: {dedup_keys})")
    
    # 🆕 패치: Flow Code 정규화
    if 'Flow_Code' in df_processed.columns:
        df_processed['Flow_Code'] = df_processed['Flow_Code'].apply(normalize_flow_code)
    elif 'Logistics Flow Code' in df_processed.columns:
        df_processed['Logistics Flow Code'] = df_processed['Logistics Flow Code'].apply(normalize_flow_code)
    
    # 🆕 패치: OUT 트랜잭션 부호 처리 (선택적)
    if validation_rules.get('out_negative_pkg', False):
        if 'Transaction_Type' in df_processed.columns and 'Pkg' in df_processed.columns:
            out_mask = df_processed['Transaction_Type'].str.contains('OUT', na=False)
            out_count = out_mask.sum()
            if out_count > 0:
                df_processed.loc[out_mask, 'Pkg'] = df_processed.loc[out_mask, 'Pkg'] * -1
                logger.info(f"OUT 부호 처리: {out_count}건 음수 변환")
        elif 'TxType' in df_processed.columns and 'Pkg' in df_processed.columns:
            out_mask = df_processed['TxType'].str.contains('OUT', na=False)
            out_count = out_mask.sum()
            if out_count > 0:
                df_processed.loc[out_mask, 'Pkg'] = df_processed.loc[out_mask, 'Pkg'] * -1
                logger.info(f"OUT 부호 처리: {out_count}건 음수 변환")
    
    return df_processed 