#!/usr/bin/env python3
"""
Event-Based Outbound Processor (v0.4) for HVDC Project
-----------------------------------------------------
* 목적: DSV Indoor → DSV Al Markaz 등 다단계 창고 이동 시 최종 위치(final_location) 정밀 산출
* 특징:
  1. WH_PRIORITY 테이블에 정의된 창고 체인(Indoor→Main WH 등) 우선순위 기반 이동 판별
  2. 두 컬럼 모두 날짜가 있는 경우 **최신 날짜**를 최종 위치로 선정
  3. 결과 컬럼 `final_location` 및 `final_location_date` 자동 생성
  4. CLI: --rebuild-final-location [--input FILE] [--output FILE]
  5. TDD 방식으로 개발된 창고 입출고 계산 로직 (v2.8.2-hotfix-EB-004 호환)

사용 예)
$ python event_based_outbound.py --rebuild-final-location --input stock_raw.xlsx --output stock_final.xlsx
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import argparse
import yaml
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------
# CONFIG
# -----------------------------
# (Indoor, 최종창고) 튜플 우선순위 목록 – 필요 시 확장
WH_PRIORITY: List[Tuple[str, str]] = [
    ("DSV Indoor", "DSV Al Markaz"),
    ("DHL Warehouse", "DSV Indoor"),  # 예시 – 실제 필요 시 수정
    ("Hauler Indoor", "DSV Outdoor"),
    ("AAA Storage", "DSV MZP"),
]

class EventBasedOutboundResolver:
    """이벤트 기반 출고 로직 해결기 (v0.4)"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        초기화
        
        Args:
            config_path: 창고 우선순위 설정 파일 경로
        """
        self.warehouse_columns = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP', 
            'AAA Storage', 'Hauler Indoor', 'MOSB', 'DHL Warehouse'
        ]
        
        self.site_columns = [
            'MIR', 'SHU', 'DAS', 'AGI', 'Direct Delivery'
        ]
        
        # 기본 창고 우선순위 (config 파일이 없을 때)
        self.default_warehouse_priority = [
            'DSV Indoor',
            'DSV Al Markaz',
            'DSV Outdoor',
            'DSV MZP',
            'AAA Storage',
            'Hauler Indoor',
            'MOSB',
            'DHL Warehouse'
        ]
        
        # 설정 파일 로드
        self.warehouse_priority = self._load_warehouse_priority(config_path)
        
        # v0.4: WH_PRIORITY 튜플 설정
        self.wh_priority_tuples = WH_PRIORITY
        
        logger.info(f"EventBasedOutboundResolver v0.4 초기화 완료")
        logger.info(f"창고 우선순위: {self.warehouse_priority}")
        logger.info(f"창고 체인 우선순위: {self.wh_priority_tuples}")
    
    def _load_warehouse_priority(self, config_path: Optional[str]) -> List[str]:
        """창고 우선순위 설정 로드"""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    return config.get('warehouse_priority', self.default_warehouse_priority)
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패: {e}, 기본값 사용")
                return self.default_warehouse_priority
        else:
            return self.default_warehouse_priority

    def _choose_latest(self, row: pd.Series, col_a: str, col_b: str) -> str:
        """두 날짜 중 늦은 날짜의 컬럼명을 반환"""
        if col_a not in row.index or col_b not in row.index:
            return col_a if col_a in row.index else col_b
            
        date_a, date_b = row[col_a], row[col_b]
        if pd.isna(date_a):
            return col_b
        if pd.isna(date_b):
            return col_a
        
        # 날짜 변환 시도
        try:
            if isinstance(date_a, str):
                date_a = pd.to_datetime(date_a)
            if isinstance(date_b, str):
                date_b = pd.to_datetime(date_b)
            return col_a if date_a >= date_b else col_b
        except:
            # 날짜 변환 실패 시 첫 번째 우선
            return col_a

    def _determine_final_location(self, row: pd.Series) -> str:
        """v0.4: 우선순위 체인에 따라 최종 위치를 결정"""
        
        # 1. 현장 날짜 확인 (최우선)
        for site_col in self.site_columns:
            if site_col in row.index and pd.notna(row[site_col]):
                return site_col
        
        # 2. v0.4: 창고 체인 우선순위 확인
        for indoor, dest in self.wh_priority_tuples:
            if indoor in row.index and dest in row.index:
                if pd.notna(row[indoor]) and pd.notna(row[dest]):
                    return self._choose_latest(row, indoor, dest)
                if pd.notna(row[dest]):
                    return dest
                if pd.notna(row[indoor]):
                    return indoor
        
        # 3. 기본 창고 우선순위 확인
        for warehouse_col in self.warehouse_priority:
            if warehouse_col in row.index and pd.notna(row[warehouse_col]):
                return warehouse_col
        
        # 4. 기타 창고 확인 (우선순위에 없는 창고)
        for warehouse_col in self.warehouse_columns:
            if warehouse_col not in self.warehouse_priority:
                if warehouse_col in row.index and pd.notna(row[warehouse_col]):
                    return warehouse_col
        
        # 5. 다른 컬럼들 중 최초로 값이 있는 곳 반환
        for col, val in row.items():
            if pd.notna(val) and col not in ("Pkg", "final_location", "final_location_date", "Case No.", "HVDC CODE"):
                return col
        
        # 6. 모두 없으면 Unknown
        return 'Unknown'

    def resolve_final_location(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Final_Location 해결 - 핵심 함수 (v0.4 enhanced)
        
        Args:
            df: HVDC 데이터프레임
            
        Returns:
            Final_Location 및 final_location_date 컬럼이 추가된 데이터프레임
        
        로직:
        1. 현장 날짜가 있으면 → 현장명
        2. 창고 체인(Indoor→Dest) 우선순위에 따라 최신 날짜 위치 선정
        3. 기본 창고 우선순위 적용
        4. 둘 다 없으면 → 'Unknown'
        """
        logger.info(f"Final_Location 해결 시작 (v0.4) - 총 {len(df)} 건")
        
        result_df = df.copy()
        
        # v0.4: 날짜 컬럼 자동 변환
        result_df = self._auto_parse_dates(result_df)
        
        final_locations = []
        final_location_dates = []
        
        # 통계 변수
        site_count = 0
        warehouse_count = 0
        unknown_count = 0
        
        for idx, row in result_df.iterrows():
            final_location = self._determine_final_location(row)
            final_locations.append(final_location)
            
            # v0.4: 최종 위치 날짜 추출
            final_date = row.get(final_location, pd.NaT) if final_location != 'Unknown' else pd.NaT
            final_location_dates.append(final_date)
            
            # 통계 업데이트
            if final_location in self.site_columns:
                site_count += 1
            elif final_location in self.warehouse_columns:
                warehouse_count += 1
            else:
                unknown_count += 1
        
        result_df['Final_Location'] = final_locations
        result_df['final_location_date'] = final_location_dates
        
        # 결과 로깅
        logger.info(f"Final_Location 해결 완료 (v0.4):")
        logger.info(f"  - 현장 배송: {site_count} 건")
        logger.info(f"  - 창고 보관: {warehouse_count} 건")
        logger.info(f"  - 미확인: {unknown_count} 건")
        
        return result_df

    def _auto_parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """YYYY-MM-DD 패턴 칼럼을 datetime으로 변환"""
        for col in df.columns:
            if col in self.warehouse_columns + self.site_columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        return df

    def rebuild_final_location(self, input_file: str, output_file: str = None) -> str:
        """
        Final_Location 재구성 - CLI에서 호출되는 메인 함수 (v0.4)
        
        Args:
            input_file: 입력 엑셀 파일 경로
            output_file: 출력 엑셀 파일 경로 (None이면 자동 생성)
            
        Returns:
            출력 파일 경로
        """
        logger.info(f"Final_Location 재구성 시작 (v0.4): {input_file}")
        
        try:
            # 데이터 로드
            if input_file.endswith('.xlsx') or input_file.endswith('.xls'):
                # 엑셀 파일의 첫 번째 시트 로드
                excel_file = pd.ExcelFile(input_file)
                sheet_name = excel_file.sheet_names[0]
                df = pd.read_excel(input_file, sheet_name=sheet_name)
                logger.info(f"엑셀 시트 '{sheet_name}' 로드 완료: {len(df)} 행")
            else:
                df = pd.read_csv(input_file)
                logger.info(f"CSV 파일 로드 완료: {len(df)} 행")
            
            # Final_Location 해결
            result_df = self.resolve_final_location(df)
            
            # 출력 파일명 생성
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                input_path = Path(input_file)
                output_file = str(input_path.parent / f"{input_path.stem}_final_location_{timestamp}.xlsx")
            
            # 결과 저장
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                result_df.to_excel(writer, sheet_name='Final_Location_Resolved', index=False)
                
                # 통계 시트 추가
                stats_df = self._generate_final_location_stats(result_df)
                stats_df.to_excel(writer, sheet_name='Final_Location_Stats', index=False)
            
            logger.info(f"Final_Location 재구성 완료 (v0.4): {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Final_Location 재구성 중 오류: {str(e)}")
            raise
    
    def _generate_final_location_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final_Location 통계 생성 (v0.4 enhanced)"""
        stats = df['Final_Location'].value_counts().reset_index()
        stats.columns = ['Final_Location', 'Count']
        
        # 비율 계산
        stats['Percentage'] = (stats['Count'] / len(df) * 100).round(2)
        
        # 카테고리 분류
        stats['Category'] = stats['Final_Location'].apply(
            lambda x: 'Site' if x in self.site_columns 
                     else 'Warehouse' if x in self.warehouse_columns 
                     else 'Unknown'
        )
        
        # v0.4: 날짜 통계 추가
        if 'final_location_date' in df.columns:
            date_stats = df.groupby('Final_Location')['final_location_date'].agg(['count', 'min', 'max']).reset_index()
            date_stats.columns = ['Final_Location', 'Date_Count', 'Earliest_Date', 'Latest_Date']
            stats = stats.merge(date_stats, on='Final_Location', how='left')
        
        return stats

# -----------------------------
# v0.4 STANDALONE FUNCTIONS
# -----------------------------

def _choose_latest(row: pd.Series, col_a: str, col_b: str) -> str:
    """두 날짜 중 늦은 날짜의 컬럼명을 반환"""
    date_a, date_b = row[col_a], row[col_b]
    if pd.isna(date_a):
        return col_b
    if pd.isna(date_b):
        return col_a
    return col_a if date_a >= date_b else col_b

def resolve_final_location_standalone(row: pd.Series) -> str:
    """v0.4: 우선순위 체인에 따라 최종 위치를 결정 (standalone)"""
    for indoor, dest in WH_PRIORITY:
        if pd.notna(row[indoor]) and pd.notna(row[dest]):
            return _choose_latest(row, indoor, dest)
        if pd.notna(row[dest]):
            return dest
        if pd.notna(row[indoor]):
            return indoor
    # 다른 창고/현장 컬럼들 중 최초로 값이 있는 곳 반환
    for col, val in row.items():
        if pd.notna(val) and col not in ("Pkg", "final_location", "final_location_date"):
            return col
    return "Unknown"

def rebuild_final_location_standalone(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame에 final_location / final_location_date 컬럼 추가 후 반환 (standalone)"""
    df = df.copy()
    df["final_location"] = df.apply(resolve_final_location_standalone, axis=1)
    # 최종 위치 날짜 추출: 해당 컬럼의 날짜 값
    df["final_location_date"] = df.apply(
        lambda r: r.get(r["final_location"], pd.NaT), axis=1
    )
    return df

def _auto_parse_dates_standalone(df: pd.DataFrame) -> pd.DataFrame:
    """YYYY-MM-DD 패턴 칼럼을 datetime으로 변환 (standalone)"""
    for col in df.columns:
        if df[col].astype(str).str.match(r"\d{4}-\d{2}-\d{2}").any():
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

# -----------------------------
# CLI
# -----------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description='HVDC Event-Based Outbound Logic v0.4 - Final_Location Resolver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python event_based_outbound.py --rebuild-final-location input.xlsx
  python event_based_outbound.py --rebuild-final-location input.xlsx --output output.xlsx
  python event_based_outbound.py --rebuild-final-location input.xlsx --config config/wh_priority.yaml
  
v0.4 새로운 사용법:
  python event_based_outbound.py --rebuild-final-location --input stock_raw.xlsx --output stock_final.xlsx
        """
    )
    
    parser.add_argument(
        '--rebuild-final-location',
        nargs='?',
        const=True,
        help='Final_Location을 재구성할 엑셀 파일 경로 (v0.4: --input과 함께 사용 가능)'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='v0.4: 입력 파일 경로 (Excel/CSV)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='출력 파일 경로 (선택사항, 미지정시 자동 생성)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='창고 우선순위 설정 파일 경로 (YAML)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='상세 로그 출력'
    )
    
    args = parser.parse_args()
    
    # 로깅 레벨 설정
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 명령어 처리
    if args.rebuild_final_location:
        try:
            # v0.4: --input 옵션 지원
            if args.input:
                input_file = args.input
            elif isinstance(args.rebuild_final_location, str):
                input_file = args.rebuild_final_location
            else:
                parser.error("입력 파일을 지정해주세요: --rebuild-final-location FILE 또는 --input FILE")
            
            # 입력 파일 존재 확인
            if not Path(input_file).exists():
                raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_file}")
            
            resolver = EventBasedOutboundResolver(config_path=args.config)
            output_file = resolver.rebuild_final_location(
                input_file=input_file,
                output_file=args.output
            )
            print(f"Final_Location 재구성 완료 (v0.4): {output_file}")
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            return 1
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 