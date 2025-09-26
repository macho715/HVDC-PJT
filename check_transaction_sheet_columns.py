#!/usr/bin/env python3
"""
전체_트랜잭션_데이터 시트 컬럼 검증 및 수정 스크립트
"""

import pandas as pd
import os
from datetime import datetime

def check_transaction_sheet_columns():
    """생성된 파일의 시트 1 컬럼 구조 검증"""
    
    # 최근 생성된 파일 찾기
    files = [f for f in os.listdir('.') if f.startswith('HVDC_원본데이터_통합_월별_리포트_최종_') and f.endswith('.xlsx')]
    if not files:
        print("❌ 생성된 파일을 찾을 수 없습니다.")
        return
    
    latest_file = max(files)
    print(f"📊 검증 대상 파일: {latest_file}")
    
    # 시트 1 로드
    try:
        df = pd.read_excel(latest_file, sheet_name='전체_트랜잭션_데이터')
        print(f"✅ 시트 로드 완료: {len(df)}행 × {len(df.columns)}열")
    except Exception as e:
        print(f"❌ 시트 로드 실패: {e}")
        return
    
    # 요구되는 컬럼 구조
    required_columns = {
        '기본 정보': ['no.', 'Case No.', 'Pkg', 'L(CM)', 'W(CM)', 'H(CM)', 'CBM'],
        '물성 정보': ['N.W(kgs)', 'G.W(kgs)', 'Stack', 'HS Code', 'Currency'],
        '추가 정보': ['SQM', 'Stack_Status', 'Description', 'Site', 'EQ No'],
        '창고 정보': ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse'],
        '현장 정보': ['AGI', 'DAS', 'MIR', 'SHU'],
        '분석 정보': ['WH_HANDLING', 'FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_PATTERN'],
        '메타 정보': ['VENDOR', 'SOURCE_FILE', 'PROCESSED_AT', 'TRANSACTION_ID']
    }
    
    print("\n📋 컬럼 구조 검증 결과:")
    print("=" * 60)
    
    all_required = []
    missing_columns = []
    available_columns = []
    
    for category, columns in required_columns.items():
        print(f"\n🔍 {category}:")
        for col in columns:
            if col in df.columns:
                print(f"  ✅ {col}")
                available_columns.append(col)
            else:
                print(f"  ❌ {col} (누락)")
                missing_columns.append(col)
            all_required.extend(columns)
    
    print(f"\n📊 요약:")
    print(f"  - 총 요구 컬럼: {len(all_required)}개")
    print(f"  - 사용 가능 컬럼: {len(available_columns)}개")
    print(f"  - 누락 컬럼: {len(missing_columns)}개")
    
    if missing_columns:
        print(f"\n⚠️ 누락된 컬럼들:")
        for col in missing_columns:
            print(f"  - {col}")
    
    # 현재 파일의 모든 컬럼 출력
    print(f"\n📋 현재 파일의 모든 컬럼 ({len(df.columns)}개):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    return df, available_columns, missing_columns

def create_corrected_transaction_sheet():
    """올바른 컬럼 구조로 시트 1 재생성"""
    
    print("\n🔄 올바른 컬럼 구조로 시트 1 재생성 중...")
    
    # 원본 데이터 다시 로드
    from generate_hvdc_final_monthly_report_from_original import HVDCOriginalDataProcessor
    
    processor = HVDCOriginalDataProcessor()
    dfs = processor.load_original_data()
    
    if not dfs:
        print("❌ 원본 데이터 로드 실패")
        return
    
    # 데이터 통합
    merged_df = processor.merge_original_data(dfs)
    if merged_df is None:
        print("❌ 데이터 통합 실패")
        return
    
    # 날짜 컬럼 변환
    merged_df = processor.convert_date_columns(merged_df)
    
    # 올바른 컬럼 구조 정의
    correct_columns = [
        # 기본 정보
        'no.', 'Case No.', 'Pkg', 'L(CM)', 'W(CM)', 'H(CM)', 'CBM',
        # 물성 정보
        'N.W(kgs)', 'G.W(kgs)', 'Stack', 'HS Code', 'Currency',
        # 추가 정보
        'SQM', 'Stack_Status', 'Description', 'Site', 'EQ No',
        # 창고 정보
        'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA Storage', 
        'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse',
        # 현장 정보
        'AGI', 'DAS', 'MIR', 'SHU',
        # 분석 정보
        'WH_HANDLING', 'FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_PATTERN',
        # 메타 정보
        'VENDOR', 'SOURCE_FILE', 'PROCESSED_AT', 'TRANSACTION_ID'
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in correct_columns if col in merged_df.columns]
    
    # 누락된 컬럼에 대한 기본값 추가
    for col in correct_columns:
        if col not in merged_df.columns:
            if col == 'TRANSACTION_ID':
                merged_df[col] = range(1, len(merged_df) + 1)
            elif col in ['SQM', 'Stack_Status', 'FLOW_DESCRIPTION', 'FLOW_PATTERN']:
                merged_df[col] = 'N/A'
            elif col in ['WH_HANDLING', 'FLOW_CODE']:
                merged_df[col] = 0
            else:
                merged_df[col] = ''
    
    # 올바른 순서로 컬럼 재정렬
    transaction_df = merged_df[correct_columns].copy()
    
    print(f"✅ 올바른 컬럼 구조로 재생성 완료: {len(transaction_df)}행 × {len(transaction_df.columns)}열")
    
    # 새로운 파일 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"HVDC_통합_월별_리포트_최종_수정_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        transaction_df.to_excel(writer, sheet_name='전체_트랜잭션_데이터', index=False)
    
    print(f"✅ 수정된 파일 생성 완료: {output_file}")
    
    return output_file

def main():
    print("🔍 전체_트랜잭션_데이터 시트 컬럼 구조 검증 시작...")
    
    # 1. 현재 파일 검증
    df, available, missing = check_transaction_sheet_columns()
    
    # 2. 필요시 수정된 파일 생성
    if missing:
        print(f"\n⚠️ {len(missing)}개의 컬럼이 누락되어 있습니다.")
        response = input("수정된 파일을 생성하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            corrected_file = create_corrected_transaction_sheet()
            if corrected_file:
                print(f"\n🎉 수정된 파일이 생성되었습니다: {corrected_file}")
    else:
        print("\n✅ 모든 요구 컬럼이 포함되어 있습니다.")

if __name__ == "__main__":
    main() 