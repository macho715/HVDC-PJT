#!/usr/bin/env python3
"""
HVDC MOSB 컬럼 진단 스크립트
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics
Purpose: Code 3-4 미인식 원인 진단
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 상위 디렉토리에서 모듈 임포트
sys.path.append('../hvdc_macho_gpt/WAREHOUSE')

def diagnose_mosb_columns():
    """MOSB 컬럼 진단"""
    
    data_paths = {
        'hvdc_status': '../hvdc_macho_gpt/WAREHOUSE/data/HVDC-STATUS.xlsx',
        'hitachi': '../hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
        'simense': '../hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    }
    
    logger.info("🔍 MOSB 컬럼 진단 시작...")
    
    for name, path in data_paths.items():
        if not Path(path).exists():
            logger.warning(f"⚠️ {name} 파일 없음: {path}")
            continue
            
        logger.info(f"\n📊 {name.upper()} 분석 중...")
        
        try:
            # Excel 파일 로드
            df = pd.read_excel(path)
            logger.info(f"   총 {len(df)}행 × {len(df.columns)}열")
            
            # MOSB 관련 컬럼 찾기
            mosb_cols = [col for col in df.columns if 'MOSB' in col.upper()]
            wh_cols = [col for col in df.columns if any(wh in col.upper() for wh in ['DSV', 'INDOOR', 'OUTDOOR', 'WAREHOUSE'])]
            
            logger.info(f"   MOSB 컬럼: {mosb_cols}")
            logger.info(f"   WH 컬럼: {wh_cols[:5]}...")  # 처음 5개만
            
            # MOSB 컬럼 상세 분석
            for mosb_col in mosb_cols:
                logger.info(f"\n   🔍 {mosb_col} 컬럼 분석:")
                
                # 기본 통계
                total_rows = len(df)
                non_null_count = df[mosb_col].notna().sum()
                null_count = df[mosb_col].isna().sum()
                
                logger.info(f"      총 행수: {total_rows}")
                logger.info(f"      비어있지 않은 값: {non_null_count} ({non_null_count/total_rows*100:.1f}%)")
                logger.info(f"      비어있는 값: {null_count} ({null_count/total_rows*100:.1f}%)")
                
                # 고유값 분석
                if non_null_count > 0:
                    unique_values = df[mosb_col].dropna().unique()
                    logger.info(f"      고유값 개수: {len(unique_values)}")
                    logger.info(f"      고유값 샘플: {list(unique_values)[:10]}")  # 처음 10개만
                    
                    # 값 타입 분석
                    value_types = {}
                    for val in df[mosb_col].dropna():
                        val_type = type(val).__name__
                        value_types[val_type] = value_types.get(val_type, 0) + 1
                    
                    logger.info(f"      값 타입 분포: {value_types}")
                    
                    # 실제 값들 샘플 출력
                    sample_values = df[df[mosb_col].notna()][mosb_col].head(10).tolist()
                    logger.info(f"      실제 값 샘플: {sample_values}")
                
                # 패턴 분석
                if non_null_count > 0:
                    # 문자열로 변환 후 패턴 확인
                    str_values = df[mosb_col].dropna().astype(str)
                    
                    # 날짜 패턴 확인
                    date_like = str_values.str.contains(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}', na=False).sum()
                    if date_like > 0:
                        logger.info(f"      날짜 형식 값: {date_like}개")
                        date_samples = str_values[str_values.str.contains(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}', na=False)].head(5).tolist()
                        logger.info(f"      날짜 샘플: {date_samples}")
                    
                    # 공백이 아닌 실제 데이터 확인
                    non_empty = str_values[str_values.str.strip() != ''].count()
                    logger.info(f"      공백이 아닌 실제 데이터: {non_empty}개")
                    
                    if non_empty > 0:
                        actual_samples = str_values[str_values.str.strip() != ''].head(10).tolist()
                        logger.info(f"      실제 데이터 샘플: {actual_samples}")
            
            # WH와 MOSB 동시 존재하는 행 분석
            if mosb_cols and wh_cols:
                logger.info(f"\n   🔗 WH-MOSB 연관 분석:")
                
                # 각 WH 컬럼과 MOSB 동시 존재 확인
                for wh_col in wh_cols[:3]:  # 처음 3개 WH 컬럼만
                    for mosb_col in mosb_cols:
                        both_exist = df[(df[wh_col].notna()) & (df[mosb_col].notna())].shape[0]
                        logger.info(f"      {wh_col} + {mosb_col}: {both_exist}행")
                        
                        if both_exist > 0:
                            # 샘플 출력
                            sample_df = df[(df[wh_col].notna()) & (df[mosb_col].notna())].head(3)
                            for idx, row in sample_df.iterrows():
                                logger.info(f"         샘플 {idx}: WH={row[wh_col]}, MOSB={row[mosb_col]}")
            
            # Flow Code 계산 시뮬레이션
            logger.info(f"\n   🧮 Flow Code 시뮬레이션:")
            
            code_3_candidates = 0  # Port→WH→MOSB→Site
            code_4_candidates = 0  # Port→WH→wh→MOSB→Site
            
            for idx, row in df.iterrows():
                # WH 단계 계산
                wh_count = sum(1 for col in wh_cols if pd.notna(row.get(col)) and str(row.get(col)).strip())
                
                # MOSB 확인
                mosb_exists = any(pd.notna(row.get(col)) and str(row.get(col)).strip() for col in mosb_cols)
                
                if wh_count >= 1 and mosb_exists:
                    if wh_count == 1:
                        code_3_candidates += 1
                    elif wh_count >= 2:
                        code_4_candidates += 1
            
            logger.info(f"      Code 3 후보 (WH 1단계 + MOSB): {code_3_candidates}건")
            logger.info(f"      Code 4 후보 (WH 2+단계 + MOSB): {code_4_candidates}건")
            
        except Exception as e:
            logger.error(f"❌ {name} 분석 실패: {e}")
    
    logger.info("\n✅ MOSB 진단 완료")

def main():
    """메인 실행 함수"""
    diagnose_mosb_columns()
    
    logger.info("\n🔧 **추천 명령어:**")
    logger.info("/logi_master fix_mosb_recognition --column_scanner [MOSB 인식 수정]")
    logger.info("/logi_master validate_flow_patterns --mosb_focus [MOSB 패턴 검증]")
    logger.info("/logi_master upgrade_to_v282 --mosb_support [v2.8.2 업그레이드]")

if __name__ == "__main__":
    main() 