# Create visualizations of warehouse movements over time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.dates as mdates
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (15, 8)

print("📅 HVDC 창고 이동 시간별 분석 시스템")
print("=" * 60)
print("🔄 분석 시작:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Load the Case List sheet
try:
    df = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx', sheet_name='Case List', engine='openpyxl')
    print(f"✅ 데이터 로드 성공: {len(df)}건")
except Exception as e:
    print(f"❌ 데이터 로드 실패: {e}")
    exit(1)

# Convert date columns to datetime format
date_columns = ['ETD/ATD', 'ETA/ATA', 'DHL Warehouse', 'DSV Indoor', 
                'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 
                'Hauler Indoor', 'DSV MZP', 'MOSB', 'Shifting', 
                'MIR', 'SHU', 'DAS', 'AGI']

# 실제 존재하는 컬럼만 선택
existing_date_columns = [col for col in date_columns if col in df.columns]
print(f"📊 발견된 날짜 컬럼: {len(existing_date_columns)}개")
print(f"   {existing_date_columns}")

print("\n🔄 날짜 변환 중...")
for col in existing_date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Create a long-format dataframe for time series analysis
print("📈 시계열 데이터 생성 중...")
movement_data = []

# For each row in the original dataframe
for idx, row in df.iterrows():
    # For each date column
    for col in existing_date_columns:
        if pd.notna(row[col]):
            movement_data.append({
                'Date': row[col],
                'Location': col,
                'Case_No': row.get('Case No.', f'Case_{idx}'),
                'Description': row.get('Description', 'N/A'),
                'HVDC_CODE': row.get('HVDC CODE', 'N/A'),
                'CBM': row.get('CBM', 0),
                'G_W': row.get('G.W(kgs)', 0)
            })

# Create a dataframe from the movement data
movement_df = pd.DataFrame(movement_data)
print(f"📊 총 이동 기록: {len(movement_df)}건")

if len(movement_df) == 0:
    print("❌ 이동 데이터가 없습니다.")
    exit(1)

# 날짜 범위 확인
date_range = movement_df['Date'].agg(['min', 'max'])
print(f"📅 분석 기간: {date_range['min'].strftime('%Y-%m-%d')} ~ {date_range['max'].strftime('%Y-%m-%d')}")

# Count movements by location and date
movement_counts = movement_df.groupby(['Date', 'Location']).size().reset_index(name='Count')

# Create a pivot table for easier plotting
pivot_data = movement_counts.pivot_table(index='Date', columns='Location', values='Count', fill_value=0)

# Resample to monthly frequency to make the visualization clearer
monthly_data = pivot_data.resample('M').sum()

print(f"📊 월별 데이터 포인트: {len(monthly_data)}개월")

# 1. 월별 창고 이동량 (적층 막대 그래프)
print("\n📊 1. 월별 창고 이동량 시각화...")
plt.figure(figsize=(16, 10))

# 상위 창고만 표시 (가독성을 위해)
top_locations = monthly_data.sum().sort_values(ascending=False).head(8)
monthly_data_filtered = monthly_data[top_locations.index]

ax1 = plt.subplot(2, 2, 1)
monthly_data_filtered.plot(kind='bar', stacked=True, ax=ax1, 
                          colormap='Set3', alpha=0.8)
plt.title('Monthly Warehouse Movements (Top 8 Locations)', fontsize=14, fontweight='bold')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Number of Items', fontsize=12)
plt.xticks(rotation=45)
plt.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.grid(axis='y', alpha=0.3)

# 2. 누적 이동량 (라인 차트)
print("📈 2. 누적 이동량 시각화...")
ax2 = plt.subplot(2, 2, 2)
cumulative_data = monthly_data_filtered.cumsum()
cumulative_data.plot(ax=ax2, linewidth=2, marker='o', markersize=4)
plt.title('Cumulative Warehouse Movements Over Time', fontsize=14, fontweight='bold')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Cumulative Items', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)

# 3. 위치별 총 이동량 (파이 차트)
print("🥧 3. 위치별 총 이동량 분포...")
ax3 = plt.subplot(2, 2, 3)
location_totals = movement_df['Location'].value_counts().head(8)
colors = plt.cm.Set3(np.linspace(0, 1, len(location_totals)))

wedges, texts, autotexts = ax3.pie(location_totals.values, 
                                   labels=location_totals.index,
                                   autopct='%1.1f%%',
                                   colors=colors,
                                   startangle=90)
plt.title('Distribution of Movements by Location', fontsize=14, fontweight='bold')

# 라벨 크기 조정
for text in texts:
    text.set_fontsize(9)
for autotext in autotexts:
    autotext.set_fontsize(8)
    autotext.set_color('white')
    autotext.set_weight('bold')

# 4. 월별 트렌드 (라인 차트)
print("📈 4. 월별 총 이동량 트렌드...")
ax4 = plt.subplot(2, 2, 4)
monthly_totals = monthly_data.sum(axis=1)
ax4.plot(monthly_totals.index, monthly_totals.values, 
         linewidth=3, marker='o', markersize=8, 
         color='steelblue', alpha=0.8)
ax4.fill_between(monthly_totals.index, monthly_totals.values, 
                 alpha=0.3, color='steelblue')
plt.title('Monthly Total Movement Trend', fontsize=14, fontweight='bold')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Total Items', fontsize=12)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

# 최고점과 최저점 표시
max_idx = monthly_totals.idxmax()
min_idx = monthly_totals.idxmin()
ax4.annotate(f'Peak: {monthly_totals[max_idx]}', 
             xy=(max_idx, monthly_totals[max_idx]),
             xytext=(10, 10), textcoords='offset points',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
ax4.annotate(f'Low: {monthly_totals[min_idx]}', 
             xy=(min_idx, monthly_totals[min_idx]),
             xytext=(10, -20), textcoords='offset points',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='blue', alpha=0.7),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

plt.tight_layout()
plt.savefig('hvdc_time_analysis_overview.png', dpi=300, bbox_inches='tight')
plt.show()

# 5. 히트맵 생성
print("\n🔥 5. 월별/위치별 히트맵 생성...")
plt.figure(figsize=(16, 10))

# Create a month-year column
movement_df['Month_Year'] = movement_df['Date'].dt.to_period('M')
heatmap_data = movement_df.groupby(['Month_Year', 'Location']).size().unstack(fill_value=0)

# 상위 위치만 선택
top_locations_for_heatmap = heatmap_data.sum().sort_values(ascending=False).head(10)
heatmap_data_filtered = heatmap_data[top_locations_for_heatmap.index]

# Sort the index to ensure chronological order
heatmap_data_filtered = heatmap_data_filtered.sort_index()

# 히트맵 그리기
sns.heatmap(heatmap_data_filtered, 
            cmap='YlOrRd', 
            annot=True, 
            fmt='g',
            cbar_kws={'label': 'Number of Movements'},
            linewidths=0.5)
plt.title('Heatmap of Warehouse Movements by Location and Month', 
          fontsize=16, fontweight='bold')
plt.xlabel('Location', fontsize=12)
plt.ylabel('Month-Year', fontsize=12)
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('hvdc_movement_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()

# 6. 통계 분석
print("\n📊 시간별 이동 통계 분석")
print("=" * 50)

# Calculate the top 5 busiest months overall
busiest_months = movement_df.groupby('Month_Year').size().sort_values(ascending=False).head(5)
print("🚛 상위 5개 최대 이동량 월:")
for i, (month, count) in enumerate(busiest_months.items(), 1):
    print(f"   {i}. {month}: {count:,}건")

# 월별 평균 및 표준편차
monthly_stats = monthly_totals.agg(['mean', 'std', 'min', 'max'])
print(f"\n📈 월별 이동량 통계:")
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

# 월별 패턴 분석
print(f"\n📅 월별 패턴 분석:")
movement_df['Month'] = movement_df['Date'].dt.month
monthly_pattern = movement_df.groupby('Month').size()
busiest_month = monthly_pattern.idxmax()
slowest_month = monthly_pattern.idxmin()

month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
print(f"   가장 바쁜 달: {month_names[busiest_month]} ({monthly_pattern[busiest_month]:,}건)")
print(f"   가장 한가한 달: {month_names[slowest_month]} ({monthly_pattern[slowest_month]:,}건)")

# 요일별 패턴 (만약 충분한 데이터가 있다면)
if len(movement_df) > 100:
    movement_df['Weekday'] = movement_df['Date'].dt.day_name()
    weekday_pattern = movement_df['Weekday'].value_counts()
    print(f"\n📆 요일별 이동량:")
    for weekday, count in weekday_pattern.items():
        percentage = (count / len(movement_df)) * 100
        print(f"   {weekday:<9}: {count:>5,}건 ({percentage:5.1f}%)")

# CBM 및 무게 분석 (데이터가 있는 경우)
if 'CBM' in movement_df.columns and movement_df['CBM'].notna().sum() > 0:
    print(f"\n📦 CBM 분석:")
    cbm_stats = movement_df['CBM'].agg(['mean', 'sum', 'count'])
    print(f"   총 CBM: {cbm_stats['sum']:,.1f} m³")
    print(f"   평균 CBM: {cbm_stats['mean']:.2f} m³/건")

if 'G_W' in movement_df.columns and movement_df['G_W'].notna().sum() > 0:
    print(f"\n⚖️  중량 분석:")
    weight_stats = movement_df['G_W'].agg(['mean', 'sum', 'count'])
    print(f"   총 중량: {weight_stats['sum']:,.1f} kg")
    print(f"   평균 중량: {weight_stats['mean']:.1f} kg/건")

# 데이터 저장
print(f"\n💾 분석 결과 저장...")
analysis_results = {
    'Monthly_Summary': monthly_data,
    'Location_Summary': location_stats.to_frame('Count'),
    'Busiest_Months': busiest_months.to_frame('Count'),
    'Monthly_Statistics': pd.DataFrame([monthly_stats], index=['Monthly_Stats'])
}

with pd.ExcelWriter('HVDC_Time_Analysis_Results.xlsx', engine='openpyxl') as writer:
    for sheet_name, data in analysis_results.items():
        data.to_excel(writer, sheet_name=sheet_name)

print(f"✅ 분석 완료!")
print(f"   - 이미지: hvdc_time_analysis_overview.png, hvdc_movement_heatmap.png")
print(f"   - 데이터: HVDC_Time_Analysis_Results.xlsx")

print(f"\n🔧 추천 명령어:")
print("/seasonal-analysis [계절별 패턴 분석]")
print("/peak-optimization [피크 시즌 최적화]")
print("/capacity-planning [용량 계획 수립]") 