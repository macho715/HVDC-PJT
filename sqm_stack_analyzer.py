#!/usr/bin/env python3
"""
TDD GREEN 단계: 스택 적재 기반 SQM 분석 기능 구현
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import traceback

class SqmStackAnalyzer:
    """스택 적재 기반 SQM 분석기"""
    
    def __init__(self, integration_file):
        self.integration_file = integration_file
        self.df = None
        self.analysis_results = {}
        
    def load_data(self):
        """데이터 로드"""
        try:
            self.df = pd.read_excel(self.integration_file)
            print(f"✅ 데이터 로드 완료: {len(self.df)}건")
            return True
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def calculate_actual_sqm(self):
        """실제 면적 계산 (스택 적재 고려)"""
        try:
            print("🔄 실제 면적 계산 중...")
            
            # 유효한 SQM과 Stack_Status 데이터 확인
            valid_mask = (self.df['SQM'].notna()) & (self.df['Stack_Status'].notna())
            
            # 실제 면적 계산: SQM / Stack_Status
            self.df['실제_SQM'] = np.where(
                valid_mask,
                self.df['SQM'] / np.maximum(self.df['Stack_Status'], 1),
                np.nan
            )
            
            # 통계 계산
            total_original = self.df['SQM'].sum()
            total_actual = self.df['실제_SQM'].sum()
            savings = total_original - total_actual
            savings_rate = (savings / total_original) * 100
            
            self.analysis_results['area_savings'] = {
                'total_original': total_original,
                'total_actual': total_actual,
                'savings': savings,
                'savings_rate': savings_rate
            }
            
            print(f"✅ 실제 면적 계산 완료")
            print(f"   원본 면적: {total_original:,.1f}㎡")
            print(f"   실제 면적: {total_actual:,.1f}㎡")
            print(f"   절약 면적: {savings:,.1f}㎡ ({savings_rate:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ 실제 면적 계산 실패: {e}")
            traceback.print_exc()
            return False
    
    def calculate_stack_efficiency(self):
        """스택 효율성 분석"""
        try:
            print("🔄 스택 효율성 분석 중...")
            
            # 스택 효율성 = 스택 레벨 (높을수록 효율적)
            self.df['스택_효율성'] = self.df['Stack_Status'].fillna(1)
            
            # 면적 절약률 계산
            self.df['면적_절약률'] = np.where(
                self.df['Stack_Status'].notna(),
                ((self.df['SQM'] - self.df['실제_SQM']) / self.df['SQM']) * 100,
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
            
            self.df['스택_등급'] = self.df['Stack_Status'].apply(get_stack_grade)
            
            print(f"✅ 스택 효율성 분석 완료")
            
            return True
            
        except Exception as e:
            print(f"❌ 스택 효율성 분석 실패: {e}")
            traceback.print_exc()
            return False
    
    def calculate_area_savings_details(self):
        """면적 절약 상세 계산"""
        try:
            print("🔄 면적 절약 상세 계산 중...")
            
            # 전체 면적 절약 정보를 모든 행에 추가
            savings_info = self.analysis_results.get('area_savings', {})
            
            self.df['총_면적_절약'] = savings_info.get('savings', 0)
            self.df['절약_비율'] = savings_info.get('savings_rate', 0)
            
            print(f"✅ 면적 절약 상세 계산 완료")
            
            return True
            
        except Exception as e:
            print(f"❌ 면적 절약 상세 계산 실패: {e}")
            traceback.print_exc()
            return False
    
    def create_stack_level_summary(self):
        """스택 레벨별 요약"""
        try:
            print("🔄 스택 레벨별 요약 생성 중...")
            
            # 스택 레벨별 집계
            stack_summary = self.df.groupby('Stack_Status').agg({
                'SQM': ['count', 'sum', 'mean'],
                '실제_SQM': ['sum', 'mean']
            }).round(2)
            
            # 스택 레벨별 요약 정보를 각 행에 추가
            for _, row in self.df.iterrows():
                stack_level = row['Stack_Status']
                if pd.notna(stack_level):
                    try:
                        count = stack_summary.loc[stack_level, ('SQM', 'count')]
                        total_area = stack_summary.loc[stack_level, ('SQM', 'sum')]
                        actual_area = stack_summary.loc[stack_level, ('실제_SQM', 'sum')]
                        
                        summary_text = f"{int(stack_level)}단:{count}건,면적:{total_area:.1f}㎡,실제:{actual_area:.1f}㎡"
                    except:
                        summary_text = f"{int(stack_level)}단:요약불가"
                else:
                    summary_text = "N/A"
                
                self.df.loc[row.name, '스택_레벨_요약'] = summary_text
            
            # 레벨별 상세 정보 추가
            self.df['레벨별_건수'] = self.df['Stack_Status'].map(
                self.df['Stack_Status'].value_counts().to_dict()
            ).fillna(0)
            
            self.df['레벨별_면적'] = self.df.groupby('Stack_Status')['SQM'].transform('sum')
            self.df['레벨별_절약'] = self.df.groupby('Stack_Status')['실제_SQM'].transform('sum')
            
            print(f"✅ 스택 레벨별 요약 생성 완료")
            
            return True
            
        except Exception as e:
            print(f"❌ 스택 레벨별 요약 생성 실패: {e}")
            traceback.print_exc()
            return False
    
    def create_optimization_insights(self):
        """창고 최적화 인사이트"""
        try:
            print("🔄 창고 최적화 인사이트 생성 중...")
            
            # 최적화 점수 계산 (0-100)
            def calculate_optimization_score(row):
                try:
                    stack_level = row['Stack_Status']
                    if pd.isna(stack_level):
                        return 0
                    
                    # 기본 점수: 스택 레벨 * 20
                    base_score = min(stack_level * 20, 80)
                    
                    # 추가 점수: 면적 효율성
                    if row['면적_절약률'] > 50:
                        base_score += 20
                    elif row['면적_절약률'] > 25:
                        base_score += 10
                    
                    return min(base_score, 100)
                except:
                    return 0
            
            self.df['최적화_점수'] = self.df.apply(calculate_optimization_score, axis=1)
            
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
            
            self.df['개선_권장사항'] = self.df.apply(generate_recommendations, axis=1)
            
            # 비용 절감 잠재력 계산
            def calculate_cost_savings_potential(row):
                try:
                    savings_sqm = row['SQM'] - row['실제_SQM']
                    if pd.isna(savings_sqm) or savings_sqm <= 0:
                        return 0
                    
                    # 가정: 창고 임대료 $10/㎡/월
                    monthly_savings = savings_sqm * 10
                    return monthly_savings * 12  # 연간 절감 잠재력
                except:
                    return 0
            
            self.df['비용_절감_잠재력'] = self.df.apply(calculate_cost_savings_potential, axis=1)
            
            print(f"✅ 창고 최적화 인사이트 생성 완료")
            
            return True
            
        except Exception as e:
            print(f"❌ 창고 최적화 인사이트 생성 실패: {e}")
            traceback.print_exc()
            return False
    
    def save_enhanced_excel(self):
        """SQM 분석 포함 향상된 Excel 저장"""
        try:
            print("🔄 SQM 분석 포함 향상된 Excel 저장 중...")
            
            timestamp = datetime.now().strftime("%Y%m%d")
            enhanced_file = f'output/화물이력관리_SQM분석_통합시스템_{timestamp}.xlsx'
            
            with pd.ExcelWriter(enhanced_file, engine='openpyxl') as writer:
                # 메인 통합 데이터 시트
                self.df.to_excel(writer, sheet_name='화물이력관리_통합데이터', index=False)
                
                # SQM 스택 분석 시트
                stack_analysis_df = self.create_stack_analysis_sheet()
                stack_analysis_df.to_excel(writer, sheet_name='SQM_스택분석', index=False)
                
                # 면적 절약 분석 시트
                savings_analysis_df = self.create_savings_analysis_sheet()
                savings_analysis_df.to_excel(writer, sheet_name='면적_절약_분석', index=False)
                
                # 창고 최적화 인사이트 시트
                optimization_df = self.create_optimization_sheet()
                optimization_df.to_excel(writer, sheet_name='창고_최적화_인사이트', index=False)
                
                # 스택 효율성 리포트 시트
                efficiency_report_df = self.create_efficiency_report_sheet()
                efficiency_report_df.to_excel(writer, sheet_name='스택_효율성_리포트', index=False)
            
            print(f"✅ SQM 분석 포함 향상된 Excel 저장 완료")
            print(f"📁 파일 위치: {enhanced_file}")
            
            return enhanced_file
            
        except Exception as e:
            print(f"❌ 향상된 Excel 저장 실패: {e}")
            traceback.print_exc()
            return None
    
    def create_stack_analysis_sheet(self):
        """스택 분석 시트 생성"""
        try:
            # 스택 레벨별 요약
            stack_summary = self.df.groupby('Stack_Status').agg({
                'SQM': ['count', 'sum', 'mean'],
                '실제_SQM': ['sum', 'mean'],
                '면적_절약률': 'mean',
                '최적화_점수': 'mean'
            }).round(2)
            
            # 컬럼명 정리
            stack_summary.columns = ['건수', '총_면적', '평균_면적', '실제_총_면적', '실제_평균_면적', '평균_절약률', '평균_최적화_점수']
            stack_summary.reset_index(inplace=True)
            
            # 추가 분석 정보
            stack_summary['스택_등급'] = stack_summary['Stack_Status'].apply(
                lambda x: 'Basic' if x == 1 else 'Good' if x == 2 else 'Excellent' if x == 3 else 'Superior'
            )
            
            return stack_summary
            
        except Exception as e:
            print(f"❌ 스택 분석 시트 생성 실패: {e}")
            return pd.DataFrame()
    
    def create_savings_analysis_sheet(self):
        """면적 절약 분석 시트 생성"""
        try:
            savings_data = []
            
            for stack_level in sorted(self.df['Stack_Status'].dropna().unique()):
                stack_data = self.df[self.df['Stack_Status'] == stack_level]
                
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
                    '월간_비용절감': savings * 10,  # $10/㎡/월 가정
                    '연간_비용절감': savings * 10 * 12
                })
            
            return pd.DataFrame(savings_data)
            
        except Exception as e:
            print(f"❌ 면적 절약 분석 시트 생성 실패: {e}")
            return pd.DataFrame()
    
    def create_optimization_sheet(self):
        """최적화 시트 생성"""
        try:
            # 최적화 점수별 분포
            optimization_summary = self.df.groupby('스택_등급').agg({
                '최적화_점수': ['count', 'mean'],
                '비용_절감_잠재력': 'sum',
                '면적_절약률': 'mean'
            }).round(2)
            
            optimization_summary.columns = ['건수', '평균_최적화_점수', '총_비용절감잠재력', '평균_면적절약률']
            optimization_summary.reset_index(inplace=True)
            
            return optimization_summary
            
        except Exception as e:
            print(f"❌ 최적화 시트 생성 실패: {e}")
            return pd.DataFrame()
    
    def create_efficiency_report_sheet(self):
        """효율성 리포트 시트 생성"""
        try:
            # 벤더별 효율성 분석
            vendor_efficiency = self.df.groupby('VENDOR').agg({
                '스택_효율성': 'mean',
                '면적_절약률': 'mean',
                '최적화_점수': 'mean',
                '비용_절감_잠재력': 'sum'
            }).round(2)
            
            vendor_efficiency.reset_index(inplace=True)
            
            return vendor_efficiency
            
        except Exception as e:
            print(f"❌ 효율성 리포트 시트 생성 실패: {e}")
            return pd.DataFrame()
    
    def run_complete_analysis(self):
        """전체 분석 실행"""
        try:
            print("🚀 SQM 스택 분석 시작")
            print("=" * 50)
            
            # 1. 데이터 로드
            if not self.load_data():
                return False
            
            # 2. 실제 면적 계산
            if not self.calculate_actual_sqm():
                return False
            
            # 3. 스택 효율성 분석
            if not self.calculate_stack_efficiency():
                return False
            
            # 4. 면적 절약 상세 계산
            if not self.calculate_area_savings_details():
                return False
            
            # 5. 스택 레벨별 요약
            if not self.create_stack_level_summary():
                return False
            
            # 6. 최적화 인사이트
            if not self.create_optimization_insights():
                return False
            
            # 7. 향상된 Excel 저장
            enhanced_file = self.save_enhanced_excel()
            if not enhanced_file:
                return False
            
            # 8. 원본 파일 업데이트
            self.df.to_excel(self.integration_file, index=False)
            
            print("=" * 50)
            print("🎉 SQM 스택 분석 완료!")
            print(f"📁 향상된 파일: {enhanced_file}")
            print(f"📊 분석 결과:")
            
            savings_info = self.analysis_results.get('area_savings', {})
            print(f"   • 총 면적 절약: {savings_info.get('savings', 0):,.1f}㎡")
            print(f"   • 절약 비율: {savings_info.get('savings_rate', 0):.1f}%")
            print(f"   • 분석 레코드: {len(self.df[self.df['실제_SQM'].notna()]):,}건")
            
            return True
            
        except Exception as e:
            print(f"❌ 전체 분석 실패: {e}")
            traceback.print_exc()
            return False

def main():
    """메인 실행 함수"""
    try:
        # 분석기 초기화
        analyzer = SqmStackAnalyzer('output/화물이력관리_통합시스템_20250703_175306.xlsx')
        
        # 전체 분석 실행
        success = analyzer.run_complete_analysis()
        
        if success:
            print("\n🎯 다음 단계: 테스트 실행으로 GREEN 단계 확인")
            print("python test_sqm_stack_analysis.py")
        else:
            print("\n❌ 분석 실패. 로그를 확인하세요.")
            
    except Exception as e:
        print(f"❌ 메인 실행 오류: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 