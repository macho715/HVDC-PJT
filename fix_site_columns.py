#!/usr/bin/env python3
"""
현장 컬럼 누락 문제 해결 스크립트
기존 통합 데이터에 현장 컬럼들(AGI, DAS, MIR, SHU)을 추가
"""

import pandas as pd
from datetime import datetime
import os

def fix_site_columns():
    """현장 컬럼들을 추가하여 새로운 통합 데이터 생성"""
    print("🔧 현장 컬럼 누락 문제 해결 중...")
    
    # 1. 기존 통합 데이터 로드
    existing_file = "MACHO_WH_HANDLING_전체트랜잭션데이터_20250703_114640.xlsx"
    if not os.path.exists(existing_file):
        print(f"❌ 기존 파일을 찾을 수 없습니다: {existing_file}")
        return
    
    combined_df = pd.read_excel(existing_file)
    print(f"✅ 기존 통합 데이터 로드: {len(combined_df):,}행")
    
    # 2. 원본 데이터에서 현장 컬럼 정보 추가
    file_paths = {
        'HITACHI': "HVDC_PJT/hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        'SIMENSE': "HVDC_PJT/hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
    }
    
    site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
    
    # 각 벤더별로 현장 컬럼 정보 추가
    for vendor, file_path in file_paths.items():
        if not os.path.exists(file_path):
            print(f"⚠️ {vendor} 파일을 찾을 수 없습니다: {file_path}")
            continue
            
        # 원본 데이터 로드
        original_df = pd.read_excel(file_path)
        print(f"📂 {vendor} 원본 데이터 로드: {len(original_df):,}행")
        
        # Case No.를 기준으로 현장 컬럼 정보 매핑 (벤더별 키 컬럼 다름)
        vendor_data = combined_df[combined_df['VENDOR'] == vendor].copy()
        
        # 벤더별 키 컬럼 설정
        if vendor == 'HITACHI':
            key_col = 'Case No.'
        elif vendor == 'SIMENSE':
            key_col = 'SERIAL NO.'
        else:
            key_col = 'Case No.'  # 기본값
        
        # 현장 컬럼들을 추가
        for site_col in site_columns:
            if site_col in original_df.columns and key_col in original_df.columns:
                # 키 컬럼을 기준으로 매핑
                if vendor == 'SIMENSE':
                    # SIMENSE의 경우 SERIAL NO.와 Case No.가 같은 값이라고 가정
                    site_mapping = original_df.set_index(key_col)[site_col].to_dict()
                    vendor_data[site_col] = vendor_data['Case No.'].map(site_mapping)
                else:
                    # HITACHI의 경우 직접 매핑
                    site_mapping = original_df.set_index(key_col)[site_col].to_dict()
                    vendor_data[site_col] = vendor_data['Case No.'].map(site_mapping)
                print(f"  ✅ {site_col} 컬럼 추가: {vendor_data[site_col].notna().sum():,}건")
            else:
                # 컬럼이 없으면 NaN으로 채움
                vendor_data[site_col] = pd.NaT
                print(f"  ⚠️ {site_col} 컬럼 없음 - NaN으로 채움")
        
        # 원래 데이터프레임에서 해당 벤더 데이터 업데이트
        combined_df.loc[combined_df['VENDOR'] == vendor, site_columns] = vendor_data[site_columns].values
    
    # 3. 새로운 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"MACHO_WH_HANDLING_전체트랜잭션데이터_{timestamp}.xlsx"
    
    combined_df.to_excel(output_file, index=False)
    print(f"✅ 현장 컬럼이 추가된 새로운 파일 생성: {output_file}")
    
    # 4. 현장 데이터 확인
    print(f"\n📊 현장 데이터 확인:")
    for site_col in site_columns:
        if site_col in combined_df.columns:
            count = combined_df[site_col].notna().sum()
            print(f"  {site_col}: {count:,}건")
    
    return output_file

if __name__ == "__main__":
    fix_site_columns() 