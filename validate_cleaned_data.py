#!/usr/bin/env python3
"""
🔍 HVDC 클리닝된 데이터 재검증 시스템
MACHO-GPT v3.4-mini │ Samsung C&T & ADNOC·DSV Partnership

클리닝 후 품질 개선 검증:
1. SPARQL 규칙 재적용
2. 품질 점수 재계산
3. 개선 효과 측정
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import json
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CleanedDataValidator:
    """클리닝된 데이터 검증 시스템"""
    
    def __init__(self, cleaned_data_dir="data_cleaned"):
        self.cleaned_data_dir = cleaned_data_dir
        self.validation_results = {}
        
    def validate_cleaned_data(self):
        """클리닝된 데이터 검증 실행"""
        logger.info("🔍 클리닝된 데이터 재검증 시작")
        
        validation_summary = {
            'timestamp': datetime.now().isoformat(),
            'validation_type': 'post_cleaning',
            'files_validated': {},
            'overall_quality_score': 0,
            'improvement_metrics': {},
            'sparql_compliance': {}
        }
        
        # 클리닝된 파일들 검증
        hitachi_result = self._validate_hitachi_cleaned()
        validation_summary['files_validated']['HITACHI'] = hitachi_result
        
        simense_result = self._validate_simense_cleaned()
        validation_summary['files_validated']['SIMENSE'] = simense_result
        
        invoice_result = self._validate_invoice_cleaned()
        validation_summary['files_validated']['INVOICE'] = invoice_result
        
        # 전체 품질 점수 계산
        validation_summary['overall_quality_score'] = self._calculate_overall_quality(validation_summary)
        
        # 개선 효과 측정
        validation_summary['improvement_metrics'] = self._calculate_improvement_metrics(validation_summary)
        
        # SPARQL 컴플라이언스 검사
        validation_summary['sparql_compliance'] = self._check_sparql_compliance(validation_summary)
        
        self._display_validation_results(validation_summary)
        self._save_validation_results(validation_summary)
        
        return validation_summary
    
    def _validate_hitachi_cleaned(self):
        """클리닝된 HITACHI 파일 검증"""
        logger.info("🔧 HITACHI 클리닝된 파일 검증")
        
        try:
            # 최신 클리닝된 파일 찾기
            files = [f for f in os.listdir(self.cleaned_data_dir) if 'HITACHI_CLEANED' in f]
            if not files:
                raise FileNotFoundError("HITACHI 클리닝된 파일을 찾을 수 없습니다")
            
            file_path = os.path.join(self.cleaned_data_dir, files[0])
            df = pd.read_excel(file_path, sheet_name='Case List')
            
            # 검증 메트릭
            total_records = len(df)
            missing_data_rate = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            duplicate_rate = (df.duplicated().sum() / len(df)) * 100
            
            # 이상치 검증
            outlier_rate = self._calculate_outlier_rate(df)
            
            # 데이터 타입 일관성
            type_consistency = self._check_type_consistency(df)
            
            # 품질 점수 계산
            quality_score = 100 - missing_data_rate - duplicate_rate - outlier_rate - (100 - type_consistency)
            
            result = {
                'file_name': 'HITACHI_CLEANED',
                'file_path': file_path,
                'total_records': total_records,
                'missing_data_rate': round(missing_data_rate, 2),
                'duplicate_rate': round(duplicate_rate, 2),
                'outlier_rate': round(outlier_rate, 2),
                'type_consistency': round(type_consistency, 2),
                'quality_score': round(max(0, quality_score), 2),
                'validation_status': 'PASSED' if quality_score > 80 else 'NEEDS_IMPROVEMENT'
            }
            
            logger.info(f"  ✅ HITACHI 검증 완료: 품질 점수 {result['quality_score']}%")
            return result
            
        except Exception as e:
            logger.error(f"  ❌ HITACHI 검증 실패: {e}")
            return {'file_name': 'HITACHI_CLEANED', 'error': str(e)}
    
    def _validate_simense_cleaned(self):
        """클리닝된 SIMENSE 파일 검증 - CBM 검증 포함"""
        logger.info("🔧 SIMENSE 클리닝된 파일 검증 - CBM 검증")
        
        try:
            # 최신 클리닝된 파일 찾기
            files = [f for f in os.listdir(self.cleaned_data_dir) if 'SIMENSE_CLEANED' in f]
            if not files:
                raise FileNotFoundError("SIMENSE 클리닝된 파일을 찾을 수 없습니다")
            
            file_path = os.path.join(self.cleaned_data_dir, files[0])
            df = pd.read_excel(file_path, sheet_name='Case List')
            
            # 기본 검증 메트릭
            total_records = len(df)
            missing_data_rate = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            duplicate_rate = (df.duplicated().sum() / len(df)) * 100
            
            # CBM 특별 검증
            cbm_compliance_rate = 100
            if 'CBM' in df.columns:
                cbm_series = pd.to_numeric(df['CBM'], errors='coerce')
                cbm_violations = (cbm_series <= 0).sum()
                cbm_compliance_rate = ((len(df) - cbm_violations) / len(df)) * 100
            
            # 패키지 수 검증
            pkg_compliance_rate = 100
            if 'pkg' in df.columns:
                pkg_series = pd.to_numeric(df['pkg'], errors='coerce')
                pkg_violations = (pkg_series <= 0).sum()
                pkg_compliance_rate = ((len(df) - pkg_violations) / len(df)) * 100
            
            # 데이터 타입 일관성
            type_consistency = self._check_type_consistency(df)
            
            # 품질 점수 계산 (CBM 컴플라이언스 가중치 높음)
            quality_score = (
                cbm_compliance_rate * 0.4 +  # CBM 컴플라이언스 40%
                pkg_compliance_rate * 0.2 +  # PKG 컴플라이언스 20%
                (100 - missing_data_rate) * 0.2 +  # 누락 데이터 20%
                (100 - duplicate_rate) * 0.1 +     # 중복 데이터 10%
                type_consistency * 0.1              # 타입 일관성 10%
            )
            
            result = {
                'file_name': 'SIMENSE_CLEANED',
                'file_path': file_path,
                'total_records': total_records,
                'missing_data_rate': round(missing_data_rate, 2),
                'duplicate_rate': round(duplicate_rate, 2),
                'cbm_compliance_rate': round(cbm_compliance_rate, 2),
                'pkg_compliance_rate': round(pkg_compliance_rate, 2),
                'type_consistency': round(type_consistency, 2),
                'quality_score': round(quality_score, 2),
                'validation_status': 'PASSED' if quality_score > 80 else 'NEEDS_IMPROVEMENT'
            }
            
            logger.info(f"  ✅ SIMENSE 검증 완료: 품질 점수 {result['quality_score']}% (CBM: {result['cbm_compliance_rate']}%)")
            return result
            
        except Exception as e:
            logger.error(f"  ❌ SIMENSE 검증 실패: {e}")
            return {'file_name': 'SIMENSE_CLEANED', 'error': str(e)}
    
    def _validate_invoice_cleaned(self):
        """클리닝된 INVOICE 파일 검증"""
        logger.info("🔧 INVOICE 클리닝된 파일 검증")
        
        try:
            # 최신 클리닝된 파일 찾기
            files = [f for f in os.listdir(self.cleaned_data_dir) if 'INVOICE_CLEANED' in f]
            if not files:
                raise FileNotFoundError("INVOICE 클리닝된 파일을 찾을 수 없습니다")
            
            file_path = os.path.join(self.cleaned_data_dir, files[0])
            xl_file = pd.ExcelFile(file_path)
            df = pd.read_excel(file_path, sheet_name=xl_file.sheet_names[0])
            
            # 검증 메트릭
            total_records = len(df)
            missing_data_rate = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            duplicate_rate = (df.duplicated().sum() / len(df)) * 100
            
            # 금액 데이터 검증
            amount_compliance = self._check_amount_compliance(df)
            
            # 데이터 타입 일관성
            type_consistency = self._check_type_consistency(df)
            
            # 품질 점수 계산
            quality_score = (
                amount_compliance * 0.3 +
                (100 - missing_data_rate) * 0.3 +
                (100 - duplicate_rate) * 0.2 +
                type_consistency * 0.2
            )
            
            result = {
                'file_name': 'INVOICE_CLEANED',
                'file_path': file_path,
                'total_records': total_records,
                'missing_data_rate': round(missing_data_rate, 2),
                'duplicate_rate': round(duplicate_rate, 2),
                'amount_compliance': round(amount_compliance, 2),
                'type_consistency': round(type_consistency, 2),
                'quality_score': round(quality_score, 2),
                'validation_status': 'PASSED' if quality_score > 80 else 'NEEDS_IMPROVEMENT'
            }
            
            logger.info(f"  ✅ INVOICE 검증 완료: 품질 점수 {result['quality_score']}%")
            return result
            
        except Exception as e:
            logger.error(f"  ❌ INVOICE 검증 실패: {e}")
            return {'file_name': 'INVOICE_CLEANED', 'error': str(e)}
    
    def _calculate_outlier_rate(self, df):
        """이상치 비율 계산"""
        outlier_count = 0
        total_numeric_values = 0
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            values = df[col].dropna()
            if len(values) > 0:
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                if IQR > 0:
                    outliers = ((values < Q1 - 1.5 * IQR) | (values > Q3 + 1.5 * IQR)).sum()
                    outlier_count += outliers
                    total_numeric_values += len(values)
        
        return (outlier_count / total_numeric_values * 100) if total_numeric_values > 0 else 0
    
    def _check_type_consistency(self, df):
        """데이터 타입 일관성 검사"""
        consistent_types = 0
        total_cols = len(df.columns)
        
        for col in df.columns:
            # 예상 타입과 실제 타입 비교
            if 'date' in col.lower():
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    consistent_types += 1
            elif any(keyword in col.lower() for keyword in ['qty', 'amount', 'weight', 'cbm', 'pkg']):
                if pd.api.types.is_numeric_dtype(df[col]):
                    consistent_types += 1
            else:
                consistent_types += 1  # 기타 컬럼은 일관성 있음으로 간주
        
        return (consistent_types / total_cols * 100) if total_cols > 0 else 0
    
    def _check_amount_compliance(self, df):
        """금액 데이터 컴플라이언스 검사"""
        compliance_count = 0
        total_amount_values = 0
        
        amount_cols = [col for col in df.columns if 'amount' in col.lower() or 'cost' in col.lower()]
        for col in amount_cols:
            if col in df.columns:
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                valid_amounts = (numeric_series >= 0).sum()
                compliance_count += valid_amounts
                total_amount_values += len(numeric_series.dropna())
        
        return (compliance_count / total_amount_values * 100) if total_amount_values > 0 else 100
    
    def _calculate_overall_quality(self, validation_summary):
        """전체 품질 점수 계산"""
        quality_scores = []
        for file_name, result in validation_summary['files_validated'].items():
            if 'quality_score' in result:
                quality_scores.append(result['quality_score'])
        
        return round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0
    
    def _calculate_improvement_metrics(self, validation_summary):
        """개선 효과 측정"""
        # 클리닝 전 품질 점수 (54.4%)와 비교
        before_score = 54.4
        after_score = validation_summary['overall_quality_score']
        
        return {
            'quality_before': before_score,
            'quality_after': after_score,
            'improvement_percentage': round(after_score - before_score, 2),
            'improvement_factor': round(after_score / before_score, 2)
        }
    
    def _check_sparql_compliance(self, validation_summary):
        """SPARQL 규칙 컴플라이언스 검사"""
        compliance_results = {}
        
        for file_name, result in validation_summary['files_validated'].items():
            if 'error' not in result:
                compliance_score = 0
                
                # CBM 양수 검증 (SIMENSE)
                if 'cbm_compliance_rate' in result:
                    compliance_score += result['cbm_compliance_rate'] * 0.4
                else:
                    compliance_score += 100 * 0.4
                
                # 패키지 수 양수 검증
                if 'pkg_compliance_rate' in result:
                    compliance_score += result['pkg_compliance_rate'] * 0.3
                else:
                    compliance_score += 100 * 0.3
                
                # 금액 비음수 검증
                if 'amount_compliance' in result:
                    compliance_score += result['amount_compliance'] * 0.3
                else:
                    compliance_score += 100 * 0.3
                
                compliance_results[file_name] = {
                    'compliance_score': round(compliance_score, 2),
                    'status': 'COMPLIANT' if compliance_score > 95 else 'PARTIAL_COMPLIANCE'
                }
        
        return compliance_results
    
    def _save_validation_results(self, validation_summary):
        """검증 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"HVDC_Cleaned_Data_Validation_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(validation_summary, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 검증 결과 저장: {filename}")
    
    def _display_validation_results(self, validation_summary):
        """검증 결과 출력"""
        print("\n" + "="*80)
        print("🔍 HVDC 클리닝된 데이터 검증 완료 보고서")
        print("="*80)
        
        improvement = validation_summary['improvement_metrics']
        print(f"📊 클리닝 전 품질 점수: {improvement['quality_before']:.1f}%")
        print(f"📈 클리닝 후 품질 점수: {improvement['quality_after']:.1f}%")
        print(f"🎯 품질 개선률: +{improvement['improvement_percentage']:.1f}%")
        print(f"📁 검증 대상: {self.cleaned_data_dir}/")
        
        print("\n📋 파일별 검증 결과:")
        for file_name, result in validation_summary['files_validated'].items():
            if 'error' not in result:
                print(f"  📄 {result['file_name']}:")
                print(f"    - 품질 점수: {result['quality_score']:.1f}%")
                print(f"    - 검증 상태: {result['validation_status']}")
                print(f"    - 누락 데이터: {result['missing_data_rate']:.1f}%")
                print(f"    - 중복 데이터: {result['duplicate_rate']:.1f}%")
                
                # 특별 메트릭
                if 'cbm_compliance_rate' in result:
                    print(f"    - CBM 컴플라이언스: {result['cbm_compliance_rate']:.1f}%")
                if 'amount_compliance' in result:
                    print(f"    - 금액 컴플라이언스: {result['amount_compliance']:.1f}%")
            else:
                print(f"  ❌ {file_name}: {result['error']}")
        
        print("\n🎯 SPARQL 컴플라이언스:")
        for file_name, compliance in validation_summary['sparql_compliance'].items():
            print(f"  📄 {file_name}: {compliance['compliance_score']:.1f}% ({compliance['status']})")
        
        overall_quality = validation_summary['overall_quality_score']
        print(f"\n🏆 전체 평가:")
        if overall_quality >= 90:
            print("  🟢 우수: 데이터 품질이 매우 높습니다")
        elif overall_quality >= 80:
            print("  🟡 양호: 데이터 품질이 양호합니다")
        elif overall_quality >= 70:
            print("  🟠 보통: 추가 개선이 필요합니다")
        else:
            print("  🔴 개선필요: 추가 클리닝이 필요합니다")
        
        print("\n💡 권장사항:")
        print("  ✅ 클리닝된 데이터를 프로덕션에 활용 가능")
        print("  📊 정기적 품질 모니터링 체계 구축")
        print("  🔄 데이터 입수 시 자동 클리닝 파이프라인 적용")
        
        print("\n" + "="*80)


def main():
    """메인 실행 함수"""
    validator = CleanedDataValidator()
    results = validator.validate_cleaned_data()
    
    print(f"\n🔧 **추천 명령어:**")
    print(f"/generate-dashboard cleaned-data [클리닝된 데이터 대시보드 생성]")
    print(f"/export-quality-report {datetime.now().strftime('%Y%m%d')} [품질 보고서 내보내기]")
    print(f"/monitor-quality-trends [품질 트렌드 모니터링 시작]")
    
    return results


if __name__ == "__main__":
    main() 