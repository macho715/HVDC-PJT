#!/usr/bin/env python3
"""
정확한 HITACHI 월별 피벗 테이블 생성 스크립트
입고 로직 보고서의 정확한 로직에 따라 구현

핵심 로직:
1. 창고 컬럼에 날짜가 있으면 입고로 판단
2. 각 입고 건별로 Final_Location 계산 (DSV Al Markaz 우선 → DSV Indoor 차순위 → Status_Location)
3. Final_Location 기준으로 월별 피벗 테이블 생성
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class CorrectHitachiPivotAnalyzer:
    """정확한 HITACHI 피벗 테이블 분석기"""
    
    def __init__(self):
        print("🔧 정확한 HITACHI 월별 피벗 테이블 생성 v1.0")
        print("📋 입고 로직 보고서 기준으로 정확한 구현")
        print("=" * 80)
        
        # 창고 컬럼 정의 (보고서 기준)
        self.warehouse_columns = [
            'DSV Outdoor',
            'DSV Indoor', 
            'DSV Al Markaz',
            'AAA  Storage',
            'DHL Warehouse',
            'MOSB',
            'Hauler Indoor'
        ]
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.hitachi_data = None
        self.correct_pivot = None
        
    def load_hitachi_data(self):
        """HITACHI 데이터 로드"""
        print("\n📂 HITACHI 데이터 로드 중...")
        
        # 개선된 데이터 파일 찾기
        improved_files = [f for f in os.listdir('.') if f.startswith('HVDC_DataQuality_Improved_') and f.endswith('.xlsx')]
        
        if not improved_files:
            print("❌ 개선된 데이터 파일을 찾을 수 없습니다.")
            return False
        
        latest_file = max(improved_files, key=lambda x: os.path.getmtime(x))
        print(f"📁 파일: {latest_file}")
        
        try:
            all_data = pd.read_excel(latest_file, sheet_name='개선된_전체_데이터')
            self.hitachi_data = all_data[all_data['Data_Source'] == 'HITACHI'].copy()
            
            print(f"✅ HITACHI 데이터 로드 완료: {len(self.hitachi_data):,}건")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def calculate_final_location(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Final_Location 파생 계산 (보고서 기준 로직)
        - DSV Al Markaz 우선 선택
        - DSV Indoor 차순위
        - 나머지는 Status_Location 사용
        """
        print("\n🔍 Final_Location 계산 중...")
        
        result_df = df.copy()
        
        # Status_Location이 없으면 기본값 설정
        if 'Status_Location' not in result_df.columns:
            result_df['Status_Location'] = 'Unknown'
        
        # np.select를 사용한 고성능 계산 (보고서 기준)
        conditions = [
            result_df['DSV Al Markaz'].notna() & result_df['DSV Al Markaz'].ne(''),
            result_df['DSV Indoor'].notna() & result_df['DSV Indoor'].ne('')
        ]
        
        choices = [
            'DSV Al Markaz',  # 실제 위치명이 아닌 고정값
            'DSV Indoor'      # 실제 위치명이 아닌 고정값
        ]
        
        result_df['Final_Location'] = np.select(
            conditions, 
            choices, 
            default=result_df['Status_Location']
        )
        
        # Final_Location 분포 확인
        final_location_counts = result_df['Final_Location'].value_counts()
        print(f"📊 Final_Location 분포:")
        for location, count in final_location_counts.items():
            print(f"   {location}: {count:,}건")
        
        return result_df
    
    def create_monthly_inbound_pivot_correct(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        월별 입고 피벗 테이블 생성 (보고서 기준 정확한 로직)
        - Final_Location 기준으로 월별 입고량 집계
        """
        print("\n📊 정확한 월별 입고 피벗 테이블 생성 중...")
        print("📋 보고서 기준: Final_Location 기준으로 월별 입고량 집계")
        print("-" * 60)
        
        # 1단계: Final_Location 계산
        result_df = self.calculate_final_location(df)
        inbound_records = []
        
        # 2단계: 각 행별로 창고 컬럼 확인하여 입고 데이터 생성
        print("🔍 창고별 입고 데이터 추출 중...")
        
        for _, row in result_df.iterrows():
            for warehouse in self.warehouse_columns:
                if pd.notna(row[warehouse]):
                    try:
                        warehouse_date = pd.to_datetime(row[warehouse])
                        # 보고서 기준: Final_Location 사용 (warehouse 백업)
                        final_location = row.get('Final_Location', warehouse)
                        
                        inbound_records.append({
                            'Final_Location': final_location,
                            'Month': warehouse_date.to_period('M'),
                            'Count': 1,
                            'Warehouse': warehouse,
                            'Date': warehouse_date
                        })
                    except Exception as e:
                        continue
        
        if not inbound_records:
            print("❌ 입고 데이터가 없습니다.")
            return pd.DataFrame()
        
        print(f"📋 총 입고 데이터 추출: {len(inbound_records):,}건")
        
        # 3단계: pivot_table로 월별 집계 (보고서 기준)
        pivot_df = pd.DataFrame(inbound_records)
        
        # 창고별 입고 현황 출력
        warehouse_summary = pivot_df.groupby('Warehouse')['Count'].sum().sort_values(ascending=False)
        print(f"\n📊 창고별 입고 현황:")
        for warehouse, count in warehouse_summary.items():
            print(f"   {warehouse}: {count:,}건")
        
        # Final_Location별 입고 현황 출력  
        location_summary = pivot_df.groupby('Final_Location')['Count'].sum().sort_values(ascending=False)
        print(f"\n🏢 Final_Location별 입고 현황:")
        for location, count in location_summary.items():
            print(f"   {location}: {count:,}건")
        
        # 피벗 테이블 생성
        self.correct_pivot = pivot_df.pivot_table(
            values='Count',
            index='Month',
            columns='Final_Location',
            aggfunc='sum',
            fill_value=0
        )
        
        print(f"\n✅ 정확한 월별 피벗 테이블 생성 완료:")
        print(f"   크기: {self.correct_pivot.shape[0]}행 × {self.correct_pivot.shape[1]}열")
        print(f"   기간: {self.correct_pivot.index.min()} ~ {self.correct_pivot.index.max()}")
        print(f"   Final_Location: {list(self.correct_pivot.columns)}")
        
        return self.correct_pivot
    
    def compare_with_previous_analysis(self):
        """이전 분석과 비교"""
        print("\n📊 이전 분석과 비교 중...")
        
        # 이전 보고서 파일 확인
        prev_files = [f for f in os.listdir('.') if f.startswith('HITACHI_Analysis_Report_') and f.endswith('.xlsx')]
        
        if prev_files:
            prev_file = max(prev_files, key=lambda x: os.path.getmtime(x))
            try:
                prev_pivot = pd.read_excel(prev_file, sheet_name='HITACHI_월별_피벗', index_col=0)
                
                print(f"📋 이전 분석 vs 정확한 분석:")
                print(f"   이전 피벗 크기: {prev_pivot.shape}")
                print(f"   정확한 피벗 크기: {self.correct_pivot.shape}")
                print(f"   이전 총 입고: {prev_pivot.sum().sum():,}건")
                print(f"   정확한 총 입고: {self.correct_pivot.sum().sum():,}건")
                
                # 컬럼 비교
                prev_columns = set(prev_pivot.columns)
                correct_columns = set(self.correct_pivot.columns)
                
                print(f"\n🔍 Final_Location 컬럼 비교:")
                print(f"   이전 분석만 있는 컬럼: {prev_columns - correct_columns}")
                print(f"   정확한 분석만 있는 컬럼: {correct_columns - prev_columns}")
                print(f"   공통 컬럼: {prev_columns & correct_columns}")
                
            except Exception as e:
                print(f"❌ 이전 분석 비교 실패: {e}")
    
    def generate_correct_excel_report(self):
        """정확한 Excel 보고서 생성"""
        print("\n📋 정확한 HITACHI 분석 보고서 생성 중...")
        
        report_file = f"HITACHI_Correct_Analysis_{self.timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
                # 1. HITACHI 전체 데이터 (Final_Location 포함)
                result_df = self.calculate_final_location(self.hitachi_data)
                result_df.to_excel(writer, sheet_name='HITACHI_데이터_Final_Location', index=False)
                
                # 2. 정확한 월별 피벗 테이블
                if self.correct_pivot is not None and not self.correct_pivot.empty:
                    self.correct_pivot.to_excel(writer, sheet_name='HITACHI_월별_피벗_정확한')
                
                # 3. 월별 총계
                if self.correct_pivot is not None:
                    monthly_totals = self.correct_pivot.sum(axis=1)
                    monthly_df = pd.DataFrame({
                        'Month': monthly_totals.index,
                        'Total_Inbound': monthly_totals.values
                    })
                    monthly_df.to_excel(writer, sheet_name='월별_총_입고량', index=False)
                
                # 4. Final_Location별 총계
                if self.correct_pivot is not None:
                    location_totals = self.correct_pivot.sum(axis=0).sort_values(ascending=False)
                    location_df = pd.DataFrame({
                        'Final_Location': location_totals.index,
                        'Total_Inbound': location_totals.values
                    })
                    location_df.to_excel(writer, sheet_name='Final_Location별_총_입고량', index=False)
                
                # 5. 정확성 검증 요약
                summary_data = [
                    ['보고서 기준 로직 적용', 'YES'],
                    ['Final_Location 컬럼명', 'Final_Location'],
                    ['DSV Al Markaz 우선순위', 'YES'],
                    ['DSV Indoor 차순위', 'YES'],
                    ['Status_Location 기본값', 'YES'],
                    ['총 HITACHI 데이터', f"{len(self.hitachi_data):,}건"],
                    ['총 입고 건수', f"{self.correct_pivot.sum().sum():,}건" if self.correct_pivot is not None else "0건"],
                    ['피벗 테이블 크기', f"{self.correct_pivot.shape}" if self.correct_pivot is not None else "Empty"]
                ]
                
                summary_df = pd.DataFrame(summary_data, columns=['항목', '값'])
                summary_df.to_excel(writer, sheet_name='정확성_검증_요약', index=False)
            
            print(f"✅ 정확한 보고서 생성 완료: {report_file}")
            print(f"📊 파일 크기: {os.path.getsize(report_file):,} bytes")
            
            return report_file
            
        except Exception as e:
            print(f"❌ 보고서 생성 실패: {e}")
            return None
    
    def run_correct_analysis(self):
        """정확한 분석 실행"""
        print("🚀 정확한 HITACHI 분석 시작 (보고서 기준)")
        print("=" * 80)
        
        # 1단계: 데이터 로드
        if not self.load_hitachi_data():
            return
        
        # 2단계: 정확한 월별 피벗 생성
        correct_pivot = self.create_monthly_inbound_pivot_correct(self.hitachi_data)
        
        if correct_pivot is None or correct_pivot.empty:
            print("❌ 정확한 피벗 테이블 생성 실패")
            return
        
        # 3단계: 이전 분석과 비교
        self.compare_with_previous_analysis()
        
        # 4단계: 정확한 보고서 생성
        report_file = self.generate_correct_excel_report()
        
        # 최종 결과
        print("\n" + "=" * 80)
        print("🎉 정확한 HITACHI 분석 완료!")
        print("=" * 80)
        
        print(f"📊 정확한 분석 결과:")
        print(f"   총 HITACHI 데이터: {len(self.hitachi_data):,}건")
        print(f"   총 입고 건수: {self.correct_pivot.sum().sum():,}건")
        print(f"   피벗 테이블 크기: {self.correct_pivot.shape}")
        print(f"   분석 기간: {self.correct_pivot.index.min()} ~ {self.correct_pivot.index.max()}")
        
        if report_file:
            print(f"📁 정확한 보고서: {report_file}")
        
        print("\n✅ 보고서 기준 정확한 로직으로 분석 완료!")
        
        return self.correct_pivot

def main():
    """메인 실행"""
    analyzer = CorrectHitachiPivotAnalyzer()
    analyzer.run_correct_analysis()

if __name__ == "__main__":
    main() 