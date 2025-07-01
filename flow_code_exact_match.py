#!/usr/bin/env python3
"""
HVDC Flow Code 공식 기준 완전 일치 계산기
MACHO-GPT v3.4-mini │ Samsung C&T × ADNOC·DSV Partnership

목표: 공식 보고서와 100% 일치
- SIMENSE Code 4: 1,851건
- HITACHI Code 3: 274건, Code 4: 5건
- 총 케이스: 7,573개
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowCodeExactCalculator:
    """공식 기준 완전 일치 Flow Code 계산기"""
    
    def __init__(self):
        self.case_id_col = None
        self.wh_cols = []
        self.mosb_cols = ['MOSB']
        
        # 공식 기준 타겟
        self.official_targets = {
            'HITACHI': {'total': 5346, 'code_0': 163, 'code_1': 2062, 'code_2': 2842, 'code_3': 274, 'code_4': 5},
            'SIMENSE': {'total': 2227, 'code_0': 384, 'code_1': 804, 'code_2': 805, 'code_3': 234, 'code_4': 1851}
        }
        
    @staticmethod
    def _clean_str(val) -> str:
        """전각공백 완전 제거 + NaN 안전 처리"""
        if pd.isna(val):
            return ''
        cleaned = str(val).replace('\u3000', ' ').replace('　', ' ').strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned
    
    @classmethod
    def is_valid_data(cls, val) -> bool:
        """데이터 유효성 검증"""
        if pd.isna(val):
            return False
        cleaned = cls._clean_str(val)
        return cleaned and cleaned.lower() not in {'nan', 'none', 'nat', ''}
    
    def detect_exact_case_column(self, df: pd.DataFrame, vendor_hint: str = None) -> str:
        """정확한 Case 컬럼 감지 (공식 기준)"""
        
        logger.info(f"🔍 Case 컬럼 감지 시작 (벤더 힌트: {vendor_hint})")
        
        # 벤더별 우선순위 컬럼
        if vendor_hint == 'HITACHI':
            priority_cols = ['HVDC CODE', 'Case No.', 'HVDC_CODE', 'Case_No']
        elif vendor_hint == 'SIMENSE':
            priority_cols = ['SERIAL NO.', 'SERIAL_NO', 'SerialNo', 'HVDC CODE']
        else:
            # 일반적 우선순위
            priority_cols = ['HVDC CODE', 'SERIAL NO.', 'Case No.', 'HVDC_CODE', 'SERIAL_NO']
        
        # 1단계: 직접 매칭
        for col in priority_cols:
            if col in df.columns:
                unique_count = df[col].nunique()
                logger.info(f"✅ 발견: {col} ({unique_count:,}개 고유값)")
                
                # 공식 기준 검증
                if vendor_hint == 'HITACHI' and unique_count >= 5000:
                    return col
                elif vendor_hint == 'SIMENSE' and unique_count >= 2000:
                    return col
                elif unique_count >= 1000:
                    return col
        
        # 2단계: 패턴 매칭
        patterns = [r'HVDC.*CODE', r'SERIAL.*NO', r'Case.*No', r'.*ID$', r'.*CODE$']
        for pattern in patterns:
            matches = [col for col in df.columns if re.search(pattern, col, re.I)]
            for col in matches:
                unique_count = df[col].nunique()
                if unique_count >= 1000:
                    logger.info(f"✅ 패턴 매칭: {col} ({unique_count:,}개)")
                    return col
        
        # 3단계: 최대 고유값 컬럼
        max_col = None
        max_count = 0
        for col in df.columns:
            if df[col].dtype in ['object', 'int64', 'float64']:
                unique_count = df[col].nunique()
                if unique_count > max_count:
                    max_count = unique_count
                    max_col = col
        
        if max_col and max_count >= 500:
            logger.warning(f"⚠️ 최대값 선택: {max_col} ({max_count:,}개)")
            return max_col
        
        raise ValueError(f"적절한 Case 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼: {list(df.columns)}")
    
    def detect_exact_warehouse_columns(self, df: pd.DataFrame, vendor_hint: str = None) -> List[str]:
        """정확한 창고 컬럼 감지 (공식 기준)"""
        
        logger.info(f"🏢 WH 컬럼 감지 시작 (벤더 힌트: {vendor_hint})")
        
        # 실제 존재하는 정확한 컬럼명들
        exact_columns = {
            'HITACHI': [
                'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor',
                'AAA  Storage',  # 공백 2개 정확히
                'AAA Storage',   # 공백 1개 변형
                'Hauler Indoor', 'DSV MZP'
            ],
            'SIMENSE': [
                'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor',
                'DSV MZD', 'JDN MZD',
                'AAA  Storage',  # 공백 2개
                'AAA Storage'    # 공백 1개
            ],
            'COMMON': [
                'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz',
                'AAA Storage', 'AAA  Storage',
                'Dangerous Storage', 'Waterfront', 'Vijay Tanks'
            ]
        }
        
        wh_cols = []
        
        # 벤더별 정확한 컬럼 먼저 확인
        if vendor_hint in exact_columns:
            search_list = exact_columns[vendor_hint]
        else:
            search_list = exact_columns['COMMON']
        
        # 1단계: 정확한 매칭
        for exact_col in search_list:
            if exact_col in df.columns:
                wh_cols.append(exact_col)
                logger.info(f"✅ 정확 매칭: {exact_col}")
        
        # 2단계: 패턴 매칭 (추가 감지)
        wh_patterns = [
            r'^DSV\s+Indoor$', r'^DSV\s+Outdoor$', r'^DSV\s+Al\s+Markaz$',
            r'^DSV\s+MZP$', r'^DSV\s+MZD$', r'^JDN\s+MZD$',
            r'^AAA\s+Storage$', r'^AAA\s\s+Storage$',  # 공백 1개, 2개
            r'^Hauler\s+Indoor$', r'^Dangerous\s+Storage$'
        ]
        
        for col in df.columns:
            if col not in wh_cols:  # 중복 방지
                col_clean = self._clean_str(col)
                for pattern in wh_patterns:
                    if re.match(pattern, col_clean, re.I):
                        wh_cols.append(col)
                        logger.info(f"✅ 패턴 매칭: {col}")
                        break
        
        # 3단계: 유연한 패턴 (백업)
        if len(wh_cols) < 3:
            flexible_patterns = [r'DSV', r'AAA', r'Hauler', r'MZP', r'MZD']
            for col in df.columns:
                if col not in wh_cols:
                    for pattern in flexible_patterns:
                        if re.search(pattern, col, re.I):
                            wh_cols.append(col)
                            logger.info(f"⚠️ 유연 매칭: {col}")
                            break
        
        logger.info(f"📋 최종 WH 컬럼 ({len(wh_cols)}개): {wh_cols}")
        
        if len(wh_cols) < 3:
            logger.error(f"❌ WH 컬럼 부족: {len(wh_cols)}개")
            logger.error(f"사용 가능한 모든 컬럼: {list(df.columns)}")
        
        return wh_cols
    
    def build_exact_route(self, group: pd.DataFrame) -> List[str]:
        """정확한 경로 구성 (공식 기준)"""
        
        if 'Date' in group.columns:
            group = group.sort_values('Date')
        
        route = ['port']
        
        # 방문한 창고들 추적
        visited_warehouses = set()
        
        for _, row in group.iterrows():
            for wh_col in self.wh_cols:
                if self.is_valid_data(row.get(wh_col)):
                    visited_warehouses.add(wh_col)
        
        # 창고 단계 추가 (고유한 창고 수만큼)
        warehouse_count = len(visited_warehouses)
        route.extend(['warehouse'] * warehouse_count)
        
        # MOSB 확인
        mosb_present = False
        for _, row in group.iterrows():
            if self.is_valid_data(row.get('MOSB')):
                mosb_present = True
                break
        
        if mosb_present:
            route.append('offshore')
        
        route.append('site')
        
        return route
    
    def route_to_exact_flow_code(self, route: List[str]) -> int:
        """경로를 정확한 Flow Code로 변환"""
        
        warehouse_count = route.count('warehouse')
        has_offshore = 'offshore' in route
        
        if warehouse_count == 0:
            return 1  # Port → Site
        elif warehouse_count == 1 and not has_offshore:
            return 2  # Port → WH → Site
        elif warehouse_count == 1 and has_offshore:
            return 3  # Port → WH → MOSB → Site
        elif warehouse_count >= 2 and has_offshore:
            return 4  # Port → WH × 2+ → MOSB → Site
        elif warehouse_count >= 2 and not has_offshore:
            return 2  # Port → WH × 2+ → Site (복수 창고, offshore 없음)
        else:
            return 1
    
    def calculate_exact_flow_codes(self, df: pd.DataFrame, vendor_hint: str = None) -> pd.DataFrame:
        """정확한 Flow Code 계산 (공식 기준)"""
        
        logger.info(f"🎯 공식 기준 Flow Code 계산 시작 (벤더: {vendor_hint})")
        
        # 1. 정확한 Case 컬럼 감지
        self.case_id_col = self.detect_exact_case_column(df, vendor_hint)
        logger.info(f"📋 선택된 Case 컬럼: {self.case_id_col}")
        
        # 2. 정확한 WH 컬럼 감지
        self.wh_cols = self.detect_exact_warehouse_columns(df, vendor_hint)
        
        # 3. MOSB 컬럼 처리
        if 'MOSB' not in df.columns:
            df['MOSB'] = pd.NA
        
        # 4. Case별 그룹화 및 계산
        total_cases = df[self.case_id_col].nunique()
        logger.info(f"📊 총 Case 수: {total_cases:,}개")
        
        # 공식 기준과 비교
        if vendor_hint in self.official_targets:
            expected = self.official_targets[vendor_hint]['total']
            if abs(total_cases - expected) > 100:
                logger.warning(f"⚠️ Case 수 차이: 실제 {total_cases:,} vs 기대 {expected:,}")
        
        # Flow Code 계산
        flow_codes = []
        routes_debug = []
        
        for case_id, group in df.groupby(self.case_id_col):
            route = self.build_exact_route(group)
            flow_code = self.route_to_exact_flow_code(route)
            
            for _ in range(len(group)):
                flow_codes.append(flow_code)
                routes_debug.append(' → '.join(route))
        
        df['Flow_Code_Exact'] = flow_codes
        df['Route_Debug'] = routes_debug
        
        # 결과 검증
        self.validate_exact_results(df, vendor_hint)
        
        return df
    
    def validate_exact_results(self, df: pd.DataFrame, vendor_hint: str = None):
        """정확한 결과 검증"""
        
        flow_dist = df['Flow_Code_Exact'].value_counts().sort_index()
        
        logger.info(f"📊 계산된 Flow Code 분포:")
        for code in range(5):
            count = flow_dist.get(code, 0)
            logger.info(f"   Code {code}: {count:,}건")
        
        # 공식 기준과 비교
        if vendor_hint in self.official_targets:
            target = self.official_targets[vendor_hint]
            logger.info(f"\n🎯 공식 기준 대비 검증 ({vendor_hint}):")
            
            for i in range(5):
                actual = flow_dist.get(i, 0)
                expected = target[f'code_{i}']
                diff = actual - expected
                accuracy = (actual / expected * 100) if expected > 0 else 100
                
                status = "✅" if abs(diff) <= 10 else "⚠️" if abs(diff) <= 50 else "❌"
                logger.info(f"   Code {i}: {actual:,} / {expected:,} ({diff:+,}) {status}")
        
        # Code 3-4 특별 검증
        code3_count = flow_dist.get(3, 0)
        code4_count = flow_dist.get(4, 0)
        
        if vendor_hint == 'SIMENSE' and code4_count < 1500:
            logger.error(f"❌ SIMENSE Code 4 부족: {code4_count} < 1,851 (기대)")
        elif vendor_hint == 'HITACHI' and code3_count < 200:
            logger.error(f"❌ HITACHI Code 3 부족: {code3_count} < 274 (기대)")
        else:
            logger.info(f"✅ Code 3-4 검증 통과")


def process_exact_file(file_path: str, vendor_hint: str = None) -> pd.DataFrame:
    """파일별 정확한 처리"""
    
    logger.info(f"📄 파일 처리: {file_path}")
    
    df = pd.read_excel(file_path)
    
    # 벤더 힌트 자동 감지
    if not vendor_hint:
        if 'HITACHI' in file_path.upper() or 'HE' in Path(file_path).stem:
            vendor_hint = 'HITACHI'
        elif 'SIMENSE' in file_path.upper() or 'SIM' in Path(file_path).stem:
            vendor_hint = 'SIMENSE'
    
    calculator = FlowCodeExactCalculator()
    df_result = calculator.calculate_exact_flow_codes(df, vendor_hint)
    
    # 벤더 컬럼 추가
    df_result['Vendor'] = vendor_hint if vendor_hint else 'UNKNOWN'
    
    return df_result


def generate_exact_summary(df: pd.DataFrame) -> pd.DataFrame:
    """정확한 요약 생성"""
    
    # Flow Code 분포 피벗
    summary = pd.crosstab(
        df['Vendor'], 
        df['Flow_Code_Exact'], 
        margins=True, 
        margins_name='Total'
    )
    
    # 컬럼명 정리
    summary.columns = [f'Code {int(c)}' if isinstance(c, (int, float)) else str(c) 
                      for c in summary.columns]
    
    return summary


def run_exact_match_analysis():
    """공식 기준 완전 일치 분석 실행"""
    
    print("🎯 Flow Code 공식 기준 완전 일치 분석")
    print("=" * 60)
    
    input_files = [
        ("data/HVDC WAREHOUSE_HITACHI(HE).xlsx", "HITACHI"),
        ("data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx", "SIMENSE")
    ]
    
    all_results = []
    
    for file_path, vendor in input_files:
        if Path(file_path).exists():
            try:
                df_result = process_exact_file(file_path, vendor)
                all_results.append(df_result)
                print(f"✅ {vendor} 처리 완료")
            except Exception as e:
                print(f"❌ {vendor} 처리 실패: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️ 파일 없음: {file_path}")
    
    if not all_results:
        print("❌ 처리할 파일이 없습니다.")
        return
    
    # 결과 통합
    combined_df = pd.concat(all_results, ignore_index=True)
    summary = generate_exact_summary(combined_df)
    
    print(f"\n📊 최종 결과 (공식 기준 대비):")
    print(summary)
    
    # 최종 검증
    print(f"\n🏆 공식 기준 달성 여부:")
    
    targets = {
        'HITACHI': {'Code 3': 274, 'Code 4': 5},
        'SIMENSE': {'Code 3': 234, 'Code 4': 1851}
    }
    
    success_count = 0
    total_checks = 4
    
    for vendor, target_codes in targets.items():
        if vendor in summary.index:
            for code, expected in target_codes.items():
                if code in summary.columns:
                    actual = summary.loc[vendor, code]
                    accuracy = (actual / expected * 100) if expected > 0 else 100
                    
                    if 90 <= accuracy <= 110:  # ±10% 허용
                        status = "✅"
                        success_count += 1
                    else:
                        status = "❌"
                    
                    print(f"   {vendor} {code}: {actual:,} / {expected:,} ({accuracy:.1f}%) {status}")
    
    overall_success = (success_count / total_checks) * 100
    print(f"\n📈 전체 달성률: {overall_success:.1f}% ({success_count}/{total_checks})")
    
    if overall_success >= 75:
        print("🎉 공식 기준 달성 성공!")
    else:
        print("⚠️ 추가 조정 필요")
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"HVDC_FlowCode_EXACT_MATCH_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        summary.to_excel(writer, sheet_name='공식기준_요약')
        
        for vendor in ['HITACHI', 'SIMENSE']:
            vendor_data = combined_df[combined_df['Vendor'] == vendor]
            if not vendor_data.empty:
                vendor_data.head(1000).to_excel(writer, sheet_name=f'{vendor}_상세', index=False)
    
    print(f"\n💾 결과 저장: {output_file}")
    
    return combined_df, summary


if __name__ == "__main__":
    run_exact_match_analysis() 