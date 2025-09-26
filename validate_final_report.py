#!/usr/bin/env python3
"""
최종 리포트 검증 스크립트
MACHO-GPT v3.4-mini | TDD 기반 최종 리포트 검증

목적:
1. 생성된 Excel 파일 구조 검증
2. 데이터 완전성 검증
3. Multi-level 헤더 검증
"""

import pandas as pd
import numpy as np
import os
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_final_report():
    """최종 리포트 검증"""
    logger.info("최종 리포트 검증 시작")
    
    # 가장 최근 생성된 리포트 파일 찾기
    report_files = [f for f in os.listdir('.') if f.startswith('HVDC_FINAL_REPORT_') and f.endswith('.xlsx')]
    
    if not report_files:
        raise FileNotFoundError("HVDC_FINAL_REPORT_*.xlsx 파일을 찾을 수 없습니다.")
    
    # 가장 최근 파일 선택
    latest_file = sorted(report_files)[-1]
    
    print("\n" + "="*80)
    print("HVDC 최종 리포트 검증")
    print("="*80)
    print(f"검증 파일: {latest_file}")
    
    # Excel 파일 로드
    excel_file = pd.ExcelFile(latest_file)
    sheet_names = excel_file.sheet_names
    
    print(f"\n[1] 기본 구조 검증")
    print("-" * 60)
    
    # 시트 개수 및 이름 검증
    expected_sheets = ['전체_트랜잭션_데이터', '창고_월별_입출고', '현장_월별_입고재고']
    
    print(f"시트 개수: {len(sheet_names)}개 (예상: 3개)")
    print(f"시트 목록: {sheet_names}")
    
    # 시트별 검증
    validation_results = {}
    
    for expected_sheet in expected_sheets:
        if expected_sheet in sheet_names:
            print(f"✅ '{expected_sheet}' 시트 존재")
            validation_results[expected_sheet] = True
        else:
            print(f"❌ '{expected_sheet}' 시트 누락")
            validation_results[expected_sheet] = False
    
    # 시트별 상세 검증
    print(f"\n[2] 시트별 상세 검증")
    print("-" * 60)
    
    # 시트1: 전체 트랜잭션 데이터 검증
    if '전체_트랜잭션_데이터' in sheet_names:
        sheet1_df = pd.read_excel(latest_file, sheet_name='전체_트랜잭션_데이터')
        
        print(f"\n📊 시트1: 전체_트랜잭션_데이터")
        print(f"  - 데이터: {len(sheet1_df):,}건")
        print(f"  - 컬럼: {len(sheet1_df.columns)}개")
        
        # 필수 컬럼 검증
        required_basic = ['no.', 'Case No.', 'Pkg', 'Site']
        required_analysis = ['WH_HANDLING', 'FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_PATTERN']
        required_meta = ['VENDOR', 'SOURCE_FILE', 'PROCESSED_AT', 'TRANSACTION_ID']
        
        missing_columns = []
        for col in required_basic + required_analysis + required_meta:
            if col not in sheet1_df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"  ❌ 누락된 필수 컬럼: {missing_columns}")
        else:
            print(f"  ✅ 모든 필수 컬럼 존재")
        
        # Flow Code 분포 확인
        if 'FLOW_CODE' in sheet1_df.columns:
            flow_dist = sheet1_df['FLOW_CODE'].value_counts().sort_index()
            print(f"  📈 Flow Code 분포: {flow_dist.to_dict()}")
            
            # 예상 분포와 비교
            total_records = len(sheet1_df)
            code2_pct = (flow_dist.get(2, 0) / total_records) * 100
            code3_pct = (flow_dist.get(3, 0) / total_records) * 100
            code1_pct = (flow_dist.get(1, 0) / total_records) * 100
            
            print(f"    Code 1: {flow_dist.get(1, 0):,}건 ({code1_pct:.1f}%)")
            print(f"    Code 2: {flow_dist.get(2, 0):,}건 ({code2_pct:.1f}%)")
            print(f"    Code 3: {flow_dist.get(3, 0):,}건 ({code3_pct:.1f}%)")
        
        # 데이터 소스 확인
        if 'VENDOR' in sheet1_df.columns:
            vendor_dist = sheet1_df['VENDOR'].value_counts()
            print(f"  📦 데이터 소스: {vendor_dist.to_dict()}")
    
    # 시트2: 창고 월별 입출고 검증
    if '창고_월별_입출고' in sheet_names:
        sheet2_df = pd.read_excel(latest_file, sheet_name='창고_월별_입출고')
        
        print(f"\n📊 시트2: 창고_월별_입출고")
        print(f"  - 데이터: {len(sheet2_df):,}건")
        print(f"  - 컬럼: {len(sheet2_df.columns)}개")
        
        # Multi-level 헤더 검증
        warehouse_columns = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA Storage', 
                           'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse']
        
        expected_warehouse_headers = []
        for warehouse in warehouse_columns:
            expected_warehouse_headers.extend([f"{warehouse}_입고", f"{warehouse}_출고"])
        
        found_warehouse_headers = [col for col in sheet2_df.columns if any(op in col for op in ['_입고', '_출고'])]
        
        print(f"  📋 Multi-level 헤더: {len(found_warehouse_headers)}개 발견")
        print(f"    예상: {len(expected_warehouse_headers)}개")
        
        if len(found_warehouse_headers) == len(expected_warehouse_headers):
            print(f"  ✅ Multi-level 헤더 구조 정확")
        else:
            print(f"  ❌ Multi-level 헤더 구조 불일치")
        
        # Total 행 확인
        if '월' in sheet2_df.columns:
            total_rows = sheet2_df[sheet2_df['월'] == 'Total']
            if len(total_rows) > 0:
                print(f"  ✅ Total 합계 행 존재")
            else:
                print(f"  ❌ Total 합계 행 누락")
    
    # 시트3: 현장 월별 입고재고 검증
    if '현장_월별_입고재고' in sheet_names:
        sheet3_df = pd.read_excel(latest_file, sheet_name='현장_월별_입고재고')
        
        print(f"\n📊 시트3: 현장_월별_입고재고")
        print(f"  - 데이터: {len(sheet3_df):,}건")
        print(f"  - 컬럼: {len(sheet3_df.columns)}개")
        
        # Multi-level 헤더 검증 (현장은 출고 없음)
        site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        expected_site_headers = []
        for site in site_columns:
            expected_site_headers.extend([f"{site}_입고", f"{site}_재고"])
        
        found_site_headers = [col for col in sheet3_df.columns if any(op in col for op in ['_입고', '_재고'])]
        outgoing_headers = [col for col in sheet3_df.columns if '_출고' in col]
        
        print(f"  📋 Multi-level 헤더: {len(found_site_headers)}개 발견")
        print(f"    예상: {len(expected_site_headers)}개")
        print(f"  🚫 출고 헤더: {len(outgoing_headers)}개 (0개여야 함)")
        
        if len(found_site_headers) == len(expected_site_headers) and len(outgoing_headers) == 0:
            print(f"  ✅ Multi-level 헤더 구조 정확 (현장은 출고 없음)")
        else:
            print(f"  ❌ Multi-level 헤더 구조 불일치")
    
    # 전체 검증 결과
    print(f"\n[3] 전체 검증 결과")
    print("-" * 60)
    
    total_validations = len(validation_results)
    passed_validations = sum(validation_results.values())
    
    print(f"검증 통과: {passed_validations}/{total_validations}개 시트")
    
    if passed_validations == total_validations:
        print(f"🎉 모든 검증 통과! 최종 리포트가 성공적으로 생성되었습니다.")
        confidence_score = 100
    else:
        print(f"⚠️ 일부 검증 실패. 리포트를 검토해주세요.")
        confidence_score = (passed_validations / total_validations) * 100
    
    # 품질 지표
    print(f"\n[4] 품질 지표")
    print("-" * 60)
    
    if '전체_트랜잭션_데이터' in sheet_names:
        sheet1_df = pd.read_excel(latest_file, sheet_name='전체_트랜잭션_데이터')
        
        quality_metrics = {
            'total_records': len(sheet1_df),
            'total_columns': len(sheet1_df.columns),
            'null_percentage': (sheet1_df.isnull().sum().sum() / (len(sheet1_df) * len(sheet1_df.columns))) * 100,
            'confidence_score': confidence_score
        }
        
        print(f"총 레코드: {quality_metrics['total_records']:,}건")
        print(f"총 컬럼: {quality_metrics['total_columns']}개")
        print(f"NULL 비율: {quality_metrics['null_percentage']:.1f}%")
        print(f"신뢰도: {quality_metrics['confidence_score']:.1f}%")
        
        # TDD 목표 달성도
        if quality_metrics['total_records'] >= 7700:
            print(f"✅ TDD 목표 달성: 7,700건 이상")
        else:
            print(f"❌ TDD 목표 미달: {quality_metrics['total_records']:,}건 < 7,700건")
        
        return quality_metrics
    
    return {'confidence_score': confidence_score}

if __name__ == "__main__":
    try:
        validation_results = validate_final_report()
        
        print(f"\n" + "="*80)
        print("✅ 최종 리포트 검증 완료!")
        print("="*80)
        print(f"신뢰도: {validation_results['confidence_score']:.1f}%")
        
        if validation_results['confidence_score'] >= 90:
            print("🎉 고품질 리포트 생성 성공!")
        elif validation_results['confidence_score'] >= 70:
            print("✅ 양호한 품질의 리포트 생성")
        else:
            print("⚠️ 품질 개선이 필요한 리포트")
        
    except Exception as e:
        logger.error(f"검증 중 오류 발생: {e}")
        print(f"오류: {e}") 