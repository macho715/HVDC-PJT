#!/usr/bin/env python3
"""
FLOW CODE 0 로직 보정 실제 적용 스크립트
MACHO-GPT v3.4-mini | 2,543건 차이 해결

적용 내용:
1. determine_flow_code 함수를 개선된 로직으로 교체
2. 실제 Pre Arrival 상태 식별 로직 적용
3. WH HANDLING NaN 처리 방식 개선
4. 검증 로직 강화
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
import logging

# 개선된 Flow Code 시스템 import
from improved_flow_code_system import ImprovedFlowCodeSystem, EnhancedFlowCodeValidator

class FlowCode0FixApplier:
    """FLOW CODE 0 로직 보정 적용기"""
    
    def __init__(self):
        """초기화"""
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 개선된 시스템 인스턴스
        self.improved_system = ImprovedFlowCodeSystem()
        self.validator = EnhancedFlowCodeValidator()
        
        # 파일 경로 설정
        self.file_paths = {
            'HITACHI': "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
            'SIMENSE': "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        }
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 예상 결과
        self.expected_counts = {
            'COMBINED': {0: 2845, 1: 3517, 2: 1131, 3: 80, 'total': 7573}
        }
        
    def load_original_data(self):
        """원본 데이터 로드"""
        print("📂 원본 데이터 로드 중...")
        
        all_data = []
        
        for vendor, file_path in self.file_paths.items():
            if os.path.exists(file_path):
                print(f"   📄 {vendor} 데이터 로드: {file_path}")
                df = pd.read_excel(file_path)
                df['VENDOR'] = vendor
                all_data.append(df)
                print(f"   ✅ {vendor}: {len(df):,}건")
            else:
                print(f"   ❌ {vendor} 파일을 찾을 수 없습니다: {file_path}")
        
        if not all_data:
            raise FileNotFoundError("로드할 데이터가 없습니다.")
        
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"📊 총 데이터: {len(combined_df):,}건")
        
        return combined_df
    
    def apply_original_logic(self, df):
        """기존 로직 적용 (비교용)"""
        print("\n🔍 기존 로직 적용 중...")
        
        result_df = df.copy()
        
        # 기존 WH HANDLING 계산
        result_df['WH_HANDLING_ORIGINAL'] = result_df.apply(
            self.calculate_wh_handling_original, axis=1
        )
        
        # 기존 Flow Code 계산
        result_df['FLOW_CODE_ORIGINAL'] = result_df['WH_HANDLING_ORIGINAL'].apply(
            self.determine_flow_code_original
        )
        
        return result_df
    
    def calculate_wh_handling_original(self, row):
        """기존 WH HANDLING 계산 방식"""
        count = 0
        for col in self.improved_system.warehouse_columns:
            if col in row.index:
                value = row[col]
                if pd.notna(value) and value != '' and str(value).strip() != '':
                    try:
                        if isinstance(value, (int, float)):
                            count += 1
                        elif isinstance(value, str):
                            if value.replace('-', '').replace('/', '').replace(' ', '').replace(':', '').isdigit():
                                count += 1
                        elif hasattr(value, 'date'):
                            count += 1
                    except:
                        pass
        return count
    
    def determine_flow_code_original(self, wh_handling):
        """기존 Flow Code 결정 방식 (문제가 있는 로직)"""
        if pd.isna(wh_handling):
            return 0  # 문제 지점: NaN이면 무조건 0
        
        wh_val = int(wh_handling)
        if wh_val <= 3:
            return wh_val
        else:
            return 3
    
    def apply_improved_logic(self, df):
        """개선된 로직 적용"""
        print("\n🔧 개선된 로직 적용 중...")
        
        result_df = self.improved_system.process_data_with_improved_logic(df)
        
        return result_df
    
    def compare_results(self, df_original, df_improved):
        """결과 비교"""
        print("\n📊 결과 비교 분석")
        print("=" * 80)
        
        # 기존 로직 결과
        original_flow_counts = df_original['FLOW_CODE_ORIGINAL'].value_counts().sort_index()
        print("📋 기존 로직 Flow Code 분포:")
        for code, count in original_flow_counts.items():
            percentage = count / len(df_original) * 100
            print(f"   Code {code}: {count:,}건 ({percentage:.1f}%)")
        
        # 개선된 로직 결과
        improved_flow_counts = df_improved['FLOW_CODE_IMPROVED'].value_counts().sort_index()
        print("\n🔧 개선된 로직 Flow Code 분포:")
        for code, count in improved_flow_counts.items():
            percentage = count / len(df_improved) * 100
            print(f"   Code {code}: {count:,}건 ({percentage:.1f}%)")
        
        # 차이 분석
        print("\n📈 차이 분석:")
        for code in range(4):
            original_count = original_flow_counts.get(code, 0)
            improved_count = improved_flow_counts.get(code, 0)
            difference = improved_count - original_count
            expected_count = self.expected_counts['COMBINED'].get(code, 0)
            
            print(f"   Code {code}:")
            print(f"     기존: {original_count:,}건")
            print(f"     개선: {improved_count:,}건")
            print(f"     예상: {expected_count:,}건")
            print(f"     차이: {difference:+,}건")
            
            # 목표 달성도
            if expected_count > 0:
                original_accuracy = (1 - abs(expected_count - original_count) / expected_count) * 100
                improved_accuracy = (1 - abs(expected_count - improved_count) / expected_count) * 100
                print(f"     정확도: {original_accuracy:.1f}% → {improved_accuracy:.1f}%")
        
        # FLOW CODE 0 특별 분석
        print("\n🎯 FLOW CODE 0 (Pre Arrival) 특별 분석:")
        code_0_original = original_flow_counts.get(0, 0)
        code_0_improved = improved_flow_counts.get(0, 0)
        code_0_expected = self.expected_counts['COMBINED'][0]
        
        original_diff = abs(code_0_expected - code_0_original)
        improved_diff = abs(code_0_expected - code_0_improved)
        
        print(f"   목표: {code_0_expected:,}건")
        print(f"   기존: {code_0_original:,}건 (차이: {original_diff:,}건)")
        print(f"   개선: {code_0_improved:,}건 (차이: {improved_diff:,}건)")
        print(f"   개선 효과: {original_diff - improved_diff:+,}건 차이 감소")
        
        if improved_diff <= 100:
            print("   ✅ 목표 달성! (100건 이하 차이)")
        elif improved_diff < original_diff:
            print("   🔄 개선됨 (차이 감소)")
        else:
            print("   ⚠️ 추가 개선 필요")
        
        return {
            'original_counts': dict(original_flow_counts),
            'improved_counts': dict(improved_flow_counts),
            'expected_counts': self.expected_counts['COMBINED'],
            'code_0_improvement': original_diff - improved_diff
        }
    
    def validate_results(self, comparison_result):
        """결과 검증"""
        print("\n✅ 결과 검증")
        print("=" * 50)
        
        validation_result = self.validator.validate_distribution(
            comparison_result['improved_counts']
        )
        
        print(f"📋 검증 상태: {'✅ 통과' if validation_result['is_valid'] else '❌ 실패'}")
        print(f"📊 총 차이: {validation_result['total_difference']:,}건")
        
        if validation_result['errors']:
            print("⚠️ 오류 목록:")
            for error in validation_result['errors']:
                print(f"   - {error}")
        
        if validation_result['recommendations']:
            print("💡 권장사항:")
            for rec in validation_result['recommendations']:
                print(f"   - {rec}")
        
        return validation_result
    
    def export_results(self, df_original, df_improved, comparison_result, validation_result):
        """결과 내보내기"""
        print("\n📁 결과 내보내기")
        print("=" * 40)
        
        output_filename = f"FLOW_CODE_0_FIX_APPLIED_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # 스타일 정의
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4CAF50',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            # 시트 1: 개선된 결과
            df_improved.to_excel(writer, sheet_name='개선된_결과', index=False)
            
            # 시트 2: 기존 결과 (비교용)
            df_original[['VENDOR', 'WH_HANDLING_ORIGINAL', 'FLOW_CODE_ORIGINAL']].to_excel(
                writer, sheet_name='기존_결과_비교용', index=False
            )
            
            # 시트 3: 비교 분석
            comparison_df = pd.DataFrame([
                {
                    'Flow_Code': f'Code {code}',
                    'Expected': comparison_result['expected_counts'].get(code, 0),
                    'Original': comparison_result['original_counts'].get(code, 0),
                    'Improved': comparison_result['improved_counts'].get(code, 0),
                    'Original_Diff': abs(comparison_result['expected_counts'].get(code, 0) - 
                                        comparison_result['original_counts'].get(code, 0)),
                    'Improved_Diff': abs(comparison_result['expected_counts'].get(code, 0) - 
                                        comparison_result['improved_counts'].get(code, 0))
                }
                for code in range(4)
            ])
            comparison_df.to_excel(writer, sheet_name='비교_분석', index=False)
            
            # 시트 4: 검증 결과
            validation_df = pd.DataFrame([
                {
                    'Metric': 'Validation Status',
                    'Value': '통과' if validation_result['is_valid'] else '실패'
                },
                {
                    'Metric': 'Total Difference',
                    'Value': validation_result['total_difference']
                },
                {
                    'Metric': 'Code 0 Improvement',
                    'Value': comparison_result['code_0_improvement']
                }
            ])
            validation_df.to_excel(writer, sheet_name='검증_결과', index=False)
        
        print(f"✅ 결과 파일 저장: {output_filename}")
        return output_filename
    
    def run_fix_application(self):
        """전체 수정 적용 실행"""
        print("🚀 FLOW CODE 0 로직 보정 적용 시작")
        print("=" * 80)
        print("목표: 2,543건 차이 해결")
        print("=" * 80)
        
        try:
            # 1. 원본 데이터 로드
            original_df = self.load_original_data()
            
            # 2. 기존 로직 적용
            df_with_original = self.apply_original_logic(original_df)
            
            # 3. 개선된 로직 적용
            df_with_improved = self.apply_improved_logic(original_df)
            
            # 4. 결과 비교
            comparison_result = self.compare_results(df_with_original, df_with_improved)
            
            # 5. 결과 검증
            validation_result = self.validate_results(comparison_result)
            
            # 6. 결과 내보내기
            output_file = self.export_results(
                df_with_original, df_with_improved, 
                comparison_result, validation_result
            )
            
            # 7. 최종 요약
            print("\n" + "=" * 80)
            print("🎉 FLOW CODE 0 로직 보정 적용 완료!")
            print("=" * 80)
            print(f"📊 처리된 데이터: {len(original_df):,}건")
            print(f"📁 결과 파일: {output_file}")
            print(f"🎯 Code 0 개선 효과: {comparison_result['code_0_improvement']:+,}건")
            print(f"✅ 검증 상태: {'통과' if validation_result['is_valid'] else '실패'}")
            
            # TODO 상태 업데이트
            if abs(comparison_result['code_0_improvement']) >= 2000:
                print("\n🎊 2,543건 차이 해결 목표 달성!")
                return True
            else:
                print("\n🔄 추가 개선이 필요합니다.")
                return False
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            self.logger.error(f"Flow Code 0 수정 적용 실패: {e}")
            return False

def main():
    """메인 함수"""
    print("🔧 MACHO-GPT v3.4-mini │ FLOW CODE 0 로직 보정 적용")
    print("TDD 방식으로 개발된 개선된 로직 적용")
    print("=" * 80)
    
    fixer = FlowCode0FixApplier()
    success = fixer.run_fix_application()
    
    if success:
        print("\n🔧 **추천 명령어:**")
        print("/validate flow_code_distribution [분포 검증 상세 분석]")
        print("/analyze pre_arrival_accuracy [Pre Arrival 정확도 분석]")
        print("/implement system_logic_fix_2 [다음 로직 보정 단계]")
    else:
        print("\n⚠️ 추가 분석이 필요합니다.")
        print("/debug flow_code_logic [로직 디버깅]")
        print("/analyze data_quality [데이터 품질 분석]")

if __name__ == "__main__":
    main() 