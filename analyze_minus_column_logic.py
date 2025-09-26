#!/usr/bin/env python3
"""
🎯 MINUS 컬럼 기반 Port→Site 직접 배달 로직 분석 v2.8.3
MACHO-GPT v3.4-mini │ Samsung C&T Logistics

비즈니스 로직:
- MINUS = -1 → PORT to MIR/SHU 육상 현장 직접 배달 (Port→Site)
- 이것이 1819건의 정확한 식별 조건
"""

import pandas as pd
import numpy as np
import sys
import os

class MinusColumnAnalyzer:
    def __init__(self):
        print("🎯 MINUS 컬럼 기반 Port→Site 분석 v2.8.3")
        print("=" * 60)
        
        # 비즈니스 로직 정의
        self.business_logic = {
            'minus_negative_one': 'PORT to MIR/SHU 육상 현장 직접 배달',
            'target_locations': ['MIR', 'SHU'],
            'expected_count': 1819
        }
        
    def load_hitachi_data(self):
        """HITACHI 원본 데이터 로드"""
        file_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        
        if not os.path.exists(file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            return None
            
        try:
            print(f"📂 HITACHI 원본 데이터 로드 중...")
            df = pd.read_excel(file_path)
            print(f"✅ 데이터 로드 성공: {len(df):,}행")
            
            return df
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return None
    
    def analyze_minus_column(self, df):
        """MINUS 컬럼 분석"""
        print(f"\n🔍 MINUS 컬럼 분석")
        print("-" * 40)
        
        # MINUS 컬럼 존재 확인
        minus_columns = [col for col in df.columns if 'minus' in col.lower() or 'MINUS' in col]
        print(f"📋 MINUS 관련 컬럼: {minus_columns}")
        
        if not minus_columns:
            print("❌ MINUS 컬럼을 찾을 수 없습니다.")
            return None
            
        minus_col = minus_columns[0]  # 첫 번째 MINUS 컬럼 사용
        print(f"🎯 분석 대상: {minus_col}")
        
        # MINUS 컬럼 값 분포
        minus_counts = df[minus_col].value_counts().sort_index()
        print(f"\n📊 {minus_col} 값 분포:")
        for value, count in minus_counts.items():
            print(f"   {value}: {count:,}건")
        
        # MINUS = -1인 케이스 분석
        minus_one_cases = df[df[minus_col] == -1]
        print(f"\n🎯 MINUS = -1 케이스: {len(minus_one_cases):,}건")
        
        return minus_one_cases, minus_col
    
    def analyze_location_distribution(self, minus_one_cases):
        """Location 분포 분석"""
        print(f"\n📍 Location 분포 분석 (MINUS = -1)")
        print("-" * 40)
        
        # Location 관련 컬럼 찾기
        location_columns = [col for col in minus_one_cases.columns 
                          if any(loc in col.upper() for loc in ['LOCATION', 'SITE', 'MIR', 'SHU'])]
        
        print(f"📋 Location 관련 컬럼: {location_columns[:5]}...")  # 처음 5개만 표시
        
        # 주요 Location 컬럼들 분석
        for col in location_columns[:3]:  # 상위 3개 컬럼만 분석
            if col in minus_one_cases.columns:
                print(f"\n🔍 {col} 분포:")
                location_counts = minus_one_cases[col].value_counts().head(10)
                for location, count in location_counts.items():
                    print(f"   {location}: {count:,}건")
    
    def validate_port_to_site_logic(self, minus_one_cases):
        """Port→Site 로직 검증"""
        print(f"\n✅ Port→Site 로직 검증")
        print("-" * 40)
        
        # 예상 결과와 비교
        actual_count = len(minus_one_cases)
        expected_count = self.business_logic['expected_count']
        
        print(f"🎯 비즈니스 로직: MINUS = -1 → Port→Site 직접 배달")
        print(f"📊 실제 MINUS = -1 케이스: {actual_count:,}건")
        print(f"📊 Excel에서 확인된 Port→Site: {expected_count:,}건")
        
        match_percentage = (actual_count / expected_count * 100) if expected_count > 0 else 0
        print(f"📈 일치율: {match_percentage:.1f}%")
        
        if abs(actual_count - expected_count) <= 10:  # 오차 허용 범위
            print("✅ 완벽 일치! MINUS = -1 로직이 정확합니다.")
            return True
        else:
            print(f"❌ 차이 발견: {abs(actual_count - expected_count)}건 차이")
            return False
    
    def generate_corrected_flow_logic(self, df, minus_col):
        """수정된 Flow Code 로직 생성"""
        print(f"\n🔧 수정된 Flow Code 로직 생성")
        print("-" * 40)
        
        # 새로운 Flow Code 로직
        flow_code_logic = []
        
        # Port→Site (MINUS = -1)
        port_to_site = df[df[minus_col] == -1]
        flow_code_logic.append(('Port→Site', len(port_to_site), 'MINUS = -1'))
        
        # 나머지 케이스들 분석
        remaining_cases = df[df[minus_col] != -1]
        
        print(f"📊 새로운 Flow Code 분포:")
        print(f"   Port→Site (MINUS = -1): {len(port_to_site):,}건")
        print(f"   기타 (MINUS ≠ -1): {len(remaining_cases):,}건")
        
        return {
            'port_to_site': port_to_site,
            'remaining': remaining_cases,
            'logic': flow_code_logic
        }
    
    def run_analysis(self):
        """전체 분석 실행"""
        # 데이터 로드
        df = self.load_hitachi_data()
        if df is None:
            return None
        
        # MINUS 컬럼 분석
        result = self.analyze_minus_column(df)
        if result is None:
            return None
            
        minus_one_cases, minus_col = result
        
        # Location 분포 분석
        self.analyze_location_distribution(minus_one_cases)
        
        # Port→Site 로직 검증
        is_valid = self.validate_port_to_site_logic(minus_one_cases)
        
        # 수정된 Flow Code 로직 생성
        flow_logic = self.generate_corrected_flow_logic(df, minus_col)
        
        print(f"\n" + "=" * 60)
        print("🎯 MINUS 컬럼 분석 완료")
        print("=" * 60)
        
        if is_valid:
            print("✅ MINUS = -1 로직으로 Port→Site 1819건 정확히 식별!")
            print("🔧 이 로직을 MOSB 인식 시스템에 적용 권장")
        else:
            print("🔧 MINUS 컬럼 로직 추가 분석 필요")
        
        print(f"📊 총 HITACHI 데이터: {len(df):,}건")
        print(f"🎯 Port→Site (MINUS = -1): {len(minus_one_cases):,}건")
        
        return {
            'total_count': len(df),
            'port_to_site_count': len(minus_one_cases),
            'logic_valid': is_valid,
            'minus_column': minus_col,
            'flow_logic': flow_logic
        }

if __name__ == "__main__":
    analyzer = MinusColumnAnalyzer()
    result = analyzer.run_analysis() 