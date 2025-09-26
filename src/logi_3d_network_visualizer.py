#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini - HVDC Project 3D Network Visualizer
물류 네트워크 3D 시각화 시스템 (NetworkX + Plotly)

Features:
- 물류 노드 (창고, 현장, 부두) 3D 시각화
- 실시간 물류 플로우 추적
- FANR/MOIAT 규정 준수 시각화
- 인터랙티브 대시보드
- MACHO-GPT 명령어 통합
"""

import networkx as nx
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass
from enum import Enum
import warnings

warnings.filterwarnings("ignore")

# MACHO-GPT 통합
from macho_gpt import LogiMaster, ContainerStow, WeatherTie


class NetworkNodeType(Enum):
    """물류 네트워크 노드 타입"""

    WAREHOUSE = "warehouse"
    SITE = "site"
    PORT = "port"
    SUPPLIER = "supplier"
    CUSTOMER = "customer"
    TRANSIT = "transit"


class LogiNetworkVisualizer:
    """HVDC 물류 네트워크 3D 시각화 시스템"""

    def __init__(self, mode: str = "LATTICE"):
        self.mode = mode
        self.logger = logging.getLogger(__name__)
        self.confidence_threshold = 0.90

        # MACHO-GPT 통합
        self.logi_master = LogiMaster(mode=mode)
        self.container_stow = ContainerStow()
        self.weather_tie = WeatherTie()

        # 네트워크 그래프 초기화
        self.G = nx.Graph()
        self.node_positions = {}
        self.edge_weights = {}

        # 물류 노드 타입별 색상 매핑
        self.node_colors = {
            NetworkNodeType.WAREHOUSE: "#1f77b4",  # 파랑
            NetworkNodeType.SITE: "#ff7f0e",  # 주황
            NetworkNodeType.PORT: "#2ca02c",  # 초록
            NetworkNodeType.SUPPLIER: "#d62728",  # 빨강
            NetworkNodeType.CUSTOMER: "#9467bd",  # 보라
            NetworkNodeType.TRANSIT: "#8c564b",  # 갈색
        }

        # HVDC 특화 설정
        self.hvdc_warehouses = [
            "DSV Indoor",
            "DSV Outdoor",
            "DSV Al Markaz",
            "DSV MZP",
            "AAA Storage",
            "Hauler Indoor",
            "MOSB",
            "DHL Warehouse",
        ]
        self.hvdc_sites = ["MIR", "SHU", "DAS", "AGI"]

    def load_logistics_data(self, data_source: str) -> Dict[str, Any]:
        """
        물류 데이터 로드 및 전처리

        Args:
            data_source: 데이터 소스 경로 또는 DataFrame

        Returns:
            Dict: 전처리된 물류 데이터
        """
        try:
            if isinstance(data_source, str):
                if data_source.endswith(".xlsx"):
                    df = pd.read_excel(data_source)
                elif data_source.endswith(".csv"):
                    df = pd.read_csv(data_source)
                elif data_source.endswith(".json"):
                    with open(data_source, "r", encoding="utf-8") as f:
                        df = pd.DataFrame(json.load(f))
                else:
                    raise ValueError(f"Unsupported file format: {data_source}")
            else:
                df = data_source.copy()

            # 데이터 정규화
            df_clean = self._normalize_logistics_data(df)

            # 네트워크 그래프 구성
            self._build_network_graph(df_clean)

            result = {
                "status": "SUCCESS",
                "confidence": 0.95,
                "mode": self.mode,
                "data_shape": df_clean.shape,
                "nodes_count": len(self.G.nodes()),
                "edges_count": len(self.G.edges()),
                "triggers": self._check_auto_triggers(df_clean),
                "next_cmds": [
                    "/visualize_3d_network",
                    "/analyze_flow_patterns",
                    "/generate_kpi_dashboard",
                ],
            }

            self.logger.info(
                f"Logistics data loaded: {result['nodes_count']} nodes, {result['edges_count']} edges"
            )
            return result

        except Exception as e:
            self.logger.error(f"Failed to load logistics data: {e}")
            return {
                "status": "FAIL",
                "confidence": 0.0,
                "error": str(e),
                "mode": self.mode,
                "triggers": ["/switch_mode ZERO"],
                "next_cmds": ["/check_data_source", "/switch_mode ZERO"],
            }

    def _normalize_logistics_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """물류 데이터 정규화"""
        df_clean = df.copy()

        # NaN 처리
        df_clean = df_clean.fillna("")

        # 문자열 정규화
        for col in df_clean.select_dtypes(include=["object"]).columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()

        # 날짜 컬럼 처리
        date_columns = [
            col
            for col in df_clean.columns
            if "date" in col.lower() or "time" in col.lower()
        ]
        for col in date_columns:
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")
            except:
                pass

        return df_clean

    def _build_network_graph(self, df: pd.DataFrame) -> None:
        """물류 네트워크 그래프 구성"""
        self.G.clear()

        # 노드 추가 (창고, 현장, 부두)
        for warehouse in self.hvdc_warehouses:
            if warehouse in df.columns:
                self.G.add_node(
                    warehouse,
                    type=NetworkNodeType.WAREHOUSE,
                    category="warehouse",
                    capacity=1000,
                )

        for site in self.hvdc_sites:
            if site in df.columns:
                self.G.add_node(
                    site, type=NetworkNodeType.SITE, category="site", capacity=500
                )

        # 추가 노드들 (부두, 공급업체 등)
        additional_nodes = {
            "Jebel Ali Port": NetworkNodeType.PORT,
            "Abu Dhabi Port": NetworkNodeType.PORT,
            "Hitachi Supplier": NetworkNodeType.SUPPLIER,
            "Siemens Supplier": NetworkNodeType.SUPPLIER,
            "Samsung C&T": NetworkNodeType.SUPPLIER,
        }

        for node, node_type in additional_nodes.items():
            self.G.add_node(
                node, type=node_type, category=node_type.value, capacity=2000
            )

        # 엣지 추가 (물류 플로우)
        self._add_logistics_edges(df)

        # 3D 좌표 생성
        self._generate_3d_layout()

    def _add_logistics_edges(self, df: pd.DataFrame) -> None:
        """물류 플로우 엣지 추가"""
        # 창고 → 현장 연결
        for warehouse in self.hvdc_warehouses:
            for site in self.hvdc_sites:
                if warehouse in df.columns and site in df.columns:
                    # 실제 데이터 기반 연결 강도 계산
                    connection_strength = self._calculate_connection_strength(
                        df, warehouse, site
                    )
                    if connection_strength > 0:
                        self.G.add_edge(
                            warehouse,
                            site,
                            weight=connection_strength,
                            type="warehouse_to_site",
                            distance=50,
                        )  # km

        # 공급업체 → 창고 연결
        suppliers = ["Hitachi Supplier", "Siemens Supplier", "Samsung C&T"]
        for supplier in suppliers:
            for warehouse in self.hvdc_warehouses:
                if supplier in self.G.nodes() and warehouse in self.G.nodes():
                    self.G.add_edge(
                        supplier,
                        warehouse,
                        weight=0.8,
                        type="supplier_to_warehouse",
                        distance=100,
                    )

        # 부두 → 창고 연결
        ports = ["Jebel Ali Port", "Abu Dhabi Port"]
        for port in ports:
            for warehouse in self.hvdc_warehouses:
                if port in self.G.nodes() and warehouse in self.G.nodes():
                    self.G.add_edge(
                        port,
                        warehouse,
                        weight=0.9,
                        type="port_to_warehouse",
                        distance=30,
                    )

    def _calculate_connection_strength(
        self, df: pd.DataFrame, source: str, target: str
    ) -> float:
        """두 노드 간 연결 강도 계산"""
        try:
            # 실제 데이터에서 연결 패턴 분석
            source_data = df[source].dropna()
            target_data = df[target].dropna()

            if len(source_data) == 0 or len(target_data) == 0:
                return 0.0

            # 시간적 연관성 분석
            source_dates = pd.to_datetime(source_data, errors="coerce").dropna()
            target_dates = pd.to_datetime(target_data, errors="coerce").dropna()

            if len(source_dates) == 0 or len(target_dates) == 0:
                return 0.1  # 기본 연결

            # 평균 시간 차이 계산
            avg_time_diff = abs(
                (source_dates.mean() - target_dates.mean()).total_seconds() / 86400
            )

            # 연결 강도 계산 (시간 차이가 작을수록 강한 연결)
            strength = max(0.1, 1.0 - (avg_time_diff / 30))  # 30일 기준

            return min(1.0, strength)

        except Exception as e:
            self.logger.warning(f"Connection strength calculation failed: {e}")
            return 0.1

    def _generate_3d_layout(self) -> None:
        """3D 레이아웃 생성"""
        try:
            # NetworkX 3D spring layout
            pos = nx.spring_layout(self.G, dim=3, k=1, iterations=50, seed=42)

            # 노드 타입별 위치 조정
            for node, (x, y, z) in pos.items():
                node_type = self.G.nodes[node].get("type", NetworkNodeType.TRANSIT)

                # 타입별 위치 조정
                if node_type == NetworkNodeType.WAREHOUSE:
                    z += 0.5  # 창고는 위쪽
                elif node_type == NetworkNodeType.SITE:
                    z -= 0.5  # 현장은 아래쪽
                elif node_type == NetworkNodeType.PORT:
                    y += 0.3  # 부두는 앞쪽
                elif node_type == NetworkNodeType.SUPPLIER:
                    x -= 0.3  # 공급업체는 왼쪽

                self.node_positions[node] = (x, y, z)

            self.logger.info("3D layout generated successfully")

        except Exception as e:
            self.logger.error(f"Failed to generate 3D layout: {e}")
            # 기본 레이아웃 사용
            self.node_positions = nx.spring_layout(self.G, dim=3, seed=42)

    def create_3d_network_visualization(
        self,
        title: str = "HVDC Logistics Network 3D",
        show_labels: bool = True,
        interactive: bool = True,
    ) -> go.Figure:
        """
        3D 네트워크 시각화 생성

        Args:
            title: 그래프 제목
            show_labels: 노드 라벨 표시 여부
            interactive: 인터랙티브 기능 활성화

        Returns:
            go.Figure: Plotly 3D 네트워크 그래프
        """
        try:
            # 엣지 좌표 추출
            edge_x, edge_y, edge_z = [], [], []
            edge_colors = []
            edge_widths = []

            for edge in self.G.edges(data=True):
                x0, y0, z0 = self.node_positions[edge[0]]
                x1, y1, z1 = self.node_positions[edge[1]]

                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_z.extend([z0, z1, None])

                # 엣지 타입별 색상 (None 값 제거)
                edge_type = edge[2].get("type", "default")
                if "warehouse_to_site" in edge_type:
                    edge_colors.extend(["#ff7f0e", "#ff7f0e", "#ff7f0e"])  # 주황
                elif "supplier_to_warehouse" in edge_type:
                    edge_colors.extend(["#d62728", "#d62728", "#d62728"])  # 빨강
                elif "port_to_warehouse" in edge_type:
                    edge_colors.extend(["#2ca02c", "#2ca02c", "#2ca02c"])  # 초록
                else:
                    edge_colors.extend(["#888", "#888", "#888"])

                # 엣지 두께 (연결 강도 기반)
                weight = edge[2].get("weight", 0.5)
                width = max(1, weight * 5)
                edge_widths.extend([width, width, width])

            # 노드 좌표 추출
            node_x, node_y, node_z = [], [], []
            node_colors = []
            node_sizes = []
            node_labels = []

            for node, (x, y, z) in self.node_positions.items():
                node_x.append(x)
                node_y.append(y)
                node_z.append(z)

                node_type = self.G.nodes[node].get("type", NetworkNodeType.TRANSIT)
                node_colors.append(self.node_colors[node_type])

                # 노드 크기 (용량 기반)
                capacity = self.G.nodes[node].get("capacity", 100)
                node_sizes.append(max(5, capacity / 100))

                if show_labels:
                    node_labels.append(node)
                else:
                    node_labels.append("")

            # 엣지 트레이스
            edge_trace = go.Scatter3d(
                x=edge_x,
                y=edge_y,
                z=edge_z,
                line=dict(
                    width=2, color=edge_colors, colorscale="Viridis"  # 고정 두께 사용
                ),
                hoverinfo="none",
                mode="lines",
                name="Logistics Flow",
            )

            # 노드 트레이스
            node_trace = go.Scatter3d(
                x=node_x,
                y=node_y,
                z=node_z,
                mode="markers+text",
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    colorscale="Viridis",
                    opacity=0.8,
                    line=dict(width=2, color="white"),
                ),
                text=node_labels,
                textposition="middle center",
                hoverinfo="text",
                name="Logistics Nodes",
            )

            # 레이아웃 설정
            layout = go.Layout(
                title=dict(text=title, x=0.5, font=dict(size=20, color="#2c3e50")),
                showlegend=True,
                scene=dict(
                    xaxis=dict(
                        title="X Axis (Supplier → Warehouse)",
                        showgrid=True,
                        zeroline=True,
                        showline=True,
                        mirror=True,
                        gridcolor="lightgray",
                        zerolinecolor="black",
                    ),
                    yaxis=dict(
                        title="Y Axis (Port → Warehouse)",
                        showgrid=True,
                        zeroline=True,
                        showline=True,
                        mirror=True,
                        gridcolor="lightgray",
                        zerolinecolor="black",
                    ),
                    zaxis=dict(
                        title="Z Axis (Warehouse → Site)",
                        showgrid=True,
                        zeroline=True,
                        showline=True,
                        mirror=True,
                        gridcolor="lightgray",
                        zerolinecolor="black",
                    ),
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
                ),
                margin=dict(b=0, l=0, r=0, t=50),
                hovermode="closest",
                template="plotly_white",
            )

            # 그래프 생성
            fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

            # 인터랙티브 기능 추가
            if interactive:
                fig.update_layout(
                    updatemenus=[
                        dict(
                            type="buttons",
                            direction="right",
                            x=0.1,
                            y=1.1,
                            showactive=False,
                            buttons=list(
                                [
                                    dict(
                                        args=[
                                            {
                                                "scene.camera": dict(
                                                    eye=dict(x=1.5, y=1.5, z=1.5)
                                                )
                                            }
                                        ],
                                        label="Reset View",
                                        method="relayout",
                                    ),
                                    dict(
                                        args=[
                                            {
                                                "scene.camera": dict(
                                                    eye=dict(x=0, y=0, z=2)
                                                )
                                            }
                                        ],
                                        label="Top View",
                                        method="relayout",
                                    ),
                                    dict(
                                        args=[
                                            {
                                                "scene.camera": dict(
                                                    eye=dict(x=2, y=0, z=0)
                                                )
                                            }
                                        ],
                                        label="Side View",
                                        method="relayout",
                                    ),
                                ]
                            ),
                        )
                    ]
                )

            self.logger.info("3D network visualization created successfully")
            return fig

        except Exception as e:
            self.logger.error(f"Failed to create 3D visualization: {e}")
            # 기본 그래프 반환
            return go.Figure()

    def create_logistics_dashboard(self, df: pd.DataFrame) -> go.Figure:
        """물류 대시보드 생성 (멀티 패널)"""
        try:
            # 서브플롯 생성
            fig = make_subplots(
                rows=2,
                cols=2,
                specs=[
                    [{"type": "scatter3d"}, {"type": "bar"}],
                    [{"type": "scatter"}, {"type": "pie"}],
                ],
                subplot_titles=(
                    "3D Network",
                    "Warehouse Performance",
                    "Flow Timeline",
                    "Node Distribution",
                ),
                vertical_spacing=0.1,
                horizontal_spacing=0.1,
            )

            # 1. 3D 네트워크 (기존 함수 활용)
            network_fig = self.create_3d_network_visualization(show_labels=False)
            for trace in network_fig.data:
                fig.add_trace(trace, row=1, col=1)

            # 2. 창고별 성과 차트
            warehouse_stats = self._calculate_warehouse_stats(df)
            fig.add_trace(
                go.Bar(
                    x=list(warehouse_stats.keys()),
                    y=list(warehouse_stats.values()),
                    name="Warehouse Performance",
                    marker_color="#1f77b4",
                ),
                row=1,
                col=2,
            )

            # 3. 플로우 타임라인
            timeline_data = self._create_flow_timeline(df)
            fig.add_trace(
                go.Scatter(
                    x=timeline_data["dates"],
                    y=timeline_data["flows"],
                    mode="lines+markers",
                    name="Logistics Flow",
                    line=dict(color="#ff7f0e", width=2),
                ),
                row=2,
                col=1,
            )

            # 4. 노드 타입별 분포
            node_distribution = self._calculate_node_distribution()
            fig.add_trace(
                go.Pie(
                    labels=list(node_distribution.keys()),
                    values=list(node_distribution.values()),
                    name="Node Distribution",
                    hole=0.3,
                ),
                row=2,
                col=2,
            )

            # 레이아웃 업데이트
            fig.update_layout(
                title_text="HVDC Logistics Dashboard",
                showlegend=True,
                height=800,
                template="plotly_white",
            )

            return fig

        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            return go.Figure()

    def _calculate_warehouse_stats(self, df: pd.DataFrame) -> Dict[str, float]:
        """창고별 성과 통계 계산"""
        stats = {}
        for warehouse in self.hvdc_warehouses:
            if warehouse in df.columns:
                # 실제 데이터 기반 성과 계산
                data_count = len(df[df[warehouse].notna() & (df[warehouse] != "")])
                stats[warehouse] = data_count
        return stats

    def _create_flow_timeline(self, df: pd.DataFrame) -> Dict[str, List]:
        """물류 플로우 타임라인 생성"""
        # 날짜 컬럼 찾기
        date_columns = [col for col in df.columns if "date" in col.lower()]

        if not date_columns:
            # 기본 타임라인 생성
            dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
            flows = np.random.randint(10, 100, size=len(dates))
        else:
            # 실제 데이터 기반 타임라인
            all_dates = []
            for col in date_columns:
                dates = pd.to_datetime(df[col], errors="coerce").dropna()
                all_dates.extend(dates.tolist())

            if all_dates:
                date_series = pd.Series(all_dates)
                monthly_flows = (
                    date_series.dt.to_period("M").value_counts().sort_index()
                )
                dates = [pd.to_datetime(str(period)) for period in monthly_flows.index]
                flows = monthly_flows.values.tolist()
            else:
                dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
                flows = np.random.randint(10, 100, size=len(dates))

        return {"dates": dates, "flows": flows}

    def _calculate_node_distribution(self) -> Dict[str, int]:
        """노드 타입별 분포 계산"""
        distribution = {}
        for node, attrs in self.G.nodes(data=True):
            node_type = attrs.get("type", NetworkNodeType.TRANSIT)
            node_type_str = node_type.value
            distribution[node_type_str] = distribution.get(node_type_str, 0) + 1
        return distribution

    def _check_auto_triggers(self, df: pd.DataFrame) -> List[str]:
        """자동 트리거 조건 확인"""
        triggers = []

        # 데이터 품질 체크
        if len(df) < 100:
            triggers.append("/validate_data quality_check")

        # 네트워크 복잡도 체크
        if len(self.G.nodes()) > 50:
            triggers.append("/optimize_network performance")

        # FANR 규정 체크
        if "FANR" in str(df.columns):
            triggers.append("/fanr_compliance check")

        return triggers

    def export_visualization(
        self, fig: go.Figure, filename: str = None, format: str = "html"
    ) -> Dict[str, Any]:
        """
        시각화 결과 내보내기

        Args:
            fig: Plotly 그래프
            filename: 파일명
            format: 내보내기 형식 (html, png, pdf)

        Returns:
            Dict: 내보내기 결과
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"HVDC_3D_Network_{timestamp}"

            # output 디렉토리 생성
            import os

            os.makedirs("output", exist_ok=True)

            if format == "html":
                # 파일 경로가 이미 .html 확장자를 포함하는지 확인
                if filename.endswith(".html"):
                    filepath = filename
                else:
                    filepath = f"{filename}.html"
                fig.write_html(filepath)
            elif format == "png":
                filepath = f"output/{filename}.png"
                fig.write_image(filepath, width=1200, height=800)
            elif format == "pdf":
                filepath = f"output/{filename}.pdf"
                fig.write_image(filepath)
            else:
                raise ValueError(f"Unsupported format: {format}")

            result = {
                "status": "SUCCESS",
                "confidence": 0.95,
                "mode": self.mode,
                "filepath": filepath,
                "format": format,
                "triggers": ["/open_file " + filepath],
                "next_cmds": ["/share_visualization", "/analyze_network_metrics"],
            }

            self.logger.info(f"Visualization exported: {filepath}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to export visualization: {e}")
            return {
                "status": "FAIL",
                "confidence": 0.0,
                "error": str(e),
                "mode": self.mode,
                "triggers": ["/switch_mode ZERO"],
                "next_cmds": ["/check_file_permissions", "/switch_mode ZERO"],
            }


def main():
    """메인 실행 함수"""
    print("🚀 MACHO-GPT v3.4-mini - HVDC 3D Network Visualizer")
    print("=" * 60)

    # 시각화 시스템 초기화
    visualizer = LogiNetworkVisualizer(mode="LATTICE")

    # 샘플 데이터 생성
    sample_data = pd.DataFrame(
        {
            "Item": [f"ITEM_{i:03d}" for i in range(1, 101)],
            "DSV Indoor": [
                datetime.now() - timedelta(days=np.random.randint(1, 365))
                for _ in range(100)
            ],
            "DSV Outdoor": [
                datetime.now() - timedelta(days=np.random.randint(1, 365))
                for _ in range(100)
            ],
            "MIR": [
                datetime.now() - timedelta(days=np.random.randint(1, 365))
                for _ in range(100)
            ],
            "SHU": [
                datetime.now() - timedelta(days=np.random.randint(1, 365))
                for _ in range(100)
            ],
            "Category": np.random.choice(["Electrical", "Mechanical", "Control"], 100),
        }
    )

    # 데이터 로드
    print("📊 물류 데이터 로드 중...")
    load_result = visualizer.load_logistics_data(sample_data)

    if load_result["status"] == "SUCCESS":
        print(
            f"✅ 데이터 로드 완료: {load_result['nodes_count']} 노드, {load_result['edges_count']} 엣지"
        )

        # 3D 네트워크 시각화 생성
        print("🎨 3D 네트워크 시각화 생성 중...")
        fig_3d = visualizer.create_3d_network_visualization(
            title="HVDC Logistics Network 3D Visualization"
        )

        # 대시보드 생성
        print("📈 물류 대시보드 생성 중...")
        fig_dashboard = visualizer.create_logistics_dashboard(sample_data)

        # 결과 내보내기
        print("💾 시각화 결과 내보내기 중...")
        export_result = visualizer.export_visualization(fig_3d, "HVDC_3D_Network_Demo")

        if export_result["status"] == "SUCCESS":
            print(f"✅ 시각화 내보내기 완료: {export_result['filepath']}")
        else:
            print(f"❌ 내보내기 실패: {export_result['error']}")

        # 대시보드도 내보내기
        dashboard_result = visualizer.export_visualization(
            fig_dashboard, "HVDC_Dashboard_Demo"
        )

    else:
        print(f"❌ 데이터 로드 실패: {load_result['error']}")

    print("\n🔧 **추천 명령어:**")
    print("/visualize_3d_network --data=logistics_data.xlsx")
    print("/create_logistics_dashboard --interactive=true")
    print("/export_visualization --format=html --filename=network_report")
    print("/switch_mode LATTICE --enable_3d_visualization")


if __name__ == "__main__":
    main()
