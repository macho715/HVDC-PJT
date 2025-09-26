#!/usr/bin/env python3
"""
LOGI MASTER SYSTEM v3.4-mini
============================
HVDC Project - Samsung C&T | ADNOC·DSV Partnership
통합 물류 관리 시스템 (Shrimp Task Manager + 대시보드 + 온톨로지)

하위 구조:
- Task Management Layer (Shrimp Task Manager)
- Dashboard Integration Layer (대시보드 진입점)
- Ontology Knowledge Layer (온톨로지 엔진)
- MACHO-GPT AI Layer (AI 통합 제어)
"""

import pandas as pd
import numpy as np
import json
import yaml
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================


@dataclass
class LogiTask:
    """물류 작업 데이터 구조"""

    id: str
    title: str
    description: str
    category: str
    priority: int
    status: str = "pending"
    assigned_to: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.0
    mode: str = "PRIME"
    kpi_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogiDashboard:
    """대시보드 데이터 구조"""

    id: str
    name: str
    type: str
    url: str
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class LogiOntology:
    """온톨로지 데이터 구조"""

    id: str
    name: str
    namespace: str
    classes: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    instances: int = 0
    last_sync: datetime = field(default_factory=datetime.now)


@dataclass
class LogiCommand:
    """명령어 데이터 구조"""

    name: str
    description: str
    category: str
    handler: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


# ============================================================================
# ABSTRACT BASE CLASSES
# ============================================================================


class LogiLayer(ABC):
    """LOGI MASTER 시스템 레이어 기본 클래스"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_active = True
        self.logger = logging.getLogger(f"LogiMaster.{name}")

    @abstractmethod
    async def initialize(self) -> bool:
        """레이어 초기화"""
        pass

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """데이터 처리"""
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """상태 조회"""
        pass


# ============================================================================
# TASK MANAGEMENT LAYER (Shrimp Task Manager)
# ============================================================================


class TaskManagementLayer(LogiLayer):
    """작업 관리 레이어 - Shrimp Task Manager 통합"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("TaskManagement", config)
        self.tasks: Dict[str, LogiTask] = {}
        self.task_counter = 0
        self.db_path = config.get("database_path", "logi_tasks.db")
        self._init_database()

    def _init_database(self):
        """작업 데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    priority INTEGER,
                    status TEXT,
                    assigned_to TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    due_date TEXT,
                    tags TEXT,
                    confidence REAL,
                    mode TEXT,
                    kpi_metrics TEXT
                )
            """
            )
            conn.commit()
            conn.close()
            self.logger.info("Task database initialized successfully")
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")

    async def initialize(self) -> bool:
        """작업 관리 레이어 초기화"""
        try:
            # 기본 작업 생성
            default_tasks = [
                LogiTask(
                    id="TASK-001",
                    title="송장 OCR 처리 시스템 구축",
                    description="FANR/MOIAT 규정 준수 OCR 시스템 개발",
                    category="AI_DEVELOPMENT",
                    priority=1,
                    mode="LATTICE",
                ),
                LogiTask(
                    id="TASK-002",
                    title="컨테이너 적재 최적화",
                    description="Heat-Stow 분석 기반 적재 알고리즘 개발",
                    category="OPTIMIZATION",
                    priority=2,
                    mode="RHYTHM",
                ),
                LogiTask(
                    id="TASK-003",
                    title="창고 입출고 분석",
                    description="실시간 창고 운영 KPI 분석 시스템",
                    category="ANALYTICS",
                    priority=3,
                    mode="ORACLE",
                ),
            ]

            for task in default_tasks:
                await self.create_task(task)

            self.logger.info(
                f"TaskManagement layer initialized with {len(default_tasks)} default tasks"
            )
            return True
        except Exception as e:
            self.logger.error(f"TaskManagement initialization failed: {e}")
            return False

    async def create_task(self, task: LogiTask) -> bool:
        """작업 생성"""
        try:
            self.task_counter += 1
            task.id = f"TASK-{self.task_counter:03d}"
            task.created_at = datetime.now()
            task.updated_at = datetime.now()

            self.tasks[task.id] = task

            # 데이터베이스 저장
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO tasks 
                (id, title, description, category, priority, status, assigned_to, 
                 created_at, updated_at, due_date, tags, confidence, mode, kpi_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.id,
                    task.title,
                    task.description,
                    task.category,
                    task.priority,
                    task.status,
                    task.assigned_to,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                    task.due_date.isoformat() if task.due_date else None,
                    json.dumps(task.tags),
                    task.confidence,
                    task.mode,
                    json.dumps(task.kpi_metrics),
                ),
            )
            conn.commit()
            conn.close()

            self.logger.info(f"Task created: {task.id} - {task.title}")
            return True
        except Exception as e:
            self.logger.error(f"Task creation failed: {e}")
            return False

    async def list_tasks(self) -> List[LogiTask]:
        """작업 목록 조회"""
        return list(self.tasks.values())

    async def get_task_analytics(self) -> Dict[str, Any]:
        """작업 분석 데이터"""
        if not self.tasks:
            return {"total_tasks": 0, "completion_rate": 0.0}

        total_tasks = len(self.tasks)
        completed_tasks = len(
            [t for t in self.tasks.values() if t.status == "completed"]
        )
        completion_rate = (completed_tasks / total_tasks) * 100

        status_distribution = {}
        for task in self.tasks.values():
            status_distribution[task.status] = (
                status_distribution.get(task.status, 0) + 1
            )

        return {
            "total_tasks": total_tasks,
            "completion_rate": completion_rate,
            "status_distribution": status_distribution,
            "recent_tasks": sorted(
                list(self.tasks.values())[-5:], key=lambda x: x.created_at, reverse=True
            ),
        }

    async def process(self, data: Any) -> Any:
        """작업 데이터 처리"""
        if isinstance(data, dict):
            if data.get("action") == "create_task":
                task = LogiTask(**data.get("task_data", {}))
                return await self.create_task(task)
            elif data.get("action") == "list_tasks":
                return await self.list_tasks()
            elif data.get("action") == "get_analytics":
                return await self.get_task_analytics()
        return None

    async def get_status(self) -> Dict[str, Any]:
        """작업 관리 레이어 상태"""
        analytics = await self.get_task_analytics()
        return {
            "layer": "TaskManagement",
            "is_active": self.is_active,
            "total_tasks": analytics["total_tasks"],
            "completion_rate": analytics["completion_rate"],
            "database_path": self.db_path,
        }


# ============================================================================
# DASHBOARD INTEGRATION LAYER
# ============================================================================


class DashboardIntegrationLayer(LogiLayer):
    """대시보드 통합 레이어"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("DashboardIntegration", config)
        self.dashboards: Dict[str, LogiDashboard] = {}
        self.dashboard_config = config.get("dashboards", {})
        self._init_dashboards()

    def _init_dashboards(self):
        """대시보드 초기화"""
        default_dashboards = [
            LogiDashboard(
                id="main",
                name="HVDC Logistics System",
                type="main_entry",
                url="index.html",
                description="Samsung C&T | ADNOC·DSV Partnership 메인 대시보드",
            ),
            LogiDashboard(
                id="warehouse",
                name="Warehouse Monitor",
                type="monitoring",
                url="hvdc_warehouse_monitor.html",
                description="실시간 창고 운영 모니터링",
            ),
            LogiDashboard(
                id="inventory",
                name="Inventory Tracking",
                type="tracking",
                url="hvdc_inventory_tracking.html",
                description="종합 재고 관리 시스템",
            ),
            LogiDashboard(
                id="kpi",
                name="MACHO KPI Dashboard",
                type="kpi",
                url="macho_realtime_kpi_dashboard.py",
                description="실시간 KPI 모니터링",
            ),
            LogiDashboard(
                id="tdd",
                name="TDD Progress Dashboard",
                type="development",
                url="tdd_progress_dashboard.html",
                description="TDD 개발 진행 상황",
            ),
        ]

        for dashboard in default_dashboards:
            self.dashboards[dashboard.id] = dashboard

    async def initialize(self) -> bool:
        """대시보드 통합 레이어 초기화"""
        try:
            # 대시보드 상태 업데이트
            for dashboard in self.dashboards.values():
                dashboard.last_updated = datetime.now()
                dashboard.metrics = {
                    "access_count": 0,
                    "last_access": None,
                    "is_available": True,
                }

            self.logger.info(
                f"DashboardIntegration layer initialized with {len(self.dashboards)} dashboards"
            )
            return True
        except Exception as e:
            self.logger.error(f"DashboardIntegration initialization failed: {e}")
            return False

    async def get_dashboard_list(self) -> List[LogiDashboard]:
        """대시보드 목록 조회"""
        return list(self.dashboards.values())

    async def access_dashboard(self, dashboard_id: str) -> Optional[LogiDashboard]:
        """대시보드 접근"""
        if dashboard_id in self.dashboards:
            dashboard = self.dashboards[dashboard_id]
            dashboard.metrics["access_count"] += 1
            dashboard.metrics["last_access"] = datetime.now()
            dashboard.last_updated = datetime.now()
            return dashboard
        return None

    async def process(self, data: Any) -> Any:
        """대시보드 데이터 처리"""
        if isinstance(data, dict):
            if data.get("action") == "list_dashboards":
                return await self.get_dashboard_list()
            elif data.get("action") == "access_dashboard":
                return await self.access_dashboard(data.get("dashboard_id"))
        return None

    async def get_status(self) -> Dict[str, Any]:
        """대시보드 통합 레이어 상태"""
        return {
            "layer": "DashboardIntegration",
            "is_active": self.is_active,
            "total_dashboards": len(self.dashboards),
            "active_dashboards": len(
                [d for d in self.dashboards.values() if d.is_active]
            ),
            "dashboard_types": list(set(d.type for d in self.dashboards.values())),
        }


# ============================================================================
# ONTOLOGY KNOWLEDGE LAYER
# ============================================================================


class OntologyKnowledgeLayer(LogiLayer):
    """온톨로지 지식 레이어"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("OntologyKnowledge", config)
        self.ontologies: Dict[str, LogiOntology] = {}
        self.ontology_path = config.get("ontology_path", "hvdc_ontology_system/")
        self._init_ontologies()

    def _init_ontologies(self):
        """온톨로지 초기화"""
        default_ontologies = [
            LogiOntology(
                id="hvdc_main",
                name="HVDC Main Ontology",
                namespace="http://hvdc.samsung-ct.com/ontology#",
                classes=["Container", "Warehouse", "Shipment", "Invoice", "Task"],
                properties=["hasLocation", "hasStatus", "hasPriority", "belongsTo"],
                instances=0,
            ),
            LogiOntology(
                id="logistics",
                name="Logistics Domain Ontology",
                namespace="http://logistics.samsung-ct.com/ontology#",
                classes=["LogisticsOperation", "TransportMode", "Route", "Cost"],
                properties=["usesMode", "followsRoute", "hasCost", "requiresApproval"],
                instances=0,
            ),
            LogiOntology(
                id="regulatory",
                name="Regulatory Compliance Ontology",
                namespace="http://regulatory.samsung-ct.com/ontology#",
                classes=["FANR", "MOIAT", "Compliance", "Certificate"],
                properties=[
                    "requiresCompliance",
                    "hasCertificate",
                    "validates",
                    "approves",
                ],
                instances=0,
            ),
        ]

        for ontology in default_ontologies:
            self.ontologies[ontology.id] = ontology

    async def initialize(self) -> bool:
        """온톨로지 지식 레이어 초기화"""
        try:
            # 온톨로지 파일 동기화
            for ontology in self.ontologies.values():
                ontology.last_sync = datetime.now()
                # 실제 파일 존재 여부 확인
                ttl_file = Path(f"{self.ontology_path}ontology/{ontology.id}.ttl")
                if ttl_file.exists():
                    ontology.instances = 100  # 예시 값
                else:
                    ontology.instances = 0

            self.logger.info(
                f"OntologyKnowledge layer initialized with {len(self.ontologies)} ontologies"
            )
            return True
        except Exception as e:
            self.logger.error(f"OntologyKnowledge initialization failed: {e}")
            return False

    async def get_ontology_list(self) -> List[LogiOntology]:
        """온톨로지 목록 조회"""
        return list(self.ontologies.values())

    async def query_ontology(self, ontology_id: str, query: str) -> Dict[str, Any]:
        """온톨로지 쿼리 실행"""
        if ontology_id in self.ontologies:
            ontology = self.ontologies[ontology_id]
            # 실제 SPARQL 쿼리 실행 로직 (예시)
            return {
                "ontology_id": ontology_id,
                "query": query,
                "result": f"Query executed on {ontology.name}",
                "timestamp": datetime.now().isoformat(),
            }
        return {"error": f"Ontology {ontology_id} not found"}

    async def process(self, data: Any) -> Any:
        """온톨로지 데이터 처리"""
        if isinstance(data, dict):
            if data.get("action") == "list_ontologies":
                return await self.get_ontology_list()
            elif data.get("action") == "query_ontology":
                return await self.query_ontology(
                    data.get("ontology_id"), data.get("query")
                )
        return None

    async def get_status(self) -> Dict[str, Any]:
        """온톨로지 지식 레이어 상태"""
        total_instances = sum(o.instances for o in self.ontologies.values())
        return {
            "layer": "OntologyKnowledge",
            "is_active": self.is_active,
            "total_ontologies": len(self.ontologies),
            "total_instances": total_instances,
            "ontology_path": self.ontology_path,
        }


# ============================================================================
# MACHO-GPT AI LAYER
# ============================================================================


class MachoGPTAILayer(LogiLayer):
    """MACHO-GPT AI 레이어 - Excel Agent 통합"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("MachoGPTAI", config)
        self.current_mode = "PRIME"
        self.confidence_threshold = 0.95
        self.excel_agent_integration = None
        self.excel_agent_adapter = None
        self._init_commands()

    def _init_commands(self):
        """MACHO-GPT 명령어 초기화"""
        self.commands = {
            # 기존 명령어들
            "enhance_dashboard": {
                "description": "대시보드 강화 기능",
                "handler": self._enhance_dashboard,
                "parameters": ["dashboard_id", "enhancement_type"],
            },
            "switch_mode": {
                "description": "MACHO-GPT 모드 전환",
                "handler": self._switch_mode,
                "parameters": ["new_mode"],
            },
            "get_kpi": {
                "description": "KPI 데이터 조회",
                "handler": self._get_kpi_data,
                "parameters": ["kpi_type", "time_range"],
            },
            "validate_fanr": {
                "description": "FANR 규정 준수 검증",
                "handler": self._validate_fanr_compliance,
                "parameters": ["certification_data"],
            },
            "optimize_stowage": {
                "description": "컨테이너 적재 최적화",
                "handler": self._optimize_container_stowage,
                "parameters": ["container_data", "pressure_limit"],
            },
            "weather_tie": {
                "description": "기상 조건 연동 분석",
                "handler": self._weather_tie_analysis,
                "parameters": ["weather_data", "eta_data"],
            },
            "analyze_architecture": {
                "description": "시스템 아키텍처 상세 분석",
                "handler": self._analyze_system_architecture,
                "parameters": ["analysis_type", "detail_level"],
            },
            "cost_guard": {
                "description": "비용 관리 및 모니터링",
                "handler": self._cost_guard_analysis,
                "parameters": ["cost_data", "budget_limit"],
            },
            "cert_check": {
                "description": "인증서 유효성 검증",
                "handler": self._certificate_validation,
                "parameters": ["certificate_data"],
            },
            # Excel Agent 통합 명령어들
            "excel_load": {
                "description": "Excel 파일 로드",
                "handler": self._excel_load_file,
                "parameters": ["file_path", "dataframe_name"],
            },
            "excel_query": {
                "description": "자연어 Excel 데이터 쿼리",
                "handler": self._excel_natural_query,
                "parameters": ["query", "dataframe_name"],
            },
            "excel_info": {
                "description": "Excel 데이터프레임 정보 조회",
                "handler": self._excel_get_info,
                "parameters": ["dataframe_name"],
            },
            "excel_export": {
                "description": "Excel 분석 리포트 내보내기",
                "handler": self._excel_export_report,
                "parameters": ["output_path"],
            },
            "excel_status": {
                "description": "Excel Agent 시스템 상태 조회",
                "handler": self._excel_get_status,
                "parameters": [],
            },
            "hvdc_analysis": {
                "description": "HVDC 특화 데이터 분석",
                "handler": self._hvdc_specific_analysis,
                "parameters": ["analysis_type", "parameters"],
            },
        }

        # Excel Agent 통합 초기화
        try:
            from excel_agent_integration import (
                ExcelAgentIntegration,
                ExcelAgentMACHOAdapter,
            )

            self.excel_agent_integration = ExcelAgentIntegration()
            self.excel_agent_adapter = ExcelAgentMACHOAdapter(
                self.excel_agent_integration
            )
            self.logger.info("Excel Agent integration initialized successfully")
        except ImportError as e:
            self.logger.warning(f"Excel Agent integration not available: {e}")
            self.excel_agent_integration = None
            self.excel_agent_adapter = None

    async def initialize(self) -> bool:
        """MACHO-GPT AI 레이어 초기화"""
        try:
            self.logger.info(
                f"MachoGPTAI layer initialized with {len(self.commands)} commands"
            )
            return True
        except Exception as e:
            self.logger.error(f"MachoGPTAI initialization failed: {e}")
            return False

    async def execute_command(
        self, command_name: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """MACHO-GPT 명령어 실행"""
        try:
            parameters = parameters or {}

            if command_name not in self.commands:
                return {
                    "status": "ERROR",
                    "error_message": f"Unknown command: {command_name}",
                    "confidence": 0.0,
                }

            command_info = self.commands[command_name]
            handler = command_info["handler"]

            # 명령어 실행
            result = await handler(parameters)

            # 결과에 명령어 정보 추가
            result["command"] = command_name
            result["mode"] = self.current_mode
            result["timestamp"] = datetime.now().isoformat()

            # 추천 명령어 추가 (기본 추천 명령어)
            result["recommended_commands"] = [
                "get_kpi - KPI 데이터 조회",
                "switch_mode - 모드 전환",
                "excel_status - Excel Agent 상태 확인",
            ]

            self.logger.info(f"Command executed: {command_name} -> {result['status']}")
            return result

        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {
                "status": "ERROR",
                "error_message": str(e),
                "confidence": 0.0,
                "command": command_name,
                "mode": self.current_mode,
                "timestamp": datetime.now().isoformat(),
            }

    async def switch_mode(self, new_mode: str) -> bool:
        """모드 전환"""
        valid_modes = ["PRIME", "LATTICE", "ORACLE", "RHYTHM", "COST-GUARD", "ZERO"]
        if new_mode in valid_modes:
            self.current_mode = new_mode
            self.logger.info(f"Mode switched to {new_mode}")
            return True
        return False

    async def process(self, data: Any) -> Any:
        """AI 데이터 처리"""
        if isinstance(data, dict):
            if data.get("action") == "execute_command":
                return await self.execute_command(
                    data.get("command_name"), data.get("parameters")
                )
            elif data.get("action") == "switch_mode":
                return await self.switch_mode(data.get("mode"))
        return None

    async def _enhance_dashboard(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """대시보드 강화 기능 구현"""
        try:
            if not parameters:
                return {
                    "status": "ERROR",
                    "error_message": "Parameters required for dashboard enhancement",
                }

            dashboard_id = parameters.get("dashboard_id")
            enhancement_type = parameters.get("enhancement_type")

            # 파라미터 검증
            valid_enhancement_types = [
                "weather_integration",
                "ocr_processing",
                "kpi_monitoring",
                "real_api_integration",
                "real_time_data",
            ]

            # 잘못된 파라미터 검증
            if not dashboard_id or not enhancement_type:
                return {
                    "status": "ERROR",
                    "error_message": "dashboard_id and enhancement_type are required",
                }

            if enhancement_type not in valid_enhancement_types:
                return {
                    "status": "ERROR",
                    "error_message": f"Invalid enhancement_type. Valid types: {valid_enhancement_types}",
                }

            # 대시보드 강화 로직 - enhancement_type에 따른 기능 분기
            if enhancement_type == "weather_integration":
                enhanced_features = [
                    "weather_data",
                    "eta_updates",
                    "storm_alerts",
                    "route_optimization",
                ]
            elif enhancement_type == "ocr_processing":
                enhanced_features = [
                    "ocr_processing",
                    "invoice_validation",
                    "hs_code_extraction",
                    "compliance_checking",
                ]
            elif enhancement_type == "kpi_monitoring":
                enhanced_features = [
                    "real_time_kpi",
                    "alert_system",
                    "performance_dashboard",
                    "trend_analysis",
                ]
            elif enhancement_type == "real_api_integration":
                enhanced_features = [
                    "api_integration",
                    "real_time_data",
                    "weather_data",
                    "ocr_processing",
                    "shipping_tracking",
                ]
            else:
                enhanced_features = [
                    "real_time_data_sync",
                    "interactive_charts",
                    "automated_alerts",
                    "performance_metrics",
                ]

            enhanced_data = {
                "dashboard_id": dashboard_id,
                "enhancement_type": enhancement_type,
                "enhanced_features": enhanced_features,
                "status": "enhanced",
                "timestamp": datetime.now().isoformat(),
            }

            # HTML 대시보드 생성
            await self._create_enhanced_html(enhanced_data)

            return {
                "status": "SUCCESS",
                "message": f"Dashboard {dashboard_id} enhanced with {enhancement_type}",
                "data": enhanced_data,
                "confidence": 0.95,
                "mode": self.current_mode,
                "enhanced_dashboard_url": f"logi_master_enhanced_{dashboard_id}.html",
                "new_features": enhanced_data["enhanced_features"],
            }

        except Exception as e:
            self.logger.error(f"Dashboard enhancement failed: {e}")
            return {"status": "ERROR", "error_message": str(e), "confidence": 0.0}

    # Excel Agent 통합 명령어 핸들러들
    async def _excel_load_file(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Excel 파일 로드"""
        try:
            if not self.excel_agent_adapter:
                return {
                    "status": "ERROR",
                    "error_message": "Excel Agent integration not available",
                    "confidence": 0.0,
                }

            return await self.excel_agent_adapter.execute_command(
                "load_excel", parameters
            )

        except Exception as e:
            self.logger.error(f"Excel load failed: {e}")
            return {"status": "ERROR", "error_message": str(e), "confidence": 0.0}

    async def _excel_natural_query(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """자연어 Excel 데이터 쿼리"""
        try:
            if not self.excel_agent_adapter:
                return {
                    "status": "ERROR",
                    "error_message": "Excel Agent integration not available",
                    "confidence": 0.0,
                }
            return await self.excel_agent_adapter.execute_command(
                "query_data", parameters
            )
        except Exception as e:
            self.logger.error(f"Excel query failed: {e}")
            return {"status": "ERROR", "error_message": str(e), "confidence": 0.0}

    async def _excel_get_info(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Excel 데이터프레임 정보 조회"""
        try:
            if not self.excel_agent_adapter:
                return {
                    "status": "ERROR",
                    "error_message": "Excel Agent integration not available",
                    "confidence": 0.0,
                }
            return await self.excel_agent_adapter.execute_command(
                "get_info", parameters
            )
        except Exception as e:
            self.logger.error(f"Excel info failed: {e}")
            return {"status": "ERROR", "error_message": str(e), "confidence": 0.0}

    async def _excel_export_report(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Excel 분석 리포트 내보내기"""
        try:
            if not self.excel_agent_adapter:
                return {
                    "status": "ERROR",
                    "error_message": "Excel Agent integration not available",
                    "confidence": 0.0,
                }
            return await self.excel_agent_adapter.execute_command(
                "export_report", parameters
            )
        except Exception as e:
            self.logger.error(f"Excel export failed: {e}")
            return {"status": "ERROR", "error_message": str(e), "confidence": 0.0}

    async def _excel_get_status(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Excel Agent 시스템 상태 조회"""
        try:
            if not self.excel_agent_adapter:
                return {
                    "status": "ERROR",
                    "error_message": "Excel Agent integration not available",
                    "confidence": 0.0,
                }
            return await self.excel_agent_adapter.execute_command(
                "get_status", parameters
            )
        except Exception as e:
            self.logger.error(f"Excel status failed: {e}")
            return {"status": "ERROR", "error_message": str(e), "confidence": 0.0}

    async def _hvdc_specific_analysis(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """HVDC 특화 데이터 분석"""
        try:
            if not self.excel_agent_adapter:
                return {
                    "status": "ERROR",
                    "error_message": "Excel Agent integration not available",
                    "confidence": 0.0,
                }

            analysis_type = parameters.get("analysis_type", "general")

            # HVDC 특화 분석 쿼리 생성
            hvdc_queries = {
                "warehouse": "창고별 항목 수와 분포를 분석해주세요",
                "site": "현장별 작업량과 상태를 분석해주세요",
                "hvdc_codes": "HVDC 코드별 통계를 분석해주세요",
                "status": "현재 상태별 항목 분포를 분석해주세요",
                "comprehensive": "창고, 현장, HVDC 코드, 상태를 종합적으로 분석해주세요",
            }

            query = hvdc_queries.get(analysis_type, hvdc_queries["comprehensive"])

            return await self.excel_agent_adapter.execute_command(
                "query_data", {"query": query}
            )

        except Exception as e:
            self.logger.error(f"HVDC analysis failed: {e}")
            return {"status": "ERROR", "error_message": str(e), "confidence": 0.0}

    async def _analyze_system_architecture(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """시스템 아키텍처 상세 분석"""
        try:
            analysis_type = parameters.get("analysis_type", "overview")
            detail_level = parameters.get("detail_level", "high")

            if analysis_type == "overview":
                return {
                    "status": "SUCCESS",
                    "message": "시스템 전체 아키텍처 개요 분석",
                    "confidence": 0.95,
                    "architecture_overview": {
                        "layers": [
                            "TaskManagement",
                            "DashboardIntegration",
                            "OntologyKnowledge",
                            "MachoGPTAI",
                        ],
                        "data_flow": "데이터는 각 레이어를 통해 흐르며, 최종적으로 Excel Agent를 통해 처리됩니다.",
                        "key_components": [
                            "Shrimp Task Manager",
                            "대시보드",
                            "온톨로지 엔진",
                            "Excel Agent",
                        ],
                    },
                }
            elif analysis_type == "layer_details":
                return {
                    "status": "SUCCESS",
                    "message": f"특정 레이어 아키텍처 상세 분석 (현재는 TaskManagement 레이어만 지원)",
                    "confidence": 0.90,
                    "layer_details": {
                        "TaskManagement": {
                            "description": "작업 관리 및 데이터 저장",
                            "data_sources": [
                                "온톨로지 데이터",
                                "작업 로그",
                                "사용자 입력",
                            ],
                            "data_storage": "SQLite 데이터베이스",
                            "data_processing": "작업 상태 업데이트, 분석 결과 저장",
                        },
                        "DashboardIntegration": {
                            "description": "대시보드 통합 및 데이터 시각화",
                            "data_sources": [
                                "Excel Agent 데이터",
                                "온톨로지 데이터",
                                "실시간 API",
                            ],
                            "data_storage": "메모리 및 캐시",
                            "data_processing": "대시보드 상태 업데이트, 데이터 캐싱",
                        },
                        "OntologyKnowledge": {
                            "description": "온톨로지 지식 베이스 및 쿼리 엔진",
                            "data_sources": ["SPARQL 쿼리", "데이터베이스 로그"],
                            "data_storage": "TTL 파일 및 메모리",
                            "data_processing": "온톨로지 동기화, 쿼리 실행",
                        },
                        "MachoGPTAI": {
                            "description": "MACHO-GPT AI 레이어 - Excel Agent 통합",
                            "data_sources": [
                                "Excel Agent 데이터",
                                "온톨로지 데이터",
                                "실시간 API",
                            ],
                            "data_storage": "메모리 및 캐시",
                            "data_processing": "명령어 실행, 결과 저장",
                        },
                    },
                }
            else:
                return {
                    "status": "ERROR",
                    "error_message": "지원하지 않는 분석 유형입니다.",
                    "confidence": 0.0,
                }
        except Exception as e:
            self.logger.error(f"System architecture analysis failed: {e}")
            return {"status": "ERROR", "error_message": str(e), "confidence": 0.0}

    # 기존 명령어 핸들러들 (스텁 구현)
    async def _switch_mode(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """모드 전환"""
        return {
            "status": "SUCCESS",
            "message": "Mode switch functionality",
            "confidence": 0.9,
        }

    async def _get_kpi_data(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """KPI 데이터 조회"""
        return {"status": "SUCCESS", "message": "KPI data retrieval", "confidence": 0.9}

    async def _validate_fanr_compliance(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """FANR 규정 준수 검증"""
        return {
            "status": "SUCCESS",
            "message": "FANR compliance validation",
            "confidence": 0.9,
        }

    async def _optimize_container_stowage(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """컨테이너 적재 최적화"""
        return {
            "status": "SUCCESS",
            "message": "Container stowage optimization",
            "confidence": 0.9,
        }

    async def _weather_tie_analysis(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """기상 조건 연동 분석"""
        return {
            "status": "SUCCESS",
            "message": "Weather tie analysis",
            "confidence": 0.9,
        }

    async def _cost_guard_analysis(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """비용 관리 및 모니터링"""
        return {
            "status": "SUCCESS",
            "message": "Cost guard analysis",
            "confidence": 0.9,
        }

    async def _certificate_validation(
        self, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """인증서 유효성 검증"""
        return {
            "status": "SUCCESS",
            "message": "Certificate validation",
            "confidence": 0.9,
        }

    async def _create_enhanced_html(self, result: Dict[str, Any]):
        """강화된 HTML 파일 생성"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOGI MASTER Enhanced Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .feature-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .status {{
            background: #e8f5e8;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 LOGI MASTER Enhanced Dashboard</h1>
            <p>실시간 데이터 연동 대시보드 - {result['timestamp']}</p>
        </div>
        <div class="content">
            <div class="status">
                <h3>✅ 대시보드 강화 완료</h3>
                <p><strong>신뢰도:</strong> {result.get('confidence', 0.95)*100:.1f}% | <strong>모드:</strong> {result.get('mode', 'PRIME')}</p>
            </div>
            
            <h2>🆕 새로 추가된 기능</h2>
            <div class="features-grid">
"""

            for feature in result.get(
                "new_features",
                ["real_time_data", "weather_integration", "ocr_processing"],
            ):
                html_content += f"""
                <div class="feature-card">
                    <h3>✨ {feature.replace('_', ' ').title()}</h3>
                    <p>실시간 데이터 연동 기능이 활성화되었습니다.</p>
                </div>
"""

            html_content += """
            </div>
            
            <div class="status">
                <h3>🔧 추천 명령어</h3>
                <p>/logi_master switch_mode [모드 전환]</p>
                <p>/logi_master kpi-dash [KPI 대시보드]</p>
                <p>/logi_master weather-tie [날씨 영향 분석]</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

            # HTML 파일 저장
            file_path = Path(
                result.get(
                    "enhanced_dashboard_url", "logi_master_enhanced_dashboard.html"
                )
            )
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

        except Exception as e:
            self.logger.error(f"Failed to create enhanced HTML: {e}")

    async def get_status(self) -> Dict[str, Any]:
        """MACHO-GPT AI 레이어 상태 조회"""
        try:
            status = {
                "name": self.name,
                "is_active": self.is_active,
                "current_mode": self.current_mode,
                "active_commands": len(self.commands),
                "excel_agent_integration": self.excel_agent_integration is not None,
                "available_commands": list(self.commands.keys()),
                "timestamp": datetime.now().isoformat(),
            }

            return status

        except Exception as e:
            self.logger.error(f"Status retrieval failed: {e}")
            return {"name": self.name, "is_active": False, "error": str(e)}


# ============================================================================
# LOGI MASTER SYSTEM (MAIN CONTROLLER)
# ============================================================================


class LogiMasterSystem:
    """LOGI MASTER 시스템 메인 컨트롤러"""

    def __init__(self, config_path: str = "config/logi_master_config.yaml"):
        self.config = self._load_config(config_path)
        self.layers: Dict[str, LogiLayer] = {}
        self.is_initialized = False
        self.logger = logging.getLogger("LogiMaster")

        # 레이어 초기화
        self._init_layers()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # 기본 설정
            return {
                "task_management": {"database_path": "logi_tasks.db"},
                "dashboard_integration": {"dashboards": {}},
                "ontology_knowledge": {"ontology_path": "hvdc_ontology_system/"},
                "macho_gpt_ai": {"confidence_threshold": 0.90},
            }

    def _init_layers(self):
        """레이어 초기화"""
        self.layers["task_management"] = TaskManagementLayer(
            self.config.get("task_management", {})
        )
        self.layers["dashboard_integration"] = DashboardIntegrationLayer(
            self.config.get("dashboard_integration", {})
        )
        self.layers["ontology_knowledge"] = OntologyKnowledgeLayer(
            self.config.get("ontology_knowledge", {})
        )
        self.layers["macho_gpt_ai"] = MachoGPTAILayer(
            self.config.get("macho_gpt_ai", {})
        )

    async def initialize(self) -> bool:
        """LOGI MASTER 시스템 초기화"""
        try:
            self.logger.info("🚀 Initializing LOGI MASTER SYSTEM v3.4-mini...")

            # 모든 레이어 초기화
            for layer_name, layer in self.layers.items():
                self.logger.info(f"Initializing {layer_name} layer...")
                success = await layer.initialize()
                if not success:
                    self.logger.error(f"Failed to initialize {layer_name} layer")
                    return False

            self.is_initialized = True
            self.logger.info("✅ LOGI MASTER SYSTEM initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            return False

    async def execute_command(
        self, command: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """명령어 실행"""
        if not self.is_initialized:
            return {"error": "System not initialized"}

        try:
            # MACHO-GPT AI 레이어를 통해 명령어 실행
            ai_layer = self.layers["macho_gpt_ai"]
            result = await ai_layer.execute_command(command, parameters)

            # 결과에 추천 명령어 추가
            result["recommended_commands"] = self._get_recommended_commands(command)

            return result
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"error": str(e)}

    def _get_recommended_commands(self, executed_command: str) -> List[str]:
        """실행된 명령어에 따른 추천 명령어 반환"""
        recommendations = {
            # Excel Agent 관련 명령어 추천
            "excel_load": [
                "excel_query - 자연어로 데이터 분석",
                "excel_info - 데이터프레임 정보 확인",
                "hvdc_analysis - HVDC 특화 분석",
            ],
            "excel_query": [
                "excel_export - 분석 결과 리포트 내보내기",
                "hvdc_analysis - 종합 HVDC 분석",
                "excel_status - 시스템 상태 확인",
            ],
            "excel_info": [
                "excel_query - 데이터 분석 쿼리 실행",
                "hvdc_analysis - HVDC 특화 분석",
                "excel_export - 분석 리포트 생성",
            ],
            "hvdc_analysis": [
                "excel_export - 분석 결과 내보내기",
                "excel_query - 추가 데이터 쿼리",
                "excel_status - 시스템 상태 확인",
            ],
            "excel_export": [
                "excel_query - 새로운 분석 쿼리",
                "hvdc_analysis - 다른 분석 유형",
                "excel_load - 다른 파일 로드",
            ],
            "excel_status": [
                "excel_load - Excel 파일 로드",
                "excel_info - 데이터프레임 정보 확인",
                "hvdc_analysis - HVDC 분석 시작",
            ],
            # 기존 명령어 추천
            "enhance_dashboard": [
                "get_kpi - KPI 데이터 조회",
                "switch_mode - 모드 전환",
                "excel_load - Excel 데이터 로드",
            ],
            "switch_mode": [
                "get_kpi - KPI 데이터 조회",
                "enhance_dashboard - 대시보드 강화",
                "excel_status - Excel Agent 상태 확인",
            ],
            "get_kpi": [
                "enhance_dashboard - 대시보드 강화",
                "excel_query - 데이터 분석",
                "hvdc_analysis - HVDC 특화 분석",
            ],
            "validate_fanr": [
                "cert_check - 인증서 검증",
                "excel_export - 검증 결과 내보내기",
                "get_kpi - KPI 데이터 조회",
            ],
            "optimize_stowage": [
                "weather_tie - 기상 조건 분석",
                "excel_query - 적재 데이터 분석",
                "get_kpi - 성능 KPI 확인",
            ],
            "weather_tie": [
                "optimize_stowage - 적재 최적화",
                "excel_query - 기상 데이터 분석",
                "enhance_dashboard - 대시보드 업데이트",
            ],
            "cost_guard": [
                "get_kpi - 비용 KPI 확인",
                "excel_export - 비용 분석 리포트",
                "enhance_dashboard - 비용 대시보드",
            ],
            "cert_check": [
                "validate_fanr - FANR 규정 검증",
                "excel_export - 인증서 상태 리포트",
                "get_kpi - 인증서 KPI 확인",
            ],
            "analyze_architecture": [
                "overview - 시스템 전체 아키텍처 개요",
                "layer_details - 특정 레이어 상세 분석",
            ],
        }

        return recommendations.get(
            executed_command,
            [
                "excel_load - Excel 파일 로드",
                "excel_query - 자연어 데이터 분석",
                "hvdc_analysis - HVDC 특화 분석",
            ],
        )

    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 전체 상태 조회"""
        try:
            # MACHO-GPT AI 레이어에서 현재 모드 가져오기
            current_mode = "PRIME"  # 기본값
            if "macho_gpt_ai" in self.layers:
                try:
                    ai_layer = self.layers["macho_gpt_ai"]
                    current_mode = getattr(ai_layer, "current_mode", "PRIME")
                except:
                    current_mode = "PRIME"

            status = {
                "system_name": "LOGI MASTER SYSTEM",
                "version": "v3.4-mini",
                "status": "ACTIVE" if self.is_initialized else "INITIALIZING",
                "current_mode": current_mode,
                "layers": {},
                "timestamp": datetime.now().isoformat(),
            }

            # 각 레이어 상태 수집
            for layer_name, layer in self.layers.items():
                try:
                    status["layers"][layer_name] = await layer.get_status()
                except Exception as e:
                    self.logger.error(
                        f"Failed to get status for layer {layer_name}: {e}"
                    )
                    status["layers"][layer_name] = {
                        "name": layer_name,
                        "is_active": False,
                        "error": str(e),
                    }

            return status

        except Exception as e:
            self.logger.error(f"System status retrieval failed: {e}")
            return {
                "system_name": "LOGI MASTER SYSTEM",
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def process_layer_data(self, layer_name: str, data: Any) -> Any:
        """특정 레이어 데이터 처리"""
        if layer_name in self.layers:
            return await self.layers[layer_name].process(data)
        return {"error": f"Layer {layer_name} not found"}


# ============================================================================
# MAIN EXECUTION
# ============================================================================


async def main():
    """메인 실행 함수"""
    # LOGI MASTER 시스템 초기화
    logi_master = LogiMasterSystem()

    if await logi_master.initialize():
        print("🚀 LOGI MASTER SYSTEM v3.4-mini Ready!")
        print("=" * 50)

        # 시스템 상태 출력
        status = await logi_master.get_system_status()
        print(f"📊 System Status: {status['system_name']}")
        print(f"✅ Initialized: {status['status']}")
        print(f"🔧 Active Layers: {len(status['layers'])}")

        # 예시 명령어 실행
        print("\n🔧 Example Commands:")
        commands = ["list_tasks", "get_analytics", "switch_mode", "generate_kpi"]

        for command in commands:
            print(f"\n📋 Executing: {command}")
            result = await logi_master.execute_command(command)
            print(f"✅ Result: {result.get('status', 'UNKNOWN')}")
            if "recommended_commands" in result:
                print(f"💡 Recommended: {', '.join(result['recommended_commands'])}")

        print("\n🎯 LOGI MASTER SYSTEM is ready for integration!")
        print("💡 Use /task_manager, /macho_gpt commands for operations")

    else:
        print("❌ System initialization failed!")


if __name__ == "__main__":
    asyncio.run(main())
