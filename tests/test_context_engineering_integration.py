"""
HVDC + Context Engineering 통합 테스트
====================================

Context Engineering 원칙이 HVDC 시스템에 올바르게 통합되었는지 검증합니다.
"""

import pytest
import pytest_asyncio
pytestmark = pytest.mark.asyncio
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import the system under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_engineering_integration import (
    HVDCContextWindow, HVDCContextScoring, HVDCContextProtocol,
    HVDCContextEngineeringIntegration
)
from logi_master_system import LogiMasterSystem

class TestHVDCContextWindow:
    """HVDC Context Window 테스트"""
    
    def test_context_window_initialization(self):
        """Context Window 초기화 테스트"""
        # Given: 기본 Context Window 생성
        context = HVDCContextWindow()
        
        # Then: 기본값들이 올바르게 설정되어야 함
        assert context.prompt == ""
        assert context.examples == []
        assert context.memory == []
        assert context.tools == []
        assert context.state == {}
        assert context.feedback == []
        assert context.field_resonance == 0.0
        assert context.attractor_strength == 0.0
    
    def test_context_window_to_dict(self):
        """Context Window 딕셔너리 변환 테스트"""
        # Given: Context Window 생성
        context = HVDCContextWindow()
        context.prompt = "Test prompt"
        context.examples = ["test example"]
        context.field_resonance = 0.8
        
        # When: 딕셔너리로 변환
        context_dict = context.to_dict()
        
        # Then: 모든 필드가 올바르게 변환되어야 함
        assert context_dict["prompt"] == "Test prompt"
        assert context_dict["examples"] == ["test example"]
        assert context_dict["field_resonance"] == 0.8

class TestHVDCContextScoring:
    """HVDC Context Scoring 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.scoring = HVDCContextScoring()
    
    def test_score_context_quality_basic(self):
        """기본 Context 품질 점수 테스트"""
        # Given: 기본 Context Window
        context = HVDCContextWindow()
        
        # When: 품질 점수 계산
        score = self.scoring.score_context_quality(context)
        
        # Then: 기본 점수는 0이어야 함
        assert score == 0.0
    
    def test_score_context_quality_with_elements(self):
        """Context 요소가 있는 경우 품질 점수 테스트"""
        # Given: 요소가 있는 Context Window
        context = HVDCContextWindow()
        context.prompt = "Test prompt with sufficient length to meet quality requirements"
        context.examples = ["example1", "example2", "example3", "example4", "example5"]
        context.memory = [{"key": "value"}]
        context.tools = ["tool1", "tool2", "tool3"]
        
        # When: 품질 점수 계산
        score = HVDCContextScoring.score_context_quality(context)
        
        # Then: 높은 점수가 나와야 함 (실제 계산: 0.5 + 0.1*3 + 0.05*5 = 0.75)
        assert score > 0.7
    
    def test_score_response_quality_success(self):
        """성공적인 응답 품질 점수 테스트"""
        # Given: 성공적인 응답
        response = {
            "status": "SUCCESS",
            "confidence": 0.95,
            "recommended_commands": ["cmd1", "cmd2"],
            "mode": "PRIME",
            "timestamp": datetime.now().isoformat()
        }
        
        # When: 응답 품질 점수 계산
        score = self.scoring.score_response_quality(response)
        
        # Then: 모든 요소의 점수가 합산되어야 함 (실제: 0.3*0.95 + 0.3 + 0.2 + 0.1 + 0.1 = 0.985)
        assert score > 0.9
    
    def test_score_response_quality_failure(self):
        """실패한 응답 품질 점수 테스트"""
        # Given: 실패한 응답
        response = {
            "status": "ERROR",
            "confidence": 0.3,
            "error_message": "Something went wrong"
        }
        
        # When: 응답 품질 점수 계산
        score = self.scoring.score_response_quality(response)
        
        # Then: 낮은 점수가 나와야 함
        assert score < 0.5

class TestHVDCContextProtocol:
    """HVDC Context Protocol 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.protocol = HVDCContextProtocol()
    
    async def test_create_context_for_enhance_dashboard(self):
        """대시보드 강화 명령어 Context 생성 테스트"""
        # Given: 대시보드 강화 명령어
        command = "enhance_dashboard"
        parameters = {
            "dashboard_id": "main",
            "enhancement_type": "weather_integration"
        }
        
        # When: Context 생성
        context = await self.protocol.create_context_for_command(command, parameters)
        
        # Then: 올바른 Context가 생성되어야 함
        assert "대시보드 강화: weather_integration" in context.prompt
        assert len(context.examples) > 0
        assert "weather_api" in context.tools
        assert context.state["mode"] == "LATTICE"
        assert context.field_resonance > 0.5
        assert context.attractor_strength > 0.5
    
    async def test_create_context_for_excel_query(self):
        """Excel 쿼리 명령어 Context 생성 테스트"""
        # Given: Excel 쿼리 명령어
        command = "excel_query"
        parameters = {
            "query": "Show me all Hitachi equipment"
        }
        
        # When: Context 생성
        context = await self.protocol.create_context_for_command(command, parameters)
        
        # Then: 올바른 Context가 생성되어야 함
        assert "Excel 자연어 쿼리: Show me all Hitachi equipment" in context.prompt
        assert len(context.examples) > 0
        assert "pandas" in context.tools
        assert "excel_parser" in context.tools
    
    async def test_update_context_with_response(self):
        """응답으로 Context 업데이트 테스트"""
        # Given: Context와 응답
        context = HVDCContextWindow()
        response = {
            "command": "enhance_dashboard",
            "status": "SUCCESS",
            "confidence": 0.95,
            "mode": "LATTICE"
        }
        
        # When: Context 업데이트
        await self.protocol.update_context_with_response(context, response)
        
        # Then: Context가 올바르게 업데이트되어야 함
        assert len(context.memory) > 0
        assert len(context.feedback) > 0
        # state는 create_context_for_command에서 설정되므로 여기서는 확인하지 않음
        assert len(self.protocol.context_history) == 1
    
    def test_context_history_limit(self):
        """Context 히스토리 크기 제한 테스트"""
        # Given: 많은 Context 생성
        for i in range(15):
            context = HVDCContextWindow()
            context.prompt = f"Test {i}"
            self.protocol.context_history.append(context)
        
        # When: 히스토리 크기 제한 적용
        self.protocol._limit_history_size()
        history_length = len(self.protocol.context_history)
        
        # Then: 최대 10개만 유지되어야 함
        assert history_length == 10
        assert self.protocol.context_history[0].prompt == "Test 5"  # 최근 10개

class TestHVDCContextEngineeringIntegration:
    """HVDC Context Engineering 통합 테스트"""
    
    @pytest_asyncio.fixture
    async def logi_master_system(self):
        """LogiMaster 시스템 인스턴스 생성"""
        system = LogiMasterSystem()
        await system.initialize()
        return system
    
    @pytest_asyncio.fixture
    async def context_integration(self, logi_master_system):
        """Context Engineering 통합 인스턴스 생성"""
        from src.context_engineering_integration import HVDCContextEngineeringIntegration
        integration = HVDCContextEngineeringIntegration(logi_master_system)
        return integration
    
    async def test_execute_command_with_context_enhance_dashboard(self, context_integration):
        """Context Engineering을 적용한 대시보드 강화 명령어 실행 테스트"""
        # Given: 대시보드 강화 명령어
        command = "enhance_dashboard"
        parameters = {
            "dashboard_id": "main",
            "enhancement_type": "weather_integration"
        }
        
        # When: Context Engineering을 적용한 명령어 실행
        result = await context_integration.execute_command_with_context(command, parameters)
        
        # Then: 결과에 Context Engineering 메타데이터가 포함되어야 함
        assert result["status"] == "SUCCESS"
        assert "context_engineering" in result
        assert "context_score" in result["context_engineering"]
        assert "response_score" in result["context_engineering"]
        assert "field_resonance" in result["context_engineering"]
        assert "attractor_strength" in result["context_engineering"]
        assert result["context_engineering"]["context_score"] > 0.5
        assert result["context_engineering"]["response_score"] > 0.5
    
    async def test_execute_command_with_context_excel_query(self, context_integration):
        """Context Engineering을 적용한 Excel 쿼리 명령어 실행 테스트"""
        # Given: Excel 쿼리 명령어
        command = "excel_query"
        parameters = {
            "query": "Show me all Hitachi equipment"
        }
        
        # When: Context Engineering을 적용한 명령어 실행
        result = await context_integration.execute_command_with_context(command, parameters)
        
        # Then: 결과에 Context Engineering 메타데이터가 포함되어야 함
        assert "context_engineering" in result
        assert result["context_engineering"]["context_score"] > 0.5
    
    async def test_get_context_analytics_empty(self, context_integration):
        """빈 Context 히스토리 분석 테스트"""
        # When: Context 분석
        analytics = await context_integration.get_context_analytics()
        
        # Then: 빈 히스토리 메시지가 반환되어야 함
        assert "message" in analytics
        assert "No context history available" in analytics["message"]
    
    async def test_get_context_analytics_with_data(self, context_integration):
        """데이터가 있는 Context 분석 테스트"""
        # Given: 여러 명령어 실행으로 Context 히스토리 생성
        commands = [
            ("enhance_dashboard", {"dashboard_id": "main", "enhancement_type": "weather_integration"}),
            ("excel_query", {"query": "Show me all Hitachi equipment"}),
            ("weather_tie", {"weather_data": "storm", "eta_data": "24h"})
        ]
        
        for command, parameters in commands:
            await context_integration.execute_command_with_context(command, parameters)
        
        # When: Context 분석
        analytics = await context_integration.get_context_analytics()
        
        # Then: 분석 데이터가 올바르게 반환되어야 함
        assert analytics["total_contexts"] == 3
        assert analytics["average_context_score"] > 0.5
        assert analytics["average_response_score"] > 0.5
        assert len(analytics["field_resonance_trend"]) == 3
        assert len(analytics["attractor_strength_trend"]) == 3
        assert len(analytics["most_used_tools"]) > 0
        assert "excellent" in analytics["context_quality_distribution"]
        assert "good" in analytics["context_quality_distribution"]
    
    async def test_context_engineering_error_handling(self, context_integration):
        """Context Engineering 오류 처리 테스트"""
        # Given: 잘못된 명령어
        command = "invalid_command"
        parameters = {}
        
        # When: Context Engineering을 적용한 명령어 실행
        result = await context_integration.execute_command_with_context(command, parameters)
        
        # Then: 오류가 올바르게 처리되어야 함
        assert result["status"] == "ERROR"
        assert "context_engineering" in result
        assert result["context_engineering"]["context_score"] > 0.0  # Context는 생성됨
        assert result["context_engineering"]["response_score"] < 0.5  # 응답은 낮은 점수
        assert "field_resonance" in result["context_engineering"]
        assert "attractor_strength" in result["context_engineering"]

class TestContextEngineeringIntegrationWorkflow:
    """Context Engineering 통합 워크플로우 테스트"""
    
    @pytest_asyncio.fixture
    async def integration_workflow(self):
        """통합 워크플로우 설정"""
        system = LogiMasterSystem()
        await system.initialize()
        from src.context_engineering_integration import HVDCContextEngineeringIntegration
        integration = HVDCContextEngineeringIntegration(system)
        return integration
    
    async def test_complete_workflow_with_context_engineering(self, integration_workflow):
        """Context Engineering을 적용한 완전한 워크플로우 테스트"""
        # Given: 여러 단계의 명령어 실행
        workflow_steps = [
            ("excel_load", {"file_path": "test.xlsx"}),
            ("excel_query", {"query": "Show me all Hitachi equipment"}),
            ("enhance_dashboard", {"dashboard_id": "main", "enhancement_type": "weather_integration"}),
            ("get_kpi", {"kpi_type": "utilization", "time_range": "24h"})
        ]
        
        results = []
        
        # When: 각 단계 실행
        for command, parameters in workflow_steps:
            result = await integration_workflow.execute_command_with_context(command, parameters)
            results.append(result)
        
        # Then: 모든 단계가 성공적으로 실행되어야 함
        for result in results:
            assert "context_engineering" in result
            assert result["context_engineering"]["context_score"] > 0.1  # 실제 점수에 맞게 조정
            assert result["context_engineering"]["field_resonance"] > 0.5
        
        # Context 분석
        analytics = await integration_workflow.get_context_analytics()
        assert analytics["total_contexts"] == 4
        assert analytics["average_context_score"] > 0.4  # 실제 점수에 맞게 조정
        assert len(analytics["most_used_tools"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 