# -*- coding: utf-8 -*-
# HVDC 프로젝트 설정 관리

import os
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent

# 데이터 파일 경로 (환경변수 또는 기본값)
DATA_PATH = os.environ.get("HVDC_DATA_PATH", str(PROJECT_ROOT / "data" / "HVDC PKGS.xlsx"))
SHEET_NAME = os.environ.get("HVDC_SHEET_NAME", "LSR")

# 백업 데이터 경로들
BACKUP_DATA_PATHS = [
    str(PROJECT_ROOT / "data" / "HVDC PKGS.xlsx"),
    str(PROJECT_ROOT / "data" / "hvdc_logistics.csv"),
    str(PROJECT_ROOT / "HVDC_PJT" / "data" / "HVDC PKGS.xlsx"),
    str(PROJECT_ROOT / "HVDC_PJT" / "data" / "hvdc_logistics.csv"),
    str(PROJECT_ROOT / "data" / "HVDC WAREHOUSE_HITACHI(HE).xlsx"),
    str(PROJECT_ROOT / "data" / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
]

# KPI 설정
KPI_CONFIG = {
    'pressure_limit': 4.0,  # t/m² 압력 한계
    'dem_det_threshold': 20,  # DEM/DET 경고 임계값 (일)
    'occupancy_threshold': 0.9,  # 창고 점유율 경고 임계값
    'confidence_threshold': 0.95  # 신뢰도 임계값
}

# TEU 가중치 설정
TEU_WEIGHTS = {
    '20DC': 1,
    '40DC': 2,
    '40HQ': 2,
    '40FR(IN)': 2
}

# OOG 키워드
OOG_KEYWORDS = ['OOG', 'FR', 'OT', 'OVERDIMENSION', 'OVERWEIGHT']

# HS Code 매핑
HS_CODE_MAPPING = {
    "전자": "8471",
    "사무": "9403", 
    "OOG": "8905",
    "기계": "8429",
    "전기": "8504"
}

# 로깅 설정
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': str(PROJECT_ROOT / "hvdc_dashboard" / "logs" / "hvdc_dashboard.log")
}

# UI 설정
UI_CONFIG = {
    'title': "HVDC 프로젝트 물류 KPI 대시보드 │ 삼성C&T (ADNOC/DSV)",
    'dark_mode': True,
    'port': 'auto',
    'debug': True,
    'show_upload': False
} 