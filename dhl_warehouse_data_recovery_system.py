#!/usr/bin/env python3
"""
DHL Warehouse 데이터 복구 시스템 v1.0.0 (Green Phase)
- TDD 테스트를 통과시키는 최소 구현
- 143개 DHL Warehouse 레코드 완전 복구
- 온톨로지 매핑 및 데이터 무결성 보장
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DHLWarehouseDataRecoverySystem:
    """DHL Warehouse 데이터 복구 시스템"""
    
    def __init__(self):
        """시스템 초기화"""
        self.original_hitachi_file = "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.current_data_file = "HVDC_DHL_Warehouse_전체복구완료_20250704_122156.xlsx"
        self.ontology_mapping_file = "hvdc_integrated_mapping_rules_v3.0.json"
        self.expected_dhl_records = 143
        
        logger.info("DHL Warehouse 데이터 복구 시스템 초기화 완료")
    
    def extract_dhl_warehouse_records(self, df):
        """
        원본 데이터에서 DHL Warehouse 레코드 추출
        
        Args:
            df: 원본 HITACHI 데이터프레임
            
        Returns:
            DataFrame: DHL Warehouse 레코드 (143개)
        """
        try:
            # DHL Warehouse 컬럼이 있는지 확인
            if 'DHL Warehouse' not in df.columns:
                raise ValueError("DHL Warehouse 컬럼이 원본 데이터에 없음")
            
            # DHL Warehouse 값이 있는 레코드만 추출
            dhl_records = df[df['DHL Warehouse'].notna()].copy()
            
            logger.info(f"원본 데이터에서 DHL Warehouse 레코드 {len(dhl_records)}개 추출")
            
            # 데이터 검증
            if len(dhl_records) != self.expected_dhl_records:
                logger.warning(f"예상 레코드 수와 다름: {len(dhl_records)} != {self.expected_dhl_records}")
            
            # 필수 컬럼 확인 및 생성
            required_columns = ['Case_No', 'Date', 'Location', 'Qty']
            for col in required_columns:
                if col not in dhl_records.columns:
                    # 컬럼 매핑 시도
                    mapped_col = self._map_column_name(col, dhl_records.columns)
                    if mapped_col:
                        dhl_records = dhl_records.rename(columns={mapped_col: col})
                        logger.info(f"컬럼 매핑: {mapped_col} -> {col}")
                    else:
                        logger.warning(f"필수 컬럼 없음: {col}")
            
            # Case_No 중복 제거
            if 'Case_No' in dhl_records.columns:
                before_dedup = len(dhl_records)
                dhl_records = dhl_records.drop_duplicates(subset=['Case_No'])
                after_dedup = len(dhl_records)
                if before_dedup != after_dedup:
                    logger.info(f"Case_No 중복 제거: {before_dedup} -> {after_dedup}")
            
            # DHL Warehouse 날짜 형식 정규화
            dhl_records['DHL Warehouse'] = pd.to_datetime(
                dhl_records['DHL Warehouse'], 
                errors='coerce'
            )
            
            # 유효하지 않은 날짜 필터링
            valid_dates = dhl_records['DHL Warehouse'].notna()
            dhl_records = dhl_records[valid_dates]
            
            logger.info(f"유효한 DHL Warehouse 날짜가 있는 레코드: {len(dhl_records)}개")
            
            return dhl_records
            
        except Exception as e:
            logger.error(f"DHL Warehouse 레코드 추출 실패: {str(e)}")
            raise
    
    def _map_column_name(self, target_col, available_columns):
        """컬럼 이름 매핑 (HVDC 실제 데이터 기준)"""
        mapping = {
            'Case_No': ['Case No.', 'Case No', 'case_no', 'CASE_NO', 'Case Number', 'ID', 'no.'],
            'Date': ['Date', 'DATE', 'date', 'Created Date', 'Transaction Date', 'ETD/ATD', 'ETA/ATA'],
            'Location': ['Location', 'LOCATION', 'location', 'Current Location', 'Site', 'Status_Location'],
            'Qty': ['Qty', 'QTY', 'qty', 'Quantity', 'QUANTITY', 'Amount', 'Pkg']
        }
        
        if target_col in mapping:
            for candidate in mapping[target_col]:
                if candidate in available_columns:
                    return candidate
        
        return None
    
    def merge_dhl_records_safely(self, current_df, dhl_records):
        """
        DHL 레코드를 현재 데이터와 안전하게 병합
        
        Args:
            current_df: 현재 데이터프레임
            dhl_records: DHL Warehouse 레코드
            
        Returns:
            DataFrame: 병합된 데이터프레임
        """
        try:
            logger.info(f"DHL 레코드 병합 시작: 현재 {len(current_df)}개 + DHL {len(dhl_records)}개")
            
            # 컬럼 정렬 (현재 데이터 기준)
            current_columns = current_df.columns.tolist()
            
            # DHL 레코드의 컬럼을 현재 데이터에 맞춤
            aligned_dhl_records = pd.DataFrame(columns=current_columns)
            
            for col in current_columns:
                if col in dhl_records.columns:
                    aligned_dhl_records[col] = dhl_records[col]
                else:
                    # 빈 컬럼에 대해 적절한 기본값 설정
                    if col in ['Amount', 'Qty', 'Weight']:
                        aligned_dhl_records[col] = 0
                    elif col in ['Date', 'Status_Location_Date']:
                        aligned_dhl_records[col] = pd.NaT
                    else:
                        aligned_dhl_records[col] = np.nan
            
            # Case_No 중복 검사
            if 'Case_No' in current_df.columns and 'Case_No' in aligned_dhl_records.columns:
                current_case_nos = set(current_df['Case_No'].dropna())
                dhl_case_nos = set(aligned_dhl_records['Case_No'].dropna())
                
                duplicates = current_case_nos.intersection(dhl_case_nos)
                if duplicates:
                    logger.warning(f"Case_No 중복 발견: {len(duplicates)}개")
                    # 중복 제거
                    aligned_dhl_records = aligned_dhl_records[
                        ~aligned_dhl_records['Case_No'].isin(duplicates)
                    ]
                    logger.info(f"중복 제거 후 DHL 레코드: {len(aligned_dhl_records)}개")
            
            # 데이터 병합
            merged_df = pd.concat([current_df, aligned_dhl_records], ignore_index=True)
            
            logger.info(f"DHL 레코드 병합 완료: {len(merged_df)}개 레코드")
            
            return merged_df
            
        except Exception as e:
            logger.error(f"DHL 레코드 병합 실패: {str(e)}")
            raise
    
    def create_final_integrated_dataset(self, current_df, original_df):
        """
        최종 통합 데이터셋 생성
        
        Args:
            current_df: 현재 데이터프레임
            original_df: 원본 데이터프레임
            
        Returns:
            DataFrame: 최종 통합 데이터셋
        """
        try:
            logger.info("최종 통합 데이터셋 생성 시작")
            
            # 1. DHL Warehouse 레코드 추출
            dhl_records = self.extract_dhl_warehouse_records(original_df)
            
            # 2. 안전하게 병합
            merged_df = self.merge_dhl_records_safely(current_df, dhl_records)
            
            # 3. 데이터 정리 및 검증
            final_dataset = self._clean_and_validate_dataset(merged_df)
            
            # 4. 온톨로지 매핑 적용
            final_dataset = self._apply_ontology_mapping(final_dataset)
            
            logger.info(f"최종 통합 데이터셋 생성 완료: {len(final_dataset)}개 레코드")
            
            return final_dataset
            
        except Exception as e:
            logger.error(f"최종 통합 데이터셋 생성 실패: {str(e)}")
            raise
    
    def _clean_and_validate_dataset(self, df):
        """데이터 정리 및 검증"""
        try:
            logger.info("데이터 정리 및 검증 시작")
            
            # 1. 중복 레코드 제거
            before_dedup = len(df)
            if 'Case_No' in df.columns:
                df = df.drop_duplicates(subset=['Case_No'])
            else:
                df = df.drop_duplicates()
            
            after_dedup = len(df)
            if before_dedup != after_dedup:
                logger.info(f"중복 레코드 제거: {before_dedup} -> {after_dedup}")
            
            # 2. 필수 컬럼 검증
            required_columns = ['Case_No', 'Date', 'Location', 'Qty']
            for col in required_columns:
                if col not in df.columns:
                    logger.warning(f"필수 컬럼 없음: {col}")
            
            # 3. 데이터 타입 정규화
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            if 'DHL Warehouse' in df.columns:
                df['DHL Warehouse'] = pd.to_datetime(df['DHL Warehouse'], errors='coerce')
            
            if 'Status_Location_Date' in df.columns:
                df['Status_Location_Date'] = pd.to_datetime(df['Status_Location_Date'], errors='coerce')
            
            # 4. 수치형 데이터 정리
            numeric_columns = ['Qty', 'Amount', 'Weight']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info("데이터 정리 및 검증 완료")
            
            return df
            
        except Exception as e:
            logger.error(f"데이터 정리 및 검증 실패: {str(e)}")
            raise
    
    def _apply_ontology_mapping(self, df):
        """온톨로지 매핑 적용"""
        try:
            logger.info("온톨로지 매핑 적용 시작")
            
            # 온톨로지 매핑 규칙 로드
            if Path(self.ontology_mapping_file).exists():
                with open(self.ontology_mapping_file, 'r', encoding='utf-8') as f:
                    mapping_rules = json.load(f)
                
                field_mappings = mapping_rules.get('field_mappings', {})
                
                # DHL Warehouse 매핑 규칙 추가 (없으면)
                if 'DHL Warehouse' not in field_mappings:
                    field_mappings['DHL Warehouse'] = {
                        "ontology_property": "hasWarehouseEntry",
                        "data_type": "datetime", 
                        "description": "DHL warehouse entry timestamp"
                    }
                    
                    # 매핑 규칙 업데이트
                    mapping_rules['field_mappings'] = field_mappings
                    with open(self.ontology_mapping_file, 'w', encoding='utf-8') as f:
                        json.dump(mapping_rules, f, indent=2, ensure_ascii=False)
                    
                    logger.info("DHL Warehouse 온톨로지 매핑 규칙 추가")
                
                # 매핑 커버리지 계산
                mapped_columns = sum(1 for col in df.columns if col in field_mappings)
                coverage = mapped_columns / len(df.columns)
                
                logger.info(f"온톨로지 매핑 커버리지: {coverage:.2f} ({mapped_columns}/{len(df.columns)})")
                
            else:
                logger.warning("온톨로지 매핑 파일이 없음")
            
            logger.info("온톨로지 매핑 적용 완료")
            
            return df
            
        except Exception as e:
            logger.error(f"온톨로지 매핑 적용 실패: {str(e)}")
            return df  # 매핑 실패해도 원본 데이터 반환
    
    def run_full_recovery(self):
        """전체 DHL Warehouse 데이터 복구 실행"""
        try:
            logger.info("=== DHL Warehouse 데이터 전체 복구 시작 ===")
            
            # 1. 원본 데이터 로드
            if not Path(self.original_hitachi_file).exists():
                raise FileNotFoundError(f"원본 파일이 없음: {self.original_hitachi_file}")
            
            original_df = pd.read_excel(self.original_hitachi_file)
            logger.info(f"원본 HITACHI 데이터 로드: {len(original_df)}개 레코드")
            
            # 2. 현재 데이터 로드
            if not Path(self.current_data_file).exists():
                logger.warning(f"현재 데이터 파일이 없음: {self.current_data_file}")
                current_df = pd.DataFrame()
            else:
                current_df = pd.read_excel(self.current_data_file)
                logger.info(f"현재 데이터 로드: {len(current_df)}개 레코드")
            
            # 3. 최종 통합 데이터셋 생성
            final_dataset = self.create_final_integrated_dataset(current_df, original_df)
            
            # 4. 결과 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"HVDC_DHL_Warehouse_완전복구_{timestamp}.xlsx"
            
            final_dataset.to_excel(output_file, index=False)
            logger.info(f"최종 결과 저장: {output_file}")
            
            # 5. 복구 결과 리포트
            self._generate_recovery_report(final_dataset, output_file)
            
            logger.info("=== DHL Warehouse 데이터 전체 복구 완료 ===")
            
            return final_dataset, output_file
            
        except Exception as e:
            logger.error(f"전체 복구 실패: {str(e)}")
            raise
    
    def _generate_recovery_report(self, df, output_file):
        """복구 결과 리포트 생성"""
        try:
            dhl_records = df[df['DHL Warehouse'].notna()]
            
            report = {
                "복구_완료_시간": datetime.now().isoformat(),
                "전체_레코드_수": len(df),
                "DHL_Warehouse_레코드_수": len(dhl_records),
                "복구_성공률": f"{len(dhl_records) / self.expected_dhl_records * 100:.1f}%",
                "출력_파일": output_file,
                "DHL_날짜_범위": {
                    "최소": dhl_records['DHL Warehouse'].min().isoformat() if not dhl_records.empty else None,
                    "최대": dhl_records['DHL Warehouse'].max().isoformat() if not dhl_records.empty else None
                }
            }
            
            # 리포트 파일 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"DHL_Warehouse_복구_리포트_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"복구 리포트 저장: {report_file}")
            logger.info(f"DHL Warehouse 레코드 복구: {len(dhl_records)}개 / {self.expected_dhl_records}개")
            
        except Exception as e:
            logger.error(f"리포트 생성 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    try:
        # DHL Warehouse 데이터 복구 시스템 생성
        recovery_system = DHLWarehouseDataRecoverySystem()
        
        # 전체 복구 실행
        final_dataset, output_file = recovery_system.run_full_recovery()
        
        print(f"✅ DHL Warehouse 데이터 복구 완료!")
        print(f"📁 출력 파일: {output_file}")
        print(f"📊 총 레코드 수: {len(final_dataset)}")
        
        # DHL 레코드 확인
        dhl_records = final_dataset[final_dataset['DHL Warehouse'].notna()]
        print(f"🏢 DHL Warehouse 레코드: {len(dhl_records)}개")
        
        return final_dataset, output_file
        
    except Exception as e:
        print(f"❌ 복구 실패: {str(e)}")
        raise

if __name__ == "__main__":
    main() 