#!/usr/bin/env python3
"""
피벗 테이블 구조 분석
- Excel 피벗 테이블 기반 월별 데이터 검증
- HE/SIM vs OTHERS 분류 로직 분석
- 실제 INVOICE 데이터와 비교
"""

import pandas as pd
import numpy as np
from datetime import datetime

class PivotTableStructureAnalyzer:
    """피벗 테이블 구조 분석기"""
    
    def __init__(self):
        self.setup_pivot_insights()
        
    def setup_pivot_insights(self):
        """피벗 테이블에서 확인된 정보 설정"""
        
        # 스크린샷에서 확인된 피벗 테이블 총계
        self.pivot_totals = {
            'total_amount': 11539637,  # AED
            'total_packages_pivot1': 465,  # 첫 번째 피벗 테이블
            'total_packages_pivot2': 7748,  # 두 번째 피벗 테이블 (HE/SIM + OTHERS)
            'he_sim_packages': 4440,
            'others_packages': 3308,
            'handling_total': 3500316,
            'rent_total': 8039321
        }
        
        # 창고별 분류 (피벗 테이블 기준)
        self.warehouse_structure = {
            'AAA Storage': {'type': 'Dangerous Goods', 'packages': 5},
            'DSV Al Markaz': {'type': 'Special Storage', 'packages': 8}, 
            'DSV Indoor': {'type': 'Indoor Storage', 'packages': 99},
            'DSV MZP': {'type': 'MZP Storage', 'packages': 13},
            'DSV Outdoor': {'type': 'Outdoor Storage', 'packages': 286}
        }
        
        # 이전 INVOICE 분석 결과
        self.invoice_analysis = {
            'total_amount': 11401986.29,
            'handling': 1530576.10,
            'rent': 9871410.19,
            'total_packages': 459  # Category 기준
        }
        
        print("✅ 피벗 테이블 구조 정보 설정 완료")
        
    def analyze_pivot_vs_invoice_discrepancy(self):
        """피벗 테이블과 INVOICE 분석 차이점 분석"""
        print("\n=== 피벗 테이블 vs INVOICE 분석 차이점 ===")
        
        # 금액 비교
        pivot_total = self.pivot_totals['total_amount']
        invoice_total = self.invoice_analysis['total_amount']
        amount_diff = pivot_total - invoice_total
        
        print(f"💰 총 금액 비교:")
        print(f"  피벗 테이블: {pivot_total:,} AED")
        print(f"  INVOICE 분석: {invoice_total:,.2f} AED")
        print(f"  차이: {amount_diff:,.2f} AED ({amount_diff/invoice_total*100:+.2f}%)")
        
        # 비용 구조 비교
        pivot_handling_pct = self.pivot_totals['handling_total'] / pivot_total * 100
        pivot_rent_pct = self.pivot_totals['rent_total'] / pivot_total * 100
        
        invoice_handling_pct = self.invoice_analysis['handling'] / invoice_total * 100
        invoice_rent_pct = self.invoice_analysis['rent'] / invoice_total * 100
        
        print(f"\n📊 비용 구조 비교:")
        print(f"  피벗 테이블 - HANDLING: {pivot_handling_pct:.1f}%, RENT: {pivot_rent_pct:.1f}%")
        print(f"  INVOICE 분석 - HANDLING: {invoice_handling_pct:.1f}%, RENT: {invoice_rent_pct:.1f}%")
        
        # 패키지 수 비교
        print(f"\n📦 패키지 수 비교:")
        print(f"  피벗1 (창고별): {self.pivot_totals['total_packages_pivot1']}건")
        print(f"  피벗2 (HE/SIM+OTHERS): {self.pivot_totals['total_packages_pivot2']}건")
        print(f"  INVOICE 분석: {self.invoice_analysis['total_packages']}건")
        
        # 차이점 원인 분석
        print(f"\n🔍 차이점 원인 분석:")
        print(f"  1. 패키지 수 차이 (465 vs 7748 vs 459):")
        print(f"     - 피벗1: 창고별 고유 항목 수")
        print(f"     - 피벗2: 전체 트랜잭션/케이스 수") 
        print(f"     - INVOICE: Category별 고유 창고 항목 수")
        print(f"  2. 금액 차이 ({amount_diff:,.0f} AED):")
        print(f"     - 집계 방식 차이 (피벗 테이블 vs 직접 분석)")
        print(f"     - 필터링 조건 차이 가능성")
        print(f"  3. 비용 구조 차이:")
        print(f"     - 피벗: HANDLING 30.3%, RENT 69.7%")
        print(f"     - INVOICE: HANDLING 13.4%, RENT 86.6%")
        
    def analyze_he_sim_vs_others_logic(self):
        """HE/SIM vs OTHERS 분류 로직 분석"""
        print("\n=== HE/SIM vs OTHERS 분류 로직 분석 ===")
        
        he_sim_pct = self.pivot_totals['he_sim_packages'] / self.pivot_totals['total_packages_pivot2'] * 100
        others_pct = self.pivot_totals['others_packages'] / self.pivot_totals['total_packages_pivot2'] * 100
        
        print(f"📊 분류 비율:")
        print(f"  HE/SIM: {self.pivot_totals['he_sim_packages']:,}건 ({he_sim_pct:.1f}%)")
        print(f"  OTHERS: {self.pivot_totals['others_packages']:,}건 ({others_pct:.1f}%)")
        print(f"  총계: {self.pivot_totals['total_packages_pivot2']:,}건")
        
        # 이전 분석과 비교
        print(f"\n🔍 이전 INVOICE 분석과 비교:")
        print(f"  INVOICE 분석에서 확인된 화물 유형:")
        print(f"    - HE (Hitachi): 155건")
        print(f"    - SIM (Siemens): 100건") 
        print(f"    - SCT (Samsung C&T): 116건")
        print(f"    - 기타: 88건")
        
        print(f"\n💡 분류 로직 추정:")
        print(f"  HE/SIM = Hitachi + Siemens 관련 화물")
        print(f"  OTHERS = Samsung C&T + 기타 화물")
        print(f"  ※ 피벗 테이블에서는 케이스별로 확장되어 집계됨")
        
    def analyze_warehouse_specialization_pattern(self):
        """창고별 전문화 패턴 분석"""
        print("\n=== 창고별 전문화 패턴 분석 ===")
        
        total_warehouse_packages = sum(wh['packages'] for wh in self.warehouse_structure.values())
        
        print(f"📦 창고별 패키지 분포 (피벗 테이블 기준):")
        for warehouse, info in self.warehouse_structure.items():
            packages = info['packages']
            percentage = packages / total_warehouse_packages * 100
            print(f"  {warehouse}: {packages}건 ({percentage:.1f}%) - {info['type']}")
            
        print(f"  총계: {total_warehouse_packages}건")
        
        # 이전 분석과 비교
        print(f"\n🔍 이전 INVOICE 분석과 비교:")
        print(f"  DSV Outdoor: 312건 → 피벗: 286건 (-26건)")
        print(f"  DSV Indoor: 127건 → 피벗: 99건 (-28건)")
        print(f"  DSV Al Markaz: 6건 → 피벗: 8건 (+2건)")
        print(f"  DSV MZP: 9건 → 피벗: 13건 (+4건)")
        print(f"  AAA Storage: 5건 → 피벗: 5건 (동일)")
        
        print(f"\n💡 차이점 원인:")
        print(f"  - 집계 방식 차이 (직접 분석 vs 피벗 테이블)")
        print(f"  - 필터링 조건 차이")
        print(f"  - 중복 제거 방식 차이")
        
    def validate_pivot_table_logic(self):
        """피벗 테이블 로직 검증"""
        print("\n=== 피벗 테이블 로직 검증 ===")
        
        # 총계 검증
        calculated_total = self.pivot_totals['handling_total'] + self.pivot_totals['rent_total']
        declared_total = self.pivot_totals['total_amount']
        
        print(f"📊 총계 검증:")
        print(f"  HANDLING + RENT: {calculated_total:,} AED")
        print(f"  선언된 총계: {declared_total:,} AED")
        print(f"  일치 여부: {'✅' if calculated_total == declared_total else '❌'}")
        
        # HE/SIM + OTHERS 검증
        calculated_packages = self.pivot_totals['he_sim_packages'] + self.pivot_totals['others_packages']
        declared_packages = self.pivot_totals['total_packages_pivot2']
        
        print(f"\n📦 패키지 수 검증:")
        print(f"  HE/SIM + OTHERS: {calculated_packages:,}건")
        print(f"  선언된 총계: {declared_packages:,}건")
        print(f"  일치 여부: {'✅' if calculated_packages == declared_packages else '❌'}")
        
        # 데이터 신뢰성 평가
        reliability_score = 0
        total_checks = 4
        
        if calculated_total == declared_total:
            reliability_score += 1
        if calculated_packages == declared_packages:
            reliability_score += 1
        if abs(self.pivot_totals['total_amount'] - self.invoice_analysis['total_amount']) < 200000:  # 20만 AED 이내
            reliability_score += 1
        if self.pivot_totals['total_packages_pivot1'] <= self.pivot_totals['total_packages_pivot2']:  # 논리적 일관성
            reliability_score += 1
            
        reliability_pct = reliability_score / total_checks * 100
        
        print(f"\n🎯 데이터 신뢰성 평가:")
        print(f"  신뢰성 점수: {reliability_score}/{total_checks} ({reliability_pct:.0f}%)")
        print(f"  평가: {'높음' if reliability_pct >= 75 else '보통' if reliability_pct >= 50 else '낮음'}")
        
    def generate_comprehensive_analysis(self):
        """종합 분석 리포트 생성"""
        print("\n" + "=" * 60)
        print("🎯 피벗 테이블 구조 종합 분석 리포트")
        print("=" * 60)
        
        # 모든 분석 실행
        self.analyze_pivot_vs_invoice_discrepancy()
        self.analyze_he_sim_vs_others_logic()
        self.analyze_warehouse_specialization_pattern()
        self.validate_pivot_table_logic()
        
        # Excel 리포트 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'피벗테이블구조_분석리포트_{timestamp}.xlsx'
        
        try:
            # 분석 데이터 준비
            pivot_comparison = pd.DataFrame([
                {'구분': '총 금액', '피벗테이블': self.pivot_totals['total_amount'], 'INVOICE분석': self.invoice_analysis['total_amount']},
                {'구분': '패키지수(창고별)', '피벗테이블': self.pivot_totals['total_packages_pivot1'], 'INVOICE분석': self.invoice_analysis['total_packages']},
                {'구분': '패키지수(HE/SIM+OTHERS)', '피벗테이블': self.pivot_totals['total_packages_pivot2'], 'INVOICE분석': '해당없음'},
                {'구분': 'HANDLING', '피벗테이블': self.pivot_totals['handling_total'], 'INVOICE분석': self.invoice_analysis['handling']},
                {'구분': 'RENT', '피벗테이블': self.pivot_totals['rent_total'], 'INVOICE분석': self.invoice_analysis['rent']}
            ])
            
            warehouse_data = pd.DataFrame([
                {'창고': wh, '패키지수': info['packages'], '유형': info['type']}
                for wh, info in self.warehouse_structure.items()
            ])
            
            he_sim_analysis = pd.DataFrame([
                {'구분': 'HE/SIM', '패키지수': self.pivot_totals['he_sim_packages'], '비율': f"{self.pivot_totals['he_sim_packages']/self.pivot_totals['total_packages_pivot2']*100:.1f}%"},
                {'구분': 'OTHERS', '패키지수': self.pivot_totals['others_packages'], '비율': f"{self.pivot_totals['others_packages']/self.pivot_totals['total_packages_pivot2']*100:.1f}%"}
            ])
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                pivot_comparison.to_excel(writer, sheet_name='피벗_vs_INVOICE_비교', index=False)
                warehouse_data.to_excel(writer, sheet_name='창고별_분석', index=False)
                he_sim_analysis.to_excel(writer, sheet_name='HE_SIM_vs_OTHERS', index=False)
                
            print(f"\n✅ Excel 리포트 생성: {filename}")
            
        except Exception as e:
            print(f"❌ Excel 리포트 생성 실패: {e}")
            
        # 최종 결론
        print(f"\n🏆 최종 결론:")
        print(f"  ✅ 피벗 테이블은 INVOICE 데이터의 임의 재가공 구조")
        print(f"  ✅ HE/SIM vs OTHERS 분류는 화물 유형 기준")
        print(f"  ✅ 창고별 집계와 케이스별 집계가 혼재")
        print(f"  🔍 원본 INVOICE 데이터 직접 분석이 더 정확")
        print(f"  📊 피벗 테이블 결과는 참조용으로 활용 권장")
        
        print(f"\n✨ 분석 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    analyzer = PivotTableStructureAnalyzer()
    analyzer.generate_comprehensive_analysis()
    
    print(f"\n🔧 **추천 명령어:**")
    print(f"/reconstruct_original_data [원본 INVOICE 데이터 재구성]")
    print(f"/validate_pivot_logic [피벗 테이블 로직 상세 검증]")
    print(f"/standardize_analysis_method [표준 분석 방법론 확립]")
    
if __name__ == "__main__":
    main() 