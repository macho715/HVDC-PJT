#!/usr/bin/env python3
"""
HVDC 프로젝트 SQM (Square Meter) 종합 분석 시스템
MACHO-GPT v3.4-mini | Samsung C&T × ADNOC·DSV Partnership

목적: 창고별 SQM 임대료 및 면적 데이터 완전 분석
- HVDC CODE 2 = 'SQM' 필터링 데이터 분석
- 창고별 면적 및 임대료 분석
- 벤더별 (HITACHI/SIMENSE) SQM 분포 분석
- 월별 SQM 사용량 패턴 분석
- 비용 효율성 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class HVDCSQMAnalyzer:
    """HVDC SQM 종합 분석기"""
    
    def __init__(self):
        self.invoice_file = "data_cleaned/HVDC_WAREHOUSE_INVOICE_CLEANED_20250709_201121.xlsx"
        self.hitachi_file = "data_cleaned/HVDC_WAREHOUSE_HITACHI_CLEANED_20250709_201121.xlsx"
        self.simense_file = "data_cleaned/HVDC_WAREHOUSE_SIMENSE_CLEANED_20250709_201121.xlsx"
        
        self.invoice_data = None
        self.hitachi_data = None
        self.simense_data = None
        
        print("🏢 HVDC SQM 종합 분석 시스템 초기화")
        print("=" * 70)
        
    def load_data(self):
        """데이터 로드"""
        print("📊 데이터 로드 중...")
        
        try:
            # INVOICE 데이터 로드
            self.invoice_data = pd.read_excel(self.invoice_file)
            print(f"✅ INVOICE 데이터: {len(self.invoice_data):,}건")
            
            # HITACHI 데이터 로드
            try:
                self.hitachi_data = pd.read_excel(self.hitachi_file)
                print(f"✅ HITACHI 데이터: {len(self.hitachi_data):,}건")
            except FileNotFoundError:
                print("⚠️  HITACHI 파일 없음")
                
            # SIMENSE 데이터 로드
            try:
                self.simense_data = pd.read_excel(self.simense_file)
                print(f"✅ SIMENSE 데이터: {len(self.simense_data):,}건")
            except FileNotFoundError:
                print("⚠️  SIMENSE 파일 없음")
                
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def analyze_invoice_sqm(self):
        """INVOICE SQM 분석"""
        print("\n🏢 INVOICE SQM 데이터 분석")
        print("=" * 50)
        
        if self.invoice_data is None:
            print("❌ INVOICE 데이터가 없습니다.")
            return
        
        # HVDC CODE 2 분포 확인
        print("=== HVDC CODE 2 전체 분포 ===")
        if 'HVDC CODE 2' in self.invoice_data.columns:
            code2_dist = self.invoice_data['HVDC CODE 2'].value_counts().dropna()
            for value, count in code2_dist.items():
                print(f'  "{value}": {count:,}건')
        
            # SQM 필터링
            sqm_data = self.invoice_data[self.invoice_data['HVDC CODE 2'] == 'SQM'].copy()
            print(f"\n=== SQM 필터링 결과: {len(sqm_data):,}건 ===")
            
            if len(sqm_data) > 0:
                self.analyze_sqm_details(sqm_data)
            else:
                print("❌ SQM 데이터가 없습니다.")
        else:
            print("❌ HVDC CODE 2 컬럼이 없습니다.")
    
    def analyze_sqm_details(self, sqm_data):
        """SQM 상세 분석"""
        
        # 기본 통계
        print("\n=== 기본 통계 ===")
        
        # 면적 통계
        if 'Sqm' in sqm_data.columns:
            sqm_stats = sqm_data['Sqm'].describe()
            print(f"📏 면적 통계:")
            print(f"  총 면적: {sqm_data['Sqm'].sum():,.0f} SQM")
            print(f"  평균: {sqm_stats['mean']:.1f} SQM")
            print(f"  중간값: {sqm_stats['50%']:.0f} SQM")
            print(f"  범위: {sqm_stats['min']:.0f} ~ {sqm_stats['max']:.0f} SQM")
            print(f"  NULL: {sqm_data['Sqm'].isnull().sum():,}개")
        
        # 금액 통계
        if 'TOTAL' in sqm_data.columns:
            total_stats = sqm_data['TOTAL'].describe()
            print(f"\n💰 금액 통계:")
            print(f"  총 금액: ${sqm_data['TOTAL'].sum():,.0f}")
            print(f"  평균: ${total_stats['mean']:,.0f}")
            print(f"  중간값: ${total_stats['50%']:,.0f}")
            print(f"  범위: ${total_stats['min']:,.0f} ~ ${total_stats['max']:,.0f}")
        
        # 패키지 통계
        if 'pkg' in sqm_data.columns:
            pkg_stats = sqm_data['pkg'].describe()
            print(f"\n📦 패키지 통계:")
            print(f"  총 패키지: {sqm_data['pkg'].sum():,.0f}개")
            print(f"  평균: {pkg_stats['mean']:.1f}개")
            print(f"  범위: {pkg_stats['min']:.0f} ~ {pkg_stats['max']:.0f}개")
        
        # 창고별 분석
        self.analyze_warehouse_sqm(sqm_data)
        
        # 벤더별 분석
        self.analyze_vendor_sqm(sqm_data)
        
        # 비용 효율성 분석
        self.analyze_cost_efficiency(sqm_data)
    
    def analyze_warehouse_sqm(self, sqm_data):
        """창고별 SQM 분석"""
        print("\n=== 창고별 SQM 분석 ===")
        
        if 'HVDC CODE 1' not in sqm_data.columns:
            print("❌ 창고 정보 없음")
            return
        
        # 창고별 집계
        warehouse_cols = ['Sqm', 'TOTAL']
        if 'pkg' in sqm_data.columns:
            warehouse_cols.append('pkg')
        
        # 유효한 컬럼만 사용
        available_cols = [col for col in warehouse_cols if col in sqm_data.columns]
        
        if available_cols:
            warehouse_analysis = sqm_data.groupby('HVDC CODE 1').agg({
                col: ['sum', 'mean', 'count'] for col in available_cols
            }).round(1)
            
            # 창고별 상세 정보
            for warehouse in warehouse_analysis.index:
                if pd.notna(warehouse):
                    print(f"\n🏭 {warehouse}:")
                    
                    if 'Sqm' in available_cols:
                        sqm_sum = warehouse_analysis.loc[warehouse, ('Sqm', 'sum')]
                        sqm_mean = warehouse_analysis.loc[warehouse, ('Sqm', 'mean')]
                        sqm_count = warehouse_analysis.loc[warehouse, ('Sqm', 'count')]
                        print(f"  총 면적: {sqm_sum:,.0f} SQM")
                        print(f"  평균 면적: {sqm_mean:.1f} SQM")
                        print(f"  건수: {sqm_count:.0f}건")
                    
                    if 'TOTAL' in available_cols:
                        total_sum = warehouse_analysis.loc[warehouse, ('TOTAL', 'sum')]
                        print(f"  총 금액: ${total_sum:,.0f}")
                        
                        # 단가 계산
                        if 'Sqm' in available_cols:
                            sqm_sum = warehouse_analysis.loc[warehouse, ('Sqm', 'sum')]
                            if sqm_sum > 0:
                                price_per_sqm = total_sum / sqm_sum
                                print(f"  단가: ${price_per_sqm:.2f}/SQM")
                    
                    if 'pkg' in available_cols:
                        pkg_sum = warehouse_analysis.loc[warehouse, ('pkg', 'sum')]
                        print(f"  총 패키지: {pkg_sum:,.0f}개")
        
        # 창고별 순위
        self.rank_warehouses_by_sqm(sqm_data)
    
    def analyze_vendor_sqm(self, sqm_data):
        """벤더별 SQM 분석"""
        print("\n=== 벤더별 SQM 분석 ===")
        
        if 'HVDC CODE 3' not in sqm_data.columns:
            print("❌ 벤더 정보 없음")
            return
        
        vendor_dist = sqm_data['HVDC CODE 3'].value_counts().dropna()
        print("벤더별 분포:")
        for vendor, count in vendor_dist.items():
            print(f"  {vendor}: {count:,}건")
        
        # 벤더별 상세 분석
        if 'Sqm' in sqm_data.columns and 'TOTAL' in sqm_data.columns:
            vendor_analysis = sqm_data.groupby('HVDC CODE 3').agg({
                'Sqm': ['sum', 'mean'],
                'TOTAL': ['sum', 'mean']
            }).round(1)
            
            print("\n벤더별 상세 분석:")
            for vendor in vendor_analysis.index:
                if pd.notna(vendor):
                    print(f"\n📋 {vendor}:")
                    sqm_sum = vendor_analysis.loc[vendor, ('Sqm', 'sum')]
                    total_sum = vendor_analysis.loc[vendor, ('TOTAL', 'sum')]
                    print(f"  총 면적: {sqm_sum:,.0f} SQM")
                    print(f"  총 금액: ${total_sum:,.0f}")
                    if sqm_sum > 0:
                        price_per_sqm = total_sum / sqm_sum
                        print(f"  단가: ${price_per_sqm:.2f}/SQM")
    
    def analyze_cost_efficiency(self, sqm_data):
        """비용 효율성 분석"""
        print("\n=== 비용 효율성 분석 ===")
        
        if 'Sqm' not in sqm_data.columns or 'TOTAL' not in sqm_data.columns:
            print("❌ 비용 분석에 필요한 데이터 없음")
            return
        
        # 전체 평균 단가
        total_sqm = sqm_data['Sqm'].sum()
        total_cost = sqm_data['TOTAL'].sum()
        
        if total_sqm > 0:
            avg_price_per_sqm = total_cost / total_sqm
            print(f"💰 전체 평균 단가: ${avg_price_per_sqm:.2f}/SQM")
            print(f"📊 총 규모: {total_sqm:,.0f} SQM, ${total_cost:,.0f}")
        
        # 창고별 효율성 순위
        if 'HVDC CODE 1' in sqm_data.columns:
            warehouse_efficiency = sqm_data.groupby('HVDC CODE 1').agg({
                'Sqm': 'sum',
                'TOTAL': 'sum'
            })
            
            # 단가 계산
            warehouse_efficiency['Price_per_SQM'] = (
                warehouse_efficiency['TOTAL'] / warehouse_efficiency['Sqm']
            ).round(2)
            
            # 효율성 순위 (낮은 단가가 좋음)
            efficiency_ranking = warehouse_efficiency.sort_values('Price_per_SQM')
            
            print(f"\n🏆 창고별 비용 효율성 순위 (단가 기준):")
            for i, (warehouse, data) in enumerate(efficiency_ranking.iterrows(), 1):
                if pd.notna(warehouse) and data['Sqm'] > 0:
                    percentage = data['Sqm'] / total_sqm * 100
                    print(f"  {i}위. {warehouse}: ${data['Price_per_SQM']:.2f}/SQM ({percentage:.1f}% 점유)")
    
    def rank_warehouses_by_sqm(self, sqm_data):
        """창고별 면적 순위"""
        print("\n=== 창고별 면적 순위 ===")
        
        if 'HVDC CODE 1' not in sqm_data.columns or 'Sqm' not in sqm_data.columns:
            return
        
        warehouse_sqm = sqm_data.groupby('HVDC CODE 1')['Sqm'].sum().sort_values(ascending=False)
        total_sqm = warehouse_sqm.sum()
        
        print("📊 면적 기준 순위:")
        for i, (warehouse, sqm) in enumerate(warehouse_sqm.items(), 1):
            percentage = sqm / total_sqm * 100
            print(f"  {i}위. {warehouse}: {sqm:,.0f} SQM ({percentage:.1f}%)")
    
    def analyze_monthly_patterns(self, sqm_data):
        """월별 SQM 패턴 분석"""
        print("\n=== 월별 SQM 패턴 분석 ===")
        
        if 'Operation Month' not in sqm_data.columns:
            print("❌ 월별 데이터 없음")
            return
        
        # Operation Month를 datetime으로 변환
        sqm_data['Operation Month'] = pd.to_datetime(sqm_data['Operation Month'])
        sqm_data['Year_Month'] = sqm_data['Operation Month'].dt.strftime('%Y-%m')
        
        # 월별 집계
        monthly_sqm = sqm_data.groupby('Year_Month').agg({
            'Sqm': 'sum',
            'TOTAL': 'sum'
        }).round(0)
        
        print("월별 SQM 사용량:")
        for month, data in monthly_sqm.iterrows():
            print(f"  {month}: {data['Sqm']:,.0f} SQM, ${data['TOTAL']:,.0f}")
    
    def analyze_vendor_data(self):
        """벤더별 데이터 분석 (HITACHI/SIMENSE)"""
        print("\n🏭 벤더별 데이터 분석")
        print("=" * 50)
        
        # HITACHI 분석
        if self.hitachi_data is not None:
            print(f"\n📦 HITACHI 데이터 분석 ({len(self.hitachi_data):,}건)")
            self.analyze_vendor_specific_sqm(self.hitachi_data, "HITACHI")
        
        # SIMENSE 분석
        if self.simense_data is not None:
            print(f"\n📦 SIMENSE 데이터 분석 ({len(self.simense_data):,}건)")
            self.analyze_vendor_specific_sqm(self.simense_data, "SIMENSE")
    
    def analyze_vendor_specific_sqm(self, vendor_data, vendor_name):
        """특정 벤더의 SQM 분석"""
        
        # SQM 관련 컬럼 찾기
        sqm_columns = [col for col in vendor_data.columns if 'SQM' in str(col).upper()]
        
        if sqm_columns:
            print(f"  📊 {vendor_name} SQM 컬럼: {sqm_columns}")
            
            for sqm_col in sqm_columns:
                sqm_values = vendor_data[sqm_col].dropna()
                if len(sqm_values) > 0:
                    print(f"    {sqm_col}: {len(sqm_values):,}건, 총 {sqm_values.sum():,.1f} SQM")
        else:
            print(f"  ❌ {vendor_name}에 SQM 컬럼 없음")
    
    def generate_summary_report(self):
        """요약 보고서 생성"""
        print("\n📋 SQM 분석 요약 보고서")
        print("=" * 50)
        
        print(f"📅 분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏢 프로젝트: HVDC Samsung C&T × ADNOC·DSV")
        print(f"🤖 시스템: MACHO-GPT v3.4-mini")
        
        if self.invoice_data is not None:
            print(f"\n📊 데이터 현황:")
            print(f"  INVOICE 데이터: {len(self.invoice_data):,}건")
            
            if 'HVDC CODE 2' in self.invoice_data.columns:
                sqm_count = len(self.invoice_data[self.invoice_data['HVDC CODE 2'] == 'SQM'])
                print(f"  SQM 필터링: {sqm_count:,}건")
            
            if self.hitachi_data is not None:
                print(f"  HITACHI 데이터: {len(self.hitachi_data):,}건")
                
            if self.simense_data is not None:
                print(f"  SIMENSE 데이터: {len(self.simense_data):,}건")
        
        print("\n🎯 분석 완료!")
    
    def run_complete_analysis(self):
        """전체 분석 실행"""
        
        # 1. 데이터 로드
        if not self.load_data():
            return
        
        # 2. INVOICE SQM 분석
        self.analyze_invoice_sqm()
        
        # 3. 벤더별 데이터 분석
        self.analyze_vendor_data()
        
        # 4. 요약 보고서
        self.generate_summary_report()
        
        # 5. 추천 명령어
        print("\n🔧 **추천 명령어:**")
        print("/logi_master [창고별 SQM 최적화 분석 - 면적 효율성 개선]")
        print("/analyze_warehouse [창고별 상세 분석 - 비용 효율성 검토]")
        print("/visualize_data [SQM 데이터 시각화 - 월별 패턴 분석]")

def main():
    """메인 실행 함수"""
    analyzer = HVDCSQMAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main() 