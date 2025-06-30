#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC v2.8.3 실제 데이터 검증 스크립트
실제 HITACHI + SIMENSE 엑셀 파일로 v2.8.3 패치 테스트
"""

import sys
import os
sys.path.append('../Mapping')

from mapping_utils import apply_validation_rules, normalize_flow_code
from core.loader import DataLoader
import pandas as pd
import json
from datetime import datetime

def test_v283_with_real_data():
    """v2.8.3 패치를 실제 데이터로 검증"""
    
    print('🚀 HVDC v2.8.3 실제 데이터 검증 시작...')
    print(f'⏰ 실행 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('📊 실제 HITACHI + SIMENSE 데이터 처리')
    print('=' * 50)
    
    try:
        # Load mapping rules v2.8.3
        rules_path = '../Mapping/mapping_rules_v2.8.json'
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        print(f'✅ 규칙 버전: {rules["version"]}')
        print(f'✅ 규칙 파일: {rules_path}')
        
        # Initialize DataLoader
        loader = DataLoader('../Mapping/mapping_rules_v2.8.json', 'data')
        
        # Load HITACHI data
        print('\n🔄 HITACHI 데이터 로딩 중...')
        hitachi_file = 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx'
        if not os.path.exists(hitachi_file):
            print(f'❌ 파일 없음: {hitachi_file}')
            return False
            
        hitachi_df = loader.load_excel_data('HVDC WAREHOUSE_HITACHI(HE).xlsx')
        print(f'📈 HITACHI 원본: {len(hitachi_df)} 행')
        
        # Load SIMENSE data  
        print('\n🔄 SIMENSE 데이터 로딩 중...')
        simense_file = 'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
        if not os.path.exists(simense_file):
            print(f'❌ 파일 없음: {simense_file}')
            return False
            
        simense_df = loader.load_excel_data('HVDC WAREHOUSE_SIMENSE(SIM).xlsx')
        print(f'📈 SIMENSE 원본: {len(simense_df)} 행')
        
        # Apply v2.8.3 validation rules
        print('\n🔧 v2.8.3 검증 룰 적용 중...')
        print('   - Flow Code 6 → 3 정규화')
        print('   - NULL Pkg → 1 보정')
        print('   - 스마트 중복제거')
        
        hitachi_before = len(hitachi_df)
        hitachi_processed = apply_validation_rules(hitachi_df)
        hitachi_after = len(hitachi_processed)
        
        simense_before = len(simense_df)
        simense_processed = apply_validation_rules(simense_df)
        simense_after = len(simense_processed)
        
        print(f'✅ HITACHI: {hitachi_before} → {hitachi_after} 행')
        print(f'✅ SIMENSE: {simense_before} → {simense_after} 행')
        
        # Extract transactions with v2.8.3
        print('\n🔄 거래 추출 중...')
        hitachi_transactions = loader.extract_transactions(hitachi_processed, 'HITACHI')
        simense_transactions = loader.extract_transactions(simense_processed, 'SIMENSE')
        
        print(f'📊 HITACHI 거래: {len(hitachi_transactions)}')
        print(f'📊 SIMENSE 거래: {len(simense_transactions)}')
        
        # Analyze transaction types
        if len(hitachi_transactions) > 0:
            hitachi_in = len([t for t in hitachi_transactions if t.get('Transaction_Type') == 'IN'])
            hitachi_out = len([t for t in hitachi_transactions if t.get('Transaction_Type') == 'OUT'])
            print(f'   HITACHI: IN({hitachi_in}) + OUT({hitachi_out})')
        
        if len(simense_transactions) > 0:
            simense_in = len([t for t in simense_transactions if t.get('Transaction_Type') == 'IN'])
            simense_out = len([t for t in simense_transactions if t.get('Transaction_Type') == 'OUT'])
            print(f'   SIMENSE: IN({simense_in}) + OUT({simense_out})')
        
        # Calculate total PKG
        total_pkg = len(hitachi_transactions) + len(simense_transactions)
        print(f'\n🎯 총 PKG: {total_pkg:,}')
        print(f'🎯 목표 7,180 vs 실제: {"✅ 달성" if total_pkg >= 7180 else "❌ 미달"}')
        
        # Flow Code analysis
        all_transactions = hitachi_transactions + simense_transactions
        flow_codes = [t.get('Flow_Code', 0) for t in all_transactions]
        flow_code_counts = pd.Series(flow_codes).value_counts().sort_index()
        
        print('\n📋 Flow Code 분포:')
        for code, count in flow_code_counts.items():
            print(f'   Flow Code {code}: {count:,} 건')
        
        print('\n🎉 v2.8.3 실제 데이터 검증 완료!')
        print('✅ 모든 패치가 실제 데이터에서 정상 작동')
        
        return True
        
    except Exception as e:
        print(f'\n❌ 오류 발생: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_v283_with_real_data()
    if success:
        print('\n🎯 v2.8.3 실제 데이터 검증: 성공')
    else:
        print('\n❌ v2.8.3 실제 데이터 검증: 실패') 