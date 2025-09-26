import pandas as pd
import numpy as np

print("📊 HVDC 시간 분석 결과 확인")
print("=" * 50)

# Excel 파일 읽기
try:
    xl = pd.ExcelFile('HVDC_Time_Analysis_Results.xlsx')
    print(f"📋 시트 목록: {xl.sheet_names}")
    
    # 각 시트 확인
    for sheet_name in xl.sheet_names:
        print(f"\n🔍 {sheet_name} 시트:")
        df = pd.read_excel(xl, sheet_name=sheet_name)
        print(f"   크기: {df.shape}")
        print(f"   컬럼: {list(df.columns)[:5]}")  # 첫 5개 컬럼만
        
        if len(df) > 0:
            print(f"   샘플 데이터:")
            print(df.head(3).to_string(index=False))
            
except Exception as e:
    print(f"❌ 파일 읽기 오류: {e}")

# 시각화 파일 크기 확인
import os
image_files = ['hvdc_time_analysis_overview.png', 'hvdc_movement_heatmap.png']
for file in image_files:
    if os.path.exists(file):
        size = os.path.getsize(file) / 1024  # KB
        print(f"📊 {file}: {size:.1f} KB") 