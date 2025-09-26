#!/usr/bin/env python3
"""
HVDC PROJECT 시스템 아키텍처 분석 테스트
========================================
/logi_master analyze_architecture 명령어 실행 테스트
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.logi_master_system import LogiMasterSystem

async def test_architecture_analysis():
    """시스템 아키텍처 분석 테스트"""
    print("🏗️ HVDC PROJECT 시스템 아키텍처 분석 시작")
    print("=" * 60)
    
    # LOGI MASTER 시스템 초기화
    logi_master = LogiMasterSystem()
    
    if await logi_master.initialize():
        print("✅ 시스템 초기화 완료")
        
        # 1. 전체 아키텍처 개요 분석
        print("\n📋 1. 전체 아키텍처 개요 분석")
        print("-" * 40)
        result = await logi_master.execute_command("analyze_architecture", {
            "analysis_type": "overview",
            "detail_level": "high"
        })
        
        if result.get("status") == "SUCCESS":
            print(f"✅ 분석 성공 (신뢰도: {result.get('confidence', 0):.1%})")
            print(f"📝 메시지: {result.get('message', 'N/A')}")
            
            if "architecture_overview" in result:
                overview = result["architecture_overview"]
                print(f"🏗️ 레이어 구성: {', '.join(overview.get('layers', []))}")
                print(f"🔄 데이터 흐름: {overview.get('data_flow', 'N/A')}")
                print(f"🔧 핵심 컴포넌트: {', '.join(overview.get('key_components', []))}")
        else:
            print(f"❌ 분석 실패: {result.get('error_message', 'Unknown error')}")
        
        # 2. 레이어별 상세 분석
        print("\n📋 2. 레이어별 상세 분석")
        print("-" * 40)
        result = await logi_master.execute_command("analyze_architecture", {
            "analysis_type": "layer_details",
            "detail_level": "high"
        })
        
        if result.get("status") == "SUCCESS":
            print(f"✅ 분석 성공 (신뢰도: {result.get('confidence', 0):.1%})")
            print(f"📝 메시지: {result.get('message', 'N/A')}")
            
            if "layer_details" in result:
                layers = result["layer_details"]
                for layer_name, layer_info in layers.items():
                    print(f"\n🔧 {layer_name} 레이어:")
                    print(f"   📝 설명: {layer_info.get('description', 'N/A')}")
                    print(f"   📊 데이터 소스: {', '.join(layer_info.get('data_sources', []))}")
                    print(f"   💾 데이터 저장: {layer_info.get('data_storage', 'N/A')}")
                    print(f"   ⚙️ 데이터 처리: {layer_info.get('data_processing', 'N/A')}")
        else:
            print(f"❌ 분석 실패: {result.get('error_message', 'Unknown error')}")
        
        # 3. 시스템 상태 확인
        print("\n📋 3. 시스템 전체 상태")
        print("-" * 40)
        status = await logi_master.get_system_status()
        print(f"🏢 시스템명: {status.get('system_name', 'N/A')}")
        print(f"📦 버전: {status.get('version', 'N/A')}")
        print(f"🟢 상태: {status.get('status', 'N/A')}")
        print(f"🎮 현재 모드: {status.get('current_mode', 'N/A')}")
        print(f"🔧 활성 레이어 수: {len(status.get('layers', {}))}")
        
        # 4. 추천 명령어 확인
        print("\n📋 4. 추천 명령어")
        print("-" * 40)
        if "recommended_commands" in result:
            print("💡 다음 단계 추천 명령어:")
            for i, cmd in enumerate(result["recommended_commands"], 1):
                print(f"   {i}. {cmd}")
        
        print("\n🎯 시스템 아키텍처 분석 완료!")
        print("💡 추가 분석이 필요하면 다음 명령어를 사용하세요:")
        print("   - /macho_gpt system_status")
        print("   - /logi_master analyze_inventory")
        print("   - /automate test-pipeline")
        
    else:
        print("❌ 시스템 초기화 실패")

if __name__ == "__main__":
    asyncio.run(test_architecture_analysis()) 