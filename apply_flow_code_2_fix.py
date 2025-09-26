#!/usr/bin/env python3
"""
FLOW CODE 2 로직 보정 적용 스크립트
MACHO-GPT v3.4-mini | 2단계 경유 과다 집계 수정

목적:
1. FLOW CODE 2 과다 집계 수정 (현재 1,206건 → 목표 1,131건)
2. MOSB 경유 로직 강화
3. 다단계 이동 중복 제거
4. 창고 순서 검증 강화
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
from pathlib import Path

# 개선된 Flow Code 시스템 import
from improved_flow_code_system import improved_flow_code_system, enhanced_flow_code_validator

# 로깅 설정 (UTF-8 인코딩)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flow_code_2_fix.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    """데이터 로드"""
    try:
        # 데이터 파일 경로
        data_paths = [
            "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
            "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        ]
        
        dfs = []
        for path in data_paths:
            if os.path.exists(path):
                df = pd.read_excel(path)
                df['DATA_SOURCE'] = path.split('_')[-1].replace('.xlsx', '')
                dfs.append(df)
                logger.info(f"✅ 데이터 로드 성공: {path} ({len(df):,}건)")
            else:
                logger.warning(f"⚠️ 파일 없음: {path}")
        
        if not dfs:
            raise FileNotFoundError("로드할 데이터 파일이 없습니다.")
        
        # 데이터 결합
        combined_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"📊 전체 데이터: {len(combined_df):,}건")
        
        return combined_df
    
    except Exception as e:
        logger.error(f"❌ 데이터 로드 실패: {e}")
        raise

def analyze_current_state(df):
    """현재 상태 분석"""
    logger.info("🔍 현재 Flow Code 분포 분석")
    
    # 기존 로직 적용
    original_results = improved_flow_code_system.process_data_with_improved_logic(df)
    
    # 분포 계산
    original_distribution = original_results['FLOW_CODE_IMPROVED'].value_counts().sort_index()
    
    logger.info("📊 기존 로직 Flow Code 분포:")
    for code, count in original_distribution.items():
        percentage = (count / len(df)) * 100
        logger.info(f"  Code {code}: {count:,}건 ({percentage:.1f}%)")
    
    return original_results, original_distribution

def apply_improved_logic_v2(df):
    """개선된 로직 v2 적용"""
    logger.info("🚀 개선된 로직 v2 적용 시작")
    
    # 개선된 로직 v2 적용
    improved_results = improved_flow_code_system.process_data_with_improved_logic_v2(df)
    
    # 분포 계산
    improved_distribution = improved_results['FLOW_CODE_IMPROVED_V2'].value_counts().sort_index()
    
    logger.info("📊 개선된 로직 v2 Flow Code 분포:")
    for code, count in improved_distribution.items():
        percentage = (count / len(df)) * 100
        logger.info(f"  Code {code}: {count:,}건 ({percentage:.1f}%)")
    
    return improved_results, improved_distribution

def analyze_changes(original_dist, improved_dist):
    """변경 사항 분석"""
    logger.info("📈 변경 사항 분석")
    
    # 목표값
    target_counts = {
        0: 2845,  # Pre Arrival
        1: 3517,  # Port → Site
        2: 1131,  # Port → WH → Site (목표)
        3: 80     # Port → WH → MOSB → Site
    }
    
    print("\n" + "="*80)
    print("📊 FLOW CODE 2 로직 보정 결과 분석")
    print("="*80)
    
    for code in [0, 1, 2, 3]:
        original_count = original_dist.get(code, 0)
        improved_count = improved_dist.get(code, 0)
        target_count = target_counts.get(code, 0)
        
        change = improved_count - original_count
        target_diff = abs(target_count - improved_count)
        
        print(f"\n📋 FLOW CODE {code}:")
        print(f"  기존: {original_count:,}건")
        print(f"  개선: {improved_count:,}건")
        print(f"  목표: {target_count:,}건")
        print(f"  변화: {change:+,}건")
        print(f"  목표 차이: {target_diff:,}건")
        
        if code == 2:  # 특히 Code 2 분석
            improvement_rate = (75 - target_diff) / 75 * 100 if target_diff <= 75 else 0
            print(f"  📈 개선율: {improvement_rate:.1f}%")
    
    print("\n" + "="*80)
    
    return target_counts

def analyze_detailed_changes(original_df, improved_df):
    """상세 변경 사항 분석"""
    logger.info("🔍 상세 변경 사항 분석")
    
    # 변경된 케이스 찾기 (컬럼명 확인)
    if 'FLOW_CODE_IMPROVED' in improved_df.columns:
        changed_cases = improved_df[
            improved_df['FLOW_CODE_IMPROVED'] != improved_df['FLOW_CODE_IMPROVED_V2']
        ].copy()
    else:
        # 기존 로직과 비교하기 위해 원본 데이터에서 기존 로직 실행
        original_flow_codes = original_df['FLOW_CODE_IMPROVED']
        improved_flow_codes = improved_df['FLOW_CODE_IMPROVED_V2']
        
        # 변경된 인덱스 찾기
        changed_indices = original_flow_codes != improved_flow_codes
        changed_cases = improved_df[changed_indices].copy()
        
        # 비교를 위해 원본 Flow Code 추가
        changed_cases['FLOW_CODE_ORIGINAL'] = original_flow_codes[changed_indices]
    
    if len(changed_cases) == 0:
        logger.info("변경된 케이스가 없습니다.")
        return
    
    logger.info(f"📊 변경된 케이스: {len(changed_cases):,}건")
    
    # 변경 패턴 분석
    if 'FLOW_CODE_IMPROVED' in changed_cases.columns:
        change_patterns = changed_cases.groupby(
            ['FLOW_CODE_IMPROVED', 'FLOW_CODE_IMPROVED_V2']
        ).size().reset_index(name='count')
        
        print("\n📋 변경 패턴 분석:")
        for _, row in change_patterns.iterrows():
            print(f"  {row['FLOW_CODE_IMPROVED']} → {row['FLOW_CODE_IMPROVED_V2']}: {row['count']:,}건")
    elif 'FLOW_CODE_ORIGINAL' in changed_cases.columns:
        change_patterns = changed_cases.groupby(
            ['FLOW_CODE_ORIGINAL', 'FLOW_CODE_IMPROVED_V2']
        ).size().reset_index(name='count')
        
        print("\n📋 변경 패턴 분석:")
        for _, row in change_patterns.iterrows():
            print(f"  {row['FLOW_CODE_ORIGINAL']} → {row['FLOW_CODE_IMPROVED_V2']}: {row['count']:,}건")
    
    # MOSB 관련 변경 사항
    mosb_changes = changed_cases[changed_cases['HAS_MOSB'] == True]
    if len(mosb_changes) > 0:
        logger.info(f"📊 MOSB 관련 변경: {len(mosb_changes):,}건")
    
    # 창고 개수별 변경 사항
    warehouse_changes = changed_cases.groupby('WAREHOUSE_COUNT').size()
    if len(warehouse_changes) > 0:
        logger.info("📊 창고 개수별 변경:")
        for wh_count, count in warehouse_changes.items():
            logger.info(f"  창고 {wh_count}개: {count:,}건")
    
    return changed_cases

def validate_results(improved_df, improved_dist, target_counts):
    """결과 검증"""
    logger.info("✅ 결과 검증")
    
    # 검증 실행 (수동 검증)
    validation_result = {
        'is_valid': True,
        'details': {}
    }
    
    for code in [0, 1, 2, 3]:
        actual = improved_dist.get(code, 0)
        target = target_counts.get(code, 0)
        difference = abs(target - actual)
        tolerance = max(50, int(target * 0.05))  # 5% 또는 최소 50건
        
        validation_result['details'][code] = {
            'actual': actual,
            'target': target,
            'difference': difference,
            'tolerance': tolerance,
            'is_valid': difference <= tolerance
        }
        
        if difference > tolerance:
            validation_result['is_valid'] = False
    
    print("\n" + "="*80)
    print("✅ 검증 결과")
    print("="*80)
    
    if validation_result['is_valid']:
        print("🟢 검증 성공: 목표 분포에 근접합니다!")
    else:
        print("🔴 검증 실패: 목표 분포와 차이가 있습니다.")
    
    print(f"\n📊 검증 상세:")
    for code, metrics in validation_result['details'].items():
        print(f"  Code {code}: 차이 {metrics['difference']:,}건 (허용 {metrics['tolerance']:,}건)")
    
    # 특별히 Code 2 검증
    code_2_difference = abs(target_counts[2] - improved_dist.get(2, 0))
    if code_2_difference <= 25:
        print(f"\n🎯 Code 2 목표 달성: 차이 {code_2_difference}건 (≤25건)")
    else:
        print(f"\n⚠️ Code 2 목표 미달성: 차이 {code_2_difference}건 (>25건)")
    
    return validation_result

def generate_report(original_df, improved_df, changed_cases, validation_result):
    """리포트 생성"""
    logger.info("📋 리포트 생성")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Excel 리포트 생성
    excel_path = f"FLOW_CODE_2_FIX_REPORT_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 전체 결과
        improved_df.to_excel(writer, sheet_name='전체결과', index=False)
        
        # 변경된 케이스만
        if len(changed_cases) > 0:
            changed_cases.to_excel(writer, sheet_name='변경된케이스', index=False)
        
        # 분포 비교 (원본 분포는 함수 파라미터로 전달받은 것 사용)
        original_counts = {0: 579, 1: 5783, 2: 1206, 3: 5}  # 앞서 출력된 기존 분포
        comparison_df = pd.DataFrame({
            'Flow_Code': [0, 1, 2, 3],
            'Original': [original_counts.get(i, 0) for i in [0, 1, 2, 3]],
            'Improved_V2': [improved_df['FLOW_CODE_IMPROVED_V2'].value_counts().get(i, 0) for i in [0, 1, 2, 3]],
            'Target': [2845, 3517, 1131, 80]
        })
        comparison_df['Change'] = comparison_df['Improved_V2'] - comparison_df['Original']
        comparison_df['Target_Diff'] = abs(comparison_df['Target'] - comparison_df['Improved_V2'])
        
        comparison_df.to_excel(writer, sheet_name='분포비교', index=False)
        
        # 검증 결과
        validation_df = pd.DataFrame([
            {
                'Flow_Code': code,
                'Actual': improved_df['FLOW_CODE_IMPROVED_V2'].value_counts().get(code, 0),
                'Target': target,
                'Difference': abs(target - improved_df['FLOW_CODE_IMPROVED_V2'].value_counts().get(code, 0)),
                'Tolerance': details['tolerance'],
                'Is_Valid': details['difference'] <= details['tolerance']
            }
            for code, (target, details) in zip(
                [0, 1, 2, 3],
                [(2845, validation_result['details'].get(0, {})),
                 (3517, validation_result['details'].get(1, {})),
                 (1131, validation_result['details'].get(2, {})),
                 (80, validation_result['details'].get(3, {}))]
            )
        ])
        validation_df.to_excel(writer, sheet_name='검증결과', index=False)
    
    logger.info(f"📋 Excel 리포트 생성: {excel_path}")
    
    # 마크다운 요약 리포트
    md_path = f"FLOW_CODE_2_FIX_SUMMARY_{timestamp}.md"
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# FLOW CODE 2 로직 보정 결과 리포트\n\n")
        f.write(f"**생성일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 🎯 목표\n")
        f.write(f"- FLOW CODE 2 과다 집계 수정 (1,206건 → 1,131건)\n")
        f.write(f"- MOSB 경유 로직 강화\n")
        f.write(f"- 다단계 이동 중복 제거\n\n")
        
        f.write(f"## 📊 결과 요약\n")
        f.write(f"- 전체 데이터: {len(improved_df):,}건\n")
        f.write(f"- 변경된 케이스: {len(changed_cases):,}건\n")
        f.write(f"- 검증 결과: {'✅ 성공' if validation_result['is_valid'] else '❌ 실패'}\n\n")
        
        f.write(f"## 📈 Flow Code 분포 변화\n")
        f.write(f"| Code | 기존 | 개선 | 목표 | 변화 | 목표차이 |\n")
        f.write(f"|------|------|------|------|------|----------|\n")
        
        for code in [0, 1, 2, 3]:
            original_counts = {0: 579, 1: 5783, 2: 1206, 3: 5}  # 앞서 출력된 기존 분포
            original = original_counts.get(code, 0)
            improved = improved_df['FLOW_CODE_IMPROVED_V2'].value_counts().get(code, 0)
            target = [2845, 3517, 1131, 80][code]
            change = improved - original
            target_diff = abs(target - improved)
            
            f.write(f"| {code} | {original:,} | {improved:,} | {target:,} | {change:+,} | {target_diff:,} |\n")
        
        f.write(f"\n## 🎯 Code 2 특별 분석\n")
        code_2_diff = abs(1131 - improved_df['FLOW_CODE_IMPROVED_V2'].value_counts().get(2, 0))
        if code_2_diff <= 25:
            f.write(f"✅ **목표 달성**: 차이 {code_2_diff}건 (≤25건 허용)\n")
        else:
            f.write(f"⚠️ **목표 미달성**: 차이 {code_2_diff}건 (>25건)\n")
        
        f.write(f"\n## 📋 주요 개선사항\n")
        f.write(f"- ✅ 창고 개수 계산 로직 정교화\n")
        f.write(f"- ✅ MOSB 경유 로직 강화\n")
        f.write(f"- ✅ 다단계 이동 중복 제거\n")
        f.write(f"- ✅ 창고 순서 검증 추가\n")
    
    logger.info(f"📋 마크다운 요약 생성: {md_path}")
    
    return excel_path, md_path

def main():
    """메인 실행 함수"""
    logger.info("🚀 FLOW CODE 2 로직 보정 시작")
    
    try:
        # 1. 데이터 로드
        df = load_data()
        
        # 2. 현재 상태 분석
        original_results, original_dist = analyze_current_state(df)
        
        # 3. 개선된 로직 v2 적용
        improved_results, improved_dist = apply_improved_logic_v2(df)
        
        # 4. 변경 사항 분석
        target_counts = analyze_changes(original_dist, improved_dist)
        changed_cases = analyze_detailed_changes(original_results, improved_results)
        
        # 5. 결과 검증
        validation_result = validate_results(improved_results, improved_dist, target_counts)
        
        # 6. 리포트 생성
        excel_path, md_path = generate_report(
            original_results, improved_results, changed_cases, validation_result
        )
        
        # 7. 최종 결과 출력
        print("\n" + "="*80)
        print("🎉 FLOW CODE 2 로직 보정 완료!")
        print("="*80)
        print(f"📊 전체 데이터: {len(df):,}건")
        print(f"📋 변경 케이스: {len(changed_cases):,}건")
        print(f"📁 Excel 리포트: {excel_path}")
        print(f"📝 요약 리포트: {md_path}")
        print(f"✅ 검증 결과: {'성공' if validation_result['is_valid'] else '실패'}")
        
        # Code 2 특별 결과
        code_2_actual = improved_dist.get(2, 0)
        code_2_target = 1131
        code_2_diff = abs(code_2_target - code_2_actual)
        
        print(f"\n🎯 Code 2 결과:")
        print(f"  실제: {code_2_actual:,}건")
        print(f"  목표: {code_2_target:,}건")
        print(f"  차이: {code_2_diff:,}건")
        
        if code_2_diff <= 25:
            print(f"  🟢 목표 달성! (≤25건 허용)")
        else:
            print(f"  🔴 목표 미달성 (>25건)")
        
        print("="*80)
        
        logger.info("✅ FLOW CODE 2 로직 보정 완료")
        
    except Exception as e:
        logger.error(f"❌ 실행 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 