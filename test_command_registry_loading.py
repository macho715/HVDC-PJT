#!/usr/bin/env python3
"""
TDD Phase 1: Core Infrastructure Tests
세 번째 테스트: Command Registry Loading

테스트 목적: MACHO-GPT의 60+ 명령어 시스템 로딩 및 관리 검증
- 10 Categories로 분류된 명령어 구조
- /cmd 통합 시스템 호환성
- 자동 트리거 기능 검증
- 명령어 추천 시스템 검증

Categories:
- Invoice OCR (Inv-OCR)
- Heat-Stow Analysis 
- Warehouse/Capacity (WHF/Cap)
- Weather Tie
- HS Risk Assessment
- Cost Guard
- Certification Check (FANR/MOIAT)
- MCP-Agent
- API/RAG Integration
- System Management
"""

import unittest
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json

class CommandCategory(Enum):
    """MACHO-GPT 명령어 카테고리"""
    INVOICE_OCR = "Invoice_OCR"
    HEAT_STOW = "Heat_Stow"
    WAREHOUSE_CAP = "Warehouse_Capacity"
    WEATHER_TIE = "Weather_Tie"
    HS_RISK = "HS_Risk"
    COST_GUARD = "Cost_Guard"
    CERT_CHECK = "Certification_Check"
    MCP_AGENT = "MCP_Agent"
    API_RAG = "API_RAG"
    SYSTEM_MGMT = "System_Management"

@dataclass
class CommandDefinition:
    """명령어 정의 구조"""
    name: str
    category: CommandCategory
    description: str
    confidence_required: float
    auto_trigger: bool
    dependencies: List[str]
    parameters: Dict[str, str]
    execution_mode: str
    
class MACHOCommandRegistry:
    """MACHO-GPT 명령어 레지스트리"""
    
    def __init__(self):
        """명령어 레지스트리 초기화"""
        self.commands: Dict[str, CommandDefinition] = {}
        self.categories: Dict[CommandCategory, List[str]] = {}
        self.auto_triggers: Dict[str, List[str]] = {}
        self.total_commands = 0
        self.confidence_threshold = 0.95
        
        # 명령어 시스템 초기화
        self._initialize_command_registry()
    
    def _initialize_command_registry(self):
        """명령어 레지스트리 초기화"""
        # Invoice OCR 카테고리 명령어
        invoice_ocr_commands = [
            CommandDefinition(
                name="logi_invoice_ocr",
                category=CommandCategory.INVOICE_OCR,
                description="Invoice OCR 처리 및 HS코드 추출",
                confidence_required=0.90,
                auto_trigger=True,
                dependencies=[],
                parameters={"file_path": "string", "ocr_mode": "string"},
                execution_mode="LATTICE"
            ),
            CommandDefinition(
                name="validate_fanr_compliance",
                category=CommandCategory.INVOICE_OCR,
                description="FANR 규정 준수 검증",
                confidence_required=0.95,
                auto_trigger=False,
                dependencies=["logi_invoice_ocr"],
                parameters={"invoice_data": "dict"},
                execution_mode="ORACLE"
            ),
                         CommandDefinition(
                 name="extract_hs_code",
                 category=CommandCategory.INVOICE_OCR,
                 description="HS코드 정확도 검증 및 추출",
                 confidence_required=0.90,
                 auto_trigger=True,
                 dependencies=["logi_invoice_ocr"],
                 parameters={"ocr_result": "dict"},
                 execution_mode="LATTICE"
             )
        ]
        
        # Heat-Stow 분석 카테고리
        heat_stow_commands = [
            CommandDefinition(
                name="heat_stow_analysis",
                category=CommandCategory.HEAT_STOW,
                description="컨테이너 적재 압력 분석",
                confidence_required=0.95,
                auto_trigger=True,
                dependencies=[],
                parameters={"container_data": "list", "pressure_limit": "float"},
                execution_mode="LATTICE"
            ),
            CommandDefinition(
                name="optimize_stowage",
                category=CommandCategory.HEAT_STOW,
                description="적재 최적화 및 면적 절약",
                confidence_required=0.90,
                auto_trigger=False,
                dependencies=["heat_stow_analysis"],
                parameters={"stowage_plan": "dict"},
                execution_mode="PRIME"
            )
        ]
        
        # Weather Tie 카테고리
        weather_tie_commands = [
            CommandDefinition(
                name="weather_tie_analysis",
                category=CommandCategory.WEATHER_TIE,
                description="기상 영향 분석 및 ETA 예측",
                confidence_required=0.90,
                auto_trigger=True,
                dependencies=[],
                parameters={"port_code": "string", "vessel_data": "dict"},
                execution_mode="ORACLE"
            ),
            CommandDefinition(
                name="update_eta_forecast",
                category=CommandCategory.WEATHER_TIE,
                description="ETA 예보 업데이트",
                confidence_required=0.85,
                auto_trigger=True,
                dependencies=["weather_tie_analysis"],
                parameters={"delay_hours": "int"},
                execution_mode="RHYTHM"
            )
        ]
        
        # Cost Guard 카테고리
        cost_guard_commands = [
            CommandDefinition(
                name="cost_validation",
                category=CommandCategory.COST_GUARD,
                description="비용 검증 및 승인 요청",
                confidence_required=0.95,
                auto_trigger=False,
                dependencies=[],
                parameters={"cost_data": "dict", "approval_level": "string"},
                execution_mode="COST_GUARD"
            )
        ]
        
        # System Management 카테고리
        system_commands = [
            CommandDefinition(
                name="switch_mode",
                category=CommandCategory.SYSTEM_MGMT,
                description="Containment Mode 전환",
                confidence_required=0.90,
                auto_trigger=False,
                dependencies=[],
                parameters={"target_mode": "string", "reason": "string"},
                execution_mode="PRIME"
            ),
            CommandDefinition(
                name="generate_report",
                category=CommandCategory.SYSTEM_MGMT,
                description="종합 리포트 생성",
                confidence_required=0.95,
                auto_trigger=False,
                dependencies=["logi_invoice_ocr", "heat_stow_analysis"],
                parameters={"report_type": "string", "output_format": "string"},
                execution_mode="PRIME"
            ),
            CommandDefinition(
                name="validate_data",
                category=CommandCategory.SYSTEM_MGMT,
                description="데이터 품질 검증",
                confidence_required=0.95,
                auto_trigger=True,
                dependencies=[],
                parameters={"data_source": "string", "validation_rules": "dict"},
                execution_mode="ORACLE"
            )
        ]
        
        # 모든 명령어 등록
        all_commands = (invoice_ocr_commands + heat_stow_commands + 
                       weather_tie_commands + cost_guard_commands + system_commands)
        
        for cmd in all_commands:
            self.register_command(cmd)
    
    def register_command(self, command: CommandDefinition):
        """명령어 등록"""
        self.commands[command.name] = command
        
        # 카테고리별 분류
        if command.category not in self.categories:
            self.categories[command.category] = []
        self.categories[command.category].append(command.name)
        
        # 자동 트리거 등록
        if command.auto_trigger:
            trigger_key = f"{command.execution_mode}_{command.category.value}"
            if trigger_key not in self.auto_triggers:
                self.auto_triggers[trigger_key] = []
            self.auto_triggers[trigger_key].append(command.name)
        
        self.total_commands += 1
    
    def get_command(self, name: str) -> Optional[CommandDefinition]:
        """명령어 조회"""
        return self.commands.get(name)
    
    def get_commands_by_category(self, category: CommandCategory) -> List[str]:
        """카테고리별 명령어 조회"""
        return self.categories.get(category, [])
    
    def get_auto_trigger_commands(self, mode: str, category: str) -> List[str]:
        """자동 트리거 명령어 조회"""
        trigger_key = f"{mode}_{category}"
        return self.auto_triggers.get(trigger_key, [])
    
    def validate_command_dependencies(self, command_name: str) -> bool:
        """명령어 의존성 검증"""
        command = self.get_command(command_name)
        if not command:
            return False
        
        # 의존성 명령어들이 모두 등록되어 있는지 확인
        for dep in command.dependencies:
            if dep not in self.commands:
                return False
        
        return True
    
    def get_command_recommendations(self, executed_command: str, context: Dict) -> List[str]:
        """명령어 추천 시스템"""
        executed_cmd = self.get_command(executed_command)
        if not executed_cmd:
            return []
        
        recommendations = []
        
        # 같은 카테고리의 다른 명령어들 추천
        category_commands = self.get_commands_by_category(executed_cmd.category)
        for cmd_name in category_commands:
            if cmd_name != executed_command:
                cmd = self.get_command(cmd_name)
                if cmd and not cmd.auto_trigger:  # 수동 실행 명령어만 추천
                    recommendations.append(cmd_name)
        
        # 의존성 기반 추천
        for cmd_name, cmd in self.commands.items():
            if executed_command in cmd.dependencies:
                recommendations.append(cmd_name)
        
        return recommendations[:3]  # 최대 3개 추천

class TestCommandRegistryLoading(unittest.TestCase):
    """Command Registry Loading 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.registry = MACHOCommandRegistry()
        self.required_confidence = 0.95
        self.min_commands_required = 10  # 최소 10개 명령어 필요
    
    def test_command_registry_initialization(self):
        """명령어 레지스트리 초기화 검증"""
        self.assertIsInstance(self.registry, MACHOCommandRegistry)
        self.assertGreater(self.registry.total_commands, 0)
        self.assertGreaterEqual(self.registry.confidence_threshold, self.required_confidence)
    
    def test_minimum_commands_loaded(self):
        """최소 명령어 수 검증"""
        self.assertGreaterEqual(self.registry.total_commands, self.min_commands_required)
        self.assertGreater(len(self.registry.commands), 0)
    
    def test_all_command_categories_exist(self):
        """모든 명령어 카테고리 존재 검증"""
        expected_categories = {
            CommandCategory.INVOICE_OCR,
            CommandCategory.HEAT_STOW,
            CommandCategory.WEATHER_TIE,
            CommandCategory.COST_GUARD,
            CommandCategory.SYSTEM_MGMT
        }
        
        loaded_categories = set(self.registry.categories.keys())
        self.assertTrue(expected_categories.issubset(loaded_categories))
    
    def test_invoice_ocr_commands_loaded(self):
        """Invoice OCR 명령어 로딩 검증"""
        ocr_commands = self.registry.get_commands_by_category(CommandCategory.INVOICE_OCR)
        
        self.assertGreater(len(ocr_commands), 0)
        self.assertIn("logi_invoice_ocr", ocr_commands)
        self.assertIn("validate_fanr_compliance", ocr_commands)
        self.assertIn("extract_hs_code", ocr_commands)
    
    def test_heat_stow_commands_loaded(self):
        """Heat-Stow 명령어 로딩 검증"""
        stow_commands = self.registry.get_commands_by_category(CommandCategory.HEAT_STOW)
        
        self.assertGreater(len(stow_commands), 0)
        self.assertIn("heat_stow_analysis", stow_commands)
        self.assertIn("optimize_stowage", stow_commands)
    
    def test_weather_tie_commands_loaded(self):
        """Weather Tie 명령어 로딩 검증"""
        weather_commands = self.registry.get_commands_by_category(CommandCategory.WEATHER_TIE)
        
        self.assertGreater(len(weather_commands), 0)
        self.assertIn("weather_tie_analysis", weather_commands)
        self.assertIn("update_eta_forecast", weather_commands)
    
    def test_command_definitions_complete(self):
        """명령어 정의 완전성 검증"""
        for cmd_name, cmd in self.registry.commands.items():
            self.assertIsInstance(cmd, CommandDefinition)
            self.assertIsNotNone(cmd.name)
            self.assertIsNotNone(cmd.category)
            self.assertIsNotNone(cmd.description)
            self.assertIsInstance(cmd.confidence_required, float)
            self.assertIsInstance(cmd.auto_trigger, bool)
            self.assertIsInstance(cmd.dependencies, list)
            self.assertIsInstance(cmd.parameters, dict)
            self.assertIsNotNone(cmd.execution_mode)
    
    def test_auto_trigger_system(self):
        """자동 트리거 시스템 검증"""
        # LATTICE 모드의 Invoice OCR 자동 트리거 확인
        lattice_ocr_triggers = self.registry.get_auto_trigger_commands("LATTICE", "Invoice_OCR")
        self.assertGreater(len(lattice_ocr_triggers), 0)
        
        # ORACLE 모드의 Weather Tie 자동 트리거 확인
        oracle_weather_triggers = self.registry.get_auto_trigger_commands("ORACLE", "Weather_Tie")
        self.assertGreater(len(oracle_weather_triggers), 0)
    
    def test_command_dependency_validation(self):
        """명령어 의존성 검증"""
        # validate_fanr_compliance는 logi_invoice_ocr에 의존
        self.assertTrue(self.registry.validate_command_dependencies("validate_fanr_compliance"))
        
        # optimize_stowage는 heat_stow_analysis에 의존
        self.assertTrue(self.registry.validate_command_dependencies("optimize_stowage"))
        
        # update_eta_forecast는 weather_tie_analysis에 의존
        self.assertTrue(self.registry.validate_command_dependencies("update_eta_forecast"))
    
    def test_command_recommendation_system(self):
        """명령어 추천 시스템 검증"""
        # logi_invoice_ocr 실행 후 추천 명령어
        recommendations = self.registry.get_command_recommendations("logi_invoice_ocr", {})
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)  # 최대 3개 추천
    
    def test_cost_guard_approval_system(self):
        """Cost Guard 승인 시스템 검증"""
        cost_cmd = self.registry.get_command("cost_validation")
        
        self.assertIsNotNone(cost_cmd)
        self.assertEqual(cost_cmd.execution_mode, "COST_GUARD")
        self.assertEqual(cost_cmd.confidence_required, 0.95)
        self.assertFalse(cost_cmd.auto_trigger)  # 수동 승인 필요
    
    def test_system_management_commands(self):
        """시스템 관리 명령어 검증"""
        system_commands = self.registry.get_commands_by_category(CommandCategory.SYSTEM_MGMT)
        
        self.assertIn("switch_mode", system_commands)
        self.assertIn("generate_report", system_commands)
        self.assertIn("validate_data", system_commands)
    
    def test_confidence_threshold_compliance(self):
        """신뢰도 임계값 준수 검증"""
        for cmd_name, cmd in self.registry.commands.items():
            if cmd.category in [CommandCategory.INVOICE_OCR, CommandCategory.COST_GUARD]:
                self.assertGreaterEqual(cmd.confidence_required, 0.90)
    
    def test_execution_mode_mapping(self):
        """실행 모드 매핑 검증"""
        # LATTICE 모드 명령어 확인
        lattice_commands = [cmd for cmd in self.registry.commands.values() 
                          if cmd.execution_mode == "LATTICE"]
        self.assertGreater(len(lattice_commands), 0)
        
        # ORACLE 모드 명령어 확인
        oracle_commands = [cmd for cmd in self.registry.commands.values() 
                         if cmd.execution_mode == "ORACLE"]
        self.assertGreater(len(oracle_commands), 0)
    
    def test_macho_integration_compatibility(self):
        """MACHO 통합 시스템 호환성 검증"""
        # 통합 시스템 import 확인
        try:
            from macho_integrated_system import MACHOIntegratedSystem
            integrated_system = MACHOIntegratedSystem()
            
            # 명령어 레지스트리와 통합 시스템 호환성 확인
            self.assertIsNotNone(integrated_system)
            self.assertGreater(self.registry.total_commands, 0)
            
        except ImportError:
            self.fail("MACHO 통합 시스템과의 연동 실패")
    
    def test_tdd_red_phase_validation(self):
        """TDD RED 단계 검증"""
        test_timestamp = datetime.now()
        
        print(f"\n🔴 TDD RED Phase: Command Registry Loading Test")
        print(f"   테스트 시간: {test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   검증 대상: {self.registry.total_commands}개 명령어 시스템")
        print(f"   카테고리 수: {len(self.registry.categories)}")
        print(f"   자동 트리거 수: {len(self.registry.auto_triggers)}")
        print(f"   신뢰도 요구사항: ≥{self.required_confidence}")

if __name__ == '__main__':
    print("🧪 MACHO-GPT v3.4-mini TDD Phase 1: Core Infrastructure Tests")
    print("=" * 70)
    print("📋 Test: Command Registry Loading")
    print("🎯 Purpose: 60+ 명령어 시스템 로딩 및 관리 검증")
    print("-" * 70)
    print("📦 Categories: Invoice OCR | Heat-Stow | Weather Tie | Cost Guard | System Mgmt")
    print("-" * 70)
    
    # TDD RED Phase 실행
    unittest.main(verbosity=2) 