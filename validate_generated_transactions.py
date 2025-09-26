#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini 생성된 트랜잭션 데이터 검증기
생성된 월별 트랜잭션 데이터가 요구사항을 충족하는지 검증
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import glob
import os

class TransactionDataValidator:
    """트랜잭션 데이터 검증기"""
    
    def __init__(self, excel_file: str):
        """검증기 초기화"""
        self.excel_file = excel_file
        self.df = None
        self.validation_results = {}
        
    def load_data(self):
        """Excel 파일에서 데이터 로드"""
        print(f"📁 데이터 로딩: {self.excel_file}")
        try:
            self.df = pd.read_excel(self.excel_file, sheet_name='전체트랜잭션')
            print(f"✅ 데이터 로드 완료: {len(self.df):,}건")
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
        return True
        
    def validate_column_structure(self):
        """컬럼 구조 검증"""
        print("\n🔍 컬럼 구조 검증...")
        
        required_columns = [
            'Case_No', 'Date', 'Location', 'TxType_Refined', 'Qty', 
            'Amount', 'Handling Fee', 'Storage_Type', 'Source_File'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        extra_columns = [col for col in self.df.columns if col not in required_columns + ['월', 'Billing month', 'Category', 'Loc_From', 'Target_Warehouse']]
        
        if missing_columns:
            self.validation_results['missing_columns'] = missing_columns
            print(f"❌ 누락된 컬럼: {missing_columns}")
        else:
            print("✅ 모든 필수 컬럼 존재")
            
        if extra_columns:
            print(f"ℹ️ 추가 컬럼: {extra_columns}")
            
        self.validation_results['column_structure'] = len(missing_columns) == 0
        
    def validate_date_ranges(self):
        """날짜 범위 검증"""
        print("\n📅 날짜 범위 검증...")
        
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        min_date = self.df['Date'].min()
        max_date = self.df['Date'].max()
        
        expected_start = datetime(2023, 12, 1)
        expected_end = datetime(2025, 12, 31)
        
        print(f"   실제 기간: {min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
        print(f"   기대 기간: {expected_start.strftime('%Y-%m-%d')} ~ {expected_end.strftime('%Y-%m-%d')}")
        
        date_valid = (min_date >= expected_start) and (max_date <= expected_end)
        self.validation_results['date_range'] = date_valid
        
        if date_valid:
            print("✅ 날짜 범위 올바름")
        else:
            print("❌ 날짜 범위 오류")
            
    def validate_warehouse_distribution(self):
        """창고별 분포 검증"""
        print("\n🏢 창고별 분포 검증...")
        
        expected_warehouses = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'MOSB']
        actual_warehouses = list(self.df['Location'].unique())
        
        print(f"   기대 창고: {expected_warehouses}")
        print(f"   실제 창고: {actual_warehouses}")
        
        warehouse_distribution = self.df.groupby('Location')['Qty'].sum()
        total_qty = warehouse_distribution.sum()
        
        print(f"\n   **창고별 수량 분포:**")
        for warehouse in expected_warehouses:
            if warehouse in warehouse_distribution:
                qty = warehouse_distribution[warehouse]
                percentage = (qty / total_qty) * 100
                print(f"   {warehouse}: {qty:,}개 ({percentage:.1f}%)")
            else:
                print(f"   {warehouse}: 데이터 없음")
                
        # 분포 비율 검증 (±5% 허용)
        expected_ratios = {
            'DSV Outdoor': 0.35,
            'DSV Al Markaz': 0.30,
            'DSV Indoor': 0.20,
            'MOSB': 0.15
        }
        
        distribution_valid = True
        for warehouse, expected_ratio in expected_ratios.items():
            if warehouse in warehouse_distribution:
                actual_ratio = warehouse_distribution[warehouse] / total_qty
                if abs(actual_ratio - expected_ratio) > 0.05:
                    distribution_valid = False
                    print(f"⚠️ {warehouse} 분포 오차: 기대 {expected_ratio:.1%}, 실제 {actual_ratio:.1%}")
                    
        self.validation_results['warehouse_distribution'] = distribution_valid
        if distribution_valid:
            print("✅ 창고별 분포 올바름")
            
    def validate_transaction_types(self):
        """트랜잭션 타입 검증"""
        print("\n🔄 트랜잭션 타입 검증...")
        
        expected_types = ['IN', 'TRANSFER_OUT', 'FINAL_OUT']
        actual_types = list(self.df['TxType_Refined'].unique())
        
        print(f"   기대 타입: {expected_types}")
        print(f"   실제 타입: {actual_types}")
        
        type_distribution = self.df['TxType_Refined'].value_counts()
        total_tx = len(self.df)
        
        print(f"\n   **트랜잭션 타입별 분포:**")
        for tx_type in expected_types:
            if tx_type in type_distribution:
                count = type_distribution[tx_type]
                percentage = (count / total_tx) * 100
                print(f"   {tx_type}: {count:,}건 ({percentage:.1f}%)")
            else:
                print(f"   {tx_type}: 데이터 없음")
                
        types_valid = all(t in actual_types for t in expected_types)
        self.validation_results['transaction_types'] = types_valid
        
        if types_valid:
            print("✅ 트랜잭션 타입 올바름")
        else:
            print("❌ 트랜잭션 타입 오류")
            
    def validate_data_quality(self):
        """데이터 품질 검증"""
        print("\n🔬 데이터 품질 검증...")
        
        # NULL 값 검사
        null_counts = self.df.isnull().sum()
        critical_nulls = null_counts[null_counts > 0]
        
        if len(critical_nulls) > 0:
            print(f"⚠️ NULL 값 발견:")
            for col, count in critical_nulls.items():
                print(f"   {col}: {count}개")
        else:
            print("✅ NULL 값 없음")
            
        # 수량 및 금액 범위 검사
        qty_stats = self.df['Qty'].describe()
        amount_stats = self.df['Amount'].describe()
        fee_stats = self.df['Handling Fee'].describe()
        
        print(f"\n   **수량 통계:**")
        print(f"   평균: {qty_stats['mean']:.1f}, 최소: {qty_stats['min']:.0f}, 최대: {qty_stats['max']:.0f}")
        
        print(f"\n   **금액 통계:**")
        print(f"   평균: ${amount_stats['mean']:,.2f}, 최소: ${amount_stats['min']:,.2f}, 최대: ${amount_stats['max']:,.2f}")
        
        print(f"\n   **하역비 통계:**")
        print(f"   평균: ${fee_stats['mean']:,.2f}, 최소: ${fee_stats['min']:,.2f}, 최대: ${fee_stats['max']:,.2f}")
        
        # 데이터 품질 기준
        quality_checks = {
            'positive_qty': (self.df['Qty'] > 0).all(),
            'positive_amount': (self.df['Amount'] > 0).all(),
            'positive_fee': (self.df['Handling Fee'] >= 0).all(),
            'unique_case_ids': self.df['Case_No'].nunique() == len(self.df),
            'realistic_qty': (self.df['Qty'] <= 100).all(),
            'realistic_amount': (self.df['Amount'] <= 50000).all()
        }
        
        quality_valid = all(quality_checks.values())
        self.validation_results['data_quality'] = quality_valid
        
        print(f"\n   **품질 검사 결과:**")
        for check, result in quality_checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}: {result}")
            
    def validate_seasonal_patterns(self):
        """계절적 패턴 검증"""
        print("\n🌱 계절적 패턴 검증...")
        
        monthly_qty = self.df.groupby('월')['Qty'].sum().sort_index()
        
        # 피크 월 확인
        peak_months = monthly_qty.nlargest(3).index.tolist()
        expected_peaks = ['2024-06', '2024-08', '2025-03']
        
        print(f"   기대 피크: {expected_peaks}")
        print(f"   실제 피크: {peak_months}")
        
        # 월별 상위 10개월 표시
        print(f"\n   **월별 수량 상위 10개월:**")
        for month, qty in monthly_qty.nlargest(10).items():
            print(f"   {month}: {qty:,}개")
            
        peaks_match = len(set(peak_months) & set(expected_peaks)) >= 2
        self.validation_results['seasonal_patterns'] = peaks_match
        
        if peaks_match:
            print("✅ 계절적 패턴 적절함")
        else:
            print("⚠️ 계절적 패턴 확인 필요")
            
    def generate_validation_report(self):
        """검증 리포트 생성"""
        print("\n" + "="*60)
        print("📋 **트랜잭션 데이터 검증 리포트**")
        print("="*60)
        
        total_checks = len(self.validation_results)
        passed_checks = sum(self.validation_results.values())
        
        print(f"📊 **전체 검증 결과:** {passed_checks}/{total_checks} 통과")
        print(f"📁 **파일:** {self.excel_file}")
        print(f"📈 **총 트랜잭션:** {len(self.df):,}건")
        print(f"💰 **총 금액:** ${self.df['Amount'].sum():,.2f}")
        print(f"🚛 **총 하역비:** ${self.df['Handling Fee'].sum():,.2f}")
        
        print(f"\n🔍 **상세 검증 결과:**")
        for check, result in self.validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {check}")
            
        overall_status = "✅ 검증 성공" if passed_checks == total_checks else f"⚠️ {total_checks - passed_checks}개 항목 확인 필요"
        print(f"\n🎯 **최종 결과:** {overall_status}")
        
        return passed_checks == total_checks
        
def main():
    """메인 검증 함수"""
    print("🔍 MACHO-GPT v3.4-mini 트랜잭션 데이터 검증기")
    print("=" * 60)
    
    # 최신 Excel 파일 찾기
    excel_files = glob.glob("HVDC_월별트랜잭션데이터_*.xlsx")
    if not excel_files:
        print("❌ 트랜잭션 Excel 파일을 찾을 수 없습니다.")
        return False
        
    latest_file = max(excel_files, key=os.path.getctime)
    print(f"📁 최신 파일: {latest_file}")
    
    # 검증기 실행
    validator = TransactionDataValidator(latest_file)
    
    if not validator.load_data():
        return False
        
    # 모든 검증 실행
    validator.validate_column_structure()
    validator.validate_date_ranges()
    validator.validate_warehouse_distribution()
    validator.validate_transaction_types()
    validator.validate_data_quality()
    validator.validate_seasonal_patterns()
    
    # 최종 리포트
    success = validator.generate_validation_report()
    
    if success:
        print("\n🎉 모든 검증을 통과했습니다!")
    else:
        print("\n⚠️ 일부 검증에서 문제가 발견되었습니다.")
        
    return success

if __name__ == '__main__':
    success = main()
    
    print("\n🔧 **추천 명령어:**")
    print("/logi_master transaction_analysis [상세 트랜잭션 분석]")
    print("/excel_reporter monthly_summary [월별 요약 리포트]")
    print("/data_quality_check advanced [고급 품질 검사]") 