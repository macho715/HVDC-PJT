#!/usr/bin/env python3
"""
HITACHI 월별 창고 입고/출고 및 현장 입고/재고 종합 리포트 v1.0
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class HitachiMonthlyWarehouseReport:
    """HITACHI 월별 창고 및 현장 리포트 생성"""
    
    def __init__(self):
        print("🚀 HITACHI 월별 창고 입고/출고 및 현장 입고/재고 종합 리포트 v1.0")
        print("📊 Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini")
        print("=" * 80)
        
        # 창고 컬럼 정의
        self.warehouse_columns = [
            'DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'AAA  Storage',
            'DHL Warehouse', 'MOSB', 'Hauler Indoor'
        ]
        
        # 현장 컬럼 정의 (출고 기준)
        self.site_columns = [
            'Final_Location', 'Status_Location'
        ]
        
        self.hitachi_data = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_hitachi_data(self):
        """HITACHI 데이터 로드"""
        print("\n📂 HITACHI 데이터 로드 중...")
        
        improved_files = [f for f in os.listdir('.') 
                          if f.startswith('HVDC_DataQuality_Improved_') and f.endswith('.xlsx')]
        
        if not improved_files:
            print("❌ 개선된 데이터 파일을 찾을 수 없습니다.")
            return False
        
        latest_file = max(improved_files, key=lambda x: os.path.getmtime(x))
        print(f"📁 로드할 파일: {latest_file}")
        
        try:
            all_data = pd.read_excel(latest_file, sheet_name='개선된_전체_데이터')
            self.hitachi_data = all_data[all_data['Data_Source'] == 'HITACHI'].copy()
            
            # Final_Location 계산 (우선순위 기준)
            self.hitachi_data = self.calculate_final_location(self.hitachi_data)
            
            print(f"✅ HITACHI 데이터 로드 완료: {len(self.hitachi_data):,}건")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def calculate_final_location(self, df):
        """Final_Location 계산"""
        df = df.copy()
        
        # 우선순위 로직 적용
        conditions = [
            df['DSV Al Markaz'].notna() & (df['DSV Al Markaz'] != ''),
            df['DSV Indoor'].notna() & (df['DSV Indoor'] != ''),
            df['DSV Outdoor'].notna() & (df['DSV Outdoor'] != '')
        ]
        
        choices = ['DSV Al Markaz', 'DSV Indoor', 'DSV Outdoor']
        
        df['Final_Location'] = np.select(conditions, choices, default=df['Status_Location'])
        
        return df
    
    def analyze_warehouse_inbound_outbound(self):
        """창고별 월별 입고/출고 분석"""
        print("\n📊 창고별 월별 입고/출고 분석 중...")
        
        # 입고 데이터 분석
        inbound_records = []
        outbound_records = []
        
        for _, row in self.hitachi_data.iterrows():
            # 입고: 창고 컬럼에 날짜가 있으면 입고
            for warehouse in self.warehouse_columns:
                if pd.notna(row[warehouse]):
                    try:
                        date = pd.to_datetime(row[warehouse])
                        inbound_records.append({
                            'Month': date.to_period('M'),
                            'Warehouse': warehouse,
                            'Type': 'Inbound',
                            'Item': row.name,
                            'Date': date
                        })
                    except:
                        continue
            
            # 출고: Final_Location이 창고면 출고로 간주
            final_loc = row.get('Final_Location', '')
            if final_loc in self.warehouse_columns:
                # 가장 최근 창고 날짜를 출고 날짜로 사용
                latest_date = None
                for warehouse in self.warehouse_columns:
                    if pd.notna(row[warehouse]):
                        try:
                            date = pd.to_datetime(row[warehouse])
                            if latest_date is None or date > latest_date:
                                latest_date = date
                        except:
                            continue
                
                if latest_date:
                    outbound_records.append({
                        'Month': latest_date.to_period('M'),
                        'Warehouse': final_loc,
                        'Type': 'Outbound',
                        'Item': row.name,
                        'Date': latest_date
                    })
        
        # 데이터프레임 생성
        if inbound_records:
            inbound_df = pd.DataFrame(inbound_records)
            inbound_pivot = inbound_df.pivot_table(
                values='Item', index='Month', columns='Warehouse', 
                aggfunc='count', fill_value=0
            )
        else:
            inbound_pivot = pd.DataFrame()
        
        if outbound_records:
            outbound_df = pd.DataFrame(outbound_records)
            outbound_pivot = outbound_df.pivot_table(
                values='Item', index='Month', columns='Warehouse', 
                aggfunc='count', fill_value=0
            )
        else:
            outbound_pivot = pd.DataFrame()
        
        return inbound_pivot, outbound_pivot
    
    def analyze_site_inbound_inventory(self):
        """현장별 월별 입고/재고 분석"""
        print("\n📊 현장별 월별 입고/재고 분석 중...")
        
        # 현장 입고 데이터 생성
        site_records = []
        
        for _, row in self.hitachi_data.iterrows():
            final_loc = row.get('Final_Location', '')
            
            # 현장별 입고 날짜 계산
            if final_loc:
                # Final_Location의 마지막 날짜를 현장 입고일로 사용
                latest_date = None
                
                if final_loc in self.warehouse_columns:
                    # 창고인 경우 해당 창고 날짜
                    if pd.notna(row[final_loc]):
                        try:
                            latest_date = pd.to_datetime(row[final_loc])
                        except:
                            pass
                
                if latest_date:
                    site_records.append({
                        'Month': latest_date.to_period('M'),
                        'Site': final_loc,
                        'Type': 'Site_Inbound',
                        'Item': row.name,
                        'Date': latest_date
                    })
        
        # 현장별 입고 피벗 테이블
        if site_records:
            site_df = pd.DataFrame(site_records)
            site_inbound_pivot = site_df.pivot_table(
                values='Item', index='Month', columns='Site', 
                aggfunc='count', fill_value=0
            )
            
            # 재고 계산 (누적)
            site_inventory_pivot = site_inbound_pivot.cumsum()
        else:
            site_inbound_pivot = pd.DataFrame()
            site_inventory_pivot = pd.DataFrame()
        
        return site_inbound_pivot, site_inventory_pivot
    
    def generate_summary_statistics(self, inbound_pivot, outbound_pivot, site_inbound_pivot, site_inventory_pivot):
        """요약 통계 생성"""
        print("\n📊 요약 통계 생성 중...")
        
        summary_stats = {}
        
        # 창고별 총 입고/출고
        if not inbound_pivot.empty:
            summary_stats['warehouse_total_inbound'] = inbound_pivot.sum()
        if not outbound_pivot.empty:
            summary_stats['warehouse_total_outbound'] = outbound_pivot.sum()
        
        # 현장별 총 입고/재고
        if not site_inbound_pivot.empty:
            summary_stats['site_total_inbound'] = site_inbound_pivot.sum()
        if not site_inventory_pivot.empty:
            summary_stats['site_current_inventory'] = site_inventory_pivot.iloc[-1] if len(site_inventory_pivot) > 0 else pd.Series()
        
        # 월별 총계
        if not inbound_pivot.empty:
            summary_stats['monthly_total_inbound'] = inbound_pivot.sum(axis=1)
        if not outbound_pivot.empty:
            summary_stats['monthly_total_outbound'] = outbound_pivot.sum(axis=1)
        
        return summary_stats
    
    def create_visualizations(self, inbound_pivot, outbound_pivot, site_inbound_pivot):
        """시각화 생성"""
        print("\n📊 시각화 생성 중...")
        
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('HITACHI 월별 창고 및 현장 물류 현황', fontsize=16, fontweight='bold')
        
        # 1. 창고별 월별 입고
        if not inbound_pivot.empty:
            inbound_pivot.plot(kind='bar', ax=axes[0, 0], stacked=True)
            axes[0, 0].set_title('창고별 월별 입고 현황')
            axes[0, 0].set_xlabel('월')
            axes[0, 0].set_ylabel('입고 건수')
            axes[0, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 2. 창고별 월별 출고
        if not outbound_pivot.empty:
            outbound_pivot.plot(kind='bar', ax=axes[0, 1], stacked=True)
            axes[0, 1].set_title('창고별 월별 출고 현황')
            axes[0, 1].set_xlabel('월')
            axes[0, 1].set_ylabel('출고 건수')
            axes[0, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 3. 현장별 월별 입고
        if not site_inbound_pivot.empty:
            # 상위 10개 현장만 표시
            top_sites = site_inbound_pivot.sum().nlargest(10)
            site_inbound_pivot[top_sites.index].plot(kind='bar', ax=axes[1, 0], stacked=True)
            axes[1, 0].set_title('현장별 월별 입고 현황 (Top 10)')
            axes[1, 0].set_xlabel('월')
            axes[1, 0].set_ylabel('입고 건수')
            axes[1, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 4. 월별 총 물류량 추이
        if not inbound_pivot.empty and not outbound_pivot.empty:
            monthly_inbound = inbound_pivot.sum(axis=1)
            monthly_outbound = outbound_pivot.sum(axis=1)
            
            axes[1, 1].plot(monthly_inbound.index.astype(str), monthly_inbound.values, 
                           marker='o', label='입고', linewidth=2)
            axes[1, 1].plot(monthly_outbound.index.astype(str), monthly_outbound.values, 
                           marker='s', label='출고', linewidth=2)
            axes[1, 1].set_title('월별 총 물류량 추이')
            axes[1, 1].set_xlabel('월')
            axes[1, 1].set_ylabel('물류량')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 차트 저장
        chart_file = f"HITACHI_Monthly_Warehouse_Charts_{self.timestamp}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 시각화 생성 완료: {chart_file}")
        return chart_file
    
    def generate_excel_report(self, inbound_pivot, outbound_pivot, site_inbound_pivot, site_inventory_pivot, summary_stats):
        """Excel 리포트 생성"""
        print("\n📋 Excel 리포트 생성 중...")
        
        report_file = f"HITACHI_Monthly_Warehouse_Report_{self.timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
                
                # 1. 창고별 월별 입고
                if not inbound_pivot.empty:
                    inbound_pivot.to_excel(writer, sheet_name='창고_월별_입고', index=True)
                
                # 2. 창고별 월별 출고
                if not outbound_pivot.empty:
                    outbound_pivot.to_excel(writer, sheet_name='창고_월별_출고', index=True)
                
                # 3. 현장별 월별 입고
                if not site_inbound_pivot.empty:
                    site_inbound_pivot.to_excel(writer, sheet_name='현장_월별_입고', index=True)
                
                # 4. 현장별 월별 재고
                if not site_inventory_pivot.empty:
                    site_inventory_pivot.to_excel(writer, sheet_name='현장_월별_재고', index=True)
                
                # 5. 요약 통계
                summary_data = []
                for key, value in summary_stats.items():
                    if isinstance(value, pd.Series):
                        for idx, val in value.items():
                            summary_data.append([key, str(idx), val])
                    else:
                        summary_data.append([key, '', value])
                
                summary_df = pd.DataFrame(summary_data, columns=['통계항목', '세부항목', '값'])
                summary_df.to_excel(writer, sheet_name='요약_통계', index=False)
                
                # 6. 분석 정보
                analysis_info = [
                    ['분석 대상', 'HITACHI 데이터'],
                    ['총 데이터 건수', len(self.hitachi_data)],
                    ['분석 창고 수', len(self.warehouse_columns)],
                    ['분석 기간', f"{inbound_pivot.index.min()} ~ {inbound_pivot.index.max()}" if not inbound_pivot.empty else "데이터 없음"],
                    ['보고서 생성 일시', self.timestamp],
                    ['시스템 버전', 'MACHO-GPT v3.4-mini']
                ]
                
                info_df = pd.DataFrame(analysis_info, columns=['항목', '값'])
                info_df.to_excel(writer, sheet_name='분석_정보', index=False)
            
            print(f"✅ Excel 리포트 생성 완료: {report_file}")
            print(f"📊 파일 크기: {os.path.getsize(report_file):,} bytes")
            
            return report_file
            
        except Exception as e:
            print(f"❌ Excel 리포트 생성 실패: {e}")
            return None
    
    def print_summary_report(self, inbound_pivot, outbound_pivot, site_inbound_pivot, site_inventory_pivot):
        """요약 보고서 출력"""
        print("\n" + "=" * 80)
        print("📊 HITACHI 월별 창고 및 현장 물류 현황 요약")
        print("=" * 80)
        
        # 기본 정보
        print(f"📅 분석 기간: {inbound_pivot.index.min()} ~ {inbound_pivot.index.max()}" if not inbound_pivot.empty else "데이터 없음")
        print(f"📦 총 데이터: {len(self.hitachi_data):,}건")
        
        # 창고별 입고 현황
        if not inbound_pivot.empty:
            print(f"\n🏭 창고별 총 입고 현황:")
            warehouse_totals = inbound_pivot.sum().sort_values(ascending=False)
            for warehouse, total in warehouse_totals.items():
                print(f"   {warehouse}: {total:,}건")
        
        # 현장별 입고 현황 (Top 10)
        if not site_inbound_pivot.empty:
            print(f"\n🏗️ 현장별 총 입고 현황 (Top 10):")
            site_totals = site_inbound_pivot.sum().sort_values(ascending=False).head(10)
            for site, total in site_totals.items():
                print(f"   {site}: {total:,}건")
        
        # 월별 추이
        if not inbound_pivot.empty:
            print(f"\n📈 월별 입고 추이:")
            monthly_totals = inbound_pivot.sum(axis=1).sort_index()
            for month, total in monthly_totals.items():
                print(f"   {month}: {total:,}건")
        
        print("\n✅ 분석 완료!")
    
    def run_analysis(self):
        """전체 분석 실행"""
        print("🚀 HITACHI 월별 창고 및 현장 물류 분석 시작")
        print("=" * 80)
        
        # 1. 데이터 로드
        if not self.load_hitachi_data():
            return
        
        # 2. 창고별 입고/출고 분석
        inbound_pivot, outbound_pivot = self.analyze_warehouse_inbound_outbound()
        
        # 3. 현장별 입고/재고 분석
        site_inbound_pivot, site_inventory_pivot = self.analyze_site_inbound_inventory()
        
        # 4. 요약 통계 생성
        summary_stats = self.generate_summary_statistics(
            inbound_pivot, outbound_pivot, site_inbound_pivot, site_inventory_pivot
        )
        
        # 5. 시각화 생성
        chart_file = self.create_visualizations(inbound_pivot, outbound_pivot, site_inbound_pivot)
        
        # 6. Excel 리포트 생성
        report_file = self.generate_excel_report(
            inbound_pivot, outbound_pivot, site_inbound_pivot, site_inventory_pivot, summary_stats
        )
        
        # 7. 요약 보고서 출력
        self.print_summary_report(inbound_pivot, outbound_pivot, site_inbound_pivot, site_inventory_pivot)
        
        print(f"\n🎉 HITACHI 월별 창고 및 현장 물류 리포트 생성 완료!")
        print(f"📊 Excel 리포트: {report_file}")
        print(f"📈 시각화 차트: {chart_file}")
        
        return {
            'inbound_pivot': inbound_pivot,
            'outbound_pivot': outbound_pivot,
            'site_inbound_pivot': site_inbound_pivot,
            'site_inventory_pivot': site_inventory_pivot,
            'summary_stats': summary_stats,
            'chart_file': chart_file,
            'report_file': report_file
        }


def main():
    """메인 실행 함수"""
    reporter = HitachiMonthlyWarehouseReport()
    results = reporter.run_analysis()
    return results


if __name__ == "__main__":
    main() 