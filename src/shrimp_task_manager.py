"""
Shrimp Task Manager - HVDC Project MCP Server
MACHO-GPT 통합 프로젝트 관리 시스템
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid
import logging

# MACHO-GPT 통합
try:
    from macho_gpt import LogiMaster, ContainerStow, WeatherTie

    MACHO_GPT_AVAILABLE = True
except ImportError:
    print("⚠️ MACHO-GPT modules not found, using fallback mode")
    MACHO_GPT_AVAILABLE = False

    # Fallback classes
    class LogiMaster:
        def __init__(self):
            self.mode = "PRIME"
            self.confidence_threshold = 0.90

    class ContainerStow:
        def __init__(self):
            self.pressure_limit = 4.0

    class WeatherTie:
        def __init__(self):
            self.weather_api_available = False


@dataclass
class Task:
    """작업 데이터 클래스"""

    id: str
    title: str
    description: str
    status: str  # 'pending', 'in_progress', 'completed', 'blocked'
    priority: str  # 'low', 'medium', 'high', 'critical'
    assignee: str
    created_at: str
    due_date: Optional[str]
    category: str  # 'logistics', 'warehouse', 'inventory', 'analysis', 'reporting'
    confidence: float  # MACHO-GPT 신뢰도
    mode: str  # 현재 containment mode
    tags: List[str]
    dependencies: List[str]
    kpi_metrics: Dict[str, Any]


class ShrimpTaskManager:
    """HVDC 프로젝트용 Shrimp Task Manager"""

    def __init__(self, db_path: str = "hvdc_tasks.db"):
        self.db_path = db_path
        self.logi_master = LogiMaster()
        self.container_stow = ContainerStow()
        self.weather_tie = WeatherTie()
        self.macho_gpt_available = MACHO_GPT_AVAILABLE
        self.setup_database()
        self.setup_logging()

    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("shrimp_task_manager.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def setup_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 작업 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                assignee TEXT,
                created_at TEXT NOT NULL,
                due_date TEXT,
                category TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                mode TEXT DEFAULT 'PRIME',
                tags TEXT,
                dependencies TEXT,
                kpi_metrics TEXT
            )
        """
        )

        # KPI 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS kpi_metrics (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        """
        )

        # 프로젝트 설정 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS project_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )

        conn.commit()
        conn.close()

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 작업 생성"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            title=task_data["title"],
            description=task_data.get("description", ""),
            status="pending",
            priority=task_data.get("priority", "medium"),
            assignee=task_data.get("assignee", ""),
            created_at=datetime.now().isoformat(),
            due_date=task_data.get("due_date"),
            category=task_data.get("category", "logistics"),
            confidence=0.0,
            mode="PRIME",
            tags=task_data.get("tags", []),
            dependencies=task_data.get("dependencies", []),
            kpi_metrics=task_data.get("kpi_metrics", {}),
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                task.id,
                task.title,
                task.description,
                task.status,
                task.priority,
                task.assignee,
                task.created_at,
                task.due_date,
                task.category,
                task.confidence,
                task.mode,
                json.dumps(task.tags),
                json.dumps(task.dependencies),
                json.dumps(task.kpi_metrics),
            ),
        )

        conn.commit()
        conn.close()

        self.logger.info(f"새 작업 생성: {task.title} (ID: {task_id})")
        return asdict(task)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """작업 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_task_dict(row)
        return None

    def update_task(
        self, task_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """작업 업데이트"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 업데이트 가능한 필드들
        allowed_fields = [
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "due_date",
            "category",
            "confidence",
            "mode",
            "tags",
            "dependencies",
            "kpi_metrics",
        ]

        update_parts = []
        values = []

        for field, value in updates.items():
            if field in allowed_fields:
                if field in ["tags", "dependencies", "kpi_metrics"]:
                    update_parts.append(f"{field} = ?")
                    values.append(json.dumps(value))
                else:
                    update_parts.append(f"{field} = ?")
                    values.append(value)

        if update_parts:
            values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(update_parts)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

        conn.close()

        return self.get_task(task_id)

    def list_tasks(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """작업 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM tasks"
        values = []

        if filters:
            conditions = []
            for key, value in filters.items():
                if key in ["status", "priority", "category", "assignee", "mode"]:
                    conditions.append(f"{key} = ?")
                    values.append(value)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, values)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task_dict(row) for row in rows]

    def delete_task(self, task_id: str) -> bool:
        """작업 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        if deleted:
            self.logger.info(f"작업 삭제: {task_id}")

        return deleted

    def _row_to_task_dict(self, row) -> Dict[str, Any]:
        """DB 행을 딕셔너리로 변환"""
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "assignee": row[5],
            "created_at": row[6],
            "due_date": row[7],
            "category": row[8],
            "confidence": row[9],
            "mode": row[10],
            "tags": json.loads(row[11]) if row[11] else [],
            "dependencies": json.loads(row[12]) if row[12] else [],
            "kpi_metrics": json.loads(row[13]) if row[13] else {},
        }

    def get_task_analytics(self) -> Dict[str, Any]:
        """작업 분석 데이터"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 상태별 통계
        cursor.execute(
            """
            SELECT status, COUNT(*) FROM tasks GROUP BY status
        """
        )
        status_stats = dict(cursor.fetchall())

        # 카테고리별 통계
        cursor.execute(
            """
            SELECT category, COUNT(*) FROM tasks GROUP BY category
        """
        )
        category_stats = dict(cursor.fetchall())

        # 우선순위별 통계
        cursor.execute(
            """
            SELECT priority, COUNT(*) FROM tasks GROUP BY priority
        """
        )
        priority_stats = dict(cursor.fetchall())

        # 전체 작업 수
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]

        # 완료된 작업 수
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "completed"')
        completed_tasks = cursor.fetchone()[0]

        conn.close()

        completion_rate = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completion_rate, 2),
            "status_distribution": status_stats,
            "category_distribution": category_stats,
            "priority_distribution": priority_stats,
        }

    def integrate_with_macho_gpt(self, task_id: str) -> Dict[str, Any]:
        """MACHO-GPT 시스템과 통합"""
        task = self.get_task(task_id)
        if not task:
            return {"error": "Task not found"}

        # 작업 카테고리에 따른 MACHO-GPT 모드 설정
        mode_mapping = {
            "logistics": "PRIME",
            "warehouse": "LATTICE",
            "inventory": "ORACLE",
            "analysis": "RHYTHM",
            "reporting": "COST-GUARD",
        }

        recommended_mode = mode_mapping.get(task["category"], "PRIME")

        # KPI 메트릭 업데이트
        kpi_metrics = {
            "processing_time": 0,
            "accuracy_rate": 0.95,
            "cost_efficiency": 0.90,
            "compliance_score": 0.98,
        }

        # 작업 업데이트
        updates = {
            "mode": recommended_mode,
            "confidence": 0.95,
            "kpi_metrics": kpi_metrics,
        }

        updated_task = self.update_task(task_id, updates)

        return {
            "task": updated_task,
            "macho_integration": {
                "mode": recommended_mode,
                "confidence": 0.95,
                "recommended_commands": [
                    "/logi_master analyze_performance",
                    "/switch_mode " + recommended_mode,
                    "/visualize_data task_analytics",
                ],
            },
        }


def main():
    """메인 실행 함수"""
    print("🦐 Shrimp Task Manager - HVDC Project")
    print("=" * 50)

    # Task Manager 초기화
    task_manager = ShrimpTaskManager()

    # 샘플 작업 생성
    sample_tasks = [
        {
            "title": "HVDC 창고 입출고 분석",
            "description": "DSV Outdoor/Indoor 창고별 입출고 패턴 분석 및 최적화",
            "priority": "high",
            "category": "warehouse",
            "assignee": "MACHO-GPT",
            "tags": ["HVDC", "DSV", "창고분석"],
        },
        {
            "title": "송장 OCR 처리 시스템 구축",
            "description": "FANR/MOIAT 규정 준수 송장 OCR 처리 시스템 개발",
            "priority": "critical",
            "category": "logistics",
            "assignee": "MACHO-GPT",
            "tags": ["OCR", "FANR", "MOIAT", "송장처리"],
        },
        {
            "title": "컨테이너 적재 최적화",
            "description": "Heat-Stow 분석을 통한 컨테이너 적재 압력 최적화",
            "priority": "high",
            "category": "analysis",
            "assignee": "MACHO-GPT",
            "tags": ["Heat-Stow", "컨테이너", "적재최적화"],
        },
    ]

    for task_data in sample_tasks:
        task = task_manager.create_task(task_data)
        print(f"✅ 작업 생성: {task['title']}")

        # MACHO-GPT 통합
        integration = task_manager.integrate_with_macho_gpt(task["id"])
        print(f"🔗 MACHO-GPT 통합: {integration['macho_integration']['mode']} 모드")

    # 분석 데이터 출력
    analytics = task_manager.get_task_analytics()
    print("\n📊 작업 분석:")
    print(f"총 작업 수: {analytics['total_tasks']}")
    print(f"완료율: {analytics['completion_rate']}%")
    print(f"상태별 분포: {analytics['status_distribution']}")

    print("\n🎯 추천 명령어:")
    print("/task_manager list_tasks - 모든 작업 조회")
    print("/task_manager create_task - 새 작업 생성")
    print("/task_manager get_analytics - 작업 분석")
    print("/macho_gpt integrate_task - MACHO-GPT 통합")


if __name__ == "__main__":
    main()
