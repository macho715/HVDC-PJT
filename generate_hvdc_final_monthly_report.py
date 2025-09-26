import pandas as pd
import os
from datetime import datetime

# 주요 컬럼 정의
MAIN_COLUMNS = [
    # 기본 정보
    'no.', 'Case No.', 'Pkg', 'L(CM)', 'W(CM)', 'H(CM)', 'CBM',
    # 물성 정보
    'N.W(kgs)', 'G.W(kgs)', 'Stack', 'HS Code', 'Currency',
    # 추가 정보
    'SQM', 'Stack_Status', 'Description', 'Site', 'EQ No',
    # 창고 정보
    'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse',
    # 현장 정보
    'AGI', 'DAS', 'MIR', 'SHU',
    # 분석 정보
    'WH_HANDLING', 'FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_PATTERN',
    # 메타 정보
    'VENDOR', 'SOURCE_FILE', 'PROCESSED_AT', 'TRANSACTION_ID'
]

def convert_date_columns(df):
    """날짜 컬럼을 datetime 형식으로 변환"""
    print("📅 날짜 컬럼 변환 중...")
    
    # 창고 및 현장 날짜 컬럼들
    date_columns = [
        'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 
        'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse',
        'AGI', 'DAS', 'MIR', 'SHU'
    ]
    
    for col in date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                print(f"✅ {col}: 변환 완료")
            except Exception as e:
                print(f"⚠️ {col}: 변환 실패 - {e}")
    
    return df

def main():
    print("🚀 HVDC 통합 월별 리포트 생성 시작...")
    
    # 1. 원본 데이터 로드
    input_file = "HVDC_DHL_Warehouse_완전복구_20250704_125724.xlsx"
    if not os.path.exists(input_file):
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
        return
    
    print(f"📊 데이터 로드 중: {input_file}")
    df = pd.read_excel(input_file)
    print(f"✅ 데이터 로드 완료: {len(df)}행 × {len(df.columns)}열")
    
    # 2. 날짜 컬럼 변환
    df = convert_date_columns(df)
    
    # 3. 주요 컬럼만 선택하여 Sheet1 생성
    print("📋 Sheet1: 전체_트랜잭션_데이터 생성 중...")
    available_columns = [col for col in MAIN_COLUMNS if col in df.columns]
    transaction_df = df[available_columns].copy()
    print(f"✅ Sheet1 완료: {len(transaction_df)}행 × {len(transaction_df.columns)}열")
    
    # 4. 창고/현장 월별 집계 시트 생성
    try:
        from generate_warehouse_site_monthly_report_correct import WarehouseSiteMonthlyReportCorrect
        
        reporter = WarehouseSiteMonthlyReportCorrect()
        
        print("📊 창고_월별_입출고 시트 생성 중 (올바른 계산)...")
        warehouse_monthly = reporter.create_warehouse_monthly_sheet(df)
        
        print("📊 현장_월별_입고재고 시트 생성 중 (올바른 계산)...")
        site_monthly = reporter.create_site_monthly_sheet(df)
        
    except Exception as e:
        print(f"❌ 월별 집계 생성 실패: {e}")
        return
    
    # 5. Excel 파일 생성
    output_file = "HVDC_통합_월별_리포트_최종.xlsx"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"HVDC_통합_월별_리포트_최종_{timestamp}.xlsx"
    
    print(f"💾 Excel 파일 생성 중: {output_file}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet1: 전체 트랜잭션 데이터
        transaction_df.to_excel(writer, sheet_name='전체_트랜잭션_데이터', index=False)
        
        # Sheet2: 창고 월별 입출고
        warehouse_monthly.to_excel(writer, sheet_name='창고_월별_입출고', index=False)
        
        # Sheet3: 현장 월별 입고재고
        site_monthly.to_excel(writer, sheet_name='현장_월별_입고재고', index=False)
    
    print(f"✅ 최종 리포트 생성 완료: {output_file}")
    print(f"📊 시트 구성:")
    print(f"   - Sheet1: 전체_트랜잭션_데이터 ({len(transaction_df)}행)")
    print(f"   - Sheet2: 창고_월별_입출고 ({len(warehouse_monthly)}행)")
    print(f"   - Sheet3: 현장_월별_입고재고 ({len(site_monthly)}행)")
    
    return output_file

if __name__ == "__main__":
    main() 