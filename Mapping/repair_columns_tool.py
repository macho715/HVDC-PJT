#!/usr/bin/env python3
"""
HVDC 컬럼 복구 도구 v2.8.1
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics
Purpose: Location/Status 컬럼 자동 생성 및 데이터 보강
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class ColumnRepairTool:
    """컬럼 복구 도구"""
    
    def __init__(self):
        # 컬럼 매핑 규칙
        self.column_mappings = {
            'Location': [
                'Status_Location', 'Current_Location', 'Warehouse', 
                'Storage_Location', 'Position', 'Site'
            ],
            'Status': [
                'Status_Current', 'Current_Status', 'Item_Status',
                'Delivery_Status', 'State', 'Condition'
            ],
            'Case_No': [
                'Case_Number', 'CaseNo', 'Case ID', 'ID', 'Item_ID'
            ]
        }
        
        # 기본값 규칙
        self.default_values = {
            'Status': 'Active',
            'Location': 'Unknown'
        }
        
        # 위치 정규화 규칙
        self.location_normalization = {
            'DSV INDOOR': ['DSV Indoor', 'DSV_Indoor', 'Indoor', 'DSV-Indoor'],
            'DSV OUTDOOR': ['DSV Outdoor', 'DSV_Outdoor', 'Outdoor', 'DSV-Outdoor'],
            'DSV AL MARKAZ': ['DSV Al Markaz', 'Al Markaz', 'Markaz', 'DSV-Markaz'],
            'MOSB': ['MARINE BASE', 'Offshore Base', 'Marine Offshore', 'MOSB'],
            'PRE ARRIVAL': ['Pre Arrival', 'PRE_ARRIVAL', 'Not Received', 'Pending'],
            'AGI': ['AGI Site', 'AGI_Site', 'AGI Plant'],
            'DAS': ['DAS Site', 'DAS_Site', 'DAS Plant'],
            'MIR': ['MIR Site', 'MIR_Site', 'MIR Plant'],
            'SHU': ['SHU Site', 'SHU_Site', 'SHU Plant']
        }
    
    def analyze_dataframe_structure(self, df: pd.DataFrame) -> Dict:
        """DataFrame 구조 분석"""
        analysis = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'missing_columns': [],
            'similar_columns': {},
            'data_quality': {}
        }
        
        # 필수 컬럼 확인
        required_columns = ['Location', 'Status', 'Case_No']
        for req_col in required_columns:
            if req_col not in df.columns:
                analysis['missing_columns'].append(req_col)
                
                # 유사한 컬럼 찾기
                similar = self._find_similar_columns(req_col, df.columns)
                if similar:
                    analysis['similar_columns'][req_col] = similar
        
        # 데이터 품질 분석
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            analysis['data_quality'][col] = {
                'null_count': null_count,
                'null_percentage': null_pct,
                'data_type': str(df[col].dtype),
                'unique_values': df[col].nunique()
            }
        
        return analysis
    
    def _find_similar_columns(self, target_col: str, available_cols: List[str]) -> List[str]:
        """유사한 컬럼명 찾기"""
        similar = []
        
        # 정확한 매핑 확인
        if target_col in self.column_mappings:
            for mapping in self.column_mappings[target_col]:
                for col in available_cols:
                    if mapping.lower() in col.lower() or col.lower() in mapping.lower():
                        similar.append(col)
        
        # 키워드 기반 매칭
        keywords = {
            'Location': ['location', 'position', 'warehouse', 'site', 'place'],
            'Status': ['status', 'state', 'condition', 'delivery'],
            'Case_No': ['case', 'id', 'number', 'no']
        }
        
        if target_col in keywords:
            for keyword in keywords[target_col]:
                for col in available_cols:
                    if keyword in col.lower() and col not in similar:
                        similar.append(col)
        
        return similar
    
    def repair_missing_columns(self, df: pd.DataFrame, auto_fix: bool = True) -> pd.DataFrame:
        """
        누락된 컬럼 복구
        v2.8.2 핫픽스: 전각공백 처리 추가
        """
        logger.info("🔧 컬럼 복구 시작...")
        
        df_repaired = df.copy()
        repair_log = []
        
        # ★ v2.8.2 핫픽스: 컬럼 헤더 전각공백 정리
        df_repaired.columns = [str(col).replace('\u3000', ' ').strip() for col in df_repaired.columns]
        repair_log.append("🔧 컬럼 헤더 전각공백 정리 완료")
        
        # 구조 분석
        analysis = self.analyze_dataframe_structure(df)
        
        # 누락된 컬럼 처리
        for missing_col in analysis['missing_columns']:
            logger.info(f"   누락 컬럼 처리: {missing_col}")
            
            # 유사한 컬럼이 있는 경우 매핑
            if missing_col in analysis['similar_columns']:
                similar_cols = analysis['similar_columns'][missing_col]
                if similar_cols and auto_fix:
                    source_col = similar_cols[0]  # 첫 번째 유사 컬럼 사용
                    df_repaired[missing_col] = df_repaired[source_col]
                    repair_log.append(f"✅ {missing_col} ← {source_col} (매핑)")
                    logger.info(f"      매핑: {source_col} → {missing_col}")
                else:
                    # 수동 확인 필요
                    repair_log.append(f"⚠️ {missing_col} 유사 컬럼: {similar_cols} (수동 확인 필요)")
            
            # 유사한 컬럼이 없는 경우 기본값 생성
            if missing_col not in df_repaired.columns:
                if missing_col in self.default_values:
                    df_repaired[missing_col] = self.default_values[missing_col]
                    repair_log.append(f"🔧 {missing_col} 기본값 생성: {self.default_values[missing_col]}")
                elif missing_col == 'Case_No':
                    # Case_No 자동 생성
                    df_repaired['Case_No'] = [f'HE{i+1:04d}' for i in range(len(df_repaired))]
                    repair_log.append(f"🔧 Case_No 자동 생성: HE0001~HE{len(df_repaired):04d}")
        
        # 위치 데이터 정규화
        if 'Location' in df_repaired.columns:
            df_repaired = self._normalize_locations(df_repaired)
            repair_log.append("🔧 Location 데이터 정규화 완료")
        
        # 복구 결과 로그
        logger.info("✅ 컬럼 복구 완료")
        for log_entry in repair_log:
            logger.info(f"   {log_entry}")
        
        return df_repaired
    
    def _normalize_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """위치 데이터 정규화"""
        df_normalized = df.copy()
        
        # 정규화 매핑 적용
        location_map = {}
        for standard, variations in self.location_normalization.items():
            for variation in variations:
                location_map[variation.upper()] = standard
        
        # Location 컬럼 정규화
        def normalize_location(location):
            if pd.isna(location):
                return 'Unknown'
            
            location_str = str(location).strip().upper()
            
            # 정확한 매칭
            if location_str in location_map:
                return location_map[location_str]
            
            # 부분 매칭
            for variation, standard in location_map.items():
                if variation in location_str:
                    return standard
            
            return location  # 원본 반환
        
        df_normalized['Location'] = df_normalized['Location'].apply(normalize_location)
        
        return df_normalized
    
    def generate_missing_status_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Status 데이터 보강"""
        df_enhanced = df.copy()
        
        # Location 기반 Status 추론
        def infer_status(row):
            location = str(row.get('Location', '')).upper()
            
            if 'PRE ARRIVAL' in location or 'PENDING' in location:
                return 'PRE ARRIVAL'
            elif any(site in location for site in ['AGI', 'DAS', 'MIR', 'SHU']):
                return 'DELIVERED'
            elif any(wh in location for wh in ['DSV', 'WAREHOUSE']):
                return 'IN WAREHOUSE'
            elif 'MOSB' in location or 'OFFSHORE' in location:
                return 'AT OFFSHORE BASE'
            else:
                return 'ACTIVE'
        
        # Status가 없거나 Unknown인 경우 추론
        mask = df_enhanced['Status'].isnull() | (df_enhanced['Status'] == 'Unknown')
        df_enhanced.loc[mask, 'Status'] = df_enhanced.loc[mask].apply(infer_status, axis=1)
        
        return df_enhanced
    
    def validate_repaired_data(self, df: pd.DataFrame) -> Dict:
        """복구된 데이터 검증"""
        validation = {
            'total_rows': len(df),
            'required_columns_present': True,
            'data_completeness': {},
            'location_distribution': {},
            'status_distribution': {},
            'issues': []
        }
        
        # 필수 컬럼 확인
        required_columns = ['Location', 'Status', 'Case_No']
        for col in required_columns:
            if col not in df.columns:
                validation['required_columns_present'] = False
                validation['issues'].append(f"필수 컬럼 누락: {col}")
        
        # 데이터 완성도 확인
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            validation['data_completeness'][col] = {
                'null_count': null_count,
                'null_percentage': null_pct
            }
            
            if null_pct > 50:
                validation['issues'].append(f"높은 결측률: {col} ({null_pct:.1f}%)")
        
        # 분포 확인
        if 'Location' in df.columns:
            validation['location_distribution'] = df['Location'].value_counts().to_dict()
        
        if 'Status' in df.columns:
            validation['status_distribution'] = df['Status'].value_counts().to_dict()
        
        return validation
    
    def repair_excel_file(self, input_path: str, output_path: str = None, auto_fix: bool = True) -> Dict:
        """Excel 파일 복구"""
        logger.info(f"📁 Excel 파일 복구 시작: {input_path}")
        
        try:
            # Excel 파일 로드
            df = pd.read_excel(input_path)
            logger.info(f"   원본 데이터: {len(df)}행 × {len(df.columns)}열")
            
            # 컬럼 복구
            df_repaired = self.repair_missing_columns(df, auto_fix)
            
            # Status 데이터 보강
            df_repaired = self.generate_missing_status_data(df_repaired)
            
            # 검증
            validation = self.validate_repaired_data(df_repaired)
            
            # 결과 저장
            if output_path:
                df_repaired.to_excel(output_path, index=False)
                logger.info(f"   복구된 파일 저장: {output_path}")
            
            return {
                'original_df': df,
                'repaired_df': df_repaired,
                'validation': validation,
                'success': len(validation['issues']) == 0
            }
            
        except Exception as e:
            logger.error(f"Excel 파일 복구 실패: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """메인 실행 함수"""
    tool = ColumnRepairTool()
    
    # 테스트 데이터 생성
    test_data = {
        'Case_Number': ['HE0001', 'HE0002', 'HE0003', 'HE0004', 'HE0005'],
        'Status_Location': ['DSV Indoor', 'AGI Site', 'Pre Arrival', 'MOSB', 'DSV Outdoor'],
        'Current_Status': ['Active', 'Delivered', 'Pending', 'Active', 'Active'],
        'Qty': [10, 5, 8, 3, 12],
        'Amount': [50000, 25000, 40000, 15000, 60000]
    }
    
    df_test = pd.DataFrame(test_data)
    logger.info("🧪 테스트 데이터 생성")
    logger.info(f"   컬럼: {list(df_test.columns)}")
    
    # 컬럼 복구 테스트
    df_repaired = tool.repair_missing_columns(df_test)
    
    logger.info("✅ 복구 결과:")
    logger.info(f"   복구 후 컬럼: {list(df_repaired.columns)}")
    
    # 검증
    validation = tool.validate_repaired_data(df_repaired)
    logger.info(f"   검증 결과: {'성공' if len(validation['issues']) == 0 else '문제 발견'}")
    
    if validation['issues']:
        for issue in validation['issues']:
            logger.warning(f"   ⚠️ {issue}")
    
    # 추천 명령어
    logger.info("\n🔧 **추천 명령어:**")
    logger.info("/logi_master repair_columns --fast [필수 컬럼 자동 생성]")
    logger.info("/logi_master flow-kpi --deep [Code 0-4 분포 & 위험 리스트 보고]")
    logger.info("/automate_workflow mosb-ageing-guard [MOSB 체류 > 30d 경고]")

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main() 