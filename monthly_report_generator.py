#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini 월별 입고/출고 이력 리포트 생성기
생성된 트랜잭션 데이터를 기반으로 종합적인 월별 리포트 생성

리포트 구성:
1. 월별 입고/출고 요약
2. 창고별 성과 분석
3. 계절적 패턴 분석
4. KPI 대시보드
5. 비용 분석
6. 운영 효율성 지표
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from typing import Dict, List, Tuple, Any
import json

class MonthlyReportGenerator:
    """월별 리포트 생성기"""
    
    def __init__(self, excel_file: str):
        """리포트 생성기 초기화"""
        self.excel_file = excel_file
        self.df = None
        self.monthly_summary = {}
        self.warehouse_summary = {}
        self.kpi_metrics = {}
        
    def load_data(self):
        """Excel 파일에서 데이터 로드"""
        print(f"📁 데이터 로딩: {self.excel_file}")
        try:
            self.df = pd.read_excel(self.excel_file, sheet_name='전체트랜잭션')
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            print(f"✅ 데이터 로드 완료: {len(self.df):,}건")
            return True
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
            
    def generate_monthly_summary(self):
        """월별 요약 생성"""
        print("\n📅 월별 요약 생성...")
        
        monthly_data = self.df.groupby(['월', 'TxType_Refined']).agg({
            'Qty': ['count', 'sum'],
            'Amount': 'sum',
            'Handling Fee': 'sum'
        }).round(2)
        
        # 월별 총계
        monthly_totals = self.df.groupby('월').agg({
            'Qty': 'sum',
            'Amount': 'sum',
            'Handling Fee': 'sum',
            'Case_No': 'nunique'
        }).round(2)
        
        # 월별 성장률 계산
        monthly_totals['Qty_Growth'] = monthly_totals['Qty'].pct_change().fillna(0) * 100
        monthly_totals['Amount_Growth'] = monthly_totals['Amount'].pct_change().fillna(0) * 100
        
        # 계절적 지수 계산 (연평균 대비)
        yearly_avg = monthly_totals['Qty'].mean()
        monthly_totals['Seasonal_Index'] = (monthly_totals['Qty'] / yearly_avg * 100).round(1)
        
        self.monthly_summary = {
            'detailed': monthly_data,
            'totals': monthly_totals,
            'peak_months': monthly_totals.nlargest(3, 'Qty').index.tolist(),
            'low_months': monthly_totals.nsmallest(3, 'Qty').index.tolist()
        }
        
        print(f"   ✅ {len(monthly_totals)}개월 데이터 분석 완료")
        
    def generate_warehouse_analysis(self):
        """창고별 분석 생성"""
        print("\n🏢 창고별 분석 생성...")
        
        warehouse_data = self.df.groupby(['Location', 'TxType_Refined']).agg({
            'Qty': ['count', 'sum'],
            'Amount': 'sum',
            'Handling Fee': 'sum'
        }).round(2)
        
        # 창고별 효율성 지표
        warehouse_efficiency = self.df.groupby('Location').agg({
            'Qty': 'sum',
            'Amount': ['sum', 'mean'],
            'Handling Fee': ['sum', 'mean'],
            'Case_No': 'nunique'
        }).round(2)
        
        # 처리량 대비 비용 효율성
        warehouse_efficiency['Cost_Per_Unit'] = (
            warehouse_efficiency[('Handling Fee', 'sum')] / 
            warehouse_efficiency[('Qty', 'sum')]
        ).round(2)
        
        # 평균 거래 규모
        warehouse_efficiency['Avg_Transaction_Size'] = (
            warehouse_efficiency[('Amount', 'sum')] / 
            warehouse_efficiency[('Case_No', 'nunique')]
        ).round(2)
        
        # 창고 이용률 계산 (실제 vs 기대)
        expected_distribution = {
            'DSV Outdoor': 0.35,
            'DSV Al Markaz': 0.30,
            'DSV Indoor': 0.20,
            'MOSB': 0.15
        }
        
        total_qty = warehouse_efficiency[('Qty', 'sum')].sum()
        utilization_analysis = {}
        
        for warehouse in warehouse_efficiency.index:
            actual_ratio = warehouse_efficiency.loc[warehouse, ('Qty', 'sum')] / total_qty
            expected_ratio = expected_distribution.get(warehouse, 0.25)
            utilization_analysis[warehouse] = {
                'actual_ratio': actual_ratio,
                'expected_ratio': expected_ratio,
                'utilization_rate': (actual_ratio / expected_ratio * 100) if expected_ratio > 0 else 0
            }
        
        self.warehouse_summary = {
            'detailed': warehouse_data,
            'efficiency': warehouse_efficiency,
            'utilization': utilization_analysis
        }
        
        print(f"   ✅ {len(warehouse_efficiency)}개 창고 분석 완료")
        
    def calculate_kpi_metrics(self):
        """KPI 지표 계산"""
        print("\n📊 KPI 지표 계산...")
        
        # 기본 KPI
        total_transactions = len(self.df)
        total_volume = self.df['Qty'].sum()
        total_revenue = self.df['Amount'].sum()
        total_costs = self.df['Handling Fee'].sum()
        
        # 운영 효율성 KPI
        avg_transaction_value = total_revenue / total_transactions
        avg_handling_cost = total_costs / total_volume
        profit_margin = ((total_revenue - total_costs) / total_revenue * 100) if total_revenue > 0 else 0
        
        # 시간 기반 KPI
        date_range = (self.df['Date'].max() - self.df['Date'].min()).days
        daily_avg_transactions = total_transactions / date_range if date_range > 0 else 0
        daily_avg_volume = total_volume / date_range if date_range > 0 else 0
        
        # 트랜잭션 타입별 KPI
        tx_type_distribution = self.df['TxType_Refined'].value_counts(normalize=True) * 100
        
        # 창고별 처리량 균형도 (표준편차로 측정)
        warehouse_volumes = self.df.groupby('Location')['Qty'].sum()
        volume_balance_score = 100 - (warehouse_volumes.std() / warehouse_volumes.mean() * 100)
        
        # 계절성 지수 (최고/최저 월 비율)
        monthly_volumes = self.df.groupby('월')['Qty'].sum()
        seasonality_ratio = monthly_volumes.max() / monthly_volumes.min() if monthly_volumes.min() > 0 else 0
        
        self.kpi_metrics = {
            'operational': {
                'total_transactions': total_transactions,
                'total_volume': total_volume,
                'total_revenue': total_revenue,
                'total_costs': total_costs,
                'avg_transaction_value': avg_transaction_value,
                'avg_handling_cost': avg_handling_cost,
                'profit_margin': profit_margin
            },
            'efficiency': {
                'daily_avg_transactions': daily_avg_transactions,
                'daily_avg_volume': daily_avg_volume,
                'volume_balance_score': volume_balance_score,
                'seasonality_ratio': seasonality_ratio
            },
            'distribution': {
                'transaction_types': tx_type_distribution.to_dict(),
                'warehouse_volumes': warehouse_volumes.to_dict()
            }
        }
        
        print(f"   ✅ KPI 지표 계산 완료")
        
    def generate_trend_analysis(self):
        """트렌드 분석 생성"""
        print("\n📈 트렌드 분석 생성...")
        
        # 월별 트렌드
        monthly_trends = self.df.groupby('월').agg({
            'Qty': 'sum',
            'Amount': 'sum',
            'Handling Fee': 'sum'
        })
        
        # 이동평균 계산 (3개월)
        monthly_trends['Qty_MA3'] = monthly_trends['Qty'].rolling(window=3, min_periods=1).mean()
        monthly_trends['Amount_MA3'] = monthly_trends['Amount'].rolling(window=3, min_periods=1).mean()
        
        # 트렌드 방향 분석
        recent_3_months = monthly_trends.tail(3)
        last_3_months = monthly_trends.tail(6).head(3)
        
        qty_trend_direction = "증가" if recent_3_months['Qty'].mean() > last_3_months['Qty'].mean() else "감소"
        amount_trend_direction = "증가" if recent_3_months['Amount'].mean() > last_3_months['Amount'].mean() else "감소"
        
        # 예측 (단순 선형 회귀)
        months_numeric = pd.to_numeric(pd.to_datetime(monthly_trends.index))
        qty_slope = np.polyfit(months_numeric, monthly_trends['Qty'], 1)[0]
        amount_slope = np.polyfit(months_numeric, monthly_trends['Amount'], 1)[0]
        
        trend_analysis = {
            'monthly_data': monthly_trends,
            'trends': {
                'qty_direction': qty_trend_direction,
                'amount_direction': amount_trend_direction,
                'qty_slope': qty_slope,
                'amount_slope': amount_slope
            },
            'forecasts': {
                'next_month_qty': monthly_trends['Qty'].iloc[-1] + qty_slope * 30,
                'next_month_amount': monthly_trends['Amount'].iloc[-1] + amount_slope * 30
            }
        }
        
        return trend_analysis
        
    def export_comprehensive_report(self):
        """종합 리포트 Excel 내보내기"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"HVDC_월별입출고이력리포트_{timestamp}.xlsx"
        
        print(f"\n📊 종합 리포트 생성: {filename}")
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # 포맷 정의
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})
            number_format = workbook.add_format({'num_format': '#,##0'})
            percent_format = workbook.add_format({'num_format': '0.0%'})
            
            # 1. 월별 요약
            monthly_totals = self.monthly_summary['totals']
            monthly_totals.to_excel(writer, sheet_name='월별요약', startrow=1)
            worksheet = writer.sheets['월별요약']
            worksheet.write('A1', '월별 입고/출고 요약 리포트', header_format)
            
            # 2. 창고별 분석
            warehouse_efficiency = self.warehouse_summary['efficiency']
            warehouse_efficiency.to_excel(writer, sheet_name='창고별분석', startrow=1)
            worksheet = writer.sheets['창고별분석']
            worksheet.write('A1', '창고별 성과 분석', header_format)
            
            # 3. KPI 대시보드
            kpi_data = []
            for category, metrics in self.kpi_metrics.items():
                if isinstance(metrics, dict):
                    for metric, value in metrics.items():
                        if isinstance(value, (int, float)):
                            kpi_data.append({
                                '카테고리': category,
                                '지표명': metric,
                                '값': value
                            })
            
            kpi_df = pd.DataFrame(kpi_data)
            kpi_df.to_excel(writer, sheet_name='KPI대시보드', index=False)
            
            # 4. 트렌드 분석
            trend_analysis = self.generate_trend_analysis()
            trend_analysis['monthly_data'].to_excel(writer, sheet_name='트렌드분석', startrow=1)
            worksheet = writer.sheets['트렌드분석']
            worksheet.write('A1', '월별 트렌드 분석', header_format)
            
            # 5. 상세 트랜잭션 (샘플)
            sample_df = self.df.head(1000)  # 첫 1000건만
            sample_df.to_excel(writer, sheet_name='상세트랜잭션샘플', index=False)
            
            # 6. 요약 통계
            summary_stats = {
                '전체 트랜잭션 수': [f"{len(self.df):,}건"],
                '총 처리량': [f"{self.df['Qty'].sum():,}개"],
                '총 금액': [f"${self.df['Amount'].sum():,.2f}"],
                '총 하역비': [f"${self.df['Handling Fee'].sum():,.2f}"],
                '분석 기간': [f"{self.df['Date'].min().strftime('%Y-%m-%d')} ~ {self.df['Date'].max().strftime('%Y-%m-%d')}"],
                '창고 수': [f"{self.df['Location'].nunique()}개"],
                '평균 거래액': [f"${self.df['Amount'].mean():,.2f}"],
                '평균 하역비': [f"${self.df['Handling Fee'].mean():.2f}"]
            }
            
            summary_df = pd.DataFrame(summary_stats).T
            summary_df.columns = ['값']
            summary_df.to_excel(writer, sheet_name='요약통계')
            
        print(f"✅ 종합 리포트 저장 완료: {filename}")
        return filename
        
    def print_executive_summary(self):
        """경영진 요약 출력"""
        print("\n" + "="*60)
        print("📋 **HVDC 월별 입고/출고 이력 리포트 - 경영진 요약**")
        print("="*60)
        
        # 기본 지표
        kpi = self.kpi_metrics['operational']
        print(f"📊 **핵심 지표:**")
        print(f"   총 트랜잭션: {kpi['total_transactions']:,}건")
        print(f"   총 처리량: {kpi['total_volume']:,}개")
        print(f"   총 매출: ${kpi['total_revenue']:,.2f}")
        print(f"   총 비용: ${kpi['total_costs']:,.2f}")
        print(f"   수익률: {kpi['profit_margin']:.1f}%")
        
        # 월별 성과
        monthly_totals = self.monthly_summary['totals']
        peak_months = self.monthly_summary['peak_months']
        print(f"\n📅 **월별 성과:**")
        print(f"   최고 성과월: {', '.join(peak_months[:3])}")
        for month in peak_months[:3]:
            qty = monthly_totals.loc[month, 'Qty']
            print(f"   {month}: {qty:,}개")
            
        # 창고별 성과
        warehouse_vols = self.kpi_metrics['distribution']['warehouse_volumes']
        print(f"\n🏢 **창고별 성과:**")
        for warehouse, volume in sorted(warehouse_vols.items(), key=lambda x: x[1], reverse=True):
            percentage = (volume / sum(warehouse_vols.values())) * 100
            print(f"   {warehouse}: {volume:,}개 ({percentage:.1f}%)")
            
        # 효율성 지표
        efficiency = self.kpi_metrics['efficiency']
        print(f"\n⚡ **운영 효율성:**")
        print(f"   일평균 거래: {efficiency['daily_avg_transactions']:.1f}건")
        print(f"   일평균 처리량: {efficiency['daily_avg_volume']:,.1f}개")
        print(f"   창고 균형도: {efficiency['volume_balance_score']:.1f}점")
        print(f"   계절성 지수: {efficiency['seasonality_ratio']:.2f}")
        
        # 트렌드 전망
        trend = self.generate_trend_analysis()
        print(f"\n📈 **트렌드 전망:**")
        print(f"   수량 트렌드: {trend['trends']['qty_direction']}")
        print(f"   금액 트렌드: {trend['trends']['amount_direction']}")
        print(f"   다음달 예상 처리량: {trend['forecasts']['next_month_qty']:,.0f}개")
        print(f"   다음달 예상 매출: ${trend['forecasts']['next_month_amount']:,.0f}")

def main():
    """메인 리포트 생성 함수"""
    print("📊 MACHO-GPT v3.4-mini 월별 입고/출고 이력 리포트 생성기")
    print("=" * 60)
    
    # 최신 Excel 파일 찾기
    excel_files = glob.glob("HVDC_월별트랜잭션데이터_*.xlsx")
    if not excel_files:
        print("❌ 트랜잭션 Excel 파일을 찾을 수 없습니다.")
        return False
        
    latest_file = max(excel_files, key=os.path.getctime)
    print(f"📁 분석 파일: {latest_file}")
    
    # 리포트 생성기 실행
    generator = MonthlyReportGenerator(latest_file)
    
    if not generator.load_data():
        return False
        
    # 모든 분석 실행
    generator.generate_monthly_summary()
    generator.generate_warehouse_analysis()
    generator.calculate_kpi_metrics()
    
    # 리포트 출력 및 내보내기
    generator.print_executive_summary()
    report_file = generator.export_comprehensive_report()
    
    print(f"\n🎯 **리포트 생성 완료!**")
    print(f"   📁 파일: {report_file}")
    print(f"   📊 분석 완료: {len(generator.df):,}건 트랜잭션")
    
    return True

if __name__ == '__main__':
    success = main()
    
    print("\n🔧 **추천 명령어:**")
    print("/bi_dashboard create_visualization [대시보드 시각화 생성]")
    print("/forecast_analyzer predict_trends [트렌드 예측 분석]")
    print("/performance_optimizer suggest_improvements [성능 최적화 제안]") 