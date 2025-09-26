#!/usr/bin/env python3
"""
표준 데이터 스키마 정의 및 검증
- 표준화된 INVOICE 데이터 구조 정의
- 데이터 타입 및 제약 조건 검증
- 비즈니스 룰 검증
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

class DataType(Enum):
    """데이터 타입 정의"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"

class ValidationLevel(Enum):
    """검증 수준 정의"""
    CRITICAL = "critical"    # 필수 검증 (실패시 레코드 거부)
    WARNING = "warning"      # 경고 수준 (로그만 기록)
    INFO = "info"           # 정보성 (통계만 수집)

@dataclass
class FieldSchema:
    """필드 스키마 정의"""
    name: str
    data_type: DataType
    nullable: bool = True
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None
    pattern: Optional[str] = None
    business_rules: List[str] = field(default_factory=list)
    validation_level: ValidationLevel = ValidationLevel.WARNING
    description: str = ""

@dataclass 
class ValidationResult:
    """검증 결과"""
    field_name: str
    record_index: int
    validation_level: ValidationLevel
    is_valid: bool
    error_message: str = ""
    actual_value: Any = None
    expected_constraint: str = ""

class StandardDataSchemaValidator:
    """표준 데이터 스키마 검증기"""
    
    def __init__(self):
        """초기화 및 스키마 정의"""
        self.schema = self._define_standard_schema()
        self.validation_results = []
        self.summary_stats = {}
        
    def _define_standard_schema(self) -> Dict[str, FieldSchema]:
        """표준 HVDC INVOICE 스키마 정의"""
        
        schema = {
            # 1. 고유 식별자
            'record_id': FieldSchema(
                name='record_id',
                data_type=DataType.STRING,
                nullable=False,
                min_length=12,
                max_length=15,
                pattern=r'^HVDC_INV_\d{6}$',
                validation_level=ValidationLevel.CRITICAL,
                description='고유 레코드 식별자 (HVDC_INV_nnnnnn 형식)'
            ),
            
            # 2. 운영 월
            'operation_month': FieldSchema(
                name='operation_month',
                data_type=DataType.DATETIME,
                nullable=True,
                validation_level=ValidationLevel.WARNING,
                business_rules=['should_be_within_project_period'],
                description='화물 운영 발생 월'
            ),
            
            # 3. HVDC 프로젝트 코드
            'hvdc_project_code': FieldSchema(
                name='hvdc_project_code',
                data_type=DataType.CATEGORICAL,
                nullable=False,
                allowed_values=['HVDC', 'HVDC_PROJECT'],
                validation_level=ValidationLevel.CRITICAL,
                description='HVDC 프로젝트 식별 코드'
            ),
            
            # 4. 작업 유형
            'work_type': FieldSchema(
                name='work_type',
                data_type=DataType.CATEGORICAL,
                nullable=True,
                allowed_values=['ADOPT', 'HANDLING', 'STORAGE', 'TRANSFER', 'UNKNOWN'],
                validation_level=ValidationLevel.INFO,
                description='물류 작업 유형'
            ),
            
            # 5. 화물 유형 (표준화됨)
            'cargo_type': FieldSchema(
                name='cargo_type',
                data_type=DataType.CATEGORICAL,
                nullable=False,
                allowed_values=['HITACHI', 'SIEMENS', 'SAMSUNG_CT', 'SCHNEIDER', 'PRYSMIAN', 'MOELLER', 'ALL_RENTAL'],
                validation_level=ValidationLevel.CRITICAL,
                business_rules=['cargo_warehouse_consistency'],
                description='표준화된 화물 유형 (브랜드별)'
            ),
            
            # 6. 창고명 (표준화됨)
            'warehouse_name': FieldSchema(
                name='warehouse_name',
                data_type=DataType.CATEGORICAL,
                nullable=False,
                allowed_values=['DSV_OUTDOOR', 'DSV_INDOOR', 'DSV_AL_MARKAZ', 'DSV_MZP', 'AAA_STORAGE', 'SHIFTING'],
                validation_level=ValidationLevel.CRITICAL,
                business_rules=['warehouse_specialization_check'],
                description='표준화된 창고명'
            ),
            
            # 7. 패키지 수
            'package_count': FieldSchema(
                name='package_count',
                data_type=DataType.INTEGER,
                nullable=True,
                min_value=0,
                max_value=10000,
                validation_level=ValidationLevel.WARNING,
                business_rules=['package_amount_correlation'],
                description='화물 패키지 수'
            ),
            
            # 8. 중량 (kg)
            'weight_kg': FieldSchema(
                name='weight_kg',
                data_type=DataType.FLOAT,
                nullable=True,
                min_value=0.0,
                max_value=500000.0,  # 500톤 제한
                validation_level=ValidationLevel.INFO,
                business_rules=['weight_volume_consistency'],
                description='화물 중량 (킬로그램)'
            ),
            
            # 9. 부피 (CBM)
            'volume_cbm': FieldSchema(
                name='volume_cbm',
                data_type=DataType.FLOAT,
                nullable=True,
                min_value=0.0,
                max_value=10000.0,
                validation_level=ValidationLevel.INFO,
                description='화물 부피 (입방미터)'
            ),
            
            # 10. 면적 (SQM)
            'area_sqm': FieldSchema(
                name='area_sqm',
                data_type=DataType.FLOAT,
                nullable=True,
                min_value=0.0,
                max_value=50000.0,
                validation_level=ValidationLevel.WARNING,
                business_rules=['area_rent_correlation'],
                description='창고 점유 면적 (제곱미터)'
            ),
            
            # 11. 금액 (AED)
            'amount_aed': FieldSchema(
                name='amount_aed',
                data_type=DataType.FLOAT,
                nullable=True,
                min_value=0.0,
                max_value=1000000.0,  # 100만 AED 제한
                validation_level=ValidationLevel.CRITICAL,
                business_rules=['amount_reasonability_check'],
                description='청구 금액 (UAE 디르함)'
            ),
            
            # 12. 입고 핸들링
            'handling_in': FieldSchema(
                name='handling_in',
                data_type=DataType.FLOAT,
                nullable=True,
                min_value=0.0,
                validation_level=ValidationLevel.INFO,
                description='입고 핸들링 비용'
            ),
            
            # 13. 출고 핸들링
            'handling_out': FieldSchema(
                name='handling_out',
                data_type=DataType.FLOAT,
                nullable=True,
                min_value=0.0,
                validation_level=ValidationLevel.INFO,
                description='출고 핸들링 비용'
            ),
            
            # 14. 청구 월
            'billing_month': FieldSchema(
                name='billing_month',
                data_type=DataType.DATETIME,
                nullable=True,
                validation_level=ValidationLevel.WARNING,
                business_rules=['billing_operation_sequence'],
                description='청구 발생 월'
            ),
            
            # 15. 데이터 품질 점수
            'data_quality_score': FieldSchema(
                name='data_quality_score',
                data_type=DataType.FLOAT,
                nullable=False,
                min_value=0.0,
                max_value=1.0,
                validation_level=ValidationLevel.INFO,
                description='레코드 데이터 품질 점수 (0.0-1.0)'
            )
        }
        
        return schema
    
    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """데이터 전체 검증"""
        
        print("🔍 표준 데이터 스키마 검증 시작")
        print("=" * 50)
        
        self.validation_results = []
        validation_summary = {
            'total_records': len(data),
            'total_fields': len(self.schema),
            'validation_timestamp': datetime.now().isoformat(),
            'field_validation_results': {},
            'business_rule_results': {},
            'overall_quality_score': 0.0,
            'critical_errors': 0,
            'warnings': 0,
            'info_messages': 0
        }
        
        # 1. 스키마 구조 검증
        structure_result = self._validate_structure(data)
        validation_summary['structure_validation'] = structure_result
        
        # 2. 필드별 데이터 타입 및 제약 조건 검증
        for field_name, field_schema in self.schema.items():
            if field_name in data.columns:
                field_result = self._validate_field(data, field_name, field_schema)
                validation_summary['field_validation_results'][field_name] = field_result
        
        # 3. 비즈니스 룰 검증
        business_rules_result = self._validate_business_rules(data)
        validation_summary['business_rule_results'] = business_rules_result
        
        # 4. 전체 품질 점수 계산
        overall_score = self._calculate_overall_quality_score()
        validation_summary['overall_quality_score'] = overall_score
        
        # 5. 에러 통계
        critical_count = sum(1 for r in self.validation_results if r.validation_level == ValidationLevel.CRITICAL and not r.is_valid)
        warning_count = sum(1 for r in self.validation_results if r.validation_level == ValidationLevel.WARNING and not r.is_valid)
        info_count = sum(1 for r in self.validation_results if r.validation_level == ValidationLevel.INFO and not r.is_valid)
        
        validation_summary.update({
            'critical_errors': critical_count,
            'warnings': warning_count,  
            'info_messages': info_count
        })
        
        print(f"\n📊 검증 결과 요약:")
        print(f"  ✅ 전체 레코드: {validation_summary['total_records']:,}건")
        print(f"  ✅ 전체 필드: {validation_summary['total_fields']}개")
        print(f"  ✅ 전체 품질점수: {overall_score:.3f}")
        print(f"  ❌ 중요 오류: {critical_count:,}건")
        print(f"  ⚠️  경고: {warning_count:,}건")  
        print(f"  ℹ️  정보: {info_count:,}건")
        
        return validation_summary
    
    def _validate_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """데이터 구조 검증"""
        
        expected_columns = set(self.schema.keys())
        actual_columns = set(data.columns)
        
        missing_columns = expected_columns - actual_columns
        extra_columns = actual_columns - expected_columns
        matching_columns = expected_columns & actual_columns
        
        structure_result = {
            'expected_columns': len(expected_columns),
            'actual_columns': len(actual_columns),
            'matching_columns': len(matching_columns),
            'missing_columns': list(missing_columns),
            'extra_columns': list(extra_columns),
            'structure_compliance': len(matching_columns) / len(expected_columns) * 100
        }
        
        print(f"📋 구조 검증:")
        print(f"  예상 컬럼: {len(expected_columns)}개")
        print(f"  실제 컬럼: {len(actual_columns)}개")
        print(f"  일치 컬럼: {len(matching_columns)}개")
        print(f"  구조 준수율: {structure_result['structure_compliance']:.1f}%")
        
        if missing_columns:
            print(f"  ❌ 누락 컬럼: {', '.join(missing_columns)}")
        if extra_columns:
            print(f"  ➕ 추가 컬럼: {', '.join(extra_columns)}")
            
        return structure_result
    
    def _validate_field(self, data: pd.DataFrame, field_name: str, field_schema: FieldSchema) -> Dict[str, Any]:
        """개별 필드 검증"""
        
        field_data = data[field_name]
        field_result = {
            'field_name': field_name,
            'total_records': len(field_data),
            'null_count': field_data.isnull().sum(),
            'null_ratio': field_data.isnull().sum() / len(field_data),
            'valid_records': 0,
            'invalid_records': 0,
            'validation_errors': []
        }
        
        valid_count = 0
        invalid_count = 0
        
        for idx, value in field_data.items():
            is_valid, error_msg = self._validate_single_value(value, field_schema)
            
            if not is_valid:
                invalid_count += 1
                error_result = ValidationResult(
                    field_name=field_name,
                    record_index=idx,
                    validation_level=field_schema.validation_level,
                    is_valid=False,
                    error_message=error_msg,
                    actual_value=value
                )
                self.validation_results.append(error_result)
                field_result['validation_errors'].append({
                    'record_index': idx,
                    'error': error_msg,
                    'value': str(value)
                })
            else:
                valid_count += 1
        
        field_result.update({
            'valid_records': valid_count,
            'invalid_records': invalid_count,
            'validity_ratio': valid_count / len(field_data) if len(field_data) > 0 else 0
        })
        
        return field_result
    
    def _validate_single_value(self, value: Any, schema: FieldSchema) -> tuple[bool, str]:
        """단일 값 검증"""
        
        # NULL 값 검사
        if pd.isna(value):
            if not schema.nullable:
                return False, f"NULL 값이 허용되지 않음"
            return True, ""
        
        # 데이터 타입 검증
        if schema.data_type == DataType.STRING:
            if not isinstance(value, str):
                return False, f"문자열이 아님: {type(value)}"
            if schema.min_length and len(value) < schema.min_length:
                return False, f"최소 길이 {schema.min_length} 미달: {len(value)}"
            if schema.max_length and len(value) > schema.max_length:
                return False, f"최대 길이 {schema.max_length} 초과: {len(value)}"
            if schema.pattern:
                import re
                if not re.match(schema.pattern, value):
                    return False, f"패턴 미일치: {schema.pattern}"
                    
        elif schema.data_type == DataType.INTEGER:
            if not isinstance(value, (int, np.integer)):
                return False, f"정수가 아님: {type(value)}"
            if schema.min_value is not None and value < schema.min_value:
                return False, f"최소값 {schema.min_value} 미달: {value}"
            if schema.max_value is not None and value > schema.max_value:
                return False, f"최대값 {schema.max_value} 초과: {value}"
                
        elif schema.data_type == DataType.FLOAT:
            if not isinstance(value, (int, float, np.number)):
                return False, f"숫자가 아님: {type(value)}"
            float_value = float(value)
            if schema.min_value is not None and float_value < schema.min_value:
                return False, f"최소값 {schema.min_value} 미달: {float_value}"
            if schema.max_value is not None and float_value > schema.max_value:
                return False, f"최대값 {schema.max_value} 초과: {float_value}"
                
        elif schema.data_type == DataType.DATETIME:
            if not isinstance(value, (datetime, date, pd.Timestamp, np.datetime64)):
                return False, f"날짜형이 아님: {type(value)}"
                
        elif schema.data_type == DataType.CATEGORICAL:
            if schema.allowed_values and str(value) not in schema.allowed_values:
                return False, f"허용값 범위 벗어남: {value} (허용: {schema.allowed_values})"
        
        return True, ""
    
    def _validate_business_rules(self, data: pd.DataFrame) -> Dict[str, Any]:
        """비즈니스 룰 검증"""
        
        business_results = {
            'total_business_rules': 0,
            'passed_rules': 0,
            'failed_rules': 0,
            'rule_details': {}
        }
        
        # 1. 화물-창고 일치성 검증
        if 'cargo_type' in data.columns and 'warehouse_name' in data.columns:
            cargo_warehouse_result = self._check_cargo_warehouse_consistency(data)
            business_results['rule_details']['cargo_warehouse_consistency'] = cargo_warehouse_result
            business_results['total_business_rules'] += 1
            if cargo_warehouse_result['compliance_rate'] >= 0.8:
                business_results['passed_rules'] += 1
            else:
                business_results['failed_rules'] += 1
        
        # 2. 금액 합리성 검증
        if 'amount_aed' in data.columns and 'package_count' in data.columns:
            amount_reasonability_result = self._check_amount_reasonability(data)
            business_results['rule_details']['amount_reasonability'] = amount_reasonability_result
            business_results['total_business_rules'] += 1
            if amount_reasonability_result['reasonable_ratio'] >= 0.7:
                business_results['passed_rules'] += 1
            else:
                business_results['failed_rules'] += 1
        
        # 3. 창고 전문화 패턴 검증
        if 'warehouse_name' in data.columns and 'cargo_type' in data.columns:
            specialization_result = self._check_warehouse_specialization(data)
            business_results['rule_details']['warehouse_specialization'] = specialization_result
            business_results['total_business_rules'] += 1
            business_results['passed_rules'] += 1  # 정보성 검증
        
        print(f"\n🏢 비즈니스 룰 검증:")
        print(f"  전체 룰: {business_results['total_business_rules']}개")
        print(f"  통과 룰: {business_results['passed_rules']}개")
        print(f"  실패 룰: {business_results['failed_rules']}개")
        
        return business_results
    
    def _check_cargo_warehouse_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """화물-창고 일치성 검증"""
        
        # 전문화 규칙 정의
        specialization_rules = {
            'AAA_STORAGE': ['SCHNEIDER', 'PRYSMIAN'],  # 위험물 전용
            'DSV_AL_MARKAZ': ['ALL_RENTAL'],           # 렌탈 전용
            'DSV_INDOOR': ['HITACHI', 'SIEMENS'],      # 정밀기기 우선
        }
        
        consistent_count = 0
        total_count = 0
        violations = []
        
        for idx, row in data.iterrows():
            if pd.notna(row.get('warehouse_name')) and pd.notna(row.get('cargo_type')):
                warehouse = row['warehouse_name']
                cargo = row['cargo_type']
                total_count += 1
                
                if warehouse in specialization_rules:
                    allowed_cargo = specialization_rules[warehouse]
                    if cargo in allowed_cargo:
                        consistent_count += 1
                    else:
                        violations.append({
                            'record_index': idx,
                            'warehouse': warehouse,
                            'cargo': cargo,
                            'allowed': allowed_cargo
                        })
                else:
                    consistent_count += 1  # 특별 규칙이 없는 창고는 일치로 간주
        
        compliance_rate = consistent_count / total_count if total_count > 0 else 0
        
        return {
            'total_checked': total_count,
            'consistent_records': consistent_count,
            'violations': len(violations),
            'compliance_rate': compliance_rate,
            'violation_details': violations[:10]  # 상위 10개만 표시
        }
    
    def _check_amount_reasonability(self, data: pd.DataFrame) -> Dict[str, Any]:
        """금액 합리성 검증"""
        
        reasonable_count = 0
        total_count = 0
        outliers = []
        
        # 패키지당 평균 금액 계산
        valid_data = data[(data['amount_aed'].notna()) & (data['package_count'].notna()) & (data['package_count'] > 0)]
        
        if len(valid_data) > 0:
            per_package_amounts = valid_data['amount_aed'] / valid_data['package_count']
            median_per_package = per_package_amounts.median()
            q1 = per_package_amounts.quantile(0.25)
            q3 = per_package_amounts.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            for idx, row in valid_data.iterrows():
                total_count += 1
                per_package = row['amount_aed'] / row['package_count']
                
                if lower_bound <= per_package <= upper_bound:
                    reasonable_count += 1
                else:
                    outliers.append({
                        'record_index': idx,
                        'amount_aed': row['amount_aed'],
                        'package_count': row['package_count'],
                        'per_package': per_package,
                        'expected_range': f"{lower_bound:.2f} - {upper_bound:.2f}"
                    })
        
        reasonable_ratio = reasonable_count / total_count if total_count > 0 else 0
        
        return {
            'total_checked': total_count,
            'reasonable_records': reasonable_count,
            'outliers': len(outliers),
            'reasonable_ratio': reasonable_ratio,
            'median_per_package': median_per_package if len(valid_data) > 0 else 0,
            'outlier_details': outliers[:10]
        }
    
    def _check_warehouse_specialization(self, data: pd.DataFrame) -> Dict[str, Any]:
        """창고 전문화 패턴 분석"""
        
        if 'warehouse_name' not in data.columns or 'cargo_type' not in data.columns:
            return {}
        
        specialization_analysis = {}
        
        for warehouse in data['warehouse_name'].unique():
            if pd.notna(warehouse):
                warehouse_data = data[data['warehouse_name'] == warehouse]
                cargo_distribution = warehouse_data['cargo_type'].value_counts(normalize=True)
                
                specialization_analysis[warehouse] = {
                    'total_records': len(warehouse_data),
                    'cargo_distribution': cargo_distribution.to_dict(),
                    'primary_cargo': cargo_distribution.index[0] if len(cargo_distribution) > 0 else None,
                    'specialization_ratio': cargo_distribution.iloc[0] if len(cargo_distribution) > 0 else 0
                }
        
        return specialization_analysis
    
    def _calculate_overall_quality_score(self) -> float:
        """전체 품질 점수 계산"""
        
        if not self.validation_results:
            return 1.0
        
        total_validations = len(self.validation_results)
        critical_failures = sum(1 for r in self.validation_results 
                              if r.validation_level == ValidationLevel.CRITICAL and not r.is_valid)
        warning_failures = sum(1 for r in self.validation_results 
                             if r.validation_level == ValidationLevel.WARNING and not r.is_valid)
        
        # 가중치 적용: CRITICAL 0.7, WARNING 0.3
        penalty = (critical_failures * 0.7 + warning_failures * 0.3) / total_validations
        quality_score = max(0.0, 1.0 - penalty)
        
        return quality_score
    
    def export_validation_report(self, validation_summary: Dict[str, Any], output_path: str = None) -> str:
        """검증 결과 리포트 출력"""
        
        output_path = output_path or f"스키마_검증_리포트_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            
            # 1. 검증 요약
            summary_df = pd.DataFrame([{
                '항목': '전체 레코드 수',
                '값': validation_summary['total_records'],
                '단위': '건'
            }, {
                '항목': '전체 필드 수',
                '값': validation_summary['total_fields'],
                '단위': '개'
            }, {
                '항목': '전체 품질점수',
                '값': f"{validation_summary['overall_quality_score']:.3f}",
                '단위': '점'
            }, {
                '항목': '중요 오류',
                '값': validation_summary['critical_errors'],
                '단위': '건'
            }, {
                '항목': '경고',
                '값': validation_summary['warnings'],
                '단위': '건'
            }])
            summary_df.to_excel(writer, sheet_name='검증_요약', index=False)
            
            # 2. 필드별 검증 결과
            field_results = []
            for field_name, result in validation_summary['field_validation_results'].items():
                field_results.append({
                    '필드명': field_name,
                    '전체레코드': result['total_records'],
                    '유효레코드': result['valid_records'],
                    '무효레코드': result['invalid_records'],
                    '유효율': f"{result['validity_ratio']:.1%}",
                    '결측률': f"{result['null_ratio']:.1%}"
                })
            
            if field_results:
                fields_df = pd.DataFrame(field_results)
                fields_df.to_excel(writer, sheet_name='필드별_검증', index=False)
            
            # 3. 비즈니스 룰 검증 결과
            if validation_summary.get('business_rule_results'):
                business_results = []
                for rule_name, result in validation_summary['business_rule_results']['rule_details'].items():
                    if isinstance(result, dict) and 'compliance_rate' in result:
                        business_results.append({
                            '비즈니스룰': rule_name,
                            '검증대상': result.get('total_checked', 0),
                            '준수건수': result.get('consistent_records', 0),
                            '위반건수': result.get('violations', 0),
                            '준수율': f"{result['compliance_rate']:.1%}"
                        })
                
                if business_results:
                    business_df = pd.DataFrame(business_results)
                    business_df.to_excel(writer, sheet_name='비즈니스룰_검증', index=False)
        
        print(f"📄 검증 리포트 출력 완료: {output_path}")
        return output_path

def main():
    """메인 실행 함수"""
    
    print("🎯 표준 데이터 스키마 검증 시작")
    print("=" * 60)
    
    try:
        # 1. 검증기 초기화
        validator = StandardDataSchemaValidator()
        
        # 2. 표준화된 데이터 로드
        standardized_file = "HVDC_표준화_INVOICE_20250702_145255.xlsx"
        data = pd.read_excel(standardized_file, sheet_name='Cleaned_Data')
        
        print(f"📂 표준화 데이터 로드: {len(data):,}건")
        
        # 3. 스키마 검증 실행
        validation_result = validator.validate_data(data)
        
        # 4. 검증 리포트 출력
        report_file = validator.export_validation_report(validation_result)
        
        print(f"\n🏆 스키마 검증 완료!")
        print(f"  ✅ 리포트 파일: {report_file}")
        print(f"  ✅ 전체 품질점수: {validation_result['overall_quality_score']:.3f}")
        
        return validation_result, report_file
        
    except Exception as e:
        print(f"\n❌ 스키마 검증 실패: {e}")
        raise

if __name__ == "__main__":
    result, report = main()
    
    print(f"\n🔧 **추천 명령어:**")
    print(f"/analyze_quality_gaps [품질 격차 분석]")
    print(f"/optimize_data_quality [데이터 품질 최적화]")
    print(f"/validate_business_rules [비즈니스 룰 강화]") 