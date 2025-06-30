#!/usr/bin/env python3
"""
HVDC Flow Code 계산 알고리즘 v2.8.1
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics
Purpose: Path-scanner 기반 다중 경유 인식 + MOSB 플래그 지원
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FlowCodeCalculatorV2:
    
    # ---- v2.8.2 핫픽스: 실데이터에서 확인된 전용 컬럼 ----
    WH_COLS   = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz']
    MOSB_COLS = ['MOSB']          # 필요시 확장: 'Marine Base', 'Offshore Base' …

    # ------------------------------------------------------------------
    # 🩹 2025-06-30 Hot-Fix:  전각공백·NaN 안전 문자열 클리너
    # ------------------------------------------------------------------
    @staticmethod
    def _clean_str(val) -> str:
        """U+3000(전각공백) 제거 + strip. NaN → '' """
        if pd.isna(val):
            return ''
        # 전각공백 및 다양한 공백 문자 제거
        cleaned = str(val).replace('\u3000', ' ').replace('　', ' ').strip()
        # 연속된 공백을 단일 공백으로 변환
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    @classmethod
    def is_valid_data(cls, val) -> bool:
        """공백/NaN/None 제외한 실제 값 여부 판정"""
        cleaned = cls._clean_str(val)
        return cleaned and cleaned.lower() not in {'nan', 'none'}
    """개선된 Flow Code 계산기 v2"""
    
    def __init__(self):
        # 위치 분류 규칙
        self.location_types = {
            'port': ['PORT', 'JEBEL ALI', 'HAMAD PORT'],
            'warehouse': ['DSV INDOOR', 'DSV OUTDOOR', 'DSV AL MARKAZ', 'DSV MZP', 'HAULER INDOOR'],
            'offshore': ['MOSB', 'MARINE BASE', 'OFFSHORE BASE', 'MARINE OFFSHORE'],
            'site': ['AGI', 'DAS', 'MIR', 'SHU'],
            'pre_arrival': ['PRE ARRIVAL', 'INBOUND_PENDING', 'NOT_YET_RECEIVED']
        }
        
        # 경로 패턴 정의
        self.flow_patterns = {
            0: ['pre_arrival'],                                    # Pre Arrival
            1: ['port', 'site'],                                   # Port→Site
            2: ['port', 'warehouse', 'site'],                      # Port→WH→Site  
            3: ['port', 'warehouse', 'offshore', 'site'],          # Port→WH→MOSB→Site
            4: ['port', 'warehouse', 'warehouse', 'offshore', 'site']  # Port→WH→wh→MOSB→Site
        }
    
    def classify_location_type(self, location: str) -> str:
        """
        위치를 타입으로 분류
        v2.8.1 패치: 전각공백(\u3000) 처리 추가
        """
        # v2.8.2 핫픽스: _clean_str로 전각공백 제거
        loc = self._clean_str(location).upper()
        if not loc:
            return "unknown"
        
        # 정확한 매칭 먼저 시도
        for loc_type, patterns in self.location_types.items():
            for pattern in patterns:
                if pattern.upper() == loc:
                    return loc_type
        
        # 부분 매칭
        for loc_type, patterns in self.location_types.items():
            for pattern in patterns:
                if pattern.upper() in loc:
                    return loc_type
        
        # 휴리스틱 매칭
        if any(keyword in loc for keyword in ['WAREHOUSE', 'WH', 'STORAGE']):
            return 'warehouse'
        if any(keyword in loc for keyword in ['SITE', 'PLANT', 'FACILITY']):
            return 'site'
        if any(keyword in loc for keyword in ['OFFSHORE', 'MARINE', 'MOSB']):
            return 'offshore'
        
        return 'unknown'
    
    def extract_route_from_record(self, record: Dict) -> List[str]:
        """
        레코드에서 경로 추출
        v2.8.2 핫픽스: 다중 WH 및 MOSB 인식 완전 개선
        """
        route: List[str] = []

        # 0. Location 1차 판별 (기존 유지)
        location_type = self.classify_location_type(
            self._clean_str(record.get('Location', ''))
        )
        if location_type == 'pre_arrival':
            return ['pre_arrival']

        # 1. Port (항상 시작)
        route.append('port')

        # 2. 다중 WH 계산 (실제 0~2단계)
        wh_count = 0
        for col in self.WH_COLS:
            if self.is_valid_data(record.get(col)):
                wh_count += 1
        route.extend(['warehouse'] * wh_count)

        # 3. MOSB 단계 (날짜값·전각공백 포함 판정)
        mosb_present = any(
            self.is_valid_data(record.get(c)) for c in self.MOSB_COLS
        )
        if mosb_present:
            route.append('offshore')

        # 4. Site (항상 종료)
        route.append('site')

        return route
    
    def extract_route_from_history(self, case_no: str, history_df: pd.DataFrame = None) -> List[str]:
        """이력 데이터에서 경로 추출 (향후 확장용)"""
        if history_df is None:
            return []
        
        # Case No 기준 이력 필터링
        case_history = history_df[history_df['Case_No'] == case_no].sort_values('Date')
        
        route = ['port']  # 시작은 항상 port
        
        for _, row in case_history.iterrows():
            location_type = self.classify_location_type(row.get('Location', ''))
            if location_type not in ['unknown', 'port'] and location_type not in route:
                route.append(location_type)
        
        # 최종 목적지가 site가 아니면 추가
        if route[-1] != 'site':
            route.append('site')
        
        return route
    
    def match_route_to_flow_code(self, route: List[str]) -> int:
        """경로를 Flow Code로 매핑"""
        # Pre Arrival 체크
        if 'pre_arrival' in route:
            return 0
        
        # 정확한 패턴 매칭
        for code, pattern in self.flow_patterns.items():
            if route == pattern:
                return code
        
        # 유사 패턴 매칭
        route_str = '→'.join(route)
        
        # Code 1: Port→Site (직송)
        if len(route) == 2 and 'warehouse' not in route and 'offshore' not in route:
            return 1
        
        # Code 2: 창고 경유, 해상기지 없음
        if 'warehouse' in route and 'offshore' not in route:
            return 2
        
        # Code 3: 해상기지 포함, 창고 1개
        if 'offshore' in route and route.count('warehouse') == 1:
            return 3
        
        # Code 4: 해상기지 포함, 창고 2개 이상
        if 'offshore' in route and route.count('warehouse') >= 2:
            return 4
        
        # 기본값: 창고 경유로 간주
        return 2
    
    def calc_flow_code_v2(self, record: Dict, history_df: pd.DataFrame = None) -> Dict:
        """개선된 Flow Code 계산 (v2)"""
        try:
            # 1. 기본 경로 추출
            route = self.extract_route_from_record(record)
            
            # 2. 이력 기반 경로 보강 (옵션)
            if history_df is not None:
                history_route = self.extract_route_from_history(record.get('Case_No', ''), history_df)
                if len(history_route) > len(route):
                    route = history_route
            
            # 3. Flow Code 계산
            flow_code = self.match_route_to_flow_code(route)
            
            # 4. 상세 정보 반환
            return {
                'flow_code': flow_code,
                'route': route,
                'route_string': '→'.join(route),
                'location_type': self.classify_location_type(record.get('Location', '')),
                'confidence': self._calculate_confidence(record, route, flow_code)
            }
            
        except Exception as e:
            logger.error(f"Flow Code 계산 오류: {e}")
            return {
                'flow_code': 1,  # 기본값
                'route': ['port', 'site'],
                'route_string': 'port→site',
                'location_type': 'unknown',
                'confidence': 0.5
            }
    
    def _calculate_confidence(self, record: Dict, route: List[str], flow_code: int) -> float:
        """신뢰도 계산"""
        confidence = 1.0
        
        # Location 정보 없으면 신뢰도 감소
        if not record.get('Location'):
            confidence -= 0.3
        
        # Status 정보 없으면 신뢰도 감소
        if not record.get('Status'):
            confidence -= 0.2
        
        # 경로가 너무 단순하면 신뢰도 감소
        if len(route) < 2:
            confidence -= 0.2
        
        # Pre Arrival은 높은 신뢰도
        if flow_code == 0:
            confidence = max(confidence, 0.95)
        
        return max(confidence, 0.1)
    
    def add_flow_code_v2_to_dataframe(self, df: pd.DataFrame, history_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        DataFrame에 개선된 Flow Code 추가
        v2.8.1 패치: 전처리 훅 추가 (전각공백·NaN 제거)
        """
        logger.info("🚀 Flow Code v2 계산 시작...")
        
        # ★ v2.8.2 핫픽스: 모든 문자열 컬럼 정규화 (전각공백·NaN 제거)
        df = df.copy()
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].apply(self._clean_str)
        
        logger.info("✅ 전각공백 정규화 완료")
        
        results = []
        for _, row in df.iterrows():
            record = row.to_dict()
            result = self.calc_flow_code_v2(record, history_df)
            results.append(result)
        
        # 결과 컬럼 추가
        df['Logistics_Flow_Code_V2'] = [r['flow_code'] for r in results]
        df['Flow_Route'] = [r['route_string'] for r in results]
        df['Flow_Confidence'] = [r['confidence'] for r in results]
        df['Location_Type'] = [r['location_type'] for r in results]
        
        # 통계 로그
        flow_counts = df['Logistics_Flow_Code_V2'].value_counts().sort_index()
        avg_confidence = df['Flow_Confidence'].mean()
        
        logger.info(f"✅ Flow Code v2 계산 완료")
        logger.info(f"   분포: {dict(flow_counts)}")
        logger.info(f"   평균 신뢰도: {avg_confidence:.3f}")
        
        return df

# 편의 함수들
def calc_flow_code_v2(record: Dict, history_df: pd.DataFrame = None) -> int:
    """편의 함수: 단일 레코드 Flow Code 계산"""
    calculator = FlowCodeCalculatorV2()
    result = calculator.calc_flow_code_v2(record, history_df)
    return result['flow_code']

def add_flow_code_v2_to_dataframe(df: pd.DataFrame, history_df: pd.DataFrame = None) -> pd.DataFrame:
    """편의 함수: DataFrame Flow Code v2 추가"""
    calculator = FlowCodeCalculatorV2()
    return calculator.add_flow_code_v2_to_dataframe(df, history_df)

# 테스트 함수
def test_flow_code_v2():
    """Flow Code v2 테스트"""
    calculator = FlowCodeCalculatorV2()
    
    test_cases = [
        # (레코드, 예상 코드, 설명)
        ({'Status': 'PRE ARRIVAL', 'Location': 'PRE ARRIVAL'}, 0, "Pre Arrival"),
        ({'Status': 'Active', 'Location': 'AGI'}, 1, "Port→Site 직송"),
        ({'Status': 'Active', 'Location': 'DSV Indoor'}, 2, "Port→WH→Site"),
        ({'Status': 'Active', 'Location': 'MOSB'}, 3, "Port→WH→MOSB→Site"),
        ({'Status': 'Active', 'Location': 'OFFSHORE BASE'}, 3, "Port→WH→OffshoreBase→Site"),
    ]
    
    print("🧪 Flow Code v2 테스트 시작")
    print("=" * 50)
    
    for record, expected, description in test_cases:
        result = calculator.calc_flow_code_v2(record)
        actual = result['flow_code']
        status = "✅" if actual == expected else "❌"
        
        print(f"{status} {description}")
        print(f"   입력: {record}")
        print(f"   경로: {result['route_string']}")
        print(f"   코드: {actual} (예상: {expected})")
        print(f"   신뢰도: {result['confidence']:.3f}")
        print()

if __name__ == "__main__":
    test_flow_code_v2() 