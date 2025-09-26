#!/usr/bin/env python3
"""
HVDC DHL Warehouse 완전복구 데이터 분석 및 보고서 생성기
- 입력: HVDC_DHL_Warehouse_완전복구_20250704_125724.xlsx
- 출력: 종합 분석 보고서 (Excel + Markdown)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import traceback

class HVDCDHLWarehouseAnalyzer:
    def __init__(self, file_path):
        """초기화"""
        self.file_path = file_path
        self.df = None
        self.analysis_results = {}
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def load_data(self):
        """Excel 파일 로드 및 기본 정보 수집"""
        try:
            print(f"📊 데이터 로드 중: {os.path.basename(self.file_path)}")
            self.df = pd.read_excel(self.file_path)
            
            # 기본 정보 수집
            self.analysis_results['basic_info'] = {
                'file_name': os.path.basename(self.file_path),
                'total_records': len(self.df),
                'total_columns': len(self.df.columns),
                'file_size_mb': round(os.path.getsize(self.file_path) / (1024*1024), 2),
                'analysis_timestamp': self.timestamp
            }
            
            print(f"✅ 데이터 로드 완료: {len(self.df):,}건, {len(self.df.columns)}개 컬럼")
            print(f"📋 컬럼 목록: {list(self.df.columns)}")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
            return False
    
    def analyze_column_structure(self):
        """컬럼 구조 분석"""
        try:
            print("🔍 컬럼 구조 분석 중...")
            
            column_analysis = []
            for col in self.df.columns:
                col_info = {
                    'column_name': col,
                    'data_type': str(self.df[col].dtype),
                    'non_null_count': self.df[col].notna().sum(),
                    'null_count': self.df[col].isna().sum(),
                    'null_percentage': round(self.df[col].isna().sum() / len(self.df) * 100, 2),
                    'unique_values': self.df[col].nunique()
                }
                
                # 수치형 컬럼의 경우 추가 통계
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    col_info.update({
                        'min_value': self.df[col].min(),
                        'max_value': self.df[col].max(),
                        'mean_value': self.df[col].mean(),
                        'std_value': self.df[col].std()
                    })
                
                column_analysis.append(col_info)
            
            self.analysis_results['column_structure'] = column_analysis
            print(f"✅ 컬럼 구조 분석 완료: {len(column_analysis)}개 컬럼")
            
        except Exception as e:
            print(f"❌ 컬럼 구조 분석 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
    
    def analyze_warehouse_data(self):
        """창고 데이터 분석"""
        try:
            print("🏢 창고 데이터 분석 중...")
            
            # 창고 관련 컬럼 찾기
            warehouse_cols = [col for col in self.df.columns if any(keyword in str(col).upper() 
                           for keyword in ['WAREHOUSE', 'WH', 'DSV', 'AAA', 'HAULER', 'MOSB'])]
            
            print(f"🔍 발견된 창고 컬럼: {warehouse_cols}")
            
            warehouse_analysis = {}
            
            for col in warehouse_cols:
                if self.df[col].dtype == 'object':
                    # 날짜 컬럼인지 확인
                    try:
                        pd.to_datetime(self.df[col].dropna().iloc[0])
                        is_date = True
                    except:
                        is_date = False
                    
                    if not is_date:
                        value_counts = self.df[col].value_counts()
                        warehouse_analysis[col] = {
                            'type': 'categorical',
                            'unique_values': len(value_counts),
                            'top_values': value_counts.head(5).to_dict(),
                            'null_count': self.df[col].isna().sum()
                        }
                else:
                    # 수치형 컬럼
                    warehouse_analysis[col] = {
                        'type': 'numeric',
                        'min': self.df[col].min(),
                        'max': self.df[col].max(),
                        'mean': self.df[col].mean(),
                        'null_count': self.df[col].isna().sum()
                    }
            
            self.analysis_results['warehouse_analysis'] = warehouse_analysis
            print(f"✅ 창고 데이터 분석 완료: {len(warehouse_cols)}개 창고 컬럼")
            
        except Exception as e:
            print(f"❌ 창고 데이터 분석 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
    
    def analyze_site_data(self):
        """현장 데이터 분석"""
        try:
            print("🏗️ 현장 데이터 분석 중...")
            
            # 현장 관련 컬럼 찾기
            site_cols = [col for col in self.df.columns if any(keyword in str(col).upper() 
                       for keyword in ['AGI', 'DAS', 'MIR', 'SHU', 'SITE'])]
            
            print(f"🔍 발견된 현장 컬럼: {site_cols}")
            
            site_analysis = {}
            
            for col in site_cols:
                if self.df[col].dtype == 'object':
                    # 날짜 컬럼인지 확인
                    try:
                        pd.to_datetime(self.df[col].dropna().iloc[0])
                        is_date = True
                    except:
                        is_date = False
                    
                    if not is_date:
                        value_counts = self.df[col].value_counts()
                        site_analysis[col] = {
                            'type': 'categorical',
                            'unique_values': len(value_counts),
                            'top_values': value_counts.head(5).to_dict(),
                            'null_count': self.df[col].isna().sum()
                        }
                else:
                    # 수치형 컬럼
                    site_analysis[col] = {
                        'type': 'numeric',
                        'min': self.df[col].min(),
                        'max': self.df[col].max(),
                        'mean': self.df[col].mean(),
                        'null_count': self.df[col].isna().sum()
                    }
            
            self.analysis_results['site_analysis'] = site_analysis
            print(f"✅ 현장 데이터 분석 완료: {len(site_cols)}개 현장 컬럼")
            
        except Exception as e:
            print(f"❌ 현장 데이터 분석 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
    
    def analyze_date_patterns(self):
        """날짜 패턴 분석"""
        try:
            print("📅 날짜 패턴 분석 중...")
            
            # 날짜 컬럼 찾기
            date_cols = []
            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    try:
                        sample_data = self.df[col].dropna().head(10)
                        if len(sample_data) > 0:
                            pd.to_datetime(sample_data.iloc[0])
                            date_cols.append(col)
                    except:
                        continue
            
            print(f"🔍 발견된 날짜 컬럼: {date_cols}")
            
            date_analysis = {}
            
            for col in date_cols:
                try:
                    date_series = pd.to_datetime(self.df[col], errors='coerce')
                    valid_dates = date_series.dropna()
                    
                    if len(valid_dates) > 0:
                        date_analysis[col] = {
                            'total_records': len(self.df[col]),
                            'valid_dates': len(valid_dates),
                            'null_dates': len(self.df[col]) - len(valid_dates),
                            'date_range': {
                                'start': valid_dates.min().strftime('%Y-%m-%d'),
                                'end': valid_dates.max().strftime('%Y-%m-%d')
                            },
                            'monthly_distribution': valid_dates.dt.to_period('M').value_counts().sort_index().to_dict()
                        }
                except Exception as e:
                    date_analysis[col] = {'error': str(e)}
            
            self.analysis_results['date_analysis'] = date_analysis
            print(f"✅ 날짜 패턴 분석 완료: {len(date_cols)}개 날짜 컬럼")
            
        except Exception as e:
            print(f"❌ 날짜 패턴 분석 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
    
    def analyze_numeric_data(self):
        """수치형 데이터 분석"""
        try:
            print("📊 수치형 데이터 분석 중...")
            
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            print(f"🔍 발견된 수치형 컬럼: {numeric_cols}")
            
            numeric_analysis = {}
            
            for col in numeric_cols:
                numeric_analysis[col] = {
                    'count': self.df[col].count(),
                    'mean': self.df[col].mean(),
                    'std': self.df[col].std(),
                    'min': self.df[col].min(),
                    'max': self.df[col].max(),
                    'median': self.df[col].median(),
                    'null_count': self.df[col].isna().sum(),
                    'zero_count': (self.df[col] == 0).sum(),
                    'negative_count': (self.df[col] < 0).sum()
                }
            
            self.analysis_results['numeric_analysis'] = numeric_analysis
            print(f"✅ 수치형 데이터 분석 완료: {len(numeric_cols)}개 수치 컬럼")
            
        except Exception as e:
            print(f"❌ 수치형 데이터 분석 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
    
    def generate_summary_statistics(self):
        """요약 통계 생성"""
        try:
            print("📈 요약 통계 생성 중...")
            
            # 데이터 품질 지표
            total_cells = len(self.df) * len(self.df.columns)
            null_cells = self.df.isnull().sum().sum()
            data_quality = {
                'total_cells': total_cells,
                'null_cells': null_cells,
                'data_completeness': round((total_cells - null_cells) / total_cells * 100, 2),
                'duplicate_rows': self.df.duplicated().sum(),
                'unique_rows': len(self.df.drop_duplicates())
            }
            
            # 컬럼 타입별 분포
            column_types = {
                'numeric': len(self.df.select_dtypes(include=[np.number]).columns),
                'object': len(self.df.select_dtypes(include=['object']).columns),
                'datetime': len(self.df.select_dtypes(include=['datetime']).columns),
                'boolean': len(self.df.select_dtypes(include=['bool']).columns)
            }
            
            self.analysis_results['summary_statistics'] = {
                'data_quality': data_quality,
                'column_types': column_types
            }
            
            print("✅ 요약 통계 생성 완료")
            
        except Exception as e:
            print(f"❌ 요약 통계 생성 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
    
    def create_excel_report(self):
        """Excel 보고서 생성"""
        try:
            print("📋 Excel 보고서 생성 중...")
            
            output_file = f"HVDC_DHL_Warehouse_분석보고서_{self.timestamp}.xlsx"
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # 1. 원본 데이터
                self.df.to_excel(writer, sheet_name='원본_데이터', index=False)
                
                # 2. 기본 정보
                basic_info = pd.DataFrame([self.analysis_results['basic_info']])
                basic_info.to_excel(writer, sheet_name='기본_정보', index=False)
                
                # 3. 컬럼 구조
                column_df = pd.DataFrame(self.analysis_results['column_structure'])
                column_df.to_excel(writer, sheet_name='컬럼_구조', index=False)
                
                # 4. 창고 분석
                if 'warehouse_analysis' in self.analysis_results:
                    warehouse_df = pd.DataFrame(self.analysis_results['warehouse_analysis']).T
                    warehouse_df.to_excel(writer, sheet_name='창고_분석')
                
                # 5. 현장 분석
                if 'site_analysis' in self.analysis_results:
                    site_df = pd.DataFrame(self.analysis_results['site_analysis']).T
                    site_df.to_excel(writer, sheet_name='현장_분석')
                
                # 6. 날짜 분석
                if 'date_analysis' in self.analysis_results:
                    date_df = pd.DataFrame(self.analysis_results['date_analysis']).T
                    date_df.to_excel(writer, sheet_name='날짜_분석')
                
                # 7. 수치형 분석
                if 'numeric_analysis' in self.analysis_results:
                    numeric_df = pd.DataFrame(self.analysis_results['numeric_analysis']).T
                    numeric_df.to_excel(writer, sheet_name='수치형_분석')
                
                # 8. 요약 통계
                if 'summary_statistics' in self.analysis_results:
                    summary_df = pd.DataFrame(self.analysis_results['summary_statistics'])
                    summary_df.to_excel(writer, sheet_name='요약_통계')
            
            print(f"✅ Excel 보고서 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Excel 보고서 생성 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
            return None
    
    def create_markdown_report(self):
        """Markdown 보고서 생성"""
        try:
            print("📝 Markdown 보고서 생성 중...")
            
            output_file = f"HVDC_DHL_Warehouse_분석보고서_{self.timestamp}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# 🔌 HVDC DHL Warehouse 완전복구 데이터 분석 보고서\n\n")
                f.write(f"**분석일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}\n")
                f.write(f"**원본파일**: {self.analysis_results['basic_info']['file_name']}\n\n")
                
                # 기본 정보
                f.write("## 📋 기본 정보\n\n")
                basic_info = self.analysis_results['basic_info']
                f.write(f"- **총 레코드 수**: {basic_info['total_records']:,}건\n")
                f.write(f"- **총 컬럼 수**: {basic_info['total_columns']}개\n")
                f.write(f"- **파일 크기**: {basic_info['file_size_mb']}MB\n\n")
                
                # 데이터 품질
                if 'summary_statistics' in self.analysis_results:
                    f.write("## 📊 데이터 품질\n\n")
                    quality = self.analysis_results['summary_statistics']['data_quality']
                    f.write(f"- **데이터 완성도**: {quality['data_completeness']}%\n")
                    f.write(f"- **중복 행 수**: {quality['duplicate_rows']}건\n")
                    f.write(f"- **고유 행 수**: {quality['unique_rows']}건\n\n")
                
                # 컬럼 타입 분포
                if 'summary_statistics' in self.analysis_results:
                    f.write("## 🏗️ 컬럼 타입 분포\n\n")
                    types = self.analysis_results['summary_statistics']['column_types']
                    f.write(f"- **수치형**: {types['numeric']}개\n")
                    f.write(f"- **문자형**: {types['object']}개\n")
                    f.write(f"- **날짜형**: {types['datetime']}개\n")
                    f.write(f"- **불린형**: {types['boolean']}개\n\n")
                
                # 창고 분석
                if 'warehouse_analysis' in self.analysis_results:
                    f.write("## 🏢 창고 데이터 분석\n\n")
                    for col, info in self.analysis_results['warehouse_analysis'].items():
                        f.write(f"### {col}\n")
                        f.write(f"- **타입**: {info['type']}\n")
                        if info['type'] == 'categorical':
                            f.write(f"- **고유값 수**: {info['unique_values']}개\n")
                            f.write(f"- **상위값**: {list(info['top_values'].keys())[:3]}\n")
                        else:
                            f.write(f"- **평균**: {info['mean']:.2f}\n")
                            f.write(f"- **범위**: {info['min']:.2f} ~ {info['max']:.2f}\n")
                        f.write(f"- **결측값**: {info['null_count']}건\n\n")
                
                # 현장 분석
                if 'site_analysis' in self.analysis_results:
                    f.write("## 🏗️ 현장 데이터 분석\n\n")
                    for col, info in self.analysis_results['site_analysis'].items():
                        f.write(f"### {col}\n")
                        f.write(f"- **타입**: {info['type']}\n")
                        if info['type'] == 'categorical':
                            f.write(f"- **고유값 수**: {info['unique_values']}개\n")
                            f.write(f"- **상위값**: {list(info['top_values'].keys())[:3]}\n")
                        else:
                            f.write(f"- **평균**: {info['mean']:.2f}\n")
                            f.write(f"- **범위**: {info['min']:.2f} ~ {info['max']:.2f}\n")
                        f.write(f"- **결측값**: {info['null_count']}건\n\n")
                
                # 날짜 분석
                if 'date_analysis' in self.analysis_results:
                    f.write("## 📅 날짜 패턴 분석\n\n")
                    for col, info in self.analysis_results['date_analysis'].items():
                        if 'error' not in info:
                            f.write(f"### {col}\n")
                            f.write(f"- **유효 날짜**: {info['valid_dates']}건\n")
                            f.write(f"- **결측 날짜**: {info['null_dates']}건\n")
                            f.write(f"- **날짜 범위**: {info['date_range']['start']} ~ {info['date_range']['end']}\n\n")
                
                # 수치형 분석
                if 'numeric_analysis' in self.analysis_results:
                    f.write("## 📊 수치형 데이터 분석\n\n")
                    for col, info in self.analysis_results['numeric_analysis'].items():
                        f.write(f"### {col}\n")
                        f.write(f"- **평균**: {info['mean']:.2f}\n")
                        f.write(f"- **표준편차**: {info['std']:.2f}\n")
                        f.write(f"- **범위**: {info['min']:.2f} ~ {info['max']:.2f}\n")
                        f.write(f"- **중앙값**: {info['median']:.2f}\n")
                        f.write(f"- **결측값**: {info['null_count']}건\n")
                        f.write(f"- **0값**: {info['zero_count']}건\n")
                        f.write(f"- **음수**: {info['negative_count']}건\n\n")
                
                f.write("---\n\n")
                f.write("**보고서 생성 완료**\n")
                f.write(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}\n")
            
            print(f"✅ Markdown 보고서 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Markdown 보고서 생성 실패: {e}")
            print(f"상세 오류: {traceback.format_exc()}")
            return None
    
    def run_analysis(self):
        """전체 분석 실행"""
        print("🚀 HVDC DHL Warehouse 데이터 분석 시작")
        print("=" * 60)
        
        if not self.load_data():
            return False
        
        self.analyze_column_structure()
        self.analyze_warehouse_data()
        self.analyze_site_data()
        self.analyze_date_patterns()
        self.analyze_numeric_data()
        self.generate_summary_statistics()
        
        excel_file = self.create_excel_report()
        markdown_file = self.create_markdown_report()
        
        print("=" * 60)
        print("✅ 분석 완료!")
        if excel_file:
            print(f"📊 Excel 보고서: {excel_file}")
        if markdown_file:
            print(f"📝 Markdown 보고서: {markdown_file}")
        
        return True

def main():
    """메인 실행 함수"""
    file_path = "HVDC_DHL_Warehouse_완전복구_20250704_125724.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return
    
    analyzer = HVDCDHLWarehouseAnalyzer(file_path)
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 