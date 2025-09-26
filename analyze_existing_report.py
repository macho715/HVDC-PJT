#!/usr/bin/env python3
"""
HVDC 입고로직 종합리포트 분석 스크립트
기존 파일의 구조와 내용을 상세히 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_existing_report():
    """기존 HVDC 입고로직 종합리포트 분석"""
    
    report_file = "HVDC_입고로직_종합리포트_20250709_203855.xlsx"
    
    print("=" * 100)
    print("🔍 HVDC 입고로직 종합리포트 분석")
    print("=" * 100)
    
    # 파일 존재 확인
    if not os.path.exists(report_file):
        print(f"❌ 파일을 찾을 수 없습니다: {report_file}")
        return
    
    # 파일 기본 정보
    file_size = os.path.getsize(report_file)
    modification_time = os.path.getmtime(report_file)
    
    print(f"\n📋 파일 기본 정보:")
    print(f"   파일명: {report_file}")
    print(f"   크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"   수정 시간: {datetime.fromtimestamp(modification_time)}")
    
    # Excel 파일 시트 목록 확인
    try:
        with pd.ExcelFile(report_file) as xls:
            sheet_names = xls.sheet_names
            print(f"\n📊 시트 목록 ({len(sheet_names)}개):")
            for i, sheet in enumerate(sheet_names, 1):
                print(f"   {i}. {sheet}")
    except Exception as e:
        print(f"❌ 시트 목록 읽기 실패: {str(e)}")
        return
    
    # 각 시트별 상세 분석
    print(f"\n" + "=" * 80)
    print("📊 시트별 상세 분석")
    print("=" * 80)
    
    for sheet_name in sheet_names:
        try:
            print(f"\n🔍 [{sheet_name}] 시트 분석:")
            
            # 시트 데이터 읽기
            df = pd.read_excel(report_file, sheet_name=sheet_name)
            
            print(f"   데이터 형태: {df.shape[0]:,}행 × {df.shape[1]}열")
            
            # 컬럼 정보
            print(f"   컬럼 목록:")
            for i, col in enumerate(df.columns, 1):
                col_type = str(df[col].dtype)
                non_null_count = df[col].notna().sum()
                print(f"      {i:2d}. {col} ({col_type}, {non_null_count:,}개 값)")
            
            # 데이터 샘플 (첫 3행)
            if len(df) > 0:
                print(f"   데이터 샘플 (첫 3행):")
                for idx in range(min(3, len(df))):
                    print(f"      행 {idx+1}: {df.iloc[idx].to_dict()}")
            
            # 숫자 컬럼 통계
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                print(f"   숫자 컬럼 통계:")
                for col in numeric_cols:
                    if df[col].notna().sum() > 0:
                        stats = df[col].describe()
                        print(f"      {col}: 평균={stats['mean']:.1f}, 최대={stats['max']:.1f}, 최소={stats['min']:.1f}")
            
            # 텍스트 컬럼 분포
            text_cols = df.select_dtypes(include=['object']).columns
            if len(text_cols) > 0:
                print(f"   텍스트 컬럼 분포:")
                for col in text_cols:
                    if df[col].notna().sum() > 0:
                        unique_count = df[col].nunique()
                        top_values = df[col].value_counts().head(3)
                        print(f"      {col}: {unique_count}개 고유값, 상위: {dict(top_values)}")
            
        except Exception as e:
            print(f"   ❌ 시트 분석 실패: {str(e)}")
            continue
    
    # Flow Code 분석 (만약 해당 시트가 있다면)
    if 'Flow_Code_분석' in sheet_names:
        print(f"\n" + "=" * 80)
        print("🔍 Flow Code 분석 시트 상세 분석")
        print("=" * 80)
        
        try:
            flow_df = pd.read_excel(report_file, sheet_name='Flow_Code_분석')
            
            print(f"   Flow Code 분포:")
            if 'Count' in flow_df.columns and 'FLOW_CODE' in flow_df.columns:
                total_count = flow_df['Count'].sum()
                for _, row in flow_df.iterrows():
                    flow_code = row['FLOW_CODE']
                    count = row['Count']
                    percentage = (count / total_count) * 100
                    description = row.get('FLOW_DESCRIPTION', 'Unknown')
                    print(f"      Code {flow_code}: {count:,}건 ({percentage:.1f}%) - {description}")
            
        except Exception as e:
            print(f"   ❌ Flow Code 분석 실패: {str(e)}")
    
    # 전체 트랜잭션 요약 분석
    if '전체_트랜잭션_요약' in sheet_names:
        print(f"\n" + "=" * 80)
        print("🔍 전체 트랜잭션 요약 시트 상세 분석")
        print("=" * 80)
        
        try:
            summary_df = pd.read_excel(report_file, sheet_name='전체_트랜잭션_요약')
            
            print(f"   요약 정보:")
            for _, row in summary_df.iterrows():
                category = row.get('Category', 'Unknown')
                item = row.get('Item', 'Unknown')
                value = row.get('Value', 'Unknown')
                percentage = row.get('Percentage', 'N/A')
                print(f"      [{category}] {item}: {value} ({percentage})")
            
        except Exception as e:
            print(f"   ❌ 트랜잭션 요약 분석 실패: {str(e)}")
    
    # 종합 평가
    print(f"\n" + "=" * 80)
    print("📋 종합 평가")
    print("=" * 80)
    
    print(f"   ✅ 파일 상태: 정상 ({file_size/1024:.1f} KB)")
    print(f"   ✅ 시트 구성: {len(sheet_names)}개 시트")
    print(f"   ✅ 데이터 품질: 분석 완료")
    
    # 개선 권장사항
    print(f"\n📈 개선 권장사항:")
    print(f"   1. v3.4 Flow Code 수정사항 적용")
    print(f"   2. Pre Arrival 정확도 100% 반영")
    print(f"   3. 직송 물량 652건 추가")
    print(f"   4. Off-by-One 버그 수정 적용")
    
    print(f"\n🔧 다음 단계:")
    print(f"   - 기존 구조 유지하면서 데이터 업데이트")
    print(f"   - v3.4-corrected 로직 적용")
    print(f"   - 검증 결과 반영")

if __name__ == "__main__":
    analyze_existing_report() 