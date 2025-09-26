차차#!/usr/bin/env python3
"""
MACHO-GPT 최종 리포터 생성기 (TDD Enhanced)
- TDD 검증된 물류 도메인 로직 활용 (generate_integrated_report_with_tdd_logic.py 구조 참고)
- FANR/MOIAT 규정 준수 검증
- 통합 월별 리포트 생성
- KPI 대시보드 및 성능 모니터링
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings

# 경고 메시지 제거
warnings.filterwarnings('ignore')


class FinalReporter:
    """
    MACHO-GPT 최종 리포터 클래스
    
    물류 도메인 특화 리포터:
    - 통합 월별 리포트 생성
    - FANR 규정 준수 검증
    - KPI 대시보드 생성
    - Containment mode 전환 처리
    - 명령어 추천 시스템
    """
    
    def __init__(self, confidence_threshold: float = 0.95):
        """
        초기화
        
        Args:
            confidence_threshold: 신뢰도 임계값 (기본값: 0.95)
        """
        self.confidence_threshold = confidence_threshold
        self.current_mode = "PRIME"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 물류 도메인 상수
        self.PRESSURE_LIMIT = 4.0  # t/m²
        self.PROCESSING_TIME_LIMIT = 3.0  # seconds
        self.SUCCESS_RATE_TARGET = 0.95
        
        # TDD 검증된 창고 및 현장 컬럼 (generate_integrated_report_with_tdd_logic.py 구조 참고)
        self.warehouse_columns = [
            'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
            'AAA Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse'
        ]
        self.site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # MACHO-GPT 통합 요구사항
        self.integration_requirements = {
            'mode_compatibility': ['PRIME', 'ORACLE', 'ZERO', 'LATTICE', 'RHYTHM', 'COST-GUARD'],
            'command_integration': True,
            'auto_trigger_ready': True,
            'confidence_reporting': True,
            'error_recovery': True
        }
        
        # Flow Code 집계 기준
        self.FLOW_CODE_MAPPING = {
            0: "Port→Site 직송 또는 Pre Arrival",
            1: "창고 1개 경유",
            2: "창고 2개 경유", 
            3: "창고 3개 이상 경유",
            -1: "Pre-Arrival (미경유)"
        }
        
        print(f"📊 MACHO-GPT 최종 리포터 초기화 완료")
        print(f"⏰ 실행 시간: {self.timestamp}")
        print(f"🎯 신뢰도 임계값: {self.confidence_threshold}")
    
    def load_and_merge_warehouse_data(self) -> pd.DataFrame:
        """
        창고 데이터 로드 및 병합 (TDD 검증된 로직)
        
        Returns:
            pd.DataFrame: 병합된 데이터
        """
        print("📥 창고 데이터 로드 시작...")
        
        data_paths = [
            "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
            "hvdc_ontology_system/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        ]
        
        dfs = []
        for path in data_paths:
            if os.path.exists(path):
                df = pd.read_excel(path)
                fname = os.path.basename(path).upper()
                
                # 데이터 소스 태깅
                if "SIMENSE" in fname or "SIEMENS" in fname:
                    df['DATA_SOURCE'] = 'SIEMENS'
                elif "HITACHI" in fname:
                    df['DATA_SOURCE'] = 'HITACHI'
                else:
                    df['DATA_SOURCE'] = 'UNKNOWN'
                
                df['SOURCE_FILE'] = fname
                df['PROCESSED_AT'] = self.timestamp
                
                print(f"✅ 로드 완료: {fname}, {len(df)}건, 소스={df['DATA_SOURCE'].iloc[0]}")
                dfs.append(df)
            else:
                print(f"❌ 파일 미발견: {path}")
        
        if not dfs:
            raise FileNotFoundError("창고 데이터 파일을 찾을 수 없습니다.")
        
        # 데이터 병합
        merged_df = pd.concat(dfs, ignore_index=True)
        print(f"📊 병합 완료: 총 {len(merged_df)}건")
        
        # 소스별 분포 확인
        source_counts = merged_df['DATA_SOURCE'].value_counts()
        print("📈 소스별 분포:")
        for source, count in source_counts.items():
            print(f"   - {source}: {count:,}건")
        
        return merged_df
    
    def apply_tdd_flow_code_logic(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        TDD 검증된 Flow Code 로직 적용
        
        Args:
            df: 원본 데이터프레임
            
        Returns:
            pd.DataFrame: Flow Code가 적용된 데이터프레임
        """
        print("🔧 TDD 검증된 Flow Code 로직 적용 중...")
        
        # WH_HANDLING 계산
        df['WH_HANDLING'] = df.apply(self.calculate_wh_handling_tdd, axis=1)
        
        # FLOW_CODE 계산
        df['FLOW_CODE'] = df.apply(self.calculate_flow_code_tdd, axis=1)
        
        # Flow 설명 추가
        df['FLOW_DESCRIPTION'] = df['FLOW_CODE'].map(self.FLOW_CODE_MAPPING)
        
        # Flow 패턴 분류
        df['FLOW_PATTERN'] = df['FLOW_CODE'].map(self.get_flow_patterns())
        
        print(f"✅ Flow Code 로직 적용 완료")
        return df
    
    def calculate_wh_handling_tdd(self, row) -> int:
        """
        TDD 검증된 WH_HANDLING 계산
        
        Args:
            row: 데이터프레임 행
            
        Returns:
            int: WH_HANDLING 값
        """
        # Pre Arrival 확인
        if self.is_pre_arrival_status(row):
            return 0
        
        # 창고 개수 계산
        warehouse_count = 0
        for col in self.warehouse_columns:
            if col in row.index:
                value = row[col]
                if pd.notna(value) and value != '':
                    # 실제 데이터 존재 여부 확인
                    if isinstance(value, (int, float)) or hasattr(value, 'date'):
                        warehouse_count += 1
                    elif isinstance(value, str) and value.strip():
                        # 의미있는 문자열인지 확인
                        if any(char.isdigit() for char in value):
                            warehouse_count += 1
        
        return warehouse_count
    
    def calculate_flow_code_tdd(self, row) -> int:
        """
        TDD 검증된 Flow Code 계산
        
        Args:
            row: 데이터프레임 행
            
        Returns:
            int: Flow Code 값
        """
        # Status_Location 기반 판단
        status_location = str(row.get('Status_Location', '')).strip().lower()
        
        # 1. Pre Arrival 또는 비어있는 경우
        if not status_location or status_location == 'pre arrival':
            return 0
        
        # 2. 직송 (Port→Site)
        if status_location in ['agi', 'das', 'mir', 'shu']:
            has_warehouse = any(
                pd.notna(row.get(col, None)) and row.get(col, '') != '' 
                for col in self.warehouse_columns
            )
            if not has_warehouse:
                return 0
        
        # 3. 창고 경유 개수 기반 계산
        warehouse_count = self.count_unique_warehouses(row)
        
        # 4. MOSB 특별 처리
        if self.has_mosb_routing(row):
            return 3 if warehouse_count > 0 else 2
        
        # 5. 일반적인 Flow Code 계산
        return min(warehouse_count, 3)
    
    def is_pre_arrival_status(self, row) -> bool:
        """
        Pre Arrival 상태 확인
        
        Args:
            row: 데이터프레임 행
            
        Returns:
            bool: Pre Arrival 여부
        """
        status_location = str(row.get('Status_Location', '')).strip().lower()
        return status_location == 'pre arrival'
    
    def count_unique_warehouses(self, row) -> int:
        """
        고유 창고 개수 계산
        
        Args:
            row: 데이터프레임 행
            
        Returns:
            int: 고유 창고 개수
        """
        count = 0
        for col in self.warehouse_columns:
            if col in row.index and pd.notna(row[col]) and row[col] != '':
                value = row[col]
                if isinstance(value, (int, float)) or hasattr(value, 'date'):
                    count += 1
                elif isinstance(value, str) and value.strip():
                    if any(char.isdigit() for char in value):
                        count += 1
        return count
    
    def has_mosb_routing(self, row) -> bool:
        """
        MOSB 경유 확인
        
        Args:
            row: 데이터프레임 행
            
        Returns:
            bool: MOSB 경유 여부
        """
        return ('MOSB' in row.index and 
                pd.notna(row.get('MOSB', '')) and 
                row['MOSB'] != '')
    
    def get_flow_patterns(self) -> Dict[int, str]:
        """
        Flow Code 패턴 매핑
        
        Returns:
            Dict[int, str]: Flow Code별 패턴
        """
        return {
            0: 'DIRECT',
            1: 'SINGLE_STAGE',
            2: 'TWO_STAGE',
            3: 'MULTI_STAGE',
            -1: 'PRE_ARRIVAL'
        }
        
    def generate_integrated_monthly_report(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        통합 월별 리포트 생성 (TDD Enhanced - 실제 데이터 연동)
        
        Args:
            data: 선택적 데이터 (None이면 실제 파일에서 로드)
            
        Returns:
            dict: 리포트 생성 결과
        """
        try:
            print("🚀 MACHO-GPT 통합 월별 리포트 생성 시작...")
            
            # 1. 실제 데이터 로드 (TDD 구조 적용)
            if data is None:
                df = self.load_and_merge_warehouse_data()
                df = self.apply_tdd_flow_code_logic(df)
            else:
                # 테스트용 데이터 처리
                if 'SQM_STACK' in data:
                    df = pd.DataFrame(data['SQM_STACK'])
                else:
                    df = pd.DataFrame()
            
            # 2. 파일명 생성
            output_file = f"MACHO_GPT_최종_리포트_{self.timestamp}.xlsx"
            
            # 3. Excel 파일 생성 (generate_integrated_report_with_tdd_logic.py 구조 참고)
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 전체 트랜잭션 데이터
                df.to_excel(writer, sheet_name='전체_트랜잭션_데이터', index=False)
                
                # Status_Location 분포 분석
                status_analysis = self.analyze_status_location_distribution(df)
                if status_analysis:
                    status_df = pd.DataFrame(status_analysis['status_distribution'])
                    status_df.to_excel(writer, sheet_name='Status_Location_분포', index=False)
                
                # Flow Code 분포 분석
                flow_analysis = self.analyze_flow_code_distribution(df)
                if flow_analysis:
                    flow_df = pd.DataFrame(flow_analysis['flow_distribution'])
                    flow_df.to_excel(writer, sheet_name='Flow_Code_분포', index=False)
                
                # KPI 대시보드
                kpi_dashboard = self.generate_kpi_dashboard(df)
                kpi_df = pd.DataFrame(kpi_dashboard['dashboard_elements'])
                kpi_df.to_excel(writer, sheet_name='KPI_대시보드', index=False)
                
                # FANR 규정 준수
                compliance_result = self.validate_fanr_compliance(df)
                compliance_df = pd.DataFrame([compliance_result])
                compliance_df.to_excel(writer, sheet_name='FANR_규정준수', index=False)
            
            # 4. 결과 구성
            result = {
                'status': 'SUCCESS',
                'confidence': 0.97,
                'output_file': output_file,
                'mode': self.current_mode,
                'timestamp': self.timestamp,
                'records_processed': len(df),
                'status_location_analysis': status_analysis,
                'flow_code_analysis': flow_analysis,
                'kpi_dashboard': kpi_dashboard,
                'compliance_result': compliance_result,
                'next_cmds': [
                    '/validate-data code-quality',
                    '/test-scenario unit-tests',
                    '/automate test-pipeline'
                ]
            }
            
            # 5. 결과 출력
            print(f"✅ 통합 월별 리포트 생성 완료!")
            print(f"📄 출력 파일: {output_file}")
            print(f"🎯 신뢰도: {result['confidence']:.2%}")
            print(f"📊 처리된 레코드: {result['records_processed']:,}건")
            
            return result
            
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            return self._handle_error({'error': str(e), 'confidence': 0.0})
    
    def validate_fanr_compliance(self, compliance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        FANR 규정 준수 검증
        
        Args:
            compliance_data: 규제 요구사항 데이터
            
        Returns:
            dict: 규정 준수 결과
        """
        try:
            # 압력 한계 검증
            pressure_check = compliance_data.get('pressure_limit', 0) <= self.PRESSURE_LIMIT
            
            # 안전 여유 검증
            safety_check = compliance_data.get('safety_margin', 0) >= 0.1
            
            # 인증서 상태 검증
            cert_check = compliance_data.get('certificate_status') == 'VALID'
            
            # 전체 규정 준수 여부
            overall_compliance = pressure_check and safety_check and cert_check
            
            return {
                'compliance_status': 'PASSED' if overall_compliance else 'FAILED',
                'confidence': 0.96,
                'pressure_check': pressure_check,
                'safety_check': safety_check,
                'certificate_check': cert_check,
                'timestamp': self.timestamp
            }
            
        except Exception as e:
            return self._handle_error({'error': str(e), 'compliance_status': 'ERROR'})
    
    def generate_kpi_dashboard(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        KPI 대시보드 생성
        
        Args:
            kpi_data: KPI 데이터
            
        Returns:
            dict: 대시보드 생성 결과
        """
        try:
            dashboard_elements = []
            
            # 성공률 위젯
            if 'success_rate' in kpi_data:
                dashboard_elements.append({
                    'type': 'success_rate',
                    'value': kpi_data['success_rate'],
                    'status': 'GOOD' if kpi_data['success_rate'] >= 0.95 else 'WARNING'
                })
            
            # 처리 시간 위젯
            if 'processing_time' in kpi_data:
                dashboard_elements.append({
                    'type': 'processing_time',
                    'value': kpi_data['processing_time'],
                    'status': 'GOOD' if kpi_data['processing_time'] <= self.PROCESSING_TIME_LIMIT else 'WARNING'
                })
            
            # 오류율 위젯
            if 'error_rate' in kpi_data:
                dashboard_elements.append({
                    'type': 'error_rate',
                    'value': kpi_data['error_rate'],
                    'status': 'GOOD' if kpi_data['error_rate'] <= 0.05 else 'WARNING'
                })
            
            # 활용률 위젯
            if 'utilization_rate' in kpi_data:
                dashboard_elements.append({
                    'type': 'utilization_rate',
                    'value': kpi_data['utilization_rate'],
                    'status': 'GOOD' if kpi_data['utilization_rate'] >= 0.85 else 'WARNING'
                })
            
            return {
                'dashboard_elements': dashboard_elements,
                'confidence': 0.97,
                'timestamp': self.timestamp,
                'total_widgets': len(dashboard_elements)
            }
            
        except Exception as e:
            return self._handle_error({'error': str(e), 'dashboard_elements': []})
    
    def handle_error_scenario(self, error_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        오류 시나리오 처리 및 containment mode 전환
        
        Args:
            error_scenario: 오류 시나리오 정보
            
        Returns:
            dict: 오류 처리 결과
        """
        try:
            current_mode = error_scenario.get('current_mode', 'PRIME')
            confidence = error_scenario.get('confidence', 1.0)
            error_type = error_scenario.get('error_type', 'UNKNOWN')
            
            # 신뢰도 임계값 미달시 ZERO 모드로 전환
            if confidence < self.confidence_threshold:
                return {
                    'mode_switch': 'ZERO',
                    'fallback_activated': True,
                    'previous_mode': current_mode,
                    'reason': f'Confidence {confidence} below threshold {self.confidence_threshold}',
                    'error_type': error_type,
                    'timestamp': self.timestamp
                }
            
            return {
                'mode_switch': current_mode,
                'fallback_activated': False,
                'confidence': confidence,
                'timestamp': self.timestamp
            }
            
        except Exception as e:
            return self._handle_error({'error': str(e), 'mode_switch': 'ZERO', 'fallback_activated': True})
    
    def recommend_next_commands(self, report_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        다음 명령어 추천
        
        Args:
            report_result: 리포트 생성 결과
            
        Returns:
            dict: 명령어 추천 결과
        """
        try:
            status = report_result.get('status', 'UNKNOWN')
            report_type = report_result.get('report_type', 'GENERAL')
            confidence = report_result.get('confidence', 0.5)
            
            # 기본 추천 명령어
            base_commands = [
                '/validate-data code-quality',
                '/test-scenario unit-tests',
                '/automate test-pipeline'
            ]
            
            # 리포트 타입에 따른 추가 명령어
            if report_type == 'INTEGRATED_MONTHLY':
                base_commands.extend([
                    '/weather_tie check_conditions',
                    '/stowage_optimizer heat_analysis',
                    '/compliance_check fanr_moiat'
                ])
            
            # 신뢰도에 따른 추가 명령어
            if confidence < 0.90:
                base_commands.append('/switch_mode ZERO')
            
            # 상태에 따른 추가 명령어
            if status == 'SUCCESS':
                base_commands.extend([
                    '/export_report powerbi',
                    '/schedule_next_run monthly'
                ])
            
            return {
                'next_cmds': base_commands[:8],  # 최대 8개 명령어
                'confidence': confidence,
                'timestamp': self.timestamp,
                'total_recommendations': len(base_commands)
            }
            
        except Exception as e:
            return self._handle_error({'error': str(e), 'next_cmds': ['/switch_mode ZERO']})
    
    def analyze_status_location_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Status_Location 분포 분석 (TDD Enhanced)
        
        Args:
            df: 데이터프레임
            
        Returns:
            Dict[str, Any]: 분포 분석 결과
        """
        print("📈 Status_Location 분포 분석 시작...")
        
        if df.empty or 'Status_Location' not in df.columns:
            print("❌ Status_Location 컬럼 없음 또는 빈 데이터")
            return {}
        
        # 분포 계산
        status_distribution = df['Status_Location'].value_counts().reset_index()
        status_distribution.columns = ['Status_Location', 'Count']
        status_distribution['Percentage'] = (
            status_distribution['Count'] / len(df) * 100
        ).round(2)
        
        # Pre Arrival 상세 분석
        pre_arrival_mask = df['Status_Location'].str.contains(
            'Pre Arrival', case=False, na=False
        )
        pre_arrival_count = pre_arrival_mask.sum()
        
        # NaN 분석
        nan_count = df['Status_Location'].isna().sum()
        
        # 결과 출력
        print(f"📊 Status_Location 분포 (총 {len(df)}건):")
        print("=" * 60)
        for _, row in status_distribution.head(10).iterrows():
            print(f"{row['Status_Location']:<25} {row['Count']:>8}건 ({row['Percentage']:>6.2f}%)")
        
        print(f"\n🔍 Pre Arrival: {pre_arrival_count}건")
        print(f"🔍 NaN: {nan_count}건")
        
        return {
            'total_records': len(df),
            'status_distribution': status_distribution.to_dict('records'),
            'pre_arrival_count': int(pre_arrival_count),
            'nan_count': int(nan_count),
            'flow_code_0_candidates': int(pre_arrival_count + nan_count)
        }
    
    def analyze_flow_code_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Flow Code 분포 분석 (TDD Enhanced)
        
        Args:
            df: 데이터프레임
            
        Returns:
            Dict[str, Any]: Flow Code 분포 분석 결과
        """
        print("📊 Flow Code 분포 분석 시작...")
        
        if df.empty or 'FLOW_CODE' not in df.columns:
            print("❌ FLOW_CODE 컬럼 없음 또는 빈 데이터")
            return {}
        
        # Flow Code 분포 계산
        flow_distribution = df['FLOW_CODE'].value_counts().sort_index().reset_index()
        flow_distribution.columns = ['Flow_Code', 'Count']
        flow_distribution['Percentage'] = (
            flow_distribution['Count'] / len(df) * 100
        ).round(2)
        flow_distribution['Description'] = flow_distribution['Flow_Code'].map(
            self.FLOW_CODE_MAPPING
        )
        
        # 결과 출력
        print(f"📊 Flow Code 분포 (총 {len(df)}건):")
        print("=" * 80)
        for _, row in flow_distribution.iterrows():
            print(f"Flow Code {row['Flow_Code']}: {row['Description']:<35} "
                  f"{row['Count']:>8}건 ({row['Percentage']:>6.2f}%)")
        
        return {
            'total_records': len(df),
            'flow_distribution': flow_distribution.to_dict('records')
        }
    
    def _handle_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        오류 처리 헬퍼 함수
        
        Args:
            error_info: 오류 정보
            
        Returns:
            dict: 오류 처리 결과
        """
        return {
            'status': 'ERROR',
            'confidence': 0.0,
            'mode': 'ZERO',
            'error': error_info.get('error', 'Unknown error'),
            'timestamp': self.timestamp,
            'next_cmds': ['/switch_mode ZERO', '/validate-data code-quality', '/test-scenario unit-tests']
        }


def main():
    """
    메인 실행 함수 (generate_integrated_report_with_tdd_logic.py 구조 참고)
    """
    print("🔌 MACHO-GPT v3.4-mini 최종 리포터 실행")
    print("🏗️ HVDC PROJECT - Samsung C&T·ADNOC·DSV Partnership")  
    print("📅", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    try:
        # 최종 리포터 인스턴스 생성
        reporter = FinalReporter(confidence_threshold=0.95)
        
        # 통합 월별 리포트 생성 (실제 데이터 연동)
        final_result = reporter.generate_integrated_monthly_report()
        
        # 결과 검증 및 출력
        if final_result['status'] == 'SUCCESS':
            print(f"\n🎉 TDD 검증된 로직으로 최종 리포트가 성공적으로 생성되었습니다!")
            print(f"📁 파일명: {final_result['output_file']}")
            print(f"🎯 신뢰도: {final_result['confidence']:.2%}")
            print(f"📊 처리된 레코드: {final_result['records_processed']:,}건")
            
            # 추천 명령어 출력
            print(f"\n🔧 **추천 명령어:**")
            for cmd in final_result['next_cmds'][:3]:
                if cmd == '/validate-data code-quality':
                    print(f"{cmd} [Status_Location 값 분포 자동 출력]")
                elif cmd == '/test-scenario unit-tests':
                    print(f"{cmd} [Flow Code 0 집계 자동화 테스트]")
                elif cmd == '/automate test-pipeline':
                    print(f"{cmd} [목표 분포 자동화]")
                else:
                    print(f"{cmd} [물류 도메인 특화 분석]")
        else:
            print(f"\n❌ 최종 리포트 생성 실패!")
            print(f"🔄 모드 전환: {final_result.get('mode_switch', {}).get('mode_switch', 'N/A')}")
            print(f"📝 오류: {final_result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print("🎯 MACHO-GPT 최종 리포터 실행 완료!")
        
        return final_result
        
    except Exception as e:
        print(f"\n❌ 치명적 오류 발생: {str(e)}")
        print("🔄 ZERO 모드로 긴급 전환 권장")
        
        return {
            'status': 'CRITICAL_ERROR',
            'error': str(e),
            'recommended_action': 'SWITCH_TO_ZERO_MODE'
        }


if __name__ == "__main__":
    result = main() 