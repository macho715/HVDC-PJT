#!/usr/bin/env python3
"""
INVOICE 데이터 클리너
- TDD 테스트 통과 기반 표준화 구현
- 실제 데이터 구조 반영 (465건, 7,416,327 AED)
- 중복 제거, 누락값 처리, 컬럼 표준화
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class InvoiceDataCleaner:
    """INVOICE 데이터 표준화 클리너"""
    
    def __init__(self, config=None):
        """초기화"""
        self.config = config or self._default_config()
        self.cleaning_log = []
        self.quality_metrics = {}
        
    def _default_config(self):
        """기본 설정"""
        return {
            'file_path': r"C:\HVDC PJT\hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_INVOICE_.xlsx",
            'output_path': 'cleaned_invoice_data.xlsx',
            'quality_threshold': 0.85,
            'amount_tolerance': 0.05,
            'warehouse_mapping': {
                'DSV Outdoor': 'DSV_OUTDOOR',
                'DSV Indoor': 'DSV_INDOOR', 
                'DSV Al Markaz': 'DSV_AL_MARKAZ',
                'DSV MZP': 'DSV_MZP',
                'AAA Storage': 'AAA_STORAGE',
                'Shifting': 'SHIFTING'
            },
            'cargo_type_mapping': {
                'HE': 'HITACHI',
                'SIM': 'SIEMENS',
                'SCT': 'SAMSUNG_CT',
                'SEI': 'SCHNEIDER',
                'PPL': 'PRYSMIAN',
                'MOSB': 'MOELLER',
                'ALL': 'ALL_RENTAL'
            },
            'standard_columns': [
                'record_id',           # 고유 식별자
                'operation_month',     # 운영 월
                'hvdc_project_code',   # HVDC 프로젝트 코드
                'work_type',          # 작업 유형 (HVDC CODE 2)
                'cargo_type',         # 화물 유형 (표준화)
                'warehouse_name',     # 창고명 (표준화)
                'package_count',      # 패키지 수
                'weight_kg',          # 중량 (kg)
                'volume_cbm',         # 부피 (CBM)
                'area_sqm',           # 면적 (SQM)
                'amount_aed',         # 금액 (AED)
                'handling_in',        # 입고 핸들링
                'handling_out',       # 출고 핸들링
                'billing_month',      # 청구 월
                'data_quality_score'  # 데이터 품질 점수
            ]
        }
    
    def load_raw_data(self):
        """원본 데이터 로드"""
        try:
            self.raw_data = pd.read_excel(self.config['file_path'])
            self._log(f"원본 데이터 로드 성공: {len(self.raw_data):,}건")
            return self.raw_data
            
        except Exception as e:
            self._log(f"데이터 로드 실패: {e}", level='ERROR')
            raise
    
    def analyze_data_quality(self):
        """데이터 품질 분석"""
        if self.raw_data is None:
            raise ValueError("원본 데이터를 먼저 로드해주세요")
            
        quality_report = {
            'total_records': len(self.raw_data),
            'total_columns': len(self.raw_data.columns),
            'duplicate_records': self.raw_data.duplicated().sum(),
            'null_analysis': {},
            'data_type_analysis': {},
            'value_distribution': {}
        }
        
        # 결측값 분석
        for col in self.raw_data.columns:
            null_count = self.raw_data[col].isnull().sum()
            null_ratio = null_count / len(self.raw_data)
            quality_report['null_analysis'][col] = {
                'null_count': null_count,
                'null_ratio': null_ratio,
                'status': 'CRITICAL' if null_ratio > 0.5 else 'WARNING' if null_ratio > 0.1 else 'OK'
            }
        
        # 핵심 컬럼 분석
        key_columns = ['Category', 'HVDC CODE 3', 'Amount', 'pkg']
        for col in key_columns:
            if col in self.raw_data.columns:
                values = self.raw_data[col].dropna()
                if len(values) > 0:
                    if col == 'Amount':
                        quality_report['value_distribution'][col] = {
                            'total_amount': values.sum(),
                            'avg_amount': values.mean(),
                            'valid_records': len(values)
                        }
                    elif col == 'pkg':
                        quality_report['value_distribution'][col] = {
                            'total_packages': values.sum(),
                            'avg_packages': values.mean(),
                            'valid_records': len(values)
                        }
                    else:
                        quality_report['value_distribution'][col] = values.value_counts().to_dict()
        
        self.quality_metrics = quality_report
        self._log(f"데이터 품질 분석 완료: 품질 점수 계산됨")
        
        return quality_report
    
    def clean_and_standardize(self):
        """데이터 정리 및 표준화"""
        if self.raw_data is None:
            raise ValueError("원본 데이터를 먼저 로드해주세요")
            
        cleaned_data = self.raw_data.copy()
        
        # 1. 중복 제거
        duplicates_before = cleaned_data.duplicated().sum()
        cleaned_data = cleaned_data.drop_duplicates()
        duplicates_removed = duplicates_before - cleaned_data.duplicated().sum()
        self._log(f"중복 제거: {duplicates_removed}건 제거됨")
        
        # 2. 표준 컬럼 생성
        standardized_data = pd.DataFrame()
        
        # 고유 식별자 생성
        standardized_data['record_id'] = ['HVDC_INV_' + str(i+1).zfill(6) for i in range(len(cleaned_data))]
        
        # 운영 월 표준화
        if 'Operation Month' in cleaned_data.columns:
            standardized_data['operation_month'] = pd.to_datetime(cleaned_data['Operation Month'], errors='coerce')
        
        # 프로젝트 코드 (HVDC CODE 1)
        if 'HVDC CODE 1' in cleaned_data.columns:
            standardized_data['hvdc_project_code'] = cleaned_data['HVDC CODE 1'].fillna('HVDC')
        
        # 작업 유형 (HVDC CODE 2)
        if 'HVDC CODE 2' in cleaned_data.columns:
            standardized_data['work_type'] = cleaned_data['HVDC CODE 2'].fillna('UNKNOWN')
        
        # 화물 유형 표준화 (HVDC CODE 3)
        if 'HVDC CODE 3' in cleaned_data.columns:
            cargo_mapping = self.config['cargo_type_mapping']
            standardized_data['cargo_type'] = cleaned_data['HVDC CODE 3'].map(cargo_mapping).fillna(cleaned_data['HVDC CODE 3'])
        
        # 창고명 표준화 (Category)
        if 'Category' in cleaned_data.columns:
            warehouse_mapping = self.config['warehouse_mapping']
            standardized_data['warehouse_name'] = cleaned_data['Category']
            for original, standard in warehouse_mapping.items():
                mask = standardized_data['warehouse_name'].str.contains(original, na=False)
                standardized_data.loc[mask, 'warehouse_name'] = standard
        
        # 수치 데이터 정리
        numeric_columns = {
            'pkg': 'package_count',
            'Weight (kg)': 'weight_kg',
            'CBM': 'volume_cbm',
            'Sqm': 'area_sqm',
            'Amount': 'amount_aed',
            'Handling In': 'handling_in',
            'Handling out': 'handling_out'
        }
        
        for original_col, standard_col in numeric_columns.items():
            if original_col in cleaned_data.columns:
                # 수치형으로 변환, 오류시 NaN
                numeric_values = pd.to_numeric(cleaned_data[original_col], errors='coerce')
                # 음수값 처리 (절댓값으로 변환)
                numeric_values = numeric_values.abs()
                # 이상치 처리 (99.9 percentile 기준)
                if len(numeric_values.dropna()) > 0:
                    upper_limit = numeric_values.quantile(0.999)
                    numeric_values = numeric_values.clip(upper=upper_limit)
                
                standardized_data[standard_col] = numeric_values
        
        # 청구 월
        if 'Billing month' in cleaned_data.columns:
            standardized_data['billing_month'] = pd.to_datetime(cleaned_data['Billing month'], errors='coerce')
        
        # 3. 데이터 품질 점수 계산
        standardized_data['data_quality_score'] = self._calculate_quality_scores(standardized_data)
        
        # 4. 품질 기준 미달 레코드 표시
        low_quality_threshold = self.config['quality_threshold']
        low_quality_count = sum(standardized_data['data_quality_score'] < low_quality_threshold)
        self._log(f"품질 기준 미달 레코드: {low_quality_count}건 ({low_quality_count/len(standardized_data)*100:.1f}%)")
        
        self.cleaned_data = standardized_data
        self._log(f"데이터 표준화 완료: {len(standardized_data):,}건")
        
        return standardized_data
    
    def _calculate_quality_scores(self, data):
        """레코드별 데이터 품질 점수 계산"""
        scores = []
        
        for idx, row in data.iterrows():
            score = 1.0  # 최대 점수 1.0
            
            # 필수 필드 완성도 (60%)
            essential_fields = ['cargo_type', 'warehouse_name', 'amount_aed', 'package_count']
            essential_completeness = sum(pd.notna(row[field]) for field in essential_fields if field in row.index) / len(essential_fields)
            score *= (0.6 * essential_completeness + 0.4)  # 최소 40% 보장
            
            # 수치 데이터 유효성 (30%)
            numeric_fields = ['amount_aed', 'package_count', 'weight_kg', 'volume_cbm']
            valid_numeric = 0
            total_numeric = 0
            for field in numeric_fields:
                if field in row.index:
                    total_numeric += 1
                    if pd.notna(row[field]) and row[field] > 0:
                        valid_numeric += 1
            
            if total_numeric > 0:
                numeric_score = valid_numeric / total_numeric
                score *= (0.7 + 0.3 * numeric_score)  # 최소 70% 보장
            
            # 논리적 일관성 (10%)
            consistency_score = 1.0
            
            # 창고와 화물 유형 일치성 확인
            if pd.notna(row.get('warehouse_name')) and pd.notna(row.get('cargo_type')):
                warehouse = row['warehouse_name']
                cargo = row['cargo_type']
                
                # AAA Storage는 위험물만
                if warehouse == 'AAA_STORAGE' and cargo not in ['SCHNEIDER', 'PRYSMIAN']:
                    consistency_score *= 0.8
                
                # DSV Al Markaz는 주로 ALL_RENTAL
                if warehouse == 'DSV_AL_MARKAZ' and cargo != 'ALL_RENTAL':
                    consistency_score *= 0.9
            
            score *= consistency_score
            scores.append(min(score, 1.0))  # 최대값 1.0 제한
        
        return scores
    
    def generate_summary_report(self):
        """정리 요약 리포트 생성"""
        if self.cleaned_data is None:
            raise ValueError("데이터 정리를 먼저 실행해주세요")
            
        report = {
            'processing_timestamp': datetime.now().isoformat(),
            'data_summary': {
                'original_records': len(self.raw_data),
                'cleaned_records': len(self.cleaned_data),
                'records_removed': len(self.raw_data) - len(self.cleaned_data),
                'data_retention_rate': len(self.cleaned_data) / len(self.raw_data) * 100
            },
            'quality_summary': {
                'avg_quality_score': self.cleaned_data['data_quality_score'].mean(),
                'high_quality_records': sum(self.cleaned_data['data_quality_score'] >= 0.9),
                'medium_quality_records': sum((self.cleaned_data['data_quality_score'] >= 0.7) & (self.cleaned_data['data_quality_score'] < 0.9)),
                'low_quality_records': sum(self.cleaned_data['data_quality_score'] < 0.7)
            },
            'business_summary': {},
            'cleaning_log': self.cleaning_log
        }
        
        # 비즈니스 요약
        if 'amount_aed' in self.cleaned_data.columns:
            valid_amounts = self.cleaned_data['amount_aed'].dropna()
            report['business_summary']['total_amount'] = valid_amounts.sum()
            report['business_summary']['avg_amount'] = valid_amounts.mean()
            report['business_summary']['amount_records'] = len(valid_amounts)
        
        if 'package_count' in self.cleaned_data.columns:
            valid_packages = self.cleaned_data['package_count'].dropna()
            report['business_summary']['total_packages'] = valid_packages.sum()
            report['business_summary']['avg_packages'] = valid_packages.mean()
            report['business_summary']['package_records'] = len(valid_packages)
        
        # 창고별 분포
        if 'warehouse_name' in self.cleaned_data.columns:
            warehouse_dist = self.cleaned_data['warehouse_name'].value_counts().to_dict()
            report['business_summary']['warehouse_distribution'] = warehouse_dist
        
        # 화물 유형별 분포
        if 'cargo_type' in self.cleaned_data.columns:
            cargo_dist = self.cleaned_data['cargo_type'].value_counts().to_dict()
            report['business_summary']['cargo_distribution'] = cargo_dist
        
        return report
    
    def export_cleaned_data(self, output_path=None):
        """정리된 데이터 및 리포트 Excel 출력"""
        if self.cleaned_data is None:
            raise ValueError("데이터 정리를 먼저 실행해주세요")
            
        output_path = output_path or f"HVDC_표준화_INVOICE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 메인 정리된 데이터
            self.cleaned_data.to_excel(writer, sheet_name='Cleaned_Data', index=False)
            
            # 품질 분석
            quality_df = pd.DataFrame([{
                '품질구분': '높음 (≥0.9)',
                '레코드수': sum(self.cleaned_data['data_quality_score'] >= 0.9),
                '비율': f"{sum(self.cleaned_data['data_quality_score'] >= 0.9) / len(self.cleaned_data) * 100:.1f}%"
            }, {
                '품질구분': '중간 (0.7-0.9)',
                '레코드수': sum((self.cleaned_data['data_quality_score'] >= 0.7) & (self.cleaned_data['data_quality_score'] < 0.9)),
                '비율': f"{sum((self.cleaned_data['data_quality_score'] >= 0.7) & (self.cleaned_data['data_quality_score'] < 0.9)) / len(self.cleaned_data) * 100:.1f}%"
            }, {
                '품질구분': '낮음 (<0.7)',
                '레코드수': sum(self.cleaned_data['data_quality_score'] < 0.7),
                '비율': f"{sum(self.cleaned_data['data_quality_score'] < 0.7) / len(self.cleaned_data) * 100:.1f}%"
            }])
            quality_df.to_excel(writer, sheet_name='Quality_Analysis', index=False)
            
            # 창고별 요약
            if 'warehouse_name' in self.cleaned_data.columns:
                warehouse_summary = self.cleaned_data.groupby('warehouse_name').agg({
                    'record_id': 'count',
                    'amount_aed': ['sum', 'mean'],
                    'package_count': ['sum', 'mean'],
                    'data_quality_score': 'mean'
                }).round(2)
                warehouse_summary.to_excel(writer, sheet_name='Warehouse_Summary')
            
            # 화물 유형별 요약
            if 'cargo_type' in self.cleaned_data.columns:
                cargo_summary = self.cleaned_data.groupby('cargo_type').agg({
                    'record_id': 'count',
                    'amount_aed': ['sum', 'mean'],
                    'package_count': ['sum', 'mean'],
                    'data_quality_score': 'mean'
                }).round(2)
                cargo_summary.to_excel(writer, sheet_name='Cargo_Summary')
            
            # 정리 로그
            log_df = pd.DataFrame(self.cleaning_log)
            log_df.to_excel(writer, sheet_name='Cleaning_Log', index=False)
        
        self._log(f"데이터 및 리포트 출력 완료: {output_path}")
        return output_path
    
    def _log(self, message, level='INFO'):
        """로깅"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.cleaning_log.append(log_entry)
        print(f"[{timestamp}] {level}: {message}")

def main():
    """메인 실행"""
    print("🧹 HVDC INVOICE 데이터 표준화 시작")
    print("=" * 60)
    
    try:
        # 클리너 초기화
        cleaner = InvoiceDataCleaner()
        
        # 1. 원본 데이터 로드
        print("\n📂 1단계: 원본 데이터 로드")
        raw_data = cleaner.load_raw_data()
        
        # 2. 데이터 품질 분석
        print("\n📊 2단계: 데이터 품질 분석")
        quality_report = cleaner.analyze_data_quality()
        
        # 3. 데이터 정리 및 표준화
        print("\n🔧 3단계: 데이터 정리 및 표준화")
        cleaned_data = cleaner.clean_and_standardize()
        
        # 4. 요약 리포트 생성
        print("\n📋 4단계: 요약 리포트 생성")
        summary_report = cleaner.generate_summary_report()
        
        # 5. 결과 출력
        print("\n💾 5단계: 결과 출력")
        output_file = cleaner.export_cleaned_data()
        
        # 최종 요약
        print(f"\n🏆 표준화 완료!")
        print(f"  ✅ 원본 레코드: {summary_report['data_summary']['original_records']:,}건")
        print(f"  ✅ 정리 레코드: {summary_report['data_summary']['cleaned_records']:,}건")
        print(f"  ✅ 데이터 보존율: {summary_report['data_summary']['data_retention_rate']:.1f}%")
        print(f"  ✅ 평균 품질점수: {summary_report['quality_summary']['avg_quality_score']:.3f}")
        print(f"  ✅ 출력 파일: {output_file}")
        
        # 비즈니스 요약
        if 'total_amount' in summary_report['business_summary']:
            print(f"  💰 총 금액: {summary_report['business_summary']['total_amount']:,.2f} AED")
        if 'total_packages' in summary_report['business_summary']:
            print(f"  📦 총 패키지: {summary_report['business_summary']['total_packages']:,.0f}건")
        
        return output_file, summary_report
        
    except Exception as e:
        print(f"\n❌ 표준화 실패: {e}")
        raise

if __name__ == "__main__":
    result_file, report = main()
    
    print(f"\n🔧 **추천 명령어:**")
    print(f"/validate_cleaned_data [정리된 데이터 검증]")
    print(f"/compare_before_after [정리 전후 비교]")
    print(f"/generate_business_insights [비즈니스 인사이트 생성]") 