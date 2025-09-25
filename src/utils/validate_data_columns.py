import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime

REQUIRED_COLUMNS = ['Case No.', 'Vendor', 'Status_Current', 'Status_Location']

def validate_excel_columns(file_path: str) -> List[str]:
    """
    엑셀 파일의 컬럼 구조를 검증합니다.
    누락된 필수 컬럼을 리스트로 반환합니다.
    """
    df = pd.read_excel(file_path, nrows=1)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        print(f"[경고] 누락된 필수 컬럼: {missing}")
        print(f"[참고] 실제 컬럼 목록: {list(df.columns)}")
    else:
        print("[확인] 모든 필수 컬럼이 존재합니다.")
    return missing

def validate_vendor_data_quality(hitachi_file: str, simense_file: str) -> Dict[str, Any]:
    """
    벤더별 데이터 품질 종합 검증
    
    Args:
        hitachi_file: HITACHI 데이터 파일 경로
        simense_file: SIMENSE 데이터 파일 경로
        
    Returns:
        Dict: 검증 결과 및 통계
    """
    print("🔍 벤더별 데이터 품질 종합 검증 시작...")
    
    validation_results = {
        'hitachi_stats': {},
        'simense_stats': {},
        'combined_stats': {},
        'column_analysis': {},
        'status_analysis': {},
        'recommendations': []
    }
    
    # 1. HITACHI 파일 검증
    try:
        df_hitachi = pd.read_excel(hitachi_file)
        df_hitachi['Vendor'] = 'HITACHI'
        
        validation_results['hitachi_stats'] = {
            'total_records': len(df_hitachi),
            'columns': list(df_hitachi.columns),
            'missing_values': df_hitachi.isnull().sum().to_dict(),
            'data_types': df_hitachi.dtypes.to_dict()
        }
        print(f"✅ HITACHI 파일 검증 완료: {len(df_hitachi)}건")
        
    except Exception as e:
        print(f"❌ HITACHI 파일 검증 실패: {e}")
        validation_results['hitachi_stats'] = {'error': str(e)}
    
    # 2. SIMENSE 파일 검증
    try:
        df_simense = pd.read_excel(simense_file)
        df_simense['Vendor'] = 'SIMENSE'
        
        validation_results['simense_stats'] = {
            'total_records': len(df_simense),
            'columns': list(df_simense.columns),
            'missing_values': df_simense.isnull().sum().to_dict(),
            'data_types': df_simense.dtypes.to_dict()
        }
        print(f"✅ SIMENSE 파일 검증 완료: {len(df_simense)}건")
        
    except Exception as e:
        print(f"❌ SIMENSE 파일 검증 실패: {e}")
        validation_results['simense_stats'] = {'error': str(e)}
    
    # 3. 통합 데이터 검증
    if 'error' not in validation_results['hitachi_stats'] and 'error' not in validation_results['simense_stats']:
        df_combined = pd.concat([df_hitachi, df_simense], ignore_index=True)
        
        validation_results['combined_stats'] = {
            'total_records': len(df_combined),
            'vendor_distribution': df_combined['Vendor'].value_counts().to_dict(),
            'columns': list(df_combined.columns)
        }
        
        # 4. 컬럼 분석
        print("\n📊 컬럼 구조 분석:")
        for col in df_combined.columns:
            if col in ['Case No.', 'Vendor', 'Status_Current', 'Status_Location']:
                print(f"  ✅ 필수 컬럼: {col}")
            elif 'HVDC' in col or 'CODE' in col:
                print(f"  🔧 HVDC 컬럼: {col}")
                unique_values = df_combined[col].dropna().unique()[:5]
                print(f"    샘플 값: {unique_values}")
            elif any(loc in col for loc in ['DSV', 'AAA', 'MOSB', 'AGI', 'DAS', 'MIR', 'SHU']):
                print(f"  📍 위치 컬럼: {col}")
                non_null_count = df_combined[col].notna().sum()
                print(f"    유효 데이터: {non_null_count}/{len(df_combined)}")
        
        # 5. 상태별 분석
        print("\n📋 상태별 데이터 분석:")
        status_columns = [col for col in df_combined.columns if 'Status' in col or 'Current' in col]
        for col in status_columns:
            if col in df_combined.columns:
                status_counts = df_combined[col].value_counts()
                print(f"  {col}: {dict(status_counts)}")
        
        # 6. 위치별 분석
        print("\n📍 위치별 데이터 분석:")
        location_columns = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP', 
                           'MOSB', 'AAA  Storage', 'Hauler Indoor', 'AGI', 'DAS', 'MIR', 'SHU']
        for col in location_columns:
            if col in df_combined.columns:
                non_null_count = df_combined[col].notna().sum()
                if non_null_count > 0:
                    print(f"  {col}: {non_null_count}건")
        
        # 7. 권장사항 생성
        recommendations = []
        
        # 목표값과 비교
        target_hitachi = 5126
        target_simense = 1853
        target_total = 6979
        
        actual_hitachi = validation_results['combined_stats']['vendor_distribution'].get('HITACHI', 0)
        actual_simense = validation_results['combined_stats']['vendor_distribution'].get('SIMENSE', 0)
        actual_total = validation_results['combined_stats']['total_records']
        
        if actual_hitachi > target_hitachi:
            recommendations.append(f"HITACHI 데이터 {actual_hitachi - target_hitachi}건 초과 - 상태별 필터링 필요")
        if actual_simense > target_simense:
            recommendations.append(f"SIMENSE 데이터 {actual_simense - target_simense}건 초과 - 상태별 필터링 필요")
        if actual_total > target_total:
            recommendations.append(f"총 데이터 {actual_total - target_total}건 초과 - 완료된 아이템 제거 필요")
        
        validation_results['recommendations'] = recommendations
        
        print(f"\n📈 목표값 대비 현황:")
        print(f"  HITACHI: {actual_hitachi} vs {target_hitachi} ({actual_hitachi - target_hitachi:+d})")
        print(f"  SIMENSE: {actual_simense} vs {target_simense} ({actual_simense - target_simense:+d})")
        print(f"  Total: {actual_total} vs {target_total} ({actual_total - target_total:+d})")
        
        if recommendations:
            print(f"\n💡 권장사항:")
            for rec in recommendations:
                print(f"  - {rec}")
    
    return validation_results

def analyze_status_filtering(df: pd.DataFrame) -> Dict[str, Any]:
    """
    상태별 필터링 분석
    
    Args:
        df: 통합 데이터프레임
        
    Returns:
        Dict: 상태별 분석 결과
    """
    print("\n🔍 상태별 필터링 분석:")
    
    status_analysis = {}
    
    # 상태 관련 컬럼 찾기
    status_columns = [col for col in df.columns if 'Status' in col or 'Current' in col or 'Complete' in col]
    
    for col in status_columns:
        if col in df.columns:
            try:
                unique_values = df[col].dropna().unique()
                print(f"  {col}: {list(unique_values)}")
                
                # 각 상태별 벤더 분포 (날짜/시간 컬럼 제외)
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    status_vendor_counts = df.groupby([col, 'Vendor']).size().unstack(fill_value=0)
                    print(f"    벤더별 분포:\n{status_vendor_counts}")
                    
                    status_analysis[col] = {
                        'unique_values': list(unique_values),
                        'vendor_distribution': status_vendor_counts.to_dict()
                    }
                else:
                    print(f"    ⏰ 날짜/시간 컬럼 - 벤더별 분포 생략")
                    status_analysis[col] = {
                        'unique_values': list(unique_values),
                        'vendor_distribution': {}
                    }
            except Exception as e:
                print(f"    ❌ 분석 오류: {e}")
                status_analysis[col] = {'error': str(e)}
    
    return status_analysis

def apply_status_filtering(df: pd.DataFrame) -> pd.DataFrame:
    """
    상태별 필터링 적용 (Pre Arrival만 제거)
    
    Args:
        df: 원본 데이터프레임
        
    Returns:
        pd.DataFrame: 필터링된 데이터프레임
    """
    print("\n🔧 상태별 필터링 적용 (Pre Arrival만 제거):")
    
    original_count = len(df)
    df_filtered = df.copy()
    
    # 1. Pre Arrival 상태만 제거
    if 'Status_Current' in df_filtered.columns:
        pre_arrival_mask = df_filtered['Status_Current'] == 'Pre Arrival'
        pre_arrival_count = pre_arrival_mask.sum()
        df_filtered = df_filtered[~pre_arrival_mask]
        print(f"  ✅ Pre Arrival 제거: {pre_arrival_count}건")
    
    # 2. Status_Storage에서 Pre Arrival 제거 (중복 확인)
    if 'Status_Storage' in df_filtered.columns:
        storage_pre_arrival_mask = df_filtered['Status_Storage'] == 'Pre Arrival'
        storage_pre_arrival_count = storage_pre_arrival_mask.sum()
        if storage_pre_arrival_count > 0:
            df_filtered = df_filtered[~storage_pre_arrival_mask]
            print(f"  ✅ Status_Storage Pre Arrival 제거: {storage_pre_arrival_count}건")
    
    # 3. Status_Location에서 Pre Arrival 제거
    if 'Status_Location' in df_filtered.columns:
        location_pre_arrival_mask = df_filtered['Status_Location'] == 'Pre Arrival'
        location_pre_arrival_count = location_pre_arrival_mask.sum()
        if location_pre_arrival_count > 0:
            df_filtered = df_filtered[~location_pre_arrival_mask]
            print(f"  ✅ Status_Location Pre Arrival 제거: {location_pre_arrival_count}건")
    
    filtered_count = len(df_filtered)
    removed_count = original_count - filtered_count
    
    print(f"  📊 필터링 결과: {original_count} → {filtered_count} (제거: {removed_count}건)")
    
    # 벤더별 분포 확인
    if 'Vendor' in df_filtered.columns:
        vendor_dist = df_filtered['Vendor'].value_counts()
        print(f"  📋 필터링 후 벤더별 분포:")
        for vendor, count in vendor_dist.items():
            print(f"    {vendor}: {count}건")
    
    # 상태별 분포 확인
    if 'Status_Current' in df_filtered.columns:
        status_dist = df_filtered['Status_Current'].value_counts()
        print(f"  📋 필터링 후 상태별 분포:")
        for status, count in status_dist.items():
            print(f"    {status}: {count}건")
    
    return df_filtered

def validate_filtered_data_quality(df_filtered: pd.DataFrame) -> Dict[str, Any]:
    """
    필터링된 데이터 품질 검증
    
    Args:
        df_filtered: 필터링된 데이터프레임
        
    Returns:
        Dict: 검증 결과
    """
    print("\n🔍 필터링된 데이터 품질 검증:")
    
    validation_results = {
        'total_records': len(df_filtered),
        'vendor_distribution': {},
        'location_distribution': {},
        'target_comparison': {},
        'recommendations': []
    }
    
    # 벤더별 분포
    if 'Vendor' in df_filtered.columns:
        vendor_dist = df_filtered['Vendor'].value_counts().to_dict()
        validation_results['vendor_distribution'] = vendor_dist
        print(f"  📊 벤더별 분포: {vendor_dist}")
    
    # 위치별 분포
    if 'Status_Location' in df_filtered.columns:
        location_dist = df_filtered['Status_Location'].value_counts().to_dict()
        validation_results['location_distribution'] = location_dist
        print(f"  📍 위치별 분포: {location_dist}")
    
    # 목표값과 비교
    target_hitachi = 5126
    target_simense = 1853
    target_total = 6979
    
    actual_hitachi = vendor_dist.get('HITACHI', 0)
    actual_simense = vendor_dist.get('SIMENSE', 0)
    actual_total = len(df_filtered)
    
    validation_results['target_comparison'] = {
        'hitachi': {'actual': actual_hitachi, 'target': target_hitachi, 'difference': actual_hitachi - target_hitachi},
        'simense': {'actual': actual_simense, 'target': target_simense, 'difference': actual_simense - target_simense},
        'total': {'actual': actual_total, 'target': target_total, 'difference': actual_total - target_total}
    }
    
    print(f"\n📈 목표값 대비 현황:")
    print(f"  HITACHI: {actual_hitachi} vs {target_hitachi} ({actual_hitachi - target_hitachi:+d})")
    print(f"  SIMENSE: {actual_simense} vs {target_simense} ({actual_simense - target_simense:+d})")
    print(f"  Total: {actual_total} vs {target_total} ({actual_total - target_total:+d})")
    
    # 권장사항 생성
    if actual_hitachi > target_hitachi:
        validation_results['recommendations'].append(f"HITACHI 여전히 {actual_hitachi - target_hitachi}건 초과")
    if actual_simense > target_simense:
        validation_results['recommendations'].append(f"SIMENSE 여전히 {actual_simense - target_simense}건 초과")
    if actual_total > target_total:
        validation_results['recommendations'].append(f"총 데이터 여전히 {actual_total - target_total}건 초과")
    
    if validation_results['recommendations']:
        print(f"\n💡 추가 권장사항:")
        for rec in validation_results['recommendations']:
            print(f"  - {rec}")
    else:
        print(f"\n✅ 목표값 달성!")
    
    return validation_results

def validate_hitachi_location_targets(df_filtered: pd.DataFrame) -> None:
    """
    HITACHI 벤더에 대해 위치별 목표값과 실제값을 비교하여 일치 여부를 검증합니다.
    목표값은 Pre Arrival 제외, 표의 값으로 하드코딩.
    """
    print("\n📋 HITACHI 위치별 목표값 일치 검증:")
    # 위치별 목표값 (Pre Arrival 제외)
    hitachi_targets = {
        'AGI': 40,
        'DAS': 964,
        'MIR': 753,
        'SHU': 1304,
        'AAA  Storage': 392,
        'DHL Warehouse': 119,
        'DSV Al Markaz': 256,
        'DSV Indoor': 360,
        'DSV Outdoor': 788,
        'Hauler Indoor': 10,
        'MOSB': 38
    }
    # HITACHI만 필터링
    df_hitachi = df_filtered[df_filtered['Vendor'] == 'HITACHI']
    # 위치별 집계
    actual_counts = df_hitachi['Status_Location'].value_counts().to_dict()
    total_actual = 0
    total_target = 0
    for loc, target in hitachi_targets.items():
        actual = actual_counts.get(loc, 0)
        match = '✅' if actual == target else f'❌ (차이: {actual - target:+d})'
        print(f"  {loc:<15} 목표: {target:<4} | 실제: {actual:<4} {match}")
        total_actual += actual
        total_target += target
    print(f"  {'TOTAL':<15} 목표: {total_target:<4} | 실제: {total_actual:<4} {'✅' if total_actual == total_target else f'❌ (차이: {total_actual - total_target:+d})'}")

def summarize_location_pivot(
    df: pd.DataFrame,
    value_col: str = "Case No.",
    storage_col: str = "Status_Storage",
    location_col: str = "Status_Location",
    sublocation_col: str = None
) -> pd.DataFrame:
    """
    원본 데이터에서 Status_Storage, Status_Location, (선택) 세부 Location별로 합계를 자동 집계합니다.
    Args:
        df: 원본 데이터프레임
        value_col: 집계할 값 컬럼명 (예: 'Case No.', '합계 : Pkg' 등)
        storage_col: 1차 그룹핑 컬럼 (예: 'Status_Storage')
        location_col: 2차 그룹핑 컬럼 (예: 'Status_Location')
        sublocation_col: 3차 그룹핑 컬럼 (예: 'Status_Location_DSV Indoor'), 없으면 2단계만
    Returns:
        pd.DataFrame: 피벗테이블 형태의 집계 결과
    """
    group_cols = [storage_col, location_col]
    if sublocation_col and sublocation_col in df.columns:
        group_cols.append(sublocation_col)
    summary = (
        df.groupby(group_cols)[value_col]
        .count()
        .reset_index()
        .rename(columns={value_col: "count"})
    )
    return summary

def excel_style_pivot(
    df: pd.DataFrame,
    value_col: str = "Case No.",
    index_cols: list = None,
    columns_col: str = "total handling",
    aggfunc: str = "count"
) -> pd.DataFrame:
    """
    엑셀 피벗테이블(행+열+값) 구조로 자동 집계
    Args:
        df: 원본 데이터프레임
        value_col: 값 필드 (예: '합계 : Pkg', 'Case No.')
        index_cols: 행 필드 리스트
        columns_col: 열 필드 (예: 'total handling')
        aggfunc: 집계 함수 ('count', 'sum' 등)
    Returns:
        pd.DataFrame: 피벗테이블 결과
    """
    if index_cols is None:
        index_cols = [
            "Status_Storage",
            "Status_Location",
            "Status_Location_DSV Indoor",
            "Status_Location_DSV Al Markaz"
        ]
    pivot = pd.pivot_table(
        df,
        index=index_cols,
        columns=columns_col,
        values=value_col,
        aggfunc=aggfunc,
        fill_value=0,
        margins=True,
        margins_name="총합계"
    )
    return pivot

if __name__ == "__main__":
    # 벤더별 파일 품질 검증 실행
    hitachi_file = "data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
    simense_file = "data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
    
    validation_results = validate_vendor_data_quality(hitachi_file, simense_file)
    
    # 상태별 필터링 분석 및 적용
    if 'error' not in validation_results['hitachi_stats'] and 'error' not in validation_results['simense_stats']:
        df_hitachi = pd.read_excel(hitachi_file)
        df_hitachi['Vendor'] = 'HITACHI'
        df_simense = pd.read_excel(simense_file)
        df_simense['Vendor'] = 'SIMENSE'
        df_combined = pd.concat([df_hitachi, df_simense], ignore_index=True)
        
        # 상태별 필터링 분석
        status_analysis = analyze_status_filtering(df_combined)
        
        # 상태별 필터링 적용
        df_filtered = apply_status_filtering(df_combined)
        
        # 필터링된 데이터 품질 검증
        filtered_validation = validate_filtered_data_quality(df_filtered)
        
        print(f"\n🎯 최종 결과:")
        print(f"  원본 데이터: {len(df_combined)}건")
        print(f"  필터링 후: {len(df_filtered)}건")
        print(f"  제거된 데이터: {len(df_combined) - len(df_filtered)}건")
        
        # 목표값 달성 여부 확인
        target_total = 6979
        actual_total = len(df_filtered)
        if abs(actual_total - target_total) <= 10:  # 10건 이내 오차 허용
            print(f"  ✅ 목표값 달성! (오차: {actual_total - target_total:+d}건)")
        else:
            print(f"  ⚠️ 목표값 미달성 (오차: {actual_total - target_total:+d}건)")
        
        # HITACHI 위치별 목표값 일치 검증
        validate_hitachi_location_targets(df_filtered) 

    # RAW DATA 자동 집계 결과 검증
    print("\n📊 [RAW DATA 자동 집계 결과]")
    df_hitachi = pd.read_excel("data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
    pivot = summarize_location_pivot(
        df_hitachi,
        value_col="Case No.",
        storage_col="Status_Storage",
        location_col="Status_Location",
        sublocation_col="Status_Location_DSV Indoor" if "Status_Location_DSV Indoor" in df_hitachi.columns else None
    )
    print(pivot) 

    # 피벗테이블 자동 집계 및 리포트
    print("\n📊 [엑셀 피벗테이블 구조 자동 집계 결과]")
    df_hitachi = pd.read_excel("data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
    value_col = "합계 : Pkg" if "합계 : Pkg" in df_hitachi.columns else "Case No."
    columns_col = "total handling" if "total handling" in df_hitachi.columns else None
    if columns_col:
        pivot = excel_style_pivot(
            df_hitachi,
            value_col=value_col,
            index_cols=[
                "Status_Storage",
                "Status_Location",
                "Status_Location_DSV Indoor",
                "Status_Location_DSV Al Markaz"
            ],
            columns_col=columns_col,
            aggfunc="sum" if value_col == "합계 : Pkg" else "count"
        )
        print(pivot)
        pivot.to_csv("output/hitachi_pivot_report.csv", encoding="utf-8-sig")
        print("[저장 완료] output/hitachi_pivot_report.csv")
    else:
        print("⚠️ 'total handling' 컬럼이 데이터에 없습니다. 열 필드 없이 피벗을 생성합니다.") 