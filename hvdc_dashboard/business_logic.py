# -*- coding: utf-8 -*-
# HVDC 비즈니스 로직 및 KPI 계산 모듈

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple
from .config import TEU_WEIGHTS, OOG_KEYWORDS, HS_CODE_MAPPING, KPI_CONFIG

logger = logging.getLogger(__name__)

def calc_teu(row: pd.Series) -> float:
    """TEU 계산"""
    teu = 0.0
    for col, weight in TEU_WEIGHTS.items():
        if col in row.index:
            value = pd.to_numeric(row.get(col, 0), errors='coerce')
            if pd.notna(value):
                teu += value * weight
    return teu

def is_oog(row: pd.Series) -> bool:
    """OOG 여부 판단"""
    ship_mode = str(row.get('SHIP\n MODE', '')).upper()
    description = str(row.get('MAIN DESCRIPTION (PO)', '')).upper()
    
    text = f"{ship_mode} {description}"
    return any(keyword in text for keyword in OOG_KEYWORDS)

def get_warehouse(row: pd.Series) -> str:
    """창고 구분"""
    warehouse_cols = ['DSV Indoor', 'DSV Outdoor', 'AAA Storage']
    
    for wh in warehouse_cols:
        if wh in row.index and pd.notna(row.get(wh)) and row[wh] == 1:
            return wh
    return '기타'

def calculate_dem_det(row: pd.Series) -> int:
    """DEM/DET 일수 계산"""
    if '반출일' in row.index and '입고일' in row.index:
        try:
            out_date = pd.to_datetime(row['반출일'])
            in_date = pd.to_datetime(row['입고일'])
            days = (out_date - in_date).days - 3  # 3일 여유
            return max(0, days)
        except:
            return 0
    return 0

def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """데이터 풍부화 (파생 컬럼 생성)"""
    logger.info("데이터 풍부화 시작...")
    
    # TEU 계산
    df['TEU'] = df.apply(calc_teu, axis=1)
    
    # OOG 구분
    df['OOG'] = df.apply(is_oog, axis=1)
    
    # 연월 필드 생성
    if 'Status_Location_Date_Year' in df.columns:
        df['YEAR'] = pd.to_numeric(df['Status_Location_Date_Year'], errors='coerce').fillna(0).astype(int)
        df['MONTH'] = pd.to_numeric(df['Status_Location_Date_Month'], errors='coerce').fillna(0).astype(int)
        df['YYYYMM'] = df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str).str.zfill(2)
    else:
        # CSV 데이터용
        if '입고일' in df.columns:
            # numpy.datetime64를 pandas datetime으로 변환
            df['입고일'] = pd.to_datetime(df['입고일'])
            df['YEAR'] = df['입고일'].dt.year
            df['MONTH'] = df['입고일'].dt.month
            df['YYYYMM'] = df['입고일'].dt.strftime('%Y-%m')
    
    # 창고 구분
    df['WAREHOUSE'] = df.apply(get_warehouse, axis=1)
    
    # HS Code 매핑
    if 'HS Code' not in df.columns and 'CATEGORY' in df.columns:
        df['HS Code'] = df['CATEGORY'].map(HS_CODE_MAPPING).fillna('기타')
    
    # DEM/DET 계산
    if 'DEM/DET(일)' not in df.columns:
        df['DEM/DET(일)'] = df.apply(calculate_dem_det, axis=1)
    
    logger.info("데이터 풍부화 완료")
    return df

def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """KPI 계산"""
    kpis = {
        'total_teu': int(df['TEU'].sum()),
        'oog_count': int(df['OOG'].sum()),
        'total_items': len(df),
        'avg_teu_per_item': float(df['TEU'].mean()),
        'oog_percentage': float((df['OOG'].sum() / len(df)) * 100)
    }
    
    # 금액 관련 KPI
    if 'DUTY AMT\n (AED)' in df.columns:
        kpis['total_duty'] = float(df['DUTY AMT\n (AED)'].sum())
        kpis['avg_duty'] = float(df['DUTY AMT\n (AED)'].mean())
    
    if 'VAT AMT\n (AED)' in df.columns:
        kpis['total_vat'] = float(df['VAT AMT\n (AED)'].sum())
        kpis['avg_vat'] = float(df['VAT AMT\n (AED)'].mean())
    
    # DEM/DET 관련 KPI
    if 'DEM/DET(일)' in df.columns:
        kpis['total_dem_det'] = int(df['DEM/DET(일)'].sum())
        kpis['avg_dem_det'] = float(df['DEM/DET(일)'].mean())
    
    # 창고 점유율 (가정: 전체 10,000㎡)
    if '창고면적' in df.columns:
        kpis['occupancy_rate'] = float(df['창고면적'].sum() / 10000)
    else:
        kpis['occupancy_rate'] = float(len(df) / 1000)  # 샘플 계산
    
    return kpis

def check_alerts(kpis: Dict[str, Any]) -> Dict[str, str]:
    """알림 체크"""
    alerts = {}
    
    # DEM/DET 경고
    if kpis.get('total_dem_det', 0) > KPI_CONFIG['dem_det_threshold']:
        alerts['dem_det'] = f"⚠️ DEM/DET 초과: {kpis['total_dem_det']}일 (임계값: {KPI_CONFIG['dem_det_threshold']}일)"
    
    # 창고 점유율 경고
    if kpis.get('occupancy_rate', 0) > KPI_CONFIG['occupancy_threshold']:
        alerts['occupancy'] = f"⚠️ 창고 점유율 초과: {kpis['occupancy_rate']:.1%} (임계값: {KPI_CONFIG['occupancy_threshold']:.1%})"
    
    # OOG 비율 경고
    if kpis.get('oog_percentage', 0) > 30:  # OOG 30% 이상
        alerts['oog'] = f"⚠️ OOG 비율 높음: {kpis['oog_percentage']:.1f}%"
    
    return alerts

def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """필터 적용"""
    filtered_df = df.copy()
    
    # 연도 필터
    if filters.get('year'):
        filtered_df = filtered_df[filtered_df['YEAR'] == filters['year']]
    
    # 월 필터
    if filters.get('month'):
        filtered_df = filtered_df[filtered_df['MONTH'] == filters['month']]
    
    # 카테고리 필터
    if filters.get('category') and filters['category'] != 'All':
        filtered_df = filtered_df[filtered_df['CATEGORY'] == filters['category']]
    
    # 창고 필터
    if filters.get('warehouse') and filters['warehouse'] != 'All':
        filtered_df = filtered_df[filtered_df['WAREHOUSE'] == filters['warehouse']]
    
    return filtered_df

def get_visualization_data(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """시각화용 데이터 생성"""
    viz_data = {}
    
    # 월별 TEU 추이
    if 'YYYYMM' in df.columns:
        monthly_teu = df.groupby('YYYYMM')['TEU'].sum().reset_index()
        viz_data['monthly_teu'] = monthly_teu
    
    # 카테고리별 TEU
    if 'CATEGORY' in df.columns:
        category_teu = df.groupby('CATEGORY')['TEU'].sum().reset_index()
        viz_data['category_teu'] = category_teu
    
    # 창고별 TEU
    if 'WAREHOUSE' in df.columns:
        warehouse_teu = df.groupby('WAREHOUSE')['TEU'].sum().reset_index()
        viz_data['warehouse_teu'] = warehouse_teu
    
    # OOG 비율
    if 'OOG' in df.columns:
        oog_ratio = df['OOG'].value_counts(normalize=True).reset_index()
        oog_ratio.columns = ['OOG', 'Ratio']
        viz_data['oog_ratio'] = oog_ratio
    
    return viz_data

def get_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """요약 테이블 생성"""
    display_cols = ['HVDC CODE', 'CATEGORY', 'MAIN DESCRIPTION (PO)', 'TEU', 'OOG', 'WAREHOUSE']
    
    # 존재하는 컬럼만 선택
    available_cols = [col for col in display_cols if col in df.columns]
    
    # 금액 컬럼 추가
    if 'DUTY AMT\n (AED)' in df.columns:
        available_cols.append('DUTY AMT\n (AED)')
    if 'VAT AMT\n (AED)' in df.columns:
        available_cols.append('VAT AMT\n (AED)')
    
    return df[available_cols].head(50)  # 상위 50건만 표시 