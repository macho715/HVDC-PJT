#!/usr/bin/env python3
"""
LOGI MASTER Main Dashboard Integration System
============================================
모든 대시보드를 하나의 메인 대시보드에서 연결하는 통합 시스템
- HVDC Logistics System (index.html)
- HVDC Dashboard Main (hvdc_dashboard_main.html)  
- MACHO Real-time KPI Dashboard (macho_realtime_kpi_dashboard.py)
- TDD Progress Dashboard (tdd_progress_dashboard.html)
- Enhanced Dashboard (logi_master_enhanced_dashboard.html)
- Warehouse Monitor (hvdc_warehouse_monitor.html)
- Inventory Tracking (hvdc_inventory_tracking.html)
"""

import json
import yaml
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from pathlib import Path
import webbrowser
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DashboardInfo:
    """대시보드 정보"""
    id: str
    name: str
    description: str
    url: str
    type: str
    status: str = "active"
    last_updated: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemStatus:
    """시스템 상태"""
    overall_confidence: float
    active_dashboards: int
    total_dashboards: int
    system_health: str
    last_sync: datetime = field(default_factory=datetime.now)

class LogiMasterMainDashboard:
    """LOGI MASTER 메인 대시보드 통합 시스템"""
    
    def __init__(self):
        self.dashboards: Dict[str, DashboardInfo] = {}
        self.system_status = SystemStatus(0.0, 0, 0, "UNKNOWN")
        self.dashboard_config = self._load_dashboard_config()
        self._init_dashboards()
    
    def _load_dashboard_config(self) -> Dict[str, Any]:
        """대시보드 설정 로드"""
        return {
            "dashboards": {
                "main": {
                    "name": "HVDC Logistics System",
                    "description": "Samsung C&T | ADNOC·DSV Partnership 메인 대시보드",
                    "url": "index.html",
                    "type": "main_entry"
                },
                "hvdc_main": {
                    "name": "HVDC Dashboard Main",
                    "description": "HVDC 프로젝트 물류 운영 종합 개요",
                    "url": "hvdc_dashboard_main.html",
                    "type": "overview"
                },
                "warehouse_monitor": {
                    "name": "Warehouse Monitor",
                    "description": "실시간 창고 운영 모니터링",
                    "url": "hvdc_warehouse_monitor.html",
                    "type": "monitoring"
                },
                "inventory_tracking": {
                    "name": "Inventory Tracking",
                    "description": "종합 재고 관리 시스템",
                    "url": "hvdc_inventory_tracking.html",
                    "type": "tracking"
                },
                "macho_kpi": {
                    "name": "MACHO Real-time KPI",
                    "description": "실시간 KPI 모니터링 대시보드",
                    "url": "macho_realtime_kpi_dashboard.py",
                    "type": "kpi"
                },
                "tdd_progress": {
                    "name": "TDD Progress Dashboard",
                    "description": "TDD 개발 진행 상황 대시보드",
                    "url": "tdd_progress_dashboard.html",
                    "type": "development"
                },
                "enhanced": {
                    "name": "LOGI MASTER Enhanced",
                    "description": "Heat-Stow & Weather Analysis 통합 대시보드",
                    "url": "logi_master_enhanced_dashboard.html",
                    "type": "integrated"
                }
            }
        }
    
    def _init_dashboards(self):
        """대시보드 초기화"""
        for dashboard_id, config in self.dashboard_config["dashboards"].items():
            dashboard = DashboardInfo(
                id=dashboard_id,
                name=config["name"],
                description=config["description"],
                url=config["url"],
                type=config["type"]
            )
            self.dashboards[dashboard_id] = dashboard
    
    def update_dashboard_status(self, dashboard_id: str, status: str, metrics: Dict[str, Any] = None):
        """대시보드 상태 업데이트"""
        if dashboard_id in self.dashboards:
            dashboard = self.dashboards[dashboard_id]
            dashboard.status = status
            dashboard.last_updated = datetime.now()
            if metrics:
                dashboard.metrics = metrics
            logger.info(f"Dashboard {dashboard_id} status updated: {status}")
    
    def get_dashboard_list(self) -> List[DashboardInfo]:
        """대시보드 목록 조회"""
        return list(self.dashboards.values())
    
    def calculate_system_status(self) -> SystemStatus:
        """시스템 상태 계산"""
        total_dashboards = len(self.dashboards)
        active_dashboards = len([d for d in self.dashboards.values() if d.status == "active"])
        
        # 신뢰도 계산 (각 대시보드의 메트릭 기반)
        confidences = []
        for dashboard in self.dashboards.values():
            if "confidence" in dashboard.metrics:
                confidences.append(dashboard.metrics["confidence"])
            else:
                confidences.append(0.85)  # 기본값
        
        overall_confidence = np.mean(confidences) if confidences else 0.85
        
        # 시스템 상태 평가
        if overall_confidence >= 0.9 and active_dashboards == total_dashboards:
            system_health = "EXCELLENT"
        elif overall_confidence >= 0.8 and active_dashboards >= total_dashboards * 0.8:
            system_health = "GOOD"
        elif overall_confidence >= 0.7:
            system_health = "FAIR"
        else:
            system_health = "NEEDS_ATTENTION"
        
        self.system_status = SystemStatus(
            overall_confidence=overall_confidence,
            active_dashboards=active_dashboards,
            total_dashboards=total_dashboards,
            system_health=system_health
        )
        
        return self.system_status
    
    def create_main_dashboard_html(self) -> str:
        """메인 대시보드 HTML 생성"""
        system_status = self.calculate_system_status()
        dashboard_list = self.get_dashboard_list()
        
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOGI MASTER Main Dashboard - 통합 물류 관리 시스템</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        
        .main-container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            border-radius: 15px 15px 0 0;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 3em;
            font-weight: 300;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .system-status {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .status-card {{
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
        }}
        
        .status-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .status-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        
        .health-indicator {{
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 10px;
        }}
        
        .health-excellent {{ background: #27ae60; }}
        .health-good {{ background: #f39c12; }}
        .health-fair {{ background: #e74c3c; }}
        .health-needs-attention {{ background: #e67e22; }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .dashboard-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            border-left: 5px solid #3498db;
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .dashboard-card.main-entry {{ border-left-color: #e74c3c; }}
        .dashboard-card.overview {{ border-left-color: #f39c12; }}
        .dashboard-card.monitoring {{ border-left-color: #27ae60; }}
        .dashboard-card.tracking {{ border-left-color: #9b59b6; }}
        .dashboard-card.kpi {{ border-left-color: #1abc9c; }}
        .dashboard-card.development {{ border-left-color: #34495e; }}
        .dashboard-card.integrated {{ border-left-color: #e67e22; }}
        
        .dashboard-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .dashboard-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .dashboard-type {{
            background: #ecf0f1;
            color: #7f8c8d;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .dashboard-description {{
            color: #7f8c8d;
            margin-bottom: 15px;
            line-height: 1.5;
        }}
        
        .dashboard-metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .metric {{
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .metric-value {{
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .metric-label {{
            font-size: 0.8em;
            color: #95a5a6;
        }}
        
        .dashboard-actions {{
            display: flex;
            gap: 10px;
        }}
        
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: bold;
            transition: background 0.3s ease;
        }}
        
        .btn-primary {{
            background: #3498db;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #2980b9;
        }}
        
        .btn-secondary {{
            background: #ecf0f1;
            color: #7f8c8d;
        }}
        
        .btn-secondary:hover {{
            background: #bdc3c7;
        }}
        
        .footer {{
            background: white;
            border-radius: 0 0 15px 15px;
            padding: 30px;
            text-align: center;
            color: #7f8c8d;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .quick-actions {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .quick-actions h3 {{
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        
        .action-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .action-btn {{
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.3s ease;
        }}
        
        .action-btn:hover {{
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            .status-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <h1>🚀 LOGI MASTER Main Dashboard</h1>
            <p>통합 물류 관리 시스템 - Samsung C&T | ADNOC·DSV Partnership</p>
        </div>
        
        <div class="system-status">
            <h3>⚙️ 시스템 상태</h3>
            <div class="status-grid">
                <div class="status-card">
                    <div class="status-value">{system_status.overall_confidence*100:.1f}%</div>
                    <div class="status-label">전체 신뢰도</div>
                </div>
                <div class="status-card">
                    <div class="status-value">{system_status.active_dashboards}/{system_status.total_dashboards}</div>
                    <div class="status-label">활성 대시보드</div>
                </div>
                <div class="status-card">
                    <div class="status-value">
                        <span class="health-indicator health-{system_status.system_health.lower().replace('_', '-')}"></span>
                        {system_status.system_health}
                    </div>
                    <div class="status-label">시스템 상태</div>
                </div>
                <div class="status-card">
                    <div class="status-value">{datetime.now().strftime('%H:%M')}</div>
                    <div class="status-label">마지막 업데이트</div>
                </div>
            </div>
        </div>
        
        <div class="quick-actions">
            <h3>⚡ 빠른 액션</h3>
            <div class="action-buttons">
                <button class="action-btn" onclick="openDashboard('main')">🏠 메인 대시보드</button>
                <button class="action-btn" onclick="openDashboard('enhanced')">📊 통합 분석</button>
                <button class="action-btn" onclick="openDashboard('macho_kpi')">🤖 KPI 모니터링</button>
                <button class="action-btn" onclick="openDashboard('warehouse_monitor')">🏭 창고 모니터</button>
                <button class="action-btn" onclick="openDashboard('inventory_tracking')">📦 재고 추적</button>
                <button class="action-btn" onclick="openDashboard('tdd_progress')">🧪 TDD 진행상황</button>
            </div>
        </div>
        
        <div class="dashboard-grid">
            {self._generate_dashboard_cards_html(dashboard_list)}
        </div>
        
        <div class="footer">
            <p>🚀 LOGI MASTER SYSTEM v3.4-mini | HVDC Project - Samsung C&T | ADNOC·DSV Partnership</p>
            <p>Heat-Stow 적재 최적화 | 날씨 영향 분석 | PRIME, RHYTHM 모드 통합 | 실시간 KPI 모니터링</p>
        </div>
    </div>
    
    <script>
        function openDashboard(dashboardId) {{
            const dashboards = {json.dumps({d.id: d.url for d in dashboard_list})};
            const url = dashboards[dashboardId];
            if (url) {{
                window.open(url, '_blank');
            }}
        }}
        
        function refreshDashboard(dashboardId) {{
            // 대시보드 새로고침 로직
            console.log('Refreshing dashboard:', dashboardId);
            location.reload();
        }}
        
        // 자동 새로고침 (5분마다)
        setInterval(() => {{
            location.reload();
        }}, 300000);
        
        // 실시간 업데이트 표시
        function updateLastSync() {{
            const now = new Date();
            document.querySelector('.status-value:last-child').textContent = now.toLocaleTimeString();
        }}
        
        setInterval(updateLastSync, 1000);
    </script>
</body>
</html>
        """
        
        return html_template
    
    def _generate_dashboard_cards_html(self, dashboard_list: List[DashboardInfo]) -> str:
        """대시보드 카드 HTML 생성"""
        html = ""
        for dashboard in dashboard_list:
            metrics_html = self._generate_metrics_html(dashboard)
            
            html += f"""
            <div class="dashboard-card {dashboard.type}">
                <div class="dashboard-header">
                    <div class="dashboard-title">{dashboard.name}</div>
                    <div class="dashboard-type">{dashboard.type.upper()}</div>
                </div>
                <div class="dashboard-description">{dashboard.description}</div>
                {metrics_html}
                <div class="dashboard-actions">
                    <button class="btn btn-primary" onclick="openDashboard('{dashboard.id}')">열기</button>
                    <button class="btn btn-secondary" onclick="refreshDashboard('{dashboard.id}')">새로고침</button>
                </div>
            </div>
            """
        
        return html
    
    def _generate_metrics_html(self, dashboard: DashboardInfo) -> str:
        """대시보드 메트릭 HTML 생성"""
        if not dashboard.metrics:
            return '<div class="dashboard-metrics"><div class="metric"><div class="metric-value">-</div><div class="metric-label">메트릭 없음</div></div></div>'
        
        metrics_html = '<div class="dashboard-metrics">'
        for key, value in list(dashboard.metrics.items())[:4]:  # 최대 4개 메트릭
            if isinstance(value, float):
                display_value = f"{value:.1f}"
            else:
                display_value = str(value)
            
            metrics_html += f"""
            <div class="metric">
                <div class="metric-value">{display_value}</div>
                <div class="metric-label">{key}</div>
            </div>
            """
        metrics_html += '</div>'
        
        return metrics_html
    
    def update_all_dashboards(self):
        """모든 대시보드 상태 업데이트"""
        # 실제 파일 존재 여부 확인
        for dashboard_id, dashboard in self.dashboards.items():
            file_path = Path(dashboard.url)
            if file_path.exists():
                self.update_dashboard_status(dashboard_id, "active", {
                    "confidence": 0.95,
                    "last_updated": datetime.now().isoformat()
                })
            else:
                self.update_dashboard_status(dashboard_id, "inactive", {
                    "confidence": 0.0,
                    "error": "File not found"
                })
    
    def save_main_dashboard(self, filename: str = "logi_master_main_dashboard.html"):
        """메인 대시보드 저장"""
        html_content = self.create_main_dashboard_html()
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Main dashboard saved: {filename}")
        return filename
    
    def open_main_dashboard(self, filename: str = "logi_master_main_dashboard.html"):
        """메인 대시보드 오픈"""
        try:
            webbrowser.open(f"file://{os.path.abspath(filename)}")
            logger.info(f"Main dashboard opened: {filename}")
        except Exception as e:
            logger.error(f"Failed to open dashboard: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 LOGI MASTER Main Dashboard Integration System")
    print("=" * 60)
    
    # 메인 대시보드 시스템 초기화
    main_dashboard = LogiMasterMainDashboard()
    
    # 모든 대시보드 상태 업데이트
    main_dashboard.update_all_dashboards()
    
    # 메인 대시보드 생성 및 저장
    filename = main_dashboard.save_main_dashboard()
    
    # 메인 대시보드 오픈
    main_dashboard.open_main_dashboard(filename)
    
    print("✅ 메인 대시보드 생성 완료!")
    print(f"📁 파일 저장: {filename}")
    print("🌐 브라우저에서 자동 오픈됨")
    print("\n📊 연결된 대시보드:")
    
    for dashboard in main_dashboard.get_dashboard_list():
        status_icon = "✅" if dashboard.status == "active" else "❌"
        print(f"  {status_icon} {dashboard.name} ({dashboard.type})")
    
    print(f"\n⚙️ 시스템 상태: {main_dashboard.system_status.system_health}")
    print(f"📈 전체 신뢰도: {main_dashboard.system_status.overall_confidence*100:.1f}%")
    print(f"🔗 활성 대시보드: {main_dashboard.system_status.active_dashboards}/{main_dashboard.system_status.total_dashboards}")

if __name__ == "__main__":
    main() 