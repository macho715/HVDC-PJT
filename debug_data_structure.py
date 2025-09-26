#!/usr/bin/env python3
"""
실제 데이터 구조 분석 및 디버깅
HVDC 물류 마스터 시스템 v3.4-mini
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def analyze_data_structure():
    """실제 데이터 구조 분석"""
    print("🔍 실제 데이터 구조 분석 시작")
    print("=" * 60)
    
    # 데이터 로드
    main_source = "MACHO_통합관리_20250702_205301/MACHO_Final_Report_Complete_20250703_230904.xlsx"
    
    try:
        df = pd.read_excel(main_source, engine='openpyxl')
        print(f"✅ 데이터 로드 성공: {len(df)}건, {len(df.columns)}개 컬럼")
        
        # 기본 정보
        print(f"\n📊 기본 정보:")
        print(f"- 데이터 건수: {len(df):,}건")
        print(f"- 컬럼 수: {len(df.columns)}개")
        print(f"- 메모리 사용량: {df.memory_usage().sum() / 1024 / 1024:.2f} MB")
        
        # 컬럼 목록 출력
        print(f"\n📋 전체 컬럼 목록:")
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
        
        # 창고 관련 컬럼 찾기
        print(f"\n🏭 창고 관련 컬럼:")
        warehouse_keywords = ['Storage', 'DSV', 'MOSB', 'Hauler', 'Warehouse', '창고']
        warehouse_columns = []
        for col in df.columns:
            if any(keyword.lower() in col.lower() for keyword in warehouse_keywords):
                warehouse_columns.append(col)
                print(f"  - {col}")
        
        # 현장 관련 컬럼 찾기
        print(f"\n🏗️ 현장 관련 컬럼:")
        site_keywords = ['Site', 'AGI', 'DAS', 'MIR', 'SHU', '현장']
        site_columns = []
        for col in df.columns:
            if any(keyword.lower() in col.lower() for keyword in site_keywords):
                site_columns.append(col)
                print(f"  - {col}")
        
        # 날짜 관련 컬럼 찾기
        print(f"\n📅 날짜 관련 컬럼:")
        date_columns = []
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'Date' in col or 'date' in col or '_Date' in col:
                date_columns.append(col)
                print(f"  - {col}: {df[col].dtype}")
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    print(f"    범위: {df[col].min()} ~ {df[col].max()}")
                    print(f"    누락값: {df[col].isna().sum()}개")
        
        # 위치 관련 컬럼 분석
        print(f"\n📍 위치 관련 컬럼:")
        location_keywords = ['Location', 'Status', 'Current', 'Site']
        location_columns = []
        for col in df.columns:
            if any(keyword.lower() in col.lower() for keyword in location_keywords):
                location_columns.append(col)
                print(f"  - {col}")
                if col in df.columns:
                    print(f"    유니크 값: {df[col].nunique()}개")
                    print(f"    Top 5 값:")
                    try:
                        top_values = df[col].value_counts().head(5)
                        for val, count in top_values.items():
                            print(f"      {val}: {count}건")
                    except:
                        print(f"      (분석 불가)")
        
        # 입출고 패턴 분석
        print(f"\n📦 입출고 패턴 분석:")
        
        # Status_Location 분석
        if 'Status_Location' in df.columns:
            print(f"Status_Location 분포:")
            location_counts = df['Status_Location'].value_counts()
            for loc, count in location_counts.head(10).items():
                percentage = (count / len(df)) * 100
                print(f"  {loc}: {count:,}건 ({percentage:.1f}%)")
        
        # 월별 분포 분석
        if 'Status_Location_Date' in df.columns:
            print(f"\n📊 월별 분포 분석:")
            try:
                df['Status_Location_Date'] = pd.to_datetime(df['Status_Location_Date'])
                df['Month'] = df['Status_Location_Date'].dt.to_period('M')
                monthly_counts = df['Month'].value_counts().sort_index()
                print(f"월별 데이터 분포:")
                for month, count in monthly_counts.head(10).items():
                    print(f"  {month}: {count:,}건")
            except Exception as e:
                print(f"  ❌ 월별 분석 실패: {e}")
        
        # 샘플 데이터 출력
        print(f"\n🔍 샘플 데이터 (처음 3건):")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return None

def suggest_fix_strategy(df):
    """수정 전략 제안"""
    print(f"\n🔧 수정 전략 제안:")
    print("=" * 60)
    
    # 1. 창고 매핑 전략
    print("1. 창고 매핑 전략:")
    if 'Status_Location' in df.columns:
        locations = df['Status_Location'].dropna().unique()
        warehouse_mapping = {}
        for loc in locations:
            if any(w in str(loc) for w in ['DSV', 'Storage', 'MOSB', 'Hauler']):
                warehouse_mapping[loc] = 'warehouse'
                print(f"  📦 창고: {loc}")
        
        # 2. 현장 매핑 전략
        print("\n2. 현장 매핑 전략:")
        site_mapping = {}
        for loc in locations:
            if any(s in str(loc) for s in ['AGI', 'DAS', 'MIR', 'SHU']):
                site_mapping[loc] = 'site'
                print(f"  🏗️ 현장: {loc}")
        
        # 3. 날짜 기반 집계 전략
        print("\n3. 날짜 기반 집계 전략:")
        if 'Status_Location_Date' in df.columns:
            print("  - Status_Location_Date 컬럼 사용")
            print("  - 월별 그룹화 후 위치별 집계")
            print("  - 입고: 해당 월에 해당 위치로 이동한 건수")
            print("  - 출고: 해당 월에 해당 위치에서 이동한 건수")
            print("  - 재고: 해당 월 말 기준 해당 위치에 남은 건수")
    
    # 4. 구체적인 수정 코드 제안
    print("\n4. 구체적인 수정 필요 사항:")
    print("  - 실제 Status_Location 값을 기반으로 창고/현장 분류")
    print("  - Status_Location_Date를 기반으로 월별 집계")
    print("  - 빈 데이터가 아닌 실제 집계 결과 생성")

def main():
    """메인 실행 함수"""
    df = analyze_data_structure()
    if df is not None:
        suggest_fix_strategy(df)
    
    print(f"\n🎯 다음 단계:")
    print("1. 실제 데이터 구조 기반으로 집계 로직 수정")
    print("2. 창고_월별_입출고 시트 데이터 채우기")
    print("3. 현장_월별_입고재고 시트 데이터 채우기")
    print("4. Multi-level Header 구조 검증")

if __name__ == "__main__":
    main() 