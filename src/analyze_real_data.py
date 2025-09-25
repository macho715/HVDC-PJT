"""
실제 HVDC 데이터 파일 분석 및 구조 파악
- HITACHI(HE) 데이터
- SIMENSE(SIM) 데이터
- 기존 Calculator와 호환성 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analyze_hitachi_data():
    """HITACHI 데이터 분석"""
    print("📊 HITACHI 데이터 분석 시작...")
    
    try:
        # HITACHI 데이터 읽기
        df = pd.read_excel("../data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
        
        print(f"   📏 크기: {df.shape[0]} 행 × {df.shape[1]} 열")
        print(f"   📋 컬럼 목록:")
        for i, col in enumerate(df.columns):
            print(f"      {i+1:2d}. {col}")
        
        print("\n   📄 데이터 타입:")
        print(df.dtypes)
        
        print("\n   📊 샘플 데이터 (첫 3행):")
        print(df.head(3))
        
        print("\n   📈 기본 통계:")
        print(df.describe())
        
        return df
        
    except Exception as e:
        print(f"   ❌ HITACHI 데이터 읽기 오류: {str(e)}")
        return None

def analyze_simense_data():
    """SIMENSE 데이터 분석"""
    print("\n📊 SIMENSE 데이터 분석 시작...")
    
    try:
        # SIMENSE 데이터 읽기
        df = pd.read_excel("../data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
        
        print(f"   📏 크기: {df.shape[0]} 행 × {df.shape[1]} 열")
        print(f"   📋 컬럼 목록:")
        for i, col in enumerate(df.columns):
            print(f"      {i+1:2d}. {col}")
        
        print("\n   📄 데이터 타입:")
        print(df.dtypes)
        
        print("\n   📊 샘플 데이터 (첫 3행):")
        print(df.head(3))
        
        print("\n   📈 기본 통계:")
        print(df.describe())
        
        return df
        
    except Exception as e:
        print(f"   ❌ SIMENSE 데이터 읽기 오류: {str(e)}")
        return None

def identify_warehouse_and_site_columns(df):
    """창고 및 현장 컬럼 식별"""
    print("\n🔍 창고 및 현장 컬럼 식별...")
    
    # 일반적인 창고 패턴
    warehouse_patterns = ['DSV', 'Storage', 'Warehouse', 'Indoor', 'Outdoor', 'Markaz', 'MZP', 'Hauler', 'DHL']
    
    # 일반적인 현장 패턴
    site_patterns = ['MIR', 'SHU', 'DAS', 'AGI', 'MOSB', 'Site', 'Project']
    
    warehouse_cols = []
    site_cols = []
    date_cols = []
    
    for col in df.columns:
        col_str = str(col).upper()
        
        # 창고 컬럼 확인
        if any(pattern.upper() in col_str for pattern in warehouse_patterns):
            warehouse_cols.append(col)
        
        # 현장 컬럼 확인
        elif any(pattern.upper() in col_str for pattern in site_patterns):
            site_cols.append(col)
        
        # 날짜 컬럼 확인
        elif 'DATE' in col_str or pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)
    
    print(f"   🏭 식별된 창고 컬럼 ({len(warehouse_cols)}개): {warehouse_cols}")
    print(f"   🏗️ 식별된 현장 컬럼 ({len(site_cols)}개): {site_cols}")
    print(f"   📅 식별된 날짜 컬럼 ({len(date_cols)}개): {date_cols}")
    
    return warehouse_cols, site_cols, date_cols

def check_compatibility_with_calculator(df):
    """기존 Calculator와 호환성 확인"""
    print("\n🔧 기존 Calculator와 호환성 확인...")
    
    # 필수 컬럼 확인
    required_cols = ['Item', 'Status_Current', 'Status_Location']
    missing_cols = []
    
    for col in required_cols:
        if col not in df.columns:
            missing_cols.append(col)
    
    if missing_cols:
        print(f"   ⚠️  누락된 필수 컬럼: {missing_cols}")
        
        # 대체 컬럼 찾기
        potential_item_cols = [col for col in df.columns if 'item' in col.lower() or 'id' in col.lower()]
        potential_status_cols = [col for col in df.columns if 'status' in col.lower() or 'current' in col.lower()]
        
        print(f"   🔍 Item 컬럼 후보: {potential_item_cols}")
        print(f"   🔍 Status 컬럼 후보: {potential_status_cols}")
    else:
        print("   ✅ 모든 필수 컬럼이 존재합니다.")
    
    return missing_cols

def suggest_data_mapping(df):
    """데이터 매핑 제안"""
    print("\n📋 데이터 매핑 제안...")
    
    # 첫 번째 컬럼을 Item으로 가정
    first_col = df.columns[0]
    print(f"   🔸 '{first_col}' → Item 컬럼으로 매핑 제안")
    
    # 날짜 컬럼들을 창고/현장으로 분류
    date_cols = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]) or 'date' in col.lower():
            date_cols.append(col)
    
    print(f"   🔸 날짜 컬럼들 ({len(date_cols)}개): {date_cols}")
    
    # 마지막 몇 개 컬럼을 Status 정보로 가정
    last_cols = df.columns[-3:]
    print(f"   🔸 Status 컬럼 후보 (마지막 3개): {list(last_cols)}")
    
    return {
        'item_col': first_col,
        'date_cols': date_cols,
        'status_cols': list(last_cols)
    }

def main():
    """메인 분석 함수"""
    print("🚀 실제 HVDC 데이터 분석 시작")
    print("=" * 60)
    
    # HITACHI 데이터 분석
    hitachi_df = analyze_hitachi_data()
    if hitachi_df is not None:
        warehouse_cols, site_cols, date_cols = identify_warehouse_and_site_columns(hitachi_df)
        missing_cols = check_compatibility_with_calculator(hitachi_df)
        mapping_suggestion = suggest_data_mapping(hitachi_df)
        
        print("\n📊 HITACHI 데이터 매핑 제안:")
        print(f"   Item 컬럼: {mapping_suggestion['item_col']}")
        print(f"   날짜 컬럼: {len(mapping_suggestion['date_cols'])}개")
        print(f"   Status 컬럼: {mapping_suggestion['status_cols']}")
    
    # SIMENSE 데이터 분석
    simense_df = analyze_simense_data()
    if simense_df is not None:
        warehouse_cols, site_cols, date_cols = identify_warehouse_and_site_columns(simense_df)
        missing_cols = check_compatibility_with_calculator(simense_df)
        mapping_suggestion = suggest_data_mapping(simense_df)
        
        print("\n📊 SIMENSE 데이터 매핑 제안:")
        print(f"   Item 컬럼: {mapping_suggestion['item_col']}")
        print(f"   날짜 컬럼: {len(mapping_suggestion['date_cols'])}개")
        print(f"   Status 컬럼: {mapping_suggestion['status_cols']}")
    
    print("\n" + "=" * 60)
    print("✅ 실제 데이터 분석 완료")
    
    return hitachi_df, simense_df

if __name__ == "__main__":
    main() 