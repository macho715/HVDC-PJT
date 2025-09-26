#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
화물 이력 관리 통합 Excel 파일 구조 확인
"""

import pandas as pd
import openpyxl
from pathlib import Path

def check_excel_structure(excel_file):
    """Excel 파일 구조 및 시트 정보 확인"""
    print("🔍 화물 이력 관리 통합 Excel 파일 구조 분석")
    print("=" * 60)
    
    try:
        # 1. 시트 목록 확인
        wb = openpyxl.load_workbook(excel_file)
        sheet_names = wb.sheetnames
        print(f"📋 시트 개수: {len(sheet_names)}개")
        
        for i, sheet_name in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet_name}")
        
        # 2. 각 시트별 정보 확인
        for sheet_name in sheet_names:
            print(f"\n📊 [{sheet_name}] 시트 정보:")
            
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                print(f"  ✅ 행 수: {len(df):,}건")
                print(f"  ✅ 컬럼 수: {len(df.columns)}개")
                
                # 주요 컬럼 확인
                if len(df.columns) > 0:
                    print(f"  📌 주요 컬럼 (상위 10개):")
                    for i, col in enumerate(df.columns[:10], 1):
                        print(f"    {i:2d}. {col}")
                    
                    if len(df.columns) > 10:
                        print(f"    ... 외 {len(df.columns)-10}개 컬럼")
                
                # 데이터 샘플 확인
                if len(df) > 0:
                    print(f"  📋 데이터 샘플 (첫 3행):")
                    if 'FLOW_CODE' in df.columns and 'Status_Location' in df.columns:
                        sample_cols = ['FLOW_CODE', 'Status_Location', 'VENDOR', 'Status_Location_Date']
                        available_cols = [col for col in sample_cols if col in df.columns]
                        
                        if available_cols:
                            for idx, row in df[available_cols].head(3).iterrows():
                                print(f"    Row {idx+1}: {dict(row)}")
                    
            except Exception as e:
                print(f"  ❌ 시트 읽기 오류: {str(e)}")
        
        # 3. 화물 이력 관리 핵심 정보 확인
        print(f"\n🎯 화물 이력 관리 핵심 정보:")
        try:
            main_df = pd.read_excel(excel_file, sheet_name=sheet_names[0])
            
            # FLOW CODE 분포
            if 'FLOW_CODE' in main_df.columns:
                flow_dist = main_df['FLOW_CODE'].value_counts().sort_index()
                print(f"  📊 FLOW CODE 분포:")
                for code, count in flow_dist.items():
                    percentage = (count / len(main_df)) * 100
                    print(f"    Code {code}: {count:,}건 ({percentage:.1f}%)")
            
            # Status_Location 분포
            if 'Status_Location' in main_df.columns:
                location_dist = main_df['Status_Location'].value_counts().head(5)
                print(f"  📍 주요 위치 TOP 5:")
                for location, count in location_dist.items():
                    percentage = (count / len(main_df)) * 100
                    print(f"    {location}: {count:,}건 ({percentage:.1f}%)")
            
            # 벤더 분포
            if 'VENDOR' in main_df.columns:
                vendor_dist = main_df['VENDOR'].value_counts()
                print(f"  🏭 벤더 분포:")
                for vendor, count in vendor_dist.items():
                    percentage = (count / len(main_df)) * 100
                    print(f"    {vendor}: {count:,}건 ({percentage:.1f}%)")
            
            # 날짜 정보
            if 'Status_Location_Date' in main_df.columns:
                dates = pd.to_datetime(main_df['Status_Location_Date'], errors='coerce').dropna()
                if len(dates) > 0:
                    print(f"  📅 날짜 정보:")
                    print(f"    최초 도착: {dates.min().strftime('%Y-%m-%d')}")
                    print(f"    최종 도착: {dates.max().strftime('%Y-%m-%d')}")
                    print(f"    총 기간: {(dates.max() - dates.min()).days}일")
            
        except Exception as e:
            print(f"  ❌ 핵심 정보 분석 오류: {str(e)}")
            
    except Exception as e:
        print(f"❌ Excel 파일 분석 오류: {str(e)}")

def main():
    excel_file = Path("output/화물이력관리_통합시스템_20250703_174211.xlsx")
    
    if not excel_file.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {excel_file}")
        return
    
    check_excel_structure(excel_file)
    
    print(f"\n🎉 화물 이력 관리 통합 시스템 구조 분석 완료!")
    print(f"📁 파일 위치: {excel_file.absolute()}")
    print(f"📊 파일 크기: {excel_file.stat().st_size / (1024*1024):.1f} MB")

if __name__ == '__main__':
    main() 