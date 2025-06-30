#!/usr/bin/env python3
"""
HVDC 실데이터 검증 스크립트 v2.8.1
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics
Purpose: 실제 Excel 데이터로 Flow Code 갭 분석 검증
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import json
from typing import Dict, List, Tuple
import sys
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 상위 디렉토리에서 모듈 임포트
sys.path.append('../hvdc_macho_gpt/WAREHOUSE')
try:
    from mapping_utils import MappingManager, calc_flow_code, add_logistics_flow_code_to_dataframe
    from calc_flow_code_v2 import FlowCodeCalculatorV2, add_flow_code_v2_to_dataframe
    from repair_columns_tool import ColumnRepairTool
except ImportError as e:
    logger.warning(f"모듈 임포트 실패: {e}")

class RealDataValidator:
    """실데이터 검증기"""
    
    def __init__(self):
        self.data_paths = {
            'hvdc_status': '../hvdc_macho_gpt/WAREHOUSE/data/HVDC-STATUS.xlsx',
            'hitachi': '../hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
            'simense': '../hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx',
            'invoice': '../hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx'
        }
        
        # 보고서 기준 분포
        self.report_distribution = {
            0: 163,    # Pre Arrival
            1: 3593,   # Port→Site
            2: 1183,   # Port→WH→Site
            3: 402,    # Port→WH→MOSB→Site
            4: 5       # Port→WH→wh→MOSB→Site
        }
        
        self.total_expected = sum(self.report_distribution.values())  # 5,346
        
    def load_excel_files(self) -> Dict[str, pd.DataFrame]:
        """모든 Excel 파일 로드"""
        dataframes = {}
        total_rows = 0
        
        logger.info("📁 실제 Excel 파일 로드 시작...")
        
        for name, path in self.data_paths.items():
            if Path(path).exists():
                try:
                    df = pd.read_excel(path)
                    dataframes[name] = df
                    total_rows += len(df)
                    logger.info(f"✅ {name}: {len(df)}행 × {len(df.columns)}열")
                    logger.info(f"   컬럼: {list(df.columns)[:5]}...")  # 처음 5개 컬럼만 표시
                except Exception as e:
                    logger.error(f"❌ {name} 로드 실패: {e}")
            else:
                logger.warning(f"⚠️ {name} 파일 없음: {path}")
        
        logger.info(f"📊 총 로드된 데이터: {total_rows}행 ({len(dataframes)}개 파일)")
        return dataframes
    
    def analyze_data_structure(self, dataframes: Dict[str, pd.DataFrame]) -> Dict:
        """데이터 구조 분석"""
        analysis = {
            'total_files': len(dataframes),
            'total_rows': sum(len(df) for df in dataframes.values()),
            'file_details': {},
            'column_analysis': {},
            'potential_issues': []
        }
        
        logger.info("🔍 데이터 구조 분석 시작...")
        
        # 각 파일별 상세 분석
        for name, df in dataframes.items():
            file_analysis = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_list': list(df.columns),
                'has_location': any('location' in col.lower() for col in df.columns),
                'has_status': any('status' in col.lower() for col in df.columns),
                'has_case_no': any('case' in col.lower() or 'id' in col.lower() for col in df.columns),
                'potential_wh_cols': [col for col in df.columns if any(wh in col.upper() for wh in ['DSV', 'INDOOR', 'OUTDOOR', 'WAREHOUSE'])],
                'potential_mosb_cols': [col for col in df.columns if any(mosb in col.upper() for mosb in ['MOSB', 'OFFSHORE', 'MARINE'])],
                'date_cols': [col for col in df.columns if 'date' in col.lower() or df[col].dtype in ['datetime64[ns]', 'object']]
            }
            
            analysis['file_details'][name] = file_analysis
            
            # 잠재적 문제점 식별
            if not file_analysis['has_location']:
                analysis['potential_issues'].append(f"{name}: Location 컬럼 부재")
            if not file_analysis['has_status']:
                analysis['potential_issues'].append(f"{name}: Status 컬럼 부재")
            if file_analysis['potential_wh_cols']:
                analysis['potential_issues'].append(f"{name}: WH 관련 컬럼 발견 - {file_analysis['potential_wh_cols'][:3]}")
            if file_analysis['potential_mosb_cols']:
                analysis['potential_issues'].append(f"{name}: MOSB 관련 컬럼 발견 - {file_analysis['potential_mosb_cols']}")
        
        return analysis
    
    def test_current_v28_algorithm(self, dataframes: Dict[str, pd.DataFrame]) -> Dict:
        """현재 v2.8 알고리즘 테스트"""
        logger.info("🧪 현재 v2.8 알고리즘 테스트 시작...")
        
        results = {}
        total_flow_distribution = {i: 0 for i in range(5)}
        
        try:
            manager = MappingManager()
            
            for name, df in dataframes.items():
                logger.info(f"   📊 {name} 처리 중...")
                
                # 컬럼 복구 시도
                repair_tool = ColumnRepairTool()
                df_repaired = repair_tool.repair_missing_columns(df.copy())
                
                # Storage Type 추가
                df_with_storage = manager.add_storage_type_to_dataframe(df_repaired)
                
                # Flow Code 추가 (기존 v2.8)
                df_complete = add_logistics_flow_code_to_dataframe(df_with_storage)
                
                # 분포 계산
                flow_distribution = df_complete['Logistics_Flow_Code'].value_counts().to_dict()
                normalized_flow = {i: flow_distribution.get(i, 0) for i in range(5)}
                
                results[name] = {
                    'original_rows': len(df),
                    'processed_rows': len(df_complete),
                    'flow_distribution': normalized_flow,
                    'storage_distribution': df_complete['Storage_Type'].value_counts().to_dict()
                }
                
                # 전체 분포에 합산
                for code, count in normalized_flow.items():
                    total_flow_distribution[code] += count
                
                logger.info(f"      Flow 분포: {normalized_flow}")
        
        except Exception as e:
            logger.error(f"❌ v2.8 알고리즘 테스트 실패: {e}")
            return {'error': str(e)}
        
        return {
            'file_results': results,
            'total_distribution': total_flow_distribution,
            'total_rows': sum(res['processed_rows'] for res in results.values())
        }
    
    def test_improved_v281_algorithm(self, dataframes: Dict[str, pd.DataFrame]) -> Dict:
        """개선된 v2.8.1 알고리즘 테스트"""
        logger.info("🚀 개선된 v2.8.1 알고리즘 테스트 시작...")
        
        results = {}
        total_flow_distribution = {i: 0 for i in range(5)}
        
        try:
            calculator = FlowCodeCalculatorV2()
            
            for name, df in dataframes.items():
                logger.info(f"   📊 {name} 처리 중...")
                
                # 컬럼 복구
                repair_tool = ColumnRepairTool()
                df_repaired = repair_tool.repair_missing_columns(df.copy())
                
                # Flow Code v2 추가
                df_complete = add_flow_code_v2_to_dataframe(df_repaired)
                
                # 분포 계산
                flow_distribution = df_complete['Logistics_Flow_Code_V2'].value_counts().to_dict()
                normalized_flow = {i: flow_distribution.get(i, 0) for i in range(5)}
                
                results[name] = {
                    'original_rows': len(df),
                    'processed_rows': len(df_complete),
                    'flow_distribution': normalized_flow,
                    'avg_confidence': df_complete['Flow_Confidence'].mean()
                }
                
                # 전체 분포에 합산
                for code, count in normalized_flow.items():
                    total_flow_distribution[code] += count
                
                logger.info(f"      Flow 분포: {normalized_flow}")
                logger.info(f"      평균 신뢰도: {results[name]['avg_confidence']:.3f}")
        
        except Exception as e:
            logger.error(f"❌ v2.8.1 알고리즘 테스트 실패: {e}")
            return {'error': str(e)}
        
        return {
            'file_results': results,
            'total_distribution': total_flow_distribution,
            'total_rows': sum(res['processed_rows'] for res in results.values())
        }
    
    def calculate_gaps(self, v28_result: Dict, v281_result: Dict) -> Dict:
        """갭 분석 계산"""
        logger.info("📊 갭 분석 계산 시작...")
        
        gaps = {
            'report_vs_v28': {},
            'report_vs_v281': {},
            'v28_vs_v281': {},
            'summary': {}
        }
        
        # 보고서 vs v2.8
        v28_total = v28_result.get('total_distribution', {})
        for code in range(5):
            report_count = self.report_distribution[code]
            v28_count = v28_total.get(code, 0)
            gap = v28_count - report_count
            
            gaps['report_vs_v28'][code] = {
                'report': report_count,
                'v28': v28_count,
                'gap': gap,
                'gap_pct': (gap / report_count * 100) if report_count > 0 else 0
            }
        
        # 보고서 vs v2.8.1
        v281_total = v281_result.get('total_distribution', {})
        for code in range(5):
            report_count = self.report_distribution[code]
            v281_count = v281_total.get(code, 0)
            gap = v281_count - report_count
            
            gaps['report_vs_v281'][code] = {
                'report': report_count,
                'v281': v281_count,
                'gap': gap,
                'gap_pct': (gap / report_count * 100) if report_count > 0 else 0
            }
        
        # v2.8 vs v2.8.1
        for code in range(5):
            v28_count = v28_total.get(code, 0)
            v281_count = v281_total.get(code, 0)
            improvement = v281_count - v28_count
            
            gaps['v28_vs_v281'][code] = {
                'v28': v28_count,
                'v281': v281_count,
                'improvement': improvement
            }
        
        # 요약 통계
        gaps['summary'] = {
            'total_rows_v28': v28_result.get('total_rows', 0),
            'total_rows_v281': v281_result.get('total_rows', 0),
            'expected_total': self.total_expected,
            'v28_accuracy': self._calculate_accuracy(v28_total),
            'v281_accuracy': self._calculate_accuracy(v281_total)
        }
        
        return gaps
    
    def _calculate_accuracy(self, distribution: Dict) -> float:
        """정확도 계산"""
        total_error = 0
        total_expected = 0
        
        for code in range(5):
            expected = self.report_distribution[code]
            actual = distribution.get(code, 0)
            total_error += abs(actual - expected)
            total_expected += expected
        
        return max(0, 1 - (total_error / total_expected)) if total_expected > 0 else 0
    
    def generate_validation_report(self, analysis: Dict, gaps: Dict) -> str:
        """검증 보고서 생성"""
        report = []
        report.append("# HVDC 실데이터 검증 보고서")
        report.append("**Date:** 2025-06-29")
        report.append("**Validator:** MACHO-GPT v3.4-mini")
        report.append("")
        
        # Executive Summary
        report.append("## 📋 Executive Summary")
        report.append("")
        v28_acc = gaps['summary']['v28_accuracy'] * 100
        v281_acc = gaps['summary']['v281_accuracy'] * 100
        total_rows = gaps['summary']['total_rows_v28']
        
        report.append(f"실제 Excel 데이터 **{total_rows:,}행**을 v2.8 및 v2.8.1 알고리즘으로 분석한 결과:")
        report.append(f"- **v2.8 정확도**: {v28_acc:.1f}%")
        report.append(f"- **v2.8.1 정확도**: {v281_acc:.1f}%")
        report.append(f"- **개선도**: {v281_acc - v28_acc:+.1f}%p")
        report.append("")
        
        # 데이터 구조 분석
        report.append("## 📊 데이터 구조 분석")
        report.append("")
        report.append(f"- **총 파일 수**: {analysis['total_files']}개")
        report.append(f"- **총 데이터**: {analysis['total_rows']:,}행")
        report.append("")
        
        for name, details in analysis['file_details'].items():
            report.append(f"### {name.upper()}")
            report.append(f"- 행 수: {details['rows']:,}")
            report.append(f"- 컬럼 수: {details['columns']}")
            report.append(f"- Location 컬럼: {'✅' if details['has_location'] else '❌'}")
            report.append(f"- Status 컬럼: {'✅' if details['has_status'] else '❌'}")
            if details['potential_wh_cols']:
                report.append(f"- WH 관련 컬럼: {details['potential_wh_cols'][:3]}")
            if details['potential_mosb_cols']:
                report.append(f"- MOSB 관련 컬럼: {details['potential_mosb_cols']}")
            report.append("")
        
        # 갭 분석 결과
        report.append("## 📈 Flow Code 분포 비교")
        report.append("")
        report.append("| Code | 정의 | 보고서 | v2.8 | v2.8.1 | v2.8 갭 | v2.8.1 갭 |")
        report.append("|:----:|:-----|:-----:|:----:|:------:|:-------:|:---------:|")
        
        definitions = {
            0: "Pre Arrival",
            1: "Port→Site", 
            2: "Port→WH→Site",
            3: "Port→WH→MOSB→Site",
            4: "Port→WH→wh→MOSB→Site"
        }
        
        for code in range(5):
            def_text = definitions[code]
            report_count = self.report_distribution[code]
            v28_gap = gaps['report_vs_v28'][code]
            v281_gap = gaps['report_vs_v281'][code]
            
            v28_gap_str = f"{v28_gap['gap']:+d}" if v28_gap['gap'] != 0 else "0"
            v281_gap_str = f"{v281_gap['gap']:+d}" if v281_gap['gap'] != 0 else "0"
            
            report.append(f"| {code} | {def_text} | {report_count:,} | {v28_gap['v28']:,} | {v281_gap['v281']:,} | {v28_gap_str} | {v281_gap_str} |")
        
        report.append("")
        
        # 문제점 및 개선사항
        if analysis['potential_issues']:
            report.append("## ⚠️ 발견된 문제점")
            report.append("")
            for issue in analysis['potential_issues'][:10]:  # 최대 10개만 표시
                report.append(f"- {issue}")
            report.append("")
        
        return "\n".join(report)
    
    def run_full_validation(self) -> Dict:
        """전체 검증 실행"""
        logger.info("🚀 HVDC 실데이터 검증 시작")
        logger.info("=" * 60)
        
        # 1. 데이터 로드
        dataframes = self.load_excel_files()
        if not dataframes:
            logger.error("❌ 로드된 데이터가 없습니다.")
            return {'success': False, 'error': 'No data loaded'}
        
        # 2. 데이터 구조 분석
        analysis = self.analyze_data_structure(dataframes)
        
        # 3. v2.8 알고리즘 테스트
        v28_result = self.test_current_v28_algorithm(dataframes)
        
        # 4. v2.8.1 알고리즘 테스트
        v281_result = self.test_improved_v281_algorithm(dataframes)
        
        # 5. 갭 분석
        gaps = self.calculate_gaps(v28_result, v281_result)
        
        # 6. 보고서 생성
        report = self.generate_validation_report(analysis, gaps)
        
        # 결과 출력
        logger.info("\n📊 검증 결과 요약:")
        logger.info(f"   총 데이터: {analysis['total_rows']:,}행")
        logger.info(f"   v2.8 정확도: {gaps['summary']['v28_accuracy']*100:.1f}%")
        logger.info(f"   v2.8.1 정확도: {gaps['summary']['v281_accuracy']*100:.1f}%")
        
        return {
            'success': True,
            'analysis': analysis,
            'v28_result': v28_result,
            'v281_result': v281_result,
            'gaps': gaps,
            'report': report
        }

def main():
    """메인 실행 함수"""
    validator = RealDataValidator()
    
    # 전체 검증 실행
    result = validator.run_full_validation()
    
    if result['success']:
        # 보고서 저장
        report_path = "HVDC_Real_Data_Validation_Report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(result['report'])
        
        logger.info(f"📋 검증 보고서 저장: {report_path}")
        
        # 추천 명령어
        logger.info("\n🔧 **추천 명령어:**")
        logger.info("/logi_master validate_real_data --complete [전체 실데이터 검증]")
        logger.info("/logi_master compare_algorithms --v28_vs_v281 [알고리즘 성능 비교]")
        logger.info("/logi_master optimize_flow_code --target_accuracy 95 [Flow Code 최적화]")
    else:
        logger.error(f"❌ 검증 실패: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    main() 