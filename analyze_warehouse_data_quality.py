#!/usr/bin/env python3
"""
창고 데이터 품질 분석 스크립트
입고 로직 정확도가 39.1%인 이유 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class WarehouseDataQualityAnalyzer:
    """창고 데이터 품질 분석기"""
    
    def __init__(self):
        print("🔍 창고 데이터 품질 분석 시작")
        print("=" * 60)
        
        # 데이터 로드
        self.data_path = Path("data")
        self.hitachi_file = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.simense_file = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        
        self.warehouse_columns = [
            'DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'AAA  Storage',
            'DHL Warehouse', 'MOSB', 'Hauler Indoor'
        ]
        
        self.combined_data = None
        
    def load_data(self):
        """데이터 로드"""
        combined_dfs = []
        
        if self.hitachi_file.exists():
            hitachi_data = pd.read_excel(self.hitachi_file, engine='openpyxl')
            combined_dfs.append(hitachi_data)
        
        if self.simense_file.exists():
            simense_data = pd.read_excel(self.simense_file, engine='openpyxl')
            combined_dfs.append(simense_data)
        
        if combined_dfs:
            self.combined_data = pd.concat(combined_dfs, ignore_index=True, sort=False)
            print(f"📊 총 데이터: {len(self.combined_data):,}건")
            return True
        return False
    
    def analyze_warehouse_column_quality(self):
        """창고 컬럼 데이터 품질 분석"""
        print("\n🏢 창고 컬럼 데이터 품질 분석")
        print("-" * 60)
        
        for warehouse in self.warehouse_columns:
            if warehouse not in self.combined_data.columns:
                continue
                
            print(f"\n📋 {warehouse} 컬럼 분석:")
            
            # 전체 데이터 현황
            total_count = len(self.combined_data)
            non_null_count = self.combined_data[warehouse].notna().sum()
            null_count = total_count - non_null_count
            
            print(f"   전체 행 수: {total_count:,}")
            print(f"   비어있지 않은 값: {non_null_count:,}건 ({non_null_count/total_count*100:.1f}%)")
            print(f"   비어있는 값: {null_count:,}건 ({null_count/total_count*100:.1f}%)")
            
            if non_null_count > 0:
                # 데이터 타입 분석
                non_null_data = self.combined_data[warehouse].dropna()
                
                # 날짜 형식 체크
                date_count = 0
                non_date_count = 0
                non_date_samples = []
                
                for value in non_null_data:
                    try:
                        pd.to_datetime(value)
                        date_count += 1
                    except:
                        non_date_count += 1
                        if len(non_date_samples) < 5:
                            non_date_samples.append(str(value))
                
                print(f"   날짜 형식 가능: {date_count:,}건 ({date_count/non_null_count*100:.1f}%)")
                print(f"   날짜 형식 불가: {non_date_count:,}건 ({non_date_count/non_null_count*100:.1f}%)")
                
                if non_date_samples:
                    print(f"   날짜 형식 불가 샘플: {non_date_samples}")
                
                # 유니크 값 개수
                unique_count = non_null_data.nunique()
                print(f"   유니크 값 개수: {unique_count:,}")
                
                # 가장 많은 값들
                value_counts = non_null_data.value_counts().head(5)
                print(f"   상위 5개 값:")
                for value, count in value_counts.items():
                    print(f"     '{value}': {count:,}건")
    
    def analyze_final_location_impact(self):
        """Final_Location 파생이 입고 로직에 미치는 영향 분석"""
        print("\n🎯 Final_Location 파생 로직 영향 분석")
        print("-" * 60)
        
        # Status_Location 컬럼 확인
        if 'Status_Location' in self.combined_data.columns:
            print("✅ Status_Location 컬럼 존재")
            
            # Status_Location 분포
            status_location_counts = self.combined_data['Status_Location'].value_counts()
            print(f"📊 Status_Location 분포 (상위 10개):")
            for location, count in status_location_counts.head(10).items():
                percentage = (count / len(self.combined_data)) * 100
                print(f"   {location}: {count:,}건 ({percentage:.1f}%)")
        else:
            print("❌ Status_Location 컬럼 없음")
        
        # Final_Location 파생 로직 시뮬레이션
        print(f"\n🔍 Final_Location 파생 로직 시뮬레이션:")
        
        # DSV Al Markaz 우선 조건
        dsv_al_markaz_condition = (
            self.combined_data['DSV Al Markaz'].notna() & 
            self.combined_data['DSV Al Markaz'].ne('')
        )
        dsv_al_markaz_count = dsv_al_markaz_condition.sum()
        
        # DSV Indoor 차순위 조건
        dsv_indoor_condition = (
            (~dsv_al_markaz_condition) &
            self.combined_data['DSV Indoor'].notna() & 
            self.combined_data['DSV Indoor'].ne('')
        )
        dsv_indoor_count = dsv_indoor_condition.sum()
        
        # 나머지 (Status_Location 사용)
        remaining_count = len(self.combined_data) - dsv_al_markaz_count - dsv_indoor_count
        
        print(f"   DSV Al Markaz 우선 선택: {dsv_al_markaz_count:,}건")
        print(f"   DSV Indoor 차순위 선택: {dsv_indoor_count:,}건")
        print(f"   Status_Location 사용: {remaining_count:,}건")
    
    def analyze_inbound_logic_accuracy(self):
        """입고 로직 정확도 분석"""
        print("\n📊 입고 로직 정확도 분석")
        print("-" * 60)
        
        # 창고별 실제 엔트리 vs 날짜 형식 엔트리 비교
        total_entries = 0
        total_date_entries = 0
        
        for warehouse in self.warehouse_columns:
            if warehouse not in self.combined_data.columns:
                continue
                
            # 전체 non-null 엔트리
            non_null_count = self.combined_data[warehouse].notna().sum()
            total_entries += non_null_count
            
            # 날짜 형식 엔트리
            date_count = 0
            if non_null_count > 0:
                non_null_data = self.combined_data[warehouse].dropna()
                for value in non_null_data:
                    try:
                        pd.to_datetime(value)
                        date_count += 1
                    except:
                        pass
            
            total_date_entries += date_count
            
            accuracy = (date_count / non_null_count * 100) if non_null_count > 0 else 0
            print(f"   {warehouse}:")
            print(f"     전체 엔트리: {non_null_count:,}건")
            print(f"     날짜 형식: {date_count:,}건")
            print(f"     정확도: {accuracy:.1f}%")
        
        overall_accuracy = (total_date_entries / total_entries * 100) if total_entries > 0 else 0
        print(f"\n📈 전체 입고 로직 정확도:")
        print(f"   총 창고 엔트리: {total_entries:,}건")
        print(f"   날짜 형식 엔트리: {total_date_entries:,}건")
        print(f"   정확도: {overall_accuracy:.1f}%")
    
    def suggest_improvements(self):
        """개선 방안 제시"""
        print("\n💡 입고 로직 개선 방안")
        print("-" * 60)
        
        print("1. 📅 날짜 형식 표준화:")
        print("   - 창고 컬럼의 비날짜 데이터 처리 방안 수립")
        print("   - 날짜 형식 변환 로직 개선")
        
        print("\n2. 🔍 데이터 품질 개선:")
        print("   - 창고 컬럼 데이터 입력 규칙 정의")
        print("   - 데이터 검증 로직 추가")
        
        print("\n3. 🎯 Final_Location 로직 최적화:")
        print("   - Status_Location 기반 분류 정확도 향상")
        print("   - 우선순위 로직 재검토")
        
        print("\n4. 📊 입고 로직 대안:")
        print("   - 날짜 형식 외 다른 입고 판단 기준 검토")
        print("   - 복합 조건 기반 입고 로직 개발")
    
    def run_analysis(self):
        """전체 분석 실행"""
        if not self.load_data():
            return
        
        self.analyze_warehouse_column_quality()
        self.analyze_final_location_impact()
        self.analyze_inbound_logic_accuracy()
        self.suggest_improvements()


def main():
    analyzer = WarehouseDataQualityAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main() 