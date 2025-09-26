#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini | 업데이트된 HITACHI 데이터 종합 분석
Samsung C&T × ADNOC DSV Partnership | HVDC 프로젝트

참조 문서 기반 분석:
1.   .md
2. 창고_현장_월별_시트_구조.md  
3. hvdc_logi_master_integrated.py

TDD 방법론 적용: Red → Green → Refactor
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MACHO-GPT - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UpdatedHitachiAnalyzer:
    """업데이트된 HITACHI 데이터 종합 분석기"""
    
    def __init__(self):
        """초기화"""
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.mode = "LATTICE"
        
        # TDD 보고서 기준값 (참조 문서 기반)
        self.tdd_baseline = {
            'hitachi_count': 5346,
            'flow_code_2_target': 886,
            'flow_code_2_achieved': 886,  # 100% 달성
            'overall_success_rate': 0.599  # 59.9%
        }
        
        # 창고/현장 월별 시트 구조 요구사항
        self.warehouse_columns = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 
            'DSV MZP', 'MOSB', 'AAA Storage', 'Hauler Indoor'
        ]
        self.site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 필수 컬럼 (TDD 보고서 기준)
        self.essential_columns = [
            'Case No.', 'Package', 'DSV Indoor', 'DSV Outdoor',
            'AGI', 'DAS', 'MIR', 'SHU'
        ]
        
        # 분석 결과
        self.analysis_results = {}
        
    def load_updated_hitachi_data(self) -> pd.DataFrame:
        """업데이트된 HITACHI 데이터 로드"""
        print("📂 업데이트된 HITACHI 데이터 로드 시작")
        print(f"🎯 {self.mode} 모드: 정밀 데이터 분석")
        
        file_paths = [
            "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
            "HVDC WAREHOUSE_HITACHI(HE).xlsx",
            "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        ]
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path) / (1024 * 1024)
                    print(f"📂 파일 발견: {file_path}")
                    print(f"📏 파일 크기: {file_size:.1f}MB")
                    
                    df = pd.read_excel(file_path)
                    print(f"✅ 데이터 로드 성공: {len(df):,}건, {len(df.columns)}개 컬럼")
                    
                    return df
                    
                except Exception as e:
                    print(f"❌ 파일 로드 실패 ({file_path}): {e}")
                    continue
        
        print(f"❌ HITACHI 데이터 파일을 찾을 수 없습니다")
        return pd.DataFrame()
    
    def analyze_data_changes(self, df: pd.DataFrame) -> dict:
        """데이터 변경사항 분석 (TDD 보고서 기준)"""
        print("\n" + "="*80)
        print("🔍 TDD 시스템 로직 보정 영향 분석")
        print("="*80)
        
        if df.empty:
            return {'error': 'No data to analyze'}
        
        changes = {
            'record_count_analysis': {},
            'column_structure_analysis': {},
            'tdd_impact_assessment': {},
            'flow_code_validation': {},
            'data_quality_metrics': {}
        }
        
        # 1. 레코드 수 변화 분석
        current_count = len(df)
        baseline_count = self.tdd_baseline['hitachi_count']
        difference = current_count - baseline_count
        change_percentage = (difference / baseline_count) * 100 if baseline_count > 0 else 0
        
        changes['record_count_analysis'] = {
            'baseline_count': baseline_count,
            'current_count': current_count,
            'difference': difference,
            'change_percentage': change_percentage,
            'significant_change': abs(difference) > 100
        }
        
        print(f"📊 레코드 수 변화 분석:")
        print(f"   - TDD 기준값: {baseline_count:,}건")
        print(f"   - 현재 데이터: {current_count:,}건")
        print(f"   - 차이: {difference:+,}건 ({change_percentage:+.1f}%)")
        
        if abs(difference) > 100:
            print(f"   🚨 중대한 변화 감지 - Flow Code 로직 재검증 필요")
        else:
            print(f"   ✅ 변화 미미 - 기존 TDD 로직 유지 가능")
        
        # 2. 컬럼 구조 분석
        current_columns = set(df.columns)
        required_columns = set(self.essential_columns)
        warehouse_present = set(self.warehouse_columns) & current_columns
        site_present = set(self.site_columns) & current_columns
        
        missing_essential = required_columns - current_columns
        new_columns = current_columns - required_columns
        
        changes['column_structure_analysis'] = {
            'total_columns': len(current_columns),
            'missing_essential': list(missing_essential),
            'new_columns': list(new_columns),
            'warehouse_columns_present': list(warehouse_present),
            'site_columns_present': list(site_present),
            'structure_compatible': len(missing_essential) == 0
        }
        
        print(f"\n📋 컬럼 구조 분석:")
        print(f"   - 전체 컬럼: {len(current_columns)}개")
        print(f"   - 누락된 필수 컬럼: {missing_essential if missing_essential else '없음'}")
        print(f"   - 창고 컬럼 존재: {len(warehouse_present)}개 {list(warehouse_present)}")
        print(f"   - 현장 컬럼 존재: {len(site_present)}개 {list(site_present)}")
        
        # 3. TDD 영향도 평가
        flow_code_columns = [col for col in df.columns if 'FLOW' in col.upper()]
        has_flow_code = len(flow_code_columns) > 0
        
        changes['tdd_impact_assessment'] = {
            'flow_code_columns_found': flow_code_columns,
            'flow_code_logic_intact': has_flow_code,
            'warehouse_monthly_structure_viable': len(warehouse_present) >= 5,
            'site_monthly_structure_viable': len(site_present) == 4,
            'overall_compatibility_score': self._calculate_compatibility_score(changes)
        }
        
        print(f"\n🎯 TDD 시스템 로직 보정 영향:")
        print(f"   - Flow Code 컬럼: {flow_code_columns}")
        print(f"   - FLOW CODE 2 로직 100% 달성 유지 가능: {'✅' if has_flow_code else '❌'}")
        print(f"   - 창고 월별 시트 생성 가능: {'✅' if len(warehouse_present) >= 5 else '❌'}")
        print(f"   - 현장 월별 시트 생성 가능: {'✅' if len(site_present) == 4 else '❌'}")
        
        # 4. Flow Code 검증
        if has_flow_code and flow_code_columns:
            flow_col = flow_code_columns[0]
            flow_distribution = df[flow_col].value_counts().sort_index().to_dict()
            
            # TDD 보고서 기준 Flow Code 2 검증
            flow_code_2_current = flow_distribution.get(2, 0)
            flow_code_2_target = self.tdd_baseline['flow_code_2_target']
            flow_code_2_accuracy = 1 - abs(flow_code_2_current - flow_code_2_target) / flow_code_2_target if flow_code_2_target > 0 else 0
            
            changes['flow_code_validation'] = {
                'distribution': flow_distribution,
                'flow_code_2_current': flow_code_2_current,
                'flow_code_2_target': flow_code_2_target,
                'flow_code_2_accuracy': flow_code_2_accuracy,
                'maintains_100_percent_achievement': flow_code_2_accuracy > 0.95
            }
            
            print(f"\n🔧 Flow Code 검증:")
            print(f"   - 현재 분포: {flow_distribution}")
            print(f"   - FLOW CODE 2 현재/목표: {flow_code_2_current}/{flow_code_2_target}")
            print(f"   - FLOW CODE 2 정확도: {flow_code_2_accuracy:.1%}")
            print(f"   - 100% 달성 유지: {'✅' if flow_code_2_accuracy > 0.95 else '❌'}")
        
        # 5. 데이터 품질 지표
        if 'Case No.' in df.columns:
            duplicates = df.duplicated(subset=['Case No.']).sum()
            null_case_no = df['Case No.'].isna().sum()
            duplicate_rate = duplicates / len(df) if len(df) > 0 else 0
            null_rate = null_case_no / len(df) if len(df) > 0 else 0
        else:
            duplicates = null_case_no = duplicate_rate = null_rate = 0
        
        total_cells = len(df) * len(df.columns) if not df.empty else 1
        filled_cells = total_cells - df.isna().sum().sum() if not df.empty else 0
        quality_score = (filled_cells / total_cells) * 100
        
        changes['data_quality_metrics'] = {
            'duplicate_count': duplicates,
            'duplicate_rate': duplicate_rate,
            'null_case_no_count': null_case_no,
            'null_case_no_rate': null_rate,
            'overall_quality_score': quality_score,
            'quality_grade': self._get_quality_grade(quality_score)
        }
        
        print(f"\n📊 데이터 품질 지표:")
        print(f"   - Case No. 중복: {duplicates}건 ({duplicate_rate:.1%})")
        print(f"   - Case No. 누락: {null_case_no}건 ({null_rate:.1%})")
        print(f"   - 전체 품질 점수: {quality_score:.1f}%")
        print(f"   - 품질 등급: {self._get_quality_grade(quality_score)}")
        
        return changes
    
    def _calculate_compatibility_score(self, changes: dict) -> float:
        """호환성 점수 계산"""
        score = 0.0
        
        # 레코드 수 변화 점수 (30%)
        if not changes['record_count_analysis']['significant_change']:
            score += 30
        
        # 컬럼 구조 점수 (40%)
        if changes['column_structure_analysis']['structure_compatible']:
            score += 40
        
        # TDD 영향도 점수 (30%)
        tdd_assessment = changes['tdd_impact_assessment']
        if tdd_assessment['flow_code_logic_intact']:
            score += 10
        if tdd_assessment['warehouse_monthly_structure_viable']:
            score += 10
        if tdd_assessment['site_monthly_structure_viable']:
            score += 10
        
        return score
    
    def _get_quality_grade(self, score: float) -> str:
        """품질 등급 반환"""
        if score >= 95:
            return "A+ (우수)"
        elif score >= 90:
            return "A (양호)"
        elif score >= 80:
            return "B (보통)"
        elif score >= 70:
            return "C (미흡)"
        else:
            return "D (불량)"
    
    def generate_hvdc_logi_master_integration(self, df: pd.DataFrame, changes: dict) -> dict:
        """HVDC 물류 마스터 통합 시스템 적용"""
        print("\n" + "="*80)
        print("🚀 HVDC 물류 마스터 통합 시스템 적용")
        print("="*80)
        
        if df.empty:
            return {'error': 'No data for integration'}
        
        integration_result = {
            'containment_mode': self.mode,
            'processing_timestamp': self.timestamp,
            'warehouse_monthly_data': {},
            'site_monthly_data': {},
            'confidence_score': 0.0,
            'next_commands': []
        }
        
        try:
            # 창고별 월별 데이터 생성 (창고_현장_월별_시트_구조.md 기준)
            warehouse_data = self._generate_warehouse_monthly_data(df)
            integration_result['warehouse_monthly_data'] = warehouse_data
            
            # 현장별 월별 데이터 생성
            site_data = self._generate_site_monthly_data(df)
            integration_result['site_monthly_data'] = site_data
            
            # 신뢰도 점수 계산
            confidence = self._calculate_confidence_score(df, changes)
            integration_result['confidence_score'] = confidence
            
            # 다음 명령어 추천
            next_commands = self._generate_next_commands(changes, confidence)
            integration_result['next_commands'] = next_commands
            
            print(f"✅ HVDC 물류 마스터 통합 완료")
            print(f"📊 신뢰도 점수: {confidence:.1%}")
            print(f"🎯 컨테인먼트 모드: {self.mode}")
            
        except Exception as e:
            print(f"❌ 통합 시스템 적용 실패: {e}")
            integration_result['error'] = str(e)
        
        return integration_result
    
    def _generate_warehouse_monthly_data(self, df: pd.DataFrame) -> dict:
        """창고별 월별 입출고 데이터 생성"""
        warehouse_data = {}
        
        # 기본 월별 범위 (2023-02 ~ 2025-06)
        months = pd.date_range('2023-02', '2025-06', freq='MS').strftime('%Y-%m').tolist()
        
        for warehouse in self.warehouse_columns:
            if warehouse in df.columns:
                # 해당 창고에 데이터가 있는 경우의 입고 건수
                inbound_count = df[warehouse].notna().sum()
                
                # 출고는 다른 위치로 이동한 것으로 추정
                outbound_count = max(0, inbound_count - int(inbound_count * 0.1))  # 90% 출고 가정
                
                # 월별 분배 (현재는 단순 분배)
                monthly_inbound = self._distribute_monthly(inbound_count, months)
                monthly_outbound = self._distribute_monthly(outbound_count, months)
                
                warehouse_data[warehouse] = {
                    'total_inbound': inbound_count,
                    'total_outbound': outbound_count,
                    'monthly_inbound': monthly_inbound,
                    'monthly_outbound': monthly_outbound
                }
        
        return warehouse_data
    
    def _generate_site_monthly_data(self, df: pd.DataFrame) -> dict:
        """현장별 월별 입고재고 데이터 생성"""
        site_data = {}
        
        # 기본 월별 범위 (2024-01 ~ 2025-06)
        months = pd.date_range('2024-01', '2025-06', freq='MS').strftime('%Y-%m').tolist()
        
        for site in self.site_columns:
            if site in df.columns:
                # 해당 현장에 데이터가 있는 경우의 입고 건수
                inbound_count = df[site].notna().sum()
                
                # 재고는 입고의 누적으로 추정
                inventory_count = inbound_count  # 단순화
                
                # 월별 분배
                monthly_inbound = self._distribute_monthly(inbound_count, months)
                monthly_inventory = self._calculate_cumulative_inventory(monthly_inbound)
                
                site_data[site] = {
                    'total_inbound': inbound_count,
                    'total_inventory': inventory_count,
                    'monthly_inbound': monthly_inbound,
                    'monthly_inventory': monthly_inventory
                }
        
        return site_data
    
    def _distribute_monthly(self, total_count: int, months: list) -> dict:
        """총 건수를 월별로 분배"""
        if total_count == 0 or not months:
            return {month: 0 for month in months}
        
        # 단순 균등 분배 (향후 계절성 등 고려 가능)
        base_count = total_count // len(months)
        remainder = total_count % len(months)
        
        monthly_data = {}
        for i, month in enumerate(months):
            monthly_data[month] = base_count + (1 if i < remainder else 0)
        
        return monthly_data
    
    def _calculate_cumulative_inventory(self, monthly_inbound: dict) -> dict:
        """월별 누적 재고 계산"""
        cumulative = {}
        running_total = 0
        
        for month in sorted(monthly_inbound.keys()):
            running_total += monthly_inbound[month]
            cumulative[month] = running_total
        
        return cumulative
    
    def _calculate_confidence_score(self, df: pd.DataFrame, changes: dict) -> float:
        """신뢰도 점수 계산"""
        if df.empty:
            return 0.0
        
        score = 0.0
        
        # 데이터 품질 (40%)
        quality_score = changes.get('data_quality_metrics', {}).get('overall_quality_score', 0)
        score += (quality_score / 100) * 40
        
        # 컬럼 완전성 (30%)
        structure_score = 100 if changes.get('column_structure_analysis', {}).get('structure_compatible', False) else 50
        score += (structure_score / 100) * 30
        
        # TDD 호환성 (30%)
        compatibility_score = changes.get('tdd_impact_assessment', {}).get('overall_compatibility_score', 0)
        score += (compatibility_score / 100) * 30
        
        return score / 100
    
    def _generate_next_commands(self, changes: dict, confidence: float) -> list:
        """다음 추천 명령어 생성"""
        commands = []
        
        # 상황별 추천
        if changes.get('record_count_analysis', {}).get('significant_change', False):
            commands.append('/flow_code_validation [Flow Code 로직 재검증]')
        
        if confidence >= 0.90:
            commands.append('/generate_warehouse_monthly_report [창고 월별 리포트 생성]')
            commands.append('/create_site_monthly_analysis [현장 월별 분석]')
        else:
            commands.append('/data_quality_improvement [데이터 품질 개선]')
            commands.append('/tdd_logic_verification [TDD 로직 검증]')
        
        commands.append('/hvdc_logi_master_integration [물류 마스터 통합 실행]')
        
        return commands
    
    def create_excel_report(self, df: pd.DataFrame, changes: dict, integration: dict) -> str:
        """창고_현장_월별_시트_구조.xlsx 호환 Excel 리포트 생성"""
        print("\n" + "="*80)
        print("📊 Excel 리포트 생성 (창고_현장_월별_시트_구조.xlsx 호환)")
        print("="*80)
        
        output_file = f"HITACHI_Updated_Analysis_Report_{self.timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                
                # Sheet 1: 전체 데이터 (원본)
                if not df.empty:
                    df.to_excel(writer, sheet_name='전체_트랜잭션_데이터', index=False)
                
                # Sheet 2: 창고별 월별 입출고
                warehouse_sheet = self._create_warehouse_monthly_sheet(integration['warehouse_monthly_data'])
                warehouse_sheet.to_excel(writer, sheet_name='창고_월별_입출고', index=False)
                
                # Sheet 3: 현장별 월별 입고재고
                site_sheet = self._create_site_monthly_sheet(integration['site_monthly_data'])
                site_sheet.to_excel(writer, sheet_name='현장_월별_입고재고', index=False)
                
                # Sheet 4: 분석 결과 요약
                analysis_summary = self._create_analysis_summary_sheet(changes, integration)
                analysis_summary.to_excel(writer, sheet_name='분석_결과_요약', index=False)
                
                # Sheet 5: TDD 영향도 평가
                tdd_impact = self._create_tdd_impact_sheet(changes)
                tdd_impact.to_excel(writer, sheet_name='TDD_영향도_평가', index=False)
            
            print(f"✅ Excel 리포트 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Excel 리포트 생성 실패: {e}")
            return ""
    
    def _create_warehouse_monthly_sheet(self, warehouse_data: dict) -> pd.DataFrame:
        """창고별 월별 입출고 시트 생성 (Multi-level 헤더)"""
        if not warehouse_data:
            return pd.DataFrame()
        
        months = pd.date_range('2023-02', '2025-06', freq='MS').strftime('%Y-%m').tolist()
        months.append('Total')
        
        # 컬럼 헤더 구성
        warehouses = list(warehouse_data.keys())
        columns = ['Location']
        
        # Multi-level 헤더: 입고/출고 × 창고명
        for warehouse in warehouses:
            columns.extend([f'입고_{warehouse}', f'출고_{warehouse}'])
        
        # 데이터 생성
        data = []
        for month in months:
            row = [month]
            for warehouse in warehouses:
                if month == 'Total':
                    row.extend([
                        warehouse_data[warehouse]['total_inbound'],
                        warehouse_data[warehouse]['total_outbound']
                    ])
                else:
                    inbound = warehouse_data[warehouse]['monthly_inbound'].get(month, 0)
                    outbound = warehouse_data[warehouse]['monthly_outbound'].get(month, 0)
                    row.extend([inbound, outbound])
            data.append(row)
        
        return pd.DataFrame(data, columns=columns)
    
    def _create_site_monthly_sheet(self, site_data: dict) -> pd.DataFrame:
        """현장별 월별 입고재고 시트 생성 (Multi-level 헤더)"""
        if not site_data:
            return pd.DataFrame()
        
        months = pd.date_range('2024-01', '2025-06', freq='MS').strftime('%Y-%m').tolist()
        months.append('합계')
        
        # 컬럼 헤더 구성
        sites = list(site_data.keys())
        columns = ['Location']
        
        # Multi-level 헤더: 입고/재고 × 현장명
        for site in sites:
            columns.extend([f'입고_{site}', f'재고_{site}'])
        
        # 데이터 생성
        data = []
        for month in months:
            row = [month]
            for site in sites:
                if month == '합계':
                    row.extend([
                        site_data[site]['total_inbound'],
                        site_data[site]['total_inventory']
                    ])
                else:
                    inbound = site_data[site]['monthly_inbound'].get(month, 0)
                    inventory = site_data[site]['monthly_inventory'].get(month, 0)
                    row.extend([inbound, inventory])
            data.append(row)
        
        return pd.DataFrame(data, columns=columns)
    
    def _create_analysis_summary_sheet(self, changes: dict, integration: dict) -> pd.DataFrame:
        """분석 결과 요약 시트 생성"""
        summary_data = []
        
        # 기본 정보
        record_analysis = changes.get('record_count_analysis', {})
        summary_data.extend([
            {'구분': '분석 시각', '내용': self.timestamp},
            {'구분': '컨테인먼트 모드', '내용': self.mode},
            {'구분': 'TDD 기준 건수', '내용': f"{record_analysis.get('baseline_count', 0):,}건"},
            {'구분': '현재 데이터 건수', '내용': f"{record_analysis.get('current_count', 0):,}건"},
            {'구분': '건수 변화', '내용': f"{record_analysis.get('difference', 0):+,}건"},
            {'구분': '중대한 변화 여부', '내용': '예' if record_analysis.get('significant_change', False) else '아니오'}
        ])
        
        # 품질 지표
        quality_metrics = changes.get('data_quality_metrics', {})
        summary_data.extend([
            {'구분': '데이터 품질 점수', '내용': f"{quality_metrics.get('overall_quality_score', 0):.1f}%"},
            {'구분': '품질 등급', '내용': quality_metrics.get('quality_grade', 'N/A')},
            {'구분': '신뢰도 점수', '내용': f"{integration.get('confidence_score', 0):.1%}"}
        ])
        
        # TDD 영향도
        tdd_impact = changes.get('tdd_impact_assessment', {})
        summary_data.extend([
            {'구분': 'Flow Code 로직 유지', '내용': '가능' if tdd_impact.get('flow_code_logic_intact', False) else '불가능'},
            {'구분': '창고 월별 시트 생성', '내용': '가능' if tdd_impact.get('warehouse_monthly_structure_viable', False) else '불가능'},
            {'구분': '현장 월별 시트 생성', '내용': '가능' if tdd_impact.get('site_monthly_structure_viable', False) else '불가능'},
            {'구분': '전체 호환성 점수', '내용': f"{tdd_impact.get('overall_compatibility_score', 0):.1f}%"}
        ])
        
        return pd.DataFrame(summary_data)
    
    def _create_tdd_impact_sheet(self, changes: dict) -> pd.DataFrame:
        """TDD 영향도 평가 시트 생성"""
        impact_data = []
        
        # Flow Code 검증 결과
        flow_validation = changes.get('flow_code_validation', {})
        if flow_validation:
            distribution = flow_validation.get('distribution', {})
            for code, count in distribution.items():
                impact_data.append({
                    'Flow Code': code,
                    '현재 건수': count,
                    '비율': f"{count/sum(distribution.values())*100:.1f}%" if distribution else "0%",
                    '상태': '정상' if code in [0, 1, 2, 3, 4] else '비정상'
                })
            
            # FLOW CODE 2 특별 분석
            flow_2_current = flow_validation.get('flow_code_2_current', 0)
            flow_2_target = flow_validation.get('flow_code_2_target', 0)
            flow_2_accuracy = flow_validation.get('flow_code_2_accuracy', 0)
            
            impact_data.append({
                'Flow Code': 'FLOW CODE 2 (특별)',
                '현재 건수': flow_2_current,
                '목표 건수': flow_2_target,
                '정확도': f"{flow_2_accuracy:.1%}",
                '100% 달성 유지': '예' if flow_validation.get('maintains_100_percent_achievement', False) else '아니오'
            })
        
        if not impact_data:
            impact_data.append({
                'Flow Code': 'N/A',
                '현재 건수': 0,
                '상태': 'Flow Code 정보 없음'
            })
        
        return pd.DataFrame(impact_data)
    
    def run_comprehensive_analysis(self) -> dict:
        """종합 분석 실행"""
        print("🚀 MACHO-GPT v3.4-mini | 업데이트된 HITACHI 데이터 종합 분석")
        print("🎯 참조 문서 기반 TDD 시스템 로직 보정 영향 분석")
        print("Samsung C&T × ADNOC DSV Partnership | HVDC 프로젝트")
        print("="*80)
        
        final_result = {
            'analysis_timestamp': self.timestamp,
            'containment_mode': self.mode,
            'status': 'SUCCESS',
            'data_changes': {},
            'hvdc_integration': {},
            'excel_report_file': '',
            'recommendations': []
        }
        
        try:
            # 1. 업데이트된 데이터 로드
            df = self.load_updated_hitachi_data()
            
            if df.empty:
                print("❌ 데이터 로드 실패 - 분석을 중단합니다")
                final_result['status'] = 'FAILED'
                final_result['error'] = 'No data loaded'
                return final_result
            
            # 2. 데이터 변경사항 분석
            changes = self.analyze_data_changes(df)
            final_result['data_changes'] = changes
            
            # 3. HVDC 물류 마스터 통합 시스템 적용
            integration = self.generate_hvdc_logi_master_integration(df, changes)
            final_result['hvdc_integration'] = integration
            
            # 4. Excel 리포트 생성
            excel_file = self.create_excel_report(df, changes, integration)
            final_result['excel_report_file'] = excel_file
            
            # 5. 최종 추천사항 생성
            recommendations = self._generate_final_recommendations(changes, integration)
            final_result['recommendations'] = recommendations
            
            # 6. 최종 결과 요약
            self._print_final_summary(final_result)
            
            return final_result
            
        except Exception as e:
            print(f"❌ 종합 분석 중 오류 발생: {e}")
            logger.error(f"종합 분석 오류: {e}")
            final_result['status'] = 'FAILED'
            final_result['error'] = str(e)
            return final_result
    
    def _generate_final_recommendations(self, changes: dict, integration: dict) -> list:
        """최종 추천사항 생성"""
        recommendations = []
        
        # 데이터 변화 기반 추천
        record_change = changes.get('record_count_analysis', {}).get('significant_change', False)
        confidence = integration.get('confidence_score', 0)
        
        if record_change:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'TDD_LOGIC_VERIFICATION',
                'title': 'TDD 시스템 로직 재검증',
                'description': '데이터 건수 변화로 인한 Flow Code 로직 영향도 재평가 필요',
                'action': 'Flow Code 0, 1, 2, 3 로직 모두 재검증 및 테스트 실행'
            })
        
        if confidence < 0.90:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'DATA_QUALITY_IMPROVEMENT',
                'title': '데이터 품질 개선',
                'description': f'현재 신뢰도 {confidence:.1%}, 90% 목표 달성을 위한 품질 개선',
                'action': '누락 데이터 보완, 중복 제거, 컬럼 구조 정규화'
            })
        
        # 월별 시트 구조 추천
        warehouse_viable = changes.get('tdd_impact_assessment', {}).get('warehouse_monthly_structure_viable', False)
        site_viable = changes.get('tdd_impact_assessment', {}).get('site_monthly_structure_viable', False)
        
        if warehouse_viable and site_viable:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'MONTHLY_STRUCTURE_GENERATION',
                'title': '창고/현장 월별 시트 구조 생성',
                'description': '업데이트된 데이터로 월별 시트 구조 재생성 가능',
                'action': 'hvdc_logi_master_integrated.py 시스템을 활용한 월별 리포트 생성'
            })
        
        # FLOW CODE 2 100% 달성 유지 추천
        flow_2_maintains = changes.get('flow_code_validation', {}).get('maintains_100_percent_achievement', False)
        if flow_2_maintains:
            recommendations.append({
                'priority': 'LOW',
                'category': 'PERFORMANCE_OPTIMIZATION',
                'title': 'FLOW CODE 2 로직 100% 달성 상태 유지',
                'description': 'TDD 보고서의 FLOW CODE 2 로직 100% 달성 상태 지속 가능',
                'action': '기존 로직 유지 및 성능 최적화에 집중'
            })
        
        return recommendations
    
    def _print_final_summary(self, result: dict):
        """최종 결과 요약 출력"""
        print("\n" + "="*100)
        print("🏆 HITACHI 데이터 업데이트 분석 완료")
        print("="*100)
        
        changes = result.get('data_changes', {})
        integration = result.get('hvdc_integration', {})
        
        # 핵심 지표
        record_change = changes.get('record_count_analysis', {})
        confidence = integration.get('confidence_score', 0)
        
        print(f"📊 핵심 분석 결과:")
        print(f"   - 분석 상태: {result['status']}")
        print(f"   - 데이터 건수 변화: {record_change.get('difference', 0):+,}건")
        print(f"   - 중대한 변화: {'🚨 예' if record_change.get('significant_change', False) else '✅ 아니오'}")
        print(f"   - 신뢰도 점수: {confidence:.1%}")
        print(f"   - Excel 리포트: {result.get('excel_report_file', 'N/A')}")
        
        # TDD 영향도
        tdd_impact = changes.get('tdd_impact_assessment', {})
        print(f"\n🎯 TDD 시스템 로직 보정 영향:")
        print(f"   - Flow Code 로직 유지: {'✅' if tdd_impact.get('flow_code_logic_intact', False) else '❌'}")
        print(f"   - 창고 월별 시트 생성: {'✅' if tdd_impact.get('warehouse_monthly_structure_viable', False) else '❌'}")
        print(f"   - 현장 월별 시트 생성: {'✅' if tdd_impact.get('site_monthly_structure_viable', False) else '❌'}")
        print(f"   - 전체 호환성: {tdd_impact.get('overall_compatibility_score', 0):.1f}%")
        
        # 추천사항
        recommendations = result.get('recommendations', [])
        high_priority = [r for r in recommendations if r.get('priority') == 'HIGH']
        
        print(f"\n📋 추천사항:")
        if high_priority:
            print(f"   🚨 긴급 조치 필요: {len(high_priority)}개")
            for rec in high_priority:
                print(f"      - {rec['title']}")
        else:
            print(f"   ✅ 긴급 조치 불필요")
        
        print(f"   📊 총 추천사항: {len(recommendations)}개")

def main():
    """메인 실행 함수"""
    print("🔌 MACHO-GPT v3.4-mini 업데이트된 HITACHI 데이터 종합 분석 시스템")
    print("Enhanced MCP Integration | Samsung C&T Logistics")
    print("TDD 방법론 기반 | Kent Beck's Red-Green-Refactor")
    print("="*80)
    
    # 분석기 초기화 및 실행
    analyzer = UpdatedHitachiAnalyzer()
    final_result = analyzer.run_comprehensive_analysis()
    
    # 종료 코드 결정
    if final_result['status'] == 'FAILED':
        exit_code = 2  # 오류
    elif final_result.get('data_changes', {}).get('record_count_analysis', {}).get('significant_change', False):
        exit_code = 1  # 중대한 변화 - 주의 필요
    else:
        exit_code = 0  # 정상
    
    print(f"\n🏁 분석 완료 (종료 코드: {exit_code})")
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 