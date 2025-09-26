"""
MACHO-GPT 최종 리포터 실행 스크립트 (Enhanced)
실제 데이터 파일과 연동하여 Status_Location 분포 분석 및 최종 리포트 생성

TDD Refactor Phase
날짜: 2025-01-04
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

from final_reporter import FinalReporter


class EnhancedFinalReporter:
    """
    향상된 최종 리포터 클래스
    실제 데이터 파일과 연동하여 분석 수행
    """
    
    def __init__(self, data_path: str = None):
        """
        초기화
        
        Args:
            data_path: 데이터 파일 경로
        """
        self.data_path = data_path or "hvdc_macho_gpt/WAREHOUSE/data"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.reporter = FinalReporter(confidence_threshold=0.95)
        
        # 데이터 파일 경로 설정
        self.hitachi_file = os.path.join(self.data_path, "HVDC WAREHOUSE_HITACHI(HE).xlsx")
        self.siemens_file = os.path.join(self.data_path, "HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
        
        print(f"📊 MACHO-GPT 최종 리포터 초기화 완료")
        print(f"⏰ 실행 시간: {self.timestamp}")
        print(f"📁 데이터 경로: {self.data_path}")
        
    def load_warehouse_data(self) -> Dict[str, pd.DataFrame]:
        """
        창고 데이터 로드
        
        Returns:
            dict: 로드된 데이터프레임들
        """
        data = {}
        
        try:
            # HITACHI 데이터 로드
            if os.path.exists(self.hitachi_file):
                data['HITACHI'] = pd.read_excel(self.hitachi_file)
                print(f"✅ HITACHI 데이터 로드 완료: {len(data['HITACHI'])}건")
            else:
                print(f"❌ HITACHI 파일을 찾을 수 없음: {self.hitachi_file}")
                
            # SIEMENS 데이터 로드
            if os.path.exists(self.siemens_file):
                data['SIEMENS'] = pd.read_excel(self.siemens_file)
                print(f"✅ SIEMENS 데이터 로드 완료: {len(data['SIEMENS'])}건")
            else:
                print(f"❌ SIEMENS 파일을 찾을 수 없음: {self.siemens_file}")
                
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
            
        return data
    
    def analyze_status_location_distribution(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Status_Location 분포 분석
        
        Args:
            data: 로드된 데이터
            
        Returns:
            dict: 분포 분석 결과
        """
        print("\n📈 Status_Location 분포 분석 시작...")
        
        analysis_results = {}
        combined_data = pd.DataFrame()
        
        # 모든 데이터를 결합
        for key, df in data.items():
            if 'Status_Location' in df.columns:
                df['Source'] = key
                combined_data = pd.concat([combined_data, df], ignore_index=True)
        
        if combined_data.empty:
            print("❌ Status_Location 컬럼이 없거나 데이터가 비어있음")
            return analysis_results
        
        # Status_Location 분포 계산
        status_distribution = combined_data['Status_Location'].value_counts().reset_index()
        status_distribution.columns = ['Status_Location', 'Count']
        status_distribution['Percentage'] = (status_distribution['Count'] / len(combined_data) * 100).round(2)
        
        # 결과 출력
        print(f"\n📊 Status_Location 분포 (총 {len(combined_data)}건):")
        print("=" * 60)
        for _, row in status_distribution.head(15).iterrows():
            print(f"{row['Status_Location']:<30} {row['Count']:>8}건 ({row['Percentage']:>6.2f}%)")
        
        # Pre Arrival 분석
        pre_arrival_count = combined_data[combined_data['Status_Location'].str.contains('Pre Arrival', case=False, na=False)]['Status_Location'].value_counts()
        print(f"\n🔍 Pre Arrival 상세 분석:")
        for status, count in pre_arrival_count.items():
            print(f"  {status}: {count}건")
        
        # NaN 분석
        nan_count = combined_data['Status_Location'].isna().sum()
        print(f"\n🔍 비어있는 값(NaN): {nan_count}건")
        
        # Flow Code 0 해당 분석
        flow_code_0_candidates = combined_data[
            (combined_data['Status_Location'].str.contains('Pre Arrival', case=False, na=False)) |
            (combined_data['Status_Location'].isna())
        ]
        print(f"\n🔍 Flow Code 0 후보 (Pre Arrival + NaN): {len(flow_code_0_candidates)}건")
        
        analysis_results = {
            'total_records': len(combined_data),
            'status_distribution': status_distribution.to_dict('records'),
            'pre_arrival_count': pre_arrival_count.to_dict() if not pre_arrival_count.empty else {},
            'nan_count': nan_count,
            'flow_code_0_candidates': len(flow_code_0_candidates)
        }
        
        return analysis_results
    
    def analyze_flow_code_distribution(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Flow Code 분포 분석 (WH Handling 기반)
        
        Args:
            data: 로드된 데이터
            
        Returns:
            dict: Flow Code 분포 분석 결과
        """
        print("\n📈 Flow Code 분포 분석 시작...")
        
        analysis_results = {}
        combined_data = pd.DataFrame()
        
        # 모든 데이터를 결합
        for key, df in data.items():
            if 'wh handling' in df.columns:
                df['Source'] = key
                combined_data = pd.concat([combined_data, df], ignore_index=True)
        
        if combined_data.empty:
            print("❌ 'wh handling' 컬럼이 없거나 데이터가 비어있음")
            return analysis_results
        
        # Flow Code 분포 계산
        flow_distribution = combined_data['wh handling'].value_counts().sort_index().reset_index()
        flow_distribution.columns = ['Flow_Code', 'Count']
        flow_distribution['Percentage'] = (flow_distribution['Count'] / len(combined_data) * 100).round(2)
        
        # Flow Code별 설명 추가
        flow_descriptions = {
            0: "Port→Site 직송 또는 Pre Arrival",
            1: "창고 1개 경유",
            2: "창고 2개 경유",
            3: "창고 3개 이상 경유"
        }
        
        flow_distribution['Description'] = flow_distribution['Flow_Code'].map(flow_descriptions)
        
        # 결과 출력
        print(f"\n📊 Flow Code 분포 (총 {len(combined_data)}건):")
        print("=" * 80)
        for _, row in flow_distribution.iterrows():
            print(f"Flow Code {row['Flow_Code']}: {row['Description']:<40} {row['Count']:>8}건 ({row['Percentage']:>6.2f}%)")
        
        # Flow Code 0 상세 분석
        if 'Status_Location' in combined_data.columns:
            flow_0_data = combined_data[combined_data['wh handling'] == 0]
            print(f"\n🔍 Flow Code 0 상세 분석 ({len(flow_0_data)}건):")
            
            flow_0_status = flow_0_data['Status_Location'].value_counts().head(10)
            for status, count in flow_0_status.items():
                print(f"  {status}: {count}건")
        
        analysis_results = {
            'total_records': len(combined_data),
            'flow_distribution': flow_distribution.to_dict('records'),
            'flow_0_detail': flow_0_status.to_dict() if 'flow_0_status' in locals() else {}
        }
        
        return analysis_results
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        종합 리포트 생성
        
        Returns:
            dict: 종합 리포트 결과
        """
        print(f"\n🚀 MACHO-GPT 최종 리포트 생성 시작...")
        
        # 1. 데이터 로드
        warehouse_data = self.load_warehouse_data()
        
        if not warehouse_data:
            print("❌ 데이터 로드 실패")
            return {'status': 'ERROR', 'message': '데이터 로드 실패'}
        
        # 2. Status_Location 분포 분석
        status_analysis = self.analyze_status_location_distribution(warehouse_data)
        
        # 3. Flow Code 분포 분석
        flow_analysis = self.analyze_flow_code_distribution(warehouse_data)
        
        # 4. 통합 데이터 준비
        integrated_data = {
            'STATUS_LOCATION': status_analysis,
            'FLOW_CODE': flow_analysis,
            'WAREHOUSE_DATA': {key: len(df) for key, df in warehouse_data.items()}
        }
        
        # 5. 최종 리포트 생성
        final_report = self.reporter.generate_integrated_monthly_report(integrated_data)
        
        # 6. 추가 분석 결과 통합
        final_report.update({
            'status_location_analysis': status_analysis,
            'flow_code_analysis': flow_analysis,
            'data_sources': list(warehouse_data.keys()),
            'analysis_timestamp': self.timestamp
        })
        
        # 7. 결과 출력
        print(f"\n✅ 최종 리포트 생성 완료!")
        print(f"📄 출력 파일: {final_report.get('output_file', 'N/A')}")
        print(f"🎯 신뢰도: {final_report.get('confidence', 0):.2%}")
        print(f"📊 처리된 레코드: {final_report.get('records_processed', 0)}건")
        
        return final_report
    
    def print_next_commands(self, report_result: Dict[str, Any]):
        """
        다음 명령어 출력
        
        Args:
            report_result: 리포트 결과
        """
        next_cmds = self.reporter.recommend_next_commands(report_result)
        
        print(f"\n🔧 **추천 명령어:**")
        for i, cmd in enumerate(next_cmds.get('next_cmds', [])[:3], 1):
            if cmd == '/validate-data code-quality':
                print(f"{cmd} [Status_Location 값 분포 자동 출력]")
            elif cmd == '/test-scenario unit-tests':
                print(f"{cmd} [Flow Code 0 집계 자동화 테스트]")
            elif cmd == '/automate test-pipeline':
                print(f"{cmd} [목표 분포 자동화]")
            else:
                print(f"{cmd} [물류 도메인 특화 분석]")


def main():
    """
    메인 실행 함수
    """
    print("🔌 MACHO-GPT v3.4-mini 최종 리포터 실행")
    print("🏗️ HVDC PROJECT - Samsung C&T·ADNOC·DSV Partnership")
    print("📅", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    # 최종 리포터 실행
    enhanced_reporter = EnhancedFinalReporter()
    
    # 종합 리포트 생성
    report_result = enhanced_reporter.generate_comprehensive_report()
    
    # 다음 명령어 출력
    enhanced_reporter.print_next_commands(report_result)
    
    print("\n" + "=" * 70)
    print("🎯 최종 리포터 실행 완료!")


if __name__ == "__main__":
    main() 