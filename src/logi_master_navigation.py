#!/usr/bin/env python3
"""
LOGI MASTER Navigation System
============================
모든 대시보드에 상위로 돌아가는 네비게이션 기능 추가
- 브레드크럼 네비게이션
- 뒤로가기 버튼
- 홈 버튼
- 상위 메뉴 네비게이션
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogiMasterNavigation:
    """LOGI MASTER 네비게이션 시스템"""

    def __init__(self):
        self.main_dashboard_url = "logi_master_main_dashboard.html"
        self.dashboard_hierarchy = {
            "index.html": {"parent": None, "name": "HVDC Logistics System", "level": 0},
            "hvdc_dashboard_main.html": {
                "parent": "index.html",
                "name": "HVDC Dashboard Main",
                "level": 1,
            },
            "hvdc_warehouse_monitor.html": {
                "parent": "index.html",
                "name": "Warehouse Monitor",
                "level": 1,
            },
            "hvdc_inventory_tracking.html": {
                "parent": "index.html",
                "name": "Inventory Tracking",
                "level": 1,
            },
            "macho_realtime_kpi_dashboard.py": {
                "parent": "index.html",
                "name": "MACHO KPI Dashboard",
                "level": 1,
            },
            "tdd_progress_dashboard.html": {
                "parent": "index.html",
                "name": "TDD Progress Dashboard",
                "level": 1,
            },
            "logi_master_enhanced_dashboard.html": {
                "parent": "index.html",
                "name": "LOGI MASTER Enhanced",
                "level": 1,
            },
            "logi_master_main_dashboard.html": {
                "parent": None,
                "name": "LOGI MASTER Main Dashboard",
                "level": 0,
            },
        }

    def create_navigation_header(self, current_file: str) -> str:
        """네비게이션 헤더 HTML 생성"""
        current_info = self.dashboard_hierarchy.get(
            current_file, {"parent": None, "name": "Unknown", "level": 0}
        )

        navigation_html = f"""
        <!-- LOGI MASTER Navigation Header -->
        <div class="logi-master-nav" style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 15px 20px;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 0 auto;">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style="font-size: 1.2em; font-weight: bold;">🚀 LOGI MASTER</div>
                    <div style="display: flex; align-items: center; gap: 10px; font-size: 0.9em;">
                        <span>›</span>
                        <a href="{self.main_dashboard_url}" style="color: #3498db; text-decoration: none;">Main Dashboard</a>
                        {self._generate_breadcrumb(current_file)}
                    </div>
                </div>
                <div style="display: flex; gap: 15px;">
                    <button onclick="goToMainDashboard()" style="
                        background: #3498db;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 0.9em;
                        font-weight: bold;
                    ">🏠 홈</button>
                    <button onclick="goBack()" style="
                        background: #95a5a6;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 0.9em;
                        font-weight: bold;
                    ">← 뒤로</button>
                    <button onclick="openAllDashboards()" style="
                        background: #e74c3c;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 0.9em;
                        font-weight: bold;
                    ">📊 전체 대시보드</button>
                </div>
            </div>
        </div>
        
        <script>
        function goToMainDashboard() {{
            window.location.href = '{self.main_dashboard_url}';
        }}
        
        function goBack() {{
            if (window.history.length > 1) {{
                window.history.back();
            }} else {{
                window.location.href = '{self.main_dashboard_url}';
            }}
        }}
        
        function openAllDashboards() {{
            const dashboards = [
                'index.html',
                'hvdc_dashboard_main.html',
                'hvdc_warehouse_monitor.html',
                'hvdc_inventory_tracking.html',
                'macho_realtime_kpi_dashboard.py',
                'tdd_progress_dashboard.html',
                'logi_master_enhanced_dashboard.html',
                'logi_master_main_dashboard.html'
            ];
            
            dashboards.forEach(dashboard => {{
                window.open(dashboard, '_blank');
            }});
        }}
        
        // 페이지 로드 시 body에 상단 여백 추가
        document.addEventListener('DOMContentLoaded', function() {{
            document.body.style.paddingTop = '80px';
        }});
        </script>
        """

        return navigation_html

    def _generate_breadcrumb(self, current_file: str) -> str:
        """브레드크럼 생성"""
        breadcrumb = []
        current = current_file

        while current and current in self.dashboard_hierarchy:
            info = self.dashboard_hierarchy[current]
            if info["name"] != "LOGI MASTER Main Dashboard":  # 메인 대시보드는 제외
                breadcrumb.append(
                    f'<a href="{current}" style="color: #3498db; text-decoration: none;">{info["name"]}</a>'
                )
            current = info["parent"]

        breadcrumb.reverse()

        if breadcrumb:
            return " › ".join(breadcrumb)
        return ""

    def add_navigation_to_file(self, file_path: str) -> bool:
        """파일에 네비게이션 추가"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return False

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 이미 네비게이션이 있는지 확인
            if "logi-master-nav" in content:
                logger.info(f"Navigation already exists in {file_path}")
                return True

            # HTML 파일인지 확인
            if not file_path.endswith(".html"):
                logger.info(f"Skipping non-HTML file: {file_path}")
                return True

            # head 태그 뒤에 네비게이션 추가
            navigation_html = self.create_navigation_header(os.path.basename(file_path))

            # head 태그 찾기
            head_pattern = r"(<head[^>]*>)"
            match = re.search(head_pattern, content, re.IGNORECASE)

            if match:
                # head 태그 뒤에 네비게이션 추가
                new_content = (
                    content[: match.end()] + navigation_html + content[match.end() :]
                )
            else:
                # head 태그가 없으면 body 태그 앞에 추가
                body_pattern = r"(<body[^>]*>)"
                match = re.search(body_pattern, content, re.IGNORECASE)
                if match:
                    new_content = (
                        content[: match.end()]
                        + navigation_html
                        + content[match.end() :]
                    )
                else:
                    # body 태그도 없으면 파일 끝에 추가
                    new_content = content + navigation_html

            # 파일 저장
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(f"Navigation added to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to add navigation to {file_path}: {e}")
            return False

    def add_navigation_to_all_dashboards(self) -> Dict[str, bool]:
        """모든 대시보드에 네비게이션 추가"""
        dashboard_files = [
            "index.html",
            "hvdc_dashboard_main.html",
            "hvdc_warehouse_monitor.html",
            "hvdc_inventory_tracking.html",
            "tdd_progress_dashboard.html",
            "logi_master_enhanced_dashboard.html",
            "logi_master_main_dashboard.html",
        ]

        results = {}
        for file_path in dashboard_files:
            if os.path.exists(file_path):
                results[file_path] = self.add_navigation_to_file(file_path)
            else:
                logger.warning(f"Dashboard file not found: {file_path}")
                results[file_path] = False

        return results

    def create_floating_navigation(self) -> str:
        """플로팅 네비게이션 생성"""
        floating_nav = """
        <!-- Floating Navigation -->
        <div id="floating-nav" style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            display: none;
        ">
            <div style="
                background: rgba(44, 62, 80, 0.9);
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.3);
                backdrop-filter: blur(10px);
            ">
                <div style="color: white; font-weight: bold; margin-bottom: 10px; text-align: center;">
                    🚀 LOGI MASTER
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <button onclick="goToMainDashboard()" style="
                        background: #3498db;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 0.8em;
                        font-weight: bold;
                        white-space: nowrap;
                    ">🏠 홈</button>
                    <button onclick="goBack()" style="
                        background: #95a5a6;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 0.8em;
                        font-weight: bold;
                        white-space: nowrap;
                    ">← 뒤로</button>
                    <button onclick="toggleFloatingNav()" style="
                        background: #e74c3c;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 0.8em;
                        font-weight: bold;
                        white-space: nowrap;
                    ">✕ 닫기</button>
                </div>
            </div>
        </div>
        
        <!-- Floating Toggle Button -->
        <div id="floating-toggle" style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1001;
            background: #3498db;
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5em;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        " onclick="toggleFloatingNav()">
            🚀
        </div>
        
        <script>
        function toggleFloatingNav() {
            const nav = document.getElementById('floating-nav');
            const toggle = document.getElementById('floating-toggle');
            
            if (nav.style.display === 'none' || nav.style.display === '') {
                nav.style.display = 'block';
                toggle.style.display = 'none';
            } else {
                nav.style.display = 'none';
                toggle.style.display = 'flex';
            }
        }
        
        function goToMainDashboard() {
            window.location.href = 'logi_master_main_dashboard.html';
        }
        
        function goBack() {
            if (window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = 'logi_master_main_dashboard.html';
            }
        }
        </script>
        """

        return floating_nav

    def add_floating_navigation_to_file(self, file_path: str) -> bool:
        """파일에 플로팅 네비게이션 추가"""
        try:
            if not os.path.exists(file_path):
                return False

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 이미 플로팅 네비게이션이 있는지 확인
            if "floating-nav" in content:
                return True

            # body 태그 끝에 플로팅 네비게이션 추가
            floating_nav = self.create_floating_navigation()

            # body 태그 끝 찾기
            body_end_pattern = r"(</body>)"
            match = re.search(body_end_pattern, content, re.IGNORECASE)

            if match:
                new_content = (
                    content[: match.start()] + floating_nav + content[match.start() :]
                )
            else:
                # body 태그가 없으면 파일 끝에 추가
                new_content = content + floating_nav

            # 파일 저장
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(f"Floating navigation added to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to add floating navigation to {file_path}: {e}")
            return False


def main():
    """메인 실행 함수"""
    print("🚀 LOGI MASTER Navigation System")
    print("=" * 50)

    navigation = LogiMasterNavigation()

    # 모든 대시보드에 네비게이션 추가
    print("📋 Adding navigation to all dashboards...")
    results = navigation.add_navigation_to_all_dashboards()

    # 플로팅 네비게이션도 추가
    print("🔗 Adding floating navigation...")
    for file_path, success in results.items():
        if success:
            navigation.add_floating_navigation_to_file(file_path)

    # 결과 출력
    print("\n✅ Navigation addition results:")
    for file_path, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {status}: {file_path}")

    print(f"\n🎯 Navigation features added:")
    print("  🏠 홈 버튼 - 메인 대시보드로 이동")
    print("  ← 뒤로 버튼 - 이전 페이지로 이동")
    print("  📊 전체 대시보드 - 모든 대시보드 열기")
    print("  🚀 플로팅 네비게이션 - 우하단 플로팅 버튼")
    print("  📍 브레드크럼 - 현재 위치 표시")

    print(f"\n💡 사용법:")
    print("  - 상단 네비게이션 바에서 버튼 클릭")
    print("  - 우하단 🚀 버튼 클릭하여 플로팅 메뉴 열기")
    print("  - 브레드크럼에서 직접 링크 클릭")


if __name__ == "__main__":
    main()
