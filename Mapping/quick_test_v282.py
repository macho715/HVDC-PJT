#!/usr/bin/env python3
"""
HVDC v2.8.2 간단 검증 테스트
Author: MACHO-GPT v3.4-mini
"""

import sys
import pandas as pd

try:
    from calc_flow_code_v2 import FlowCodeCalculatorV2
    print("✅ calc_flow_code_v2 모듈 로드 성공")
except ImportError as e:
    print(f"❌ 모듈 로드 실패: {e}")
    sys.exit(1)

def test_clean_str():
    """전각공백 처리 테스트"""
    print("\n🧪 전각공백 처리 테스트...")
    calc = FlowCodeCalculatorV2()
    
    test_cases = [
        ("DSV　Indoor", "DSV Indoor"),
        ("MOSB　Base", "MOSB Base"),
        ("  Normal  ", "Normal"),
        ("", ""),
        (None, "")
    ]
    
    passed = 0
    for input_val, expected in test_cases:
        result = calc._clean_str(input_val)
        if result == expected:
            print(f"   ✅ '{input_val}' → '{result}'")
            passed += 1
        else:
            print(f"   ❌ '{input_val}' → '{result}' (기대: '{expected}')")
    
    print(f"   성공률: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    return passed == len(test_cases)

def test_flow_code_calculation():
    """Flow Code 계산 테스트"""
    print("\n🧪 Flow Code 계산 테스트...")
    calc = FlowCodeCalculatorV2()
    
    test_cases = [
        # Code 0: Pre Arrival
        {"Location": "PRE ARRIVAL", "expected": 0},
        
        # Code 1: Port→Site (직송)
        {"Location": "AGI", "expected": 1},
        
        # Code 2: Port→WH→Site
        {"Location": "DSV Indoor", "DSV Indoor": "2025-01-15", "expected": 2},
        
        # Code 3: Port→WH→MOSB→Site  
        {"Location": "DSV Indoor", "DSV Indoor": "2025-01-15", "MOSB": "2025-01-20", "expected": 3},
        
        # Code 4: Port→WH→WH→MOSB→Site
        {"Location": "DSV Indoor", "DSV Indoor": "2025-01-15", "DSV Outdoor": "2025-01-16", "MOSB": "2025-01-20", "expected": 4},
        
        # 전각공백 테스트
        {"Location": "DSV　Indoor", "DSV Indoor": "DSV　Indoor", "MOSB": "MOSB　Base", "expected": 3}
    ]
    
    passed = 0
    for i, test_case in enumerate(test_cases):
        expected = test_case.pop("expected")
        result = calc.calc_flow_code_v2(test_case)
        actual = result["flow_code"]
        
        if actual == expected:
            print(f"   ✅ Test {i+1}: Code {actual} (기대: {expected})")
            passed += 1
        else:
            print(f"   ❌ Test {i+1}: Code {actual} (기대: {expected})")
            print(f"      Route: {result['route']}")
    
    print(f"   성공률: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    return passed == len(test_cases)

def test_dataframe_processing():
    """DataFrame 처리 테스트"""
    print("\n🧪 DataFrame 처리 테스트...")
    calc = FlowCodeCalculatorV2()
    
    # 테스트 데이터 생성
    test_data = [
        {"Case_No": "TEST001", "Location": "PRE ARRIVAL"},
        {"Case_No": "TEST002", "Location": "AGI"},
        {"Case_No": "TEST003", "Location": "DSV　Indoor", "DSV Indoor": "2025-01-15"},
        {"Case_No": "TEST004", "Location": "DSV Indoor", "DSV Indoor": "2025-01-15", "MOSB": "2025-01-20"},
        {"Case_No": "TEST005", "Location": "DSV Indoor", "DSV Indoor": "2025-01-15", "DSV Outdoor": "2025-01-16", "MOSB": "2025-01-20"}
    ]
    
    df = pd.DataFrame(test_data)
    print(f"   원본 데이터: {len(df)}건")
    
    # Flow Code 계산
    df_result = calc.add_flow_code_v2_to_dataframe(df)
    
    # 결과 확인
    expected_codes = [0, 1, 2, 3, 4]
    actual_codes = df_result["Logistics_Flow_Code_V2"].tolist()
    
    success = actual_codes == expected_codes
    print(f"   예상 코드: {expected_codes}")
    print(f"   실제 코드: {actual_codes}")
    print(f"   ✅ 일치: {success}")
    
    return success

def main():
    print("🚀 HVDC v2.8.2 간단 검증 시작...")
    
    tests = [
        ("전각공백 처리", test_clean_str),
        ("Flow Code 계산", test_flow_code_calculation),
        ("DataFrame 처리", test_dataframe_processing)
    ]
    
    passed_tests = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} 테스트 통과")
                passed_tests += 1
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 오류: {e}")
    
    total_tests = len(tests)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📊 검증 결과: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 v2.8.2 패치 검증 성공!")
        return True
    else:
        print("⚠️ 일부 테스트 실패")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 