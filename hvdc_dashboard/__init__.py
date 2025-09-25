# -*- coding: utf-8 -*-
# HVDC Dashboard Package

__version__ = "1.0.0"
__author__ = "삼성C&T HVDC 프로젝트팀"
__description__ = "HVDC 프로젝트 물류 KPI 대시보드"

from .config import *
from .data_loader import load_data, get_data_info
from .business_logic import enrich_data, calculate_kpis, check_alerts
from .taipy_app import app

__all__ = [
    'load_data',
    'get_data_info', 
    'enrich_data',
    'calculate_kpis',
    'check_alerts',
    'app'
] 