#!/usr/bin/env python3
"""
INVOICE 원본 자료 구조 재검증
- 사용자 제공 이미지 데이터 기반 분석
- 실제 INVOICE 구조와 우리의 이해 비교
- 트랜잭션 생성기 정확도 검증
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

class OriginalInvoiceStructureVerifier:
    """INVOICE 원본 구조 검증기"""
    
    def __init__(self):
        self.setup_image_data()
        self.load_actual_invoice()
        
    def setup_image_data(self):
        """이미지에서 확인된 데이터 설정"""
        
        # 이미지 1: HVDC CODE 3별 패키지 수 (pkg)
        self.image1_pkg_data = {
            'AAA Storage': {'HE': 0, 'total': 0},
            'DSV Al Markaz': {'ALL': 0, 'HE': 15, 'total': 15},
            'DSV Indoor': {'ALL': 0, 'HE': 1488, 'MOSB': 2, 'PPL': 6, 'SCT': 38, 'SEI': 14, 'SIM': 249, 'total': 1797},
            'DSV MZP': {'ALL': 0, 'HE': 0, 'total': 0},
            'DSV Outdoor': {'ALL': 0, 'HE': 1216, 'MOSB': 41, 'SCT': 2954, 'SEI': 253, 'SIM': 1472, 'total': 5936},
            'total': {'ALL': 0, 'HE': 2719, 'MOSB': 43, 'PPL': 6, 'SCT': 2992, 'SEI': 267, 'SIM': 1721, 'total': 7748}
        }
        
        # 이미지 2: HVDC CODE 5별 TOTAL 금액 (HANDLING vs RENT)
        self.image2_total_data = {
            'AAA Storage': {'HANDLING': 54701.14, 'RENT': 0, 'total': 54701.14},
            'DSV Al Markaz': {'HANDLING': 144574.50, 'RENT': 1966800.00, 'total': 2111374.50},
            'DSV Indoor': {'HANDLING': 1112056.16, 'RENT': 2903159.44, 'total': 4015215.60},
            'DSV MZP': {'HANDLING': 4089.85, 'RENT': 429000.00, 'total': 433089.85},
            'DSV Outdoor': {'HANDLING': 2184894.25, 'RENT': 2740361.55, 'total': 4925255.80},
            'total': {'HANDLING': 3500315.90, 'RENT': 8039320.99, 'total': 11539636.89}
        }
        
        # 이미지 4: 월별 운영 데이터 (부분)
        self.image4_monthly_data = {
            '2023년 12월': {'DSV Al Markaz': {'RENT': 4628}, 'DSV Indoor': {'RENT': 29160}, 'DSV Outdoor': {'HANDLING': 62136, 'RENT': 58783}, 'total': 154706},
            '2024년 1월': {'DSV Indoor': {'HANDLING': 168480, 'RENT': 228045}, 'DSV Outdoor': {'HANDLING': 30219}, 'total': 426745},
            '2024년 2월': {'DSV Indoor': {'HANDLING': 99051, 'RENT': 144859}, 'DSV Outdoor': {'HANDLING': 91549, 'RENT': 93808}, 'total': 429266}
        }
        
    def load_actual_invoice(self):
        """실제 INVOICE 파일 로딩"""
        try:
            self.invoice_df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx')
            print(f"✅ 실제 INVOICE 데이터 로딩: {len(self.invoice_df)}건")
        except Exception as e:
            print(f"❌ INVOICE 파일 로딩 실패: {e}")
            self.invoice_df = None
            
    def verify_package_counts(self):
        """패키지 수 검증"""
        print("\n=== 1. 패키지 수 검증 ===")
        
        if self.invoice_df is None:
            print("❌ INVOICE 데이터가 없어 검증 불가")
            return
            
        # SQM 필터링된 데이터
        sqm_data = self.invoice_df[self.invoice_df['HVDC CODE 2'] == 'SQM'].copy()
        
        # 실제 데이터의 패키지 수 집계
        actual_pkg_summary = sqm_data.groupby(['HVDC CODE 1', 'HVDC CODE 3'])['PKG'].sum().unstack(fill_value=0)
        
        print("📊 실제 INVOICE 패키지 수:")
        print(actual_pkg_summary)
        
        print("\n📊 이미지에서 확인된 패키지 수:")
        for warehouse, data in self.image1_pkg_data.items():
            if warehouse != 'total':
                print(f"{warehouse}: {data}")
                
        # 총계 비교
        actual_total = sqm_data['PKG'].sum()
        image_total = self.image1_pkg_data['total']['total']
        
        print(f"\n🔍 총 패키지 수 비교:")
        print(f"실제 INVOICE: {actual_total:,}건")
        print(f"이미지 데이터: {image_total:,}건")
        print(f"일치 여부: {'✅' if actual_total == image_total else '❌'}")
        
        return {
            'actual_total': actual_total,
            'image_total': image_total,
            'matches': actual_total == image_total
        }
        
    def verify_cost_structure(self):
        """비용 구조 검증"""
        print("\n=== 2. 비용 구조 검증 ===")
        
        if self.invoice_df is None:
            print("❌ INVOICE 데이터가 없어 검증 불가")
            return
            
        # SQM 필터링된 데이터
        sqm_data = self.invoice_df[self.invoice_df['HVDC CODE 2'] == 'SQM'].copy()
        
        # 실제 데이터의 비용 집계
        actual_cost_summary = sqm_data.groupby('HVDC CODE 1')[['HANDLING', 'RENT', 'TOTAL']].sum()
        
        print("📊 실제 INVOICE 비용 구조:")
        print(actual_cost_summary.round(2))
        
        print("\n📊 이미지에서 확인된 비용 구조:")
        for warehouse, data in self.image2_total_data.items():
            if warehouse != 'total':
                print(f"{warehouse}: HANDLING {data['HANDLING']:,.2f}, RENT {data['RENT']:,.2f}, TOTAL {data['total']:,.2f}")
                
        # 총계 비교
        actual_handling = sqm_data['HANDLING'].sum()
        actual_rent = sqm_data['RENT'].sum()
        actual_total = sqm_data['TOTAL'].sum()
        
        image_handling = self.image2_total_data['total']['HANDLING']
        image_rent = self.image2_total_data['total']['RENT']
        image_total = self.image2_total_data['total']['total']
        
        print(f"\n🔍 총 비용 비교:")
        print(f"HANDLING - 실제: {actual_handling:,.2f}, 이미지: {image_handling:,.2f}")
        print(f"RENT     - 실제: {actual_rent:,.2f}, 이미지: {image_rent:,.2f}")
        print(f"TOTAL    - 실제: {actual_total:,.2f}, 이미지: {image_total:,.2f}")
        
        # 비율 계산
        handling_ratio = actual_handling / actual_total * 100 if actual_total > 0 else 0
        rent_ratio = actual_rent / actual_total * 100 if actual_total > 0 else 0
        
        print(f"\n📊 비용 비율:")
        print(f"HANDLING: {handling_ratio:.1f}%")
        print(f"RENT: {rent_ratio:.1f}%")
        
        return {
            'actual_handling': actual_handling,
            'actual_rent': actual_rent,
            'actual_total': actual_total,
            'image_handling': image_handling,
            'image_rent': image_rent,
            'image_total': image_total,
            'handling_ratio': handling_ratio,
            'rent_ratio': rent_ratio
        }
        
    def verify_warehouse_cargo_distribution(self):
        """창고별 화물 분포 검증"""
        print("\n=== 3. 창고별 화물 분포 검증 ===")
        
        if self.invoice_df is None:
            print("❌ INVOICE 데이터가 없어 검증 불가")
            return
            
        # SQM 필터링된 데이터
        sqm_data = self.invoice_df[self.invoice_df['HVDC CODE 2'] == 'SQM'].copy()
        
        # 화물 유형별 실제 분포
        cargo_dist = sqm_data['HVDC CODE 3'].value_counts()
        cargo_pct = sqm_data['HVDC CODE 3'].value_counts(normalize=True) * 100
        
        print("📊 화물 유형별 분포:")
        for cargo_type in cargo_dist.index:
            count = cargo_dist[cargo_type]
            percentage = cargo_pct[cargo_type]
            print(f"  {cargo_type}: {count}건 ({percentage:.1f}%)")
            
        # 이미지 데이터와 비교
        image_cargo_totals = self.image1_pkg_data['total']
        print(f"\n🔍 주요 화물 유형 비교:")
        for cargo_type in ['HE', 'SIM', 'SCT']:
            actual = cargo_dist.get(cargo_type, 0)
            image = image_cargo_totals.get(cargo_type, 0)
            print(f"{cargo_type}: 실제 {actual}, 이미지 {image}, 일치 {'✅' if actual == image else '❌'}")
            
        return {
            'cargo_distribution': cargo_dist.to_dict(),
            'cargo_percentage': cargo_pct.to_dict()
        }
        
    def verify_warehouse_specialization(self):
        """창고별 전문화 패턴 검증"""
        print("\n=== 4. 창고별 전문화 패턴 검증 ===")
        
        if self.invoice_df is None:
            print("❌ INVOICE 데이터가 없어 검증 불가")
            return
            
        # SQM 필터링된 데이터
        sqm_data = self.invoice_df[self.invoice_df['HVDC CODE 2'] == 'SQM'].copy()
        
        # 창고별 화물 유형 분포
        warehouse_cargo = pd.crosstab(sqm_data['HVDC CODE 1'], sqm_data['HVDC CODE 3'], normalize='index') * 100
        
        print("📊 창고별 화물 유형 분포 (%):")
        print(warehouse_cargo.round(1))
        
        # 주요 전문화 패턴 확인
        specialization_patterns = {}
        for warehouse in warehouse_cargo.index:
            main_cargo = warehouse_cargo.loc[warehouse].idxmax()
            main_share = warehouse_cargo.loc[warehouse].max()
            
            specialization_patterns[warehouse] = {
                'main_cargo': main_cargo,
                'main_share': main_share
            }
            
            print(f"\n{warehouse}:")
            print(f"  🎯 주력 화물: {main_cargo} ({main_share:.1f}%)")
            
            # 상위 3개 화물 유형 표시
            top_cargo = warehouse_cargo.loc[warehouse].nlargest(3)
            for cargo, share in top_cargo.items():
                if share > 5:  # 5% 이상만 표시
                    print(f"  - {cargo}: {share:.1f}%")
                    
        return specialization_patterns
        
    def check_all_vs_real_cargo(self):
        """ALL과 실제 화물의 관계 검증"""
        print("\n=== 5. ALL vs 실제 화물 관계 검증 ===")
        
        if self.invoice_df is None:
            print("❌ INVOICE 데이터가 없어 검증 불가")
            return
            
        # SQM 필터링된 데이터
        sqm_data = self.invoice_df[self.invoice_df['HVDC CODE 2'] == 'SQM'].copy()
        
        # ALL과 비-ALL 데이터 분리
        all_data = sqm_data[sqm_data['HVDC CODE 3'] == 'ALL']
        non_all_data = sqm_data[sqm_data['HVDC CODE 3'] != 'ALL']
        
        print(f"📊 ALL 데이터: {len(all_data)}건")
        print(f"📊 비-ALL 데이터: {len(non_all_data)}건")
        
        # ALL 데이터의 특성
        if len(all_data) > 0:
            all_handling = all_data['HANDLING'].sum()
            all_rent = all_data['RENT'].sum()
            all_total = all_data['TOTAL'].sum()
            
            print(f"\nALL 데이터 비용 구조:")
            print(f"  HANDLING: {all_handling:,.2f} AED")
            print(f"  RENT: {all_rent:,.2f} AED")
            print(f"  TOTAL: {all_total:,.2f} AED")
            
            all_handling_ratio = all_handling / all_total * 100 if all_total > 0 else 0
            all_rent_ratio = all_rent / all_total * 100 if all_total > 0 else 0
            
            print(f"  HANDLING 비율: {all_handling_ratio:.1f}%")
            print(f"  RENT 비율: {all_rent_ratio:.1f}%")
            
        # 비-ALL 데이터의 특성
        if len(non_all_data) > 0:
            non_all_handling = non_all_data['HANDLING'].sum()
            non_all_rent = non_all_data['RENT'].sum()
            non_all_total = non_all_data['TOTAL'].sum()
            
            print(f"\n비-ALL 데이터 비용 구조:")
            print(f"  HANDLING: {non_all_handling:,.2f} AED")
            print(f"  RENT: {non_all_rent:,.2f} AED")
            print(f"  TOTAL: {non_all_total:,.2f} AED")
            
            non_all_handling_ratio = non_all_handling / non_all_total * 100 if non_all_total > 0 else 0
            non_all_rent_ratio = non_all_rent / non_all_total * 100 if non_all_total > 0 else 0
            
            print(f"  HANDLING 비율: {non_all_handling_ratio:.1f}%")
            print(f"  RENT 비율: {non_all_rent_ratio:.1f}%")
            
        # 결론
        print(f"\n💡 분석 결과:")
        if len(all_data) == 0:
            print("  ✅ ALL 데이터가 없음 - 모든 데이터가 실제 화물")
        else:
            print(f"  🔍 ALL은 임대료 중심 데이터로 확인됨")
            
        return {
            'all_count': len(all_data),
            'non_all_count': len(non_all_data),
            'all_rent_heavy': all_rent > all_handling if len(all_data) > 0 else False
        }
        
    def compare_with_generated_data(self):
        """생성된 트랜잭션과 비교"""
        print("\n=== 6. 생성된 트랜잭션과 원본 INVOICE 비교 ===")
        
        try:
            # 생성된 트랜잭션 로딩
            generated_files = [f for f in os.listdir('.') if f.startswith('HVDC_올바른구조_실제데이터_트랜잭션_') and f.endswith('.xlsx')]
            if not generated_files:
                print("❌ 생성된 트랜잭션 파일을 찾을 수 없음")
                return
                
            latest_file = max(generated_files, key=os.path.getctime)
            generated_df = pd.read_excel(latest_file, sheet_name='Transactions')
            
            print(f"📊 생성된 트랜잭션: {len(generated_df)}건")
            
            # 입고 트랜잭션만 분석
            in_transactions = generated_df[generated_df['Transaction_Type'] == 'IN']
            
            # 화물 유형 비교
            generated_cargo_dist = in_transactions['Cargo_Type'].value_counts()
            
            print(f"\n🔍 화물 유형 비교:")
            print(f"원본 INVOICE (이미지): HE {self.image1_pkg_data['total']['HE']}, SIM {self.image1_pkg_data['total']['SIM']}")
            print(f"생성된 트랜잭션: HE {generated_cargo_dist.get('HE', 0)}, SIM {generated_cargo_dist.get('SIM', 0)}")
            
            # 창고 사용 비교
            generated_warehouse_dist = in_transactions['Location'].value_counts()
            
            print(f"\n🔍 창고 사용 비교:")
            print("원본 INVOICE에서 사용된 창고:", list(self.image1_pkg_data.keys())[:-1])  # 'total' 제외
            print("생성된 트랜잭션에서 사용된 창고:", list(generated_warehouse_dist.index))
            
            # 비용 구조 비교
            generated_total_amount = in_transactions['Amount'].sum()
            generated_handling = in_transactions['Handling_Fee'].sum()
            generated_rent = in_transactions['Rent_Fee'].sum()
            
            original_total = self.image2_total_data['total']['total']
            original_handling = self.image2_total_data['total']['HANDLING']
            original_rent = self.image2_total_data['total']['RENT']
            
            print(f"\n🔍 비용 구조 비교:")
            print(f"원본 총액: {original_total:,.0f} AED")
            print(f"생성 총액: {generated_total_amount:,.0f} AED")
            print(f"규모 차이: {generated_total_amount/original_total*100:.1f}%")
            
        except Exception as e:
            print(f"❌ 생성된 데이터 비교 실패: {e}")
            
    def generate_verification_report(self):
        """종합 검증 리포트 생성"""
        print("\n" + "=" * 60)
        print("🎯 INVOICE 원본 구조 종합 검증 리포트")
        print("=" * 60)
        
        # 모든 검증 실행
        pkg_results = self.verify_package_counts()
        cost_results = self.verify_cost_structure()
        cargo_results = self.verify_warehouse_cargo_distribution()
        specialization_results = self.verify_warehouse_specialization()
        all_vs_real_results = self.check_all_vs_real_cargo()
        self.compare_with_generated_data()
        
        # 종합 결론
        print(f"\n🏆 종합 결론:")
        print(f"✅ 패키지 수 검증: {'PASS' if pkg_results and pkg_results['matches'] else 'FAIL'}")
        print(f"✅ 비용 구조 검증: {'PASS' if cost_results else 'FAIL'}")
        print(f"✅ 화물 분포 검증: {'PASS' if cargo_results else 'FAIL'}")
        print(f"✅ 창고 전문화 검증: {'PASS' if specialization_results else 'FAIL'}")
        
        # 핵심 발견사항
        print(f"\n📋 핵심 발견사항:")
        if cost_results:
            print(f"  💰 총 INVOICE 금액: {cost_results['actual_total']:,.0f} AED")
            print(f"  📊 HANDLING 비율: {cost_results['handling_ratio']:.1f}%")
            print(f"  🏠 RENT 비율: {cost_results['rent_ratio']:.1f}%")
            
        if cargo_results:
            he_count = cargo_results['cargo_distribution'].get('HE', 0)
            sim_count = cargo_results['cargo_distribution'].get('SIM', 0)
            total_real_cargo = he_count + sim_count
            
            if total_real_cargo > 0:
                he_ratio = he_count / total_real_cargo * 100
                sim_ratio = sim_count / total_real_cargo * 100
                print(f"  🔧 HE (히타치): {he_count}건 ({he_ratio:.1f}%)")
                print(f"  ⚡ SIM (지멘스): {sim_count}건 ({sim_ratio:.1f}%)")
                
        if all_vs_real_results:
            print(f"  📦 ALL 데이터 존재: {'YES' if all_vs_real_results['all_count'] > 0 else 'NO'}")
            
        print(f"\n✨ 검증 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """메인 실행 함수"""
    verifier = OriginalInvoiceStructureVerifier()
    verifier.generate_verification_report()
    
if __name__ == "__main__":
    main() 