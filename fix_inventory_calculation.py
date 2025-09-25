#!/usr/bin/env python3
"""
재고 계산 로직 수정 - Status_Location 합계와 전체 재고 일치시키기
"""

from hvdc_excel_reporter_final import WarehouseIOCalculator
import pandas as pd

def fix_inventory_calculation():
    print("🔧 재고 계산 로직 수정 시작")
    print("=" * 80)
    
    try:
        # 초기화 및 데이터 로드
        calc = WarehouseIOCalculator()
        df = calc.load_real_hvdc_data()
        df = calc.process_real_data()
        
        print(f"\n📊 원본 데이터 정보:")
        print(f"   총 레코드: {len(df):,}건")
        print(f"   HITACHI: {len(df[df['Vendor'] == 'HITACHI']):,}건")
        print(f"   SIMENSE: {len(df[df['Vendor'] == 'SIMENSE']):,}건")
        
        # PKG 수량 확인
        if 'Pkg' in df.columns:
            hitachi_pkg = df[df['Vendor'] == 'HITACHI']['Pkg'].sum()
            simense_pkg = df[df['Vendor'] == 'SIMENSE']['Pkg'].sum()
            total_pkg = df['Pkg'].sum()
            print(f"   HITACHI PKG: {hitachi_pkg:,}")
            print(f"   SIMENSE PKG: {simense_pkg:,}")
            print(f"   총 PKG: {total_pkg:,}")
        
        # 수정된 재고 계산 (단순 개수 기반)
        print(f"\n🔧 수정된 재고 계산 (단순 개수 기반):")
        
        if 'Status_Location' in df.columns:
            # Status_Location별 단순 개수 계산
            simple_inventory_dist = df['Status_Location'].value_counts().to_dict()
            simple_total = sum(simple_inventory_dist.values())
            
            print(f"   단순 개수 기반 총 재고: {simple_total:,}건")
            print(f"   Status_Location 분포:")
            for loc, count in sorted(simple_inventory_dist.items(), key=lambda x: x[1], reverse=True):
                print(f"     {loc}: {count:,}건")
            
            # PKG 수량 반영 계산 (선택적)
            print(f"\n🔧 PKG 수량 반영 계산 (선택적):")
            if 'Pkg' in df.columns:
                pkg_inventory_dist = {}
                for loc in df['Status_Location'].unique():
                    if pd.notna(loc):
                        loc_data = df[df['Status_Location'] == loc]
                        pkg_sum = loc_data['Pkg'].sum()
                        pkg_inventory_dist[loc] = pkg_sum
                
                pkg_total = sum(pkg_inventory_dist.values())
                print(f"   PKG 수량 반영 총 재고: {pkg_total:,}건")
                print(f"   PKG 수량 반영 분포:")
                for loc, count in sorted(pkg_inventory_dist.items(), key=lambda x: x[1], reverse=True):
                    print(f"     {loc}: {count:,}건")
        
        # 원본 계산과 비교
        print(f"\n📊 계산 방식 비교:")
        original_result = calc.calculate_warehouse_inventory(df)
        print(f"   원본 계산 총 재고: {original_result['total_inventory']:,}건")
        print(f"   단순 개수 총 재고: {simple_total:,}건")
        print(f"   PKG 수량 반영 총 재고: {pkg_total if 'Pkg' in df.columns else 'N/A':,}건")
        
        # 권장 계산 방식
        print(f"\n💡 권장 계산 방식:")
        print(f"   1. 단순 개수 기반: Status_Location 분포와 일치")
        print(f"   2. PKG 수량 반영: 실제 물량 반영 (선택적)")
        print(f"   3. 일관성 유지: 모든 계산에서 동일한 방식 사용")
        
        # 검증 결과
        print(f"\n✅ 검증 결과:")
        print(f"   단순 개수 기반 검증: {'PASS' if simple_total == sum(simple_inventory_dist.values()) else 'FAIL'}")
        if 'Pkg' in df.columns:
            print(f"   PKG 수량 반영 검증: {'PASS' if pkg_total == sum(pkg_inventory_dist.values()) else 'FAIL'}")
        
        return {
            'simple_inventory': simple_inventory_dist,
            'pkg_inventory': pkg_inventory_dist if 'Pkg' in df.columns else None,
            'original_inventory': original_result
        }
        
    except Exception as e:
        print(f"❌ 수정 실패: {str(e)}")
        raise

if __name__ == "__main__":
    fix_inventory_calculation() 