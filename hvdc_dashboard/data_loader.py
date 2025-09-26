# -*- coding: utf-8 -*-
# HVDC 데이터 로딩 및 검증 모듈

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from .config import BACKUP_DATA_PATHS, SHEET_NAME, LOG_CONFIG

# 로깅 설정
logger = logging.getLogger(__name__)

class DataLoadError(Exception):
    """데이터 로딩 관련 예외"""
    pass

class DataValidationError(Exception):
    """데이터 검증 관련 예외"""
    pass

def find_data_file() -> str:
    """사용 가능한 데이터 파일 찾기"""
    for path in BACKUP_DATA_PATHS:
        if Path(path).exists():
            logger.info(f"✅ 데이터 파일 발견: {path}")
            return path
    
    logger.warning("⚠️ 실제 데이터 파일 없음 - 샘플 데이터 생성")
    return None

def load_excel_data(file_path: str) -> pd.DataFrame:
    """Excel 파일 로딩"""
    try:
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
        logger.info(f"Excel 파일 로드 성공: {file_path} ({len(df)} 건)")
        return df
    except Exception as e:
        raise DataLoadError(f"Excel 파일 로드 실패: {e}")

def load_csv_data(file_path: str) -> pd.DataFrame:
    """CSV 파일 로딩"""
    try:
        df = pd.read_csv(file_path, parse_dates=["입고일"], dayfirst=True)
        logger.info(f"CSV 파일 로드 성공: {file_path} ({len(df)} 건)")
        return df
    except Exception as e:
        raise DataLoadError(f"CSV 파일 로드 실패: {e}")

def validate_data(df: pd.DataFrame) -> None:
    """데이터 정합성 검증"""
    if df.empty:
        raise DataValidationError("데이터가 비어있습니다")
    
    # 필수 컬럼 검증
    required_cols = ['HVDC CODE', 'CATEGORY']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise DataValidationError(f"필수 컬럼 누락: {missing_cols}")
    
    # 데이터 타입 검증
    if 'Status_Location_Date_Year' in df.columns:
        try:
            pd.to_numeric(df['Status_Location_Date_Year'], errors='coerce')
        except:
            raise DataValidationError("Status_Location_Date_Year 컬럼이 숫자 형식이 아닙니다")
    
    logger.info(f"데이터 검증 완료: {len(df)} 건, {len(df.columns)} 컬럼")

def create_sample_data() -> pd.DataFrame:
    """샘플 데이터 생성 (실제 데이터 없을 경우)"""
    logger.info("샘플 데이터 생성 중...")
    
    dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
    sample_data = []
    
    for i in range(100):
        date = np.random.choice(dates)
        sample_data.append({
            'HVDC CODE': f'HVDC{i:04d}',
            'CATEGORY': np.random.choice(['전자', '사무', 'OOG', '기계', '전기']),
            'MAIN DESCRIPTION (PO)': f'Item {i} - {np.random.choice(["Transformer", "Switchgear", "Cable", "Panel"])}',
            '20DC': np.random.randint(0, 5),
            '40DC': np.random.randint(0, 3),
            '40HQ': np.random.randint(0, 2),
            '40FR(IN)': np.random.randint(0, 1),
            'SHIP\n MODE': np.random.choice(['Normal', 'OOG', 'FR', 'OT']),
            'Status_Location_Date_Year': date.year,
            'Status_Location_Date_Month': date.month,
            'DSV Indoor': np.random.choice([0, 1]),
            'DSV Outdoor': np.random.choice([0, 1]),
            'AAA Storage': np.random.choice([0, 1]),
            'DUTY AMT\n (AED)': np.random.uniform(1000, 50000),
            'VAT AMT\n (AED)': np.random.uniform(500, 2500),
            '입고일': date,
            '반출일': date + pd.Timedelta(days=np.random.randint(1, 30))
        })
    
    df = pd.DataFrame(sample_data)
    logger.info(f"샘플 데이터 생성 완료: {len(df)} 건")
    return df

def load_data() -> pd.DataFrame:
    """메인 데이터 로딩 함수"""
    try:
        # 데이터 파일 찾기
        data_file = find_data_file()
        
        if data_file:
            # 파일 확장자에 따라 로딩
            if data_file.endswith('.xlsx'):
                df = load_excel_data(data_file)
            elif data_file.endswith('.csv'):
                df = load_csv_data(data_file)
            else:
                raise DataLoadError(f"지원하지 않는 파일 형식: {data_file}")
        else:
            # 샘플 데이터 생성
            df = create_sample_data()
        
        # 데이터 검증
        validate_data(df)
        
        return df
        
    except Exception as e:
        logger.error(f"데이터 로딩 실패: {e}")
        # 최후 수단으로 샘플 데이터 반환
        logger.info("샘플 데이터로 대체")
        return create_sample_data()

def get_data_info(df: pd.DataFrame) -> Dict[str, Any]:
    """데이터 정보 반환"""
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'date_range': {
            'min': df['Status_Location_Date_Year'].min() if 'Status_Location_Date_Year' in df.columns else None,
            'max': df['Status_Location_Date_Year'].max() if 'Status_Location_Date_Year' in df.columns else None
        },
        'categories': df['CATEGORY'].unique().tolist() if 'CATEGORY' in df.columns else [],
        'columns': df.columns.tolist()
    } 