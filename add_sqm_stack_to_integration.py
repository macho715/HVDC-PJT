#!/usr/bin/env python3
"""
화물이력관리_통합시스템에 SQM 스택 분석 추가
기존 analyze_stack_sqm.py 로직을 활용하여 통합시스템에 적용
"""

import pandas as pd
import numpy as np
from datetime import datetime
import traceback

def add_sqm_stack_analysis():
    """통합시스템에 SQM 스택 분석 추가"""
    
    print("🚀 화물이력관리 통합시스템에 SQM 스택 분석 추가")
    print("=" * 60)
    
    try:
        # 기존 통합시스템 파일 로드
        input_file = 'output/화물이력관리_통합시스템_20250703_175332.xlsx'
        print(f"📂 파일 로드: {input_file}")
        
        df = pd.read_excel(input_file)
        print(f"✅ 데이터 로드 완료: {len(df)}건")
        
        # SQM과 Stack_Status 컬럼 확인
        print(f"\n📊 기존 데이터 현황:")
        print(f"  SQM 컬럼 존재: {'SQM' in df.columns}")
        print(f"  Stack_Status 컬럼 존재: {'Stack_Status' in df.columns}")
        
        if 'SQM' in df.columns and 'Stack_Status' in df.columns:
            sqm_valid = len(df[df['SQM'].notna()])
            stack_valid = len(df[df['Stack_Status'].notna()])
            print(f"  SQM 유효 데이터: {sqm_valid}건")
            print(f"  Stack_Status 유효 데이터: {stack_valid}건")
        
        # 1. 실제 SQM 계산 (스택 적재 고려)
        print(f"\n🔄 1단계: 실제 SQM 계산")
        df = calculate_actual_sqm(df)
        
        # 2. 스택 효율성 분석
        print(f"\n🔄 2단계: 스택 효율성 분석")
        df = calculate_stack_efficiency(df)
        
        # 3. 면적 절약 분석
        print(f"\n🔄 3단계: 면적 절약 분석")
        df = calculate_area_savings(df)
        
        # 4. 스택 레벨별 요약
        print(f"\n🔄 4단계: 스택 레벨별 요약")
        df = create_stack_level_summary(df)
        
        # 5. 최적화 인사이트
        print(f"\n🔄 5단계: 최적화 인사이트")
        df = create_optimization_insights(df)
        
        # 6. 향상된 Excel 저장
        print(f"\n💾 6단계: 향상된 Excel 저장")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'output/화물이력관리_SQM스택분석_통합시스템_{timestamp}.xlsx'
        
        save_enhanced_excel(df, output_file)
        
        print("=" * 60)
        print("🎉 SQM 스택 분석 추가 완료!")
        print(f"📁 출력 파일: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 분석 추가 실패: {e}")
        traceback.print_exc()
        return None

def calculate_actual_sqm(df):
    """실제 면적 계산 (스택 적재 고려)"""
    
    print("  📐 실제 면적 계산 중...")
    
    # 유효한 SQM과 Stack_Status 데이터 확인
    valid_mask = (df['SQM'].notna()) & (df['Stack_Status'].notna())
    valid_count = valid_mask.sum()
    
    print(f"    유효한 데이터: {valid_count}건")
    
    # 실제 면적 계산: SQM / Stack_Status
    df['실제_SQM'] = np.where(
        valid_mask,
        df['SQM'] / np.maximum(df['Stack_Status'], 1),
        np.nan
    )
    
    # 통계 계산
    if valid_count > 0:
        total_original = df['SQM'].sum()
        total_actual = df['실제_SQM'].sum()
        savings = total_original - total_actual
        savings_rate = (savings / total_original) * 100
        
        print(f"    원본 면적: {total_original:,.1f}㎡")
        print(f"    실제 면적: {total_actual:,.1f}㎡")
        print(f"    절약 면적: {savings:,.1f}㎡ ({savings_rate:.1f}%)")
    
    print("  ✅ 실제 면적 계산 완료")
    return df

def calculate_stack_efficiency(df):
    """스택 효율성 분석"""
    
    print("  🏗️ 스택 효율성 분석 중...")
    
    # 스택 효율성 = 스택 레벨 (높을수록 효율적)
    df['스택_효율성'] = df['Stack_Status'].fillna(1)
    
    # 면적 절약률 계산
    df['면적_절약률'] = np.where(
        (df['SQM'].notna()) & (df['실제_SQM'].notna()) & (df['SQM'] > 0),
        ((df['SQM'] - df['실제_SQM']) / df['SQM']) * 100,
        0
    )
    
    # 스택 등급 계산
    def get_stack_grade(stack_level):
        if pd.isna(stack_level):
            return 'N/A'
        elif stack_level == 1:
            return 'Basic'
        elif stack_level == 2:
            return 'Good'
        elif stack_level == 3:
            return 'Excellent'
        elif stack_level >= 4:
            return 'Superior'
        else:
            return 'Unknown'
    
    df['스택_등급'] = df['Stack_Status'].apply(get_stack_grade)
    
    # 스택 분포 출력
    if 'Stack_Status' in df.columns:
        stack_dist = df['Stack_Status'].value_counts().sort_index()
        print(f"    스택 분포:")
        for stack, count in stack_dist.items():
            if pd.notna(stack):
                print(f"      {int(stack)}단: {count}건")
    
    print("  ✅ 스택 효율성 분석 완료")
    return df

def calculate_area_savings(df):
    """면적 절약 분석"""
    
    print("  💰 면적 절약 분석 중...")
    
    # 전체 면적 절약 계산
    if 'SQM' in df.columns and '실제_SQM' in df.columns:
        valid_data = df[(df['SQM'].notna()) & (df['실제_SQM'].notna())]
        
        if len(valid_data) > 0:
            total_original = valid_data['SQM'].sum()
            total_actual = valid_data['실제_SQM'].sum()
            total_savings = total_original - total_actual
            total_savings_rate = (total_savings / total_original) * 100
            
            # 전체 절약 정보를 모든 행에 추가
            df['총_면적_절약'] = total_savings
            df['절약_비율'] = total_savings_rate
            
            print(f"    총 면적 절약: {total_savings:,.1f}㎡ ({total_savings_rate:.1f}%)")
        else:
            df['총_면적_절약'] = 0
            df['절약_비율'] = 0
    
    print("  ✅ 면적 절약 분석 완료")
    return df

def create_stack_level_summary(df):
    """스택 레벨별 요약"""
    
    print("  📋 스택 레벨별 요약 생성 중...")
    
    # 스택 레벨별 집계
    if 'Stack_Status' in df.columns and 'SQM' in df.columns:
        try:
            stack_summary = df.groupby('Stack_Status').agg({
                'SQM': ['count', 'sum'],
                '실제_SQM': 'sum'
            }).round(2)
            
            # 각 행에 스택 레벨별 요약 정보 추가
            def create_summary_text(row):
                stack_level = row['Stack_Status']
                if pd.notna(stack_level):
                    try:
                        level_data = df[df['Stack_Status'] == stack_level]
                        count = len(level_data)
                        total_sqm = level_data['SQM'].sum()
                        actual_sqm = level_data['실제_SQM'].sum()
                        
                        return f"{int(stack_level)}단:{count}건,면적:{total_sqm:.1f}㎡,실제:{actual_sqm:.1f}㎡"
                    except:
                        return f"{int(stack_level)}단:요약불가"
                else:
                    return "N/A"
            
            df['스택_레벨_요약'] = df.apply(create_summary_text, axis=1)
            
            # 레벨별 상세 정보 추가
            df['레벨별_건수'] = df['Stack_Status'].map(
                df['Stack_Status'].value_counts().to_dict()
            ).fillna(0)
            
            if '실제_SQM' in df.columns:
                df['레벨별_면적'] = df.groupby('Stack_Status')['SQM'].transform('sum')
                df['레벨별_절약'] = df.groupby('Stack_Status')['실제_SQM'].transform('sum')
            
            print(f"    스택 레벨별 요약 생성 완료")
            
        except Exception as e:
            print(f"    ⚠️ 스택 요약 생성 중 오류: {e}")
            df['스택_레벨_요약'] = "요약불가"
            df['레벨별_건수'] = 0
            df['레벨별_면적'] = 0
            df['레벨별_절약'] = 0
    
    print("  ✅ 스택 레벨별 요약 완료")
    return df

def create_optimization_insights(df):
    """최적화 인사이트"""
    
    print("  🎯 최적화 인사이트 생성 중...")
    
    # 최적화 점수 계산 (0-100)
    def calculate_optimization_score(row):
        try:
            stack_level = row['Stack_Status']
            if pd.isna(stack_level):
                return 0
            
            # 기본 점수: 스택 레벨 * 20
            base_score = min(stack_level * 20, 80)
            
            # 추가 점수: 면적 효율성
            if row.get('면적_절약률', 0) > 50:
                base_score += 20
            elif row.get('면적_절약률', 0) > 25:
                base_score += 10
            
            return min(base_score, 100)
        except:
            return 0
    
    df['최적화_점수'] = df.apply(calculate_optimization_score, axis=1)
    
    # 개선 권장사항 생성
    def generate_recommendations(row):
        try:
            stack_level = row['Stack_Status']
            optimization_score = row['최적화_점수']
            
            if pd.isna(stack_level) or optimization_score == 0:
                return "데이터 불충분"
            elif optimization_score >= 80:
                return "우수한 스택 활용"
            elif optimization_score >= 60:
                return "스택 높이 증가 검토"
            elif optimization_score >= 40:
                return "스택 효율성 개선 필요"
            else:
                return "스택 구조 재설계 권장"
        except:
            return "분석 불가"
    
    df['개선_권장사항'] = df.apply(generate_recommendations, axis=1)
    
    # 비용 절감 잠재력 계산
    def calculate_cost_savings_potential(row):
        try:
            if pd.isna(row.get('SQM')) or pd.isna(row.get('실제_SQM')):
                return 0
                
            savings_sqm = row['SQM'] - row['실제_SQM']
            if savings_sqm <= 0:
                return 0
            
            # 가정: 창고 임대료 $10/㎡/월
            monthly_savings = savings_sqm * 10
            return monthly_savings * 12  # 연간 절감 잠재력
        except:
            return 0
    
    df['비용_절감_잠재력'] = df.apply(calculate_cost_savings_potential, axis=1)
    
    print("  ✅ 최적화 인사이트 생성 완료")
    return df

def save_enhanced_excel(df, output_file):
    """향상된 Excel 저장"""
    
    print(f"  💾 Excel 파일 저장 중: {output_file}")
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 메인 통합 데이터 시트 (SQM 분석 포함)
            df.to_excel(writer, sheet_name='화물이력관리_SQM분석_통합', index=False)
            
            # SQM 스택 분석 시트
            if 'Stack_Status' in df.columns and '실제_SQM' in df.columns:
                stack_analysis_df = create_stack_analysis_sheet(df)
                stack_analysis_df.to_excel(writer, sheet_name='SQM_스택분석', index=False)
            
            # 면적 절약 분석 시트
            if '총_면적_절약' in df.columns:
                savings_analysis_df = create_savings_analysis_sheet(df)
                savings_analysis_df.to_excel(writer, sheet_name='면적_절약_분석', index=False)
            
            # 창고 최적화 인사이트 시트
            if '최적화_점수' in df.columns:
                optimization_df = create_optimization_sheet(df)
                optimization_df.to_excel(writer, sheet_name='창고_최적화_인사이트', index=False)
            
            # 스택 효율성 리포트 시트
            if 'VENDOR' in df.columns and '스택_효율성' in df.columns:
                efficiency_report_df = create_efficiency_report_sheet(df)
                efficiency_report_df.to_excel(writer, sheet_name='스택_효율성_리포트', index=False)
        
        print(f"  ✅ Excel 파일 저장 완료")
        
        # 통계 요약 출력
        print(f"\n📊 최종 분석 결과:")
        if 'SQM' in df.columns and '실제_SQM' in df.columns:
            valid_data = df[(df['SQM'].notna()) & (df['실제_SQM'].notna())]
            if len(valid_data) > 0:
                total_original = valid_data['SQM'].sum()
                total_actual = valid_data['실제_SQM'].sum()
                savings = total_original - total_actual
                savings_rate = (savings / total_original) * 100
                
                print(f"  • 분석 대상: {len(valid_data):,}건")
                print(f"  • 원본 총 면적: {total_original:,.1f}㎡")
                print(f"  • 실제 총 면적: {total_actual:,.1f}㎡")
                print(f"  • 면적 절약: {savings:,.1f}㎡ ({savings_rate:.1f}%)")
                
                if '비용_절감_잠재력' in df.columns:
                    total_cost_savings = df['비용_절감_잠재력'].sum()
                    print(f"  • 연간 비용 절감 잠재력: ${total_cost_savings:,.0f}")
        
    except Exception as e:
        print(f"  ❌ Excel 저장 실패: {e}")
        traceback.print_exc()

def create_stack_analysis_sheet(df):
    """스택 분석 시트 생성"""
    try:
        stack_summary = df.groupby('Stack_Status').agg({
            'SQM': ['count', 'sum', 'mean'],
            '실제_SQM': ['sum', 'mean'],
            '면적_절약률': 'mean',
            '최적화_점수': 'mean'
        }).round(2)
        
        stack_summary.columns = ['건수', '총_면적', '평균_면적', '실제_총_면적', '실제_평균_면적', '평균_절약률', '평균_최적화_점수']
        stack_summary.reset_index(inplace=True)
        
        stack_summary['스택_등급'] = stack_summary['Stack_Status'].apply(
            lambda x: 'Basic' if x == 1 else 'Good' if x == 2 else 'Excellent' if x == 3 else 'Superior'
        )
        
        return stack_summary
    except:
        return pd.DataFrame()

def create_savings_analysis_sheet(df):
    """면적 절약 분석 시트 생성"""
    try:
        savings_data = []
        
        for stack_level in sorted(df['Stack_Status'].dropna().unique()):
            stack_data = df[df['Stack_Status'] == stack_level]
            
            original_total = stack_data['SQM'].sum()
            actual_total = stack_data['실제_SQM'].sum()
            savings = original_total - actual_total
            savings_rate = (savings / original_total) * 100 if original_total > 0 else 0
            
            savings_data.append({
                '스택_레벨': int(stack_level),
                '건수': len(stack_data),
                '원본_면적': original_total,
                '실제_면적': actual_total,
                '절약_면적': savings,
                '절약_비율': savings_rate,
                '월간_비용절감': savings * 10,
                '연간_비용절감': savings * 10 * 12
            })
        
        return pd.DataFrame(savings_data)
    except:
        return pd.DataFrame()

def create_optimization_sheet(df):
    """최적화 시트 생성"""
    try:
        optimization_summary = df.groupby('스택_등급').agg({
            '최적화_점수': ['count', 'mean'],
            '비용_절감_잠재력': 'sum',
            '면적_절약률': 'mean'
        }).round(2)
        
        optimization_summary.columns = ['건수', '평균_최적화_점수', '총_비용절감잠재력', '평균_면적절약률']
        optimization_summary.reset_index(inplace=True)
        
        return optimization_summary
    except:
        return pd.DataFrame()

def create_efficiency_report_sheet(df):
    """효율성 리포트 시트 생성"""
    try:
        vendor_efficiency = df.groupby('VENDOR').agg({
            '스택_효율성': 'mean',
            '면적_절약률': 'mean',
            '최적화_점수': 'mean',
            '비용_절감_잠재력': 'sum'
        }).round(2)
        
        vendor_efficiency.reset_index(inplace=True)
        return vendor_efficiency
    except:
        return pd.DataFrame()

if __name__ == "__main__":
    result = add_sqm_stack_analysis()
    if result:
        print(f"\n🎯 성공! 출력 파일: {result}")
    else:
        print(f"\n❌ 실패!") 