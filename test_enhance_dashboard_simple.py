#!/usr/bin/env python3
"""
Simple test for enhance_dashboard command
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from logi_master_system import LogiMasterSystem

async def test_enhance_dashboard():
    """enhance_dashboard 명령어 테스트"""
    print("🚀 LOGI MASTER SYSTEM 테스트 시작...")
    
    # 시스템 초기화
    system = LogiMasterSystem()
    success = await system.initialize()
    
    if not success:
        print("❌ 시스템 초기화 실패")
        return
    
    print("✅ 시스템 초기화 완료")
    
    # enhance_dashboard 명령어 테스트
    test_parameters = {
        "dashboard_id": "main",
        "enhancement_type": "real_time_data",
        "features": ["weather_integration", "ocr_processing", "kpi_monitoring"],
        "data_sources": ["api_weather", "api_ocr", "api_shipping"],
        "refresh_interval": 300
    }
    
    print("🔧 enhance_dashboard 명령어 실행 중...")
    result = await system.execute_command("enhance_dashboard", test_parameters)
    
    print(f"📊 결과: {result}")
    
    if result.get("status") == "SUCCESS":
        print("✅ enhance_dashboard 명령어 성공!")
        print(f"📁 생성된 파일: {result.get('enhanced_dashboard_url')}")
        print(f"🆕 새 기능: {result.get('new_features')}")
        print(f"🎯 신뢰도: {result.get('confidence')*100:.1f}%")
    else:
        print(f"❌ enhance_dashboard 명령어 실패: {result.get('error_message', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_enhance_dashboard()) 