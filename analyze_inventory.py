#!/usr/bin/env python3
"""
/logi_master analyze_inventory - 전체 재고 분석 및 현재 상태 확인
"""

from hvdc_excel_reporter_final import WarehouseIOCalculator
import pandas as pd

def main():
    print("🔍 /logi_master analyze_inventory - 전체 재고 분석 시작")
    print("=" * 80)
    
    try:
        # 초기화 및 데이터 로드
        calc = WarehouseIOCalculator()
        df = calc.load_real_hvdc_data()
        df = calc.process_real_data()
        
        # 재고 계산
        inventory_result = calc.calculate_warehouse_inventory(df)
        
        # 결과 출력
        print(f"\n📊 전체 재고 분석 결과:")
        print(f"   총 재고: {inventory_result['total_inventory']:,}건")
        
        print(f"\n📍 Status_Location별 분포:")
        location_dist = inventory_result['status_location_distribution']
        for loc, count in sorted(location_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"   {loc}: {count:,}건")
        
        # 창고/현장 구분
        warehouse_locations = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'AAA  Storage', 
                             'Hauler Indoor', 'MOSB', 'DHL Warehouse', 'Status_WAREHOUSE']
        site_locations = ['AGI', 'DAS', 'MIR', 'SHU']
        
        warehouse_count = sum(location_dist.get(loc, 0) for loc in warehouse_locations)
        site_count = sum(location_dist.get(loc, 0) for loc in site_locations)
        pre_arrival_count = location_dist.get('Pre Arrival', 0)
        
        print(f"\n🏢 창고/현장 구분:")
        print(f"   창고 재고: {warehouse_count:,}건")
        print(f"   현장 재고: {site_count:,}건")
        print(f"   Pre Arrival: {pre_arrival_count:,}건")
        
        # KPI 검증
        print(f"\n✅ KPI 검증:")
        print(f"   Status_Location 합계 = 전체 재고: {'PASS' if sum(location_dist.values()) == inventory_result['total_inventory'] else 'FAIL'}")
        print(f"   재고 음수 없음: {'PASS' if inventory_result['total_inventory'] >= 0 else 'FAIL'}")
        
        # 벤더별 분포
        vendor_dist = df['Vendor'].value_counts()
        print(f"\n🏭 벤더별 분포:")
        for vendor, count in vendor_dist.items():
            print(f"   {vendor}: {count:,}건")
        
        print(f"\n🎉 재고 분석 완료!")
        
    except Exception as e:
        print(f"❌ 재고 분석 실패: {str(e)}")
        raise

if __name__ == "__main__":
    main() 