#!/usr/bin/env python3
"""
올바른 HVDC 구조 기반 트랜잭션 데이터 검증
- HVDC가 프로젝트 코드로 정확히 반영되었는지 확인
- DSV 계열 창고 사용 확인
- 화물 유형별 분포 검증
- 비용 구조 검증
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

class CorrectedTransactionValidator:
    """올바른 구조 기반 트랜잭션 검증기"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.load_data()
        self.setup_expected_values()
        
    def load_data(self):
        """생성된 데이터 로딩"""
        print(f"📊 데이터 로딩: {self.filename}")
        
        try:
            # 메인 트랜잭션 데이터
            self.transactions_df = pd.read_excel(self.filename, sheet_name='Transactions')
            
            # 분석 시트들
            self.monthly_summary = pd.read_excel(self.filename, sheet_name='Monthly_Summary')
            self.warehouse_analysis = pd.read_excel(self.filename, sheet_name='Warehouse_Analysis')
            self.brand_analysis = pd.read_excel(self.filename, sheet_name='Brand_Analysis')
            self.cost_structure = pd.read_excel(self.filename, sheet_name='Cost_Structure')
            self.validation_report = pd.read_excel(self.filename, sheet_name='Validation_Report')
            
            print(f"✅ 총 {len(self.transactions_df):,}건 트랜잭션 로딩 완료")
            
        except Exception as e:
            print(f"❌ 데이터 로딩 실패: {e}")
            raise
            
    def setup_expected_values(self):
        """예상 값 설정"""
        # 올바른 창고 목록 (HVDC 제외)
        self.expected_warehouses = {
            'DSV Outdoor',
            'DSV Indoor', 
            'DSV Al Markaz',
            'DSV MZP',
            'AAA Storage'
        }
        
        # 예상 화물 유형
        self.expected_cargo_types = {
            'HE', 'SIM', 'SCT', 'ALL', 'HE_LOCAL', 'Dg Warehouse'
        }
        
        # 기본 요구사항
        self.expected_total_cases = 7573
        self.expected_total_transactions = 15146
        self.expected_transaction_types = {'IN', 'FINAL_OUT'}
        
    def validate_warehouse_structure(self) -> dict:
        """창고 구조 검증"""
        print("\n=== 1. 창고 구조 검증 ===")
        
        results = {}
        
        # 사용된 창고 목록
        used_warehouses = set(self.transactions_df['Location'].unique())
        results['used_warehouses'] = used_warehouses
        
        # HVDC가 창고로 사용되지 않았는지 확인
        hvdc_in_warehouses = any('HVDC' in warehouse for warehouse in used_warehouses)
        results['hvdc_excluded'] = not hvdc_in_warehouses
        
        # DSV 계열 창고 사용 확인
        dsv_warehouses = {w for w in used_warehouses if 'DSV' in w}
        results['dsv_warehouses_used'] = dsv_warehouses
        
        # 검증 결과 출력
        print(f"사용된 창고: {used_warehouses}")
        print(f"✅ HVDC 창고 배제: {results['hvdc_excluded']}")
        print(f"✅ DSV 계열 창고 사용: {len(dsv_warehouses)}개")
        
        if results['hvdc_excluded']:
            print("🎯 HVDC는 프로젝트 코드로 정확히 인식됨")
        else:
            print("❌ HVDC가 창고로 잘못 사용됨")
            
        return results
        
    def validate_cargo_distribution(self) -> dict:
        """화물 유형 분포 검증"""
        print("\n=== 2. 화물 유형 분포 검증 ===")
        
        results = {}
        
        # 입고 트랜잭션만 분석
        in_transactions = self.transactions_df[self.transactions_df['Transaction_Type'] == 'IN']
        
        # 화물 유형별 분포
        cargo_dist = in_transactions['Cargo_Type'].value_counts()
        cargo_pct = in_transactions['Cargo_Type'].value_counts(normalize=True) * 100
        
        results['cargo_distribution'] = cargo_dist.to_dict()
        results['cargo_percentage'] = cargo_pct.to_dict()
        
        print("화물 유형별 분포:")
        for cargo_type, count in cargo_dist.items():
            percentage = cargo_pct[cargo_type]
            print(f"  {cargo_type}: {count:,}건 ({percentage:.1f}%)")
            
        # 주요 브랜드 검증
        main_brands = ['HE', 'SIM']
        total_main_brand_cases = sum(cargo_dist.get(brand, 0) for brand in main_brands)
        results['main_brand_cases'] = total_main_brand_cases
        results['main_brand_ratio'] = total_main_brand_cases / len(in_transactions) * 100
        
        print(f"✅ 주요 브랜드 (HE+SIM): {total_main_brand_cases:,}건 ({results['main_brand_ratio']:.1f}%)")
        
        return results
        
    def validate_warehouse_specialization(self) -> dict:
        """창고별 전문화 검증"""
        print("\n=== 3. 창고별 전문화 검증 ===")
        
        results = {}
        
        # 입고 트랜잭션만 분석
        in_transactions = self.transactions_df[self.transactions_df['Transaction_Type'] == 'IN']
        
        # 창고별 화물 유형 분포
        warehouse_cargo = pd.crosstab(in_transactions['Location'], in_transactions['Cargo_Type'], normalize='index') * 100
        
        results['specialization_patterns'] = {}
        
        print("창고별 화물 유형 분포 (%):")
        for warehouse in warehouse_cargo.index:
            print(f"\n{warehouse}:")
            main_cargo = warehouse_cargo.loc[warehouse].idxmax()
            main_share = warehouse_cargo.loc[warehouse].max()
            
            results['specialization_patterns'][warehouse] = {
                'main_cargo': main_cargo,
                'main_share': main_share
            }
            
            for cargo_type in warehouse_cargo.columns:
                share = warehouse_cargo.loc[warehouse, cargo_type]
                if share > 5:  # 5% 이상만 표시
                    print(f"  {cargo_type}: {share:.1f}%")
            
            print(f"  🎯 주력: {main_cargo} ({main_share:.1f}%)")
            
        return results
        
    def validate_cost_structure(self) -> dict:
        """비용 구조 검증"""
        print("\n=== 4. 비용 구조 검증 ===")
        
        results = {}
        
        # 총 비용 분석
        total_amount = self.transactions_df['Amount'].sum()
        total_handling = self.transactions_df['Handling_Fee'].sum()
        total_rent = self.transactions_df['Rent_Fee'].sum()
        
        # 비용 비율
        if total_amount > 0:
            handling_ratio = total_handling / total_amount * 100
            rent_ratio = total_rent / total_amount * 100
        else:
            handling_ratio = rent_ratio = 0
            
        results['total_amount'] = total_amount
        results['handling_amount'] = total_handling
        results['rent_amount'] = total_rent
        results['handling_ratio'] = handling_ratio
        results['rent_ratio'] = rent_ratio
        
        print(f"총 금액: {total_amount:,.0f} AED")
        print(f"HANDLING: {total_handling:,.0f} AED ({handling_ratio:.1f}%)")
        print(f"RENT: {total_rent:,.0f} AED ({rent_ratio:.1f}%)")
        
        # 실제 INVOICE 구조와 비교 (30.3% HANDLING, 69.7% RENT)
        expected_handling_ratio = 30.3
        expected_rent_ratio = 69.7
        
        handling_diff = abs(handling_ratio - expected_handling_ratio)
        rent_diff = abs(rent_ratio - expected_rent_ratio)
        
        results['handling_accuracy'] = handling_diff < 10  # 10% 이내 오차
        results['rent_accuracy'] = rent_diff < 10
        
        print(f"✅ HANDLING 비율 정확도: {results['handling_accuracy']} (차이: {handling_diff:.1f}%)")
        print(f"✅ RENT 비율 정확도: {results['rent_accuracy']} (차이: {rent_diff:.1f}%)")
        
        return results
        
    def validate_transaction_structure(self) -> dict:
        """트랜잭션 구조 검증"""
        print("\n=== 5. 트랜잭션 구조 검증 ===")
        
        results = {}
        
        # 기본 통계
        total_transactions = len(self.transactions_df)
        in_transactions = len(self.transactions_df[self.transactions_df['Transaction_Type'] == 'IN'])
        out_transactions = len(self.transactions_df[self.transactions_df['Transaction_Type'] == 'FINAL_OUT'])
        
        results['total_transactions'] = total_transactions
        results['in_transactions'] = in_transactions
        results['out_transactions'] = out_transactions
        results['balanced_transactions'] = in_transactions == out_transactions
        
        # 케이스 수 확인
        unique_cases = self.transactions_df['Case_No'].nunique()
        results['unique_cases'] = unique_cases
        results['correct_case_count'] = unique_cases == self.expected_total_cases
        
        # 트랜잭션 타입 분포
        transaction_types = self.transactions_df['Transaction_Type'].value_counts()
        results['transaction_type_distribution'] = transaction_types.to_dict()
        
        print(f"총 트랜잭션: {total_transactions:,}건")
        print(f"입고 (IN): {in_transactions:,}건")
        print(f"출고 (FINAL_OUT): {out_transactions:,}건")
        print(f"✅ 균형된 트랜잭션: {results['balanced_transactions']}")
        print(f"✅ 고유 케이스: {unique_cases:,}건")
        print(f"✅ 올바른 케이스 수: {results['correct_case_count']}")
        
        return results
        
    def validate_date_coverage(self) -> dict:
        """날짜 범위 검증"""
        print("\n=== 6. 날짜 범위 검증 ===")
        
        results = {}
        
        # 날짜 변환
        self.transactions_df['Date'] = pd.to_datetime(self.transactions_df['Date'])
        
        # 날짜 범위
        min_date = self.transactions_df['Date'].min()
        max_date = self.transactions_df['Date'].max()
        date_range_days = (max_date - min_date).days
        
        results['min_date'] = min_date
        results['max_date'] = max_date
        results['date_range_days'] = date_range_days
        
        # 월별 분포
        monthly_dist = self.transactions_df.groupby(self.transactions_df['Date'].dt.to_period('M')).size()
        results['monthly_distribution'] = monthly_dist.to_dict()
        
        print(f"시작일: {min_date:%Y-%m-%d}")
        print(f"종료일: {max_date:%Y-%m-%d}")
        print(f"총 기간: {date_range_days:,}일")
        
        # 계절성 패턴 확인
        monthly_avg = monthly_dist.mean()
        monthly_std = monthly_dist.std()
        cv = monthly_std / monthly_avg if monthly_avg > 0 else 0
        
        results['monthly_variability'] = cv
        results['has_seasonality'] = cv > 0.5  # 50% 이상 변동성
        
        print(f"✅ 월별 변동성: {cv:.2f}")
        print(f"✅ 계절성 패턴: {results['has_seasonality']}")
        
        return results
        
    def generate_comprehensive_report(self) -> dict:
        """종합 검증 리포트 생성"""
        print("\n" + "=" * 60)
        print("🎯 종합 검증 리포트")
        print("=" * 60)
        
        # 모든 검증 실행
        warehouse_results = self.validate_warehouse_structure()
        cargo_results = self.validate_cargo_distribution()
        specialization_results = self.validate_warehouse_specialization()
        cost_results = self.validate_cost_structure()
        transaction_results = self.validate_transaction_structure()
        date_results = self.validate_date_coverage()
        
        # 종합 점수 계산
        validation_checks = [
            warehouse_results['hvdc_excluded'],
            len(warehouse_results['dsv_warehouses_used']) >= 2,
            cargo_results['main_brand_ratio'] > 80,  # 주요 브랜드 80% 이상
            cost_results['handling_accuracy'] or cost_results['rent_accuracy'],
            transaction_results['balanced_transactions'],
            transaction_results['correct_case_count'],
            date_results['has_seasonality']
        ]
        
        passed_checks = sum(validation_checks)
        total_checks = len(validation_checks)
        quality_score = passed_checks / total_checks * 100
        
        # 종합 결과
        comprehensive_results = {
            'quality_score': quality_score,
            'passed_checks': passed_checks,
            'total_checks': total_checks,
            'warehouse_validation': warehouse_results,
            'cargo_validation': cargo_results,
            'specialization_validation': specialization_results,
            'cost_validation': cost_results,
            'transaction_validation': transaction_results,
            'date_validation': date_results
        }
        
        print(f"\n🏆 최종 품질 점수: {quality_score:.1f}% ({passed_checks}/{total_checks})")
        
        if quality_score >= 90:
            print("🟢 EXCELLENT: 올바른 HVDC 구조가 완벽하게 반영됨")
        elif quality_score >= 80:
            print("🟡 GOOD: 대부분의 요구사항이 충족됨")
        elif quality_score >= 70:
            print("🟠 FAIR: 개선이 필요함")
        else:
            print("🔴 POOR: 재작업 필요")
            
        # 핵심 개선사항
        print("\n📋 핵심 확인사항:")
        print(f"✅ HVDC 프로젝트 코드 인식: {warehouse_results['hvdc_excluded']}")
        print(f"✅ DSV 계열 창고 사용: {len(warehouse_results['dsv_warehouses_used'])}개")
        print(f"✅ 실제 화물 브랜드 반영: {cargo_results['main_brand_ratio']:.1f}%")
        print(f"✅ 균형된 트랜잭션: {transaction_results['balanced_transactions']}")
        print(f"✅ 올바른 케이스 수: {transaction_results['correct_case_count']}")
        
        return comprehensive_results
        
    def save_validation_report(self, results: dict):
        """검증 리포트 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"HVDC_올바른구조_검증리포트_{timestamp}.xlsx"
        
        print(f"\n💾 검증 리포트 저장: {report_filename}")
        
        # 검증 결과를 DataFrame으로 변환
        validation_summary = pd.DataFrame({
            'Validation_Area': [
                'HVDC Structure',
                'Warehouse Usage',
                'Cargo Distribution', 
                'Cost Structure',
                'Transaction Balance',
                'Case Count',
                'Date Coverage',
                'Overall Quality'
            ],
            'Status': [
                '✅ PASS' if results['warehouse_validation']['hvdc_excluded'] else '❌ FAIL',
                f"✅ {len(results['warehouse_validation']['dsv_warehouses_used'])}개 DSV 창고",
                f"✅ {results['cargo_validation']['main_brand_ratio']:.1f}% 주요 브랜드",
                '✅ PASS' if results['cost_validation']['handling_accuracy'] or results['cost_validation']['rent_accuracy'] else '❌ FAIL',
                '✅ PASS' if results['transaction_validation']['balanced_transactions'] else '❌ FAIL',
                '✅ PASS' if results['transaction_validation']['correct_case_count'] else '❌ FAIL',
                '✅ PASS' if results['date_validation']['has_seasonality'] else '❌ FAIL',
                f"🏆 {results['quality_score']:.1f}%"
            ]
        })
        
        with pd.ExcelWriter(report_filename, engine='openpyxl') as writer:
            validation_summary.to_excel(writer, sheet_name='Validation_Summary', index=False)
            
        print(f"✅ 검증 리포트 저장 완료: {report_filename}")

def main():
    """메인 실행 함수"""
    # 최신 생성된 파일 찾기
    files = [f for f in os.listdir('.') if f.startswith('HVDC_올바른구조_실제데이터_트랜잭션_') and f.endswith('.xlsx')]
    
    if not files:
        print("❌ 검증할 트랜잭션 파일을 찾을 수 없습니다.")
        return
        
    latest_file = max(files, key=os.path.getctime)
    print(f"🔍 검증 대상 파일: {latest_file}")
    
    # 검증 실행
    validator = CorrectedTransactionValidator(latest_file)
    results = validator.generate_comprehensive_report()
    validator.save_validation_report(results)
    
if __name__ == "__main__":
    main() 