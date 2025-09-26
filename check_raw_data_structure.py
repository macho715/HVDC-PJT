#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raw Data Structure Checker
SIMENSE & HITACHI 파일의 av1 컬럼(Status_Location_Date) 확인
"""

import pandas as pd
from pathlib import Path
import traceback

def check_file_structure(file_path, file_name):
    """파일 구조 확인"""
    try:
        print(f"\n{'='*60}")
        print(f"📊 {file_name} 파일 구조 분석")
        print(f"{'='*60}")
        
        # 파일 읽기
        df = pd.read_excel(file_path)
        
        print(f"📋 기본 정보:")
        print(f"  - 행 수: {len(df):,}")
        print(f"  - 컬럼 수: {len(df.columns)}")
        print(f"  - 파일 크기: {file_path.stat().st_size / (1024*1024):.2f} MB")
        
        print(f"\n📝 모든 컬럼 목록:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # av1 컬럼 확인
        av1_exists = 'av1' in df.columns
        print(f"\n🔍 av1 컬럼 존재 여부: {'✅ 있음' if av1_exists else '❌ 없음'}")
        
        if av1_exists:
            print(f"\n📊 av1 컬럼 분석:")
            av1_data = df['av1']
            print(f"  - 총 데이터: {len(av1_data)}")
            print(f"  - 빈 값: {av1_data.isna().sum()}")
            print(f"  - 유니크 값: {av1_data.nunique()}")
            
            print(f"\n📋 av1 샘플 데이터 (첫 10개):")
            for i, val in enumerate(av1_data.head(10)):
                print(f"  {i+1:2d}. {val}")
        else:
            # 날짜나 위치 관련 컬럼 찾기
            date_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                        for keyword in ['date', 'time', 'arrival', 'status', 'location'])]
            
            if date_cols:
                print(f"\n🔍 날짜/위치 관련 컬럼들:")
                for col in date_cols:
                    print(f"  - {col}")
                    if len(df[col].dropna()) > 0:
                        sample_val = df[col].dropna().iloc[0]
                        print(f"    샘플: {sample_val}")
        
        # 샘플 데이터 출력
        print(f"\n📋 처음 3행 데이터:")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        traceback.print_exc()
        return None

def main():
    """메인 실행 함수"""
    print("🔍 HVDC Raw Data Structure Checker")
    print("SIMENSE & HITACHI 파일의 av1 컬럼 분석")
    
    data_dir = Path("hvdc_macho_gpt/WAREHOUSE/data")
    
    # 파일 목록
    files_to_check = [
        ("HVDC WAREHOUSE_SIMENSE(SIM).xlsx", "SIMENSE"),
        ("HVDC WAREHOUSE_HITACHI(HE).xlsx", "HITACHI")
    ]
    
    results = {}
    
    for filename, vendor in files_to_check:
        file_path = data_dir / filename
        
        if file_path.exists():
            df = check_file_structure(file_path, vendor)
            results[vendor] = df
        else:
            print(f"\n❌ {vendor} 파일을 찾을 수 없습니다: {file_path}")
    
    # 비교 분석
    if len(results) >= 2:
        print(f"\n{'='*60}")
        print("🔄 SIMENSE vs HITACHI 비교 분석")
        print(f"{'='*60}")
        
        simense_df = results.get('SIMENSE')
        hitachi_df = results.get('HITACHI')
        
        if simense_df is not None and hitachi_df is not None:
            print(f"📊 기본 비교:")
            print(f"  SIMENSE: {len(simense_df):,}행, {len(simense_df.columns)}컬럼")
            print(f"  HITACHI: {len(hitachi_df):,}행, {len(hitachi_df.columns)}컬럼")
            
            # 공통 컬럼 확인
            common_cols = set(simense_df.columns) & set(hitachi_df.columns)
            print(f"\n🔗 공통 컬럼 ({len(common_cols)}개):")
            for col in sorted(common_cols):
                print(f"  - {col}")
            
            # av1 컬럼 존재 여부
            simense_has_av1 = 'av1' in simense_df.columns
            hitachi_has_av1 = 'av1' in hitachi_df.columns
            
            print(f"\n🎯 av1 컬럼 현황:")
            print(f"  SIMENSE: {'✅' if simense_has_av1 else '❌'}")
            print(f"  HITACHI: {'✅' if hitachi_has_av1 else '❌'}")
            
            if simense_has_av1 or hitachi_has_av1:
                print("🔧 **추천 명령어:**")
                print("/analyze_status_location comprehensive [Status Location Date 종합 분석]")
                print("/validate-data av1-column [av1 컬럼 데이터 무결성 검증]")
                print("/generate_insights arrival-timeline [도착 타임라인 인사이트]")
            else:
                print("\n⚠️  두 파일 모두 av1 컬럼이 없습니다.")
                print("💡 다음을 확인해주세요:")
                print("  1. 다른 시트에 av1 컬럼이 있는지")
                print("  2. Status_Location_Date 컬럼이 다른 이름으로 있는지")
                print("  3. 파일이 최신 버전인지")

if __name__ == '__main__':
    main() 