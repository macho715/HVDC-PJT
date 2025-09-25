#!/usr/bin/env python3
"""
HITACHI 데이터 전용 분석 시스템 v1.0
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini

HITACHI(HE) 데이터만 추출하여 상세 분석:
1. HITACHI 데이터 필터링
2. 창고별 입고 분석
3. 월별 피벗 테이블 생성
4. Final_Location 분포 분석
5. HITACHI 전용 Excel 보고서 생성
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class HitachiDataAnalyzer:
    """HITACHI 데이터 전용 분석기"""
    
    def __init__(self):
        """초기화"""
        print("🔧 HITACHI 데이터 전용 분석 시스템 v1.0")
        print("=" * 80)
        
        # 창고 컬럼 정의
        self.warehouse_columns = [
            'DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'AAA  Storage',
            'DHL Warehouse', 'MOSB', 'Hauler Indoor'
        ]
        
        # 데이터 저장
        self.hitachi_data = None
        self.hitachi_monthly_pivot = None
        self.analysis_results = {}
        
        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_hitachi_data(self):
        """HITACHI 데이터만 로드 및 필터링"""
        print("\n📂 HITACHI 데이터 로드 및 필터링 중...")
        
        # 개선된 데이터 파일 찾기
        improved_files = [f for f in os.listdir('.') if f.startswith('HVDC_DataQuality_Improved_') and f.endswith('.xlsx')]
        
        if not improved_files:
            print("❌ 개선된 데이터 파일을 찾을 수 없습니다.")
            return False
        
        # 가장 최근 파일 사용
        latest_file = max(improved_files, key=lambda x: os.path.getmtime(x))
        print(f"📁 로드할 파일: {latest_file}")
        
        try:
            # 전체 데이터 로드
            all_data = pd.read_excel(latest_file, sheet_name='개선된_전체_데이터')
            
            # HITACHI 데이터만 필터링
            self.hitachi_data = all_data[all_data['Data_Source'] == 'HITACHI'].copy()
            
            print(f"✅ HITACHI 데이터 필터링 완료:")
            print(f"   전체 데이터: {len(all_data):,}건")
            print(f"   HITACHI 데이터: {len(self.hitachi_data):,}건")
            print(f"   HITACHI 비율: {len(self.hitachi_data)/len(all_data)*100:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def analyze_hitachi_warehouse_data(self):
        """HITACHI 창고 데이터 분석"""
        print("\n🏢 HITACHI 창고 데이터 분석 중...")
        print("-" * 60)
        
        warehouse_analysis = {}
        total_hitachi_inbound = 0
        
        for warehouse in self.warehouse_columns:
            if warehouse not in self.hitachi_data.columns:
                continue
            
            # 창고별 입고 데이터 분석
            warehouse_entries = self.hitachi_data[warehouse].notna().sum()
            total_hitachi_inbound += warehouse_entries
            
            # 날짜 범위 분석
            if warehouse_entries > 0:
                warehouse_dates = self.hitachi_data[warehouse].dropna()
                date_list = []
                for date_val in warehouse_dates:
                    try:
                        date_list.append(pd.to_datetime(date_val))
                    except:
                        continue
                
                if date_list:
                    min_date = min(date_list)
                    max_date = max(date_list)
                else:
                    min_date = max_date = None
            else:
                min_date = max_date = None
            
            warehouse_analysis[warehouse] = {
                'total_entries': warehouse_entries,
                'min_date': min_date,
                'max_date': max_date,
                'date_range_days': (max_date - min_date).days if min_date and max_date else 0
            }
            
            print(f"📋 {warehouse}:")
            print(f"   입고 건수: {warehouse_entries:,}건")
            if min_date and max_date:
                print(f"   날짜 범위: {min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
                print(f"   기간: {(max_date - min_date).days}일")
        
        print(f"\n📊 HITACHI 전체 요약:")
        print(f"   총 입고 건수: {total_hitachi_inbound:,}건")
        print(f"   총 레코드 수: {len(self.hitachi_data):,}건")
        
        self.analysis_results['warehouse_analysis'] = warehouse_analysis
        self.analysis_results['total_inbound'] = total_hitachi_inbound
        
        return warehouse_analysis
    
    def generate_hitachi_monthly_pivot(self):
        """HITACHI 월별 피벗 테이블 생성"""
        print("\n📊 HITACHI 월별 피벗 테이블 생성 중...")
        print("-" * 60)
        
        # HITACHI 입고 데이터 추출
        hitachi_inbound_records = []
        
        for _, row in self.hitachi_data.iterrows():
            for warehouse in self.warehouse_columns:
                if pd.notna(row[warehouse]):
                    try:
                        warehouse_date = pd.to_datetime(row[warehouse])
                        hitachi_inbound_records.append({
                            'Item_Index': row.name,
                            'Warehouse': warehouse,
                            'Date': warehouse_date,
                            'Month': warehouse_date.to_period('M'),
                            'Year': warehouse_date.year,
                            'Month_Number': warehouse_date.month,
                            'Final_Location': row.get('Final_Location_Improved', warehouse),
                            'Quarter': f"Q{(warehouse_date.month - 1) // 3 + 1}"
                        })
                    except:
                        continue
        
        if not hitachi_inbound_records:
            print("❌ HITACHI 입고 데이터가 없습니다.")
            return None
        
        hitachi_inbound_df = pd.DataFrame(hitachi_inbound_records)
        print(f"📋 HITACHI 입고 데이터 추출 완료: {len(hitachi_inbound_df):,}건")
        
        # Final_Location 기준 월별 피벗 테이블 생성
        try:
            self.hitachi_monthly_pivot = hitachi_inbound_df.pivot_table(
                values='Item_Index',
                index='Month',
                columns='Final_Location',
                aggfunc='count',
                fill_value=0
            )
            
            print(f"✅ HITACHI 월별 피벗 테이블 생성 완료:")
            print(f"   피벗 크기: {self.hitachi_monthly_pivot.shape} (월 × Final_Location)")
            print(f"   월별 기간: {self.hitachi_monthly_pivot.index.min()} ~ {self.hitachi_monthly_pivot.index.max()}")
            print(f"   Final_Location 수: {len(self.hitachi_monthly_pivot.columns)}")
            
            # 월별 총계 계산
            monthly_totals = self.hitachi_monthly_pivot.sum(axis=1)
            print(f"   월별 평균 입고: {monthly_totals.mean():.1f}건")
            
            if len(monthly_totals) > 0:
                print(f"   최대 입고 월: {monthly_totals.idxmax()} ({monthly_totals.max():,}건)")
                print(f"   최소 입고 월: {monthly_totals.idxmin()} ({monthly_totals.min():,}건)")
            
            # 상위 Final_Location 출력
            location_totals = self.hitachi_monthly_pivot.sum(axis=0)
            print(f"\n📊 HITACHI 상위 Final_Location (상위 5개):")
            for location, total in location_totals.sort_values(ascending=False).head(5).items():
                print(f"   {location}: {total:,}건")
            
            # 계절성 분석
            self.analyze_hitachi_seasonality(hitachi_inbound_df)
            
            return self.hitachi_monthly_pivot
            
        except Exception as e:
            print(f"❌ HITACHI 피벗 테이블 생성 실패: {e}")
            return None
    
    def analyze_hitachi_seasonality(self, hitachi_inbound_df):
        """HITACHI 계절성 분석"""
        print(f"\n📈 HITACHI 계절성 분석:")
        
        # 계절별 분석
        seasonal_data = []
        for _, row in hitachi_inbound_df.iterrows():
            month_num = row['Month_Number']
            season = self.get_season(month_num)
            seasonal_data.append({
                'Season': season,
                'Quarter': row['Quarter'],
                'Year': row['Year'],
                'Count': 1
            })
        
        seasonal_df = pd.DataFrame(seasonal_data)
        
        if len(seasonal_df) > 0:
            # 계절별 평균
            seasonal_avg = seasonal_df.groupby('Season')['Count'].sum()
            print(f"   계절별 입고량:")
            for season, total in seasonal_avg.items():
                print(f"     {season}: {total:,}건")
            
            # 분기별 평균
            quarterly_avg = seasonal_df.groupby('Quarter')['Count'].sum()
            print(f"   분기별 입고량:")
            for quarter, total in quarterly_avg.items():
                print(f"     {quarter}: {total:,}건")
            
            # 연도별 분석
            if len(seasonal_df['Year'].unique()) > 1:
                yearly_avg = seasonal_df.groupby('Year')['Count'].sum()
                print(f"   연도별 입고량:")
                for year, total in yearly_avg.items():
                    print(f"     {year}: {total:,}건")
        
        self.analysis_results['seasonality'] = {
            'seasonal_totals': seasonal_avg.to_dict() if len(seasonal_df) > 0 else {},
            'quarterly_totals': quarterly_avg.to_dict() if len(seasonal_df) > 0 else {}
        }
    
    def get_season(self, month):
        """월을 계절로 변환"""
        if month in [12, 1, 2]:
            return "겨울"
        elif month in [3, 4, 5]:
            return "봄"
        elif month in [6, 7, 8]:
            return "여름"
        else:
            return "가을"
    
    def analyze_hitachi_final_location(self):
        """HITACHI Final_Location 분포 분석"""
        print(f"\n🏢 HITACHI Final_Location 분포 분석:")
        print("-" * 60)
        
        if 'Final_Location_Improved' in self.hitachi_data.columns:
            final_location_counts = self.hitachi_data['Final_Location_Improved'].value_counts()
            
            print(f"📊 HITACHI Final_Location 분포 (전체):")
            for location, count in final_location_counts.items():
                percentage = count / len(self.hitachi_data) * 100
                print(f"   {location}: {count:,}건 ({percentage:.1f}%)")
            
            self.analysis_results['final_location_distribution'] = final_location_counts.to_dict()
            
            return final_location_counts
        else:
            print("❌ Final_Location_Improved 컬럼이 없습니다.")
            return None
    
    def generate_hitachi_charts(self):
        """HITACHI 전용 차트 생성"""
        print("\n📊 HITACHI 전용 차트 생성 중...")
        
        if self.hitachi_monthly_pivot is None or self.hitachi_monthly_pivot.empty:
            print("❌ HITACHI 차트 생성을 위한 데이터가 없습니다.")
            return None
        
        try:
            # 한글 폰트 설정
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
            
            # 차트 생성
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('HITACHI 데이터 전용 분석 차트', fontsize=16, fontweight='bold')
            
            # 1. HITACHI 월별 입고 추이
            monthly_totals = self.hitachi_monthly_pivot.sum(axis=1)
            axes[0, 0].plot(monthly_totals.index.astype(str), monthly_totals.values, 
                           marker='o', linewidth=2, color='blue')
            axes[0, 0].set_title('HITACHI 월별 입고 추이', fontweight='bold')
            axes[0, 0].set_xlabel('월')
            axes[0, 0].set_ylabel('입고 건수')
            axes[0, 0].tick_params(axis='x', rotation=45)
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2. HITACHI 상위 Final_Location 분포
            location_totals = self.hitachi_monthly_pivot.sum(axis=0).sort_values(ascending=False)
            top_locations = location_totals.head(8)
            axes[0, 1].bar(range(len(top_locations)), top_locations.values, color='lightblue')
            axes[0, 1].set_title('HITACHI 상위 Final_Location 분포', fontweight='bold')
            axes[0, 1].set_xlabel('Final_Location')
            axes[0, 1].set_ylabel('총 입고 건수')
            axes[0, 1].set_xticks(range(len(top_locations)))
            axes[0, 1].set_xticklabels(top_locations.index, rotation=45)
            
            # 3. HITACHI 창고별 입고 분포
            warehouse_totals = {}
            for warehouse in self.warehouse_columns:
                if warehouse in self.hitachi_data.columns:
                    warehouse_totals[warehouse] = self.hitachi_data[warehouse].notna().sum()
            
            warehouse_names = list(warehouse_totals.keys())
            warehouse_counts = list(warehouse_totals.values())
            
            axes[1, 0].bar(warehouse_names, warehouse_counts, color='orange')
            axes[1, 0].set_title('HITACHI 창고별 입고 분포', fontweight='bold')
            axes[1, 0].set_xlabel('창고')
            axes[1, 0].set_ylabel('입고 건수')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # 4. HITACHI 계절별 분포
            if 'seasonality' in self.analysis_results:
                seasonal_data = self.analysis_results['seasonality']['seasonal_totals']
                if seasonal_data:
                    seasons = list(seasonal_data.keys())
                    counts = list(seasonal_data.values())
                    axes[1, 1].pie(counts, labels=seasons, autopct='%1.1f%%', startangle=90)
                    axes[1, 1].set_title('HITACHI 계절별 분포', fontweight='bold')
            
            plt.tight_layout()
            
            # 차트 저장
            chart_file = f"HITACHI_Analysis_Charts_{self.timestamp}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            print(f"✅ HITACHI 차트 저장 완료: {chart_file}")
            
            plt.close()
            
            return chart_file
            
        except Exception as e:
            print(f"❌ HITACHI 차트 생성 실패: {e}")
            return None
    
    def generate_hitachi_excel_report(self):
        """HITACHI 전용 Excel 보고서 생성"""
        print("\n📋 HITACHI 전용 Excel 보고서 생성 중...")
        
        report_file = f"HITACHI_Analysis_Report_{self.timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
                # 1. HITACHI 전체 데이터
                self.hitachi_data.to_excel(writer, sheet_name='HITACHI_전체_데이터', index=False)
                
                # 2. HITACHI 월별 피벗 테이블
                if self.hitachi_monthly_pivot is not None and not self.hitachi_monthly_pivot.empty:
                    self.hitachi_monthly_pivot.to_excel(writer, sheet_name='HITACHI_월별_피벗')
                
                # 3. 창고별 분석 요약
                warehouse_summary = []
                if 'warehouse_analysis' in self.analysis_results:
                    for warehouse, stats in self.analysis_results['warehouse_analysis'].items():
                        warehouse_summary.append([
                            warehouse,
                            stats['total_entries'],
                            stats['min_date'].strftime('%Y-%m-%d') if stats['min_date'] else '',
                            stats['max_date'].strftime('%Y-%m-%d') if stats['max_date'] else '',
                            stats['date_range_days']
                        ])
                    
                    warehouse_df = pd.DataFrame(warehouse_summary, 
                                              columns=['창고명', '입고_건수', '최초_날짜', '최종_날짜', '기간_일수'])
                    warehouse_df.to_excel(writer, sheet_name='HITACHI_창고별_분석', index=False)
                
                # 4. Final_Location 분포
                if 'final_location_distribution' in self.analysis_results:
                    final_location_data = []
                    for location, count in self.analysis_results['final_location_distribution'].items():
                        percentage = count / len(self.hitachi_data) * 100
                        final_location_data.append([location, count, percentage])
                    
                    final_location_df = pd.DataFrame(final_location_data, 
                                                   columns=['Final_Location', '건수', '비율(%)'])
                    final_location_df.to_excel(writer, sheet_name='HITACHI_Final_Location', index=False)
                
                # 5. 계절성 분석
                if 'seasonality' in self.analysis_results:
                    seasonal_data = []
                    
                    for season, count in self.analysis_results['seasonality']['seasonal_totals'].items():
                        seasonal_data.append(['계절별', season, count])
                    
                    for quarter, count in self.analysis_results['seasonality']['quarterly_totals'].items():
                        seasonal_data.append(['분기별', quarter, count])
                    
                    seasonal_df = pd.DataFrame(seasonal_data, columns=['구분', '기간', '입고량'])
                    seasonal_df.to_excel(writer, sheet_name='HITACHI_계절성_분석', index=False)
                
                # 6. 요약 통계
                summary_stats = [
                    ['총 HITACHI 레코드', len(self.hitachi_data)],
                    ['총 입고 건수', self.analysis_results.get('total_inbound', 0)],
                    ['Final_Location 수', len(self.analysis_results.get('final_location_distribution', {}))],
                    ['분석 기간', f"{self.hitachi_monthly_pivot.index.min()} ~ {self.hitachi_monthly_pivot.index.max()}" if self.hitachi_monthly_pivot is not None else '']
                ]
                
                summary_df = pd.DataFrame(summary_stats, columns=['항목', '값'])
                summary_df.to_excel(writer, sheet_name='HITACHI_요약_통계', index=False)
            
            print(f"✅ HITACHI Excel 보고서 생성 완료: {report_file}")
            print(f"📊 보고서 크기: {os.path.getsize(report_file):,} bytes")
            
            return report_file
            
        except Exception as e:
            print(f"❌ HITACHI 보고서 생성 실패: {e}")
            return None
    
    def run_hitachi_analysis(self):
        """HITACHI 전체 분석 실행"""
        print("🚀 HITACHI 데이터 전용 분석 시작")
        print("=" * 80)
        
        # 1단계: HITACHI 데이터 로드
        if not self.load_hitachi_data():
            return
        
        # 2단계: 창고 데이터 분석
        warehouse_analysis = self.analyze_hitachi_warehouse_data()
        
        # 3단계: 월별 피벗 테이블 생성
        monthly_pivot = self.generate_hitachi_monthly_pivot()
        
        # 4단계: Final_Location 분포 분석
        final_location_analysis = self.analyze_hitachi_final_location()
        
        # 5단계: HITACHI 차트 생성
        chart_file = self.generate_hitachi_charts()
        
        # 6단계: HITACHI Excel 보고서 생성
        report_file = self.generate_hitachi_excel_report()
        
        # 최종 결과 요약
        print("\n" + "=" * 80)
        print("🎉 HITACHI 데이터 분석 완료!")
        print("=" * 80)
        
        print(f"📊 HITACHI 분석 결과 요약:")
        print(f"   총 HITACHI 데이터: {len(self.hitachi_data):,}건")
        print(f"   총 입고 건수: {self.analysis_results.get('total_inbound', 0):,}건")
        
        if monthly_pivot is not None:
            print(f"   월별 피벗 테이블: {monthly_pivot.shape}")
            print(f"   분석 기간: {monthly_pivot.index.min()} ~ {monthly_pivot.index.max()}")
        
        if 'final_location_distribution' in self.analysis_results:
            top_location = max(self.analysis_results['final_location_distribution'].items(), key=lambda x: x[1])
            print(f"   최다 Final_Location: {top_location[0]} ({top_location[1]:,}건)")
        
        if chart_file:
            print(f"📊 HITACHI 차트: {chart_file}")
        
        if report_file:
            print(f"📁 HITACHI 보고서: {report_file}")
        
        print("\n✅ HITACHI 전용 분석이 성공적으로 완료되었습니다!")


def main():
    """메인 실행 함수"""
    analyzer = HitachiDataAnalyzer()
    analyzer.run_hitachi_analysis()


if __name__ == "__main__":
    main() 