"""
Context Engineering 통합 디버그 스크립트
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from context_engineering_integration import HVDCContextEngineeringIntegration
from logi_master_system import LogiMasterSystem

async def debug_context_engineering():
    """Context Engineering 통합 디버그"""
    
    # LogiMaster 시스템 초기화
    logi_master = LogiMasterSystem()
    await logi_master.initialize()
    
    # Context Engineering 통합
    context_integration = HVDCContextEngineeringIntegration(logi_master)
    
    # 잘못된 명령어 테스트
    print("=== 잘못된 명령어 테스트 ===")
    result = await context_integration.execute_command_with_context("invalid_command", {})
    print("결과:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 성공적인 명령어 테스트
    print("\n=== 성공적인 명령어 테스트 ===")
    result = await context_integration.execute_command_with_context(
        "enhance_dashboard",
        {"dashboard_id": "main", "enhancement_type": "weather_integration"}
    )
    print("결과:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(debug_context_engineering()) 