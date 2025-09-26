#!/usr/bin/env python3
"""
실제 HVDC 데이터를 사용한 온톨로지 통합 테스트
- 실제 INVOICE 데이터 로드
- 온톨로지 매핑 시스템과 통합 검증
- 기존 시스템과의 호환성 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import json
from ontology_integrated_schema_validator import OntologyIntegratedSchemaValidator

def load_hvdc_data():
    """실제 HVDC 데이터 로드"""
    data_files = [
        "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx", 
        "hvdc_ontology_system/data/HVDC WAREHOUSE_INVOICE.xlsx"
    ]
    
    all_data = pd.DataFrame()
    loaded_files = []
    
    for file_path in data_files:
        if Path(file_path).exists():
            try:
                print(f"📁 로드 중: {file_path}")
                df = pd.read_excel(file_path)
                df['data_source'] = Path(file_path).stem
                all_data = pd.concat([all_data, df], ignore_index=True)
                loaded_files.append(file_path)
                print(f"✅ {len(df)}건 로드 완료")
            except Exception as e:
                print(f"❌ {file_path} 로드 실패: {e}")
                
    return all_data, loaded_files

def standardize_hvdc_columns(df):
    """HVDC 데이터 컬럼 표준화"""
    # 컬럼명 매핑 (기존 → 표준)
    column_mapping = {
        'Category': 'warehouse_name',
        'HVDC CODE 3': 'cargo_type', 
        'HVDC CODE 1': 'hvdc_project_code',
        'Package No.': 'package_count',
        'IMG No.': 'image_count',
        'Net Weight (kg)': 'weight_kg',
        'SQM': 'area_sqm',
        'Total (AED)': 'amount_aed',
        'Operation Month': 'operation_month',
        'wh handling': 'wh_handling',
        'flow code': 'flow_code'
    }
    
    # 컬럼명 변경
    df_standardized = df.rename(columns=column_mapping)
    
    # 표준 컬럼 추가 (누락된 컬럼들)
    standard_columns = [
        'record_id', 'operation_month', 'hvdc_project_code', 'work_type',
        'cargo_type', 'warehouse_name', 'package_count', 'weight_kg',
        'volume_cbm', 'area_sqm', 'amount_aed', 'handling_in', 'handling_out',
        'rent', 'flow_code', 'wh_handling'
    ]
    
    for col in standard_columns:
        if col not in df_standardized.columns:
            if col == 'record_id':
                df_standardized[col] = [f'HVDC_INV_{i:06d}' for i in range(len(df_standardized))]
            elif col == 'work_type':
                # SQM이 있으면 STORAGE, 없으면 HANDLING으로 추정
                df_standardized[col] = df_standardized.apply(
                    lambda row: 'STORAGE' if pd.notna(row.get('area_sqm', 0)) and row.get('area_sqm', 0) > 0 else 'HANDLING',
                    axis=1
                )
            elif col == 'volume_cbm':
                df_standardized[col] = 0.0
            elif col in ['handling_in', 'handling_out']:
                df_standardized[col] = 0.0
            elif col == 'rent':
                # 전체 금액에서 핸들링 비용 제외한 나머지를 임대료로 추정
                total_amount = df_standardized.get('amount_aed', 0)
                estimated_handling = total_amount * 0.15  # 15% 핸들링 추정
                df_standardized[col] = total_amount - estimated_handling
            else:
                df_standardized[col] = None
                
    # 창고명 표준화
    warehouse_mapping = {
        'DSV Outdoor': 'DSV_OUTDOOR',
        'DSV Indoor': 'DSV_INDOOR', 
        'DSV Al Markaz': 'DSV_AL_MARKAZ',
        'DSV MZP': 'DSV_MZP',
        'AAA Storage': 'AAA_STORAGE'
    }
    
    if 'warehouse_name' in df_standardized.columns:
        df_standardized['warehouse_name'] = df_standardized['warehouse_name'].replace(warehouse_mapping)
    
    # 화물 타입 표준화
    cargo_mapping = {
        'HE': 'HITACHI',
        'SIM': 'SIEMENS',
        'SCT': 'SAMSUNG_CT',
        'PRP': 'PRYSMIAN',
        'MOE': 'MOELLER'
    }
    
    if 'cargo_type' in df_standardized.columns:
        df_standardized['cargo_type'] = df_standardized['cargo_type'].replace(cargo_mapping)
    
    return df_standardized

def analyze_ontology_compatibility(validation_results):
    """온톨로지 호환성 분석"""
    print("\n" + "="*70)
    print("🔍 **온톨로지 호환성 분석**")
    print("="*70)
    
    # 기본 검증 결과
    basic_validation = {
        'total_records': validation_results.get('total_records', 0),
        'validation_rate': validation_results.get('validation_rate', 0),
        'quality_score': validation_results.get('overall_quality_score', 0)
    }
    
    print(f"📊 **기본 스키마 검증:**")
    print(f"   총 레코드: {basic_validation['total_records']:,}건")
    print(f"   검증 성공률: {basic_validation['validation_rate']:.1f}%")
    print(f"   품질 점수: {basic_validation['quality_score']:.1f}%")
    
    # 온톨로지 매핑 결과 (RDF 기능이 활성화된 경우)
    if 'ontology_mapping' in validation_results:
        ontology_mapping = validation_results['ontology_mapping']
        print(f"\n🔗 **온톨로지 매핑 결과:**")
        print(f"   매핑 성공률: {ontology_mapping.get('mapping_success_rate', 0):.1f}%")
        print(f"   매핑 오류: {len(ontology_mapping.get('mapping_errors', []))}건")
        
        # 시맨틱 분류 분석
        semantic_classes = ontology_mapping.get('semantic_classifications', {})
        if semantic_classes:
            print(f"   시맨틱 분류: {len(semantic_classes)}개 클래스")
            for class_name, count in sorted(semantic_classes.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     - {class_name}: {count}건")
    
    # 비즈니스 룰 검증
    if 'business_rules' in validation_results:
        business_rules = validation_results['business_rules']
        print(f"\n📋 **비즈니스 룰 검증:**")
        print(f"   전체 룰: {business_rules.get('total_rules', 0)}개")
        print(f"   통과 룰: {business_rules.get('passed_rules', 0)}개")
        print(f"   실패 룰: {business_rules.get('failed_rules', 0)}개")
    
    # 호환성 점수 계산
    compatibility_score = 0
    max_score = 100
    
    # 기본 검증 점수 (40%)
    if basic_validation['validation_rate'] > 80:
        compatibility_score += 40
    elif basic_validation['validation_rate'] > 60:
        compatibility_score += 30
    elif basic_validation['validation_rate'] > 40:
        compatibility_score += 20
    
    # 온톨로지 매핑 점수 (40%)
    if 'ontology_mapping' in validation_results:
        mapping_rate = validation_results['ontology_mapping'].get('mapping_success_rate', 0)
        if mapping_rate > 90:
            compatibility_score += 40
        elif mapping_rate > 70:
            compatibility_score += 30
        elif mapping_rate > 50:
            compatibility_score += 20
    else:
        compatibility_score += 20  # RDF 기능 비활성화시 기본 점수
    
    # 품질 점수 (20%)
    if basic_validation['quality_score'] > 80:
        compatibility_score += 20
    elif basic_validation['quality_score'] > 60:
        compatibility_score += 15
    elif basic_validation['quality_score'] > 40:
        compatibility_score += 10
    
    print(f"\n🎯 **전체 호환성 점수: {compatibility_score}/{max_score} ({compatibility_score}%)**")
    
    # 호환성 등급
    if compatibility_score >= 90:
        grade = "A+ (완전 호환)"
        color = "🟢"
    elif compatibility_score >= 80:
        grade = "A (우수 호환)"
        color = "🟢"
    elif compatibility_score >= 70:
        grade = "B (양호 호환)"
        color = "🟡"
    elif compatibility_score >= 60:
        grade = "C (보통 호환)"
        color = "🟡"
    else:
        grade = "D (호환성 개선 필요)"
        color = "🔴"
    
    print(f"{color} **호환성 등급: {grade}**")
    
    return compatibility_score

def main():
    """메인 함수"""
    print("🔄 MACHO-GPT v3.4-mini 실제 데이터 온톨로지 통합 테스트")
    print("=" * 70)
    
    # 1. 실제 데이터 로드
    print("📂 실제 HVDC 데이터 로드 중...")
    hvdc_data, loaded_files = load_hvdc_data()
    
    if hvdc_data.empty:
        print("❌ 실제 데이터를 로드할 수 없습니다. 테스트를 종료합니다.")
        return
    
    print(f"✅ 총 {len(hvdc_data)}건 데이터 로드 완료")
    print(f"📁 로드된 파일: {len(loaded_files)}개")
    
    # 2. 데이터 표준화
    print("\n🔄 데이터 표준화 중...")
    standardized_data = standardize_hvdc_columns(hvdc_data)
    
    # 표준화 결과 요약
    print(f"✅ 표준화 완료:")
    print(f"   원본 컬럼: {len(hvdc_data.columns)}개")
    print(f"   표준 컬럼: {len(standardized_data.columns)}개")
    
    # 3. 온톨로지 통합 검증기 초기화
    print("\n🏗️ 온톨로지 통합 검증기 초기화...")
    validator = OntologyIntegratedSchemaValidator(enable_ontology=True)
    
    # 4. 온톨로지 통합 검증 실행
    print("\n🔍 온톨로지 통합 검증 실행...")
    validation_results = validator.validate_with_ontology(standardized_data)
    
    # 5. 결과 분석
    compatibility_score = analyze_ontology_compatibility(validation_results)
    
    # 6. 리포트 생성
    try:
        report_path = validator.export_ontology_report(validation_results)
        print(f"\n📄 **상세 리포트 생성:** {report_path}")
    except Exception as e:
        print(f"\n⚠️ 리포트 생성 실패: {e}")
    
    # 7. 최종 요약
    print("\n" + "="*70)
    print("📋 **MACHO-GPT v3.4-mini 온톨로지 통합 테스트 완료**")
    print("="*70)
    
    print(f"📊 **테스트 결과:**")
    print(f"   처리 데이터: {len(standardized_data):,}건")
    print(f"   데이터 소스: {len(loaded_files)}개 파일")
    print(f"   호환성 점수: {compatibility_score}%")
    print(f"   온톨로지 상태: {'활성화' if validator.enable_ontology else '비활성화 (RDF 라이브러리 필요)'}")
    
    if 'rdf_graph_path' in validation_results:
        print(f"   RDF 그래프: {validation_results['rdf_graph_path']}")
    
    print(f"\n📊 **Status:** {compatibility_score:.1f}% | Ontology_Integration_Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🔧 **추천 명령어:**")
    print("/logi_master [통합 온톨로지 기반 물류 최적화]")
    print("/switch_mode LATTICE [고급 온톨로지 추론 실행]")
    print("/visualize_data [시맨틱 분류 및 호환성 결과 시각화]")
    
    return compatibility_score

if __name__ == "__main__":
    main() 