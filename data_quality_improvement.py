#!/usr/bin/env python3
"""
HVDC 데이터 품질 개선 솔루션 v1.0
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini

주요 개선 사항:
1. 전각 공백 문자 '　' (유니코드 \u3000) 처리
2. 날짜 형식 표준화 및 검증
3. 창고 컬럼 데이터 정제
4. 개선된 입고 로직 적용
5. 개선 전후 비교 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class HVDCDataQualityImprover:
    """HVDC 데이터 품질 개선기"""
    
    def __init__(self):
        """초기화"""
        print("🔧 HVDC 데이터 품질 개선 솔루션 v1.0")
        print("=" * 80)
        
        # 데이터 파일 경로
        self.data_path = Path("data")
        self.hitachi_file = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.simense_file = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        
        # 창고 컬럼
        self.warehouse_columns = [
            'DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'AAA  Storage',
            'DHL Warehouse', 'MOSB', 'Hauler Indoor'
        ]
        
        # 데이터 저장
        self.original_data = None
        self.cleaned_data = None
        self.total_records = 0
        
        # 개선 통계
        self.improvement_stats = {}
        
        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_original_data(self):
        """원본 데이터 로드"""
        print("\n📂 원본 HVDC 데이터 로드 중...")
        
        combined_dfs = []
        
        try:
            # HITACHI 데이터 로드
            if self.hitachi_file.exists():
                print(f"📊 HITACHI 데이터 로드: {self.hitachi_file}")
                hitachi_data = pd.read_excel(self.hitachi_file, engine='openpyxl')
                hitachi_data['Data_Source'] = 'HITACHI'
                combined_dfs.append(hitachi_data)
                print(f"✅ HITACHI 로드 완료: {len(hitachi_data):,}건")
            
            # SIMENSE 데이터 로드
            if self.simense_file.exists():
                print(f"📊 SIMENSE 데이터 로드: {self.simense_file}")
                simense_data = pd.read_excel(self.simense_file, engine='openpyxl')
                simense_data['Data_Source'] = 'SIMENSE'
                combined_dfs.append(simense_data)
                print(f"✅ SIMENSE 로드 완료: {len(simense_data):,}건")
            
            # 데이터 결합
            if combined_dfs:
                self.original_data = pd.concat(combined_dfs, ignore_index=True, sort=False)
                self.total_records = len(self.original_data)
                print(f"🔗 데이터 결합 완료: {self.total_records:,}건")
                return True
            else:
                print("❌ 로드할 데이터가 없습니다.")
                return False
                
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def analyze_original_quality(self):
        """원본 데이터 품질 분석"""
        print("\n🔍 원본 데이터 품질 분석 중...")
        print("-" * 60)
        
        original_stats = {}
        total_entries = 0
        total_date_entries = 0
        total_fullwidth_spaces = 0
        
        for warehouse in self.warehouse_columns:
            if warehouse not in self.original_data.columns:
                continue
            
            # 전체 non-null 엔트리
            non_null_count = self.original_data[warehouse].notna().sum()
            total_entries += non_null_count
            
            # 전각 공백 문자 개수
            fullwidth_space_count = 0
            date_count = 0
            other_non_date_count = 0
            
            if non_null_count > 0:
                non_null_data = self.original_data[warehouse].dropna()
                
                for value in non_null_data:
                    str_value = str(value).strip()
                    
                    # 전각 공백 문자 확인
                    if str_value == '　' or str_value == '\u3000':
                        fullwidth_space_count += 1
                        total_fullwidth_spaces += 1
                    else:
                        try:
                            pd.to_datetime(value)
                            date_count += 1
                            total_date_entries += 1
                        except:
                            other_non_date_count += 1
            
            original_stats[warehouse] = {
                'total_entries': non_null_count,
                'date_entries': date_count,
                'fullwidth_spaces': fullwidth_space_count,
                'other_non_date': other_non_date_count,
                'date_accuracy': (date_count / non_null_count * 100) if non_null_count > 0 else 0
            }
            
            print(f"📋 {warehouse}:")
            print(f"   전체 엔트리: {non_null_count:,}건")
            print(f"   날짜 형식: {date_count:,}건 ({date_count/non_null_count*100:.1f}%)")
            print(f"   전각 공백: {fullwidth_space_count:,}건 ({fullwidth_space_count/non_null_count*100:.1f}%)")
            print(f"   기타 비날짜: {other_non_date_count:,}건")
        
        # 전체 통계
        overall_accuracy = (total_date_entries / total_entries * 100) if total_entries > 0 else 0
        
        print(f"\n📊 원본 데이터 전체 통계:")
        print(f"   총 창고 엔트리: {total_entries:,}건")
        print(f"   날짜 형식 엔트리: {total_date_entries:,}건")
        print(f"   전각 공백 문자: {total_fullwidth_spaces:,}건")
        print(f"   원본 정확도: {overall_accuracy:.1f}%")
        
        self.improvement_stats['original'] = {
            'total_entries': total_entries,
            'date_entries': total_date_entries,
            'fullwidth_spaces': total_fullwidth_spaces,
            'accuracy': overall_accuracy,
            'warehouse_stats': original_stats
        }
        
        return original_stats
    
    def clean_warehouse_data(self):
        """창고 데이터 정제"""
        print("\n🧹 창고 데이터 정제 중...")
        print("-" * 60)
        
        # 원본 데이터 복사
        self.cleaned_data = self.original_data.copy()
        
        cleaned_stats = {}
        total_cleaned_entries = 0
        total_cleaned_date_entries = 0
        
        for warehouse in self.warehouse_columns:
            if warehouse not in self.cleaned_data.columns:
                continue
            
            print(f"🔧 {warehouse} 정제 중...")
            
            # 정제 전 통계
            original_non_null = self.cleaned_data[warehouse].notna().sum()
            
            # 1단계: 전각 공백 문자를 NaN으로 변환
            fullwidth_space_mask = (
                self.cleaned_data[warehouse].astype(str).str.strip() == '　'
            ) | (
                self.cleaned_data[warehouse].astype(str).str.strip() == '\u3000'
            )
            
            fullwidth_spaces_found = fullwidth_space_mask.sum()
            self.cleaned_data.loc[fullwidth_space_mask, warehouse] = np.nan
            
            # 2단계: 날짜 형식 표준화
            def standardize_date(value):
                if pd.isna(value):
                    return np.nan
                
                try:
                    # 날짜 변환 시도
                    standardized_date = pd.to_datetime(value)
                    return standardized_date
                except:
                    # 날짜 변환 실패시 NaN으로 변환 (데이터 품질 개선)
                    return np.nan
            
            # 날짜 표준화 적용
            original_values = self.cleaned_data[warehouse].copy()
            self.cleaned_data[warehouse] = self.cleaned_data[warehouse].apply(standardize_date)
            
            # 정제 후 통계
            cleaned_non_null = self.cleaned_data[warehouse].notna().sum()
            cleaned_date_count = cleaned_non_null  # 정제 후에는 모든 non-null이 날짜
            
            total_cleaned_entries += cleaned_non_null
            total_cleaned_date_entries += cleaned_date_count
            
            # 정제 효과 계산
            removed_fullwidth = fullwidth_spaces_found
            removed_non_date = original_non_null - cleaned_non_null - removed_fullwidth
            
            cleaned_stats[warehouse] = {
                'original_entries': original_non_null,
                'cleaned_entries': cleaned_non_null,
                'removed_fullwidth': removed_fullwidth,
                'removed_non_date': removed_non_date,
                'improvement': ((cleaned_date_count / cleaned_non_null * 100) if cleaned_non_null > 0 else 100) - (
                    self.improvement_stats['original']['warehouse_stats'][warehouse]['date_accuracy']
                ) if warehouse in self.improvement_stats['original']['warehouse_stats'] else 0
            }
            
            print(f"   원본 엔트리: {original_non_null:,}건")
            print(f"   정제 후 엔트리: {cleaned_non_null:,}건")
            print(f"   제거된 전각 공백: {removed_fullwidth:,}건")
            print(f"   제거된 비날짜 데이터: {removed_non_date:,}건")
            print(f"   정제 후 날짜 정확도: 100.0%")
        
        # 전체 정제 결과
        cleaned_accuracy = 100.0  # 정제 후에는 모든 데이터가 날짜 형식
        
        print(f"\n✅ 데이터 정제 완료:")
        print(f"   정제 후 총 엔트리: {total_cleaned_entries:,}건")
        print(f"   정제 후 날짜 엔트리: {total_cleaned_date_entries:,}건")
        print(f"   정제 후 정확도: {cleaned_accuracy:.1f}%")
        
        self.improvement_stats['cleaned'] = {
            'total_entries': total_cleaned_entries,
            'date_entries': total_cleaned_date_entries,
            'accuracy': cleaned_accuracy,
            'warehouse_stats': cleaned_stats
        }
        
        return cleaned_stats
    
    def apply_improved_inbound_logic(self):
        """개선된 입고 로직 적용"""
        print("\n🎯 개선된 입고 로직 적용 중...")
        print("-" * 60)
        
        # Final_Location 계산 (기존 Status_Location 활용)
        if 'Status_Location' in self.cleaned_data.columns:
            print("✅ 기존 Status_Location 활용")
        else:
            print("🔧 Status_Location 계산 중...")
            # Status_Location이 없으면 생성 (가장 최근 날짜 창고 사용)
            status_locations = []
            for _, row in self.cleaned_data.iterrows():
                latest_date = None
                latest_warehouse = None
                
                for warehouse in self.warehouse_columns:
                    if pd.notna(row[warehouse]):
                        try:
                            warehouse_date = pd.to_datetime(row[warehouse])
                            if latest_date is None or warehouse_date > latest_date:
                                latest_date = warehouse_date
                                latest_warehouse = warehouse
                        except:
                            continue
                
                status_locations.append(latest_warehouse if latest_warehouse else 'Unknown')
            
            self.cleaned_data['Status_Location'] = status_locations
        
        # Final_Location 파생 (보고서 기준)
        conditions = []
        choices = []
        
        # DSV Al Markaz 우선 선택
        if 'DSV Al Markaz' in self.cleaned_data.columns:
            conditions.append(self.cleaned_data['DSV Al Markaz'].notna())
            choices.append('DSV Al Markaz')
        
        # DSV Indoor 차순위
        if 'DSV Indoor' in self.cleaned_data.columns:
            dsv_indoor_condition = (
                (~conditions[0] if conditions else True) &
                self.cleaned_data['DSV Indoor'].notna()
            )
            conditions.append(dsv_indoor_condition)
            choices.append('DSV Indoor')
        
        # Final_Location 계산
        if conditions and choices:
            self.cleaned_data['Final_Location_Improved'] = np.select(
                conditions, 
                choices, 
                default=self.cleaned_data['Status_Location']
            )
        else:
            self.cleaned_data['Final_Location_Improved'] = self.cleaned_data['Status_Location']
        
        # 개선된 입고 로직 적용
        improved_inbound_items = []
        
        for _, row in self.cleaned_data.iterrows():
            for warehouse in self.warehouse_columns:
                if pd.notna(row[warehouse]):
                    warehouse_date = pd.to_datetime(row[warehouse])
                    improved_inbound_items.append({
                        'item': row.name,
                        'warehouse': warehouse,
                        'date': warehouse_date,
                        'month': warehouse_date.to_period('M'),
                        'final_location': row['Final_Location_Improved']
                    })
        
        improved_inbound_df = pd.DataFrame(improved_inbound_items)
        
        print(f"🎯 개선된 입고 로직 결과:")
        print(f"   총 입고 건수: {len(improved_inbound_df):,}건")
        
        if len(improved_inbound_df) > 0:
            by_warehouse = improved_inbound_df.groupby('warehouse').size().to_dict()
            by_final_location = improved_inbound_df.groupby('final_location').size().to_dict()
            
            print(f"   창고별 입고 건수:")
            for warehouse, count in sorted(by_warehouse.items(), key=lambda x: x[1], reverse=True):
                print(f"     {warehouse}: {count:,}건")
            
            print(f"   Final_Location별 입고 건수 (상위 5개):")
            for location, count in sorted(by_final_location.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     {location}: {count:,}건")
        
        self.improvement_stats['improved_inbound'] = {
            'total_inbound': len(improved_inbound_df),
            'by_warehouse': by_warehouse if len(improved_inbound_df) > 0 else {},
            'by_final_location': by_final_location if len(improved_inbound_df) > 0 else {}
        }
        
        return improved_inbound_df
    
    def create_improved_monthly_pivot(self, improved_inbound_df):
        """개선된 월별 피벗 테이블 생성"""
        print("\n📊 개선된 월별 피벗 테이블 생성 중...")
        
        if len(improved_inbound_df) == 0:
            print("⚠️ 입고 데이터가 없어 피벗 테이블을 생성할 수 없습니다.")
            return pd.DataFrame()
        
        try:
            # Final_Location 기준 월별 피벗 테이블
            monthly_pivot = improved_inbound_df.pivot_table(
                values='item',
                index='month',
                columns='final_location',
                aggfunc='count',
                fill_value=0
            )
            
            print(f"✅ 개선된 월별 피벗 테이블 생성 완료:")
            print(f"   피벗 테이블 크기: {monthly_pivot.shape}")
            print(f"   월별 기간: {monthly_pivot.index.min()} ~ {monthly_pivot.index.max()}")
            print(f"   Final_Location 수: {len(monthly_pivot.columns)}")
            
            return monthly_pivot
            
        except Exception as e:
            print(f"❌ 피벗 테이블 생성 실패: {e}")
            return pd.DataFrame()
    
    def generate_improvement_report(self):
        """개선 전후 비교 리포트 생성"""
        print("\n📋 데이터 품질 개선 전후 비교 리포트")
        print("=" * 80)
        
        # 전체 개선 효과
        original_accuracy = self.improvement_stats['original']['accuracy']
        cleaned_accuracy = self.improvement_stats['cleaned']['accuracy']
        improvement_percentage = cleaned_accuracy - original_accuracy
        
        print(f"🎯 전체 개선 효과:")
        print(f"   개선 전 정확도: {original_accuracy:.1f}%")
        print(f"   개선 후 정확도: {cleaned_accuracy:.1f}%")
        print(f"   개선 효과: +{improvement_percentage:.1f}%p")
        
        # 전각 공백 문자 처리 효과
        total_fullwidth_removed = self.improvement_stats['original']['fullwidth_spaces']
        print(f"\n🧹 전각 공백 문자 처리:")
        print(f"   제거된 전각 공백: {total_fullwidth_removed:,}건")
        print(f"   처리 효과: 데이터 노이즈 제거로 품질 향상")
        
        # 창고별 개선 효과
        print(f"\n🏢 창고별 개선 효과:")
        for warehouse in self.warehouse_columns:
            if warehouse in self.improvement_stats['cleaned']['warehouse_stats']:
                original_stats = self.improvement_stats['original']['warehouse_stats'][warehouse]
                cleaned_stats = self.improvement_stats['cleaned']['warehouse_stats'][warehouse]
                
                print(f"   {warehouse}:")
                print(f"     개선 전: {original_stats['date_entries']:,}건 ({original_stats['date_accuracy']:.1f}%)")
                print(f"     개선 후: {cleaned_stats['cleaned_entries']:,}건 (100.0%)")
                print(f"     제거된 전각 공백: {cleaned_stats['removed_fullwidth']:,}건")
        
        # 입고 로직 성능
        improved_inbound_count = self.improvement_stats['improved_inbound']['total_inbound']
        print(f"\n📈 입고 로직 성능:")
        print(f"   처리된 입고 건수: {improved_inbound_count:,}건")
        print(f"   데이터 신뢰도: 100% (모든 엔트리가 검증된 날짜 형식)")
        
        return {
            'original_accuracy': original_accuracy,
            'improved_accuracy': cleaned_accuracy,
            'improvement': improvement_percentage,
            'fullwidth_removed': total_fullwidth_removed,
            'inbound_count': improved_inbound_count
        }
    
    def export_improved_data(self):
        """개선된 데이터 Excel 파일로 내보내기"""
        print("\n📁 개선된 데이터 Excel 파일 생성 중...")
        
        output_file = f"HVDC_DataQuality_Improved_{self.timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 개선된 전체 데이터
                self.cleaned_data.to_excel(writer, sheet_name='개선된_전체_데이터', index=False)
                
                # 개선 통계 요약
                improvement_summary = []
                for category, stats in self.improvement_stats.items():
                    if category in ['original', 'cleaned']:
                        improvement_summary.append([
                            category,
                            stats['total_entries'],
                            stats['date_entries'],
                            stats['accuracy']
                        ])
                
                summary_df = pd.DataFrame(improvement_summary, 
                                        columns=['구분', '총_엔트리', '날짜_엔트리', '정확도(%)'])
                summary_df.to_excel(writer, sheet_name='개선_요약', index=False)
                
                # 창고별 개선 통계
                warehouse_improvements = []
                for warehouse in self.warehouse_columns:
                    if warehouse in self.improvement_stats['original']['warehouse_stats']:
                        original = self.improvement_stats['original']['warehouse_stats'][warehouse]
                        cleaned = self.improvement_stats['cleaned']['warehouse_stats'][warehouse]
                        
                        warehouse_improvements.append([
                            warehouse,
                            original['total_entries'],
                            original['date_entries'],
                            original['date_accuracy'],
                            cleaned['cleaned_entries'],
                            100.0,
                            cleaned['removed_fullwidth']
                        ])
                
                warehouse_df = pd.DataFrame(warehouse_improvements,
                                          columns=['창고명', '개선전_총엔트리', '개선전_날짜엔트리', 
                                                 '개선전_정확도(%)', '개선후_엔트리', '개선후_정확도(%)', 
                                                 '제거된_전각공백'])
                warehouse_df.to_excel(writer, sheet_name='창고별_개선_통계', index=False)
            
            print(f"✅ 개선된 데이터 파일 생성 완료: {output_file}")
            print(f"📊 파일 크기: {os.path.getsize(output_file):,} bytes")
            
            return output_file
            
        except Exception as e:
            print(f"❌ 파일 생성 실패: {e}")
            return None
    
    def run_improvement_process(self):
        """전체 데이터 품질 개선 프로세스 실행"""
        print("🚀 HVDC 데이터 품질 개선 프로세스 시작")
        print("=" * 80)
        
        # 1단계: 원본 데이터 로드
        if not self.load_original_data():
            return
        
        # 2단계: 원본 데이터 품질 분석
        original_stats = self.analyze_original_quality()
        
        # 3단계: 데이터 정제
        cleaned_stats = self.clean_warehouse_data()
        
        # 4단계: 개선된 입고 로직 적용
        improved_inbound_df = self.apply_improved_inbound_logic()
        
        # 5단계: 개선된 월별 피벗 테이블 생성
        improved_pivot = self.create_improved_monthly_pivot(improved_inbound_df)
        
        # 6단계: 개선 리포트 생성
        improvement_report = self.generate_improvement_report()
        
        # 7단계: 개선된 데이터 내보내기
        output_file = self.export_improved_data()
        
        # 최종 결과 요약
        print("\n" + "=" * 80)
        print("🎉 HVDC 데이터 품질 개선 완료!")
        print("=" * 80)
        
        print(f"📊 주요 성과:")
        print(f"   데이터 정확도: {improvement_report['original_accuracy']:.1f}% → {improvement_report['improved_accuracy']:.1f}%")
        print(f"   개선 효과: +{improvement_report['improvement']:.1f}%p")
        print(f"   전각 공백 제거: {improvement_report['fullwidth_removed']:,}건")
        print(f"   검증된 입고 데이터: {improvement_report['inbound_count']:,}건")
        
        if output_file:
            print(f"📁 개선된 데이터 파일: {output_file}")
        
        print("\n✅ 모든 창고 컬럼이 100% 날짜 형식으로 표준화되었습니다!")


def main():
    """메인 실행 함수"""
    improver = HVDCDataQualityImprover()
    improver.run_improvement_process()


if __name__ == "__main__":
    main() 