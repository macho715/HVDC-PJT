import pandas as pd
from datetime import datetime
from warehouse_io_calculator import WarehouseIOCalculator

# 테스트 데이터 - 모든 필수 창고 컬럼 포함
test_data = pd.DataFrame({
    'Item': ['T001', 'T002', 'T003', 'T004', 'T005'],
    'DSV Indoor': [datetime(2024, 1, 15), None, datetime(2024, 2, 1), None, None],
    'DSV Outdoor': [None, datetime(2024, 1, 20), None, None, None],
    'DSV Al Markaz': [None, None, None, datetime(2024, 2, 5), None],
    'DSV MZP': [None, None, None, None, None],
    'AAA  Storage': [None, None, None, None, None],
    'AAA Storage': [None, None, None, None, None],
    'Hauler Indoor': [None, None, None, None, None],
    'MOSB': [None, None, None, None, datetime(2024, 2, 10)],
    'DHL Warehouse': [None, None, None, None, None],
    'MIR': [None, None, None, None, datetime(2024, 3, 1)],
    'SHU': [None, None, None, None, None],
    'DAS': [None, None, None, None, None],
    'AGI': [None, None, None, None, None]
})

calc = WarehouseIOCalculator()

print("=== WarehouseIOCalculator 테스트 ===")
print()

# 입고 계산
inbound = calc.calculate_warehouse_inbound(test_data)
print("=== 입고 계산 결과 ===")
print(f"총 입고: {inbound['total_inbound']}건")
print(f"창고별: {inbound['by_warehouse']}")
print(f"월별: {inbound['by_month']}")
print()

# 출고 계산
outbound = calc.calculate_warehouse_outbound(test_data)
print("=== 출고 계산 결과 ===")
print(f"총 출고: {outbound['total_outbound']}건")
print(f"창고별 출고: {outbound['by_warehouse']}")
print(f"현장별 출고: {outbound['by_site']}")
print()

# 재고 계산
inventory = calc.calculate_warehouse_inventory(test_data)
print("=== 재고 계산 결과 ===")
print(f"총 재고: {inventory['total_inventory']}건")
print(f"창고별: {inventory['by_warehouse']}")
print(f"상태별: {inventory['by_status']}")
print()

# 종합 리포트
report = calc.generate_monthly_report(test_data)
print("=== 종합 리포트 ===")
print(f"요약: {report['summary']}")
print(f"창고별 성과: {report['warehouse_performance']}")
print()

# 직배송 테스트
print("=== 직배송 테스트 ===")
direct_test_data = pd.DataFrame({
    'Item': ['D001', 'D002', 'D003', 'D004'],
    'DSV Indoor': [None, datetime(2024, 1, 15), None, None],
    'DSV Outdoor': [None, None, None, None],
    'DSV Al Markaz': [None, None, None, None],
    'MOSB': [None, None, None, None],
    'MIR': [datetime(2024, 1, 10), datetime(2024, 1, 20), None, None],
    'SHU': [None, None, datetime(2024, 1, 25), None],
    'DAS': [None, None, None, None],
    'AGI': [None, None, None, datetime(2024, 1, 30)]
})

direct_delivery = calc.calculate_direct_delivery(direct_test_data)
print(f"총 직배송: {direct_delivery['total_direct']}건")
print(f"현장별 직배송: {direct_delivery['by_site']}")
print(f"월별 직배송: {direct_delivery['by_month']}")
print(f"직배송 항목 수: {len(direct_delivery['direct_items'])}")
print()

print("✅ 모든 테스트 완료!")