#!/usr/bin/env python3
"""
실제 INVOICE 구조 상세 조사
- 모든 컬럼 값 분포 확인
- SQM, MANPOWER 위치 탐색
- 실제 데이터 샘플 확인
"""

import pandas as pd
import os

class DetailedInvoiceInvestigator:
    """상세 INVOICE 조사"""
    
    def __init__(self):
        self.load_invoice()
        
    def load_invoice(self):
        """INVOICE 로딩"""
        self.df = pd.read_excel('hvdc_ontology_system/data/HVDC WAREHOUSE_INVOICE.xlsx')
        print(f"✅ 로딩 완료: {len(self.df)}건")
        
    def search_sqm_manpower(self):
        """SQM, MANPOWER 검색"""
        print("🔍 SQM, MANPOWER 검색")
        
        # 모든 컬럼에서 SQM 검색
        sqm_found = {}
        manpower_found = {}
        
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                sqm_matches = self.df[self.df[col].astype(str).str.contains('SQM', na=False, case=False)]
                manpower_matches = self.df[self.df[col].astype(str).str.contains('MANPOWER', na=False, case=False)]
                
                if len(sqm_matches) > 0:
                    sqm_found[col] = len(sqm_matches)
                    
                if len(manpower_matches) > 0:
                    manpower_found[col] = len(manpower_matches)
                    
        print("📊 SQM 발견 위치:")
        for col, count in sqm_found.items():
            print(f"  {col}: {count}건")
            
        print("\n📊 MANPOWER 발견 위치:")
        for col, count in manpower_found.items():
            print(f"  {col}: {count}건")
            
        return sqm_found, manpower_found
        
    def analyze_all_columns(self):
        """모든 컬럼 상세 분석"""
        print("\n=== 모든 컬럼 상세 분석 ===")
        
        for col in self.df.columns:
            print(f"\n📋 {col}:")
            if self.df[col].dtype == 'object':
                value_counts = self.df[col].value_counts().head(10)
                for val, count in value_counts.items():
                    print(f"  {val}: {count}건")
                if len(self.df[col].value_counts()) > 10:
                    print(f"  ... (총 {len(self.df[col].value_counts())}개 값)")
            else:
                print(f"  수치형 데이터 - Min: {self.df[col].min()}, Max: {self.df[col].max()}")
                
    def show_sample_records(self):
        """샘플 레코드 확인"""
        print("\n=== 샘플 레코드 (첫 5건) ===")
        
        # 주요 컬럼만 선택
        key_cols = ['HVDC CODE 1', 'HVDC CODE 2', 'HVDC CODE 3', 'HVDC CODE 4', 'Category', 'pkg', 'TOTAL']
        available_cols = [col for col in key_cols if col in self.df.columns]
        
        sample_df = self.df[available_cols].head(5)
        
        for i, row in sample_df.iterrows():
            print(f"\n레코드 {i+1}:")
            for col in available_cols:
                print(f"  {col}: {row[col]}")
                
    def check_hvdc_code_patterns(self):
        """HVDC CODE 패턴 확인"""
        print("\n=== HVDC CODE 패턴 확인 ===")
        
        # HVDC CODE 3에 SQM이 있는지 확인
        if 'HVDC CODE 3' in self.df.columns:
            code3_values = self.df['HVDC CODE 3'].value_counts()
            print("📊 HVDC CODE 3 분포:")
            for val, count in code3_values.items():
                print(f"  {val}: {count}건")
                
        # Category에 SQM이 있는지 확인  
        if 'Category' in self.df.columns:
            category_values = self.df['Category'].value_counts()
            print(f"\n📊 Category 분포:")
            for val, count in category_values.items():
                print(f"  {val}: {count}건")
                
        # 기타 가능한 위치들 확인
        possible_sqm_cols = ['HVDC CODE 4', 'Sqm']
        for col in possible_sqm_cols:
            if col in self.df.columns:
                print(f"\n📊 {col}:")
                if self.df[col].dtype == 'object':
                    vals = self.df[col].value_counts().head(5)
                    for val, count in vals.items():
                        print(f"  {val}: {count}건")
                else:
                    print(f"  수치형 - Min: {self.df[col].min()}, Max: {self.df[col].max()}")
                    
    def find_rent_handling_structure(self):
        """RENT/HANDLING 구조 확인"""
        print("\n=== RENT/HANDLING 구조 확인 ===")
        
        # TOTAL 컬럼이 있는지 확인
        if 'TOTAL' in self.df.columns:
            print(f"📊 TOTAL 금액 통계:")
            print(f"  합계: {self.df['TOTAL'].sum():,.2f}")
            print(f"  평균: {self.df['TOTAL'].mean():,.2f}")
            print(f"  최대: {self.df['TOTAL'].max():,.2f}")
            print(f"  최소: {self.df['TOTAL'].min():,.2f}")
            
        # RENT, HANDLING 관련 컬럼 찾기
        rent_handling_cols = [col for col in self.df.columns if 'RENT' in col.upper() or 'HANDLING' in col.upper()]
        print(f"\n📊 RENT/HANDLING 관련 컬럼들:")
        for col in rent_handling_cols:
            print(f"  {col}")
            if self.df[col].dtype in ['int64', 'float64']:
                print(f"    합계: {self.df[col].sum():,.2f}")
                
    def run_investigation(self):
        """전체 조사 실행"""
        print("🎯 실제 INVOICE 구조 상세 조사")
        print("=" * 50)
        
        # 1. SQM, MANPOWER 검색
        self.search_sqm_manpower()
        
        # 2. HVDC CODE 패턴 확인
        self.check_hvdc_code_patterns()
        
        # 3. RENT/HANDLING 구조 확인
        self.find_rent_handling_structure()
        
        # 4. 샘플 레코드 확인
        self.show_sample_records()
        
        print(f"\n✨ 조사 완료")

def main():
    investigator = DetailedInvoiceInvestigator()
    investigator.run_investigation()
    
if __name__ == "__main__":
    main() 