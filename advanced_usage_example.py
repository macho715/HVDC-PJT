"""
Context Engineering 통합 기능 - 고급 사용법 예제
=============================================

고급 기능과 복잡한 시나리오를 다루는 예제입니다.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from context_engineering_integration import HVDCContextEngineeringIntegration
from logi_master_system import LogiMasterSystem

async def advanced_usage_example():
    """고급 사용법 예제"""
    
    print("🚀 Context Engineering 통합 기능 - 고급 사용법")
    print("=" * 60)
    
    # 시스템 초기화
    logi_master = LogiMasterSystem()
    await logi_master.initialize()
    context_integration = HVDCContextEngineeringIntegration(logi_master)
    
    print("\n📊 시나리오 1: 복잡한 워크플로우 실행")
    print("-" * 50)
    
    # 여러 명령어를 순차적으로 실행
    workflow_commands = [
        ("enhance_dashboard", {"dashboard_id": "main", "enhancement_type": "weather_integration"}),
        ("excel_query", {"query": "Show me all Hitachi equipment with status 'Active'"}),
        ("weather_tie", {"weather_data": "storm_warning", "eta_data": "24h_delay"}),
        ("get_kpi", {"kpi_type": "utilization", "time_range": "24h"}),
        ("switch_mode", {"new_mode": "LATTICE"})
    ]
    
    results = []
    for i, (command, params) in enumerate(workflow_commands, 1):
        print(f"\n{i}. {command} 실행 중...")
        result = await context_integration.execute_command_with_context(command, params)
        results.append(result)
        
        print(f"   📈 Context 품질: {result['context_engineering']['context_score']:.2f}")
        print(f"   📊 응답 품질: {result['context_engineering']['response_score']:.2f}")
        print(f"   📝 상태: {result['status']}")
    
    print("\n📊 시나리오 2: Context 품질 분석")
    print("-" * 50)
    
    # Context 분석
    analytics = await context_integration.get_context_analytics()
    
    print(f"📈 총 Context 수: {analytics['total_contexts']}")
    print(f"📊 평균 Context 품질 점수: {analytics['average_context_score']:.2f}")
    print(f"📊 평균 응답 품질 점수: {analytics['average_response_score']:.2f}")
    print(f"🌊 Field Resonance 트렌드: {analytics['field_resonance_trend']}")
    print(f"🎯 Attractor Strength 트렌드: {analytics['attractor_strength_trend']}")
    print(f"🛠️ 가장 많이 사용된 도구: {analytics['most_used_tools']}")
    print(f"📊 Context 품질 분포: {analytics['context_quality_distribution']}")
    
    print("\n📊 시나리오 3: 성능 최적화 분석")
    print("-" * 50)
    
    # 성능 분석
    context_scores = [r['context_engineering']['context_score'] for r in results]
    response_scores = [r['context_engineering']['response_score'] for r in results]
    field_resonances = [r['context_engineering']['field_resonance'] for r in results]
    attractor_strengths = [r['context_engineering']['attractor_strength'] for r in results]
    
    print(f"📈 Context 품질 점수 범위: {min(context_scores):.2f} ~ {max(context_scores):.2f}")
    print(f"📊 응답 품질 점수 범위: {min(response_scores):.2f} ~ {max(response_scores):.2f}")
    print(f"🌊 Field Resonance 범위: {min(field_resonances):.2f} ~ {max(field_resonances):.2f}")
    print(f"🎯 Attractor Strength 범위: {min(attractor_strengths):.2f} ~ {max(attractor_strengths):.2f}")
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    print(f"✅ 성공률: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    print("\n📊 시나리오 4: 오류 처리 및 복구")
    print("-" * 50)
    
    # 오류 상황 테스트
    error_commands = [
        ("invalid_command", {}),
        ("enhance_dashboard", {"invalid_param": "value"}),
        ("excel_query", {})  # 필수 파라미터 누락
    ]
    
    for i, (command, params) in enumerate(error_commands, 1):
        print(f"\n{i}. 오류 상황 테스트: {command}")
        result = await context_integration.execute_command_with_context(command, params)
        
        print(f"   📝 상태: {result['status']}")
        print(f"   📈 Context 품질: {result['context_engineering']['context_score']:.2f}")
        print(f"   📊 응답 품질: {result['context_engineering']['response_score']:.2f}")
        
        if result['status'] == 'ERROR':
            print(f"   ⚠️ 오류 메시지: {result.get('error_message', 'N/A')}")
    
    print("\n📊 시나리오 5: Context Engineering 원칙 적용 확인")
    print("-" * 50)
    
    print("✅ Atoms → Molecules → Cells → Organs → Neural Systems → Fields → Protocols → Meta")
    print("   - Atoms: 개별 Context 요소 (prompt, examples, tools)")
    print("   - Molecules: 명령어별 Context 조합")
    print("   - Cells: HVDC 도메인 특화 Context")
    print("   - Organs: 레이어별 Context 시스템")
    print("   - Neural Systems: 전체 통합 시스템")
    print("   - Fields: Field Resonance 기반 최적화")
    print("   - Protocols: Context 관리 프로토콜")
    print("   - Meta: 메타 분석 및 최적화")
    
    print("\n✅ Tidy First 원칙")
    print("   - 구조적 변경: Context 구조 개선")
    print("   - 행위적 변경: Context 품질 향상")
    print("   - 분리 원칙: 구조와 행위 변경 분리")
    
    print("\n" + "=" * 60)
    print("🎉 고급 사용법 예제 완료!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(advanced_usage_example()) 