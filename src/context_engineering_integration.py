#!/usr/bin/env python3
"""
HVDC Context Engineering Integration
===================================
Context Engineering을 LOGI MASTER 시스템에 통합하는 모듈
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class HVDCContextWindow:
    """HVDC Context Window 데이터 구조"""

    prompt: str = ""
    examples: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    memory: List[Dict[str, Any]] = field(default_factory=list)
    feedback: List[Dict[str, Any]] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)
    field_resonance: float = 0.0
    attractor_strength: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Context Window을 딕셔너리로 변환"""
        return {
            "prompt": self.prompt,
            "examples": self.examples,
            "tools": self.tools,
            "memory": self.memory,
            "feedback": self.feedback,
            "state": self.state,
            "field_resonance": self.field_resonance,
            "attractor_strength": self.attractor_strength,
        }


class HVDCContextScoring:
    """Context 품질 점수 계산"""

    @staticmethod
    def score_context_quality(context: HVDCContextWindow) -> float:
        """Context 품질 점수 계산"""
        score = 0.0

        # Prompt 품질 (30%)
        if context.prompt:
            score += 0.3 * min(len(context.prompt) / 100, 1.0)

        # Examples 품질 (25%)
        if context.examples:
            score += 0.25 * min(len(context.examples) / 5, 1.0)

        # Tools 품질 (25%)
        if context.tools:
            score += 0.25 * min(len(context.tools) / 3, 1.0)

        # Memory 품질 (20%)
        if context.memory:
            score += 0.2 * min(len(context.memory) / 10, 1.0)

        return min(score, 1.0)

    @staticmethod
    def score_response_quality(response: Dict[str, Any]) -> float:
        """응답 품질 점수 계산"""
        score = 0.0

        # Status 품질 (40%)
        if response.get("status") == "SUCCESS":
            score += 0.4
        elif response.get("status") == "PARTIAL":
            score += 0.2

        # Confidence 품질 (30%)
        confidence = response.get("confidence", 0.0)
        score += 0.3 * confidence

        # Mode 품질 (20%)
        if response.get("mode") in ["PRIME", "ORACLE", "LATTICE", "RHYTHM"]:
            score += 0.2

        # Error 처리 (10%)
        if "error" not in response:
            score += 0.1

        return min(score, 1.0)


class HVDCContextProtocol:
    """Context Engineering 프로토콜"""

    def __init__(self):
        self.context_history: List[HVDCContextWindow] = []
        self.max_history_size = 10

    async def create_context_for_command(
        self, command: str, parameters: Dict[str, Any]
    ) -> HVDCContextWindow:
        """명령어에 대한 Context 생성"""
        context = HVDCContextWindow()

        # Command별 Context 설정
        if command == "enhance_dashboard":
            context.prompt = (
                f"대시보드 강화: {parameters.get('enhancement_type', 'general')}"
            )
            context.examples = [
                "weather_integration: 날씨 데이터 통합",
                "ocr_processing: OCR 처리 기능",
                "kpi_monitoring: KPI 모니터링",
            ]
            context.tools = [
                "dashboard_api",
                "weather_api",
                "ocr_engine",
                "kpi_calculator",
            ]
            context.state = {
                "mode": "LATTICE",
                "dashboard_id": parameters.get("dashboard_id", "main"),
            }

        elif command == "excel_query":
            query = parameters.get("query", "")
            context.prompt = f"Excel 자연어 쿼리: {query}"
            context.examples = [
                "Show me all Hitachi equipment",
                "Filter by warehouse DSV Outdoor",
                "Calculate total volume by category",
            ]
            context.tools = ["pandas", "excel_parser", "natural_language_processor"]
            context.state = {"mode": "ORACLE", "query_type": "natural_language"}

        elif command == "weather_tie":
            context.prompt = (
                f"기상 조건 분석: {parameters.get('weather_data', 'general')}"
            )
            context.examples = [
                "storm: 폭풍 조건 분석",
                "delay: 지연 시간 계산",
                "eta_update: ETA 업데이트",
            ]
            context.tools = ["weather_api", "eta_calculator", "delay_predictor"]
            context.state = {
                "mode": "RHYTHM",
                "weather_condition": parameters.get("weather_data"),
            }

        else:
            context.prompt = f"일반 명령어: {command}"
            context.examples = ["기본 처리", "오류 처리", "결과 반환"]
            context.tools = ["general_processor", "error_handler"]
            context.state = {"mode": "PRIME", "command": command}

        # Field Resonance 및 Attractor Strength 계산
        context.field_resonance = self._calculate_field_resonance(context)
        context.attractor_strength = self._calculate_attractor_strength(context)

        return context

    def _calculate_field_resonance(self, context: HVDCContextWindow) -> float:
        """Field Resonance 계산"""
        base_resonance = 0.5

        # Tools 수에 따른 보정
        tool_bonus = min(len(context.tools) * 0.1, 0.3)

        # Examples 품질에 따른 보정
        example_bonus = min(len(context.examples) * 0.05, 0.2)

        return min(base_resonance + tool_bonus + example_bonus, 1.0)

    def _calculate_attractor_strength(self, context: HVDCContextWindow) -> float:
        """Attractor Strength 계산"""
        base_strength = 0.6

        # Prompt 길이에 따른 보정
        prompt_bonus = min(len(context.prompt) / 200, 0.2)

        # State 복잡도에 따른 보정
        state_bonus = min(len(context.state) * 0.05, 0.2)

        return min(base_strength + prompt_bonus + state_bonus, 1.0)

    async def update_context_with_response(
        self, context: HVDCContextWindow, response: Dict[str, Any]
    ) -> None:
        """응답으로 Context 업데이트"""
        # Memory에 응답 추가
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "response": response,
            "context_score": HVDCContextScoring.score_context_quality(context),
            "response_score": HVDCContextScoring.score_response_quality(response),
        }
        context.memory.append(memory_entry)

        # Feedback에 응답 품질 추가
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "quality_score": HVDCContextScoring.score_response_quality(response),
            "status": response.get("status", "UNKNOWN"),
            "confidence": response.get("confidence", 0.0),
        }
        context.feedback.append(feedback_entry)

        # Context 히스토리에 추가
        self.context_history.append(context)
        self._limit_history_size()

    def _limit_history_size(self) -> None:
        """Context 히스토리 크기 제한"""
        if len(self.context_history) > self.max_history_size:
            self.context_history = self.context_history[-self.max_history_size :]


class HVDCContextEngineeringIntegration:
    """HVDC Context Engineering 통합 클래스"""

    def __init__(self, logi_master_system):
        self.logi_master_system = logi_master_system
        self.protocol = HVDCContextProtocol()
        self.logger = logging.getLogger(__name__)

    async def execute_command_with_context(
        self, command: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Context Engineering을 적용한 명령어 실행"""
        try:
            # Context 생성
            context = await self.protocol.create_context_for_command(
                command, parameters or {}
            )

            # 명령어 실행
            result = await self.logi_master_system.execute_command(
                command, parameters or {}
            )

            # Context 업데이트
            await self.protocol.update_context_with_response(context, result)

            # Context Engineering 메타데이터 추가
            context_score = HVDCContextScoring.score_context_quality(context)
            response_score = HVDCContextScoring.score_response_quality(result)

            result["context_engineering"] = {
                "context_score": context_score,
                "response_score": response_score,
                "field_resonance": context.field_resonance,
                "attractor_strength": context.attractor_strength,
                "context_quality": self._get_context_quality_label(context_score),
                "response_quality": self._get_response_quality_label(response_score),
            }

            return result

        except Exception as e:
            self.logger.error(f"Context Engineering command execution failed: {e}")
            error_result = {
                "status": "ERROR",
                "error_message": str(e),
                "context_engineering": {
                    "context_score": 0.0,
                    "response_score": 0.0,
                    "field_resonance": 0.0,
                    "attractor_strength": 0.0,
                    "context_quality": "poor",
                    "response_quality": "poor",
                },
            }
            return error_result

    async def get_context_analytics(self) -> Dict[str, Any]:
        """Context 분석 데이터 반환"""
        if not self.protocol.context_history:
            return {
                "message": "No context history available",
                "total_contexts": 0,
                "average_context_score": 0.0,
                "average_response_score": 0.0,
            }

        # 기본 통계
        total_contexts = len(self.protocol.context_history)
        context_scores = []
        response_scores = []
        field_resonance_trend = []
        attractor_strength_trend = []
        tools_usage = {}

        for context in self.protocol.context_history:
            # Context 점수
            context_score = HVDCContextScoring.score_context_quality(context)
            context_scores.append(context_score)

            # Response 점수 (마지막 memory entry에서)
            if context.memory:
                response_score = context.memory[-1].get("response_score", 0.0)
                response_scores.append(response_score)

            # Field Resonance 및 Attractor Strength 트렌드
            field_resonance_trend.append(context.field_resonance)
            attractor_strength_trend.append(context.attractor_strength)

            # Tools 사용 통계
            for tool in context.tools:
                tools_usage[tool] = tools_usage.get(tool, 0) + 1

        # 품질 분포
        context_quality_distribution = self._calculate_quality_distribution(
            context_scores
        )
        response_quality_distribution = self._calculate_quality_distribution(
            response_scores
        )

        # 가장 많이 사용된 도구
        most_used_tools = sorted(tools_usage.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        return {
            "total_contexts": total_contexts,
            "average_context_score": (
                sum(context_scores) / len(context_scores) if context_scores else 0.0
            ),
            "average_response_score": (
                sum(response_scores) / len(response_scores) if response_scores else 0.0
            ),
            "field_resonance_trend": field_resonance_trend,
            "attractor_strength_trend": attractor_strength_trend,
            "most_used_tools": [tool for tool, count in most_used_tools],
            "context_quality_distribution": context_quality_distribution,
            "response_quality_distribution": response_quality_distribution,
            "timestamp": datetime.now().isoformat(),
        }

    def _get_context_quality_label(self, score: float) -> str:
        """Context 품질 라벨 반환"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"

    def _get_response_quality_label(self, score: float) -> str:
        """Response 품질 라벨 반환"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"

    def _calculate_quality_distribution(self, scores: List[float]) -> Dict[str, int]:
        """품질 분포 계산"""
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}

        for score in scores:
            if score >= 0.8:
                distribution["excellent"] += 1
            elif score >= 0.6:
                distribution["good"] += 1
            elif score >= 0.4:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1

        return distribution
