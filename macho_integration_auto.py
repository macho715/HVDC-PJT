#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MACHO-GPT v3.4 통합 파일 생성 자동화 스크립트
목적: 손상된 파일 복구 + 현장별 데이터 통합
사용법: python macho_integration_auto.py
"""

import pandas as pd
import os
from datetime import datetime

def create_integrated_macho_file():
    """MACHO 통합 파일 자동 생성"""
    
    print('🔧 MACHO 통합 파일 자동 생성 시작')
    print('=' * 60)
    
    # 원본 파일들 확인
    main_file = 'MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
    warehouse_file = 'MACHO_창고별현장별월별입출고_완전분석_20250702_195428.xlsx'
    site_file = 'MACHO_현장별월별입출고_20250702_194756.xlsx'
    
    files_to_check = [main_file, warehouse_file, site_file]
    
    print('📁 원본 파일 확인:')
    for filename in files_to_check:
        exists = os.path.exists(filename)
        print(f'   {"✅" if exists else "❌"} {filename}')
        if not exists:
            print(f'❌ 필수 파일 누락: {filename}')
            return False
    
    try:
        # 데이터 로드
        print('\n📥 데이터 로드 중...')
        df_main = pd.read_excel(main_file, sheet_name='전체_트랜잭션_SQM_STACK')
        df_warehouse = pd.read_excel(warehouse_file, sheet_name='창고별_월별_입출고')
        df_site = pd.read_excel(site_file, sheet_name='현장별_월별_입출고')
        df_site_summary = pd.read_excel(site_file, sheet_name='현장별_요약통계')
        
        print(f'   메인 데이터: {len(df_main):,}건')
        print(f'   창고 데이터: {len(df_warehouse):,}건')
        print(f'   현장 데이터: {len(df_site):,}건')
        print(f'   현장 요약: {len(df_site_summary):,}건')
        
        # 데이터 검증
        print('\n🔍 데이터 무결성 검증:')
        main_check = len(df_main) > 7500 and 'SQM' in df_main.columns and 'STACK' in df_main.columns
        warehouse_check = len(df_warehouse) >= 19
        site_check = len(df_site) >= 19
        
        print(f'   메인 데이터: {"✅ 통과" if main_check else "❌ 실패"}')
        print(f'   창고 데이터: {"✅ 통과" if warehouse_check else "❌ 실패"}')
        print(f'   현장 데이터: {"✅ 통과" if site_check else "❌ 실패"}')
        
        if not (main_check and warehouse_check and site_check):
            print('❌ 데이터 검증 실패!')
            return False
        
        # 통합 파일 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'MACHO_완전통합_현장포함_{timestamp}.xlsx'
        
        print(f'\n💾 통합 파일 생성: {output_file}')
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # 메인 데이터 시트
            df_main.to_excel(writer, sheet_name='메인_트랜잭션_SQM_STACK', index=False)
            
            # 창고별 월별 입출고
            df_warehouse.to_excel(writer, sheet_name='창고별_월별_입출고', index=False)
            
            # 현장별 월별 입출고
            df_site.to_excel(writer, sheet_name='현장별_월별_입출고', index=False)
            
            # 현장별 요약 통계
            df_site_summary.to_excel(writer, sheet_name='현장별_요약통계', index=False)
            
            # 통합 요약
            summary = pd.DataFrame({
                '항목': ['메인데이터', '창고별데이터', '현장별입출고', '현장별요약', '생성시간'],
                '값': [len(df_main), len(df_warehouse), len(df_site), len(df_site_summary), 
                      datetime.now().strftime('%Y-%m-%d %H:%M')]
            })
            summary.to_excel(writer, sheet_name='통합요약', index=False)
        
        # 생성 파일 검증
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f'✅ 파일 생성 성공!')
            print(f'📁 파일명: {output_file}')
            print(f'💾 파일 크기: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)')
            
            # 읽기 테스트
            test_excel = pd.ExcelFile(output_file)
            print(f'📊 총 시트: {len(test_excel.sheet_names)}개')
            
            total_records = 0
            for sheet in test_excel.sheet_names:
                test_df = pd.read_excel(output_file, sheet_name=sheet)
                records = len(test_df)
                total_records += records
                print(f'   • {sheet}: {records:,}건')
            
            print(f'\n🎉 통합 완료: 총 {total_records:,}건 데이터')
            print(f'📋 상태: 프로덕션 준비 완료')
            
            return output_file
        else:
            print('❌ 파일 생성 실패!')
            return False
            
    except Exception as e:
        print(f'❌ 오류 발생: {str(e)}')
        return False

def main():
    """메인 실행 함수"""
    print('🚀 MACHO-GPT 통합 파일 자동화 시작')
    print(f'📅 실행 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    result = create_integrated_macho_file()
    
    if result:
        print(f'\n✅ 자동화 완료: {result}')
        print('🔧 사용법: Excel에서 파일을 열어 분석하세요.')
        
        # 다음 실행 안내
        print('\n📋 다음에 같은 작업 실행하려면:')
        print('   python macho_integration_auto.py')
    else:
        print('\n❌ 자동화 실패')

if __name__ == '__main__':
    main() 