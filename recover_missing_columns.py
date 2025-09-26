#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
누락된 컬럼 복구 스크립트
Status_Location_Date 컬럼 복구
"""

import pandas as pd
from datetime import datetime

def recover_missing_columns():
    """누락된 컬럼 복구"""
    
    print("🔧 누락된 컬럼 복구 시작")
    print("=" * 50)
    
    # 원본 데이터 로드
    hitachi_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_HITACHI(HE).xlsx'
    simense_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    used_data_path = r'MACHO_통합관리_20250702_205301\01_원본파일\MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    
    print("📊 데이터 로드 중...")
    df_hitachi = pd.read_excel(hitachi_path)
    df_simense = pd.read_excel(simense_path)
    df_used = pd.read_excel(used_data_path)
    
    print(f"✅ HITACHI: {df_hitachi.shape[0]}행, {df_hitachi.shape[1]}컬럼")
    print(f"✅ SIMENSE: {df_simense.shape[0]}행, {df_simense.shape[1]}컬럼")
    print(f"✅ 사용된 데이터: {df_used.shape[0]}행, {df_used.shape[1]}컬럼")
    
    # 원본 데이터 결합 (Status_Location_Date 포함)
    df_hitachi['VENDOR'] = 'HITACHI'
    df_simense['VENDOR'] = 'SIMENSE'
    
    # 공통 컬럼 + Status_Location_Date 확인
    hitachi_cols = set(df_hitachi.columns)
    simense_cols = set(df_simense.columns)
    common_cols = hitachi_cols & simense_cols
    
    print(f"\n📋 공통 컬럼: {len(common_cols)}개")
    print(f"📋 Status_Location_Date in HITACHI: {'Status_Location_Date' in hitachi_cols}")
    print(f"📋 Status_Location_Date in SIMENSE: {'Status_Location_Date' in simense_cols}")
    
    # 원본 데이터 결합
    df_original = pd.concat([
        df_hitachi[list(common_cols)],
        df_simense[list(common_cols)]
    ], ignore_index=True)
    
    print(f"\n📊 결합된 원본 데이터: {df_original.shape[0]}행, {df_original.shape[1]}컬럼")
    
    # Status_Location_Date 데이터 확인
    if 'Status_Location_Date' in df_original.columns:
        print(f"\n📋 Status_Location_Date 데이터 샘플:")
        print(df_original['Status_Location_Date'].head(10).tolist())
        
        # 데이터 유형 확인
        print(f"📋 데이터 타입: {df_original['Status_Location_Date'].dtype}")
        print(f"📋 유효한 데이터 개수: {df_original['Status_Location_Date'].notna().sum()}")
        print(f"📋 누락된 데이터 개수: {df_original['Status_Location_Date'].isna().sum()}")
        
        # 고유값 확인
        unique_dates = df_original['Status_Location_Date'].dropna().unique()
        print(f"📋 고유 날짜 개수: {len(unique_dates)}")
        if len(unique_dates) <= 10:
            print(f"📋 고유 날짜들: {unique_dates}")
    
    # 사용된 데이터와 매칭하여 Status_Location_Date 복구
    print("\n🔧 Status_Location_Date 복구 시작")
    
    # 매칭 키 생성 (여러 컬럼 조합)
    matching_cols = []
    for col in ['no.', 'Shipment Invoice No.', 'HVDC CODE', 'HVDC CODE 1']:
        if col in df_original.columns and col in df_used.columns:
            matching_cols.append(col)
    
    print(f"📋 매칭에 사용할 컬럼: {matching_cols}")
    
    if matching_cols and 'Status_Location_Date' in df_original.columns:
        # 매칭 수행
        df_merged = df_used.merge(
            df_original[matching_cols + ['Status_Location_Date']],
            on=matching_cols,
            how='left'
        )
        
        # 복구된 컬럼 확인
        recovered_count = df_merged['Status_Location_Date'].notna().sum()
        print(f"✅ Status_Location_Date 복구 완료: {recovered_count}개 레코드")
        
        # 최종 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'HVDC_Status_Location_Date_복구완료_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 시트 1: 복구된 전체 데이터
            df_merged.to_excel(writer, sheet_name='복구된_전체데이터', index=False)
            
            # 시트 2: Status_Location_Date 분석
            if 'Status_Location_Date' in df_merged.columns:
                status_analysis = df_merged.groupby(['Status_Location', 'Status_Location_Date']).size().reset_index(name='count')
                status_analysis.to_excel(writer, sheet_name='Status_Location_Date_분석', index=False)
            
            # 시트 3: 복구 전후 비교
            comparison_data = {
                '구분': ['원본 데이터', '사용된 데이터', '복구된 데이터'],
                '총 행수': [df_original.shape[0], df_used.shape[0], df_merged.shape[0]],
                '총 컬럼수': [df_original.shape[1], df_used.shape[1], df_merged.shape[1]],
                'Status_Location_Date': [
                    '있음' if 'Status_Location_Date' in df_original.columns else '없음',
                    '없음' if 'Status_Location_Date' not in df_used.columns else '있음',
                    '복구됨' if 'Status_Location_Date' in df_merged.columns else '실패'
                ]
            }
            
            df_comparison = pd.DataFrame(comparison_data)
            df_comparison.to_excel(writer, sheet_name='복구_전후_비교', index=False)
        
        print(f"📊 복구 완료 파일: {output_file}")
        
        return df_merged, output_file
    
    else:
        print("❌ 매칭 불가능: 적절한 키 컬럼이 없습니다.")
        return None, None

def main():
    """메인 실행 함수"""
    
    try:
        df_recovered, output_file = recover_missing_columns()
        
        if df_recovered is not None:
            print("\n✅ 누락된 컬럼 복구 완료!")
            print("=" * 50)
            print(f"📋 복구된 데이터: {df_recovered.shape[0]}행, {df_recovered.shape[1]}컬럼")
            print(f"📊 출력 파일: {output_file}")
            
            # Status_Location_Date 최종 확인
            if 'Status_Location_Date' in df_recovered.columns:
                valid_dates = df_recovered['Status_Location_Date'].notna().sum()
                print(f"🎯 Status_Location_Date 유효 데이터: {valid_dates}개")
        else:
            print("❌ 복구 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 