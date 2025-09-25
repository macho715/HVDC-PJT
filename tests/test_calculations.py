"""
Unit tests for the calculation module.
"""
import pandas as pd
from src.calculation.calculator import WarehouseCalculator

def test_same_date_warehouse_transfer():
    """
    Tests the detection of same-day warehouse transfers.
    """
    print("\n🧪 Testing same-day warehouse transfers...")
    
    test_data = pd.DataFrame({
        'Item_ID': [1, 2, 3],
        'Pkg': [1, 2, 1],
        'DSV Indoor': ['2024-06-01', '2024-06-02', pd.NaT],
        'DSV Al Markaz': ['2024-06-01', '2024-06-03', '2024-06-01'],
        'Status_Location': ['DSV Al Markaz', 'DSV Al Markaz', 'DSV Al Markaz']
    })
    
    test_data['DSV Indoor'] = pd.to_datetime(test_data['DSV Indoor'])
    test_data['DSV Al Markaz'] = pd.to_datetime(test_data['DSV Al Markaz'])
    
    calculator = WarehouseCalculator()
    
    # Test 1: Same-day transfer
    transfers = calculator.detect_same_date_warehouse_transfer(test_data.iloc[0])
    assert len(transfers) == 1
    assert transfers[0]['from_warehouse'] == 'DSV Indoor'
    assert transfers[0]['to_warehouse'] == 'DSV Al Markaz'
    print("✅ Test 1 passed: Same-day transfer detected.")
    
    # Test 2: Different dates
    transfers = calculator.detect_same_date_warehouse_transfer(test_data.iloc[1])
    assert len(transfers) == 0
    print("✅ Test 2 passed: No transfer on different dates.")
    
    # Test 3: Missing date
    transfers = calculator.detect_same_date_warehouse_transfer(test_data.iloc[2])
    assert len(transfers) == 0
    print("✅ Test 3 passed: No transfer with missing date.")
    
    print("🎉 All tests passed for same-day warehouse transfers.")

if __name__ == "__main__":
    test_same_date_warehouse_transfer()