#!/usr/bin/env python3
"""
재고 검증 실패 디버깅 - Status_Location 합계와 전체 재고 불일치 문제 해결
"""

from hvdc_excel_reporter_final import WarehouseIOCalculator
import pandas as pd

def debug_inventory_calculation():
    print("🔍 재고 검증 실패 디버깅 시작")
    print("=" * 80)
    
    try:
        # 초기화 및 데이터 로드
        calc = WarehouseIOCalculator()
        df = calc.load_real_hvdc_data()
        df = calc.process_real_data()
        
        # 재고 계산
        inventory_result = calc.calculate_warehouse_inventory(df)
        
        print(f"\n📊 기본 재고 정보:")
        print(f"   총 재고 (total_inventory): {inventory_result['total_inventory']:,}건")
        
        # Status_Location 분포 상세 분석
        location_dist = inventory_result['status_location_distribution']
        total_by_status = sum(location_dist.values())
        
        print(f"\n📍 Status_Location별 상세 분석:")
        print(f"   Status_Location 합계: {total_by_status:,}건")
        print(f"   전체 재고: {inventory_result['total_inventory']:,}건")
        print(f"   차이: {inventory_result['total_inventory'] - total_by_status:,}건")
        
        print(f"\n📋 Status_Location별 세부 내역:")
        for loc, count in sorted(location_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"   {loc}: {count:,}건")
        
        # 원본 데이터 Status_Location 분포 확인
        print(f"\n🔍 원본 데이터 Status_Location 분포:")
        if 'Status_Location' in df.columns:
            original_dist = df['Status_Location'].value_counts()
            print(f"   원본 Status_Location 합계: {original_dist.sum():,}건")
            print(f"   원본 Status_Location 분포:")
            for loc, count in original_dist.items():
                print(f"     {loc}: {count:,}건")
        
        # 재고 계산 로직 검증
        print(f"\n🧮 재고 계산 로직 검증:")
        
        # 월별 재고 계산 확인
        if 'inventory_by_month' in inventory_result:
            print(f"   월별 재고 계산 포함: YES")
            sample_month = list(inventory_result['inventory_by_month'].keys())[0]
            sample_month_total = sum(inventory_result['inventory_by_month'][sample_month].values())
            print(f"   샘플 월({sample_month}) 총 재고: {sample_month_total:,}건")
        
        # 위치별 재고 계산 확인
        if 'inventory_by_location' in inventory_result:
            print(f"   위치별 재고 계산 포함: YES")
            location_total = sum(inventory_result['inventory_by_location'].values())
            print(f"   위치별 재고 합계: {location_total:,}건")
        
        # 문제 원인 분석
        print(f"\n🔍 문제 원인 분석:")
        
        # 1. PKG 수량 반영 확인
        if 'Pkg' in df.columns:
            total_pkg = df['Pkg'].sum()
            print(f"   1. PKG 수량 총합: {total_pkg:,}")
            print(f"      PKG 수량이 재고 계산에 반영됨: {'YES' if total_pkg > len(df) else 'NO'}")
        
        # 2. 중복 계산 확인
        print(f"   2. 중복 계산 가능성: 재고 계산에서 PKG 수량이 중복 반영될 수 있음")
        
        # 3. 계산 방식 차이
        print(f"   3. 계산 방식 차이:")
        print(f"      - Status_Location 분포: 단순 개수 계산")
        print(f"      - 전체 재고: PKG 수량 반영 누적 계산")
        
        # 해결 방안 제시
        print(f"\n💡 해결 방안:")
        print(f"   1. Status_Location 분포도 PKG 수량 반영하여 계산")
        print(f"   2. 또는 전체 재고를 단순 개수로 계산")
        print(f"   3. 계산 로직 통일화 필요")
        
        # 수정된 계산 시도
        print(f"\n🔧 수정된 계산 시도:")
        
        # PKG 수량 반영한 Status_Location 분포 계산
        if 'Status_Location' in df.columns and 'Pkg' in df.columns:
            pkg_weighted_dist = {}
            for loc in df['Status_Location'].unique():
                if pd.notna(loc):
                    loc_data = df[df['Status_Location'] == loc]
                    pkg_sum = loc_data['Pkg'].sum()
                    pkg_weighted_dist[loc] = pkg_sum
            
            pkg_weighted_total = sum(pkg_weighted_dist.values())
            print(f"   PKG 수량 반영 Status_Location 합계: {pkg_weighted_total:,}건")
            print(f"   전체 재고와의 차이: {inventory_result['total_inventory'] - pkg_weighted_total:,}건")
            
            if abs(inventory_result['total_inventory'] - pkg_weighted_total) < 100:
                print(f"   ✅ PKG 수량 반영 시 거의 일치함!")
            else:
                print(f"   ❌ 여전히 차이가 있음")
        
        print(f"\n🎯 결론:")
        print(f"   Status_Location 합계와 전체 재고의 차이는 PKG 수량 반영 방식의 차이로 인한 것으로 보임")
        print(f"   재고 계산 로직을 통일화하여 해결 가능")
        
    except Exception as e:
        print(f"❌ 디버깅 실패: {str(e)}")
        raise

if __name__ == "__main__":
    debug_inventory_calculation() 