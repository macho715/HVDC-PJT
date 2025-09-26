#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini | 업데이트된 HITACHI 데이터 분석
Samsung C&T × ADNOC DSV Partnership | HVDC 프로젝트

업데이트된 HITACHI 데이터 파일 분석:
- 데이터 구조 변경사항 확인
- 건수 변화 분석
- 컬럼 구조 검증
- Flow Code 영향도 평가
- 세부 로직 보강 방향 수립

Enhanced Integration: 
✅ 실시간 데이터 변경 감지
✅ 자동 영향도 평가
✅ 로직 보정 우선순위 결정
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import logging
from pathlib import Path
import traceback
from typing import Dict, List, Tuple, Optional, Any

# 기존 시스템 import
try:
    from improved_flow_code_system import ImprovedFlowCodeSystem
    from inventory_location_consistency import validate_quantity_consistency
except ImportError as e:
    print(f"⚠️ 기존 시스템 모듈 로드 실패: {e}")

class UpdatedHitachiDataAnalyzer:
    """업데이트된 HITACHI 데이터 분석기"""
    
    def __init__(self):
        """분석기 초기화"""
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.mode = "LATTICE"
        
        # 파일 경로
        self.hitachi_file = "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.simense_file = "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        
        # 기존 기준값 (이전 분석 결과)
        self.previous_expectations = {
            'HITACHI': {
                'total_count': 5346,
                'flow_distribution': {0: 1819, 1: 2561, 2: 886, 3: 80},
                'expected_columns': [
                    'Case No.', 'Package', 'DSV Indoor', 'DSV Outdoor', 
                    'DSV Al Markaz', 'MOSB', 'MIR', 'SHU', 'DAS', 'AGI'
                ]
            }
        }
        
        # 분석 결과 저장
        self.analysis_results = {}
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - MACHO-GPT - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 개선된 Flow Code 시스템
        try:
            self.flow_system = ImprovedFlowCodeSystem()
        except:
            self.flow_system = None
            print("⚠️ Flow Code 시스템 로드 실패")
    
    def load_updated_data(self) -> Dict[str, pd.DataFrame]:
        """업데이트된 데이터 로드"""
        print(f"📂 업데이트된 HITACHI 데이터 로드 시작...")
        print(f"🎯 {self.mode} 모드: 정밀 데이터 분석")
        
        data_frames = {}
        
        try:
            # HITACHI 데이터 로드
            if os.path.exists(self.hitachi_file):
                print(f"   📊 HITACHI 데이터 로드: {self.hitachi_file}")
                
                # 파일 정보 확인
                file_size = os.path.getsize(self.hitachi_file) / (1024 * 1024)  # MB
                print(f"   📏 파일 크기: {file_size:.1f}MB")
                
                df_hitachi = pd.read_excel(self.hitachi_file)
                data_frames['HITACHI'] = df_hitachi
                
                print(f"   ✅ HITACHI: {len(df_hitachi):,}건 로드 완료")
                print(f"   📋 컬럼 수: {len(df_hitachi.columns)}개")
                
            else:
                print(f"   ❌ HITACHI 파일 없음: {self.hitachi_file}")
                return {}
            
            # SIMENSE 데이터도 비교용으로 로드
            if os.path.exists(self.simense_file):
                print(f"   📊 SIMENSE 데이터 로드 (비교용): {self.simense_file}")
                df_simense = pd.read_excel(self.simense_file)
                data_frames['SIMENSE'] = df_simense
                print(f"   ✅ SIMENSE: {len(df_simense):,}건 로드 완료")
            
            return data_frames
            
        except Exception as e:
            print(f"   ❌ 데이터 로드 실패: {e}")
            self.logger.error(f"데이터 로드 오류: {e}")
            return {}
    
    def analyze_data_changes(self, df_hitachi: pd.DataFrame) -> Dict[str, Any]:
        """데이터 변경사항 분석"""
        print("\n" + "="*80)
        print("🔍 데이터 변경사항 분석")
        print("="*80)
        
        changes_analysis = {
            'record_count_change': {},
            'column_structure_change': {},
            'data_quality_metrics': {},
            'impact_assessment': {}
        }
        
        # 1. 레코드 수 변화 분석
        current_count = len(df_hitachi)
        previous_count = self.previous_expectations['HITACHI']['total_count']
        count_difference = current_count - previous_count
        
        changes_analysis['record_count_change'] = {
            'previous_count': previous_count,
            'current_count': current_count,
            'difference': count_difference,
            'change_percentage': (count_difference / previous_count) * 100,
            'significant_change': abs(count_difference) > 100
        }
        
        print(f"📊 레코드 수 변화:")
        print(f"   이전: {previous_count:,}건")
        print(f"   현재: {current_count:,}건")
        print(f"   차이: {count_difference:+,}건 ({changes_analysis['record_count_change']['change_percentage']:+.1f}%)")
        
        # 2. 컬럼 구조 변화 분석
        current_columns = set(df_hitachi.columns)
        expected_columns = set(self.previous_expectations['HITACHI']['expected_columns'])
        
        new_columns = current_columns - expected_columns
        missing_columns = expected_columns - current_columns
        common_columns = current_columns & expected_columns
        
        changes_analysis['column_structure_change'] = {
            'total_columns': len(current_columns),
            'new_columns': list(new_columns),
            'missing_columns': list(missing_columns),
            'common_columns': list(common_columns),
            'structure_changed': len(new_columns) > 0 or len(missing_columns) > 0
        }
        
        print(f"\n📋 컬럼 구조 변화:")
        print(f"   전체 컬럼: {len(current_columns)}개")
        print(f"   새 컬럼: {len(new_columns)}개 {list(new_columns)[:5]}")
        print(f"   누락 컬럼: {len(missing_columns)}개 {list(missing_columns)}")
        print(f"   공통 컬럼: {len(common_columns)}개")
        
        # 3. 데이터 품질 지표
        quality_metrics = {}
        
        # 필수 컬럼 완전성 확인
        essential_columns = ['Case No.', 'Package']
        for col in essential_columns:
            if col in df_hitachi.columns:
                completeness = df_hitachi[col].notna().sum() / len(df_hitachi)
                quality_metrics[f'{col}_completeness'] = completeness
                print(f"   {col} 완전성: {completeness:.1%}")
        
        # 중복 데이터 확인
        if 'Case No.' in df_hitachi.columns:
            duplicates = df_hitachi.duplicated(subset=['Case No.']).sum()
            duplicate_rate = duplicates / len(df_hitachi)
            quality_metrics['duplicate_rate'] = duplicate_rate
            print(f"   중복률: {duplicate_rate:.1%} ({duplicates}건)")
        
        changes_analysis['data_quality_metrics'] = quality_metrics
        
        return changes_analysis
    
    def analyze_flow_code_impact(self, df_hitachi: pd.DataFrame) -> Dict[str, Any]:
        """Flow Code 영향도 분석"""
        print("\n" + "="*80)
        print("🎯 Flow Code 영향도 분석")
        print("="*80)
        
        if not self.flow_system:
            print("   ⚠️ Flow Code 시스템을 사용할 수 없음")
            return {}
        
        flow_impact = {
            'current_distribution': {},
            'expected_distribution': {},
            'discrepancies': {},
            'improvement_opportunities': []
        }
        
        try:
            # 현재 데이터로 Flow Code 계산
            print("   🔧 현재 데이터로 Flow Code 계산 중...")
            processed_df = self.flow_system.process_data_with_improved_logic_v2(df_hitachi)
            
            if 'FLOW_CODE_IMPROVED_V2' in processed_df.columns:
                current_distribution = processed_df['FLOW_CODE_IMPROVED_V2'].value_counts().sort_index()
                flow_impact['current_distribution'] = dict(current_distribution)
                
                # 기대값과 비교
                expected_distribution = self.previous_expectations['HITACHI']['flow_distribution']
                flow_impact['expected_distribution'] = expected_distribution
                
                print("   📈 Flow Code 분포 분석:")
                print("   Code | 현재    | 기대    | 차이     | 정확도")
                print("   -----|---------|---------|----------|--------")
                
                total_error = 0
                for code in [0, 1, 2, 3]:
                    current = flow_impact['current_distribution'].get(code, 0)
                    expected = expected_distribution.get(code, 0)
                    difference = current - expected
                    accuracy = 1 - (abs(difference) / expected) if expected > 0 else 1
                    
                    total_error += abs(difference)
                    
                    flow_impact['discrepancies'][code] = {
                        'current': current,
                        'expected': expected,
                        'difference': difference,
                        'accuracy': accuracy
                    }
                    
                    status = "✅" if abs(difference) <= 50 else "⚠️" if abs(difference) <= 200 else "❌"
                    print(f"   {code:4} | {current:7,} | {expected:7,} | {difference:+8,} | {accuracy:6.1%} {status}")
                
                # 전체 정확도
                overall_accuracy = 1 - (total_error / sum(expected_distribution.values()))
                flow_impact['overall_accuracy'] = overall_accuracy
                print(f"\n   📊 전체 정확도: {overall_accuracy:.1%}")
                
                # 개선 기회 식별
                if flow_impact['discrepancies'][0]['accuracy'] < 0.9:
                    flow_impact['improvement_opportunities'].append("FLOW CODE 0 로직 개선 필요")
                if flow_impact['discrepancies'][1]['accuracy'] < 0.9:
                    flow_impact['improvement_opportunities'].append("FLOW CODE 1 로직 개선 필요")
                if flow_impact['discrepancies'][3]['accuracy'] < 0.9:
                    flow_impact['improvement_opportunities'].append("FLOW CODE 3 로직 개선 필요")
                
            else:
                print("   ❌ Flow Code 계산 실패")
                
        except Exception as e:
            print(f"   ❌ Flow Code 분석 오류: {e}")
            self.logger.error(f"Flow Code 분석 오류: {e}")
        
        return flow_impact
    
    def identify_logic_enhancement_priorities(self, changes_analysis: Dict, flow_impact: Dict) -> List[Dict[str, Any]]:
        """로직 보강 우선순위 식별"""
        print("\n" + "="*80)
        print("🚀 로직 보강 우선순위 분석")
        print("="*80)
        
        priorities = []
        
        # 1. Flow Code 0 로직 (Pre Arrival) 개선
        if flow_impact.get('discrepancies', {}).get(0, {}).get('accuracy', 1) < 0.8:
            difference = flow_impact['discrepancies'][0]['difference']
            priority_score = abs(difference) / 100  # 100건당 1점
            
            priorities.append({
                'priority': 1,
                'category': 'FLOW_CODE_0_LOGIC',
                'title': 'Pre Arrival 로직 정교화',
                'description': f"현재 {difference:+,}건 오차, Pre Arrival 식별 로직 개선 필요",
                'impact_score': priority_score,
                'estimated_effort': 'HIGH',
                'business_value': 'CRITICAL',
                'implementation_complexity': 'MEDIUM'
            })
        
        # 2. Flow Code 1 로직 (직송) 개선  
        if flow_impact.get('discrepancies', {}).get(1, {}).get('accuracy', 1) < 0.8:
            difference = flow_impact['discrepancies'][1]['difference']
            priority_score = abs(difference) / 100
            
            priorities.append({
                'priority': 2,
                'category': 'FLOW_CODE_1_LOGIC',
                'title': 'Port → Site 직송 로직 개선',
                'description': f"현재 {difference:+,}건 오차, 직송 경로 식별 정교화 필요",
                'impact_score': priority_score,
                'estimated_effort': 'MEDIUM',
                'business_value': 'HIGH',
                'implementation_complexity': 'LOW'
            })
        
        # 3. Flow Code 3 로직 (다단계) 개선
        if flow_impact.get('discrepancies', {}).get(3, {}).get('accuracy', 1) < 0.8:
            difference = flow_impact['discrepancies'][3]['difference']
            priority_score = abs(difference) / 100
            
            priorities.append({
                'priority': 3,
                'category': 'FLOW_CODE_3_LOGIC',
                'title': '다단계 경유 로직 최적화',
                'description': f"현재 {difference:+,}건 오차, MOSB 경유 및 복잡 경로 로직 개선",
                'impact_score': priority_score,
                'estimated_effort': 'HIGH',
                'business_value': 'MEDIUM',
                'implementation_complexity': 'HIGH'
            })
        
        # 4. 데이터 품질 개선
        if changes_analysis.get('data_quality_metrics', {}).get('duplicate_rate', 0) > 0.01:
            priorities.append({
                'priority': 4,
                'category': 'DATA_QUALITY',
                'title': '데이터 품질 개선',
                'description': "중복 데이터 제거 및 데이터 정합성 강화",
                'impact_score': changes_analysis['data_quality_metrics']['duplicate_rate'] * 100,
                'estimated_effort': 'LOW',
                'business_value': 'MEDIUM',
                'implementation_complexity': 'LOW'
            })
        
        # 5. 시스템 통합 최적화
        overall_accuracy = flow_impact.get('overall_accuracy', 1.0)
        if overall_accuracy < 0.95:
            priorities.append({
                'priority': 5,
                'category': 'SYSTEM_INTEGRATION',
                'title': '전체 시스템 균형 조정',
                'description': f"현재 {overall_accuracy:.1%} 정확도, 95% 목표 달성을 위한 종합 최적화",
                'impact_score': (0.95 - overall_accuracy) * 1000,
                'estimated_effort': 'HIGH',
                'business_value': 'CRITICAL',
                'implementation_complexity': 'HIGH'
            })
        
        # 우선순위 정렬 (impact_score 기준)
        priorities.sort(key=lambda x: x['impact_score'], reverse=True)
        
        # 우선순위 재부여
        for i, priority in enumerate(priorities, 1):
            priority['priority'] = i
        
        print("📋 식별된 로직 보강 우선순위:")
        for priority in priorities:
            print(f"   {priority['priority']}. {priority['title']}")
            print(f"      📊 영향도: {priority['impact_score']:.1f}")
            print(f"      🔧 노력: {priority['estimated_effort']}")
            print(f"      💰 가치: {priority['business_value']}")
            print(f"      🏗️ 복잡도: {priority['implementation_complexity']}")
            print()
        
        return priorities
    
    def generate_enhancement_roadmap(self, priorities: List[Dict]) -> Dict[str, Any]:
        """로직 보강 로드맵 생성"""
        print("\n" + "="*80)
        print("🗺️ 로직 보강 로드맵 생성")
        print("="*80)
        
        roadmap = {
            'phase_1_immediate': [],
            'phase_2_short_term': [],
            'phase_3_long_term': [],
            'implementation_timeline': {},
            'resource_requirements': {},
            'success_metrics': {}
        }
        
        # 우선순위에 따른 페이즈 분류
        for priority in priorities:
            if priority['priority'] <= 2 and priority['business_value'] == 'CRITICAL':
                roadmap['phase_1_immediate'].append(priority)
            elif priority['priority'] <= 4 or priority['estimated_effort'] in ['LOW', 'MEDIUM']:
                roadmap['phase_2_short_term'].append(priority)
            else:
                roadmap['phase_3_long_term'].append(priority)
        
        # 구현 타임라인
        roadmap['implementation_timeline'] = {
            'phase_1': '1-2주 (즉시 시작)',
            'phase_2': '3-6주 (단기 개선)',
            'phase_3': '2-3개월 (장기 최적화)'
        }
        
        # 리소스 요구사항
        roadmap['resource_requirements'] = {
            'development_time': '총 8-12주',
            'testing_time': '총 3-4주',
            'key_skills': ['Python/Pandas', 'TDD', '물류 도메인 지식', 'Excel 로직'],
            'team_size': '2-3명 (시니어 개발자 1명, 주니어 1-2명)'
        }
        
        # 성공 지표
        roadmap['success_metrics'] = {
            'overall_accuracy': '≥95%',
            'flow_code_0_accuracy': '≥90%',
            'flow_code_1_accuracy': '≥90%',
            'flow_code_3_accuracy': '≥85%',
            'processing_speed': '≥1000건/초',
            'data_quality': '≥98% 완전성, <1% 중복률'
        }
        
        print("🎯 Phase 1 - 즉시 개선 (1-2주):")
        for item in roadmap['phase_1_immediate']:
            print(f"   ✅ {item['title']}")
        
        print("\n🎯 Phase 2 - 단기 개선 (3-6주):")
        for item in roadmap['phase_2_short_term']:
            print(f"   🔧 {item['title']}")
        
        print("\n🎯 Phase 3 - 장기 최적화 (2-3개월):")
        for item in roadmap['phase_3_long_term']:
            print(f"   🚀 {item['title']}")
        
        return roadmap
    
    def save_analysis_report(self, data_analysis: Dict, flow_impact: Dict, priorities: List, roadmap: Dict):
        """분석 결과 리포트 저장"""
        print("\n" + "="*80)
        print("📁 분석 리포트 저장")
        print("="*80)
        
        report = {
            'analysis_timestamp': self.timestamp,
            'mode': self.mode,
            'data_analysis': data_analysis,
            'flow_code_impact': flow_impact,
            'enhancement_priorities': priorities,
            'implementation_roadmap': roadmap,
            'next_actions': [
                '1. Phase 1 즉시 개선 항목 구현',
                '2. TDD 방법론으로 각 로직 개선',
                '3. 실제 데이터로 검증 및 성능 측정',
                '4. 프로덕션 배포 준비'
            ]
        }
        
        # JSON 리포트 저장
        report_filename = f"HITACHI_Updated_Analysis_Report_{self.timestamp}.json"
        try:
            import json
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            print(f"   📊 JSON 리포트 저장: {report_filename}")
        except Exception as e:
            print(f"   ⚠️ JSON 리포트 저장 실패: {e}")
        
        # 마크다운 리포트 생성
        md_filename = f"HITACHI_Updated_Analysis_Report_{self.timestamp}.md"
        try:
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(f"# HITACHI 데이터 업데이트 분석 리포트\n\n")
                f.write(f"**분석 시각**: {self.timestamp}\n")
                f.write(f"**분석 모드**: {self.mode}\n\n")
                
                f.write("## 📊 데이터 변경사항\n\n")
                f.write(f"- **레코드 수 변화**: {data_analysis['record_count_change']['difference']:+,}건\n")
                f.write(f"- **컬럼 구조 변화**: {'있음' if data_analysis['column_structure_change']['structure_changed'] else '없음'}\n")
                
                f.write("\n## 🎯 Flow Code 영향도\n\n")
                if flow_impact.get('overall_accuracy'):
                    f.write(f"- **전체 정확도**: {flow_impact['overall_accuracy']:.1%}\n")
                
                f.write("\n## 🚀 개선 우선순위\n\n")
                for i, priority in enumerate(priorities, 1):
                    f.write(f"{i}. **{priority['title']}**\n")
                    f.write(f"   - 영향도: {priority['impact_score']:.1f}\n")
                    f.write(f"   - 비즈니스 가치: {priority['business_value']}\n\n")
                
            print(f"   📝 마크다운 리포트 저장: {md_filename}")
        except Exception as e:
            print(f"   ⚠️ 마크다운 리포트 저장 실패: {e}")
        
        return report
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """종합 분석 실행"""
        print("🚀 MACHO-GPT v3.4-mini | 업데이트된 HITACHI 데이터 종합 분석")
        print("🎯 LATTICE 모드: 정밀 데이터 변경사항 분석")
        print("Samsung C&T × ADNOC DSV Partnership | HVDC 프로젝트")
        
        try:
            # 1. 업데이트된 데이터 로드
            data_frames = self.load_updated_data()
            
            if 'HITACHI' not in data_frames:
                print("❌ HITACHI 데이터 로드 실패 - 분석을 중단합니다.")
                return {'error': 'DATA_LOAD_FAILED'}
            
            df_hitachi = data_frames['HITACHI']
            
            # 2. 데이터 변경사항 분석
            data_analysis = self.analyze_data_changes(df_hitachi)
            
            # 3. Flow Code 영향도 분석
            flow_impact = self.analyze_flow_code_impact(df_hitachi)
            
            # 4. 로직 보강 우선순위 식별
            priorities = self.identify_logic_enhancement_priorities(data_analysis, flow_impact)
            
            # 5. 구현 로드맵 생성
            roadmap = self.generate_enhancement_roadmap(priorities)
            
            # 6. 분석 리포트 저장
            final_report = self.save_analysis_report(data_analysis, flow_impact, priorities, roadmap)
            
            # 7. 최종 결과 요약
            print("\n" + "="*100)
            print("🏆 HITACHI 데이터 업데이트 분석 완료")
            print("="*100)
            
            overall_accuracy = flow_impact.get('overall_accuracy', 0)
            critical_changes = data_analysis['record_count_change']['significant_change']
            high_priority_items = len([p for p in priorities if p['business_value'] == 'CRITICAL'])
            
            print(f"📊 분석 결과 요약:")
            print(f"   - 전체 정확도: {overall_accuracy:.1%}")
            print(f"   - 중대한 데이터 변화: {'있음' if critical_changes else '없음'}")
            print(f"   - 긴급 개선 항목: {high_priority_items}개")
            print(f"   - 전체 개선 항목: {len(priorities)}개")
            
            # 다음 단계 추천
            print(f"\n📋 다음 단계 추천:")
            if high_priority_items > 0:
                print(f"   🚨 즉시 Phase 1 개선 항목 구현 시작")
                print(f"   🔧 TDD 방법론으로 로직 보정")
                print(f"   📊 실시간 성능 모니터링 구축")
            else:
                print(f"   ✅ 현재 시스템 상태 양호")
                print(f"   🔧 점진적 성능 최적화 진행")
                print(f"   📈 프로덕션 배포 준비")
            
            return final_report
            
        except Exception as e:
            print(f"❌ 종합 분석 중 오류 발생: {e}")
            print(f"📋 상세 오류:\n{traceback.format_exc()}")
            return {'error': str(e), 'traceback': traceback.format_exc()}

def main():
    """메인 실행 함수"""
    print("🔌 MACHO-GPT v3.4-mini 업데이트된 HITACHI 데이터 분석 시스템")
    print("Enhanced MCP Integration | Samsung C&T Logistics")
    print("="*80)
    
    # 분석기 초기화
    analyzer = UpdatedHitachiDataAnalyzer()
    
    # 종합 분석 실행
    final_report = analyzer.run_comprehensive_analysis()
    
    # 종료 코드 결정
    if 'error' in final_report:
        exit_code = 2  # 오류
    elif final_report.get('enhancement_priorities', []):
        priority_count = len([p for p in final_report['enhancement_priorities'] if p['business_value'] == 'CRITICAL'])
        exit_code = 1 if priority_count > 0 else 0  # 개선 필요 vs 양호
    else:
        exit_code = 0  # 양호
    
    print(f"\n🏁 분석 완료 (종료 코드: {exit_code})")
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 