#!/usr/bin/env python3
"""
DataChain 처리 리포트 확인 스크립트
HVDC 프로젝트의 DataChain 통합 결과를 분석합니다.
"""

import pandas as pd
import os
from pathlib import Path

def check_datachain_reports():
    """DataChain 처리 리포트 확인"""
    
    # 리포트 디렉토리
    report_dir = Path("output/datachain_processed")
    
    if not report_dir.exists():
        print("❌ DataChain 리포트 디렉토리가 없습니다.")
        return
    
    # 최신 리포트 파일 찾기
    report_files = list(report_dir.glob("hvdc_processing_report_*.xlsx"))
    data_files = list(report_dir.glob("hvdc_processed_data_*.xlsx"))
    
    if not report_files:
        print("❌ 처리 리포트 파일이 없습니다.")
        return
    
    # 최신 파일 선택 (타임스탬프 기준)
    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
    latest_data = max(data_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📊 DataChain 처리 리포트 분석")
    print(f"리포트 파일: {latest_report.name}")
    print(f"데이터 파일: {latest_data.name}")
    print("-" * 50)
    
    # 리포트 내용 읽기
    try:
        report_df = pd.read_excel(latest_report)
        print("📋 처리 리포트 내용:")
        for col in report_df.columns:
            value = report_df[col].iloc[0]
            print(f"  {col}: {value}")
        
        print("\n" + "-" * 50)
        
        # 처리된 데이터 확인
        data_df = pd.read_excel(latest_data)
        print(f"📈 처리된 데이터 통계:")
        print(f"  총 레코드: {len(data_df):,}건")
        print(f"  총 컬럼: {len(data_df.columns)}개")
        
        # 벤더 분포 확인
        if 'normalized_vendor' in data_df.columns:
            vendor_counts = data_df['normalized_vendor'].value_counts()
            print(f"  벤더 분포:")
            for vendor, count in vendor_counts.items():
                print(f"    {vendor}: {count:,}건")
        
        # 장비 분류 확인
        if 'equipment_class' in data_df.columns:
            equipment_counts = data_df['equipment_class'].value_counts()
            print(f"  장비 분류:")
            for equipment, count in equipment_counts.items():
                print(f"    {equipment}: {count:,}건")
        
        # 이용률 통계
        if 'utilization_rate' in data_df.columns:
            utilization_values = pd.to_numeric(data_df['utilization_rate'], errors='coerce')
            avg_utilization = utilization_values.mean()
            max_utilization = utilization_values.max()
            min_utilization = utilization_values.min()
            print(f"  이용률 통계:")
            print(f"    평균: {avg_utilization:.2f}%")
            print(f"    최대: {max_utilization:.2f}%")
            print(f"    최소: {min_utilization:.2f}%")
        
        print("\n✅ DataChain 통합 처리 완료!")
        
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")

if __name__ == "__main__":
    check_datachain_reports() 