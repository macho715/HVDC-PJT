# Improved HVDC Time Analysis with Data Quality Filtering
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (15, 8)

print("📅 HVDC 창고 이동 시간별 분석 시스템 (개선된 버전)")
print("=" * 60)
print("🔄 분석 시작:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# 데이터 로드
try:
    df = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx', sheet_name='Case List', engine='openpyxl')
    print(f"✅ 데이터 로드 성공: {len(df)}건")
except Exception as e:
    print(f"❌ 데이터 로드 실패: {e}")
    exit(1)

# 날짜 컬럼 정의
date_columns = ['ETD/ATD', 'ETA/ATA', 'DHL Warehouse', 'DSV Indoor', 
                'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 
                'Hauler Indoor', 'DSV MZP', 'MOSB', 'Shifting', 
                'MIR', 'SHU', 'DAS', 'AGI']

existing_date_columns = [col for col in date_columns if col in df.columns]
print(f"📊 발견된 날짜 컬럼: {len(existing_date_columns)}개")

# 날짜 변환 및 품질 검증
print("\n🔄 날짜 변환 및 품질 검증...")
for col in existing_date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 유효한 날짜 범위 설정 (2020-2025)
valid_start = datetime(2020, 1, 1)
valid_end = datetime(2025, 12, 31)

print(f"✅ 유효 날짜 범위: {valid_start.strftime('%Y-%m-%d')} ~ {valid_end.strftime('%Y-%m-%d')}")

# 시계열 데이터 생성 (유효한 날짜만)
print("📈 시계열 데이터 생성 (유효한 날짜만)...")
movement_data = []
invalid_dates = 0

for idx, row in df.iterrows():
    for col in existing_date_columns:
        if pd.notna(row[col]):
            if valid_start <= row[col] <= valid_end:
                movement_data.append({
                    'Date': row[col],
                    'Location': col,
                    'Case_No': row.get('Case No.', f'Case_{idx}'),
                    'Description': row.get('Description', 'N/A'),
                    'HVDC_CODE': row.get('HVDC CODE', 'N/A'),
                    'CBM': row.get('CBM', 0),
                    'G_W': row.get('G.W(kgs)', 0)
                })
            else:
                invalid_dates += 1

movement_df = pd.DataFrame(movement_data)
print(f"📊 유효한 이동 기록: {len(movement_df)}건")
print(f"❌ 제외된 잘못된 날짜: {invalid_dates}건")

if len(movement_df) == 0:
    print("❌ 유효한 이동 데이터가 없습니다.")
    exit(1)

# 실제 날짜 범위 확인
date_range = movement_df['Date'].agg(['min', 'max'])
print(f"📅 실제 분석 기간: {date_range['min'].strftime('%Y-%m-%d')} ~ {date_range['max'].strftime('%Y-%m-%d')}")

# 월별 집계
movement_counts = movement_df.groupby(['Date', 'Location']).size().reset_index(name='Count')
pivot_data = movement_counts.pivot_table(index='Date', columns='Location', values='Count', fill_value=0)
monthly_data = pivot_data.resample('M').sum()

print(f"📊 월별 데이터 포인트: {len(monthly_data)}개월")

# 실제 활동이 있는 월만 선택
active_months = monthly_data[monthly_data.sum(axis=1) > 0]
print(f"📊 활동이 있는 월: {len(active_months)}개월")

# 1. 종합 시각화
print("\n📊 종합 시각화 생성...")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('HVDC Warehouse Movement Analysis (Valid Dates Only)', fontsize=16, fontweight='bold')

# 1.1 월별 이동량 (상위 6개 위치)
ax1 = axes[0, 0]
top_locations = active_months.sum().sort_values(ascending=False).head(6)
monthly_filtered = active_months[top_locations.index]

monthly_filtered.plot(kind='bar', stacked=True, ax=ax1, colormap='Set3', alpha=0.8)
ax1.set_title('Monthly Movements by Location (Top 6)', fontweight='bold')
ax1.set_xlabel('Month')
ax1.set_ylabel('Number of Items')
ax1.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax1.grid(axis='y', alpha=0.3)

# 1.2 누적 이동량
ax2 = axes[0, 1]
cumulative_data = monthly_filtered.cumsum()
cumulative_data.plot(ax=ax2, linewidth=2, marker='o', markersize=3)
ax2.set_title('Cumulative Movements Over Time', fontweight='bold')
ax2.set_xlabel('Month')
ax2.set_ylabel('Cumulative Items')
ax2.grid(True, alpha=0.3)
ax2.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

# 1.3 위치별 분포
ax3 = axes[1, 0]
location_totals = movement_df['Location'].value_counts().head(8)
colors = plt.cm.Set3(np.linspace(0, 1, len(location_totals)))

wedges, texts, autotexts = ax3.pie(location_totals.values, 
                                   labels=location_totals.index,
                                   autopct='%1.1f%%',
                                   colors=colors,
                                   startangle=90)
ax3.set_title('Movement Distribution by Location', fontweight='bold')

# 1.4 월별 총계 트렌드
ax4 = axes[1, 1]
monthly_totals = active_months.sum(axis=1)
ax4.plot(monthly_totals.index, monthly_totals.values, 
         linewidth=3, marker='o', markersize=6, color='steelblue')
ax4.fill_between(monthly_totals.index, monthly_totals.values, alpha=0.3, color='steelblue')
ax4.set_title('Monthly Total Movement Trend', fontweight='bold')
ax4.set_xlabel('Month')
ax4.set_ylabel('Total Items')
ax4.grid(True, alpha=0.3)

# 최고점/최저점 표시
if len(monthly_totals) > 0:
    max_idx = monthly_totals.idxmax()
    min_idx = monthly_totals.idxmin()
    ax4.annotate(f'Peak: {monthly_totals[max_idx]}', 
                 xy=(max_idx, monthly_totals[max_idx]),
                 xytext=(10, 10), textcoords='offset points',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

plt.tight_layout()
plt.savefig('hvdc_improved_time_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. 정제된 히트맵
print("\n🔥 정제된 히트맵 생성...")
plt.figure(figsize=(14, 8))

# 월별 기간 생성
movement_df['Month_Year'] = movement_df['Date'].dt.to_period('M')
heatmap_data = movement_df.groupby(['Month_Year', 'Location']).size().unstack(fill_value=0)

# 상위 8개 위치만 선택
top_locations_heatmap = heatmap_data.sum().sort_values(ascending=False).head(8)
heatmap_filtered = heatmap_data[top_locations_heatmap.index]
heatmap_filtered = heatmap_filtered.sort_index()

# 활동이 있는 월만 선택
active_heatmap = heatmap_filtered[heatmap_filtered.sum(axis=1) > 0]

sns.heatmap(active_heatmap, 
            cmap='YlOrRd', 
            annot=True, 
            fmt='g',
            cbar_kws={'label': 'Number of Movements'},
            linewidths=0.5)
plt.title('Warehouse Movement Heatmap (Active Periods Only)', fontsize=16, fontweight='bold')
plt.xlabel('Location')
plt.ylabel('Month-Year')
plt.tight_layout()
plt.savefig('hvdc_improved_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()

# 3. 상세 통계 분석
print("\n📊 상세 통계 분석")
print("=" * 50)

# 가장 바쁜 달 (실제 데이터)
if len(movement_df) > 0:
    busiest_months = movement_df.groupby('Month_Year').size().sort_values(ascending=False).head(5)
    print("🚛 상위 5개 최대 이동량 월 (실제 데이터):")
    for i, (month, count) in enumerate(busiest_months.items(), 1):
        print(f"   {i}. {month}: {count:,}건")

# 월별 통계 (활동이 있는 월만)
if len(monthly_totals) > 0:
    monthly_stats = monthly_totals.agg(['mean', 'std', 'min', 'max'])
    print(f"\n📈 월별 이동량 통계 (활동 월 기준):")
    print(f"   평균: {monthly_stats['mean']:.1f}건/월")
    print(f"   표준편차: {monthly_stats['std']:.1f}건")
    print(f"   최소: {monthly_stats['min']}건")
    print(f"   최대: {monthly_stats['max']}건")

# 위치별 통계
print(f"\n🏭 위치별 이동량 (상위 10개):")
location_stats = movement_df['Location'].value_counts().head(10)
for i, (location, count) in enumerate(location_stats.items(), 1):
    percentage = (count / len(movement_df)) * 100
    print(f"   {i:2d}. {location:<15}: {count:>5,}건 ({percentage:5.1f}%)")

# 실제 데이터 기간의 월별 패턴
print(f"\n📅 월별 패턴 분석 (실제 데이터):")
movement_df['Month'] = movement_df['Date'].dt.month
monthly_pattern = movement_df.groupby('Month').size()

if len(monthly_pattern) > 0:
    busiest_month = monthly_pattern.idxmax()
    slowest_month = monthly_pattern.idxmin()
    
    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    print(f"   가장 바쁜 달: {month_names[busiest_month]} ({monthly_pattern[busiest_month]:,}건)")
    print(f"   가장 한가한 달: {month_names[slowest_month]} ({monthly_pattern[slowest_month]:,}건)")

# 요일별 패턴
if len(movement_df) > 100:
    movement_df['Weekday'] = movement_df['Date'].dt.day_name()
    weekday_pattern = movement_df['Weekday'].value_counts()
    print(f"\n📆 요일별 이동량:")
    for weekday, count in weekday_pattern.items():
        percentage = (count / len(movement_df)) * 100
        print(f"   {weekday:<9}: {count:>5,}건 ({percentage:5.1f}%)")

# 물류 데이터 분석
numeric_columns = ['CBM', 'G_W']
for col in numeric_columns:
    if col in movement_df.columns and movement_df[col].notna().sum() > 0:
        valid_data = movement_df[movement_df[col] > 0]
        if len(valid_data) > 0:
            stats = valid_data[col].agg(['mean', 'sum', 'count'])
            if col == 'CBM':
                print(f"\n📦 CBM 분석 (유효 데이터):")
                print(f"   총 CBM: {stats['sum']:,.1f} m³")
                print(f"   평균 CBM: {stats['mean']:.2f} m³/건")
                print(f"   데이터 건수: {stats['count']:,}건")
            else:
                print(f"\n⚖️  중량 분석 (유효 데이터):")
                print(f"   총 중량: {stats['sum']:,.1f} kg")
                print(f"   평균 중량: {stats['mean']:.1f} kg/건")
                print(f"   데이터 건수: {stats['count']:,}건")

# 데이터 품질 리포트
print(f"\n📋 데이터 품질 리포트:")
print(f"   총 원본 기록: {len(df):,}건")
print(f"   유효한 이동 기록: {len(movement_df):,}건")
print(f"   제외된 잘못된 날짜: {invalid_dates:,}건")
print(f"   데이터 품질: {(len(movement_df) / (len(movement_df) + invalid_dates)) * 100:.1f}%")

# 결과 저장
print(f"\n💾 개선된 분석 결과 저장...")
results = {
    'Active_Monthly_Summary': active_months,
    'Location_Summary': location_stats.to_frame('Count'),
    'Busiest_Months': busiest_months.to_frame('Count') if len(movement_df) > 0 else pd.DataFrame(),
    'Quality_Report': pd.DataFrame([{
        'Total_Records': len(df),
        'Valid_Movements': len(movement_df),
        'Invalid_Dates': invalid_dates,
        'Data_Quality_Percent': (len(movement_df) / (len(movement_df) + invalid_dates)) * 100
    }])
}

with pd.ExcelWriter('HVDC_Improved_Time_Analysis.xlsx', engine='openpyxl') as writer:
    for sheet_name, data in results.items():
        data.to_excel(writer, sheet_name=sheet_name)

print(f"✅ 개선된 분석 완료!")
print(f"   - 시각화: hvdc_improved_time_analysis.png, hvdc_improved_heatmap.png")
print(f"   - 데이터: HVDC_Improved_Time_Analysis.xlsx")

print(f"\n🔧 추천 명령어:")
print("/seasonal-trends [계절별 트렌드 분석]")
print("/logistics-efficiency [물류 효율성 분석]")
print("/capacity-forecast [용량 예측 모델링]") 