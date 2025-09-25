#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC 원본 데이터 전체 분석 및 출력
MACHO-GPT v3.4-mini for HVDC Project
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from pathlib import Path

class OriginalDataAnalyzer:
    """원본 데이터 전체 분석 클래스"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_hitachi_data(self) -> pd.DataFrame:
        """HITACHI 원본 데이터 로드"""
        file_path = self.data_dir / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        print(f"📊 HITACHI 데이터 로드: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            print(f"✅ HITACHI 데이터 로드 완료: {len(df)}행, {len(df.columns)}컬럼")
            return df
        except Exception as e:
            print(f"❌ HITACHI 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def load_siemens_data(self) -> pd.DataFrame:
        """SIEMENS 원본 데이터 로드"""
        file_path = self.data_dir / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        print(f"📊 SIEMENS 데이터 로드: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            print(f"✅ SIEMENS 데이터 로드 완료: {len(df)}행, {len(df.columns)}컬럼")
            return df
        except Exception as e:
            print(f"❌ SIEMENS 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def analyze_data_structure(self, df: pd.DataFrame, name: str) -> dict:
        """데이터 구조 분석"""
        analysis = {
            'name': name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'unique_counts': {col: df[col].nunique() for col in df.columns},
            'sample_values': {}
        }
        
        # 각 컬럼의 샘플 값들
        for col in df.columns:
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) <= 10:
                analysis['sample_values'][col] = list(unique_vals)
            else:
                analysis['sample_values'][col] = list(unique_vals[:10]) + ['...']
        
        return analysis
    
    def print_data_summary(self, analysis: dict):
        """데이터 요약 출력"""
        print(f"\n{'='*60}")
        print(f"📋 {analysis['name']} 데이터 요약")
        print(f"{'='*60}")
        print(f"총 행 수: {analysis['total_rows']:,}")
        print(f"총 컬럼 수: {analysis['total_columns']}")
        
        print(f"\n📊 컬럼 정보:")
        for i, col in enumerate(analysis['columns'], 1):
            dtype = analysis['data_types'][col]
            null_count = analysis['null_counts'][col]
            unique_count = analysis['unique_counts'][col]
            print(f"{i:2d}. {col:<25} | {str(dtype):<15} | Null: {null_count:>5} | Unique: {unique_count:>5}")
        
        print(f"\n🔍 샘플 값들:")
        for col, values in analysis['sample_values'].items():
            if values:
                print(f"{col:<25}: {values}")
    
    def print_detailed_data(self, df: pd.DataFrame, name: str, max_rows: int = 50):
        """상세 데이터 출력"""
        print(f"\n{'='*80}")
        print(f"📄 {name} 상세 데이터 (처음 {min(max_rows, len(df))}행)")
        print(f"{'='*80}")
        
        # 데이터 출력
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)
        
        print(df.head(max_rows).to_string(index=False))
        
        # 통계 정보
        print(f"\n📈 수치형 컬럼 통계:")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(df[numeric_cols].describe())
        
        # 범주형 컬럼 분포
        print(f"\n📊 범주형 컬럼 분포:")
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:5]:  # 처음 5개만
            print(f"\n{col}:")
            value_counts = df[col].value_counts().head(10)
            for val, count in value_counts.items():
                print(f"  {val}: {count:,}")
    
    def analyze_warehouse_distribution(self, df: pd.DataFrame, name: str):
        """창고별 분포 분석"""
        print(f"\n{'='*60}")
        print(f"🏢 {name} 창고별 분포 분석")
        print(f"{'='*60}")
        
        # Status_Location 컬럼이 있는지 확인
        if 'Status_Location' in df.columns:
            warehouse_dist = df['Status_Location'].value_counts()
            print("Status_Location 분포:")
            for warehouse, count in warehouse_dist.items():
                print(f"  {warehouse}: {count:,}")
        
        # Category 컬럼이 있는지 확인
        if 'Category' in df.columns:
            category_dist = df['Category'].value_counts()
            print(f"\nCategory 분포:")
            for category, count in category_dist.items():
                print(f"  {category}: {count:,}")
    
    def analyze_date_distribution(self, df: pd.DataFrame, name: str):
        """날짜 분포 분석"""
        print(f"\n{'='*60}")
        print(f"📅 {name} 날짜 분포 분석")
        print(f"{'='*60}")
        
        # 날짜 컬럼 찾기
        date_columns = []
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_columns.append(col)
        
        if date_columns:
            for col in date_columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    date_dist = df[col].dt.to_period('M').value_counts().sort_index()
                    print(f"\n{col} 월별 분포:")
                    for period, count in date_dist.head(12).items():
                        print(f"  {period}: {count:,}")
                except:
                    pass
    
    def save_analysis_report(self, hitachi_analysis: dict, siemens_analysis: dict):
        """분석 리포트 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"원본_데이터_전체분석_리포트_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# HVDC 원본 데이터 전체 분석 리포트\n\n")
            f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # HITACHI 분석
            f.write("## 1. HITACHI 데이터 분석\n\n")
            f.write(f"- 총 행 수: {hitachi_analysis['total_rows']:,}\n")
            f.write(f"- 총 컬럼 수: {hitachi_analysis['total_columns']}\n\n")
            
            f.write("### 컬럼 정보\n")
            for col in hitachi_analysis['columns']:
                dtype = hitachi_analysis['data_types'][col]
                null_count = hitachi_analysis['null_counts'][col]
                unique_count = hitachi_analysis['unique_counts'][col]
                f.write(f"- {col}: {dtype} (Null: {null_count}, Unique: {unique_count})\n")
            
            # SIEMENS 분석
            f.write("\n## 2. SIEMENS 데이터 분석\n\n")
            f.write(f"- 총 행 수: {siemens_analysis['total_rows']:,}\n")
            f.write(f"- 총 컬럼 수: {siemens_analysis['total_columns']}\n\n")
            
            f.write("### 컬럼 정보\n")
            for col in siemens_analysis['columns']:
                dtype = siemens_analysis['data_types'][col]
                null_count = siemens_analysis['null_counts'][col]
                unique_count = siemens_analysis['unique_counts'][col]
                f.write(f"- {col}: {dtype} (Null: {null_count}, Unique: {unique_count})\n")
        
        print(f"\n💾 분석 리포트 저장: {report_file}")
    
    def run_full_analysis(self):
        """전체 분석 실행"""
        print("🚀 HVDC 원본 데이터 전체 분석 시작")
        print("="*80)
        
        # 데이터 로드
        hitachi_df = self.load_hitachi_data()
        siemens_df = self.load_siemens_data()
        
        if hitachi_df.empty and siemens_df.empty:
            print("❌ 데이터 로드 실패")
            return
        
        # HITACHI 데이터 분석
        if not hitachi_df.empty:
            hitachi_analysis = self.analyze_data_structure(hitachi_df, "HITACHI")
            self.print_data_summary(hitachi_analysis)
            self.print_detailed_data(hitachi_df, "HITACHI")
            self.analyze_warehouse_distribution(hitachi_df, "HITACHI")
            self.analyze_date_distribution(hitachi_df, "HITACHI")
        else:
            hitachi_analysis = {}
        
        # SIEMENS 데이터 분석
        if not siemens_df.empty:
            siemens_analysis = self.analyze_data_structure(siemens_df, "SIEMENS")
            self.print_data_summary(siemens_analysis)
            self.print_detailed_data(siemens_df, "SIEMENS")
            self.analyze_warehouse_distribution(siemens_df, "SIEMENS")
            self.analyze_date_distribution(siemens_df, "SIEMENS")
        else:
            siemens_analysis = {}
        
        # 통합 분석
        if not hitachi_df.empty and not siemens_df.empty:
            print(f"\n{'='*80}")
            print("🔗 통합 데이터 분석")
            print(f"{'='*80}")
            
            total_records = len(hitachi_df) + len(siemens_df)
            print(f"총 레코드 수: {total_records:,}")
            print(f"HITACHI: {len(hitachi_df):,} ({len(hitachi_df)/total_records*100:.1f}%)")
            print(f"SIEMENS: {len(siemens_df):,} ({len(siemens_df)/total_records*100:.1f}%)")
            
            # 공통 컬럼 분석
            hitachi_cols = set(hitachi_df.columns)
            siemens_cols = set(siemens_df.columns)
            common_cols = hitachi_cols.intersection(siemens_cols)
            
            print(f"\n공통 컬럼 ({len(common_cols)}개):")
            for col in sorted(common_cols):
                print(f"  - {col}")
        
        # 리포트 저장
        if hitachi_analysis and siemens_analysis:
            self.save_analysis_report(hitachi_analysis, siemens_analysis)
        
        print(f"\n✅ 원본 데이터 전체 분석 완료")

def main():
    """메인 함수"""
    analyzer = OriginalDataAnalyzer()
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main() 