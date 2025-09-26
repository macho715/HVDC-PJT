#!/usr/bin/env python3
"""
🔍 실제 HVDC RAW DATA 분석 스크립트
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini

실제 RAW DATA 파일 분석:
✅ HVDC WAREHOUSE_HITACHI(HE).xlsx
✅ HVDC WAREHOUSE_SIMENSE(SIM).xlsx  
✅ HVDC WAREHOUSE_INVOICE.xlsx
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class RealHVDCDataAnalyzer:
    def __init__(self):
        print("🔍 실제 HVDC RAW DATA 분석 시작")
        print("=" * 80)
        
        # 실제 파일 경로
        self.data_path = Path("hvdc_ontology_system/data")
        self.hitachi_file = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.simense_file = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        self.invoice_file = self.data_path / "HVDC WAREHOUSE_INVOICE.xlsx"
        
        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 결과 데이터 저장
        self.hitachi_data = None
        self.simense_data = None
        self.invoice_data = None
        self.combined_data = None
        
    def load_real_data(self):
        """실제 RAW DATA 파일 로드"""
        print("📂 실제 RAW DATA 파일 로드 중...")
        
        # HITACHI 데이터 로드
        try:
            print(f"📊 HITACHI 데이터 로드: {self.hitachi_file}")
            self.hitachi_data = pd.read_excel(self.hitachi_file, engine='openpyxl')
            print(f"✅ HITACHI 로드 완료: {self.hitachi_data.shape}")
            print(f"   컬럼 수: {len(self.hitachi_data.columns)}")
            print(f"   행 수: {len(self.hitachi_data)}")
        except Exception as e:
            print(f"❌ HITACHI 로드 실패: {e}")
            
        # SIMENSE 데이터 로드
        try:
            print(f"📊 SIMENSE 데이터 로드: {self.simense_file}")
            self.simense_data = pd.read_excel(self.simense_file, engine='openpyxl')
            print(f"✅ SIMENSE 로드 완료: {self.simense_data.shape}")
            print(f"   컬럼 수: {len(self.simense_data.columns)}")
            print(f"   행 수: {len(self.simense_data)}")
        except Exception as e:
            print(f"❌ SIMENSE 로드 실패: {e}")
            
        # INVOICE 데이터 로드
        try:
            print(f"📊 INVOICE 데이터 로드: {self.invoice_file}")
            self.invoice_data = pd.read_excel(self.invoice_file, engine='openpyxl')
            print(f"✅ INVOICE 로드 완료: {self.invoice_data.shape}")
            print(f"   컬럼 수: {len(self.invoice_data.columns)}")
            print(f"   행 수: {len(self.invoice_data)}")
        except Exception as e:
            print(f"❌ INVOICE 로드 실패: {e}")
    
    def analyze_data_structure(self):
        """데이터 구조 분석"""
        print("\n🔍 데이터 구조 분석")
        print("=" * 50)
        
        # HITACHI 데이터 분석
        if self.hitachi_data is not None:
            print("\n📊 HITACHI 데이터 구조:")
            print(f"   Shape: {self.hitachi_data.shape}")
            print(f"   컬럼들: {list(self.hitachi_data.columns)}")
            print(f"   데이터 타입:")
            for col in self.hitachi_data.columns:
                print(f"     {col}: {self.hitachi_data[col].dtype}")
            
            # 샘플 데이터 확인
            print(f"\n   샘플 데이터 (처음 3행):")
            print(self.hitachi_data.head(3))
            
        # SIMENSE 데이터 분석
        if self.simense_data is not None:
            print("\n📊 SIMENSE 데이터 구조:")
            print(f"   Shape: {self.simense_data.shape}")
            print(f"   컬럼들: {list(self.simense_data.columns)}")
            print(f"   데이터 타입:")
            for col in self.simense_data.columns:
                print(f"     {col}: {self.simense_data[col].dtype}")
            
            # 샘플 데이터 확인
            print(f"\n   샘플 데이터 (처음 3행):")
            print(self.simense_data.head(3))
            
        # INVOICE 데이터 분석
        if self.invoice_data is not None:
            print("\n📊 INVOICE 데이터 구조:")
            print(f"   Shape: {self.invoice_data.shape}")
            print(f"   컬럼들: {list(self.invoice_data.columns)}")
            print(f"   데이터 타입:")
            for col in self.invoice_data.columns:
                print(f"     {col}: {self.invoice_data[col].dtype}")
            
            # 샘플 데이터 확인
            print(f"\n   샘플 데이터 (처음 3행):")
            print(self.invoice_data.head(3))
    
    def find_common_columns(self):
        """공통 컬럼 찾기"""
        print("\n🔍 공통 컬럼 분석")
        print("=" * 50)
        
        all_columns = []
        
        if self.hitachi_data is not None:
            hitachi_cols = set(self.hitachi_data.columns)
            all_columns.append(('HITACHI', hitachi_cols))
            
        if self.simense_data is not None:
            simense_cols = set(self.simense_data.columns)
            all_columns.append(('SIMENSE', simense_cols))
            
        if self.invoice_data is not None:
            invoice_cols = set(self.invoice_data.columns)
            all_columns.append(('INVOICE', invoice_cols))
        
        if len(all_columns) >= 2:
            # 공통 컬럼 찾기
            common_cols = all_columns[0][1]
            for name, cols in all_columns[1:]:
                common_cols = common_cols.intersection(cols)
            
            print(f"📊 공통 컬럼 ({len(common_cols)}개):")
            for col in sorted(common_cols):
                print(f"   - {col}")
            
            # 각 데이터셋 고유 컬럼
            for name, cols in all_columns:
                unique_cols = cols - common_cols
                print(f"\n📊 {name} 고유 컬럼 ({len(unique_cols)}개):")
                for col in sorted(unique_cols):
                    print(f"   - {col}")
        
        return all_columns
    
    def combine_data(self):
        """데이터 결합"""
        print("\n🔗 데이터 결합 시작")
        print("=" * 50)
        
        combined_dfs = []
        
        # HITACHI 데이터 추가
        if self.hitachi_data is not None:
            hitachi_df = self.hitachi_data.copy()
            hitachi_df['Vendor'] = 'HITACHI'
            hitachi_df['Source_File'] = 'HITACHI(HE)'
            combined_dfs.append(hitachi_df)
            print(f"✅ HITACHI 추가: {len(hitachi_df)}건")
        
        # SIMENSE 데이터 추가
        if self.simense_data is not None:
            simense_df = self.simense_data.copy()
            simense_df['Vendor'] = 'SIMENSE'
            simense_df['Source_File'] = 'SIMENSE(SIM)'
            combined_dfs.append(simense_df)
            print(f"✅ SIMENSE 추가: {len(simense_df)}건")
        
        # 데이터 결합
        if combined_dfs:
            self.combined_data = pd.concat(combined_dfs, ignore_index=True, sort=False)
            print(f"🎉 데이터 결합 완료: {len(self.combined_data)}건")
            print(f"   총 컬럼 수: {len(self.combined_data.columns)}")
            
            # 벤더별 분포 확인
            vendor_counts = self.combined_data['Vendor'].value_counts()
            print(f"\n📊 벤더별 분포:")
            for vendor, count in vendor_counts.items():
                percentage = count / len(self.combined_data) * 100
                print(f"   {vendor}: {count:,}건 ({percentage:.1f}%)")
        
        return self.combined_data
    
    def identify_warehouse_site_columns(self):
        """창고 및 현장 컬럼 식별"""
        print("\n🏭 창고 및 현장 컬럼 식별")
        print("=" * 50)
        
        if self.combined_data is None:
            print("❌ 결합된 데이터가 없습니다.")
            return None, None
        
        # 창고 관련 키워드
        warehouse_keywords = [
            'DSV', 'Storage', 'MOSB', 'Hauler', 'Warehouse', 'WH', 
            'Indoor', 'Outdoor', 'Al Markaz', 'MZP', 'AAA'
        ]
        
        # 현장 관련 키워드
        site_keywords = [
            'Site', 'AGI', 'DAS', 'MIR', 'SHU', 'Station', 'Plant'
        ]
        
        warehouse_columns = []
        site_columns = []
        
        for col in self.combined_data.columns:
            col_lower = col.lower()
            
            # 창고 컬럼 확인
            if any(keyword.lower() in col_lower for keyword in warehouse_keywords):
                warehouse_columns.append(col)
            
            # 현장 컬럼 확인  
            if any(keyword.lower() in col_lower for keyword in site_keywords):
                site_columns.append(col)
        
        print(f"📦 창고 컬럼 ({len(warehouse_columns)}개):")
        for col in warehouse_columns:
            print(f"   - {col}")
        
        print(f"\n🏭 현장 컬럼 ({len(site_columns)}개):")
        for col in site_columns:
            print(f"   - {col}")
        
        return warehouse_columns, site_columns
    
    def analyze_flow_patterns(self):
        """물류 흐름 패턴 분석"""
        print("\n🔄 물류 흐름 패턴 분석")
        print("=" * 50)
        
        if self.combined_data is None:
            return
        
        warehouse_cols, site_cols = self.identify_warehouse_site_columns()
        
        if not warehouse_cols and not site_cols:
            print("❌ 창고/현장 컬럼을 찾을 수 없습니다.")
            return
        
        # 날짜 컬럼 변환
        date_columns = warehouse_cols + site_cols
        for col in date_columns:
            if col in self.combined_data.columns:
                self.combined_data[col] = pd.to_datetime(self.combined_data[col], errors='coerce')
        
        # WH_HANDLING 계산
        self.combined_data['WH_HANDLING'] = 0
        for col in warehouse_cols:
            if col in self.combined_data.columns:
                self.combined_data['WH_HANDLING'] += self.combined_data[col].notna().astype(int)
        
        # Flow Code 분포
        if 'WH_HANDLING' in self.combined_data.columns:
            flow_dist = self.combined_data['WH_HANDLING'].value_counts().sort_index()
            print(f"📊 WH_HANDLING 분포:")
            for code, count in flow_dist.items():
                percentage = count / len(self.combined_data) * 100
                print(f"   Code {code}: {count:,}건 ({percentage:.1f}%)")
        
        # 벤더별 Flow Code 분포
        if 'Vendor' in self.combined_data.columns:
            print(f"\n📊 벤더별 WH_HANDLING 분포:")
            vendor_flow = self.combined_data.groupby(['Vendor', 'WH_HANDLING']).size().unstack(fill_value=0)
            print(vendor_flow)
        
        return warehouse_cols, site_cols
    
    def create_real_data_report(self):
        """실제 데이터 기반 보고서 생성"""
        print("\n📊 실제 데이터 기반 보고서 생성")
        print("=" * 50)
        
        if self.combined_data is None:
            print("❌ 결합된 데이터가 없습니다.")
            return
        
        # 출력 파일명
        output_file = f"HVDC_Real_Data_Report_{self.timestamp}.xlsx"
        
        # 요약 통계
        summary_stats = {
            'Total_Records': len(self.combined_data),
            'HITACHI_Count': len(self.combined_data[self.combined_data['Vendor'] == 'HITACHI']) if 'Vendor' in self.combined_data.columns else 0,
            'SIMENSE_Count': len(self.combined_data[self.combined_data['Vendor'] == 'SIMENSE']) if 'Vendor' in self.combined_data.columns else 0,
            'Total_Columns': len(self.combined_data.columns),
            'Analysis_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"📈 요약 통계:")
        for key, value in summary_stats.items():
            print(f"   {key}: {value}")
        
        # Excel 파일 생성
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 전체 데이터
            self.combined_data.to_excel(writer, sheet_name='전체_실제_데이터', index=False)
            
            # HITACHI 데이터
            if self.hitachi_data is not None:
                self.hitachi_data.to_excel(writer, sheet_name='HITACHI_원본', index=False)
            
            # SIMENSE 데이터
            if self.simense_data is not None:
                self.simense_data.to_excel(writer, sheet_name='SIMENSE_원본', index=False)
            
            # INVOICE 데이터
            if self.invoice_data is not None:
                self.invoice_data.to_excel(writer, sheet_name='INVOICE_원본', index=False)
            
            # 요약 통계
            summary_df = pd.DataFrame([summary_stats])
            summary_df.to_excel(writer, sheet_name='요약_통계', index=False)
        
        print(f"✅ 보고서 생성 완료: {output_file}")
        return output_file
    
    def run_full_analysis(self):
        """전체 분석 실행"""
        print("🚀 실제 HVDC RAW DATA 전체 분석 실행")
        print("=" * 80)
        
        # 1. 데이터 로드
        self.load_real_data()
        
        # 2. 데이터 구조 분석
        self.analyze_data_structure()
        
        # 3. 공통 컬럼 찾기
        self.find_common_columns()
        
        # 4. 데이터 결합
        self.combine_data()
        
        # 5. 물류 흐름 패턴 분석
        self.analyze_flow_patterns()
        
        # 6. 보고서 생성
        output_file = self.create_real_data_report()
        
        print("\n" + "=" * 80)
        print("🎉 실제 HVDC RAW DATA 분석 완료!")
        print("=" * 80)
        print(f"📁 출력 파일: {output_file}")
        
        if self.combined_data is not None:
            print(f"📊 총 레코드: {len(self.combined_data):,}건")
            print(f"📊 총 컬럼: {len(self.combined_data.columns)}개")
            
            if 'Vendor' in self.combined_data.columns:
                vendor_counts = self.combined_data['Vendor'].value_counts()
                print(f"\n📊 벤더별 분포:")
                for vendor, count in vendor_counts.items():
                    percentage = count / len(self.combined_data) * 100
                    print(f"   {vendor}: {count:,}건 ({percentage:.1f}%)")
        
        return output_file

def main():
    """메인 실행"""
    analyzer = RealHVDCDataAnalyzer()
    result = analyzer.run_full_analysis()
    
    if result:
        print(f"\n🔧 추천 명령어:")
        print(f"📁 결과 파일 열기: start {result}")
        print(f"📊 데이터 구조 확인: 각 시트별 실제 데이터 검토")
        print(f"🎯 다음 단계: 실제 데이터 기반 Excel 시스템 구축")
    
    return result

if __name__ == "__main__":
    main() 