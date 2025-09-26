import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print('📊 화물이력관리_통합데이터 시트 종합 분석 리포트')
print('=' * 80)

file_path = r'C:\cursor-mcp\HVDC_PJT\output\화물이력관리_통합시스템_20250703_174211.xlsx'
df = pd.read_excel(file_path, sheet_name=0)

print(f'\n🔍 데이터 품질 지표')
print('-' * 40)

total_cells = len(df) * len(df.columns)
filled_cells = df.notna().sum().sum()
overall_completion = filled_cells / total_cells * 100

print(f'전체 데이터 완성도: {overall_completion:.1f}%')
print(f'총 셀 수: {total_cells:,}개')
print(f'채워진 셀 수: {filled_cells:,}개')

print(f'\n📍 Status_Location_Date 핵심 분석')
print('-' * 50)

location_cols = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'MOSB', 'MIR', 'SHU', 'DAS', 'AGI']
location_data = {}

for col in location_cols:
    if col in df.columns:
        count = df[col].notna().sum()
        percentage = count / len(df) * 100
        location_data[col] = {'count': count, 'percentage': percentage}

sorted_locations = sorted(location_data.items(), key=lambda x: x[1]['count'], reverse=True)

print('주요 위치별 화물 분포:')
for location, data in sorted_locations:
    loc_type = '현장' if location in ['MIR', 'SHU', 'DAS', 'AGI'] else '창고'
    print(f'  {location:<15}: {data["count"]:>4,}건 ({data["percentage"]:>5.1f}%) [{loc_type}]')

print(f'\n🔄 Flow Code 상세 분석')
print('-' * 40)

if 'FLOW_CODE' in df.columns:
    flow_counts = df['FLOW_CODE'].value_counts().sort_index()
    
    flow_descriptions = {
        0: 'Pre Arrival (사전 도착)',
        1: 'Direct Route (Port → Site)',
        2: 'Warehouse Route (Port → WH → Site)',
        3: 'Complex Route (Port → WH → MOSB → Site)',
        4: 'Multi-WH Route (Port → WH → WH → MOSB → Site)'
    }
    
    for code, count in flow_counts.items():
        percentage = count / len(df) * 100
        desc = flow_descriptions.get(code, 'Unknown')
        print(f'  Flow Code {code}: {count:>5,}건 ({percentage:>5.1f}%) - {desc}')

print(f'\n🏭 벤더 분석')
print('-' * 30)

if 'VENDOR' in df.columns:
    vendor_counts = df['VENDOR'].value_counts()
    for vendor, count in vendor_counts.items():
        percentage = count / len(df) * 100
        print(f'  {vendor}: {count:>5,}건 ({percentage:>5.1f}%)')

print(f'\n📅 시간 범위 분석')
print('-' * 40)

if 'ETA/ATA' in df.columns:
    eta_data = df['ETA/ATA'].dropna()
    if len(eta_data) > 0:
        min_date = eta_data.min()
        max_date = eta_data.max()
        print(f'ETA/ATA 범위: {min_date.strftime("%Y-%m-%d")} ~ {max_date.strftime("%Y-%m-%d")}')
        
        # 월별 분포
        monthly_counts = df['도착년월'].value_counts().sort_index()
        print(f'\n월별 화물 분포 (상위 5개월):')
        for month, count in monthly_counts.head().items():
            percentage = count / len(df) * 100
            print(f'  {month}: {count:>4,}건 ({percentage:>5.1f}%)')

print(f'\n📊 컬럼 카테고리 요약')
print('-' * 50)

category_summary = {
    '기본정보': 5, 'HVDC코드': 6, '화물정보': 12, '가격정보': 2,
    '운송정보': 6, '위치이력': 15, '상태정보': 7, '처리정보': 5,
    'SQM_Stack': 2, 'SIMENSE추가': 5, 'Flow_Code체계': 5, '시간분석': 5, '기타': 1
}

for category, count in category_summary.items():
    print(f'  {category:<15}: {count:>2}개 컬럼')

print(f'\n총 컬럼 수: {sum(category_summary.values())}개')

print(f'\n🎯 핵심 통계 요약')
print('-' * 50)

# 핵심 통계
print(f'• 총 트랜잭션 수: {len(df):,}건')
print(f'• 전체 컬럼 수: {len(df.columns)}개')
print(f'• 완성도 95% 이상 컬럼: {len([col for col in df.columns if df[col].notna().sum()/len(df) >= 0.95])}개')

# 현장/창고별 통계 수정
site_count = sum([location_data[col]["count"] for col in ["MIR", "SHU", "DAS", "AGI"] if col in location_data])
warehouse_count = sum([location_data[col]["count"] for col in ["DSV Indoor", "DSV Al Markaz", "DSV Outdoor", "MOSB"] if col in location_data])

print(f'• 현장 배치 화물: {site_count:,}건 (중복포함)')
print(f'• 창고 보관 화물: {warehouse_count:,}건 (중복포함)')

print(f'\n💡 데이터 활용 권장사항')
print('-' * 50)
print('1. Status_Location_Date 컬럼을 활용한 실시간 화물 추적')
print('2. Flow Code 기반 물류 경로 최적화')
print('3. 월별 화물 분포를 통한 계절성 분석')
print('4. 위치별 화물 분포를 통한 창고 효율성 분석')
print('5. 95%+ 완성도 컬럼을 활용한 KPI 지표 개발')

print(f'\n📋 상세 구조 분석')
print('-' * 50)

# 주요 컬럼별 상세 분석
key_columns = ['FLOW_CODE', 'Status_Current', 'Status_Location', 'VENDOR', 'Site', 'HVDC CODE 3']

for col in key_columns:
    if col in df.columns:
        completion = df[col].notna().sum() / len(df) * 100
        unique_count = df[col].nunique()
        print(f'{col:<20}: 완성도 {completion:>5.1f}%, 고유값 {unique_count:>3}개')
        
        # 상위 3개 값 표시
        top_values = df[col].value_counts().head(3)
        for val, count in top_values.items():
            val_pct = count / len(df) * 100
            print(f'  └ {str(val):<15}: {count:>4,}건 ({val_pct:>5.1f}%)')
        print()

print(f'\n🔧 **추천 명령어:**')
print('/analyze_data [화물이력관리_통합데이터 테이블 분석 완료]')
print('/visualize_data [위치별 화물 분포 시각화 및 대시보드 생성]')
print('/generate_report [Flow Code 기반 물류 경로 최적화 보고서]') 