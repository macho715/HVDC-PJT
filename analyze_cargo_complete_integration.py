import pandas as pd
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

print('📊 화물이력관리_완전통합_창고현장포함.xlsx 파일 구조 상세 분석')
print('=' * 80)

# 파일 경로 설정
file_path = r'C:\cursor-mcp\HVDC_PJT\MACHO_통합관리_20250702_205301\화물이력관리_완전통합_창고현장포함.xlsx'

# 파일 기본 정보
if os.path.exists(file_path):
    file_size = os.path.getsize(file_path)
    file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
    print(f'📁 파일 기본 정보')
    print(f'   파일명: 화물이력관리_완전통합_창고현장포함.xlsx')
    print(f'   크기: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)')
    print(f'   수정일: {file_modified.strftime("%Y-%m-%d %H:%M:%S")}')
else:
    print('❌ 파일이 존재하지 않습니다.')
    exit()

# Excel 시트 목록 확인
try:
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    print(f'\n📋 시트 구조 ({len(sheet_names)}개 시트)')
    print('-' * 50)
    
    for i, sheet_name in enumerate(sheet_names, 1):
        print(f'{i}. {sheet_name}')
    
    # 각 시트별 상세 분석
    print(f'\n🔍 각 시트별 상세 분석')
    print('=' * 80)
    
    for sheet_name in sheet_names:
        print(f'\n📊 시트: {sheet_name}')
        print('-' * 60)
        
        # 시트 로드
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # 기본 정보
        print(f'   데이터 규모: {len(df):,}건 × {len(df.columns)}개 컬럼')
        
        # 데이터 완성도
        total_cells = len(df) * len(df.columns)
        filled_cells = df.notna().sum().sum()
        completion_rate = filled_cells / total_cells * 100 if total_cells > 0 else 0
        print(f'   완성도: {completion_rate:.1f}% ({filled_cells:,}/{total_cells:,})')
        
        # 주요 컬럼 (상위 10개)
        print(f'   주요 컬럼 (상위 10개):')
        for i, col in enumerate(df.columns[:10], 1):
            col_completion = df[col].notna().sum() / len(df) * 100 if len(df) > 0 else 0
            col_unique = df[col].nunique()
            print(f'     {i:2d}. {col:<30}: {col_completion:>6.1f}% | 고유값 {col_unique:>4}개')
        
        if len(df.columns) > 10:
            print(f'     ... 외 {len(df.columns)-10}개 컬럼 더 있음')
        
        # 시트별 특화 분석
        if '통합' in sheet_name or '메인' in sheet_name:
            print(f'   📈 핵심 통계:')
            
            # Status_Location_Date 관련 컬럼 찾기
            location_cols = [col for col in df.columns if any(keyword in col for keyword in ['DSV', 'MIR', 'SHU', 'DAS', 'AGI', 'MOSB'])]
            if location_cols:
                print(f'     위치 관련 컬럼: {len(location_cols)}개')
                location_counts = {}
                for col in location_cols[:5]:  # 상위 5개만
                    count = df[col].notna().sum()
                    if count > 0:
                        location_counts[col] = count
                
                if location_counts:
                    sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
                    for loc, count in sorted_locations:
                        percentage = count / len(df) * 100
                        print(f'     - {loc}: {count:,}건 ({percentage:.1f}%)')
            
            # Flow Code 분석
            if 'FLOW_CODE' in df.columns:
                flow_counts = df['FLOW_CODE'].value_counts().sort_index()
                print(f'     Flow Code 분포:')
                for code, count in flow_counts.items():
                    percentage = count / len(df) * 100
                    print(f'     - Code {code}: {count:,}건 ({percentage:.1f}%)')
            
            # 벤더 분석
            if 'VENDOR' in df.columns:
                vendor_counts = df['VENDOR'].value_counts()
                print(f'     벤더 분포:')
                for vendor, count in vendor_counts.items():
                    percentage = count / len(df) * 100
                    print(f'     - {vendor}: {count:,}건 ({percentage:.1f}%)')
        
        # 월별 데이터 분석 (월별 시트의 경우)
        if '월별' in sheet_name:
            print(f'   📅 월별 데이터 특성:')
            
            # 날짜 관련 컬럼 찾기
            date_cols = [col for col in df.columns if any(keyword in col for keyword in ['년월', '월', '일시', 'Date', 'ETA', 'ATA'])]
            if date_cols:
                print(f'     날짜 관련 컬럼: {", ".join(date_cols[:3])}{"..." if len(date_cols) > 3 else ""}')
            
            # 수치 데이터 요약
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f'     수치 컬럼: {len(numeric_cols)}개')
                for col in numeric_cols[:3]:  # 상위 3개만
                    if df[col].notna().sum() > 0:
                        mean_val = df[col].mean()
                        sum_val = df[col].sum()
                        print(f'     - {col}: 평균 {mean_val:.1f}, 합계 {sum_val:,.0f}')
        
        print()  # 시트 간 구분선
    
    print(f'\n🎯 종합 요약')
    print('=' * 50)
    
    # 전체 데이터 규모 계산
    total_rows = 0
    total_cols = 0
    total_sheets = len(sheet_names)
    
    for sheet_name in sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        total_rows += len(df)
        total_cols += len(df.columns)
    
    print(f'• 총 시트 수: {total_sheets}개')
    print(f'• 총 데이터 행 수: {total_rows:,}건')
    print(f'• 총 컬럼 수: {total_cols:,}개')
    print(f'• 파일 크기: {file_size/1024/1024:.2f} MB')
    
    print(f'\n💡 활용 권장사항')
    print('-' * 30)
    print('1. 메인 시트를 통한 전체 화물 현황 파악')
    print('2. 월별 시트를 통한 시계열 분석')
    print('3. 위치별 시트를 통한 창고/현장 효율성 분석')
    print('4. Flow Code 기반 물류 경로 최적화')
    print('5. 벤더별 성과 분석 및 관리')

except Exception as e:
    print(f'❌ 파일 분석 중 오류 발생: {str(e)}')

print(f'\n🔧 **추천 명령어:**')
print('/analyze_integration [화물이력관리 완전통합 파일 분석 완료]')
print('/extract_kpi [핵심 KPI 지표 추출 및 대시보드 생성]')
print('/validate_data [데이터 품질 검증 및 무결성 확인]') 