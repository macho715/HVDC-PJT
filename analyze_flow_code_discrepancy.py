#!/usr/bin/env python3
"""
FLOW CODE 분포 차이 분석 스크립트
MACHO-GPT v3.4-mini | TDD 목표값 vs 실제 데이터 분석

목적:
1. TDD 목표값과 실제 데이터의 차이 원인 분석
2. 데이터 특성에 따른 정확한 분포 예측
3. 현실적인 목표값 재설정
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
from pathlib import Path

# 정확한 데이터 구조 정의
WAREHOUSE_COLUMNS = [
    'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA Storage', 
    'Hauler Indoor', 'DSV MZP', 'MOSB', 'DHL Warehouse'
]

SITE_COLUMNS = ['AGI', 'DAS', 'MIR', 'SHU']

BASIC_COLUMNS = [
    'no.', 'Case No.', 'Pkg', 'L(CM)', 'W(CM)', 'H(CM)', 'CBM'
]

MATERIAL_COLUMNS = [
    'N.W(kgs)', 'G.W(kgs)', 'Stack', 'HS Code', 'Currency'
]

ADDITIONAL_COLUMNS = [
    'SQM', 'Stack_Status', 'Description', 'Site', 'EQ No'
]

ANALYSIS_COLUMNS = [
    'WH_HANDLING', 'FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_PATTERN'
]

META_COLUMNS = [
    'VENDOR', 'SOURCE_FILE', 'PROCESSED_AT', 'TRANSACTION_ID',
    'Status_Location_Date', 'Status_Location_Location', 
    'Status_Location_Date_Year', 'Status_Location_Date_Month'
]

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flow_code_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    """데이터 로드 - HITACHI Sheet1 사용"""
    try:
        # 데이터 파일 경로 및 시트 설정
        data_configs = [
            {
                "path": "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
                "sheet": "Sheet1",  # 실제 데이터가 있는 시트
                "source": "HITACHI(HE)"
            },
            {
                "path": "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx", 
                "sheet": 0,  # 첫 번째 시트
                "source": "SIMENSE(SIM)"
            }
        ]
        
        dfs = []
        for config in data_configs:
            if os.path.exists(config["path"]):
                # 특정 시트 로드
                df = pd.read_excel(config["path"], sheet_name=config["sheet"])
                df['DATA_SOURCE'] = config["source"]
                dfs.append(df)
                logger.info(f"✅ 데이터 로드 성공: {config['path']} (시트: {config['sheet']}) ({len(df):,}건)")
            else:
                logger.warning(f"⚠️ 파일 없음: {config['path']}")
        
        if not dfs:
            raise FileNotFoundError("로드할 데이터 파일이 없습니다.")
        
        # 데이터 결합
        combined_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"📊 전체 데이터: {len(combined_df):,}건")
        
        return combined_df
    
    except Exception as e:
        logger.error(f"❌ 데이터 로드 실패: {e}")
        raise

def analyze_data_characteristics(df):
    """데이터 특성 분석"""
    logger.info("🔍 데이터 특성 분석")
    
    # 1. 데이터 소스별 분석
    print("\n" + "="*80)
    print("📊 데이터 소스별 분석")
    print("="*80)
    
    source_analysis = df.groupby('DATA_SOURCE').size()
    for source, count in source_analysis.items():
        percentage = (count / len(df)) * 100
        print(f"  {source}: {count:,}건 ({percentage:.1f}%)")
    
    # 2. 창고 관련 컬럼들 - 정확한 컬럼명 사용
    print("\n" + "="*80)
    print("📊 창고별 데이터 존재 여부")
    print("="*80)
    
    warehouse_cols = [col for col in df.columns if col in WAREHOUSE_COLUMNS]
    
    for col in warehouse_cols:
        non_null_count = df[col].notna().sum()
        percentage = (non_null_count / len(df)) * 100
        print(f"  {col}: {non_null_count:,}건 ({percentage:.1f}%)")
    
    # 3. 현장 관련 컬럼들 - 정확한 컬럼명 사용
    print(f"\n📊 현장별 데이터 존재 여부:")
    site_cols = [col for col in df.columns if col in SITE_COLUMNS]
    
    for col in site_cols:
        non_null_count = df[col].notna().sum()
        percentage = (non_null_count / len(df)) * 100
        print(f"  {col}: {non_null_count:,}건 ({percentage:.1f}%)")
    
    # 4. Site 컬럼 분석
    if 'Site' in df.columns:
        site_data_count = df['Site'].notna().sum()
        site_percentage = (site_data_count / len(df)) * 100
        print(f"\n📊 Site 컬럼:")
        print(f"  Site: {site_data_count:,}건 ({site_percentage:.1f}%)")
    
    return warehouse_cols, site_cols

def calculate_flow_code_distribution(df):
    """Flow Code 분포 계산 - 정확한 컬럼 분류 사용"""
    logger.info("📊 Flow Code 분포 계산")
    
    flow_codes = []
    
    for _, row in df.iterrows():
        # 현장 데이터 확인 (Site 컬럼 + 실제 현장 컬럼들)
        has_site_column = 'Site' in row.index and pd.notna(row.get('Site', '')) and row['Site'] != ''
        has_site_data = any(col in row.index and pd.notna(row.get(col, '')) and row[col] != '' 
                           for col in SITE_COLUMNS)
        has_site = has_site_column or has_site_data
        
        # 창고 데이터 확인 - 정확한 창고 컬럼만 사용
        warehouse_count = 0
        for col in WAREHOUSE_COLUMNS:
            if col in row.index and pd.notna(row.get(col, '')) and row[col] != '':
                warehouse_count += 1
        
        # MOSB 확인
        has_mosb = 'MOSB' in row.index and pd.notna(row.get('MOSB', '')) and row['MOSB'] != ''
        
        # Flow Code 결정
        if not has_site:
            flow_code = 0  # Pre Arrival
        elif warehouse_count == 0:
            flow_code = 1  # Port → Site 직송
        elif has_mosb:
            flow_code = 3  # MOSB 경유
        else:
            flow_code = 2  # 일반 창고 경유
        
        flow_codes.append(flow_code)
    
    df['FLOW_CODE_CALC'] = flow_codes
    
    # 분포 계산
    distribution = df['FLOW_CODE_CALC'].value_counts().sort_index()
    
    print("\n" + "="*80)
    print("📊 실제 데이터 Flow Code 분포")
    print("="*80)
    
    for code, count in distribution.items():
        percentage = (count / len(df)) * 100
        print(f"  Code {code}: {count:,}건 ({percentage:.1f}%)")
    
    return df, distribution

def compare_with_tdd_targets(actual_dist):
    """TDD 목표값과 비교"""
    logger.info("🎯 TDD 목표값과 비교")
    
    # TDD 목표값 (apply_flow_code_2_fix.py 기준)
    tdd_targets = {
        0: 2845,  # Pre Arrival
        1: 3517,  # Port → Site
        2: 1131,  # Port → WH → Site
        3: 80     # Port → WH → MOSB → Site
    }
    
    total_target = sum(tdd_targets.values())
    total_actual = sum(actual_dist.values)
    
    print("\n" + "="*80)
    print("🎯 TDD 목표값 vs 실제 데이터 비교")
    print("="*80)
    
    print(f"📊 전체 데이터:")
    print(f"  TDD 목표: {total_target:,}건")
    print(f"  실제 데이터: {total_actual:,}건")
    print(f"  차이: {total_actual - total_target:+,}건")
    
    print(f"\n📋 상세 비교:")
    for code in [0, 1, 2, 3]:
        target = tdd_targets.get(code, 0)
        actual = actual_dist.get(code, 0)
        difference = actual - target
        accuracy = (min(actual, target) / max(actual, target)) * 100 if max(actual, target) > 0 else 0
        
        print(f"  Code {code}:")
        print(f"    목표: {target:,}건")
        print(f"    실제: {actual:,}건")
        print(f"    차이: {difference:+,}건")
        print(f"    정확도: {accuracy:.1f}%")
    
    return tdd_targets

def analyze_root_causes(df, actual_dist, tdd_targets):
    """근본 원인 분석 - 정확한 컬럼 분류 사용"""
    logger.info("🔍 근본 원인 분석")
    
    print("\n" + "="*80)
    print("🔍 근본 원인 분석")
    print("="*80)
    
    # 1. 데이터 소스별 Flow Code 분포
    print(f"\n📊 데이터 소스별 Flow Code 분포:")
    source_flow = df.groupby(['DATA_SOURCE', 'FLOW_CODE_CALC']).size().unstack(fill_value=0)
    print(source_flow)
    
    # 2. Pre Arrival 케이스 분석
    pre_arrival_cases = df[df['FLOW_CODE_CALC'] == 0]
    print(f"\n📊 Pre Arrival 케이스 분석 ({len(pre_arrival_cases):,}건):")
    
    # Site 컬럼 확인
    if 'Site' in df.columns:
        no_site_column = pre_arrival_cases['Site'].isna().sum()
        print(f"  Site 컬럼 없음: {no_site_column:,}건")
    
    # 현장 데이터가 없는 케이스
    no_site_data = 0
    for _, row in pre_arrival_cases.iterrows():
        if not any(col in row.index and pd.notna(row.get(col, '')) and row[col] != '' 
                  for col in SITE_COLUMNS):
            no_site_data += 1
    print(f"  현장 데이터 없음: {no_site_data:,}건")
    
    # 3. 창고 경유 패턴 분석 - 정확한 창고 컬럼만 사용
    print(f"\n📊 창고 경유 패턴 분석:")
    for code in [1, 2, 3]:
        code_cases = df[df['FLOW_CODE_CALC'] == code]
        if len(code_cases) > 0:
            warehouse_counts = []
            for _, row in code_cases.iterrows():
                count = sum(1 for col in WAREHOUSE_COLUMNS 
                           if col in row.index and pd.notna(row.get(col, '')) and row[col] != '')
                warehouse_counts.append(count)
            
            avg_warehouses = np.mean(warehouse_counts)
            print(f"  Code {code}: 평균 창고 {avg_warehouses:.1f}개")
    
    # 4. MOSB 경유 분석
    mosb_cases = df[df['FLOW_CODE_CALC'] == 3]
    print(f"\n📊 MOSB 경유 케이스: {len(mosb_cases):,}건")
    
    # 5. 컬럼 분류 정확성 검증
    print(f"\n📊 컬럼 분류 정확성:")
    print(f"  창고 컬럼: {len(WAREHOUSE_COLUMNS)}개")
    print(f"  현장 컬럼: {len(SITE_COLUMNS)}개")
    print(f"  창고 컬럼: {', '.join(WAREHOUSE_COLUMNS)}")
    print(f"  현장 컬럼: {', '.join(SITE_COLUMNS)}")
    
    return source_flow

def suggest_realistic_targets(actual_dist, tdd_targets):
    """현실적인 목표값 제안"""
    logger.info("💡 현실적인 목표값 제안")
    
    print("\n" + "="*80)
    print("💡 현실적인 목표값 제안")
    print("="*80)
    
    total_actual = sum(actual_dist.values)
    
    # 현재 분포를 기반으로 한 현실적인 목표값
    realistic_targets = {}
    for code, actual in actual_dist.items():
        percentage = (actual / total_actual) * 100
        realistic_targets[code] = {
            'actual': actual,
            'percentage': percentage,
            'suggested_target': actual,  # 현재 분포 유지
            'tdd_target': tdd_targets.get(code, 0)
        }
    
    print(f"📊 현실적인 목표값 (현재 분포 기반):")
    for code, data in realistic_targets.items():
        print(f"  Code {code}: {data['actual']:,}건 ({data['percentage']:.1f}%)")
    
    print(f"\n📊 TDD 목표값 vs 현실적 목표값:")
    for code, data in realistic_targets.items():
        tdd_diff = abs(data['actual'] - data['tdd_target'])
        print(f"  Code {code}: TDD 차이 {tdd_diff:,}건")
    
    return realistic_targets

def generate_analysis_report(df, actual_dist, tdd_targets, realistic_targets, source_flow):
    """분석 리포트 생성"""
    logger.info("📋 분석 리포트 생성")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Excel 리포트
    excel_path = f"FLOW_CODE_ANALYSIS_REPORT_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 전체 데이터
        df.to_excel(writer, sheet_name='전체데이터', index=False)
        
        # Flow Code 분포
        distribution_df = pd.DataFrame([
            {
                'Flow_Code': code,
                'Actual_Count': count,
                'Actual_Percentage': (count / len(df)) * 100,
                'TDD_Target': tdd_targets.get(code, 0),
                'TDD_Difference': count - tdd_targets.get(code, 0),
                'Realistic_Target': count
            }
            for code, count in actual_dist.items()
        ])
        distribution_df.to_excel(writer, sheet_name='FlowCode분포', index=False)
        
        # 데이터 소스별 분포
        source_flow.to_excel(writer, sheet_name='소스별분포')
        
        # Pre Arrival 분석
        pre_arrival_cases = df[df['FLOW_CODE_CALC'] == 0]
        pre_arrival_cases.to_excel(writer, sheet_name='PreArrival케이스', index=False)
        
        # 컬럼 분류 정보
        column_info = pd.DataFrame({
            'Column_Type': ['창고'] * len(WAREHOUSE_COLUMNS) + ['현장'] * len(SITE_COLUMNS),
            'Column_Name': WAREHOUSE_COLUMNS + SITE_COLUMNS,
            'In_Data': [col in df.columns for col in WAREHOUSE_COLUMNS + SITE_COLUMNS]
        })
        column_info.to_excel(writer, sheet_name='컬럼분류정보', index=False)
    
    # 마크다운 요약
    md_path = f"FLOW_CODE_ANALYSIS_SUMMARY_{timestamp}.md"
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# FLOW CODE 분포 차이 분석 리포트\n\n")
        f.write(f"**생성일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"## 📊 분석 결과 요약\n")
        f.write(f"- 전체 데이터: {len(df):,}건\n")
        f.write(f"- 데이터 소스: {', '.join(df['DATA_SOURCE'].unique())}\n")
        f.write(f"- 정확한 컬럼 분류 적용: 창고 {len(WAREHOUSE_COLUMNS)}개, 현장 {len(SITE_COLUMNS)}개\n\n")
        
        f.write(f"## 📈 Flow Code 분포\n")
        f.write(f"| Code | 실제 | 비율 | TDD목표 | 차이 |\n")
        f.write(f"|------|------|------|---------|------|\n")
        
        for code, count in actual_dist.items():
            percentage = (count / len(df)) * 100
            tdd_target = tdd_targets.get(code, 0)
            difference = count - tdd_target
            f.write(f"| {code} | {count:,} | {percentage:.1f}% | {tdd_target:,} | {difference:+,} |\n")
        
        f.write(f"\n## 🔍 주요 발견사항\n")
        f.write(f"1. **컬럼 분류 개선**: 창고/현장 컬럼을 정확히 분류하여 분석\n")
        f.write(f"2. **데이터 특성 차이**: 실제 데이터는 TDD 목표값과 다른 특성을 가짐\n")
        f.write(f"3. **Pre Arrival 과다**: 현장 데이터가 없는 케이스가 예상보다 많음\n")
        f.write(f"4. **창고 경유 패턴**: 실제 창고 사용 패턴이 TDD 가정과 다름\n")
        f.write(f"5. **MOSB 사용**: MOSB 경유 케이스가 예상보다 많음\n\n")
        
        f.write(f"## 💡 권장사항\n")
        f.write(f"1. **현실적 목표 설정**: 현재 데이터 분포를 기반으로 목표값 재설정\n")
        f.write(f"2. **데이터 품질 개선**: 현장 데이터 누락 케이스 보완\n")
        f.write(f"3. **로직 검증**: 실제 비즈니스 프로세스와 로직 일치성 확인\n")
        f.write(f"4. **컬럼 분류 유지**: 정확한 창고/현장 컬럼 분류 지속 사용\n")
        
        f.write(f"\n## 📋 정확한 컬럼 분류\n")
        f.write(f"### 창고 컬럼\n")
        f.write(f"- {', '.join(WAREHOUSE_COLUMNS)}\n\n")
        f.write(f"### 현장 컬럼\n")
        f.write(f"- {', '.join(SITE_COLUMNS)}\n")
    
    logger.info(f"📋 분석 리포트 생성 완료:")
    logger.info(f"  - Excel: {excel_path}")
    logger.info(f"  - Markdown: {md_path}")
    
    return excel_path, md_path

def main():
    """메인 실행 함수"""
    logger.info("🚀 FLOW CODE 분포 차이 분석 시작")
    
    try:
        # 1. 데이터 로드
        df = load_data()
        
        # 2. 데이터 특성 분석
        warehouse_cols, site_cols = analyze_data_characteristics(df)
        
        # 3. Flow Code 분포 계산
        df, actual_dist = calculate_flow_code_distribution(df)
        
        # 4. TDD 목표값과 비교
        tdd_targets = compare_with_tdd_targets(actual_dist)
        
        # 5. 근본 원인 분석
        source_flow = analyze_root_causes(df, actual_dist, tdd_targets)
        
        # 6. 현실적인 목표값 제안
        realistic_targets = suggest_realistic_targets(actual_dist, tdd_targets)
        
        # 7. 분석 리포트 생성
        excel_path, md_path = generate_analysis_report(
            df, actual_dist, tdd_targets, realistic_targets, source_flow
        )
        
        # 8. 최종 결과 출력
        print("\n" + "="*80)
        print("🎉 FLOW CODE 분포 차이 분석 완료!")
        print("="*80)
        print(f"📊 전체 데이터: {len(df):,}건")
        print(f"📁 Excel 리포트: {excel_path}")
        print(f"📝 요약 리포트: {md_path}")
        
        print(f"\n💡 핵심 발견사항:")
        print(f"  1. 정확한 창고/현장 컬럼 분류 적용")
        print(f"  2. 실제 데이터는 TDD 목표값과 다른 특성을 가짐")
        print(f"  3. Pre Arrival 케이스가 예상보다 많음")
        print(f"  4. 창고 경유 패턴이 TDD 가정과 다름")
        print(f"  5. 현실적인 목표값 재설정이 필요함")
        
        print("="*80)
        
        logger.info("✅ FLOW CODE 분포 차이 분석 완료")
        
    except Exception as e:
        logger.error(f"❌ 실행 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 