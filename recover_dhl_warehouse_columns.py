#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DHL Warehouse 컬럼 복구 스크립트
누락된 DHL Warehouse 및 관련 컬럼들 복구
"""

import pandas as pd
from datetime import datetime

def recover_dhl_warehouse_columns():
    """DHL Warehouse 컬럼 복구"""
    
    print("🔧 DHL Warehouse 컬럼 복구 시작")
    print("=" * 60)
    
    # 원본 데이터 로드
    hitachi_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_HITACHI(HE).xlsx'
    simense_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    used_data_path = r'MACHO_통합관리_20250702_205301\01_원본파일\MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    
    print("📊 데이터 로드 중...")
    df_hitachi = pd.read_excel(hitachi_path)
    df_simense = pd.read_excel(simense_path)
    df_used = pd.read_excel(used_data_path)
    
    print(f"✅ HITACHI 원본: {df_hitachi.shape[0]}행, {df_hitachi.shape[1]}컬럼")
    print(f"✅ SIMENSE 원본: {df_simense.shape[0]}행, {df_simense.shape[1]}컬럼")
    print(f"✅ 사용된 데이터: {df_used.shape[0]}행, {df_used.shape[1]}컬럼")
    
    # 누락된 컬럼 확인
    missing_cols = ['DHL Warehouse', 'Stack_Status', '열2']
    
    print("\n🔍 누락된 컬럼 상태 확인:")
    for col in missing_cols:
        in_hitachi = col in df_hitachi.columns
        in_simense = col in df_simense.columns
        in_used = col in df_used.columns
        
        print(f"  {col}: HITACHI({in_hitachi}) SIMENSE({in_simense}) 사용됨({in_used})")
    
    # 매칭 키 컬럼 확인
    matching_cols = []
    for col in ['no.', 'Shipment Invoice No.', 'HVDC CODE', 'HVDC CODE 1']:
        if col in df_hitachi.columns and col in df_used.columns:
            matching_cols.append(col)
    
    print(f"\n📋 매칭 키 컬럼: {matching_cols}")
    
    # DHL Warehouse 컬럼 복구
    if 'DHL Warehouse' in df_hitachi.columns and 'DHL Warehouse' not in df_used.columns:
        print("\n🔧 DHL Warehouse 컬럼 복구 시작...")
        
        # DHL Warehouse 데이터 추출
        dhl_mapping = df_hitachi[matching_cols + ['DHL Warehouse']].copy()
        dhl_mapping = dhl_mapping.drop_duplicates(subset=matching_cols)
        
        print(f"📊 DHL Warehouse 매핑 테이블: {dhl_mapping.shape[0]}행")
        
        # 샘플 데이터 확인
        print("\n📋 DHL Warehouse 샘플 데이터:")
        sample_data = df_hitachi['DHL Warehouse'].head(10)
        print(f"  {sample_data.tolist()}")
        
        # 데이터 타입 및 통계 확인
        print(f"\n📊 DHL Warehouse 데이터 분석:")
        print(f"  - 데이터 타입: {df_hitachi['DHL Warehouse'].dtype}")
        print(f"  - 유효 데이터: {df_hitachi['DHL Warehouse'].notna().sum()}개")
        print(f"  - 누락 데이터: {df_hitachi['DHL Warehouse'].isna().sum()}개")
        
        # 고유값 확인
        unique_values = df_hitachi['DHL Warehouse'].dropna().unique()
        print(f"  - 고유값 개수: {len(unique_values)}")
        if len(unique_values) <= 20:
            print(f"  - 고유값들: {unique_values}")
        
        # 사용된 데이터와 매칭
        df_result = df_used.merge(dhl_mapping, on=matching_cols, how='left')
        
        print(f"\n✅ DHL Warehouse 복구 완료")
        print(f"  - 결과 데이터: {df_result.shape[0]}행, {df_result.shape[1]}컬럼")
        
        if 'DHL Warehouse' in df_result.columns:
            matched_count = df_result['DHL Warehouse'].notna().sum()
            print(f"  - 복구된 DHL Warehouse 데이터: {matched_count}개")
    
    # Stack_Status 컬럼 복구
    if 'Stack_Status' in df_hitachi.columns and 'Stack_Status' not in df_used.columns:
        print("\n🔧 Stack_Status 컬럼 복구 시작...")
        
        stack_mapping = df_hitachi[matching_cols + ['Stack_Status']].copy()
        stack_mapping = stack_mapping.drop_duplicates(subset=matching_cols)
        
        df_result = df_result.merge(stack_mapping, on=matching_cols, how='left')
        
        print(f"✅ Stack_Status 복구 완료")
        if 'Stack_Status' in df_result.columns:
            stack_count = df_result['Stack_Status'].notna().sum()
            print(f"  - 복구된 Stack_Status 데이터: {stack_count}개")
    
    # 열2 컬럼 복구
    if '열2' in df_hitachi.columns and '열2' not in df_used.columns:
        print("\n🔧 열2 컬럼 복구 시작...")
        
        col2_mapping = df_hitachi[matching_cols + ['열2']].copy()
        col2_mapping = col2_mapping.drop_duplicates(subset=matching_cols)
        
        df_result = df_result.merge(col2_mapping, on=matching_cols, how='left')
        
        print(f"✅ 열2 복구 완료")
        if '열2' in df_result.columns:
            col2_count = df_result['열2'].notna().sum()
            print(f"  - 복구된 열2 데이터: {col2_count}개")
    
    # 최종 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'HVDC_DHL_Warehouse_전체복구완료_{timestamp}.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 시트 1: 복구된 전체 데이터
        df_result.to_excel(writer, sheet_name='DHL_복구완료_전체데이터', index=False)
        
        # 시트 2: DHL Warehouse 분석
        if 'DHL Warehouse' in df_result.columns:
            dhl_analysis = df_result.groupby('DHL Warehouse').size().reset_index(name='count')
            dhl_analysis.to_excel(writer, sheet_name='DHL_Warehouse_분석', index=False)
        
        # 시트 3: 복구 전후 비교
        comparison_data = {
            '구분': ['원본 HITACHI', '원본 SIMENSE', '사용된 데이터', '복구된 데이터'],
            '총 행수': [df_hitachi.shape[0], df_simense.shape[0], df_used.shape[0], df_result.shape[0]],
            '총 컬럼수': [df_hitachi.shape[1], df_simense.shape[1], df_used.shape[1], df_result.shape[1]],
            'DHL Warehouse': [
                '있음' if 'DHL Warehouse' in df_hitachi.columns else '없음',
                '있음' if 'DHL Warehouse' in df_simense.columns else '없음',
                '있음' if 'DHL Warehouse' in df_used.columns else '없음',
                '복구됨' if 'DHL Warehouse' in df_result.columns else '실패'
            ]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        df_comparison.to_excel(writer, sheet_name='복구_전후_비교', index=False)
    
    print(f"\n📊 최종 복구 완료 파일: {output_file}")
    
    return df_result, output_file

def main():
    """메인 실행 함수"""
    
    try:
        df_recovered, output_file = recover_dhl_warehouse_columns()
        
        print("\n✅ DHL Warehouse 컬럼 복구 완료!")
        print("=" * 60)
        print(f"📋 최종 데이터: {df_recovered.shape[0]}행, {df_recovered.shape[1]}컬럼")
        print(f"📊 출력 파일: {output_file}")
        
        # 복구된 컬럼들 확인
        recovered_cols = []
        for col in ['DHL Warehouse', 'Stack_Status', '열2']:
            if col in df_recovered.columns:
                valid_count = df_recovered[col].notna().sum()
                recovered_cols.append(f"{col}: {valid_count}개")
        
        print(f"🎯 복구된 컬럼 데이터:")
        for col_info in recovered_cols:
            print(f"  - {col_info}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 