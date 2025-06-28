from hvdc_engine import SimpleHVDCEngine, Warehouse

engine = SimpleHVDCEngine()
warehouses = [
    Warehouse("DSV Indoor", "Indoor", 10000, 6000, 50),
    Warehouse("DSV Outdoor", "Outdoor", 15000, 9000, 30),
    Warehouse("MOSB", "Outdoor", 8000, 4000, 35),
    Warehouse("AGI", "Site", 5000, 2000, 0)
]
for wh in warehouses:
    engine.add_warehouse(wh)
print("샘플 창고 데이터 추가 완료")