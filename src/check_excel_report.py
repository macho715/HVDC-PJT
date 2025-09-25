"""
P0 Hot-Patch 완료 - 엑셀 리포트 구조 확인 및 요약
"""

import pandas as pd
import os
from datetime import datetime

def check_excel_structure(excel_path: str):
    """엑셀 파일의 구조 확인 및 요약"""
    
    print(f"📊 엑셀 파일 분석: {excel_path}")
    print("=" * 60)
    
    # 엑셀 파일 읽기
    xl_file = pd.ExcelFile(excel_path)
    
    print(f"📋 총 시트 수: {len(xl_file.sheet_names)}")
    print(f"📋 시트 목록: {xl_file.sheet_names}")
    print()
    
    # 각 시트별 분석
    for sheet_name in xl_file.sheet_names:
        print(f"📊 시트: {sheet_name}")
        print("-" * 40)
        
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"   📏 크기: {df.shape[0]} 행 × {df.shape[1]} 열")
            print(f"   📋 컬럼: {list(df.columns)}")
            
            # 처음 3행만 출력
            if not df.empty:
                print("   📄 데이터 샘플:")
                display_df = df.head(3)
                for idx, row in display_df.iterrows():
                    print(f"      Row {idx}: {dict(row)}")
                print()
        except Exception as e:
            print(f"   ❌ 읽기 오류: {str(e)}")
            print()
    
    print("=" * 60)
    print("✅ 엑셀 파일 분석 완료")

def main():
    """메인 실행"""
    
    # 최신 엑셀 파일 찾기
    output_dir = "../output"
    excel_files = [f for f in os.listdir(output_dir) if f.startswith("HVDC_Monthly_Balance_Report_") and f.endswith(".xlsx")]
    
    if not excel_files:
        print("❌ 엑셀 파일을 찾을 수 없습니다.")
        return
    
    # 최신 파일 선택
    latest_file = sorted(excel_files)[-1]
    excel_path = os.path.join(output_dir, latest_file)
    
    check_excel_structure(excel_path)

if __name__ == "__main__":
    main() 