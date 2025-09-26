#!/usr/bin/env python3
"""
HVDC WAREHOUSE_INVOICE_.xlsx 재검증
- HVDC CODE 2 = SQM, MANPOWER 필터링
- HVDC CODE 1 = 창고 이름
- HVDC CODE 5 = RENT/HANDLING 구분
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

class InvoiceRevalidator:
    """INVOICE 재검증기"""
    
    def __init__(self):
        self.load_invoice_data()
        
    def load_invoice_data(self):
        """INVOICE 데이터 로딩"""
        invoice_paths = [
            'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx',
            'HVDC WAREHOUSE_INVOICE_.xlsx',
            'hvdc_ontology_system/data/HVDC WAREHOUSE_INVOICE.xlsx'
        ]
        
        self.invoice_df = None
        for path in invoice_paths:
            try:
                if os.path.exists(path):
                    self.invoice_df = pd.read_excel(path)
                    print(f"✅ INVOICE 데이터 로딩 성공: {path}")
                    print(f"📊 총 레코드 수: {len(self.invoice_df)}건")
                    break
            except Exception as e:
                print(f"❌ {path} 로딩 실패: {e}")
                
        if self.invoice_df is None:
            print("❌ INVOICE 파일을 찾을 수 없습니다.")
            
    def analyze_hvdc_code_structure(self):
        """HVDC CODE 구조 분석"""
        print("\n=== HVDC CODE 구조 분석 ===")
        
        if self.invoice_df is None:
            return
            
        print("📋 컬럼 목록:")
        for i, col in enumerate(self.invoice_df.columns):
            print(f"  {i+1}. {col}")
            
        # HVDC CODE 2 분석
        if 'HVDC CODE 2' in self.invoice_df.columns:
            code2_counts = self.invoice_df['HVDC CODE 2'].value_counts()
            print(f"\n📊 HVDC CODE 2 분포:")
            for code, count in code2_counts.items():
                print(f"  {code}: {count:,}건")
                
        # HVDC CODE 1 분석 (창고명)
        if 'HVDC CODE 1' in self.invoice_df.columns:
            code1_counts = self.invoice_df['HVDC CODE 1'].value_counts()
            print(f"\n🏠 HVDC CODE 1 (창고명) 분포:")
            for warehouse, count in code1_counts.items():
                print(f"  {warehouse}: {count:,}건")
                
        # HVDC CODE 5 분석 (RENT/HANDLING)
        if 'HVDC CODE 5' in self.invoice_df.columns:
            code5_counts = self.invoice_df['HVDC CODE 5'].value_counts()
            print(f"\n💰 HVDC CODE 5 (비용구분) 분포:")
            for cost_type, count in code5_counts.items():
                print(f"  {cost_type}: {count:,}건")
                
    def apply_new_filtering(self):
        """새로운 필터링 조건 적용"""
        print("\n=== 새로운 필터링 조건 적용 ===")
        
        if self.invoice_df is None:
            return None
            
        # HVDC CODE 2로 필터링: SQM, MANPOWER
        if 'HVDC CODE 2' in self.invoice_df.columns:
            filtered_df = self.invoice_df[
                self.invoice_df['HVDC CODE 2'].isin(['SQM', 'MANPOWER'])
            ].copy()
            
            print(f"📊 필터링 결과:")
            print(f"  전체 데이터: {len(self.invoice_df):,}건")
            print(f"  SQM + MANPOWER: {len(filtered_df):,}건")
            print(f"  필터링 비율: {len(filtered_df)/len(self.invoice_df)*100:.1f}%")
            
            # 필터링된 데이터의 HVDC CODE 2 분포
            if len(filtered_df) > 0:
                code2_filtered = filtered_df['HVDC CODE 2'].value_counts()
                print(f"\n필터링된 데이터의 HVDC CODE 2 분포:")
                for code, count in code2_filtered.items():
                    print(f"  {code}: {count:,}건")
                    
            return filtered_df
        else:
            print("❌ HVDC CODE 2 컬럼이 없습니다.")
            return None
            
    def analyze_warehouse_cost_structure(self, filtered_df):
        """창고별 비용 구조 분석"""
        print("\n=== 창고별 비용 구조 분석 ===")
        
        if filtered_df is None or len(filtered_df) == 0:
            print("❌ 필터링된 데이터가 없습니다.")
            return
            
        # 창고별, 비용유형별 집계
        if all(col in filtered_df.columns for col in ['HVDC CODE 1', 'HVDC CODE 5', 'TOTAL']):
            
            # 피벗 테이블 생성
            pivot_table = pd.pivot_table(
                filtered_df,
                values='TOTAL',
                index='HVDC CODE 1',
                columns='HVDC CODE 5',
                aggfunc='sum',
                fill_value=0
            )
            
            print("📊 창고별 비용 구조 (AED):")
            print(pivot_table.round(2))
            
            # 총계 계산
            if 'HANDLING' in pivot_table.columns and 'RENT' in pivot_table.columns:
                pivot_table['총계'] = pivot_table['HANDLING'] + pivot_table['RENT']
                pivot_table['HANDLING_비율'] = (pivot_table['HANDLING'] / pivot_table['총계'] * 100).round(1)
                pivot_table['RENT_비율'] = (pivot_table['RENT'] / pivot_table['총계'] * 100).round(1)
                
                print(f"\n📊 창고별 비용 비율:")
                for warehouse in pivot_table.index:
                    handling_pct = pivot_table.loc[warehouse, 'HANDLING_비율']
                    rent_pct = pivot_table.loc[warehouse, 'RENT_비율']
                    total_amount = pivot_table.loc[warehouse, '총계']
                    print(f"  {warehouse}: HANDLING {handling_pct}%, RENT {rent_pct}%, 총액 {total_amount:,.0f} AED")
                    
                # 전체 합계
                total_handling = pivot_table['HANDLING'].sum()
                total_rent = pivot_table['RENT'].sum()
                grand_total = total_handling + total_rent
                
                print(f"\n🎯 전체 합계:")
                print(f"  HANDLING: {total_handling:,.2f} AED ({total_handling/grand_total*100:.1f}%)")
                print(f"  RENT: {total_rent:,.2f} AED ({total_rent/grand_total*100:.1f}%)")
                print(f"  총계: {grand_total:,.2f} AED")
                
                return {
                    'pivot_table': pivot_table,
                    'total_handling': total_handling,
                    'total_rent': total_rent,
                    'grand_total': grand_total
                }
        else:
            print("❌ 필요한 컬럼이 없습니다.")
            return None
            
    def analyze_cargo_distribution(self, filtered_df):
        """화물 유형별 분포 분석"""
        print("\n=== 화물 유형별 분포 분석 ===")
        
        if filtered_df is None or len(filtered_df) == 0:
            return
            
        # HVDC CODE 3 (화물 유형) 분석
        if 'HVDC CODE 3' in filtered_df.columns:
            cargo_counts = filtered_df['HVDC CODE 3'].value_counts()
            cargo_pct = filtered_df['HVDC CODE 3'].value_counts(normalize=True) * 100
            
            print("📦 화물 유형별 분포:")
            for cargo_type in cargo_counts.index:
                count = cargo_counts[cargo_type]
                percentage = cargo_pct[cargo_type]
                print(f"  {cargo_type}: {count:,}건 ({percentage:.1f}%)")
                
            # 창고별 화물 유형 분포
            if 'HVDC CODE 1' in filtered_df.columns:
                warehouse_cargo = pd.crosstab(
                    filtered_df['HVDC CODE 1'], 
                    filtered_df['HVDC CODE 3']
                )
                
                print(f"\n🏠 창고별 화물 유형 분포:")
                print(warehouse_cargo)
                
                # 비율 계산
                warehouse_cargo_pct = pd.crosstab(
                    filtered_df['HVDC CODE 1'], 
                    filtered_df['HVDC CODE 3'],
                    normalize='index'
                ) * 100
                
                print(f"\n🏠 창고별 화물 유형 비율 (%):")
                print(warehouse_cargo_pct.round(1))
                
                return {
                    'cargo_counts': cargo_counts.to_dict(),
                    'warehouse_cargo': warehouse_cargo,
                    'warehouse_cargo_pct': warehouse_cargo_pct
                }
        else:
            print("❌ HVDC CODE 3 컬럼이 없습니다.")
            return None
            
    def compare_with_previous_analysis(self, results):
        """이전 분석과 비교"""
        print("\n=== 이전 분석과 비교 ===")
        
        # 이미지에서 확인된 데이터 (이전 분석)
        previous_total = 11539636.89
        previous_handling = 3500315.90
        previous_rent = 8039320.99
        
        if results and 'grand_total' in results:
            current_total = results['grand_total']
            current_handling = results['total_handling']
            current_rent = results['total_rent']
            
            print(f"💰 총액 비교:")
            print(f"  이전 (SQM만): {previous_total:,.2f} AED")
            print(f"  현재 (SQM+MANPOWER): {current_total:,.2f} AED")
            print(f"  차이: {current_total - previous_total:,.2f} AED ({(current_total/previous_total-1)*100:+.1f}%)")
            
            print(f"\n🔧 HANDLING 비교:")
            print(f"  이전: {previous_handling:,.2f} AED ({previous_handling/previous_total*100:.1f}%)")
            print(f"  현재: {current_handling:,.2f} AED ({current_handling/current_total*100:.1f}%)")
            
            print(f"\n🏠 RENT 비교:")
            print(f"  이전: {previous_rent:,.2f} AED ({previous_rent/previous_total*100:.1f}%)")
            print(f"  현재: {current_rent:,.2f} AED ({current_rent/current_total*100:.1f}%)")
            
            # MANPOWER의 영향 추정
            manpower_impact = current_total - previous_total
            print(f"\n👥 MANPOWER 추가 영향:")
            print(f"  추가 금액: {manpower_impact:,.2f} AED")
            print(f"  전체 대비: {manpower_impact/current_total*100:.1f}%")
            
    def generate_corrected_excel_report(self, filtered_df, results):
        """수정된 Excel 리포트 생성"""
        print("\n=== 수정된 Excel 리포트 생성 ===")
        
        if filtered_df is None or results is None:
            print("❌ 리포트 생성에 필요한 데이터가 없습니다.")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'HVDC_INVOICE_재검증리포트_{timestamp}.xlsx'
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                
                # 1. 필터링된 원본 데이터
                filtered_df.to_excel(writer, sheet_name='필터링된_원본데이터', index=False)
                
                # 2. 창고별 비용 구조
                if 'pivot_table' in results:
                    results['pivot_table'].to_excel(writer, sheet_name='창고별_비용구조')
                    
                # 3. 화물 유형별 분포
                if 'cargo_counts' in results:
                    cargo_summary = pd.DataFrame([
                        {'화물유형': k, '건수': v, '비율': f"{v/sum(results['cargo_counts'].values())*100:.1f}%"}
                        for k, v in results['cargo_counts'].items()
                    ])
                    cargo_summary.to_excel(writer, sheet_name='화물유형별_분포', index=False)
                    
                # 4. 창고별 화물 분포
                if 'warehouse_cargo' in results:
                    results['warehouse_cargo'].to_excel(writer, sheet_name='창고별_화물분포')
                    results['warehouse_cargo_pct'].to_excel(writer, sheet_name='창고별_화물비율')
                    
                # 5. 요약 정보
                summary_data = []
                if 'grand_total' in results:
                    summary_data = [
                        {'구분': '총 금액', '값': f"{results['grand_total']:,.2f} AED"},
                        {'구분': 'HANDLING 금액', '값': f"{results['total_handling']:,.2f} AED"},
                        {'구분': 'RENT 금액', '값': f"{results['total_rent']:,.2f} AED"},
                        {'구분': 'HANDLING 비율', '값': f"{results['total_handling']/results['grand_total']*100:.1f}%"},
                        {'구분': 'RENT 비율', '값': f"{results['total_rent']/results['grand_total']*100:.1f}%"},
                        {'구분': '필터링 조건', '값': 'HVDC CODE 2 = SQM, MANPOWER'},
                        {'구분': '생성 시간', '값': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    ]
                    
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='요약정보', index=False)
                
            print(f"✅ Excel 리포트 생성 완료: {filename}")
            
        except Exception as e:
            print(f"❌ Excel 리포트 생성 실패: {e}")
            
    def run_complete_revalidation(self):
        """완전한 재검증 실행"""
        print("🎯 HVDC WAREHOUSE_INVOICE_.xlsx 완전 재검증")
        print("=" * 60)
        
        # 1. 구조 분석
        self.analyze_hvdc_code_structure()
        
        # 2. 새로운 필터링 적용
        filtered_df = self.apply_new_filtering()
        
        # 3. 창고별 비용 구조 분석
        cost_results = self.analyze_warehouse_cost_structure(filtered_df)
        
        # 4. 화물 분포 분석
        cargo_results = self.analyze_cargo_distribution(filtered_df)
        
        # 5. 결과 통합
        combined_results = {}
        if cost_results:
            combined_results.update(cost_results)
        if cargo_results:
            combined_results.update(cargo_results)
            
        # 6. 이전 분석과 비교
        self.compare_with_previous_analysis(cost_results)
        
        # 7. Excel 리포트 생성
        self.generate_corrected_excel_report(filtered_df, combined_results)
        
        print(f"\n✨ 재검증 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return combined_results

def main():
    """메인 실행 함수"""
    revalidator = InvoiceRevalidator()
    results = revalidator.run_complete_revalidation()
    
    if results:
        print(f"\n🔧 **추천 명령어:**")
        print(f"/analyze_transaction_accuracy [새로운 필터링 기반 정확도 검증]")
        print(f"/update_generator_config [MANPOWER 데이터 반영 설정 업데이트]")
        print(f"/compare_cost_ratios [HANDLING/RENT 비율 상세 비교]")
    
if __name__ == "__main__":
    main() 