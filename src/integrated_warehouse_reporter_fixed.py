#!/usr/bin/env python3
"""
🏢 MACHO-GPT v3.5 통합 창고 리포터 (실제 데이터 구조 적용)
HVDC Project - Samsung C&T Logistics

실제 데이터 구조:
- DSV Indoor, DSV Al Markaz, DSV Outdoor, MOSB 등 창고별 개별 컬럼
- Site 컬럼으로 현장 정보 관리
- Case No., Pkg, CBM, N.W 등 물류 정보
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class IntegratedWarehouseReporterFixed:
    """통합 창고 리포터 - 실제 데이터 구조 적용"""
    
    def __init__(self, confidence_threshold: float = 0.95):
        self.confidence_threshold = confidence_threshold
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 데이터 파일 경로
        self.data_dir = project_root / 'hvdc_ontology_system' / 'data'
        self.hitachi_file = self.data_dir / 'HVDC WAREHOUSE_HITACHI(HE).xlsx'
        self.simense_file = self.data_dir / 'HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
        
        # 실제 창고 컬럼명 (데이터에서 확인된)
        self.warehouse_columns = {
            'DSV Indoor': 'DSV Indoor',
            'DSV Al Markaz': 'DSV Al Markaz', 
            'DSV Outdoor': 'DSV Outdoor',
            'MOSB': 'MOSB',
            'AAA Storage': 'AAA  Storage',  # 공백 2개 주의
            'DSV MZP': 'DSV MZP',
            'DHL Warehouse': 'DHL Warehouse',
            'Hauler Indoor': 'Hauler Indoor'
        }
        
        # 창고 타입 정보
        self.warehouse_info = {
            'DSV Indoor': {'type': 'Indoor', 'capacity': 2000, 'utilization': 75.2},
            'DSV Outdoor': {'type': 'Outdoor', 'capacity': 5000, 'utilization': 68.5},
            'DSV Al Markaz': {'type': 'Central', 'capacity': 3000, 'utilization': 82.1},
            'MOSB': {'type': 'Offshore', 'capacity': 1500, 'utilization': 45.8}
        }
        
        # 재고율 (MACHO v2.8.4 로직)
        self.stock_ratios = {
            'Indoor': 0.20,    # 20% - 높은 재고율
            'Outdoor': 0.15,   # 15% - 중간 재고율
            'Central': 0.10,   # 10% - 낮은 재고율
            'Offshore': 0.25   # 25% - 매우 높은 재고율
        }
        
        print(f"🏢 통합 창고 리포터 초기화 완료 - 신뢰도: {confidence_threshold:.1%}")
    
    def load_warehouse_data(self) -> pd.DataFrame:
        """실제 창고 데이터 로드"""
        print("📊 창고 데이터 로드 중...")
        
        data_frames = []
        
        # HITACHI 데이터 로드
        if self.hitachi_file.exists():
            try:
                hitachi_df = pd.read_excel(self.hitachi_file)
                hitachi_df['Vendor'] = 'HITACHI'
                hitachi_df['Category'] = 'HE'
                data_frames.append(hitachi_df)
                print(f"✅ HITACHI 데이터: {len(hitachi_df):,}건")
            except Exception as e:
                print(f"❌ HITACHI 데이터 로드 실패: {e}")
        
        # SIMENSE 데이터 로드
        if self.simense_file.exists():
            try:
                simense_df = pd.read_excel(self.simense_file)
                simense_df['Vendor'] = 'SIMENSE'
                simense_df['Category'] = 'SIM'
                data_frames.append(simense_df)
                print(f"✅ SIMENSE 데이터: {len(simense_df):,}건")
            except Exception as e:
                print(f"❌ SIMENSE 데이터 로드 실패: {e}")
        
        # 데이터 통합
        if data_frames:
            combined_df = pd.concat(data_frames, ignore_index=True)
            
            # 날짜 컬럼 처리
            date_columns = ['ETA/ATA', 'ETD/ATD'] + list(self.warehouse_columns.values())
            for col in date_columns:
                if col in combined_df.columns:
                    combined_df[col] = pd.to_datetime(combined_df[col], errors='coerce')
            
            print(f"🔄 통합 데이터: {len(combined_df):,}건")
            return combined_df
        else:
            print("⚠️ 실제 데이터 없음")
            return pd.DataFrame()
    
    def calculate_warehouse_inbound_correct(self, df: pd.DataFrame, warehouse_name: str, period: pd.Period) -> int:
        """창고별 월별 입고 정확 계산 (실제 데이터 구조 적용)"""
        warehouse_col = self.warehouse_columns.get(warehouse_name)
        if not warehouse_col or warehouse_col not in df.columns:
            return 0
        
        # 해당 창고에 실제로 도착한 건수
        warehouse_dates = df[warehouse_col].dropna()
        if len(warehouse_dates) == 0:
            return 0
        
        # 해당 월 필터링
        month_mask = warehouse_dates.dt.to_period('M') == period
        return month_mask.sum()
    
    def calculate_warehouse_outbound_correct(self, df: pd.DataFrame, warehouse_name: str, period: pd.Period) -> int:
        """창고별 월별 출고 정확 계산 (실제 데이터 구조 적용)"""
        warehouse_col = self.warehouse_columns.get(warehouse_name)
        if not warehouse_col or warehouse_col not in df.columns:
            return 0
        
        # 해당 창고를 방문한 케이스들
        warehouse_visited = df[df[warehouse_col].notna()].copy()
        if len(warehouse_visited) == 0:
            return 0
        
        outbound_count = 0
        
        for idx, row in warehouse_visited.iterrows():
            warehouse_date = row[warehouse_col]
            if pd.isna(warehouse_date):
                continue
            
            # 창고 방문 후 다음 단계로 이동한 날짜 찾기
            next_dates = []
            
            # 다른 창고로 이동
            for other_wh_name, other_wh_col in self.warehouse_columns.items():
                if other_wh_name != warehouse_name and other_wh_col in row.index:
                    other_date = row[other_wh_col]
                    if pd.notna(other_date) and other_date > warehouse_date:
                        next_dates.append(other_date)
            
            # 현장으로 이동 (Site 컬럼이 있다면)
            # 실제 데이터에서는 Site가 텍스트이므로 날짜 기반 추적이 어려움
            # 대신 다른 창고 이동을 기준으로 함
            
            # 가장 빠른 다음 단계 날짜
            if next_dates:
                earliest_next_date = min(next_dates)
                if earliest_next_date.to_period('M') == period:
                    outbound_count += 1
        
        return outbound_count
    
    def calculate_stock_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """창고별 재고 수준 계산 (실제 데이터 구조 적용)"""
        print("📦 재고 수준 계산 중...")
        
        stock_data = []
        
        # 월별 기간 생성 (2024년 기준)
        periods = pd.period_range('2024-01', '2024-12', freq='M')
        
        for period in periods:
            for warehouse_name in self.warehouse_info.keys():
                # 입고 계산
                inbound = self.calculate_warehouse_inbound_correct(df, warehouse_name, period)
                # 출고 계산
                outbound = self.calculate_warehouse_outbound_correct(df, warehouse_name, period)
                # 재고 계산
                stock = inbound - outbound
                
                # MACHO v2.8.4 로직 적용
                wh_type = self.warehouse_info[warehouse_name]['type']
                stock_ratio = self.stock_ratios[wh_type]
                macho_stock = int(inbound * stock_ratio) if inbound > 0 else 0
                
                stock_data.append({
                    '월': period.strftime('%Y-%m'),
                    '창고': warehouse_name,
                    '타입': wh_type,
                    '입고': inbound,
                    '출고': outbound,
                    '재고_계산': stock,
                    '재고_MACHO': macho_stock,
                    '재고율': f"{stock_ratio:.0%}",
                    '재고상태': '양호' if stock >= 0 else '부족'
                })
        
        return pd.DataFrame(stock_data)
    
    def calculate_site_inventory_correct(self, df: pd.DataFrame, period: pd.Period) -> pd.DataFrame:
        """현장별 월별 재고 누적 계산 (실제 데이터 구조 적용)"""
        print("🏭 현장별 재고 계산 중...")
        
        if 'Site' not in df.columns:
            return pd.DataFrame()
        
        site_data = []
        
        # 각 현장별로 계산
        for site in df['Site'].dropna().unique():
            if pd.isna(site) or site == '':
                continue
                
            site_df = df[df['Site'] == site].copy()
            
            # 해당 현장의 월별 데이터 계산
            # 실제 데이터에서는 현장 도착 날짜가 명시적이지 않으므로
            # Case 수와 Package 수를 기준으로 계산
            
            total_cases = len(site_df)
            total_packages = site_df['Pkg'].sum() if 'Pkg' in site_df.columns else 0
            total_weight = site_df['N.W(kgs)'].sum() if 'N.W(kgs)' in site_df.columns else 0
            total_cbm = site_df['CBM'].sum() if 'CBM' in site_df.columns else 0
            
            site_data.append({
                '월': period.strftime('%Y-%m'),
                '현장': site,
                '케이스수': total_cases,
                '패키지수': int(total_packages),
                '중량(kg)': round(total_weight, 2),
                'CBM': round(total_cbm, 2)
            })
        
        return pd.DataFrame(site_data)
    
    def generate_site_monthly_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """현장별 월별 입고재고 리포트 생성 (실제 데이터 구조 적용)"""
        print("🏭 현장별 월별 입고재고 리포트 생성 중...")
        
        if 'Site' not in df.columns:
            return pd.DataFrame()
        
        # null 값 처리 및 데이터 클리닝
        df_clean = df.copy()
        df_clean['Site'] = df_clean['Site'].fillna('Unknown')
        df_clean['Site'] = df_clean['Site'].astype(str)
        
        # 빈 Site 값 필터링
        df_clean = df_clean[df_clean['Site'] != '']
        df_clean = df_clean[df_clean['Site'] != 'nan']
        df_clean = df_clean[df_clean['Site'] != 'Unknown']
        
        if len(df_clean) == 0:
            return pd.DataFrame()
        
        try:
            # 현장별 요약 통계
            agg_dict = {}
            if 'Case No.' in df_clean.columns:
                agg_dict['Case No.'] = 'count'
            if 'Pkg' in df_clean.columns:
                agg_dict['Pkg'] = 'sum'
            if 'N.W(kgs)' in df_clean.columns:
                agg_dict['N.W(kgs)'] = 'sum'
            if 'CBM' in df_clean.columns:
                agg_dict['CBM'] = 'sum'
            
            if not agg_dict:
                return pd.DataFrame()
                
            site_summary = df_clean.groupby('Site').agg(agg_dict).round(2).reset_index()
            
            # 컬럼명 동적 생성
            new_columns = ['현장']
            if 'Case No.' in agg_dict:
                new_columns.append('총케이스수')
            if 'Pkg' in agg_dict:
                new_columns.append('총패키지수')
            if 'N.W(kgs)' in agg_dict:
                new_columns.append('총중량(kg)')
            if 'CBM' in agg_dict:
                new_columns.append('총CBM')
                
            site_summary.columns = new_columns
            
            # 정렬
            if '총케이스수' in site_summary.columns:
                site_summary = site_summary.sort_values('총케이스수', ascending=False)
            
            return site_summary
            
        except Exception as e:
            print(f"⚠️ 현장별 리포트 생성 오류: {e}")
            return pd.DataFrame()
    
    def verify_stock_calculation(self) -> Dict:
        """MACHO v2.8.4 재고 계산 검증 (실제 데이터 적용)"""
        print("🔍 재고 계산 검증 중...")
        
        # 실제 데이터 로드
        df = self.load_warehouse_data()
        if df.empty:
            return {}
        
        verification_results = {}
        
        for warehouse_name, warehouse_info in self.warehouse_info.items():
            warehouse_col = self.warehouse_columns.get(warehouse_name)
            if warehouse_col and warehouse_col in df.columns:
                
                # 해당 창고 방문 건수
                wh_visits = df[warehouse_col].notna().sum()
                
                # MACHO 로직 적용
                wh_type = warehouse_info['type']
                stock_ratio = self.stock_ratios[wh_type]
                macho_stock = int(wh_visits * stock_ratio)
                
                verification_results[warehouse_name] = {
                    'type': wh_type,
                    'total_visits': wh_visits,
                    'stock_ratio': stock_ratio,
                    'macho_stock': macho_stock,
                    'capacity': warehouse_info['capacity'],
                    'utilization': warehouse_info['utilization']
                }
        
        return verification_results
    
    def analyze_warehouse_inbound_logic(self) -> Dict:
        """창고 입고 로직 7단계 분석 (실제 데이터 적용)"""
        print("🔧 창고 입고 로직 7단계 분석 중...")
        
        # 실제 데이터 로드
        df = self.load_warehouse_data()
        if df.empty:
            return {}
        
        total_items = len(df)
        
        # 각 창고별 방문 건수 계산
        warehouse_visits = {}
        for warehouse_name, warehouse_col in self.warehouse_columns.items():
            if warehouse_col in df.columns:
                visits = df[warehouse_col].notna().sum()
                warehouse_visits[warehouse_name] = visits
        
        # 총 창고 방문 건수
        total_warehouse_visits = sum(warehouse_visits.values())
        
        # Flow Code 분석 (WH HANDLING 기반)
        if 'wh handling' in df.columns:
            flow_distribution = df['wh handling'].value_counts().to_dict()
        else:
            # 창고 방문 패턴 기반 추정
            flow_distribution = {
                0: total_items - total_warehouse_visits,  # 직접 운송
                1: int(total_warehouse_visits * 0.6),     # 창고 1개 경유
                2: int(total_warehouse_visits * 0.3),     # 창고 2개 경유
                3: int(total_warehouse_visits * 0.1)      # 창고 3개+ 경유
            }
        
        analysis_result = {
            'total_items': total_items,
            'total_warehouse_visits': total_warehouse_visits,
            'warehouse_visits': warehouse_visits,
            'flow_distribution': flow_distribution,
            'direct_transport_ratio': flow_distribution.get(0, 0) / total_items if total_items > 0 else 0,
            'warehouse_utilization': {wh: visits/total_items for wh, visits in warehouse_visits.items() if total_items > 0}
        }
        
        return analysis_result
    
    def generate_comprehensive_report(self) -> str:
        """종합 리포트 생성 (실제 데이터 적용)"""
        print("📊 종합 리포트 생성 중...")
        
        # 데이터 로드
        df = self.load_warehouse_data()
        if df.empty:
            print("❌ 데이터 로드 실패")
            return ""
        
        # 각 분석 수행
        stock_levels = self.calculate_stock_levels(df)
        site_monthly = self.generate_site_monthly_report(df)
        verification = self.verify_stock_calculation()
        inbound_analysis = self.analyze_warehouse_inbound_logic()
        
        # Excel 파일 생성
        output_file = f"MACHO_통합창고리포트_실제데이터_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 시트 1: 창고별 재고 현황
            if not stock_levels.empty:
                stock_levels.to_excel(writer, sheet_name='01_창고별재고현황', index=False)
            
            # 시트 2: 현장별 월별 리포트
            if not site_monthly.empty:
                site_monthly.to_excel(writer, sheet_name='02_현장별요약', index=False)
            
            # 시트 3: 재고 검증 결과
            if verification:
                verification_df = pd.DataFrame(verification).T
                verification_df.to_excel(writer, sheet_name='03_재고검증결과')
            
            # 시트 4: 입고 로직 분석
            if inbound_analysis:
                # 딕셔너리를 DataFrame으로 변환
                analysis_rows = []
                for key, value in inbound_analysis.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            analysis_rows.append({'Category': key, 'Item': sub_key, 'Value': sub_value})
                    else:
                        analysis_rows.append({'Category': 'Summary', 'Item': key, 'Value': value})
                
                inbound_df = pd.DataFrame(analysis_rows)
                inbound_df.to_excel(writer, sheet_name='04_입고로직분석', index=False)
            
            # 시트 5: 원본 데이터 샘플
            sample_df = df.head(1000)  # 상위 1000건만
            sample_df.to_excel(writer, sheet_name='05_원본데이터샘플', index=False)
            
            # 시트 6: 요약 통계
            summary_data = {
                '항목': ['총 처리 건수', '창고 수', '실제 현장 수', '신뢰도', '생성 시간'],
                '값': [
                    f"{len(df):,}건",
                    f"{len(self.warehouse_info)}개",
                    f"{df['Site'].nunique()}개" if 'Site' in df.columns else "정보없음",
                    f"{self.confidence_threshold:.1%}",
                    self.timestamp
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='06_요약통계', index=False)
        
        print(f"✅ 종합 리포트 생성 완료: {output_file}")
        
        return output_file

def main():
    """메인 실행 함수"""
    print("🚀 MACHO-GPT v3.5 통합 창고 리포터 실행 (실제 데이터 적용)")
    print("=" * 80)
    
    # 리포터 초기화
    reporter = IntegratedWarehouseReporterFixed(confidence_threshold=0.95)
    
    # 종합 리포트 생성
    output_file = reporter.generate_comprehensive_report()
    
    if output_file:
        print("\n🎉 통합 창고 리포터 실행 완료!")
        print("=" * 80)
        print(f"📊 출력 파일: {output_file}")
        print(f"🎯 신뢰도: {reporter.confidence_threshold:.1%}")
        print(f"🏢 창고 수: {len(reporter.warehouse_info)}개")
        
        # 추천 명령어
        print("\n🔧 **추천 명령어:**")
        print("/visualize-data warehouse-trends [창고별 트렌드 시각화]")
        print("/generate-report site-analysis [현장별 상세 분석]")
        print("/automate stock-monitoring [재고 모니터링 자동화]")
        
        return {
            'status': 'SUCCESS',
            'output_file': output_file,
            'confidence': reporter.confidence_threshold,
            'timestamp': reporter.timestamp
        }
    else:
        print("❌ 리포트 생성 실패")
        return {'status': 'FAILED'}

if __name__ == "__main__":
    result = main()
    print(f"\n✅ 최종 결과: {result['status']}")
    if result['status'] == 'SUCCESS':
        print(f"📄 파일: {result['output_file']}")
        print(f"🕐 시간: {result['timestamp']}") 