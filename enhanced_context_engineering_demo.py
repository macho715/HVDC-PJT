#!/usr/bin/env python3
"""
업계 표준 Context Engineering 시스템 실시간 데모
===============================================

업그레이드된 Context Engineering 시스템의 모든 기능을
실시간으로 시연하고 성능을 시각화합니다.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from src.context_engineering_integration_enhanced import (
    EnhancedHVDCContextWindow, EnhancedHVDCContextScoring, 
    EnhancedHVDCContextProtocol, EnhancedHVDCContextEngineeringIntegration
)

class EnhancedContextEngineeringDemo:
    """업계 표준 Context Engineering 데모 클래스"""
    
    def __init__(self):
        self.scoring = EnhancedHVDCContextScoring()
        self.protocol = EnhancedHVDCContextProtocol()
        self.demo_results = []
        
    def print_header(self, title: str):
        """헤더 출력"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_metric(self, name: str, value: float, unit: str = "", status: str = ""):
        """메트릭 출력"""
        if status == "✅":
            print(f"✅ {name}: {value:.3f}{unit}")
        elif status == "⚠️":
            print(f"⚠️ {name}: {value:.3f}{unit}")
        elif status == "❌":
            print(f"❌ {name}: {value:.3f}{unit}")
        else:
            print(f"📊 {name}: {value:.3f}{unit}")
    
    def demo_industry_standard_metrics(self):
        """업계 표준 지표 데모"""
        self.print_header("업계 표준 지표 실시간 계산")
        
        # 다양한 Context 생성
        contexts = [
            {
                "name": "완전한 HVDC Context",
                "context": EnhancedHVDCContextWindow(
                    prompt="HVDC warehouse HITACHI equipment optimization",
                    examples=[
                        {"HVDC": "project", "HITACHI": "equipment", "optimization": "success"},
                        {"warehouse": "location", "logistics": "operation", "FANR": "compliance"}
                    ],
                    tools=["optimizer", "analyzer", "compliance_checker"],
                    logistics_context={"project": "HVDC", "vendor": "HITACHI"},
                    fanr_compliance={"status": "valid", "score": 0.98},
                    kpi_metrics={"efficiency": 0.92, "performance": 0.88}
                )
            },
            {
                "name": "부분적 Context",
                "context": EnhancedHVDCContextWindow(
                    prompt="basic query",
                    examples=[{"basic": "data", "query": "simple"}],
                    tools=["basic_tool"]
                )
            },
            {
                "name": "빈 Context",
                "context": EnhancedHVDCContextWindow()
            }
        ]
        
        for ctx_data in contexts:
            print(f"\n🔍 {ctx_data['name']} 분석:")
            context = ctx_data['context']
            
            # 업계 표준 지표 계산
            precision = self.scoring.calculate_context_precision(context)
            recall = self.scoring.calculate_context_recall(context)
            groundedness = self.scoring.calculate_groundedness(context)
            memory_quality = self.scoring.calculate_memory_quality(context)
            
            # 결과 출력
            self.print_metric("Context Precision", precision, status="✅" if precision > 0.5 else "⚠️")
            self.print_metric("Context Recall", recall, status="✅" if recall > 0.1 else "⚠️")
            self.print_metric("Groundedness", groundedness, status="✅" if groundedness > 0.3 else "⚠️")
            
            print(f"🧠 Memory Quality:")
            self.print_metric("  Freshness", memory_quality['freshness'])
            self.print_metric("  Relevance", memory_quality['relevance'])
            self.print_metric("  Coherence", memory_quality['coherence'])
            
            # 전체 점수 계산
            total_score = self.scoring.score_context_quality_enhanced(context)
            self.print_metric("총 Context 점수", total_score, status="✅" if total_score > 0.6 else "⚠️")
            
            self.demo_results.append({
                "context_name": ctx_data['name'],
                "precision": precision,
                "recall": recall,
                "groundedness": groundedness,
                "memory_quality": memory_quality,
                "total_score": total_score
            })
    
    def demo_enhanced_response_quality(self):
        """향상된 응답 품질 평가 데모"""
        self.print_header("향상된 응답 품질 평가")
        
        # 다양한 응답 생성
        responses = [
            {
                "name": "우수한 응답",
                "response": {
                    "status": "SUCCESS",
                    "confidence": 0.95,
                    "mode": "PRIME",
                    "recommended_commands": ["get_kpi", "enhance_dashboard", "weather_tie"],
                    "timestamp": datetime.now().isoformat(),
                    "context_engineering": {"score": 0.9},
                    "enhanced_context_engineering": {
                        "context_score": 0.8,
                        "response_score": 0.85
                    }
                }
            },
            {
                "name": "보통 응답",
                "response": {
                    "status": "SUCCESS",
                    "confidence": 0.8,
                    "mode": "PRIME",
                    "recommended_commands": ["get_kpi"]
                }
            },
            {
                "name": "오류 응답",
                "response": {
                    "status": "ERROR",
                    "error_message": "Invalid command parameter",
                    "confidence": 0.0
                }
            }
        ]
        
        for resp_data in responses:
            print(f"\n📊 {resp_data['name']} 평가:")
            response = resp_data['response']
            
            # 다차원 응답 품질 평가
            groundedness = self.scoring._calculate_response_groundedness(response)
            completeness = self.scoring._calculate_response_completeness(response)
            faithfulness = self.scoring._calculate_response_faithfulness(response)
            helpfulness = self.scoring._calculate_response_helpfulness(response)
            toxicity = self.scoring._calculate_response_toxicity(response)
            latency = self.scoring._calculate_response_latency(response)
            
            # 가중치 적용
            weighted_groundedness = groundedness * self.scoring.response_weights["groundedness"]
            weighted_completeness = completeness * self.scoring.response_weights["completeness"]
            weighted_faithfulness = faithfulness * self.scoring.response_weights["faithfulness"]
            weighted_helpfulness = helpfulness * self.scoring.response_weights["helpfulness"]
            weighted_toxicity = toxicity * self.scoring.response_weights["toxicity"]
            weighted_latency = latency * self.scoring.response_weights["latency"]
            
            # 결과 출력
            self.print_metric("Groundedness", groundedness, " (가중치: 0.30)")
            self.print_metric("Completeness", completeness, " (가중치: 0.20)")
            self.print_metric("Faithfulness", faithfulness, " (가중치: 0.20)")
            self.print_metric("Helpfulness", helpfulness, " (가중치: 0.15)")
            self.print_metric("Toxicity", toxicity, " (가중치: -0.20)")
            self.print_metric("Latency", latency, " (가중치: -0.10)")
            
            print(f"\n📈 가중치 적용 결과:")
            self.print_metric("  Groundedness 점수", weighted_groundedness)
            self.print_metric("  Completeness 점수", weighted_completeness)
            self.print_metric("  Faithfulness 점수", weighted_faithfulness)
            self.print_metric("  Helpfulness 점수", weighted_helpfulness)
            self.print_metric("  Toxicity 점수", weighted_toxicity)
            self.print_metric("  Latency 점수", weighted_latency)
            
            # 총점 계산
            total_score = self.scoring.score_response_quality_enhanced(response)
            self.print_metric("총 응답 점수", total_score, status="✅" if total_score > 0.7 else "⚠️")
            
            self.demo_results.append({
                "response_name": resp_data['name'],
                "groundedness": groundedness,
                "completeness": completeness,
                "faithfulness": faithfulness,
                "helpfulness": helpfulness,
                "toxicity": toxicity,
                "latency": latency,
                "total_score": total_score
            })
    
    def demo_dynamic_thresholds(self):
        """동적 임계값 조정 데모"""
        self.print_header("동적 임계값 조정 시스템")
        
        # 초기 임계값
        initial_thresholds = self.scoring.dynamic_thresholds.copy()
        print("📊 초기 임계값:")
        for key, value in initial_thresholds.items():
            self.print_metric(key, value)
        
        # 가상의 성능 데이터 생성
        print(f"\n🔄 성능 데이터로 임계값 업데이트 중...")
        
        # 다양한 성능 시나리오
        scenarios = [
            {
                "name": "높은 성능 시나리오",
                "scores": [0.92, 0.94, 0.91, 0.93, 0.95, 0.90, 0.93, 0.92, 0.94, 0.91] * 3
            },
            {
                "name": "보통 성능 시나리오", 
                "scores": [0.85, 0.87, 0.83, 0.86, 0.88, 0.84, 0.87, 0.85, 0.86, 0.83] * 3
            },
            {
                "name": "낮은 성능 시나리오",
                "scores": [0.75, 0.77, 0.73, 0.76, 0.78, 0.74, 0.77, 0.75, 0.76, 0.73] * 3
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📈 {scenario['name']}:")
            
            # 임계값 업데이트
            self.scoring.update_dynamic_thresholds(scenario['scores'])
            updated_threshold = self.scoring.dynamic_thresholds["confidence"]
            
            self.print_metric("평균 성능", sum(scenario['scores']) / len(scenario['scores']))
            self.print_metric("업데이트된 임계값", updated_threshold)
            self.print_metric("임계값 변화", updated_threshold - initial_thresholds["confidence"])
            
            # 임계값 리셋
            self.scoring.dynamic_thresholds = initial_thresholds.copy()
    
    def demo_memory_penalty_system(self):
        """메모리 패널티 시스템 데모"""
        self.print_header("메모리 품질 패널티 시스템")
        
        # 메모리 품질별 Context 생성
        memory_scenarios = [
            {
                "name": "신선한 메모리 (24시간 내)",
                "memory": {
                    "recent_1": {
                        "command": "enhance_dashboard",
                        "status": "SUCCESS",
                        "timestamp": datetime.now().isoformat()
                    },
                    "recent_2": {
                        "command": "get_kpi",
                        "status": "SUCCESS", 
                        "timestamp": (datetime.now().isoformat())
                    }
                }
            },
            {
                "name": "혼합 메모리 (신선 + 오래됨)",
                "memory": {
                    "recent": {
                        "command": "enhance_dashboard",
                        "status": "SUCCESS",
                        "timestamp": datetime.now().isoformat()
                    },
                    "old": {
                        "command": "get_kpi",
                        "status": "SUCCESS",
                        "timestamp": "2025-01-01T00:00:00"
                    }
                }
            },
            {
                "name": "빈 메모리",
                "memory": {}
            }
        ]
        
        for scenario in memory_scenarios:
            print(f"\n🧠 {scenario['name']}:")
            
            context = EnhancedHVDCContextWindow()
            context.prompt = "test command"
            context.memory = scenario['memory']
            
            # 메모리 품질 계산
            memory_quality = self.scoring.calculate_memory_quality(context)
            
            self.print_metric("Memory Freshness", memory_quality['freshness'])
            self.print_metric("Memory Relevance", memory_quality['relevance'])
            self.print_metric("Memory Coherence", memory_quality['coherence'])
            self.print_metric("Memory Penalty", memory_quality['penalty'])
            
            # 전체 Context 점수
            total_score = self.scoring.score_context_quality_enhanced(context)
            self.print_metric("총 Context 점수", total_score)
            
            self.demo_results.append({
                "memory_scenario": scenario['name'],
                "memory_quality": memory_quality,
                "total_score": total_score
            })
    
    async def demo_enhanced_integration(self):
        """향상된 통합 시스템 데모"""
        self.print_header("향상된 통합 시스템 실시간 실행")
        
        # 가상의 LogiMaster 시스템
        class MockLogiMasterSystem:
            async def initialize(self):
                pass
            
            async def execute_command(self, command: str, parameters: Dict[str, Any] = None):
                # 명령어별 다른 응답 시뮬레이션
                if command == "enhance_dashboard":
                    return {
                        "status": "SUCCESS",
                        "confidence": 0.95,
                        "mode": "LATTICE",
                        "command": command,
                        "parameters": parameters,
                        "recommended_commands": ["get_kpi", "weather_tie"],
                        "timestamp": datetime.now().isoformat(),
                        "enhancement_result": "Dashboard enhanced with weather integration"
                    }
                elif command == "excel_query":
                    return {
                        "status": "SUCCESS",
                        "confidence": 0.88,
                        "mode": "PRIME",
                        "command": command,
                        "parameters": parameters,
                        "recommended_commands": ["enhance_dashboard"],
                        "timestamp": datetime.now().isoformat(),
                        "query_result": "Data filtered successfully"
                    }
                else:
                    return {
                        "status": "ERROR",
                        "error_message": f"Unknown command: {command}",
                        "confidence": 0.0,
                        "mode": "ZERO"
                    }
        
        # 향상된 통합 시스템 초기화
        mock_logi_master = MockLogiMasterSystem()
        enhanced_integration = EnhancedHVDCContextEngineeringIntegration(mock_logi_master)
        
        # 다양한 명령어 실행
        commands = [
            {
                "name": "대시보드 강화",
                "command": "enhance_dashboard",
                "parameters": {"dashboard_id": "main", "enhancement_type": "weather_integration"}
            },
            {
                "name": "Excel 쿼리",
                "command": "excel_query", 
                "parameters": {"query": "Show me all HITACHI equipment"}
            },
            {
                "name": "알 수 없는 명령어",
                "command": "unknown_command",
                "parameters": {}
            }
        ]
        
        for cmd_data in commands:
            print(f"\n🚀 {cmd_data['name']} 실행:")
            
            start_time = time.time()
            result = await enhanced_integration.execute_command_with_context(
                cmd_data['command'], cmd_data['parameters']
            )
            execution_time = time.time() - start_time
            
            # 결과 분석
            print(f"⏱️ 실행 시간: {execution_time:.3f}초")
            print(f"📊 실행 상태: {result['status']}")
            
            if 'enhanced_context_engineering' in result:
                ce_data = result['enhanced_context_engineering']
                
                print(f"🎯 Context Engineering 결과:")
                self.print_metric("Context 점수", ce_data['context_score'])
                self.print_metric("응답 점수", ce_data['response_score'])
                self.print_metric("Context Precision", ce_data['context_precision'])
                self.print_metric("Context Recall", ce_data['context_recall'])
                self.print_metric("Groundedness", ce_data['groundedness'])
                self.print_metric("Field Resonance", ce_data['field_resonance'])
                self.print_metric("Attractor Strength", ce_data['attractor_strength'])
                
                if 'memory_quality' in ce_data:
                    memory = ce_data['memory_quality']
                    print(f"🧠 Memory Quality:")
                    self.print_metric("  Freshness", memory['freshness'])
                    self.print_metric("  Relevance", memory['relevance'])
                    self.print_metric("  Coherence", memory['coherence'])
            
            self.demo_results.append({
                "command_name": cmd_data['name'],
                "execution_time": execution_time,
                "result": result
            })
        
        # 분석 데이터 조회
        print(f"\n📈 전체 시스템 분석:")
        analytics = await enhanced_integration.get_enhanced_context_analytics()
        
        self.print_metric("총 Context 수", analytics['total_contexts'])
        self.print_metric("평균 Context 점수", analytics['average_context_score'])
        self.print_metric("평균 응답 점수", analytics['average_response_score'])
        self.print_metric("평균 Precision", analytics['average_precision'])
        self.print_metric("평균 Recall", analytics['average_recall'])
        self.print_metric("평균 Groundedness", analytics['average_groundedness'])
        
        if 'memory_quality' in analytics:
            memory = analytics['memory_quality']
            print(f"🧠 전체 Memory Quality:")
            self.print_metric("  평균 Freshness", memory['average_freshness'])
            self.print_metric("  평균 Relevance", memory['average_relevance'])
            self.print_metric("  평균 Coherence", memory['average_coherence'])
        
        self.demo_results.append({
            "analytics": analytics
        })
    
    def generate_demo_report(self):
        """데모 리포트 생성"""
        self.print_header("업계 표준 Context Engineering 데모 리포트")
        
        print(f"📊 데모 실행 결과 요약:")
        print(f"  총 데모 항목: {len(self.demo_results)}개")
        
        # Context 품질 분석
        context_scores = [r['total_score'] for r in self.demo_results if 'total_score' in r and 'context_name' in r]
        if context_scores:
            print(f"  Context 품질 평균: {sum(context_scores)/len(context_scores):.3f}")
        
        # 응답 품질 분석
        response_scores = [r['total_score'] for r in self.demo_results if 'total_score' in r and 'response_name' in r]
        if response_scores:
            print(f"  응답 품질 평균: {sum(response_scores)/len(response_scores):.3f}")
        
        # 메모리 품질 분석
        memory_scores = [r['total_score'] for r in self.demo_results if 'total_score' in r and 'memory_scenario' in r]
        if memory_scores:
            print(f"  메모리 품질 평균: {sum(memory_scores)/len(memory_scores):.3f}")
        
        print(f"\n🎯 주요 개선 효과:")
        print(f"  ✅ 업계 표준 지표 도입: Precision/Recall/Groundedness")
        print(f"  ✅ 다차원 응답 품질 평가: 6개 지표 가중치 적용")
        print(f"  ✅ 동적 임계값 조정: ROC 분석 기반")
        print(f"  ✅ 메모리 패널티 시스템: LoCoMo/HELMET 벤치마크")
        print(f"  ✅ HVDC 도메인 특화: FANR/MOIAT 준수")
        
        return {
            "demo_results": self.demo_results,
            "summary": {
                "total_demos": len(self.demo_results),
                "context_quality_avg": sum(context_scores)/len(context_scores) if context_scores else 0,
                "response_quality_avg": sum(response_scores)/len(response_scores) if response_scores else 0,
                "memory_quality_avg": sum(memory_scores)/len(memory_scores) if memory_scores else 0
            }
        }
    
    async def run_full_demo(self):
        """전체 데모 실행"""
        print("🚀 업계 표준 Context Engineering 시스템 실시간 데모 시작")
        print("=" * 70)
        
        # 1. 업계 표준 지표 데모
        self.demo_industry_standard_metrics()
        
        # 2. 향상된 응답 품질 평가 데모
        self.demo_enhanced_response_quality()
        
        # 3. 동적 임계값 조정 데모
        self.demo_dynamic_thresholds()
        
        # 4. 메모리 패널티 시스템 데모
        self.demo_memory_penalty_system()
        
        # 5. 향상된 통합 시스템 데모
        await self.demo_enhanced_integration()
        
        # 6. 데모 리포트 생성
        report = self.generate_demo_report()
        
        # 결과 저장
        with open("enhanced_context_engineering_demo_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 데모 리포트가 'enhanced_context_engineering_demo_report.json'에 저장되었습니다.")
        
        return report

async def main():
    """메인 데모 실행"""
    demo = EnhancedContextEngineeringDemo()
    report = await demo.run_full_demo()
    return report

if __name__ == "__main__":
    asyncio.run(main()) 