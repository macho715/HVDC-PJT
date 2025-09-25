# -*- coding: utf-8 -*-
# MR.CHA│삼성C&T HVDC 프로젝트형 실무 대시보드

from taipy.gui import Gui
import pandas as pd
import datetime
import os

# 1. 데이터 불러오기 및 전처리
def load_hvdc_data():
    """HVDC 데이터 로딩 - 여러 소스 시도"""
    data_sources = [
        "data/HVDC PKGS.xlsx",
        "data/hvdc_logistics.csv", 
        "HVDC_PJT/data/HVDC PKGS.xlsx",
        "HVDC_PJT/data/hvdc_logistics.csv"
    ]
    
    for source in data_sources:
        try:
            if source.endswith('.xlsx'):
                df = pd.read_excel(source, sheet_name="LSR")
                print(f"✅ Excel 파일 로드 성공: {source}")
                return process_excel_data(df)
            elif source.endswith('.csv'):
                df = pd.read_csv(source, parse_dates=["입고일"], dayfirst=True)
                print(f"✅ CSV 파일 로드 성공: {source}")
                return process_csv_data(df)
        except Exception as e:
            print(f"❌ {source} 로드 실패: {e}")
            continue
    
    # 샘플 데이터 생성 (실제 데이터 없을 경우)
    print("⚠️ 실제 데이터 없음 - 샘플 데이터 생성")
    return create_sample_data()

def process_excel_data(df):
    """Excel 데이터 전처리"""
    # TEU 산정 함수
    def calc_teu(row):
        teu = 0
        teu += row.get('20DC', 0) * 1
        teu += row.get('40DC', 0) * 2
        teu += row.get('40HQ', 0) * 2
        teu += row.get('40FR(IN)', 0) * 2
        return teu

    # 컨테이너 컬럼 숫자 변환
    for col in ['20DC', '40DC', '40HQ', '40FR(IN)']:
        if col in df.columns:
            df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0)

    df['TEU'] = df.apply(calc_teu, axis=1)

    # OOG 구분
    def is_oog(row):
        txt = str(row.get('SHIP\n MODE', '')).upper() + str(row.get('MAIN DESCRIPTION (PO)', '')).upper()
        return any(key in txt for key in ['OOG', 'FR', 'OT'])

    df['OOG'] = df.apply(is_oog, axis=1)

    # 연월 필드 생성
    if 'Status_Location_Date_Year' in df.columns:
        df['YEAR'] = df['Status_Location_Date_Year'].astype('Int64').fillna(0)
        df['MONTH'] = df['Status_Location_Date_Month'].astype('Int64').fillna(0)
        df['YYYYMM'] = df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str).str.zfill(2)
    else:
        df['YEAR'] = 2024
        df['MONTH'] = 1
        df['YYYYMM'] = '2024-01'

    # 창고 구분
    warehouse_cols = ['DSV Indoor', 'DSV Outdoor', 'AAA Storage']
    def get_warehouse(row):
        for wh in warehouse_cols:
            if wh in df.columns and pd.notnull(row.get(wh)) and row[wh] == 1:
                return wh
        return '기타'
    
    df['WAREHOUSE'] = df.apply(get_warehouse, axis=1)
    
    return df

def process_csv_data(df):
    """CSV 데이터 전처리"""
    # HS Code 매핑
    if "HS Code" not in df.columns:
        df["HS Code"] = df["카테고리"].map({
            "전자": "8471", "사무": "9403", "OOG": "8905"
        }).fillna("기타")
    
    # OOG 구분
    if "OOG" not in df.columns:
        df["OOG"] = df["상품명"].str.contains("트랜스포머|중량물").map({True: "OOG", False: "일반"})
    
    # DEM/DET 계산
    if "DEM/DET(일)" not in df.columns and "반출일" in df.columns:
        df["DEM/DET(일)"] = (df["반출일"] - df["입고일"]).dt.days - 3
        df["DEM/DET(일)"] = df["DEM/DET(일)"].apply(lambda x: x if x > 0 else 0)
    
    # 월 필드 생성
    df["월"] = df["입고일"].dt.to_period("M").astype(str)
    df['YYYYMM'] = df["월"]
    
    return df

def create_sample_data():
    """샘플 데이터 생성"""
    import numpy as np
    
    dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
    sample_data = []
    
    for i in range(100):
        date = np.random.choice(dates)
        sample_data.append({
            'HVDC CODE': f'HVDC{i:04d}',
            'CATEGORY': np.random.choice(['전자', '사무', 'OOG']),
            'MAIN DESCRIPTION (PO)': f'Item {i}',
            '20DC': np.random.randint(0, 5),
            '40DC': np.random.randint(0, 3),
            '40HQ': np.random.randint(0, 2),
            '40FR(IN)': np.random.randint(0, 1),
            'SHIP\n MODE': np.random.choice(['Normal', 'OOG', 'FR']),
            'Status_Location_Date_Year': date.year,
            'Status_Location_Date_Month': date.month,
            'DSV Indoor': np.random.choice([0, 1]),
            'DSV Outdoor': np.random.choice([0, 1]),
            'AAA Storage': np.random.choice([0, 1]),
            'DUTY AMT\n (AED)': np.random.uniform(1000, 50000),
            'VAT AMT\n (AED)': np.random.uniform(500, 2500)
        })
    
    df = pd.DataFrame(sample_data)
    return process_excel_data(df)

# 2. 데이터 로드
df = load_hvdc_data()

# 3. 필터 옵션 생성
years = sorted(df['YEAR'].dropna().unique()) if 'YEAR' in df.columns else [2024]
months = sorted(df['MONTH'].dropna().unique()) if 'MONTH' in df.columns else [1]
categories = ["All"] + df['CATEGORY'].dropna().unique().tolist() if 'CATEGORY' in df.columns else ["All"]
warehouses = ["All"] + df['WAREHOUSE'].dropna().unique().tolist() if 'WAREHOUSE' in df.columns else ["All"]

# 4. 대시보드 상태 변수
selected_year = years[0] if years else 2024
selected_month = months[0] if months else 1
selected_category = "All"
selected_warehouse = "All"
selected_tab = "TEU Trend"

# KPI 변수
total_teu = 0
oog_cnt = 0
duty_amt = 0.0
vat_amt = 0.0
dem_det_days = 0
occupancy_rate = 0.0

# 5. 필터 및 KPI 계산 함수
def apply_filter(state):
    d = df.copy()
    
    # 연도/월 필터
    if hasattr(state, 'selected_year') and state.selected_year:
        d = d[d['YEAR'] == state.selected_year]
    if hasattr(state, 'selected_month') and state.selected_month:
        d = d[d['MONTH'] == state.selected_month]
    
    # 카테고리/창고 필터
    if hasattr(state, 'selected_category') and state.selected_category != "All":
        d = d[d['CATEGORY'] == state.selected_category]
    if hasattr(state, 'selected_warehouse') and state.selected_warehouse != "All":
        d = d[d['WAREHOUSE'] == state.selected_warehouse]

    # KPI 계산
    state.total_teu = int(d['TEU'].sum()) if 'TEU' in d.columns else 0
    state.oog_cnt = int(d['OOG'].sum()) if 'OOG' in d.columns else 0
    state.duty_amt = d['DUTY AMT\n (AED)'].sum() if 'DUTY AMT\n (AED)' in d.columns else 0.0
    state.vat_amt = d['VAT AMT\n (AED)'].sum() if 'VAT AMT\n (AED)' in d.columns else 0.0
    
    # DEM/DET 및 점유율 계산
    if 'DEM/DET(일)' in d.columns:
        state.dem_det_days = int(d['DEM/DET(일)'].sum())
    else:
        state.dem_det_days = 0
    
    # 창고 점유율 (가정: 전체 10,000㎡)
    if '창고면적' in d.columns:
        state.occupancy_rate = d['창고면적'].sum() / 10000
    else:
        state.occupancy_rate = len(d) / 1000  # 샘플 계산

    # 시각화 데이터
    if 'YYYYMM' in d.columns:
        state.monthly_teu = d.groupby('YYYYMM')['TEU'].sum().reset_index()
    else:
        state.monthly_teu = pd.DataFrame({'YYYYMM': ['2024-01'], 'TEU': [state.total_teu]})
    
    # KPI 테이블
    display_cols = ['HVDC CODE', 'CATEGORY', 'MAIN DESCRIPTION (PO)', 'TEU', 'OOG', 'WAREHOUSE']
    if 'DUTY AMT\n (AED)' in d.columns:
        display_cols.append('DUTY AMT\n (AED)')
    if 'VAT AMT\n (AED)' in d.columns:
        display_cols.append('VAT AMT\n (AED)')
    
    state.kpi_table = d[display_cols] if all(col in d.columns for col in display_cols) else d.head()
    state.raw_data = d

def on_change(state, var, val):
    if var in {"selected_year", "selected_month", "selected_category", "selected_warehouse", "selected_tab"}:
        apply_filter(state)

def on_init(state):
    apply_filter(state)

# 6. Taipy UI 구조
import taipy.gui.builder as tgb

with tgb.Page() as page:
    tgb.text("# 🚢 HVDC 프로젝트 물류 KPI 대시보드 │ 삼성C&T (ADNOC/DSV)", mode="md")
    
    # 필터 섹션
    with tgb.layout(columns="1 1 1 1"):
        tgb.text("**연도**")
        tgb.selector(value="{selected_year}", lov=years, dropdown=True)
        tgb.text("**월**")
        tgb.selector(value="{selected_month}", lov=months, dropdown=True)
        tgb.text("**카테고리**")
        tgb.selector(value="{selected_category}", lov=categories, dropdown=True)
        tgb.text("**창고**")
        tgb.selector(value="{selected_warehouse}", lov=warehouses, dropdown=True)
    
    # KPI 요약
    tgb.text("## 📊 KPI 요약", mode="md")
    with tgb.layout(columns="1 1 1 1"):
        tgb.text("**TEU 합계**\n{int(total_teu)}")
        tgb.text("**OOG 건수**\n{int(oog_cnt)}")
        tgb.text("**관세**\n{duty_amt:,.0f} AED")
        tgb.text("**VAT**\n{vat_amt:,.0f} AED")
    
    # 추가 KPI (있는 경우)
    if 'dem_det_days' in locals():
        with tgb.layout(columns="1 1"):
            tgb.text("**DEM/DET(일)**\n{int(dem_det_days)}")
            tgb.text("**창고점유율**\n{(occupancy_rate * 100):.1f}%")
    
    # 탭 선택
    tgb.selector(value="{selected_tab}", lov=["TEU Trend", "KPI Table", "Raw Data"], dropdown=True)
    
    # 탭별 콘텐츠
    with tgb.part(render="{selected_tab == 'TEU Trend'}"):
        tgb.chart(data="{monthly_teu}", x="YYYYMM", y="TEU", type="bar", title="📈 월별 TEU 추이")
    
    with tgb.part(render="{selected_tab == 'KPI Table'}"):
        tgb.table(data="{kpi_table}", title="📋 KPI 상세 테이블")
    
    with tgb.part(render="{selected_tab == 'Raw Data'}"):
        tgb.table(data="{raw_data}", title="📄 원본 데이터")

# 7. 실행
if __name__ == "__main__":
    print("🚀 HVDC 대시보드 시작...")
    print(f"📊 데이터 로드 완료: {len(df)} 건")
    print(f"📅 기간: {df['YEAR'].min() if 'YEAR' in df.columns else 'N/A'} ~ {df['YEAR'].max() if 'YEAR' in df.columns else 'N/A'}")
    
    Gui(page).run(
        title="HVDC Logistics Dashboard", 
        port="auto", 
        dark_mode=True, 
        debug=True,
        show_upload=False
    )
