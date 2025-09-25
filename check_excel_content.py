#!/usr/bin/env python3
"""
Excel 파일 내용 확인 스크립트
"""

import pandas as pd
import os

def check_excel_content():
    """Excel 파일 내용 확인"""
    excel_file = "HVDC_RealData_Excel_20250708_231416.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ 파일이 존재하지 않습니다: {excel_file}")
        return
    
    print(f"📁 Excel 파일 확인: {excel_file}")
    print(f"📊 파일 크기: {os.path.getsize(excel_file):,} bytes")
    print("=" * 60)
    
    try:
        with pd.ExcelFile(excel_file) as excel:
            print(f"📋 시트 목록: {excel.sheet_names}")
            print("=" * 60)
            
            for sheet_name in excel.sheet_names:
                try:
                    if sheet_name in ['창고_월별_입출고', '현장_월별_입고재고']:
                        # MultiIndex 헤더 시트
                        try:
                            df = pd.read_excel(excel, sheet_name=sheet_name, header=[0, 1])
                            print(f"📊 {sheet_name}: {df.shape} (MultiIndex 헤더)")
                        except:
                            df = pd.read_excel(excel, sheet_name=sheet_name)
                            print(f"📊 {sheet_name}: {df.shape} (일반 헤더)")
                    else:
                        # 일반 시트
                        df = pd.read_excel(excel, sheet_name=sheet_name)
                        print(f"📊 {sheet_name}: {df.shape}")
                        
                        # 첫 몇 행 미리보기
                        if len(df) > 0:
                            print(f"   샘플 데이터:")
                            print(f"   {df.head(2).to_string()}")
                        print("-" * 40)
                        
                except Exception as e:
                    print(f"❌ {sheet_name} 시트 읽기 실패: {e}")
                    
    except Exception as e:
        print(f"❌ Excel 파일 읽기 실패: {e}")

if __name__ == "__main__":
    check_excel_content() 