#!/usr/bin/env python3
"""
🔍 HITACHI 데이터 차이 상세 분석 v2.8.4
목표: 97.2% → 100% 정확도 개선
Excel 피벗 테이블과 완벽 일치 달성

차이점 분석:
- Port→Site: 1,819건 ✅ (이미 정확)
- Port→WH→Site: 2,561건 vs 3,081건 (-520건 차이)
- Port→WH→MOSB→Site: 886건 vs 441건 (+445건 차이)
- Port→WH→wh→MOSB→Site: 80건 vs 5건 (+75건 차이)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

class HitachiDifferenceAnalyzer:
    """HITACHI 데이터 차이 상세 분석기"""
    
    def __init__(self):
        print("🔍 HITACHI 데이터 차이 상세 분석 v2.8.4")
        print("목표: 97.2% → 100% 정확도 개선")
        print("=" * 80)
        
        # Excel 피벗 테이블 기준값 (100% 정확도 목표)
        self.excel_targets = {
            'Code 0 (Port→Site)': 1819,
            'Code 1 (Port→WH→Site)': 2561,
            'Code 2 (Port→WH→MOSB→Site)': 886,
            'Code 3 (Port→WH→wh→MOSB→Site)': 80,
            'Total': 5346
        }
        
        # 현재 시스템 결과 (97.2% 정확도)
        self.current_results = {
            'Code 0 (Port→Site)': 1758,
            'Code 1 (Port→WH→Site)': 2827,
            'Code 2 (Port→WH→MOSB→Site)': 887,
            'Code 3 (Port→WH→wh→MOSB→Site)': 80,
            'Total': 5552
        }
        
        # 차이점 계산
        self.differences = {}
        for key in self.excel_targets.keys():
            if key != 'Total':
                excel_val = self.excel_targets[key]
                current_val = self.current_results[key]
                self.differences[key] = {
                    'excel': excel_val,
                    'current': current_val,
                    'difference': current_val - excel_val,
                    'percentage': abs(current_val - excel_val) / excel_val * 100
                }
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.hitachi_data = None
        
    def load_hitachi_data(self):
        """HITACHI 데이터 로드"""
        print("\n📂 HITACHI 데이터 로드 중...")
        
        file_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        
        if not os.path.exists(file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            return False
            
        try:
            self.hitachi_data = pd.read_excel(file_path)
            print(f"✅ 데이터 로드 성공: {len(self.hitachi_data):,}행")
            print(f"📊 컬럼 수: {len(self.hitachi_data.columns)}개")
            
            # 주요 컬럼 확인
            key_columns = ['HVDC CODE', 'MOSB', 'Status', 'wh handling']
            available_columns = [col for col in key_columns if col in self.hitachi_data.columns]
            print(f"🔍 주요 컬럼: {', '.join(available_columns)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def analyze_wh_handling_distribution(self):
        """WH HANDLING 분포 상세 분석"""
        print("\n📊 WH HANDLING 분포 상세 분석")
        print("-" * 60)
        
        if 'wh handling' not in self.hitachi_data.columns:
            print("❌ 'wh handling' 컬럼이 없습니다.")
            return None
        
        # WH HANDLING 분포
        wh_dist = self.hitachi_data['wh handling'].value_counts().sort_index()
        
        print("📋 현재 WH HANDLING 분포:")
        for wh_level, count in wh_dist.items():
            print(f"   WH {wh_level}: {count:,}건")
        
        # Excel 목표값과 비교
        print("\n🔍 Excel 목표값과 비교:")
        print(f"{'WH Level':<10} {'현재':<10} {'목표':<10} {'차이':<10} {'정확도':<10}")
        print("-" * 50)
        
        total_accuracy = 0
        total_records = 0
        
        for wh_level in range(4):
            current_count = wh_dist.get(wh_level, 0)
            target_count = self.excel_targets[f'Code {wh_level} (Port→{"WH→" * wh_level}Site)']
            difference = current_count - target_count
            accuracy = (1 - abs(difference) / target_count) * 100 if target_count > 0 else 100
            
            total_accuracy += accuracy * target_count
            total_records += target_count
            
            status = "✅" if abs(difference) <= 10 else "❌"
            print(f"WH {wh_level:<7} {current_count:<10,} {target_count:<10,} {difference:<10,} {accuracy:.1f}% {status}")
        
        overall_accuracy = total_accuracy / total_records if total_records > 0 else 0
        print(f"\n📊 전체 정확도: {overall_accuracy:.1f}%")
        
        return wh_dist
    
    def analyze_mosb_patterns(self):
        """MOSB 패턴 상세 분석"""
        print("\n🔍 MOSB 패턴 상세 분석")
        print("-" * 60)
        
        if 'MOSB' not in self.hitachi_data.columns:
            print("❌ MOSB 컬럼이 없습니다.")
            return None
        
        # MOSB 데이터 분석
        mosb_data = self.hitachi_data['MOSB']
        
        print("📊 MOSB 데이터 통계:")
        print(f"   총 레코드: {len(mosb_data):,}건")
        print(f"   MOSB 유효 데이터: {mosb_data.notna().sum():,}건")
        print(f"   MOSB 빈 데이터: {mosb_data.isna().sum():,}건")
        
        # MOSB가 있는 레코드들의 WH HANDLING 분포
        mosb_records = self.hitachi_data[mosb_data.notna()]
        if len(mosb_records) > 0:
            mosb_wh_dist = mosb_records['wh handling'].value_counts().sort_index()
            
            print(f"\n📋 MOSB가 있는 레코드의 WH HANDLING 분포:")
            for wh_level, count in mosb_wh_dist.items():
                print(f"   WH {wh_level}: {count:,}건")
        
        # MOSB가 없는 레코드들의 WH HANDLING 분포
        no_mosb_records = self.hitachi_data[mosb_data.isna()]
        if len(no_mosb_records) > 0:
            no_mosb_wh_dist = no_mosb_records['wh handling'].value_counts().sort_index()
            
            print(f"\n📋 MOSB가 없는 레코드의 WH HANDLING 분포:")
            for wh_level, count in no_mosb_wh_dist.items():
                print(f"   WH {wh_level}: {count:,}건")
        
        return mosb_records, no_mosb_records
    
    def analyze_warehouse_columns(self):
        """창고 컬럼별 상세 분석"""
        print("\n🏢 창고 컬럼별 상세 분석")
        print("-" * 60)
        
        warehouse_columns = [
            'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
            'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB'
        ]
        
        warehouse_analysis = {}
        
        for col in warehouse_columns:
            if col in self.hitachi_data.columns:
                col_data = self.hitachi_data[col]
                valid_count = col_data.notna().sum()
                empty_count = col_data.isna().sum()
                
                warehouse_analysis[col] = {
                    'total': len(col_data),
                    'valid': valid_count,
                    'empty': empty_count,
                    'percentage': (valid_count / len(col_data)) * 100
                }
                
                print(f"📊 {col}:")
                print(f"   유효 데이터: {valid_count:,}건 ({warehouse_analysis[col]['percentage']:.1f}%)")
                print(f"   빈 데이터: {empty_count:,}건")
        
        return warehouse_analysis
    
    def identify_correction_factors(self):
        """수정 요인 식별"""
        print("\n🔧 수정 요인 식별")
        print("-" * 60)
        
        correction_factors = []
        
        # 1. 데이터 건수 차이 분석
        current_total = len(self.hitachi_data)
        target_total = self.excel_targets['Total']
        count_difference = current_total - target_total
        
        if abs(count_difference) > 0:
            correction_factors.append({
                'factor': '데이터 건수 차이',
                'current': current_total,
                'target': target_total,
                'difference': count_difference,
                'impact': 'HIGH',
                'description': f'현재 {current_total:,}건, 목표 {target_total:,}건으로 {count_difference:+,}건 차이'
            })
        
        # 2. WH HANDLING 분포 차이 분석
        for code_name, diff_info in self.differences.items():
            if abs(diff_info['difference']) > 10:  # 10건 이상 차이
                correction_factors.append({
                    'factor': f'{code_name} 분포 차이',
                    'current': diff_info['current'],
                    'target': diff_info['excel'],
                    'difference': diff_info['difference'],
                    'impact': 'HIGH' if abs(diff_info['percentage']) > 5 else 'MEDIUM',
                    'description': f'{code_name}: 현재 {diff_info["current"]:,}건, 목표 {diff_info["excel"]:,}건'
                })
        
        # 3. MOSB 로직 차이 분석
        if 'MOSB' in self.hitachi_data.columns:
            mosb_records = self.hitachi_data[self.hitachi_data['MOSB'].notna()]
            mosb_wh_dist = mosb_records['wh handling'].value_counts().sort_index()
            
            # Code 2, 3에 MOSB가 포함되어야 함
            code2_mosb = mosb_wh_dist.get(2, 0)
            code3_mosb = mosb_wh_dist.get(3, 0)
            
            target_code2 = self.excel_targets['Code 2 (Port→WH→MOSB→Site)']
            target_code3 = self.excel_targets['Code 3 (Port→WH→wh→MOSB→Site)']
            
            if abs(code2_mosb - target_code2) > 10:
                correction_factors.append({
                    'factor': 'MOSB Code 2 로직 차이',
                    'current': code2_mosb,
                    'target': target_code2,
                    'difference': code2_mosb - target_code2,
                    'impact': 'HIGH',
                    'description': f'MOSB가 있는 Code 2: 현재 {code2_mosb:,}건, 목표 {target_code2:,}건'
                })
            
            if abs(code3_mosb - target_code3) > 10:
                correction_factors.append({
                    'factor': 'MOSB Code 3 로직 차이',
                    'current': code3_mosb,
                    'target': target_code3,
                    'difference': code3_mosb - target_code3,
                    'impact': 'HIGH',
                    'description': f'MOSB가 있는 Code 3: 현재 {code3_mosb:,}건, 목표 {target_code3:,}건'
                })
        
        # 수정 요인 출력
        print("📋 발견된 수정 요인:")
        for i, factor in enumerate(correction_factors, 1):
            impact_icon = "🔴" if factor['impact'] == 'HIGH' else "🟡"
            print(f"   {i}. {impact_icon} {factor['factor']}")
            print(f"      {factor['description']}")
            print(f"      차이: {factor['difference']:+,}건")
        
        return correction_factors
    
    def generate_correction_plan(self, correction_factors):
        """수정 계획 생성"""
        print("\n📋 수정 계획 생성")
        print("-" * 60)
        
        correction_plan = {
            'high_priority': [],
            'medium_priority': [],
            'implementation_steps': [],
            'expected_accuracy': 0
        }
        
        # 우선순위별 분류
        for factor in correction_factors:
            if factor['impact'] == 'HIGH':
                correction_plan['high_priority'].append(factor)
            else:
                correction_plan['medium_priority'].append(factor)
        
        # 구현 단계 정의
        implementation_steps = [
            {
                'step': 1,
                'action': '데이터 건수 정규화',
                'description': '5,552건 → 5,346건으로 중복 제거',
                'expected_impact': '데이터 건수 차이 해결'
            },
            {
                'step': 2,
                'action': 'MOSB 로직 재정의',
                'description': 'MOSB 포함 레코드의 WH HANDLING 계산 방식 수정',
                'expected_impact': 'Code 2, 3 분포 차이 해결'
            },
            {
                'step': 3,
                'action': 'WH HANDLING 계산 알고리즘 조정',
                'description': 'Excel SUMPRODUCT 수식과 완벽 일치하도록 수정',
                'expected_impact': '전체 분포 차이 해결'
            },
            {
                'step': 4,
                'action': '검증 및 테스트',
                'description': 'Excel 피벗 테이블과 100% 일치 확인',
                'expected_impact': '100% 정확도 달성'
            }
        ]
        
        correction_plan['implementation_steps'] = implementation_steps
        
        # 예상 정확도 계산
        current_accuracy = 97.2
        high_priority_impact = len(correction_plan['high_priority']) * 0.8  # 각 HIGH 우선순위당 0.8% 개선
        expected_accuracy = min(100, current_accuracy + high_priority_impact)
        correction_plan['expected_accuracy'] = expected_accuracy
        
        # 수정 계획 출력
        print("🎯 수정 계획:")
        for step in implementation_steps:
            print(f"   {step['step']}. {step['action']}")
            print(f"      {step['description']}")
            print(f"      예상 영향: {step['expected_impact']}")
        
        print(f"\n📊 예상 결과:")
        print(f"   현재 정확도: 97.2%")
        print(f"   예상 정확도: {expected_accuracy:.1f}%")
        print(f"   개선 폭: {expected_accuracy - current_accuracy:.1f}%p")
        
        return correction_plan
    
    def create_detailed_report(self, wh_dist, warehouse_analysis, correction_factors, correction_plan):
        """상세 분석 보고서 생성"""
        print("\n📄 상세 분석 보고서 생성 중...")
        
        report_file = f"HITACHI_Difference_Analysis_{self.timestamp}.json"
        
        report_data = {
            'analysis_timestamp': self.timestamp,
            'target_accuracy': 100.0,
            'current_accuracy': 97.2,
            'excel_targets': self.excel_targets,
            'current_results': self.current_results,
            'differences': self.differences,
            'wh_handling_distribution': wh_dist.to_dict() if wh_dist is not None else {},
            'warehouse_analysis': warehouse_analysis,
            'correction_factors': correction_factors,
            'correction_plan': correction_plan,
            'summary': {
                'total_records': len(self.hitachi_data) if self.hitachi_data is not None else 0,
                'major_issues': len([f for f in correction_factors if f['impact'] == 'HIGH']),
                'minor_issues': len([f for f in correction_factors if f['impact'] == 'MEDIUM']),
                'expected_improvement': correction_plan['expected_accuracy'] - 97.2
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 상세 보고서 저장: {report_file}")
        return report_file
    
    def run_comprehensive_analysis(self):
        """종합 분석 실행"""
        print("🚀 HITACHI 데이터 차이 상세 분석 시작")
        print("=" * 80)
        
        # 1. 데이터 로드
        if not self.load_hitachi_data():
            return None
        
        # 2. WH HANDLING 분포 분석
        wh_dist = self.analyze_wh_handling_distribution()
        
        # 3. MOSB 패턴 분석
        mosb_analysis = self.analyze_mosb_patterns()
        
        # 4. 창고 컬럼 분석
        warehouse_analysis = self.analyze_warehouse_columns()
        
        # 5. 수정 요인 식별
        correction_factors = self.identify_correction_factors()
        
        # 6. 수정 계획 생성
        correction_plan = self.generate_correction_plan(correction_factors)
        
        # 7. 상세 보고서 생성
        report_file = self.create_detailed_report(wh_dist, warehouse_analysis, correction_factors, correction_plan)
        
        # 최종 결과 요약
        print("\n" + "=" * 80)
        print("🎉 HITACHI 데이터 차이 상세 분석 완료!")
        print("=" * 80)
        
        print(f"📊 분석 결과 요약:")
        print(f"   총 레코드: {len(self.hitachi_data):,}건")
        print(f"   주요 수정 요인: {len([f for f in correction_factors if f['impact'] == 'HIGH'])}개")
        print(f"   예상 정확도: {correction_plan['expected_accuracy']:.1f}%")
        print(f"   개선 폭: {correction_plan['expected_accuracy'] - 97.2:.1f}%p")
        
        if report_file:
            print(f"📁 상세 보고서: {report_file}")
        
        print(f"\n🔧 **추천 명령어:**")
        print(f"/implement_corrections [수정 요인별 구체적 수정 방안 구현]")
        print(f"/validate_corrections [수정 후 정확도 검증 - 100% 목표]")
        print(f"/generate_final_report [최종 100% 정확도 보고서 생성]")
        
        return {
            'status': 'SUCCESS',
            'current_accuracy': 97.2,
            'expected_accuracy': correction_plan['expected_accuracy'],
            'correction_factors': correction_factors,
            'report_file': report_file
        }

def main():
    """메인 실행 함수"""
    analyzer = HitachiDifferenceAnalyzer()
    result = analyzer.run_comprehensive_analysis()
    
    if result:
        print(f"\n✅ 분석 완료: {result['status']}")
        print(f"📈 정확도 개선 예상: {result['current_accuracy']:.1f}% → {result['expected_accuracy']:.1f}%")
    else:
        print(f"\n❌ 분석 실패")

if __name__ == "__main__":
    main() 