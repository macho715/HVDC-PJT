#!/usr/bin/env python3
"""
창고별 재고 계산 검증 스크립트
"""

def verify_stock_calculation():
    print('🔍 **창고별 재고 계산 검증**')
    print('='*70)
    
    # 실제 데이터
    warehouse_data = {
        'DSV Al Markaz': {'type': 'Central', 'in_qty': 1742, 'out_qty': 1467, 'stock_qty': 165},
        'DSV Indoor': {'type': 'Indoor', 'in_qty': 1032, 'out_qty': 766, 'stock_qty': 200},
        'DSV Outdoor': {'type': 'Outdoor', 'in_qty': 2032, 'out_qty': 1614, 'stock_qty': 289},
        'MOSB': {'type': 'Offshore', 'in_qty': 475, 'out_qty': 325, 'stock_qty': 111}
    }
    
    # MACHO v2.8.4 로직의 stock_ratio (코드에서 확인)
    stock_ratios = {
        'Indoor': 0.20,    # 20% - 높은 재고율 (보관 중심)
        'Outdoor': 0.15,   # 15% - 중간 재고율 (빠른 회전)
        'Central': 0.10,   # 10% - 낮은 재고율 (허브 기능)
        'Offshore': 0.25   # 25% - 매우 높은 재고율 (버퍼 기능)
    }
    
    print('📊 **재고 계산 방식 분석**')
    print('-'*70)
    print('MACHO v2.8.4 로직: stock_qty = in_qty × stock_ratio')
    print('단순 계산: stock_qty = in_qty - out_qty')
    print()
    
    for wh_name, data in warehouse_data.items():
        wh_type = data['type']
        in_qty = data['in_qty']
        out_qty = data['out_qty']
        actual_stock = data['stock_qty']
        
        # MACHO 로직에 따른 계산
        stock_ratio = stock_ratios[wh_type]
        macho_stock = int(in_qty * stock_ratio)
        
        # 단순 계산
        simple_stock = in_qty - out_qty
        
        print(f'🏢 **{wh_name} ({wh_type})**')
        print(f'   입고량: {in_qty:,}건')
        print(f'   출고량: {out_qty:,}건')
        print(f'   실제 재고: {actual_stock:,}건')
        print(f'   ')
        print(f'   MACHO 로직: {in_qty:,} × {stock_ratio:.0%} = {macho_stock:,}건')
        print(f'   단순 계산: {in_qty:,} - {out_qty:,} = {simple_stock:,}건')
        print(f'   ')
        print(f'   실제 vs MACHO: {actual_stock:,} vs {macho_stock:,} (차이: {abs(actual_stock-macho_stock)})')
        print(f'   실제 vs 단순: {actual_stock:,} vs {simple_stock:,} (차이: {abs(actual_stock-simple_stock)})')
        
        # 정확성 확인
        if actual_stock == macho_stock:
            print(f'   ✅ MACHO 로직과 완전 일치')
        elif abs(actual_stock - macho_stock) <= 5:
            print(f'   ✅ MACHO 로직과 거의 일치 (오차 ±5)')
        else:
            print(f'   ❌ MACHO 로직과 불일치')
        
        print()
    
    # 전체 재고 검증
    print('📈 **전체 재고 검증**')
    print('-'*70)
    
    total_actual = sum(data['stock_qty'] for data in warehouse_data.values())
    total_in = sum(data['in_qty'] for data in warehouse_data.values())
    total_out = sum(data['out_qty'] for data in warehouse_data.values())
    
    print(f'전체 입고: {total_in:,}건')
    print(f'전체 출고: {total_out:,}건')
    print(f'전체 재고: {total_actual:,}건')
    print(f'전체 재고율: {total_actual/total_in*100:.1f}%')
    print()
    
    # 창고별 재고율 분석
    print('📊 **창고별 실제 재고율**')
    print('-'*70)
    for wh_name, data in warehouse_data.items():
        actual_ratio = data['stock_qty'] / data['in_qty'] * 100
        expected_ratio = stock_ratios[data['type']] * 100
        print(f'{wh_name}: 실제 {actual_ratio:.1f}% vs 예상 {expected_ratio:.0f}%')

if __name__ == "__main__":
    verify_stock_calculation() 