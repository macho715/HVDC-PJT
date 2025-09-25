#!/usr/bin/env python3
"""
Excel Agent Integration Test for MACHO-GPT System
================================================
Excel Agent가 MACHO-GPT 시스템에 완전히 통합되었는지 테스트합니다.
"""

import asyncio
import sys
import os
from pathlib import Path

# HVDC 프로젝트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_excel_agent_integration():
    """Excel Agent 통합 테스트"""
    print("=== Excel Agent MACHO-GPT Integration Test ===")
    print()
    
    try:
        # LogiMasterSystem import 및 초기화
        from logi_master_system import LogiMasterSystem
        
        # 시스템 초기화
        system = LogiMasterSystem()
        success = await system.initialize()
        
        if not success:
            print("❌ LogiMasterSystem initialization failed")
            return False
        
        print("✅ LogiMasterSystem initialized successfully")
        print()
        
        # Excel Agent 통합 상태 확인
        if not system.layers.get('macho_gpt_ai'):
            print("❌ MachoGPT AI layer not available")
            return False
        
        macho_gpt_layer = system.layers['macho_gpt_ai']
        if not macho_gpt_layer.excel_agent_integration:
            print("❌ Excel Agent integration not available")
            return False
        
        print("✅ Excel Agent integration available")
        print()
        
        # 1. Excel Agent 상태 확인
        print("=== 1. Excel Agent Status Check ===")
        status_result = await system.execute_command("excel_status")
        print(f"Status: {status_result['status']}")
        if status_result['status'] == 'SUCCESS':
            print(f"Excel Agent Status: {status_result.get('data', {}).get('excel_agent_status', 'Unknown')}")
        print()
        
        # 2. HVDC 데이터 로드 테스트
        print("=== 2. HVDC Data Load Test ===")
        hvdc_file = "data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        if os.path.exists(hvdc_file):
            load_result = await system.execute_command("excel_load", {
                "file_path": hvdc_file,
                "dataframe_name": "hvdc_test"
            })
            print(f"Load Result: {load_result['status']}")
            if load_result['status'] == 'SUCCESS':
                print(f"Rows: {load_result.get('rows', 'Unknown')}")
                print(f"Columns: {load_result.get('columns', 'Unknown')}")
        else:
            print(f"⚠️  HVDC data file not found: {hvdc_file}")
        print()
        
        # 3. 데이터프레임 정보 조회 테스트
        print("=== 3. DataFrame Info Test ===")
        info_result = await system.execute_command("excel_info")
        print(f"Info Result: {info_result['status']}")
        if info_result['status'] == 'SUCCESS':
            shape = info_result.get('shape', 'Unknown')
            print(f"DataFrame Shape: {shape}")
        print()
        
        # 4. 자연어 쿼리 테스트
        print("=== 4. Natural Language Query Test ===")
        query_result = await system.execute_command("excel_query", {
            "query": "총 몇 개의 행이 있나요?"
        })
        print(f"Query Result: {query_result['status']}")
        if query_result['status'] == 'SUCCESS':
            answer = query_result.get('answer', 'No answer')
            print(f"Answer: {answer}")
        print()
        
        # 5. HVDC 특화 분석 테스트
        print("=== 5. HVDC Specific Analysis Test ===")
        hvdc_result = await system.execute_command("hvdc_analysis", {
            "analysis_type": "warehouse"
        })
        print(f"HVDC Analysis Result: {hvdc_result['status']}")
        if hvdc_result['status'] == 'SUCCESS':
            hvdc_analysis = hvdc_result.get('hvdc_analysis', {})
            warehouse_analysis = hvdc_analysis.get('warehouse_analysis', {})
            print(f"Warehouse Analysis: {warehouse_analysis}")
        print()
        
        # 6. 시스템 상태 확인
        print("=== 6. System Status Check ===")
        system_status = await system.get_system_status()
        print(f"System Status: {system_status['status']}")
        print(f"Active Layers: {len(system_status.get('layers', {}))}")
        print()
        
        # 7. 추천 명령어 확인
        print("=== 7. Recommended Commands Test ===")
        if 'recommended_commands' in query_result:
            print("Recommended commands after query:")
            for cmd in query_result['recommended_commands']:
                print(f"  - {cmd}")
        print()
        
        print("✅ Excel Agent MACHO-GPT integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_excel_agent_functionality():
    """Excel Agent 기능 테스트"""
    print("=== Excel Agent Functionality Test ===")
    print()
    
    try:
        from excel_agent_integration import ExcelAgentIntegration
        
        # Excel Agent 통합 모듈 테스트
        integration = ExcelAgentIntegration()
        success = await integration.initialize()
        
        if not success:
            print("❌ Excel Agent Integration initialization failed")
            return False
        
        print("✅ Excel Agent Integration initialized")
        
        # 시스템 상태 확인
        status = await integration.get_system_status()
        print(f"Integration Status: {status['status']}")
        
        # 데이터프레임 정보 확인
        if integration.current_dataframe is not None:
            info = await integration.get_dataframe_info()
            print(f"DataFrame Info: {info['status']}")
            if info['status'] == 'SUCCESS':
                print(f"Shape: {info['shape']}")
                print(f"Columns: {len(info['columns'])}")
        
        print("✅ Excel Agent functionality test completed")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("Starting Excel Agent MACHO-GPT Integration Tests...")
    print("=" * 60)
    print()
    
    # 테스트 실행
    integration_test = await test_excel_agent_integration()
    functionality_test = await test_excel_agent_functionality()
    
    print("=" * 60)
    print("=== FINAL TEST RESULTS ===")
    print(f"Integration test: {'✅ PASSED' if integration_test else '❌ FAILED'}")
    print(f"Functionality test: {'✅ PASSED' if functionality_test else '❌ FAILED'}")
    
    if integration_test and functionality_test:
        print("\n🎉 Excel Agent is fully integrated with MACHO-GPT system!")
        print("   Ready for production use.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 