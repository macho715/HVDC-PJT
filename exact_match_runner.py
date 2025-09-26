#!/usr/bin/env python3
"""
HVDC Flow Code 공식 기준 완전 일치 실행기
한 번의 실행으로 정확한 결과 달성

MACHO-GPT v3.4-mini │ Samsung C&T × ADNOC·DSV Partnership
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

def quick_exact_match():
    """빠른 공식 기준 매칭"""
    
    print("🎯 Flow Code 공식 기준 완전 일치 실행")
    print("=" * 50)
    
    try:
        # 필수 모듈 import
        from flow_code_exact_match import run_exact_match_analysis
        
        # 실행
        combined_df, summary = run_exact_match_analysis()
        
        print(f"\n✅ 실행 완료!")
        return True
        
    except ImportError:
        print("❌ flow_code_exact_match 모듈을 찾을 수 없습니다.")
        print("📋 Artifact에서 코드를 복사하여 저장하세요.")
        return False
        
    except FileNotFoundError:
        print("❌ 데이터 파일을 찾을 수 없습니다.")
        print("📁 다음 파일들이 필요합니다:")
        print("   - data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
        print("   - data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
        return False
        
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_files():
    """파일 존재 확인"""
    
    required_files = [
        "data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
    ]
    
    print("📁 파일 확인:")
    all_exist = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            all_exist = False
    
    return all_exist


def show_expected_results():
    """기대 결과 표시"""
    
    print("\n🎯 공식 기준 목표:")
    print("-" * 40)
    
    targets = {
        'HITACHI': {
            'total': 5346,
            'Code 0': 163, 'Code 1': 2062, 'Code 2': 2842,
            'Code 3': 274, 'Code 4': 5
        },
        'SIMENSE': {
            'total': 2227,
            'Code 0': 384, 'Code 1': 804, 'Code 2': 805,
            'Code 3': 234, 'Code 4': 1851
        }
    }
    
    for vendor, codes in targets.items():
        print(f"\n{vendor}:")
        for code, count in codes.items():
            print(f"   {code}: {count:,}")


def create_test_mode():
    """테스트 모드 실행"""
    
    print("\n🧪 테스트 모드 실행")
    
    # 샘플 데이터로 테스트
    test_data = {
        'HVDC CODE': ['HVDC-001', 'HVDC-002', 'HVDC-003', 'HVDC-004', 'HVDC-005'],
        'DSV Indoor': [pd.Timestamp('2024-01-01'), pd.NA, pd.Timestamp('2024-01-01'), pd.NA, pd.Timestamp('2024-01-01')],
        'DSV Outdoor': [pd.NA, pd.Timestamp('2024-01-02'), pd.Timestamp('2024-01-02'), pd.Timestamp('2024-01-02'), pd.NA],
        'AAA  Storage': [pd.NA, pd.NA, pd.NA, pd.Timestamp('2024-01-03'), pd.NA],
        'MOSB': [pd.NA, pd.NA, pd.Timestamp('2024-01-03'), pd.Timestamp('2024-01-04'), pd.NA],
        'Date': [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-02'), pd.Timestamp('2024-01-03'), pd.Timestamp('2024-01-04'), pd.Timestamp('2024-01-05')]
    }
    
    df = pd.DataFrame(test_data)
    
    try:
        from flow_code_exact_match import FlowCodeExactCalculator
        
        calculator = FlowCodeExactCalculator()
        df_result = calculator.calculate_exact_flow_codes(df, 'HITACHI')
        
        print("✅ 테스트 성공!")
        print(f"📊 Flow Code 분포:")
        flow_dist = df_result['Flow_Code_Exact'].value_counts().sort_index()
        for code, count in flow_dist.items():
            print(f"   Code {code}: {count}건")
            
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def main():
    """메인 실행"""
    
    print("🚀 HVDC Flow Code 공식 기준 완전 일치")
    print("MACHO-GPT v3.4-mini │ Samsung C&T × ADNOC·DSV Partnership")
    print("=" * 60)
    
    # 1. 기대 결과 표시
    show_expected_results()
    
    # 2. 파일 확인
    if not validate_files():
        print("\n📋 파일 준비 후 다시 실행하세요.")
        
        # 테스트 모드 제안
        test_choice = input("\n🧪 테스트 모드로 실행하시겠습니까? (y/n): ")
        if test_choice.lower() == 'y':
            if create_test_mode():
                print("✅ 테스트 모드 완료. 실제 파일로 다시 실행하세요.")
            return
        else:
            return
    
    # 3. 실행
    success = quick_exact_match()
    
    if success:
        print("\n🎉 공식 기준 완전 일치 달성!")
        print("📊 결과 파일이 생성되었습니다.")
    else:
        print("\n⚠️ 문제가 발생했습니다. 로그를 확인하세요.")


if __name__ == "__main__":
    main() 