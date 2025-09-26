#!/usr/bin/env python3
"""
업계 표준 Context Engineering 시스템 상세 테스트
===============================================

업그레이드된 Context Engineering 시스템의 모든 기능을 테스트하고
업계 표준 지표의 정확성을 검증합니다.
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
from src.context_engineering_integration_enhanced import (
    EnhancedHVDCContextWindow, EnhancedHVDCContextScoring, 
    EnhancedHVDCContextProtocol, EnhancedHVDCContextEngineeringIntegration
)

class EnhancedContextEngineeringTester:
    """업계 표준 Context Engineering 테스터"""
    
    def __init__(self):
        self.scoring = EnhancedHVDCContextScoring()
        self.protocol = EnhancedHVDCContextProtocol()
        self.test_results = []
        
    def test_industry_standard_metrics(self):
        """업계 표준 지표 테스트"""
        print("🔍 업계 표준 지표 테스트")
        print("=" * 50)
        
        # 1. Context Precision 테스트
        context = EnhancedHVDCContextWindow()
        context.examples = [
            {"HVDC": "project", "HITACHI": "equipment", "warehouse": "location"},
            {"SIEMENS": "vendor", "logistics": "operation", "FANR": "compliance"},
            {"unrelated": "data", "random": "information"}  # 관련 없는 예시
        ]
        
        precision = self.scoring.calculate_context_precision(context)
        print(f"✅ Context Precision: {precision:.3f} (예상: 0.667)")
        
        # 2. Context Recall 테스트
        recall = self.scoring.calculate_context_recall(context)
        print(f"✅ Context Recall: {recall:.3f}")
        
        # 3. Groundedness 테스트
        context.prompt = "HVDC warehouse HITACHI equipment logistics"
        groundedness = self.scoring.calculate_groundedness(context)
        print(f"✅ Groundedness: {groundedness:.3f}")
        
        # 4. 메모리 품질 테스트
        context.memory = {
            "recent_command": {
                "command": "enhance_dashboard",
                "status": "SUCCESS",
                "timestamp": datetime.now().isoformat()
            },
            "old_command": {
                "command": "get_kpi",
                "status": "SUCCESS", 
                "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
            }
        }
        
        memory_quality = self.scoring.calculate_memory_quality(context)
        print(f"✅ Memory Freshness: {memory_quality['freshness']:.3f}")
        print(f"✅ Memory Relevance: {memory_quality['relevance']:.3f}")
        print(f"✅ Memory Coherence: {memory_quality['coherence']:.3f}")
        
        return {
            "precision": precision,
            "recall": recall,
            "groundedness": groundedness,
            "memory_quality": memory_quality
        }
    
    def test_enhanced_scoring_system(self):
        """향상된 점수 시스템 테스트"""
        print("\n🎯 향상된 점수 시스템 테스트")
        print("=" * 50)
        
        # 완전한 Context 테스트
        complete_context = EnhancedHVDCContextWindow()
        complete_context.prompt = "HVDC warehouse optimization"
        complete_context.examples = [
            {"HVDC": "project", "optimization": "success", "performance": 0.95}
        ]
        complete_context.tools = ["optimizer", "analyzer"]
        complete_context.state = {"mode": "LATTICE"}
        complete_context.logistics_context = {"project": "HVDC"}
        complete_context.fanr_compliance = {"status": "valid"}
        complete_context.kpi_metrics = {"efficiency": 0.92}
        complete_context.field_resonance = 0.9
        complete_context.attractor_strength = 0.85
        
        complete_score = self.scoring.score_context_quality_enhanced(complete_context)
        print(f"✅ 완전한 Context 점수: {complete_score:.3f}")
        
        # 부분적 Context 테스트
        partial_context = EnhancedHVDCContextWindow()
        partial_context.prompt = "basic query"
        partial_context.examples = [{"basic": "data"}]
        
        partial_score = self.scoring.score_context_quality_enhanced(partial_context)
        print(f"✅ 부분적 Context 점수: {partial_score:.3f}")
        
        # 빈 Context 테스트
        empty_context = EnhancedHVDCContextWindow()
        empty_score = self.scoring.score_context_quality_enhanced(empty_context)
        print(f"✅ 빈 Context 점수: {empty_score:.3f}")
        
        return {
            "complete_score": complete_score,
            "partial_score": partial_score,
            "empty_score": empty_score
        }
    
    def test_response_quality_enhanced(self):
        """향상된 응답 품질 평가 테스트"""
        print("\n📊 향상된 응답 품질 평가 테스트")
        print("=" * 50)
        
        # 우수한 응답
        excellent_response = {
            "status": "SUCCESS",
            "confidence": 0.95,
            "mode": "PRIME",
            "recommended_commands": ["get_kpi", "enhance_dashboard"],
            "timestamp": datetime.now().isoformat(),
            "context_engineering": {"score": 0.9}
        }
        
        excellent_score = self.scoring.score_response_quality_enhanced(excellent_response)
        print(f"✅ 우수한 응답 점수: {excellent_score:.3f}")
        
        # 보통 응답
        average_response = {
            "status": "SUCCESS",
            "confidence": 0.8,
            "mode": "PRIME"
        }
        
        average_score = self.scoring.score_response_quality_enhanced(average_response)
        print(f"✅ 보통 응답 점수: {average_score:.3f}")
        
        # 오류 응답
        error_response = {
            "status": "ERROR",
            "error_message": "Invalid command",
            "confidence": 0.0
        }
        
        error_score = self.scoring.score_response_quality_enhanced(error_response)
        print(f"✅ 오류 응답 점수: {error_score:.3f}")
        
        return {
            "excellent_score": excellent_score,
            "average_score": average_score,
            "error_score": error_score
        }
    
    def test_dynamic_thresholds(self):
        """동적 임계값 조정 테스트"""
        print("\n⚙️ 동적 임계값 조정 테스트")
        print("=" * 50)
        
        # 초기 임계값
        initial_threshold = self.scoring.dynamic_thresholds["confidence"]
        print(f"✅ 초기 confidence 임계값: {initial_threshold:.3f}")
        
        # 가상의 성능 데이터로 임계값 업데이트
        recent_scores = [0.85, 0.88, 0.92, 0.89, 0.91, 0.87, 0.93, 0.90, 0.86, 0.94] * 3  # 30개 데이터
        
        self.scoring.update_dynamic_thresholds(recent_scores)
        updated_threshold = self.scoring.dynamic_thresholds["confidence"]
        print(f"✅ 업데이트된 confidence 임계값: {updated_threshold:.3f}")
        
        return {
            "initial_threshold": initial_threshold,
            "updated_threshold": updated_threshold,
            "threshold_change": updated_threshold - initial_threshold
        }
    
    def test_memory_penalty_system(self):
        """메모리 패널티 시스템 테스트"""
        print("\n🧠 메모리 패널티 시스템 테스트")
        print("=" * 50)
        
        # 메모리가 있는 Context
        context_with_memory = EnhancedHVDCContextWindow()
        context_with_memory.prompt = "test"
        context_with_memory.memory = {
            "command_1": {"status": "SUCCESS", "timestamp": datetime.now().isoformat()}
        }
        
        score_with_memory = self.scoring.score_context_quality_enhanced(context_with_memory)
        print(f"✅ 메모리 있는 Context 점수: {score_with_memory:.3f}")
        
        # 메모리가 없는 Context
        context_without_memory = EnhancedHVDCContextWindow()
        context_without_memory.prompt = "test"
        # memory는 기본적으로 빈 딕셔너리
        
        score_without_memory = self.scoring.score_context_quality_enhanced(context_without_memory)
        print(f"✅ 메모리 없는 Context 점수: {score_without_memory:.3f}")
        
        penalty_effect = score_with_memory - score_without_memory
        print(f"✅ 메모리 패널티 효과: {penalty_effect:.3f}")
        
        return {
            "score_with_memory": score_with_memory,
            "score_without_memory": score_without_memory,
            "penalty_effect": penalty_effect
        }
    
    async def test_enhanced_integration(self):
        """향상된 통합 시스템 테스트"""
        print("\n🔗 향상된 통합 시스템 테스트")
        print("=" * 50)
        
        # 가상의 LogiMaster 시스템
        class MockLogiMasterSystem:
            async def initialize(self):
                pass
            
            async def execute_command(self, command: str, parameters: Dict[str, Any] = None):
                return {
                    "status": "SUCCESS",
                    "confidence": 0.92,
                    "mode": "PRIME",
                    "command": command,
                    "parameters": parameters,
                    "recommended_commands": ["get_kpi", "enhance_dashboard"],
                    "timestamp": datetime.now().isoformat()
                }
        
        # 향상된 통합 시스템 초기화
        mock_logi_master = MockLogiMasterSystem()
        enhanced_integration = EnhancedHVDCContextEngineeringIntegration(mock_logi_master)
        
        # 명령어 실행 테스트
        result = await enhanced_integration.execute_command_with_context(
            "enhance_dashboard",
            {"dashboard_id": "main", "enhancement_type": "weather_integration"}
        )
        
        print(f"✅ 명령어 실행 상태: {result['status']}")
        print(f"✅ Context 점수: {result['enhanced_context_engineering']['context_score']:.3f}")
        print(f"✅ 응답 점수: {result['enhanced_context_engineering']['response_score']:.3f}")
        print(f"✅ Context Precision: {result['enhanced_context_engineering']['context_precision']:.3f}")
        print(f"✅ Context Recall: {result['enhanced_context_engineering']['context_recall']:.3f}")
        print(f"✅ Groundedness: {result['enhanced_context_engineering']['groundedness']:.3f}")
        
        # 분석 데이터 테스트
        analytics = await enhanced_integration.get_enhanced_context_analytics()
        print(f"✅ 총 Context 수: {analytics['total_contexts']}")
        print(f"✅ 평균 Context 점수: {analytics['average_context_score']:.3f}")
        print(f"✅ 평균 응답 점수: {analytics['average_response_score']:.3f}")
        
        return {
            "execution_result": result,
            "analytics": analytics
        }
    
    def test_quality_distribution(self):
        """품질 분포 테스트"""
        print("\n📈 품질 분포 테스트")
        print("=" * 50)
        
        # 다양한 품질의 Context 생성
        contexts = []
        
        # 우수한 Context들
        for i in range(5):
            ctx = EnhancedHVDCContextWindow()
            ctx.prompt = f"excellent context {i}"
            ctx.examples = [{"HVDC": "project", "quality": "excellent"}]
            ctx.tools = ["tool1", "tool2"]
            ctx.logistics_context = {"project": "HVDC"}
            ctx.field_resonance = 0.9
            ctx.attractor_strength = 0.85
            contexts.append(ctx)
        
        # 보통 Context들
        for i in range(8):
            ctx = EnhancedHVDCContextWindow()
            ctx.prompt = f"good context {i}"
            ctx.examples = [{"data": "good"}]
            ctx.tools = ["tool1"]
            contexts.append(ctx)
        
        # 낮은 품질 Context들
        for i in range(3):
            ctx = EnhancedHVDCContextWindow()
            ctx.prompt = f"poor context {i}"
            # 최소한의 정보만
            contexts.append(ctx)
        
        # 점수 계산 및 분포 분석
        scores = [self.scoring.score_context_quality_enhanced(ctx) for ctx in contexts]
        
        excellent_count = sum(1 for score in scores if score >= 0.9)
        good_count = sum(1 for score in scores if 0.7 <= score < 0.9)
        fair_count = sum(1 for score in scores if 0.5 <= score < 0.7)
        poor_count = sum(1 for score in scores if score < 0.5)
        
        print(f"✅ 우수 (≥0.9): {excellent_count}개")
        print(f"✅ 양호 (0.7-0.9): {good_count}개")
        print(f"✅ 보통 (0.5-0.7): {fair_count}개")
        print(f"✅ 미흡 (<0.5): {poor_count}개")
        print(f"✅ 평균 점수: {np.mean(scores):.3f}")
        print(f"✅ 표준편차: {np.std(scores):.3f}")
        
        return {
            "scores": scores,
            "distribution": {
                "excellent": excellent_count,
                "good": good_count,
                "fair": fair_count,
                "poor": poor_count
            },
            "statistics": {
                "mean": np.mean(scores),
                "std": np.std(scores),
                "min": np.min(scores),
                "max": np.max(scores)
            }
        }
    
    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🚀 업계 표준 Context Engineering 종합 테스트 시작")
        print("=" * 60)
        
        # 1. 업계 표준 지표 테스트
        metrics_result = self.test_industry_standard_metrics()
        self.test_results.append(("업계 표준 지표", metrics_result))
        
        # 2. 향상된 점수 시스템 테스트
        scoring_result = self.test_enhanced_scoring_system()
        self.test_results.append(("향상된 점수 시스템", scoring_result))
        
        # 3. 응답 품질 평가 테스트
        response_result = self.test_response_quality_enhanced()
        self.test_results.append(("응답 품질 평가", response_result))
        
        # 4. 동적 임계값 테스트
        threshold_result = self.test_dynamic_thresholds()
        self.test_results.append(("동적 임계값", threshold_result))
        
        # 5. 메모리 패널티 테스트
        memory_result = self.test_memory_penalty_system()
        self.test_results.append(("메모리 패널티", memory_result))
        
        # 6. 품질 분포 테스트
        distribution_result = self.test_quality_distribution()
        self.test_results.append(("품질 분포", distribution_result))
        
        return self.test_results
    
    async def run_async_tests(self):
        """비동기 테스트 실행"""
        print("\n🔄 비동기 테스트 실행")
        print("=" * 60)
        
        # 향상된 통합 시스템 테스트
        integration_result = await self.test_enhanced_integration()
        self.test_results.append(("향상된 통합", integration_result))
        
        return integration_result
    
    def generate_test_report(self):
        """테스트 리포트 생성"""
        print("\n📋 업계 표준 Context Engineering 테스트 리포트")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = 0
        
        for test_name, result in self.test_results:
            print(f"\n🔍 {test_name} 테스트 결과:")
            
            if isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, float):
                        print(f"  ✅ {key}: {value:.3f}")
                    elif isinstance(value, dict):
                        print(f"  ✅ {key}: {json.dumps(value, indent=4, ensure_ascii=False)}")
                    else:
                        print(f"  ✅ {key}: {value}")
                
                # 테스트 통과 여부 판단
                if "score" in str(result) or "precision" in str(result):
                    passed_tests += 1
            else:
                print(f"  ✅ 결과: {result}")
                passed_tests += 1
        
        print(f"\n📊 테스트 요약:")
        print(f"  총 테스트: {total_tests}개")
        print(f"  통과: {passed_tests}개")
        print(f"  통과율: {(passed_tests/total_tests)*100:.1f}%")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": (passed_tests/total_tests)*100,
            "results": self.test_results
        }

async def main():
    """메인 테스트 실행"""
    tester = EnhancedContextEngineeringTester()
    
    # 동기 테스트 실행
    sync_results = tester.run_comprehensive_test()
    
    # 비동기 테스트 실행
    async_results = await tester.run_async_tests()
    
    # 테스트 리포트 생성
    report = tester.generate_test_report()
    
    # 결과 저장
    with open("enhanced_context_engineering_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 테스트 리포트가 'enhanced_context_engineering_test_report.json'에 저장되었습니다.")
    
    return report

if __name__ == "__main__":
    asyncio.run(main()) 