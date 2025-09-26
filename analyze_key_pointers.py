import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print('🎯 메인 시트 핵심 포인터 3개 상세 분석')
print('=' * 80)
print('핵심 포인터: FLOWCODE, SQM, Status_Location_Date')
print('=' * 80)

file_path = r'C:\cursor-mcp\HVDC_PJT\MACHO_통합관리_20250702_205301\화물이력관리_완전통합_창고현장포함.xlsx'
df = pd.read_excel(file_path, sheet_name='화물이력관리_통합')

# 핵심 포인터 3개 컬럼 확인
key_pointers = ['FLOW_CODE', 'SQM', 'Status_Location_Date']
print(f'\n📊 핵심 포인터 기본 정보')
print('-' * 60)

for pointer in key_pointers:
    if pointer in df.columns:
        completion = df[pointer].notna().sum() / len(df) * 100
        unique_count = df[pointer].nunique()
        dtype = str(df[pointer].dtype)
        
        print(f'{pointer:<20}: {completion:>6.1f}% | {dtype:<15} | 고유값 {unique_count:>4}개')
        
        # 샘플 데이터
        sample_data = df[pointer].dropna().head(3).tolist()
        print(f'{"":<20}  샘플: {sample_data}')
        print()

# 1. FLOW_CODE 상세 분석
print(f'\n🔄 FLOW_CODE 상세 분석')
print('=' * 60)

if 'FLOW_CODE' in df.columns:
    flow_counts = df['FLOW_CODE'].value_counts().sort_index()
    
    flow_descriptions = {
        0: 'Pre Arrival (사전 도착)',
        1: 'Direct Route (Port → Site)',
        2: 'Warehouse Route (Port → WH → Site)',
        3: 'Complex Route (Port → WH → MOSB → Site)',
        4: 'Multi-WH Route (Port → WH → WH → MOSB → Site)'
    }
    
    total_items = len(df)
    print(f'총 트랜잭션: {total_items:,}건')
    print(f'Flow Code 분포:')
    
    for code, count in flow_counts.items():
        percentage = count / total_items * 100
        desc = flow_descriptions.get(code, 'Unknown')
        bar = '█' * int(percentage // 2)
        print(f'  Code {code}: {count:>5,}건 ({percentage:>5.1f}%) {bar} {desc}')
    
    # Flow Code별 주요 특성
    print(f'\n📈 Flow Code별 주요 특성:')
    for code in sorted(flow_counts.keys()):
        flow_data = df[df['FLOW_CODE'] == code]
        
        # 벤더 분포
        if 'VENDOR' in df.columns:
            vendor_dist = flow_data['VENDOR'].value_counts()
            vendor_str = ', '.join([f'{v}: {c}건' for v, c in vendor_dist.head(2).items()])
            print(f'  Code {code} - 벤더: {vendor_str}')
        
        # 현장 분포
        if 'Site' in df.columns:
            site_dist = flow_data['Site'].value_counts()
            site_str = ', '.join([f'{s}: {c}건' for s, c in site_dist.head(3).items()])
            print(f'  Code {code} - 현장: {site_str}')

# 2. SQM 상세 분석
print(f'\n📏 SQM 상세 분석')
print('=' * 60)

if 'SQM' in df.columns:
    sqm_data = df['SQM'].dropna()
    
    print(f'SQM 통계:')
    print(f'  총 데이터: {len(sqm_data):,}건')
    print(f'  평균: {sqm_data.mean():.2f}')
    print(f'  중간값: {sqm_data.median():.2f}')
    print(f'  최소값: {sqm_data.min():.2f}')
    print(f'  최대값: {sqm_data.max():.2f}')
    print(f'  총 SQM: {sqm_data.sum():,.2f}')
    
    # SQM 구간별 분포
    print(f'\n📊 SQM 구간별 분포:')
    sqm_ranges = [
        (0, 5, '소형'),
        (5, 20, '중형'),
        (20, 50, '대형'),
        (50, 100, '초대형'),
        (100, float('inf'), '특수')
    ]
    
    for min_val, max_val, category in sqm_ranges:
        if max_val == float('inf'):
            count = len(sqm_data[sqm_data >= min_val])
        else:
            count = len(sqm_data[(sqm_data >= min_val) & (sqm_data < max_val)])
        
        if count > 0:
            percentage = count / len(sqm_data) * 100
            range_str = f'{min_val}-{max_val}' if max_val != float('inf') else f'{min_val}+'
            print(f'  {category} ({range_str}): {count:>4,}건 ({percentage:>5.1f}%)')
    
    # Flow Code별 SQM 분석
    if 'FLOW_CODE' in df.columns:
        print(f'\n🔄 Flow Code별 SQM 분석:')
        for code in sorted(df['FLOW_CODE'].unique()):
            flow_sqm = df[df['FLOW_CODE'] == code]['SQM'].dropna()
            if len(flow_sqm) > 0:
                avg_sqm = flow_sqm.mean()
                total_sqm = flow_sqm.sum()
                print(f'  Code {code}: 평균 {avg_sqm:>6.2f} | 총합 {total_sqm:>8,.2f}')

# 3. Status_Location_Date 상세 분석
print(f'\n📍 Status_Location_Date 상세 분석')
print('=' * 60)

if 'Status_Location_Date' in df.columns:
    date_data = df['Status_Location_Date'].dropna()
    
    print(f'Status_Location_Date 통계:')
    print(f'  총 데이터: {len(date_data):,}건')
    print(f'  완성도: {len(date_data)/len(df)*100:.1f}%')
    
    if len(date_data) > 0:
        min_date = date_data.min()
        max_date = date_data.max()
        print(f'  기간: {min_date.strftime("%Y-%m-%d")} ~ {max_date.strftime("%Y-%m-%d")}')
        
        # 연도별 분포
        years = pd.to_datetime(date_data).dt.year.value_counts().sort_index()
        print(f'\n📅 연도별 분포:')
        for year, count in years.items():
            percentage = count / len(date_data) * 100
            print(f'  {year}: {count:>4,}건 ({percentage:>5.1f}%)')
        
        # 월별 분포
        months = pd.to_datetime(date_data).dt.month.value_counts().sort_index()
        print(f'\n📅 월별 분포:')
        month_names = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
        for month, count in months.items():
            percentage = count / len(date_data) * 100
            month_name = month_names[month-1]
            print(f'  {month_name}: {count:>4,}건 ({percentage:>5.1f}%)')

# 4. 3개 포인터 상호 연관성 분석
print(f'\n🔗 3개 핵심 포인터 상호 연관성 분석')
print('=' * 80)

# Flow Code별 SQM 및 Status_Location_Date 분석
if all(col in df.columns for col in ['FLOW_CODE', 'SQM', 'Status_Location_Date']):
    print(f'Flow Code별 SQM 및 날짜 통계:')
    
    for code in sorted(df['FLOW_CODE'].unique()):
        flow_data = df[df['FLOW_CODE'] == code]
        
        # SQM 통계
        sqm_stats = flow_data['SQM'].describe()
        sqm_mean = sqm_stats['mean'] if not np.isnan(sqm_stats['mean']) else 0
        sqm_count = flow_data['SQM'].notna().sum()
        
        # 날짜 통계
        date_count = flow_data['Status_Location_Date'].notna().sum()
        date_completion = date_count / len(flow_data) * 100
        
        print(f'\n  📊 Flow Code {code}:')
        print(f'     총 트랜잭션: {len(flow_data):,}건')
        print(f'     SQM 평균: {sqm_mean:.2f} ({sqm_count:,}건)')
        print(f'     날짜 완성도: {date_completion:.1f}% ({date_count:,}건)')
        
        # 해당 Flow Code의 주요 위치
        if 'Status_Location' in df.columns:
            locations = flow_data['Status_Location'].value_counts().head(3)
            location_str = ', '.join([f'{loc}: {count}건' for loc, count in locations.items()])
            print(f'     주요 위치: {location_str}')

# 5. 비즈니스 인사이트 및 활용 방안
print(f'\n💡 비즈니스 인사이트 및 활용 방안')
print('=' * 80)

print('🎯 핵심 포인터 활용 전략:')
print()
print('1. FLOW_CODE 활용:')
print('   - 물류 경로 최적화 및 효율성 분석')
print('   - 창고 경유 vs 직송 비용 효율성 비교')
print('   - 벤더별 선호 경로 패턴 분석')
print()
print('2. SQM 활용:')
print('   - 화물 규모별 처리 시간 예측')
print('   - 창고 공간 활용률 최적화')
print('   - 운송 효율성 지표 개발')
print()
print('3. Status_Location_Date 활용:')
print('   - 실시간 화물 추적 시스템')
print('   - 배송 지연 예측 및 알림')
print('   - 월별/계절별 물류 패턴 분석')
print()
print('🔄 통합 활용 방안:')
print('   - Flow Code + SQM → 경로별 화물 용량 최적화')
print('   - Flow Code + Date → 경로별 처리 시간 분석')
print('   - SQM + Date → 화물 규모별 처리 속도 분석')
print('   - 3개 통합 → 종합 KPI 대시보드 구축')

print(f'\n🔧 **추천 명령어:**')
print('/optimize_flowcode [Flow Code 기반 물류 경로 최적화]')
print('/analyze_sqm [SQM 기반 화물 용량 분석 및 예측]')
print('/track_realtime [Status_Location_Date 실시간 추적 시스템]') 