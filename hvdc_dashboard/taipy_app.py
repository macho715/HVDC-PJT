# -*- coding: utf-8 -*-
# HVDC Taipy GUI 애플리케이션

import pandas as pd
import logging
from taipy.gui import Gui
import taipy.gui.builder as tgb
from .data_loader import load_data, get_data_info
from .business_logic import enrich_data, calculate_kpis, check_alerts, apply_filters, get_visualization_data, get_summary_table
from .config import UI_CONFIG

logger = logging.getLogger(__name__)

# 전역 상태 변수
df = None
data_info = None
kpis = {}
alerts = {}
viz_data = {}
summary_table = pd.DataFrame()

# 필터 상태
selected_year = None
selected_month = None
selected_category = "All"
selected_warehouse = "All"
selected_tab = "TEU Trend"

# 에러 메시지
error_msg = ""

def initialize_data():
    """데이터 초기화"""
    global df, data_info, kpis, alerts, viz_data, summary_table, selected_year, selected_month
    
    try:
        # 데이터 로드
        df = load_data()
        df = enrich_data(df)
        
        # 데이터 정보
        data_info = get_data_info(df)
        
        # 초기 KPI 계산
        kpis = calculate_kpis(df)
        
        # 알림 체크
        alerts = check_alerts(kpis)
        
        # 시각화 데이터
        viz_data = get_visualization_data(df)
        
        # 요약 테이블
        summary_table = get_summary_table(df)
        
        # 초기 필터 설정
        if 'YEAR' in df.columns:
            selected_year = int(df['YEAR'].min())
        if 'MONTH' in df.columns:
            selected_month = int(df['MONTH'].min())
        
        logger.info("데이터 초기화 완료")
        
    except Exception as e:
        logger.error(f"데이터 초기화 실패: {e}")
        error_msg = f"데이터 로드 실패: {e}"

def apply_filter():
    """필터 적용 및 데이터 업데이트"""
    global kpis, alerts, viz_data, summary_table
    
    try:
        if df is None:
            return
        
        # 필터 적용
        filters = {
            'year': selected_year,
            'month': selected_month,
            'category': selected_category,
            'warehouse': selected_warehouse
        }
        
        filtered_df = apply_filters(df, filters)
        
        # KPI 재계산
        kpis = calculate_kpis(filtered_df)
        
        # 알림 재체크
        alerts = check_alerts(kpis)
        
        # 시각화 데이터 업데이트
        viz_data = get_visualization_data(filtered_df)
        
        # 요약 테이블 업데이트
        summary_table = get_summary_table(filtered_df)
        
        logger.info("필터 적용 완료")
        
    except Exception as e:
        logger.error(f"필터 적용 실패: {e}")
        error_msg = f"필터 적용 실패: {e}"

def on_change(state, var, val):
    """상태 변경 핸들러"""
    if var in ["selected_year", "selected_month", "selected_category", "selected_warehouse", "selected_tab"]:
        apply_filter()

def on_init(state):
    """초기화 핸들러"""
    initialize_data()

# Taipy UI 구성
with tgb.Page() as page:
    # 헤더
    tgb.text("# 🚢 HVDC 프로젝트 물류 KPI 대시보드 │ 삼성C&T (ADNOC/DSV)", mode="md")
    
    # 에러 메시지
    if error_msg:
        tgb.text(f"❌ {error_msg}", mode="md")
    
    # 데이터 정보
    if data_info:
        tgb.text(f"📊 데이터: {data_info['total_rows']}건, {data_info['total_columns']}컬럼", mode="md")
    
    # 필터 섹션
    tgb.text("## 🔍 필터", mode="md")
    with tgb.layout(columns="1 1 1 1"):
        tgb.text("**연도**")
        tgb.selector(
            value="{selected_year}", 
            lov=lambda state: sorted(df['YEAR'].unique()) if df is not None else [],
            dropdown=True
        )
        tgb.text("**월**")
        tgb.selector(
            value="{selected_month}", 
            lov=lambda state: sorted(df['MONTH'].unique()) if df is not None else [],
            dropdown=True
        )
        tgb.text("**카테고리**")
        tgb.selector(
            value="{selected_category}", 
            lov=lambda state: ["All"] + sorted(df['CATEGORY'].unique().tolist()) if df is not None else ["All"],
            dropdown=True
        )
        tgb.text("**창고**")
        tgb.selector(
            value="{selected_warehouse}", 
            lov=lambda state: ["All"] + sorted(df['WAREHOUSE'].unique().tolist()) if df is not None else ["All"],
            dropdown=True
        )
    
    # KPI 요약
    tgb.text("## 📊 KPI 요약", mode="md")
    with tgb.layout(columns="1 1 1 1"):
        tgb.text("**TEU 합계**\n{int(kpis.get('total_teu', 0))}")
        tgb.text("**OOG 건수**\n{int(kpis.get('oog_count', 0))}")
        tgb.text("**총 건수**\n{int(kpis.get('total_items', 0))}")
        tgb.text("**OOG 비율**\n{str(round(kpis.get('oog_percentage', 0), 1))}%")
    
    # 추가 KPI
    with tgb.layout(columns="1 1 1 1"):
        if 'total_duty' in kpis:
            tgb.text("**총 관세**\n{str(int(kpis.get('total_duty', 0)))} AED")
        if 'total_vat' in kpis:
            tgb.text("**총 VAT**\n{str(int(kpis.get('total_vat', 0)))} AED")
        if 'total_dem_det' in kpis:
            tgb.text("**DEM/DET**\n{str(int(kpis.get('total_dem_det', 0)))}일")
        if 'occupancy_rate' in kpis:
            tgb.text("**창고점유율**\n{str(round(kpis.get('occupancy_rate', 0) * 100, 1))}%")
    
    # 알림 섹션
    if alerts:
        tgb.text("## ⚠️ 알림", mode="md")
        for alert_type, alert_msg in alerts.items():
            tgb.text(f"**{alert_msg}**", mode="md")
    
    # 탭 선택
    tgb.text("## 📈 분석", mode="md")
    tgb.selector(
        value="{selected_tab}", 
        lov=["TEU Trend", "Category Analysis", "Warehouse Analysis", "KPI Table", "Raw Data"], 
        dropdown=True
    )
    
    # 탭별 콘텐츠
    with tgb.part(render="{selected_tab == 'TEU Trend'}"):
        if 'monthly_teu' in viz_data:
            tgb.chart(
                data="{viz_data['monthly_teu']}", 
                x="YYYYMM", 
                y="TEU", 
                type="bar", 
                title="📈 월별 TEU 추이"
            )
        else:
            tgb.text("데이터가 없습니다.")
    
    with tgb.part(render="{selected_tab == 'Category Analysis'}"):
        if 'category_teu' in viz_data:
            tgb.chart(
                data="{viz_data['category_teu']}", 
                x="CATEGORY", 
                y="TEU", 
                type="pie", 
                title="📊 카테고리별 TEU 분포"
            )
        else:
            tgb.text("데이터가 없습니다.")
    
    with tgb.part(render="{selected_tab == 'Warehouse Analysis'}"):
        if 'warehouse_teu' in viz_data:
            tgb.chart(
                data="{viz_data['warehouse_teu']}", 
                x="WAREHOUSE", 
                y="TEU", 
                type="bar", 
                title="🏭 창고별 TEU 분포"
            )
        else:
            tgb.text("데이터가 없습니다.")
    
    with tgb.part(render="{selected_tab == 'KPI Table'}"):
        tgb.table(data="{summary_table}", title="📋 KPI 상세 테이블")
    
    with tgb.part(render="{selected_tab == 'Raw Data'}"):
        if df is not None:
            tgb.table(data="{df.head(100)}", title="📄 원본 데이터 (상위 100건)")
        else:
            tgb.text("데이터가 없습니다.")

# Taipy 앱 생성
app = Gui(page) 