#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
원본 데이터 직접 사용 분석 스크립트
HVDC PROJECT - 실제 원본 데이터 vs 가공된 데이터 비교
"""

import pandas as pd
import os
from datetime import datetime

def load_original_data():
    """원본 데이터 로드"""
    
    # 원본 파일 경로
    hitachi_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_HITACHI(HE).xlsx'
    simense_path = r'hvdc_macho_gpt\WAREHOUSE\data\HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    
    # 사용된 데이터 경로
    used_data_path = r'MACHO_통합관리_20250702_205301\01_원본파일\MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    
    print("🔍 원본 데이터 분석 시작")
    print("=" * 50)
    
    # 원본 데이터 로드
    df_hitachi = pd.read_excel(hitachi_path)
    df_simense = pd.read_excel(simense_path)
    
    # 사용된 데이터 로드
    df_used = pd.read_excel(used_data_path)
    
    print(f"📊 원본 HITACHI 데이터: {df_hitachi.shape[0]:,}행, {df_hitachi.shape[1]}컬럼")
    print(f"📊 원본 SIMENSE 데이터: {df_simense.shape[0]:,}행, {df_simense.shape[1]}컬럼")
    print(f"📊 사용된 데이터: {df_used.shape[0]:,}행, {df_used.shape[1]}컬럼")
    
    # 데이터 결합
    df_hitachi['VENDOR'] = 'HITACHI'
    df_simense['VENDOR'] = 'SIMENSE'
    
    # 공통 컬럼 찾기
    common_columns = list(set(df_hitachi.columns) & set(df_simense.columns))
    print(f"📋 공통 컬럼 수: {len(common_columns)}")
    
    # 데이터 결합
    df_combined = pd.concat([
        df_hitachi[common_columns],
        df_simense[common_columns]
    ], ignore_index=True)
    
    print(f"📊 결합된 원본 데이터: {df_combined.shape[0]:,}행, {df_combined.shape[1]}컬럼")
    
    # 차이 분석
    print("\n🔍 데이터 차이 분석")
    print("=" * 30)
    
    original_total = df_combined.shape[0]
    used_total = df_used.shape[0]
    difference = original_total - used_total
    
    print(f"원본 총 행수: {original_total:,}")
    print(f"사용된 행수: {used_total:,}")
    print(f"차이: {difference:,}행 ({difference/original_total*100:.1f}%)")
    
    # 컬럼 비교
    print(f"\n📋 컬럼 비교")
    print(f"원본 컬럼수: {df_combined.shape[1]}")
    print(f"사용된 컬럼수: {df_used.shape[1]}")
    print(f"추가된 컬럼수: {df_used.shape[1] - df_combined.shape[1]}")
    
    # 원본 데이터 기반 분석 결과 생성
    analysis_result = generate_original_analysis(df_combined)
    
    return df_combined, df_used, analysis_result

def generate_original_analysis(df):
    """원본 데이터 기반 분석"""
    
    analysis = {
        'total_records': len(df),
        'vendor_distribution': df['VENDOR'].value_counts().to_dict(),
        'date_range': {
            'start': df['Date'].min() if 'Date' in df.columns else 'N/A',
            'end': df['Date'].max() if 'Date' in df.columns else 'N/A'
        },
        'key_statistics': {
            'hitachi_percentage': (df['VENDOR'] == 'HITACHI').mean() * 100,
            'simense_percentage': (df['VENDOR'] == 'SIMENSE').mean() * 100
        }
    }
    
    return analysis

def create_original_data_report(df_original, df_used, analysis):
    """원본 데이터 보고서 생성"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Excel 보고서 생성
    with pd.ExcelWriter(f'원본데이터_vs_사용데이터_비교_{timestamp}.xlsx', engine='openpyxl') as writer:
        
        # 시트 1: 요약 비교
        summary_data = {
            '구분': ['원본 HITACHI', '원본 SIMENSE', '원본 총합', '사용된 데이터', '차이'],
            '행수': [
                analysis['vendor_distribution'].get('HITACHI', 0),
                analysis['vendor_distribution'].get('SIMENSE', 0),
                analysis['total_records'],
                len(df_used),
                analysis['total_records'] - len(df_used)
            ],
            '비율': [
                f"{analysis['key_statistics']['hitachi_percentage']:.1f}%",
                f"{analysis['key_statistics']['simense_percentage']:.1f}%",
                "100.0%",
                f"{len(df_used)/analysis['total_records']*100:.1f}%",
                f"{(analysis['total_records'] - len(df_used))/analysis['total_records']*100:.1f}%"
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='데이터_비교_요약', index=False)
        
        # 시트 2: 원본 데이터 샘플 (처음 1000행)
        df_original.head(1000).to_excel(writer, sheet_name='원본데이터_샘플', index=False)
        
        # 시트 3: 사용된 데이터 샘플 (처음 1000행)
        df_used.head(1000).to_excel(writer, sheet_name='사용된데이터_샘플', index=False)
    
    print(f"📊 보고서 생성 완료: 원본데이터_vs_사용데이터_비교_{timestamp}.xlsx")
    
    return f'원본데이터_vs_사용데이터_비교_{timestamp}.xlsx'

def main():
    """메인 실행 함수"""
    
    try:
        # 원본 데이터 로드 및 분석
        df_original, df_used, analysis = load_original_data()
        
        # 보고서 생성
        report_file = create_original_data_report(df_original, df_used, analysis)
        
        print("\n✅ 원본 데이터 분석 완료")
        print("=" * 50)
        print(f"📋 결론: 사용된 데이터는 원본 데이터를 기반으로 하되,")
        print(f"       {analysis['total_records'] - len(df_used):,}개 행이 필터링/정제되었습니다.")
        print(f"📊 원본 데이터 활용도: {len(df_used)/analysis['total_records']*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    main() 