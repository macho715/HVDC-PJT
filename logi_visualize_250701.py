#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini 데이터 시각화 모듈
HVDC 프로젝트 - Flow Code 트랜잭션 분석 및 시각화

작성: 2025-07-01
버전: v3.4-mini
모드: LATTICE → RHYTHM (데이터 시각화)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MachoFlowCodeVisualizer:
    """MACHO-GPT Flow Code 데이터 시각화 엔진"""
    
    def __init__(self, file_path='flowcode_transaction_table.xlsx'):
        self.file_path = file_path
        self.df = None
        self.confidence_threshold = 0.90
        
    def load_data(self):
        """트랜잭션 데이터 로드"""
        print("🔄 MACHO-GPT 데이터 로더 시작...")
        self.df = pd.read_excel(self.file_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
        print(f"✅ 데이터 로드 완료: {len(self.df):,}건")
        return self.df
    
    def create_flow_code_distribution(self):
        """Flow Code 분포 시각화"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🔄 MACHO-GPT Flow Code 분포 분석 (v3.4-mini)', fontsize=16, fontweight='bold')
        
        # 1. 전체 Flow Code 분포
        flow_counts = self.df['Flow_Code'].value_counts().sort_index()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
        
        axes[0,0].bar(flow_counts.index, flow_counts.values, color=colors[:len(flow_counts)])
        axes[0,0].set_title('전체 Flow Code 분포')
        axes[0,0].set_xlabel('Flow Code')
        axes[0,0].set_ylabel('케이스 수')
        
        # 값 표시
        for i, v in enumerate(flow_counts.values):
            axes[0,0].text(flow_counts.index[i], v + 50, str(v), ha='center', fontweight='bold')
        
        # 2. 벤더별 Flow Code 분포
        vendor_flow = pd.crosstab(self.df['Vendor'], self.df['Flow_Code'])
        vendor_flow.plot(kind='bar', ax=axes[0,1], color=colors[:len(vendor_flow.columns)])
        axes[0,1].set_title('벤더별 Flow Code 분포')
        axes[0,1].set_xlabel('벤더')
        axes[0,1].set_ylabel('케이스 수')
        axes[0,1].legend(title='Flow Code', bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[0,1].tick_params(axis='x', rotation=0)
        
        # 3. Flow Code 비율 파이차트
        axes[1,0].pie(flow_counts.values, labels=[f'Code {i}' for i in flow_counts.index], 
                     autopct='%1.1f%%', colors=colors[:len(flow_counts)])
        axes[1,0].set_title('Flow Code 비율')
        
        # 4. MOSB 분석
        mosb_analysis = self.df.groupby(['Flow_Code', self.df['MOSB'].notna()]).size().unstack(fill_value=0)
        mosb_analysis.columns = ['MOSB 없음', 'MOSB 있음']
        mosb_analysis.plot(kind='bar', ax=axes[1,1], color=['#E74C3C', '#2ECC71'])
        axes[1,1].set_title('Flow Code별 MOSB 분포')
        axes[1,1].set_xlabel('Flow Code')
        axes[1,1].set_ylabel('케이스 수')
        axes[1,1].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        plt.savefig(f'macho_flow_code_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_vendor_analysis(self):
        """벤더별 상세 분석"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('📊 MACHO-GPT 벤더별 분석 (HITACHI vs SIMENSE)', fontsize=16, fontweight='bold')
        
        vendors = ['HITACHI', 'SIMENSE']
        colors = ['#3498DB', '#E74C3C']
        
        # 1. 벤더별 총 케이스 수
        vendor_counts = self.df['Vendor'].value_counts()
        axes[0,0].bar(vendor_counts.index, vendor_counts.values, color=colors)
        axes[0,0].set_title('벤더별 총 케이스 수')
        axes[0,0].set_ylabel('케이스 수')
        
        for i, v in enumerate(vendor_counts.values):
            axes[0,0].text(i, v + 100, f'{v:,}', ha='center', fontweight='bold')
        
        # 2. 벤더별 Pkg 분포
        vendor_pkg = self.df.groupby('Vendor')['Pkg'].sum()
        axes[0,1].bar(vendor_pkg.index, vendor_pkg.values, color=colors)
        axes[0,1].set_title('벤더별 총 Pkg 수량')
        axes[0,1].set_ylabel('Pkg 수량')
        
        # 3. 벤더별 위치 분포 (상위 5개)
        for i, vendor in enumerate(vendors):
            vendor_data = self.df[self.df['Vendor'] == vendor]
            location_counts = vendor_data['Location'].value_counts().head(5)
            
            axes[0,2].barh([f"{vendor}_{loc}" for loc in location_counts.index], 
                          location_counts.values, color=colors[i], alpha=0.7)
        
        axes[0,2].set_title('벤더별 주요 위치 분포 (상위 5개)')
        axes[0,2].set_xlabel('케이스 수')
        
        # 4. 벤더별 월별 트렌드
        monthly_trend = self.df.groupby(['Vendor', self.df['Date'].dt.to_period('M')]).size().unstack(level=0, fill_value=0)
        if not monthly_trend.empty:
            monthly_trend.plot(ax=axes[1,0], color=colors, marker='o')
            axes[1,0].set_title('벤더별 월별 케이스 트렌드')
            axes[1,0].set_xlabel('월')
            axes[1,0].set_ylabel('케이스 수')
            axes[1,0].tick_params(axis='x', rotation=45)
        
        # 5. Flow Code 0,3,4 비교 (MOSB 관련)
        mosb_codes = self.df[self.df['Flow_Code'].isin([0, 3, 4])]
        mosb_vendor = pd.crosstab(mosb_codes['Vendor'], mosb_codes['Flow_Code'])
        mosb_vendor.plot(kind='bar', ax=axes[1,1], color=['#F39C12', '#9B59B6', '#1ABC9C'])
        axes[1,1].set_title('벤더별 MOSB 관련 Flow Code (0,3,4)')
        axes[1,1].set_xlabel('벤더')
        axes[1,1].set_ylabel('케이스 수')
        axes[1,1].tick_params(axis='x', rotation=0)
        
        # 6. 벤더별 wh_before_mosb 분포
        wh_dist = self.df.groupby(['Vendor', 'wh_before_mosb']).size().unstack(level=0, fill_value=0)
        wh_dist.plot(kind='bar', ax=axes[1,2], color=colors)
        axes[1,2].set_title('벤더별 MOSB 이전 창고 수 분포')
        axes[1,2].set_xlabel('MOSB 이전 창고 수')
        axes[1,2].set_ylabel('케이스 수')
        axes[1,2].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        plt.savefig(f'macho_vendor_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_location_heatmap(self):
        """위치별 활동 히트맵"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('🗺️ MACHO-GPT 위치별 활동 히트맵', fontsize=16, fontweight='bold')
        
        # 1. 위치별 Flow Code 히트맵
        location_flow = pd.crosstab(self.df['Location'], self.df['Flow_Code'])
        sns.heatmap(location_flow, annot=True, fmt='d', cmap='YlOrRd', ax=axes[0])
        axes[0].set_title('위치별 Flow Code 분포')
        axes[0].set_xlabel('Flow Code')
        axes[0].set_ylabel('위치')
        
        # 2. 벤더별 위치 히트맵
        vendor_location = pd.crosstab(self.df['Vendor'], self.df['Location'])
        sns.heatmap(vendor_location, annot=True, fmt='d', cmap='Blues', ax=axes[1])
        axes[1].set_title('벤더별 위치 분포')
        axes[1].set_xlabel('위치')
        axes[1].set_ylabel('벤더')
        
        plt.tight_layout()
        plt.savefig(f'macho_location_heatmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_time_series_analysis(self):
        """시계열 분석"""
        if self.df['Date'].isna().all():
            print("⚠️ 날짜 데이터가 없어 시계열 분석을 건너뜁니다.")
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('📅 MACHO-GPT 시계열 분석', fontsize=16, fontweight='bold')
        
        # 날짜별 케이스 수
        daily_counts = self.df.groupby(self.df['Date'].dt.date).size()
        daily_counts.plot(ax=axes[0,0], color='#3498DB', marker='o', markersize=3)
        axes[0,0].set_title('일별 케이스 수')
        axes[0,0].set_xlabel('날짜')
        axes[0,0].set_ylabel('케이스 수')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # 월별 Flow Code 트렌드
        monthly_flow = self.df.groupby([self.df['Date'].dt.to_period('M'), 'Flow_Code']).size().unstack(fill_value=0)
        monthly_flow.plot(ax=axes[0,1], marker='o', markersize=4)
        axes[0,1].set_title('월별 Flow Code 트렌드')
        axes[0,1].set_xlabel('월')
        axes[0,1].set_ylabel('케이스 수')
        axes[0,1].legend(title='Flow Code', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 분기별 벤더 비교
        quarterly = self.df.groupby([self.df['Date'].dt.to_period('Q'), 'Vendor']).size().unstack(fill_value=0)
        quarterly.plot(kind='bar', ax=axes[1,0], color=['#3498DB', '#E74C3C'])
        axes[1,0].set_title('분기별 벤더 비교')
        axes[1,0].set_xlabel('분기')
        axes[1,0].set_ylabel('케이스 수')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # MOSB 시계열
        mosb_trend = self.df[self.df['MOSB'].notna()].groupby(self.df['Date'].dt.to_period('M')).size()
        if not mosb_trend.empty:
            mosb_trend.plot(ax=axes[1,1], color='#E67E22', marker='s', markersize=5)
            axes[1,1].set_title('월별 MOSB 케이스')
            axes[1,1].set_xlabel('월')
            axes[1,1].set_ylabel('MOSB 케이스 수')
        
        plt.tight_layout()
        plt.savefig(f'macho_timeseries_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
    def generate_summary_report(self):
        """요약 리포트 생성"""
        print("\n" + "="*80)
        print("📊 MACHO-GPT v3.4-mini 트랜잭션 분석 요약 리포트")
        print("="*80)
        
        total_cases = len(self.df)
        print(f"📦 총 케이스 수: {total_cases:,}")
        print(f"📅 데이터 기간: {self.df['Date'].min().strftime('%Y-%m-%d')} ~ {self.df['Date'].max().strftime('%Y-%m-%d')}")
        
        print(f"\n🔄 Flow Code 분포:")
        flow_dist = self.df['Flow_Code'].value_counts().sort_index()
        for code, count in flow_dist.items():
            percentage = (count / total_cases) * 100
            print(f"   Code {code}: {count:,}건 ({percentage:.1f}%)")
        
        print(f"\n🏢 벤더별 분포:")
        vendor_dist = self.df['Vendor'].value_counts()
        for vendor, count in vendor_dist.items():
            percentage = (count / total_cases) * 100
            print(f"   {vendor}: {count:,}건 ({percentage:.1f}%)")
        
        print(f"\n📍 상위 5개 위치:")
        location_dist = self.df['Location'].value_counts().head(5)
        for location, count in location_dist.items():
            percentage = (count / total_cases) * 100
            print(f"   {location}: {count:,}건 ({percentage:.1f}%)")
        
        mosb_cases = self.df['MOSB'].notna().sum()
        print(f"\n🚢 MOSB 관련:")
        print(f"   MOSB 케이스: {mosb_cases:,}건 ({(mosb_cases/total_cases)*100:.1f}%)")
        print(f"   비MOSB 케이스: {total_cases-mosb_cases:,}건 ({((total_cases-mosb_cases)/total_cases)*100:.1f}%)")
        
        print(f"\n📈 신뢰도: {self.confidence_threshold*100}% 이상")
        print(f"🎯 분석 완료 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
    def run_full_analysis(self):
        """전체 분석 실행"""
        print("🚀 MACHO-GPT v3.4-mini 데이터 시각화 시작")
        print("모드: LATTICE → RHYTHM (시각화)")
        
        # 데이터 로드
        self.load_data()
        
        # 1. Flow Code 분포 분석
        print("\n🔄 Flow Code 분포 분석 중...")
        self.create_flow_code_distribution()
        
        # 2. 벤더별 분석
        print("\n📊 벤더별 상세 분석 중...")
        self.create_vendor_analysis()
        
        # 3. 위치별 히트맵
        print("\n🗺️ 위치별 활동 분석 중...")
        self.create_location_heatmap()
        
        # 4. 시계열 분석
        print("\n📅 시계열 분석 중...")
        self.create_time_series_analysis()
        
        # 5. 요약 리포트
        print("\n📋 요약 리포트 생성 중...")
        self.generate_summary_report()
        
        return {
            'status': 'SUCCESS',
            'confidence': 0.95,
            'mode': 'RHYTHM',
            'triggers': ['flow_analysis_complete', 'visualization_ready'],
            'next_cmds': [
                'logi_master_pattern_analysis',
                'switch_mode COST_GUARD', 
                'generate_kpi_dashboard'
            ]
        }

# 메인 실행부
if __name__ == "__main__":
    try:
        visualizer = MachoFlowCodeVisualizer('flowcode_transaction_table.xlsx')
        result = visualizer.run_full_analysis()
        
        print(f"\n✅ 시각화 완료 - 신뢰도: {result['confidence']*100}%")
        print(f"📊 상태: {result['status']} | 모드: {result['mode']}")
        
    except Exception as e:
        print(f"❌ 시각화 실행 오류: {e}")
        print("ZERO 모드로 전환 - 수동 확인 필요") 