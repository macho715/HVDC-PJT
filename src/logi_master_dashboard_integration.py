#!/usr/bin/env python3
"""
LOGI MASTER Dashboard Integration System
=======================================
Heat-Stow 적재 최적화, 날씨 영향 분석, ETA 예측 결과를 대시보드에 통합
PRIME, RHYTHM 모드 자동 통합 및 신규 작업 대시보드 추가
"""

import json
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HeatStowAnalysis:
    """Heat-Stow 적재 최적화 분석 결과"""

    container_id: str
    temperature: float
    pressure: float
    optimal_position: str
    risk_level: str
    recommendations: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WeatherAnalysis:
    """날씨 영향 분석 및 ETA 예측 결과"""

    location: str
    weather_condition: str
    wind_speed: float
    visibility: float
    eta_impact: str
    delay_hours: float
    recommendations: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TaskIntegration:
    """신규 작업 통합 정보"""

    task_id: str
    title: str
    mode: str
    status: str
    priority: int
    assigned_team: str
    completion_rate: float
    kpi_metrics: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


class LogiMasterDashboardIntegration:
    """LOGI MASTER 대시보드 통합 시스템"""

    def __init__(self):
        self.heat_stow_analyses: List[HeatStowAnalysis] = []
        self.weather_analyses: List[WeatherAnalysis] = []
        self.task_integrations: List[TaskIntegration] = []
        self.dashboard_data: Dict[str, Any] = {}
        self.mode_status: Dict[str, str] = {
            "PRIME": "active",
            "RHYTHM": "active",
            "LATTICE": "active",
            "ORACLE": "active",
            "COST-GUARD": "standby",
            "ZERO": "standby",
        }

    def add_heat_stow_analysis(self, analysis: HeatStowAnalysis):
        """Heat-Stow 분석 결과 추가"""
        self.heat_stow_analyses.append(analysis)
        logger.info(f"Heat-Stow analysis added for container {analysis.container_id}")

    def add_weather_analysis(self, analysis: WeatherAnalysis):
        """날씨 분석 결과 추가"""
        self.weather_analyses.append(analysis)
        logger.info(f"Weather analysis added for location {analysis.location}")

    def add_task_integration(self, task: TaskIntegration):
        """신규 작업 통합 추가"""
        self.task_integrations.append(task)
        logger.info(f"Task integration added: {task.title}")

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """대시보드 데이터 생성"""
        # Heat-Stow 분석 요약
        heat_stow_summary = {
            "total_containers": len(self.heat_stow_analyses),
            "high_risk_containers": len(
                [a for a in self.heat_stow_analyses if a.risk_level == "HIGH"]
            ),
            "average_temperature": (
                np.mean([a.temperature for a in self.heat_stow_analyses])
                if self.heat_stow_analyses
                else 0
            ),
            "average_pressure": (
                np.mean([a.pressure for a in self.heat_stow_analyses])
                if self.heat_stow_analyses
                else 0
            ),
            "optimization_rate": (
                len([a for a in self.heat_stow_analyses if a.confidence > 0.9])
                / len(self.heat_stow_analyses)
                if self.heat_stow_analyses
                else 0
            ),
        }

        # 날씨 분석 요약
        weather_summary = {
            "total_locations": len(self.weather_analyses),
            "delayed_shipments": len(
                [w for w in self.weather_analyses if w.delay_hours > 0]
            ),
            "average_delay": (
                np.mean([w.delay_hours for w in self.weather_analyses])
                if self.weather_analyses
                else 0
            ),
            "high_impact_weather": len(
                [w for w in self.weather_analyses if w.eta_impact == "HIGH"]
            ),
            "prediction_accuracy": (
                len([w for w in self.weather_analyses if w.confidence > 0.85])
                / len(self.weather_analyses)
                if self.weather_analyses
                else 0
            ),
        }

        # 작업 통합 요약
        task_summary = {
            "total_tasks": len(self.task_integrations),
            "active_tasks": len(
                [t for t in self.task_integrations if t.status == "active"]
            ),
            "average_completion": (
                np.mean([t.completion_rate for t in self.task_integrations])
                if self.task_integrations
                else 0
            ),
            "mode_distribution": self._get_mode_distribution(),
            "priority_distribution": self._get_priority_distribution(),
        }

        # 전체 시스템 상태
        system_status = {
            "overall_confidence": self._calculate_overall_confidence(),
            "active_modes": [
                mode for mode, status in self.mode_status.items() if status == "active"
            ],
            "system_health": self._assess_system_health(),
            "last_updated": datetime.now().isoformat(),
        }

        self.dashboard_data = {
            "heat_stow_analysis": heat_stow_summary,
            "weather_analysis": weather_summary,
            "task_integration": task_summary,
            "system_status": system_status,
            "recent_analyses": {
                "heat_stow": [
                    self._serialize_analysis(a) for a in self.heat_stow_analyses[-5:]
                ],
                "weather": [
                    self._serialize_weather(w) for w in self.weather_analyses[-5:]
                ],
                "tasks": [self._serialize_task(t) for t in self.task_integrations[-5:]],
            },
        }

        return self.dashboard_data

    def _get_mode_distribution(self) -> Dict[str, int]:
        """모드별 분포 계산"""
        distribution = {}
        for task in self.task_integrations:
            mode = task.mode
            distribution[mode] = distribution.get(mode, 0) + 1
        return distribution

    def _get_priority_distribution(self) -> Dict[str, int]:
        """우선순위별 분포 계산"""
        distribution = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for task in self.task_integrations:
            if task.priority >= 8:
                distribution["HIGH"] += 1
            elif task.priority >= 5:
                distribution["MEDIUM"] += 1
            else:
                distribution["LOW"] += 1
        return distribution

    def _calculate_overall_confidence(self) -> float:
        """전체 시스템 신뢰도 계산"""
        confidences = []
        if self.heat_stow_analyses:
            confidences.extend([a.confidence for a in self.heat_stow_analyses])
        if self.weather_analyses:
            confidences.extend([w.confidence for w in self.weather_analyses])
        if self.task_integrations:
            confidences.extend(
                [t.kpi_metrics.get("confidence", 0.8) for t in self.task_integrations]
            )

        return np.mean(confidences) if confidences else 0.85

    def _assess_system_health(self) -> str:
        """시스템 상태 평가"""
        confidence = self._calculate_overall_confidence()
        if confidence >= 0.9:
            return "EXCELLENT"
        elif confidence >= 0.8:
            return "GOOD"
        elif confidence >= 0.7:
            return "FAIR"
        else:
            return "NEEDS_ATTENTION"

    def _serialize_analysis(self, analysis: HeatStowAnalysis) -> Dict[str, Any]:
        """Heat-Stow 분석 직렬화"""
        return {
            "container_id": analysis.container_id,
            "temperature": analysis.temperature,
            "pressure": analysis.pressure,
            "risk_level": analysis.risk_level,
            "confidence": analysis.confidence,
            "timestamp": analysis.timestamp.isoformat(),
        }

    def _serialize_weather(self, weather: WeatherAnalysis) -> Dict[str, Any]:
        """날씨 분석 직렬화"""
        return {
            "location": weather.location,
            "weather_condition": weather.weather_condition,
            "eta_impact": weather.eta_impact,
            "delay_hours": weather.delay_hours,
            "confidence": weather.confidence,
            "timestamp": weather.timestamp.isoformat(),
        }

    def _serialize_task(self, task: TaskIntegration) -> Dict[str, Any]:
        """작업 통합 직렬화"""
        return {
            "task_id": task.task_id,
            "title": task.title,
            "mode": task.mode,
            "status": task.status,
            "completion_rate": task.completion_rate,
            "created_at": task.created_at.isoformat(),
        }

    def create_enhanced_dashboard_html(self) -> str:
        """향상된 대시보드 HTML 생성"""
        data = self.generate_dashboard_data()

        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOGI MASTER Dashboard - Heat-Stow & Weather Analysis</title>
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
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #3498db;
        }}
        .card.heat-stow {{
            border-left-color: #e74c3c;
        }}
        .card.weather {{
            border-left-color: #f39c12;
        }}
        .card.tasks {{
            border-left-color: #27ae60;
        }}
        .card.system {{
            border-left-color: #9b59b6;
        }}
        .card h3 {{
            margin: 0 0 20px 0;
            color: #2c3e50;
            font-size: 1.3em;
            display: flex;
            align-items: center;
        }}
        .card h3::before {{
            content: '';
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 50%;
        }}
        .heat-stow h3::before {{
            background: #e74c3c;
        }}
        .weather h3::before {{
            background: #f39c12;
        }}
        .tasks h3::before {{
            background: #27ae60;
        }}
        .system h3::before {{
            background: #9b59b6;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f1;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-label {{
            font-weight: 500;
            color: #7f8c8d;
        }}
        .metric-value {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status-excellent {{ background: #27ae60; }}
        .status-good {{ background: #f39c12; }}
        .status-fair {{ background: #e74c3c; }}
        .status-needs-attention {{ background: #e67e22; }}
        .recent-list {{
            max-height: 200px;
            overflow-y: auto;
        }}
        .recent-item {{
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
            font-size: 0.9em;
        }}
        .recent-item:last-child {{
            border-bottom: none;
        }}
        .timestamp {{
            color: #95a5a6;
            font-size: 0.8em;
        }}
        .footer {{
            background: #ecf0f1;
            padding: 20px 30px;
            text-align: center;
            color: #7f8c8d;
        }}
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 LOGI MASTER Dashboard</h1>
            <p>Heat-Stow 적재 최적화 & 날씨 영향 분석 통합 대시보드</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- Heat-Stow Analysis Card -->
            <div class="card heat-stow">
                <h3>🔥 Heat-Stow 적재 최적화</h3>
                <div class="metric">
                    <span class="metric-label">총 컨테이너 수</span>
                    <span class="metric-value">{data['heat_stow_analysis']['total_containers']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">고위험 컨테이너</span>
                    <span class="metric-value">{data['heat_stow_analysis']['high_risk_containers']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">평균 온도</span>
                    <span class="metric-value">{data['heat_stow_analysis']['average_temperature']:.1f}°C</span>
                </div>
                <div class="metric">
                    <span class="metric-label">평균 압력</span>
                    <span class="metric-value">{data['heat_stow_analysis']['average_pressure']:.1f} t/m²</span>
                </div>
                <div class="metric">
                    <span class="metric-label">최적화율</span>
                    <span class="metric-value">{data['heat_stow_analysis']['optimization_rate']*100:.1f}%</span>
                </div>
                
                <h4>최근 분석</h4>
                <div class="recent-list">
                    {self._generate_recent_heat_stow_html(data['recent_analyses']['heat_stow'])}
                </div>
            </div>
            
            <!-- Weather Analysis Card -->
            <div class="card weather">
                <h3>🌤️ 날씨 영향 분석 & ETA 예측</h3>
                <div class="metric">
                    <span class="metric-label">총 위치 수</span>
                    <span class="metric-value">{data['weather_analysis']['total_locations']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">지연 화물</span>
                    <span class="metric-value">{data['weather_analysis']['delayed_shipments']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">평균 지연시간</span>
                    <span class="metric-value">{data['weather_analysis']['average_delay']:.1f}시간</span>
                </div>
                <div class="metric">
                    <span class="metric-label">고영향 날씨</span>
                    <span class="metric-value">{data['weather_analysis']['high_impact_weather']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">예측 정확도</span>
                    <span class="metric-value">{data['weather_analysis']['prediction_accuracy']*100:.1f}%</span>
                </div>
                
                <h4>최근 분석</h4>
                <div class="recent-list">
                    {self._generate_recent_weather_html(data['recent_analyses']['weather'])}
                </div>
            </div>
            
            <!-- Task Integration Card -->
            <div class="card tasks">
                <h3>📋 신규 작업 통합</h3>
                <div class="metric">
                    <span class="metric-label">총 작업 수</span>
                    <span class="metric-value">{data['task_integration']['total_tasks']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">활성 작업</span>
                    <span class="metric-value">{data['task_integration']['active_tasks']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">평균 완료율</span>
                    <span class="metric-value">{data['task_integration']['average_completion']*100:.1f}%</span>
                </div>
                
                <h4>모드별 분포</h4>
                {self._generate_mode_distribution_html(data['task_integration']['mode_distribution'])}
                
                <h4>최근 작업</h4>
                <div class="recent-list">
                    {self._generate_recent_tasks_html(data['recent_analyses']['tasks'])}
                </div>
            </div>
            
            <!-- System Status Card -->
            <div class="card system">
                <h3>⚙️ 시스템 상태</h3>
                <div class="metric">
                    <span class="metric-label">전체 신뢰도</span>
                    <span class="metric-value">{data['system_status']['overall_confidence']*100:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">시스템 상태</span>
                    <span class="metric-value">
                        <span class="status-indicator status-{data['system_status']['system_health'].lower().replace('_', '-')}"></span>
                        {data['system_status']['system_health']}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">활성 모드</span>
                    <span class="metric-value">{', '.join(data['system_status']['active_modes'])}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">마지막 업데이트</span>
                    <span class="metric-value">{data['system_status']['last_updated'][:19]}</span>
                </div>
                
                <h4>PRIME & RHYTHM 모드 통합</h4>
                <div class="recent-list">
                    <div class="recent-item">
                        <strong>PRIME 모드:</strong> 기본 AI 통합 제어 활성
                    </div>
                    <div class="recent-item">
                        <strong>RHYTHM 모드:</strong> KPI 모니터링 및 알림 활성
                    </div>
                    <div class="recent-item">
                        <strong>LATTICE 모드:</strong> 창고 최적화 활성
                    </div>
                    <div class="recent-item">
                        <strong>ORACLE 모드:</strong> 데이터 분석 및 예측 활성
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🚀 LOGI MASTER SYSTEM v3.4-mini | HVDC Project - Samsung C&T | ADNOC·DSV Partnership</p>
            <p>Heat-Stow 적재 최적화 분석 완료 | 날씨 영향 분석 및 ETA 예측 완료 | PRIME, RHYTHM 모드 자동 통합</p>
        </div>
    </div>
</body>
</html>
        """

        return html_template

    def _generate_recent_heat_stow_html(self, analyses: List[Dict[str, Any]]) -> str:
        """최근 Heat-Stow 분석 HTML 생성"""
        html = ""
        for analysis in analyses:
            html += f"""
                <div class="recent-item">
                    <strong>{analysis['container_id']}</strong> - {analysis['risk_level']} 위험
                    <br><span class="timestamp">{analysis['timestamp'][:19]}</span>
                </div>
            """
        return html if html else "<div class='recent-item'>분석 데이터 없음</div>"

    def _generate_recent_weather_html(self, weathers: List[Dict[str, Any]]) -> str:
        """최근 날씨 분석 HTML 생성"""
        html = ""
        for weather in weathers:
            html += f"""
                <div class="recent-item">
                    <strong>{weather['location']}</strong> - {weather['eta_impact']} 영향
                    <br><span class="timestamp">{weather['timestamp'][:19]}</span>
                </div>
            """
        return html if html else "<div class='recent-item'>분석 데이터 없음</div>"

    def _generate_mode_distribution_html(self, distribution: Dict[str, int]) -> str:
        """모드별 분포 HTML 생성"""
        html = ""
        for mode, count in distribution.items():
            html += f"""
                <div class="metric">
                    <span class="metric-label">{mode}</span>
                    <span class="metric-value">{count}</span>
                </div>
            """
        return html if html else "<div class='recent-item'>분포 데이터 없음</div>"

    def _generate_recent_tasks_html(self, tasks: List[Dict[str, Any]]) -> str:
        """최근 작업 HTML 생성"""
        html = ""
        for task in tasks:
            html += f"""
                <div class="recent-item">
                    <strong>{task['title']}</strong> - {task['mode']} 모드
                    <br><span class="timestamp">{task['created_at'][:19]}</span>
                </div>
            """
        return html if html else "<div class='recent-item'>작업 데이터 없음</div>"


def main():
    """메인 실행 함수"""
    # 대시보드 통합 시스템 초기화
    dashboard = LogiMasterDashboardIntegration()

    # Heat-Stow 분석 데이터 추가
    heat_stow_data = [
        HeatStowAnalysis(
            "CONT-001", 45.2, 3.8, "A1-B2", "MEDIUM", ["온도 모니터링 강화"], 0.92
        ),
        HeatStowAnalysis(
            "CONT-002", 52.1, 4.2, "C3-D4", "HIGH", ["즉시 재배치 필요"], 0.95
        ),
        HeatStowAnalysis("CONT-003", 38.7, 3.1, "E5-F6", "LOW", ["정상 범위"], 0.88),
        HeatStowAnalysis(
            "CONT-004", 48.9, 4.0, "G7-H8", "MEDIUM", ["압력 분산 조정"], 0.91
        ),
        HeatStowAnalysis("CONT-005", 41.3, 3.3, "I9-J10", "LOW", ["정상 범위"], 0.89),
    ]

    for analysis in heat_stow_data:
        dashboard.add_heat_stow_analysis(analysis)

    # 날씨 분석 데이터 추가
    weather_data = [
        WeatherAnalysis(
            "Jebel Ali Port", "Clear", 15.2, 10.0, "LOW", 0.0, ["정상 운항 가능"], 0.94
        ),
        WeatherAnalysis(
            "Fujairah Port",
            "Storm",
            45.8,
            2.5,
            "HIGH",
            8.5,
            ["지연 예상, 대안 경로 검토"],
            0.96,
        ),
        WeatherAnalysis(
            "Abu Dhabi Port", "Cloudy", 22.1, 8.0, "MEDIUM", 2.0, ["주의 운항"], 0.89
        ),
        WeatherAnalysis(
            "Dubai Creek", "Clear", 12.5, 12.0, "LOW", 0.0, ["정상 운항 가능"], 0.92
        ),
        WeatherAnalysis(
            "Sharjah Port", "Rain", 28.7, 5.0, "MEDIUM", 3.5, ["속도 조정 필요"], 0.87
        ),
    ]

    for weather in weather_data:
        dashboard.add_weather_analysis(weather)

    # 신규 작업 통합 데이터 추가
    task_data = [
        TaskIntegration(
            "TASK-001",
            "창고 입출고 분석",
            "LATTICE",
            "active",
            8,
            "창고팀",
            0.75,
            {"confidence": 0.92},
        ),
        TaskIntegration(
            "TASK-002",
            "송장 OCR 처리 시스템 구축",
            "RHYTHM",
            "active",
            9,
            "AI팀",
            0.45,
            {"confidence": 0.88},
        ),
        TaskIntegration(
            "TASK-003",
            "컨테이너 적재 최적화",
            "PRIME",
            "active",
            7,
            "최적화팀",
            0.60,
            {"confidence": 0.94},
        ),
        TaskIntegration(
            "TASK-004",
            "날씨 영향 분석 시스템",
            "ORACLE",
            "active",
            6,
            "분석팀",
            0.80,
            {"confidence": 0.91},
        ),
        TaskIntegration(
            "TASK-005",
            "KPI 대시보드 통합",
            "RHYTHM",
            "active",
            5,
            "시스템팀",
            0.90,
            {"confidence": 0.89},
        ),
    ]

    for task in task_data:
        dashboard.add_task_integration(task)

    # 향상된 대시보드 HTML 생성
    html_content = dashboard.create_enhanced_dashboard_html()

    # HTML 파일 저장
    with open("logi_master_enhanced_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("🚀 LOGI MASTER Enhanced Dashboard 생성 완료!")
    print("📊 Heat-Stow 적재 최적화 분석 완료")
    print("🌤️ 날씨 영향 분석 및 ETA 예측 완료")
    print("🤖 PRIME, RHYTHM 모드 자동 통합")
    print("📋 신규 작업 대시보드 추가 완료")
    print("💾 파일 저장: logi_master_enhanced_dashboard.html")


if __name__ == "__main__":
    main()
