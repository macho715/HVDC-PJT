#!/usr/bin/env python3
"""
Enhanced LOGI MASTER System Integration Test
===========================================
실제 API 통합이 포함된 LOGI MASTER 시스템 종합 테스트
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from logi_master_system import LogiMasterSystem

async def test_enhanced_integration():
    """향상된 통합 시스템 테스트"""
    print("🚀 Enhanced LOGI MASTER System 통합 테스트 시작...")
    
    # 시스템 초기화
    system = LogiMasterSystem()
    success = await system.initialize()
    
    if not success:
        print("❌ 시스템 초기화 실패")
        return
    
    print("✅ 시스템 초기화 완료")
    
    # 1. 기본 enhance_dashboard 테스트
    print("\n🔧 1. 기본 enhance_dashboard 테스트...")
    basic_params = {
        "dashboard_id": "test_basic",
        "enhancement_type": "real_time_data",
        "features": ["weather_integration", "ocr_processing", "kpi_monitoring"],
        "data_sources": ["api_weather", "api_ocr", "api_shipping"],
        "refresh_interval": 300
    }
    
    basic_result = await system.execute_command("enhance_dashboard", basic_params)
    print(f"📊 기본 결과: {basic_result.get('status')}")
    print(f"📁 생성된 파일: {basic_result.get('enhanced_dashboard_url')}")
    print(f"🆕 새 기능: {basic_result.get('new_features')}")
    
    # 2. 실제 API 통합 테스트
    print("\n🔧 2. 실제 API 통합 테스트...")
    real_api_params = {
        "dashboard_id": "test_real_api",
        "enhancement_type": "real_api_integration",
        "apis": {
            "weather": {"enabled": True, "api_key": "test_weather_key"},
            "ocr": {"enabled": True, "engine": "advanced"},
            "shipping": {"enabled": True, "tracking": True}
        }
    }
    
    real_api_result = await system.execute_command("enhance_dashboard", real_api_params)
    print(f"📊 실제 API 결과: {real_api_result.get('status')}")
    print(f"📁 생성된 파일: {real_api_result.get('enhanced_dashboard_url')}")
    print(f"🆕 새 기능: {real_api_result.get('new_features')}")
    print(f"🎯 신뢰도: {real_api_result.get('confidence', 0)*100:.1f}%")
    
    # 3. 날씨 통합 테스트
    print("\n🔧 3. 날씨 통합 테스트...")
    weather_params = {
        "dashboard_id": "test_weather",
        "enhancement_type": "weather_integration",
        "weather_api_key": "test_key",
        "refresh_interval": 600
    }
    
    weather_result = await system.execute_command("enhance_dashboard", weather_params)
    print(f"📊 날씨 결과: {weather_result.get('status')}")
    print(f"📁 생성된 파일: {weather_result.get('enhanced_dashboard_url')}")
    
    # 4. OCR 처리 테스트
    print("\n🔧 4. OCR 처리 테스트...")
    ocr_params = {
        "dashboard_id": "test_ocr",
        "enhancement_type": "ocr_processing",
        "ocr_engine": "advanced",
        "confidence_threshold": 0.95
    }
    
    ocr_result = await system.execute_command("enhance_dashboard", ocr_params)
    print(f"📊 OCR 결과: {ocr_result.get('status')}")
    print(f"📁 생성된 파일: {ocr_result.get('enhanced_dashboard_url')}")
    
    # 5. KPI 모니터링 테스트
    print("\n🔧 5. KPI 모니터링 테스트...")
    kpi_params = {
        "dashboard_id": "test_kpi",
        "enhancement_type": "kpi_monitoring",
        "kpi_metrics": ["utilization", "throughput", "accuracy"],
        "alert_thresholds": {"utilization": 85, "throughput": 90}
    }
    
    kpi_result = await system.execute_command("enhance_dashboard", kpi_params)
    print(f"📊 KPI 결과: {kpi_result.get('status')}")
    print(f"📁 생성된 파일: {kpi_result.get('enhanced_dashboard_url')}")
    
    # 6. 시스템 상태 확인
    print("\n🔧 6. 시스템 상태 확인...")
    system_status = await system.get_system_status()
    print(f"📊 시스템 상태: {system_status}")
    
    # 7. 생성된 파일 목록 확인
    print("\n🔧 7. 생성된 파일 목록...")
    import glob
    enhanced_files = glob.glob("logi_master_enhanced_*.html")
    for file in enhanced_files:
        print(f"📁 {file}")
    
    print(f"\n✅ 총 {len(enhanced_files)}개의 강화된 대시보드 생성 완료!")
    
    # 8. 성능 요약
    print("\n📈 성능 요약:")
    print(f"   - 기본 대시보드: {basic_result.get('status')}")
    print(f"   - 실제 API 통합: {real_api_result.get('status')}")
    print(f"   - 날씨 통합: {weather_result.get('status')}")
    print(f"   - OCR 처리: {ocr_result.get('status')}")
    print(f"   - KPI 모니터링: {kpi_result.get('status')}")
    
    if real_api_result.get('data', {}).get('real_api_used'):
        print("   🎯 실제 API 통합 성공!")
    else:
        print("   ⚠️ 시뮬레이션 모드 사용")
    
    print("\n🔧 추천 명령어:")
    print("   /logi_master enhance_dashboard [대시보드 강화]")
    print("   /logi_master switch_mode [모드 전환]")
    print("   /logi_master kpi-dash [KPI 대시보드]")
    print("   /automate test-pipeline [전체 테스트 실행]")

if __name__ == "__main__":
    asyncio.run(test_enhanced_integration()) 