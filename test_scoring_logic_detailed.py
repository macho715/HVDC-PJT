#!/usr/bin/env python3
"""
Context Engineering 평가 로직 상세 테스트
========================================

HVDC 프로젝트의 Context Engineering 평가 시스템의 모든 측면을
상세하게 테스트하고 분석합니다.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from src.context_engineering_integration import (
    HVDCContextWindow, HVDCContextScoring, HVDCContextProtocol,
    HVDCContextEngineeringIntegration
)
from src.logi_master_system import LogiMasterSystem

class ScoringLogicTester:
    """평가 로직 상세 테스터"""
    
    def __init__(self):
        self.scoring = HVDCContextScoring()
        self.protocol = HVDCContextProtocol()
        self.test_results = []
        
    def test_context_quality_scoring_breakdown(self):
        """Context 품질 점수 세부 분석 테스트"""
        print("🔍 Context 품질 점수 세부 분석 테스트")
        print("=" * 60)
        
        test_cases = [
            {
                "name": "완전한 Context (최고 점수)",
                "context": HVDCContextWindow(
                    prompt="완전한 프롬프트",
                    examples=[{"test": "data"}],
                    memory={"key": "value"},
                    tools=["tool1", "tool2"],
                    state={"status": "active"},
                    logistics_context={"project": "HVDC"},
                    fanr_compliance={"status": "compliant"},
                    kpi_metrics={"performance": 0.95},
                    field_resonance=0.8,
                    attractor_strength=0.7
                ),
                "expected_score": 1.0
            },
            {
                "name": "기본 Context (중간 점수)",
                "context": HVDCContextWindow(
                    prompt="기본 프롬프트",
                    examples=[{"test": "data"}],
                    tools=["tool1"],
                    logistics_context={"project": "HVDC"},
                    field_resonance=0.6,
                    attractor_strength=0.6
                ),
                "expected_score": 0.65
            },
            {
                "name": "최소 Context (낮은 점수)",
                "context": HVDCContextWindow(
                    prompt="최소 프롬프트"
                ),
                "expected_score": 0.2
            },
            {
                "name": "도메인 특화 Context",
                "context": HVDCContextWindow(
                    prompt="HVDC 물류 분석",
                    examples=[{"vendor": "HITACHI", "result": "success"}],
                    tools=["warehouse_api", "weather_api"],
                    logistics_context={
                        "project": "HVDC",
                        "vendor": "HITACHI/SIEMENS",
                        "location": "UAE"
                    },
                    fanr_compliance={"certification": "valid"},
                    kpi_metrics={"efficiency": 0.92},
                    field_resonance=0.9,
                    attractor_strength=0.8
                ),
                "expected_score": 1.0
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📊 테스트 케이스 {i}: {test_case['name']}")
            print("-" * 40)
            
            context = test_case["context"]
            actual_score = self.scoring.score_context_quality(context)
            expected_score = test_case["expected_score"]
            
            # 세부 점수 분석
            scores = []
            score_details = []
            
            if context.prompt:
                scores.append(0.2)
                score_details.append("✅ Prompt 존재 (+0.2)")
            else:
                score_details.append("❌ Prompt 없음 (+0.0)")
            
            if context.examples:
                scores.append(0.15)
                score_details.append("✅ Examples 존재 (+0.15)")
            else:
                score_details.append("❌ Examples 없음 (+0.0)")
            
            if context.memory:
                scores.append(0.15)
                score_details.append("✅ Memory 존재 (+0.15)")
            else:
                score_details.append("❌ Memory 없음 (+0.0)")
            
            if context.tools:
                scores.append(0.1)
                score_details.append("✅ Tools 존재 (+0.1)")
            else:
                score_details.append("❌ Tools 없음 (+0.0)")
            
            if context.state:
                scores.append(0.1)
                score_details.append("✅ State 존재 (+0.1)")
            else:
                score_details.append("❌ State 없음 (+0.0)")
            
            if context.logistics_context:
                scores.append(0.1)
                score_details.append("✅ Logistics Context 존재 (+0.1)")
            else:
                score_details.append("❌ Logistics Context 없음 (+0.0)")
            
            if context.fanr_compliance:
                scores.append(0.1)
                score_details.append("✅ FANR Compliance 존재 (+0.1)")
            else:
                score_details.append("❌ FANR Compliance 없음 (+0.0)")
            
            if context.kpi_metrics:
                scores.append(0.1)
                score_details.append("✅ KPI Metrics 존재 (+0.1)")
            else:
                score_details.append("❌ KPI Metrics 없음 (+0.0)")
            
            if context.field_resonance > 0.5:
                scores.append(0.05)
                score_details.append(f"✅ Field Resonance > 0.5 ({context.field_resonance:.1f}) (+0.05)")
            else:
                score_details.append(f"❌ Field Resonance <= 0.5 ({context.field_resonance:.1f}) (+0.0)")
            
            if context.attractor_strength > 0.5:
                scores.append(0.05)
                score_details.append(f"✅ Attractor Strength > 0.5 ({context.attractor_strength:.1f}) (+0.05)")
            else:
                score_details.append(f"❌ Attractor Strength <= 0.5 ({context.attractor_strength:.1f}) (+0.0)")
            
            calculated_score = min(sum(scores), 1.0)
            
            print("📋 세부 점수 분석:")
            for detail in score_details:
                print(f"   {detail}")
            
            print(f"\n📊 점수 결과:")
            print(f"   계산된 점수: {calculated_score:.3f}")
            print(f"   실제 점수: {actual_score:.3f}")
            print(f"   예상 점수: {expected_score:.3f}")
            
            # 검증
            if abs(actual_score - calculated_score) < 0.001:
                print("   ✅ 점수 계산 정확")
            else:
                print("   ❌ 점수 계산 오류")
            
            if abs(actual_score - expected_score) < 0.1:
                print("   ✅ 예상 점수와 일치")
            else:
                print("   ⚠️ 예상 점수와 차이")
            
            self.test_results.append({
                "test_case": test_case["name"],
                "actual_score": actual_score,
                "expected_score": expected_score,
                "calculated_score": calculated_score,
                "passed": abs(actual_score - expected_score) < 0.1
            })
    
    def test_response_quality_scoring_breakdown(self):
        """응답 품질 점수 세부 분석 테스트"""
        print("\n🔍 응답 품질 점수 세부 분석 테스트")
        print("=" * 60)
        
        test_responses = [
            {
                "name": "완벽한 응답",
                "response": {
                    "status": "SUCCESS",
                    "confidence": 0.95,
                    "recommended_commands": ["get_kpi", "switch_mode"],
                    "mode": "PRIME",
                    "timestamp": datetime.now().isoformat()
                },
                "expected_score": 1.0
            },
            {
                "name": "성공 응답 (신뢰도 낮음)",
                "response": {
                    "status": "SUCCESS",
                    "confidence": 0.7,
                    "recommended_commands": ["get_kpi"],
                    "mode": "PRIME"
                },
                "expected_score": 0.7
            },
            {
                "name": "실패 응답",
                "response": {
                    "status": "ERROR",
                    "error_message": "Command not found",
                    "confidence": 0.0
                },
                "expected_score": 0.0
            },
            {
                "name": "부분 성공 응답",
                "response": {
                    "status": "SUCCESS",
                    "confidence": 0.85,
                    "mode": "LATTICE"
                },
                "expected_score": 0.5
            }
        ]
        
        for i, test_case in enumerate(test_responses, 1):
            print(f"\n📊 응답 테스트 {i}: {test_case['name']}")
            print("-" * 40)
            
            response = test_case["response"]
            actual_score = self.scoring.score_response_quality(response)
            expected_score = test_case["expected_score"]
            
            # 세부 점수 분석
            scores = []
            score_details = []
            
            if response.get("status") == "SUCCESS":
                scores.append(0.3)
                score_details.append("✅ Status = SUCCESS (+0.3)")
            else:
                score_details.append("❌ Status != SUCCESS (+0.0)")
            
            if response.get("confidence", 0) > 0.9:
                scores.append(0.3)
                score_details.append(f"✅ Confidence > 0.9 ({response.get('confidence', 0):.2f}) (+0.3)")
            else:
                score_details.append(f"❌ Confidence <= 0.9 ({response.get('confidence', 0):.2f}) (+0.0)")
            
            if response.get("recommended_commands"):
                scores.append(0.2)
                score_details.append("✅ Recommended Commands 존재 (+0.2)")
            else:
                score_details.append("❌ Recommended Commands 없음 (+0.0)")
            
            if response.get("mode"):
                scores.append(0.1)
                score_details.append("✅ Mode 존재 (+0.1)")
            else:
                score_details.append("❌ Mode 없음 (+0.0)")
            
            if response.get("timestamp"):
                scores.append(0.1)
                score_details.append("✅ Timestamp 존재 (+0.1)")
            else:
                score_details.append("❌ Timestamp 없음 (+0.0)")
            
            calculated_score = min(sum(scores), 1.0)
            
            print("📋 세부 점수 분석:")
            for detail in score_details:
                print(f"   {detail}")
            
            print(f"\n📊 점수 결과:")
            print(f"   계산된 점수: {calculated_score:.3f}")
            print(f"   실제 점수: {actual_score:.3f}")
            print(f"   예상 점수: {expected_score:.3f}")
            
            # 검증
            if abs(actual_score - calculated_score) < 0.001:
                print("   ✅ 점수 계산 정확")
            else:
                print("   ❌ 점수 계산 오류")
            
            if abs(actual_score - expected_score) < 0.1:
                print("   ✅ 예상 점수와 일치")
            else:
                print("   ⚠️ 예상 점수와 차이")
    
    async def test_command_context_creation(self):
        """명령어별 Context 생성 테스트"""
        print("\n🔍 명령어별 Context 생성 테스트")
        print("=" * 60)
        
        commands = [
            ("enhance_dashboard", {"dashboard_id": "main", "enhancement_type": "weather_integration"}),
            ("excel_query", {"query": "Show me all Hitachi equipment"}),
            ("weather_tie", {"weather_data": "storm_warning"}),
            ("get_kpi", {"metric": "efficiency"}),
            ("switch_mode", {"mode": "LATTICE"})
        ]
        
        for i, (command, parameters) in enumerate(commands, 1):
            print(f"\n📊 명령어 테스트 {i}: {command}")
            print("-" * 40)
            
            context = await self.protocol.create_context_for_command(command, parameters)
            score = self.scoring.score_context_quality(context)
            
            print(f"📝 생성된 Context:")
            print(f"   Prompt: {context.prompt[:50]}...")
            print(f"   Examples: {len(context.examples)}개")
            print(f"   Tools: {context.tools}")
            print(f"   Logistics Context: {context.logistics_context}")
            print(f"   Field Resonance: {context.field_resonance}")
            print(f"   Attractor Strength: {context.attractor_strength}")
            print(f"   품질 점수: {score:.3f}")
            
            # 품질 평가
            if score >= 0.7:
                print("   🟢 높은 품질")
            elif score >= 0.5:
                print("   🟡 중간 품질")
            else:
                print("   🔴 낮은 품질")
    
    async def test_integration_workflow(self):
        """통합 워크플로우 테스트"""
        print("\n🔍 통합 워크플로우 테스트")
        print("=" * 60)
        
        # LogiMaster 시스템 초기화
        logi_master = LogiMasterSystem()
        await logi_master.initialize()
        
        # Context Engineering 통합
        context_integration = HVDCContextEngineeringIntegration(logi_master)
        
        # 테스트 명령어 실행
        test_commands = [
            ("enhance_dashboard", {"dashboard_id": "main", "enhancement_type": "weather_integration"}),
            ("get_kpi", {"metric": "efficiency"}),
            ("switch_mode", {"mode": "LATTICE"})
        ]
        
        for i, (command, parameters) in enumerate(test_commands, 1):
            print(f"\n📊 통합 테스트 {i}: {command}")
            print("-" * 40)
            
            result = await context_integration.execute_command_with_context(command, parameters)
            
            print(f"📝 실행 결과:")
            print(f"   Status: {result.get('status')}")
            print(f"   Context Score: {result.get('context_engineering', {}).get('context_score', 0):.3f}")
            print(f"   Response Score: {result.get('context_engineering', {}).get('response_score', 0):.3f}")
            print(f"   Field Resonance: {result.get('context_engineering', {}).get('field_resonance', 0):.3f}")
            print(f"   Attractor Strength: {result.get('context_engineering', {}).get('attractor_strength', 0):.3f}")
            
            # 품질 평가
            context_score = result.get('context_engineering', {}).get('context_score', 0)
            response_score = result.get('context_engineering', {}).get('response_score', 0)
            
            if context_score >= 0.7 and response_score >= 0.7:
                print("   🟢 우수한 품질")
            elif context_score >= 0.5 and response_score >= 0.5:
                print("   🟡 보통 품질")
            else:
                print("   🔴 개선 필요")
        
        # Context 분석
        analytics = await context_integration.get_context_analytics()
        print(f"\n📊 Context 분석 결과:")
        print(f"   총 Context 수: {analytics.get('total_contexts', 0)}")
        print(f"   평균 Context 점수: {analytics.get('average_context_score', 0):.3f}")
        print(f"   평균 응답 점수: {analytics.get('average_response_score', 0):.3f}")
        print(f"   Field Resonance 트렌드: {analytics.get('field_resonance_trend', [])}")
        print(f"   Attractor Strength 트렌드: {analytics.get('attractor_strength_trend', [])}")
        print(f"   가장 많이 사용된 도구: {analytics.get('most_used_tools', [])}")
        print(f"   품질 분포: {analytics.get('context_quality_distribution', {})}")
    
    def generate_test_report(self):
        """테스트 리포트 생성"""
        print("\n📋 테스트 리포트")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 전체 테스트 결과:")
        print(f"   총 테스트: {total_tests}개")
        print(f"   통과: {passed_tests}개")
        print(f"   실패: {failed_tests}개")
        print(f"   통과율: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   - {result['test_case']}: 예상 {result['expected_score']:.3f}, 실제 {result['actual_score']:.3f}")
        
        print(f"\n📈 점수 분포:")
        scores = [result["actual_score"] for result in self.test_results]
        if scores:
            print(f"   최고 점수: {max(scores):.3f}")
            print(f"   최저 점수: {min(scores):.3f}")
            print(f"   평균 점수: {sum(scores)/len(scores):.3f}")

async def main():
    """메인 테스트 실행"""
    print("🚀 Context Engineering 평가 로직 상세 테스트")
    print("=" * 80)
    
    tester = ScoringLogicTester()
    
    # 1. Context 품질 점수 세부 분석
    tester.test_context_quality_scoring_breakdown()
    
    # 2. 응답 품질 점수 세부 분석
    tester.test_response_quality_scoring_breakdown()
    
    # 3. 명령어별 Context 생성 테스트
    await tester.test_command_context_creation()
    
    # 4. 통합 워크플로우 테스트
    await tester.test_integration_workflow()
    
    # 5. 테스트 리포트 생성
    tester.generate_test_report()
    
    print("\n🎉 Context Engineering 평가 로직 상세 테스트 완료!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 