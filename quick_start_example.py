"""
Context Engineering 통합 기능 - 빠른 시작 예제
============================================

가장 기본적인 사용법부터 고급 기능까지 단계별로 설명합니다.
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from context_engineering_integration import HVDCContextEngineeringIntegration
from logi_master_system import LogiMasterSystem

async def quick_start_example():
    """빠른 시작 예제"""
    
    print("🚀 Context Engineering 통합 기능 - 빠른 시작")
    print("=" * 50)
    
    # 1. 시스템 초기화
    print("\n1️⃣ 시스템 초기화...")
    logi_master = LogiMasterSystem()
    await logi_master.initialize()
    
    context_integration = HVDCContextEngineeringIntegration(logi_master)
    print("✅ 초기화 완료!")
    
    # 2. 기본 명령어 실행
    print("\n2️⃣ 기본 명령어 실행...")
    
    result = await context_integration.execute_command_with_context(
        "enhance_dashboard",
        {"dashboard_id": "main", "enhancement_type": "weather_integration"}
    )
    
    print(f"📝 상태: {result['status']}")
    print(f"🎯 신뢰도: {result['confidence']:.2f}")
    print(f"📈 Context 품질: {result['context_engineering']['context_score']:.2f}")
    print(f"📊 응답 품질: {result['context_engineering']['response_score']:.2f}")
    
    # 3. Context 분석
    print("\n3️⃣ Context 분석...")
    analytics = await context_integration.get_context_analytics()
    
    print(f"📈 총 Context 수: {analytics['total_contexts']}")
    print(f"📊 평균 Context 점수: {analytics['average_context_score']:.2f}")
    print(f"🛠️ 사용된 도구: {analytics['most_used_tools']}")
    
    print("\n✅ 빠른 시작 완료!")

if __name__ == "__main__":
    asyncio.run(quick_start_example()) 