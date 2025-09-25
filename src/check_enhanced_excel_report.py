"""
Enhanced 엑셀 리포트 내용 확인 및 검증 스크립트
"""

import pandas as pd
import os
from datetime import datetime

def check_enhanced_excel_report():
    """Enhanced 엑셀 리포트 내용 확인"""
    
    # 가장 최근 생성된 파일 찾기
    output_dir = "../output"
    excel_files = [f for f in os.listdir(output_dir) if f.startswith("HVDC_Enhanced_Report_") and f.endswith(".xlsx")]
    
    if not excel_files:
        print("❌ Enhanced 엑셀 리포트 파일을 찾을 수 없습니다.")
        return
    
    # 가장 최근 파일 선택
    latest_file = max(excel_files, key=lambda x: os.path.getmtime(os.path.join(output_dir, x)))
    file_path = os.path.join(output_dir, latest_file)
    
    print(f"📊 Enhanced 엑셀 리포트 분석: {latest_file}")
    print(f"📁 파일 크기: {os.path.getsize(file_path):,} bytes")
    
    try:
        # 모든 시트 읽기
        excel_data = pd.read_excel(file_path, sheet_name=None)
        
        print(f"\n📋 총 시트 수: {len(excel_data)}")
        print(f"📋 시트 목록: {list(excel_data.keys())}")
        
        # 시트별 분석
        for sheet_name, sheet_data in excel_data.items():
            print(f"\n=== {sheet_name} ===")
            print(f"📐 크기: {sheet_data.shape[0]}행 × {sheet_data.shape[1]}열")
            
            if sheet_name == "전체_트랜잭션_요약":
                print("📊 전체_트랜잭션_요약 내용:")
                print(sheet_data.head(10).to_string(index=False))
                
            elif sheet_name == "창고_월별_입출고":
                print("📊 창고_월별_입출고 컬럼:")
                print(f"   컬럼 수: {len(sheet_data.columns)}")
                print(f"   컬럼 목록: {list(sheet_data.columns)}")
                print("\n📊 첫 5행:")
                print(sheet_data.head().to_string(index=False))
                
            elif sheet_name == "현장_월별_입고재고":
                print("📊 현장_월별_입고재고 컬럼:")
                print(f"   컬럼 수: {len(sheet_data.columns)}")
                print(f"   컬럼 목록: {list(sheet_data.columns)}")
                print("\n📊 첫 5행:")
                print(sheet_data.head().to_string(index=False))
        
        # 데이터 품질 검증
        print(f"\n🔍 데이터 품질 검증:")
        
        # 시트 1: 전체_트랜잭션_요약 검증
        if "전체_트랜잭션_요약" in excel_data:
            summary_data = excel_data["전체_트랜잭션_요약"]
            print(f"✅ 전체_트랜잭션_요약: {len(summary_data)}행 생성됨")
            
            # 총 트랜잭션 수 확인
            total_row = summary_data[summary_data.iloc[:,0] == '총 트랜잭션']
            if not total_row.empty:
                total_transactions = total_row.iloc[0, 1]
                print(f"📊 총 트랜잭션: {total_transactions}건")
        
        # 시트 2: 창고_월별_입출고 검증
        if "창고_월별_입출고" in excel_data:
            warehouse_data = excel_data["창고_월별_입출고"]
            print(f"✅ 창고_월별_입출고: {len(warehouse_data)}행 × {len(warehouse_data.columns)}열")
            
            # 분석 기간 확인
            months = warehouse_data['월'].tolist()
            if months:
                print(f"📅 분석 기간: {months[0]} ~ {months[-1]}")
                print(f"📅 총 {len(months)}개월 데이터")
        
        # 시트 3: 현장_월별_입고재고 검증
        if "현장_월별_입고재고" in excel_data:
            site_data = excel_data["현장_월별_입고재고"]
            print(f"✅ 현장_월별_입고재고: {len(site_data)}행 × {len(site_data.columns)}열")
            
            # 분석 기간 확인
            months = site_data['월'].tolist()
            if months:
                print(f"📅 분석 기간: {months[0]} ~ {months[-1]}")
                print(f"📅 총 {len(months)}개월 데이터")
        
        print(f"\n🎉 Enhanced 엑셀 리포트 검증 완료!")
        print(f"📄 파일 위치: {file_path}")
        
    except Exception as e:
        print(f"❌ 엑셀 파일 분석 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_enhanced_excel_report() 