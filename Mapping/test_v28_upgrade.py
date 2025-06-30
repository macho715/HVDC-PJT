#!/usr/bin/env python3
"""
HVDC v2.8 업그레이드 테스트 스크립트
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics
Purpose: Pre_Arrival, OffshoreBase, logistics_flow_code 기능 검증
"""

import sys
import pandas as pd
import json
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 로컬 모듈 임포트
try:
    from mapping_utils import (
        MappingManager, 
        classify_storage_type, 
        calc_flow_code,
        add_logistics_flow_code_to_dataframe
    )
except ImportError as e:
    logger.error(f"모듈 임포트 실패: {e}")
    sys.exit(1)

def test_v28_json_rules():
    """v2.8 JSON 규칙 파일 테스트"""
    logger.info("🧪 v2.8 JSON 규칙 파일 테스트 시작")
    
    # v2.8 파일 존재 확인
    v28_file = Path("mapping_rules_v2.8.json")
    if not v28_file.exists():
        logger.error("❌ mapping_rules_v2.8.json 파일이 없습니다")
        return False
    
    try:
        with open(v28_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        # 필수 필드 검증
        required_fields = [
            'warehouse_classification', 
            'logistics_flow_definition',
            'v28_features'
        ]
        
        for field in required_fields:
            if field not in rules:
                logger.error(f"❌ 필수 필드 누락: {field}")
                return False
        
        # Pre_Arrival, OffshoreBase 확인
        warehouse_class = rules['warehouse_classification']
        if 'Pre_Arrival' not in warehouse_class:
            logger.error("❌ Pre_Arrival 분류 누락")
            return False
        
        if 'OffshoreBase' not in warehouse_class:
            logger.error("❌ OffshoreBase 분류 누락")
            return False
        
        # logistics_flow_definition 확인
        flow_def = rules['logistics_flow_definition']
        expected_codes = ['0', '1', '2', '3', '4']
        for code in expected_codes:
            if code not in flow_def:
                logger.error(f"❌ 물류 흐름 코드 누락: {code}")
                return False
        
        logger.info("✅ v2.8 JSON 규칙 파일 검증 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ JSON 파일 검증 실패: {e}")
        return False

def test_storage_type_classification():
    """창고 분류 기능 테스트"""
    logger.info("🧪 창고 분류 기능 테스트 시작")
    
    # 테스트 케이스
    test_cases = [
        # (입력, 예상 출력)
        ("PRE ARRIVAL", "Pre_Arrival"),
        ("INBOUND_PENDING", "Pre_Arrival"),
        ("NOT_YET_RECEIVED", "Pre_Arrival"),
        ("MOSB", "OffshoreBase"),
        ("MARINE BASE", "OffshoreBase"),
        ("OFFSHORE BASE", "OffshoreBase"),
        ("DSV Indoor", "Indoor"),
        ("DSV Outdoor", "Outdoor"),
        ("AGI", "Site"),
        ("Unknown Location", "Unknown")
    ]
    
    manager = MappingManager()
    success_count = 0
    
    for location, expected in test_cases:
        result = manager.classify_storage_type(location)
        if result == expected:
            logger.info(f"✅ {location} → {result}")
            success_count += 1
        else:
            logger.error(f"❌ {location} → {result} (예상: {expected})")
    
    success_rate = success_count / len(test_cases) * 100
    logger.info(f"🎯 창고 분류 성공률: {success_rate:.1f}% ({success_count}/{len(test_cases)})")
    
    return success_rate >= 90

def test_logistics_flow_code():
    """물류 흐름 코드 계산 테스트"""
    logger.info("🧪 물류 흐름 코드 계산 테스트 시작")
    
    # 테스트 케이스
    test_cases = [
        # (레코드, 예상 코드)
        ({"Status": "PRE ARRIVAL"}, 0),
        ({"Status": "INBOUND_PENDING"}, 0),
        ({"Status": "Active"}, 1),  # Port→Site
        ({"Status": "Active", "Warehouse": "DSV Indoor"}, 2),  # Port→WH→Site
        ({"Status": "Active", "Warehouse": "DSV Indoor", "OffshoreBase": "MOSB"}, 3),  # Port→WH→MOSB→Site
        ({"Status": "Active", "Warehouse": "DSV Indoor", "OffshoreBase": "MOSB", "ExtraWH": "Extra"}, 4),  # 4-step
    ]
    
    success_count = 0
    
    for record, expected in test_cases:
        result = calc_flow_code(record)
        if result == expected:
            logger.info(f"✅ {record} → Code {result}")
            success_count += 1
        else:
            logger.error(f"❌ {record} → Code {result} (예상: {expected})")
    
    success_rate = success_count / len(test_cases) * 100
    logger.info(f"🎯 물류 흐름 코드 성공률: {success_rate:.1f}% ({success_count}/{len(test_cases)})")
    
    return success_rate >= 90

def test_dataframe_integration():
    """DataFrame 통합 기능 테스트"""
    logger.info("🧪 DataFrame 통합 기능 테스트 시작")
    
    # 테스트 데이터 생성
    test_data = pd.DataFrame({
        'Case_No': ['HE001', 'HE002', 'HE003', 'HE004', 'HE005'],
        'Location': ['PRE ARRIVAL', 'DSV Indoor', 'MOSB', 'AGI', 'DSV Outdoor'],
        'Status': ['PRE ARRIVAL', 'Active', 'Active', 'Active', 'Active'],
        'Qty': [10, 20, 15, 25, 30],
        'Amount': [1000, 2000, 1500, 2500, 3000]
    })
    
    try:
        # Storage Type 추가
        manager = MappingManager()
        df_with_storage = manager.add_storage_type_to_dataframe(test_data)
        
        logger.info("✅ Storage Type 추가 완료")
        logger.info(f"   Storage Type 분포: {df_with_storage['Storage_Type'].value_counts().to_dict()}")
        
        # Logistics Flow Code 추가
        df_complete = add_logistics_flow_code_to_dataframe(df_with_storage)
        
        logger.info("✅ Logistics Flow Code 추가 완료") 
        logger.info(f"   Flow Code 분포: {df_complete['Logistics_Flow_Code'].value_counts().to_dict()}")
        
        # 기본 검증: 컬럼이 제대로 추가되었는지 확인
        required_columns = ['Storage_Type', 'Logistics_Flow_Code']
        for col in required_columns:
            if col not in df_complete.columns:
                logger.error(f"❌ 필수 컬럼 누락: {col}")
                return False
        
        # 데이터 타입 검증
        if not pd.api.types.is_integer_dtype(df_complete['Logistics_Flow_Code']):
            logger.error("❌ Logistics_Flow_Code가 정수 타입이 아닙니다")
            return False
        
        # 값 범위 검증
        flow_codes = df_complete['Logistics_Flow_Code'].values
        if not all(0 <= code <= 4 for code in flow_codes):
            logger.error("❌ Flow Code 범위 오류 (0-4 범위 벗어남)")
            return False
        
        # Pre_Arrival 케이스 검증
        pre_arrival_rows = df_complete[df_complete['Storage_Type'] == 'Pre_Arrival']
        if not all(pre_arrival_rows['Logistics_Flow_Code'] == 0):
            logger.error("❌ Pre_Arrival 아이템의 Flow Code가 0이 아닙니다")
            return False
        
        logger.info("✅ DataFrame 통합 기능 테스트 완료")
        logger.info(f"📊 최종 결과:")
        logger.info(f"   총 레코드: {len(df_complete)}")
        logger.info(f"   Storage Type 분포: {df_complete['Storage_Type'].value_counts().to_dict()}")
        logger.info(f"   Flow Code 분포: {df_complete['Logistics_Flow_Code'].value_counts().to_dict()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DataFrame 통합 테스트 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    logger.info("🚀 HVDC v2.8 업그레이드 테스트 시작")
    logger.info("=" * 60)
    
    tests = [
        ("JSON 규칙 파일", test_v28_json_rules),
        ("창고 분류 기능", test_storage_type_classification),
        ("물류 흐름 코드", test_logistics_flow_code),
        ("DataFrame 통합", test_dataframe_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 {test_name} 테스트 실행...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"📊 {test_name}: {status}")
        except Exception as e:
            logger.error(f"❌ {test_name} 테스트 오류: {e}")
            results.append((test_name, False))
    
    # 최종 결과
    logger.info("\n" + "=" * 60)
    logger.info("📊 최종 테스트 결과:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = passed / total * 100
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n🎯 전체 성공률: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 90:
        logger.info("🎉 v2.8 업그레이드 테스트 성공!")
        logger.info("🔧 **추천 명령어:**")
        logger.info("/logi_master [v2.8 Pre_Arrival + OffshoreBase 매핑 시스템 활성화]")
        logger.info("/switch_mode PRIME [물류 흐름 코드 자동 계산 모드 전환]")
        logger.info("/visualize_data [v2.8 확장 기능 대시보드 생성]")
        return True
    else:
        logger.error("❌ v2.8 업그레이드 테스트 실패")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 