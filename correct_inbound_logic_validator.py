#!/usr/bin/env python3
"""
정확한 입고 로직 검증 스크립트 v2.0
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini

입고 로직 상세 보고서 기준:
1. calculate_status_current() 먼저 실행 (Status_Location 계산)
2. Final_Location 파생: DSV Al Markaz 우선 → DSV Indoor 차순위 → Status_Location 사용
3. 월별 피벗 테이블: Final_Location 기준 집계
4. 창고 컬럼 날짜 기반 입고 판단
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CorrectInboundLogicValidator:
    """정확한 입고 로직 검증기"""
    
    def __init__(self):
        """초기화"""
        print("🔍 정확한 입고 로직 검증 시작 - HVDC 프로젝트 v2.0")
        print("=" * 80)
        
        # 실제 데이터 파일 경로
        self.data_path = Path("data")
        self.hitachi_file = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.simense_file = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        
        # 보고서 기준 창고 컬럼 (정확한 순서)
        self.warehouse_columns = [
            'DSV Outdoor',
            'DSV Indoor', 
            'DSV Al Markaz',
            'AAA  Storage',
            'DHL Warehouse',
            'MOSB',
            'Hauler Indoor'
        ]
        
        # 실제 데이터 저장
        self.combined_data = None
        self.total_records = 0
        
    def load_and_analyze_data_structure(self):
        """데이터 로드 및 구조 분석"""
        print("\n📂 실제 HVDC 데이터 로드 및 구조 분석...")
        
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
                self.combined_data = pd.concat(combined_dfs, ignore_index=True, sort=False)
                self.total_records = len(self.combined_data)
                print(f"🔗 데이터 결합 완료: {self.total_records:,}건")
                
                # 컬럼 구조 분석
                print(f"\n📋 전체 컬럼 수: {len(self.combined_data.columns)}")
                print(f"📋 전체 컬럼 목록:")
                for i, col in enumerate(self.combined_data.columns):
                    print(f"  {i+1:2d}. {col}")
                
                # 중요한 컬럼 존재 확인
                print(f"\n🔍 중요 컬럼 존재 여부:")
                
                # Status_Location 컬럼 찾기
                status_location_candidates = [col for col in self.combined_data.columns 
                                            if 'status' in col.lower() or 'location' in col.lower()]
                print(f"   Status/Location 관련 컬럼: {status_location_candidates}")
                
                # 창고 컬럼 존재 확인
                existing_warehouses = [col for col in self.warehouse_columns if col in self.combined_data.columns]
                print(f"   존재하는 창고 컬럼: {existing_warehouses}")
                
                # 날짜 컬럼 분석
                print(f"\n📅 날짜 형식 컬럼 분석:")
                for warehouse in existing_warehouses:
                    non_null_count = self.combined_data[warehouse].notna().sum()
                    if non_null_count > 0:
                        sample_data = self.combined_data[warehouse].dropna().head(3)
                        print(f"   {warehouse}: {non_null_count:,}건 - 샘플: {sample_data.tolist()}")
                
                self.warehouse_columns = existing_warehouses
                return True
            else:
                print("❌ 로드할 데이터가 없습니다.")
                return False
                
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def calculate_status_current(self, df):
        """Status_Location 계산 (보고서 기준)"""
        print("\n🔍 Status_Location 계산 중...")
        
        # Status_Location 컬럼이 이미 있는지 확인
        if 'Status_Location' in df.columns:
            print("   기존 Status_Location 컬럼 사용")
            return df
        
        # Status_Location 파생 로직 (가장 최근 날짜 창고 사용)
        result_df = df.copy()
        status_locations = []
        
        for _, row in result_df.iterrows():
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
        
        result_df['Status_Location'] = status_locations
        print(f"   Status_Location 계산 완료: {len(result_df):,}건")
        
        return result_df
    
    def calculate_final_location(self, df):
        """Final_Location 파생 계산 (보고서 기준)"""
        print("\n🔍 Final_Location 파생 계산 중...")
        
        # 1단계: Status_Location 계산
        result_df = self.calculate_status_current(df)
        
        # 2단계: Final_Location 파생 로직 (보고서 기준)
        conditions = []
        choices = []
        
        # DSV Al Markaz 우선 선택
        if 'DSV Al Markaz' in result_df.columns:
            conditions.append(result_df['DSV Al Markaz'].notna() & result_df['DSV Al Markaz'].ne(''))
            choices.append('DSV Al Markaz')  # 창고명 직접 사용
        
        # DSV Indoor 차순위
        if 'DSV Indoor' in result_df.columns:
            conditions.append(result_df['DSV Indoor'].notna() & result_df['DSV Indoor'].ne(''))
            choices.append('DSV Indoor')  # 창고명 직접 사용
        
        # 나머지는 Status_Location 사용
        default_value = result_df['Status_Location']
        
        # Final_Location 계산
        if conditions and choices:
            result_df['Final_Location'] = np.select(conditions, choices, default=default_value)
        else:
            result_df['Final_Location'] = default_value
        
        # Final_Location 분포 확인
        final_location_counts = result_df['Final_Location'].value_counts()
        print(f"   Final_Location 분포:")
        for location, count in final_location_counts.head(10).items():
            percentage = (count / len(result_df)) * 100
            print(f"     {location}: {count:,}건 ({percentage:.1f}%)")
        
        return result_df
    
    def validate_correct_inbound_logic(self):
        """정확한 입고 로직 검증"""
        print("\n🔍 정확한 입고 로직 검증 시작")
        print("-" * 60)
        
        # 1단계: Final_Location 계산
        result_df = self.calculate_final_location(self.combined_data)
        
        # 2단계: 입고 아이템 추출 (보고서 기준)
        inbound_items = []
        
        for _, row in result_df.iterrows():
            for warehouse in self.warehouse_columns:
                if pd.notna(row[warehouse]):
                    try:
                        warehouse_date = pd.to_datetime(row[warehouse])
                        inbound_items.append({
                            'item': row.name,
                            'warehouse': warehouse,
                            'date': warehouse_date,
                            'month': warehouse_date.to_period('M'),
                            'final_location': row['Final_Location']
                        })
                    except:
                        continue
        
        # 3단계: 집계 계산
        inbound_df = pd.DataFrame(inbound_items)
        
        print(f"📊 정확한 입고 로직 검증 결과:")
        print(f"   총 입고 건수: {len(inbound_df):,}건")
        
        if len(inbound_df) > 0:
            by_warehouse = inbound_df.groupby('warehouse').size().to_dict()
            by_month = inbound_df.groupby('month').size().to_dict()
            by_final_location = inbound_df.groupby('final_location').size().to_dict()
            
            print(f"   창고별 입고 건수:")
            for warehouse, count in sorted(by_warehouse.items(), key=lambda x: x[1], reverse=True):
                print(f"     {warehouse}: {count:,}건")
            
            print(f"   Final_Location별 입고 건수:")
            for location, count in sorted(by_final_location.items(), key=lambda x: x[1], reverse=True):
                print(f"     {location}: {count:,}건")
            
            print(f"   월별 입고 건수 (최근 6개월):")
            recent_months = sorted(by_month.items(), key=lambda x: x[0], reverse=True)[:6]
            for month, count in recent_months:
                print(f"     {month}: {count:,}건")
        
        return inbound_df, result_df
    
    def create_correct_monthly_pivot(self, inbound_df):
        """정확한 월별 피벗 테이블 생성 (Final_Location 기준)"""
        print("\n🔍 정확한 월별 피벗 테이블 생성 (Final_Location 기준)")
        print("-" * 60)
        
        if len(inbound_df) == 0:
            print("⚠️ 입고 데이터가 없어 피벗 테이블을 생성할 수 없습니다.")
            return pd.DataFrame()
        
        try:
            # 보고서 기준: Final_Location 기준으로 피벗 테이블 생성
            monthly_pivot = inbound_df.pivot_table(
                values='item',
                index='month',
                columns='final_location',
                aggfunc='count',
                fill_value=0
            )
            
            print(f"📊 정확한 월별 피벗 테이블 결과:")
            print(f"   피벗 테이블 크기: {monthly_pivot.shape}")
            print(f"   월별 기간: {monthly_pivot.index.min()} ~ {monthly_pivot.index.max()}")
            print(f"   Final_Location 수: {len(monthly_pivot.columns)}")
            
            # 최근 6개월 데이터 미리보기
            recent_months = monthly_pivot.tail(6)
            print(f"   최근 6개월 Final_Location별 입고 현황:")
            print(recent_months.to_string())
            
            return monthly_pivot
            
        except Exception as e:
            print(f"❌ 피벗 테이블 생성 실패: {e}")
            return pd.DataFrame()
    
    def validate_final_accuracy(self, inbound_df, result_df):
        """최종 정확도 검증"""
        print("\n🔍 최종 정확도 검증")
        print("-" * 60)
        
        # 1. 입고 로직 vs 실제 데이터 일치성 검증
        total_warehouse_entries = 0
        for warehouse in self.warehouse_columns:
            if warehouse in self.combined_data.columns:
                entries = self.combined_data[warehouse].notna().sum()
                total_warehouse_entries += entries
                print(f"   {warehouse} 실제 엔트리: {entries:,}건")
        
        print(f"   총 창고 엔트리: {total_warehouse_entries:,}건")
        print(f"   입고 로직 결과: {len(inbound_df):,}건")
        
        accuracy = (len(inbound_df) / total_warehouse_entries * 100) if total_warehouse_entries > 0 else 0
        print(f"   입고 로직 정확도: {accuracy:.1f}%")
        
        # 2. Final_Location 파생 로직 검증
        dsv_al_markaz_count = (result_df['Final_Location'] == 'DSV Al Markaz').sum()
        dsv_indoor_count = (result_df['Final_Location'] == 'DSV Indoor').sum()
        
        print(f"   DSV Al Markaz Final_Location: {dsv_al_markaz_count:,}건")
        print(f"   DSV Indoor Final_Location: {dsv_indoor_count:,}건")
        
        # 3. 월별 분포 검증
        if len(inbound_df) > 0:
            monthly_distribution = inbound_df.groupby('month').size()
            print(f"   월별 분포 범위: {monthly_distribution.min()} ~ {monthly_distribution.max()}건")
        
        return accuracy
    
    def generate_correct_validation_report(self):
        """정확한 검증 리포트 생성"""
        print("\n📋 정확한 입고 로직 검증 리포트 생성")
        print("=" * 80)
        
        # 데이터 로드 및 구조 분석
        if not self.load_and_analyze_data_structure():
            return
        
        # 정확한 입고 로직 검증
        inbound_df, result_df = self.validate_correct_inbound_logic()
        
        # 정확한 월별 피벗 테이블 생성
        monthly_pivot = self.create_correct_monthly_pivot(inbound_df)
        
        # 최종 정확도 검증
        accuracy = self.validate_final_accuracy(inbound_df, result_df)
        
        # 최종 결과 요약
        print("\n" + "=" * 80)
        print("🎯 정확한 입고 로직 검증 결과 요약")
        print("=" * 80)
        
        print(f"✅ 데이터 로드: {self.total_records:,}건")
        print(f"✅ 입고 로직 검증: {len(inbound_df):,}건 입고 데이터")
        print(f"✅ Final_Location 파생: {len(result_df):,}건 처리")
        print(f"✅ 월별 피벗 테이블: {monthly_pivot.shape}")
        print(f"✅ 로직 정확도: {accuracy:.1f}%")
        
        if accuracy >= 95:
            print("🎉 입고 로직이 정확하게 동작합니다!")
        elif accuracy >= 80:
            print("⚠️ 입고 로직이 대체로 정확하지만 일부 개선이 필요합니다.")
        else:
            print("❌ 입고 로직에 중대한 오류가 있습니다. 수정이 필요합니다.")


def main():
    """메인 실행 함수"""
    validator = CorrectInboundLogicValidator()
    validator.generate_correct_validation_report()


if __name__ == "__main__":
    main() 