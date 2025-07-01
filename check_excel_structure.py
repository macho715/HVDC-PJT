import pandas as pd
import sys

def check_excel_structure(file_path):
    """Excel 파일의 구조를 확인"""
    try:
        # Excel 파일의 모든 시트 이름 확인
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"📊 Excel 파일 구조 분석: {file_path}")
        print("=" * 80)
        print(f"📋 총 시트 수: {len(sheet_names)}")
        print(f"📄 시트 목록: {', '.join(sheet_names)}")
        print("=" * 80)
        
        # 각 시트의 데이터 확인
        for sheet_name in sheet_names:
            print(f"\n📊 [{sheet_name}] 시트 내용:")
            print("-" * 60)
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"📈 행 수: {len(df)}")
                print(f"📊 열 수: {len(df.columns)}")
                print(f"📋 컬럼: {', '.join(df.columns.tolist())}")
                
                if len(df) > 0:
                    print(f"\n🔍 상위 3행 데이터:")
                    print(df.head(3).to_string(index=False))
                    
                    if len(df) > 3:
                        print(f"\n📊 요약 통계:")
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        if len(numeric_cols) > 0:
                            for col in numeric_cols[:3]:  # 상위 3개 숫자 컬럼만
                                if col in df.columns:
                                    print(f"   {col}: 합계 {df[col].sum():,}, 평균 {df[col].mean():.1f}")
                else:
                    print("   (빈 시트)")
                    
            except Exception as e:
                print(f"   ❌ 시트 읽기 오류: {e}")
        
        print("\n" + "=" * 80)
        print("✅ Excel 파일 구조 분석 완료!")
        
    except Exception as e:
        print(f"❌ Excel 파일 분석 실패: {e}")
        return False
    
    return True

if __name__ == "__main__":
    file_path = "reports/MACHO_v2.8.4_종합물류리포트_20250702_020642.xlsx"
    success = check_excel_structure(file_path)
    
    if success:
        print(f"\n🎯 **Excel 파일 활용 방법:**")
        print(f"1. Excel에서 직접 열기: {file_path}")
        print(f"2. PowerBI에서 데이터 소스로 활용")
        print(f"3. 월별/창고별/재고 분석 대시보드 구성")
        print(f"4. 트렌드 분석 및 예측 모델링")
    else:
        sys.exit(1) 