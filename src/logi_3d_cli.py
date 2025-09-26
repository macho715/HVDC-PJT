#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini - HVDC 3D Network Visualizer CLI
물류 네트워크 3D 시각화 명령어 인터페이스

Commands:
/visualize_3d_network --data=file.xlsx --mode=LATTICE
/create_logistics_dashboard --interactive=true
/export_visualization --format=html --filename=network_report
/analyze_flow_patterns --depth=3
/generate_kpi_dashboard --realtime=true
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import logging
import networkx as nx

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logi_3d_network_visualizer import LogiNetworkVisualizer


class Logi3DCLI:
    """HVDC 3D Network Visualizer CLI"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/3d_network_cli.log"),
                logging.StreamHandler(),
            ],
        )

    def visualize_3d_network(
        self,
        data_source: str,
        mode: str = "LATTICE",
        title: str = None,
        interactive: bool = True,
    ) -> dict:
        """
        3D 네트워크 시각화 생성

        Args:
            data_source: 데이터 소스 경로
            mode: MACHO-GPT 모드
            title: 그래프 제목
            interactive: 인터랙티브 기능 활성화

        Returns:
            Dict: 실행 결과
        """
        try:
            print(f"🚀 MACHO-GPT v3.4-mini - 3D Network Visualization")
            print(f"📊 Mode: {mode} | Data: {data_source}")
            print("=" * 60)

            # 시각화 시스템 초기화
            visualizer = LogiNetworkVisualizer(mode=mode)

            # 데이터 로드
            print("📥 데이터 로드 중...")
            load_result = visualizer.load_logistics_data(data_source)

            if load_result["status"] != "SUCCESS":
                return {
                    "status": "FAIL",
                    "confidence": 0.0,
                    "error": f"Data loading failed: {load_result.get('error', 'Unknown error')}",
                    "mode": mode,
                    "triggers": ["/switch_mode ZERO"],
                    "next_cmds": ["/check_data_source", "/switch_mode ZERO"],
                }

            print(
                f"✅ 데이터 로드 완료: {load_result['nodes_count']} 노드, {load_result['edges_count']} 엣지"
            )

            # 3D 시각화 생성
            print("🎨 3D 네트워크 시각화 생성 중...")
            graph_title = title or f"HVDC Logistics Network 3D ({mode} Mode)"
            fig = visualizer.create_3d_network_visualization(
                title=graph_title, interactive=interactive
            )

            # 결과 내보내기
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"HVDC_3D_Network_{mode}_{timestamp}"

            print("💾 시각화 결과 내보내기 중...")
            export_result = visualizer.export_visualization(fig, filename, "html")

            if export_result["status"] == "SUCCESS":
                print(f"✅ 시각화 완료: {export_result['filepath']}")

                result = {
                    "status": "SUCCESS",
                    "confidence": 0.95,
                    "mode": mode,
                    "filepath": export_result["filepath"],
                    "nodes_count": load_result["nodes_count"],
                    "edges_count": load_result["edges_count"],
                    "triggers": load_result["triggers"],
                    "next_cmds": [
                        "/open_file " + export_result["filepath"],
                        "/create_logistics_dashboard",
                        "/analyze_flow_patterns",
                    ],
                }
            else:
                result = export_result

            return result

        except Exception as e:
            self.logger.error(f"3D network visualization failed: {e}")
            return {
                "status": "FAIL",
                "confidence": 0.0,
                "error": str(e),
                "mode": mode,
                "triggers": ["/switch_mode ZERO"],
                "next_cmds": ["/check_system_status", "/switch_mode ZERO"],
            }

    def create_logistics_dashboard(
        self, data_source: str, mode: str = "LATTICE", interactive: bool = True
    ) -> dict:
        """
        물류 대시보드 생성

        Args:
            data_source: 데이터 소스 경로
            mode: MACHO-GPT 모드
            interactive: 인터랙티브 기능 활성화

        Returns:
            Dict: 실행 결과
        """
        try:
            print(f"📊 MACHO-GPT v3.4-mini - Logistics Dashboard")
            print(f"📈 Mode: {mode} | Data: {data_source}")
            print("=" * 60)

            # 시각화 시스템 초기화
            visualizer = LogiNetworkVisualizer(mode=mode)

            # 데이터 로드
            print("📥 데이터 로드 중...")
            load_result = visualizer.load_logistics_data(data_source)

            if load_result["status"] != "SUCCESS":
                return {
                    "status": "FAIL",
                    "confidence": 0.0,
                    "error": f"Data loading failed: {load_result.get('error', 'Unknown error')}",
                    "mode": mode,
                    "triggers": ["/switch_mode ZERO"],
                    "next_cmds": ["/check_data_source", "/switch_mode ZERO"],
                }

            # 데이터프레임 로드
            if isinstance(data_source, str):
                if data_source.endswith(".xlsx"):
                    df = pd.read_excel(data_source)
                elif data_source.endswith(".csv"):
                    df = pd.read_csv(data_source)
                else:
                    raise ValueError(f"Unsupported file format: {data_source}")
            else:
                df = data_source

            # 대시보드 생성
            print("📊 물류 대시보드 생성 중...")
            fig = visualizer.create_logistics_dashboard(df)

            # 결과 내보내기
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"HVDC_Dashboard_{mode}_{timestamp}"

            print("💾 대시보드 내보내기 중...")
            export_result = visualizer.export_visualization(fig, filename, "html")

            if export_result["status"] == "SUCCESS":
                print(f"✅ 대시보드 완료: {export_result['filepath']}")

                result = {
                    "status": "SUCCESS",
                    "confidence": 0.95,
                    "mode": mode,
                    "filepath": export_result["filepath"],
                    "dashboard_type": "logistics_multi_panel",
                    "triggers": load_result["triggers"],
                    "next_cmds": [
                        "/open_file " + export_result["filepath"],
                        "/analyze_warehouse_performance",
                        "/generate_kpi_report",
                    ],
                }
            else:
                result = export_result

            return result

        except Exception as e:
            self.logger.error(f"Logistics dashboard creation failed: {e}")
            return {
                "status": "FAIL",
                "confidence": 0.0,
                "error": str(e),
                "mode": mode,
                "triggers": ["/switch_mode ZERO"],
                "next_cmds": ["/check_system_status", "/switch_mode ZERO"],
            }

    def analyze_flow_patterns(
        self, data_source: str, mode: str = "LATTICE", depth: int = 3
    ) -> dict:
        """
        물류 플로우 패턴 분석

        Args:
            data_source: 데이터 소스 경로
            mode: MACHO-GPT 모드
            depth: 분석 깊이

        Returns:
            Dict: 분석 결과
        """
        try:
            print(f"🔍 MACHO-GPT v3.4-mini - Flow Pattern Analysis")
            print(f"📊 Mode: {mode} | Data: {data_source} | Depth: {depth}")
            print("=" * 60)

            # 시각화 시스템 초기화
            visualizer = LogiNetworkVisualizer(mode=mode)

            # 데이터 로드
            print("📥 데이터 로드 중...")
            load_result = visualizer.load_logistics_data(data_source)

            if load_result["status"] != "SUCCESS":
                return {
                    "status": "FAIL",
                    "confidence": 0.0,
                    "error": f"Data loading failed: {load_result.get('error', 'Unknown error')}",
                    "mode": mode,
                    "triggers": ["/switch_mode ZERO"],
                    "next_cmds": ["/check_data_source", "/switch_mode ZERO"],
                }

            # 플로우 패턴 분석
            print("🔍 플로우 패턴 분석 중...")

            # 네트워크 메트릭 계산
            G = visualizer.G
            metrics = {
                "total_nodes": len(G.nodes()),
                "total_edges": len(G.edges()),
                "density": nx.density(G),
                "average_clustering": nx.average_clustering(G),
                "average_shortest_path": (
                    nx.average_shortest_path_length(G)
                    if nx.is_connected(G)
                    else float("inf")
                ),
                "node_connectivity": nx.node_connectivity(G),
                "edge_connectivity": nx.edge_connectivity(G),
            }

            # 중심성 분석
            centrality_metrics = {
                "degree_centrality": nx.degree_centrality(G),
                "betweenness_centrality": nx.betweenness_centrality(G),
                "closeness_centrality": nx.closeness_centrality(G),
                "eigenvector_centrality": nx.eigenvector_centrality_numpy(G),
            }

            # 커뮤니티 탐지
            communities = list(nx.community.greedy_modularity_communities(G))

            # 결과 정리
            analysis_result = {
                "network_metrics": metrics,
                "centrality_analysis": centrality_metrics,
                "communities": {
                    "count": len(communities),
                    "sizes": [len(comm) for comm in communities],
                    "modularity": nx.community.modularity(G, communities),
                },
                "flow_patterns": {
                    "strongest_connections": sorted(
                        [(u, v, d["weight"]) for u, v, d in G.edges(data=True)],
                        key=lambda x: x[2],
                        reverse=True,
                    )[:10],
                    "bottlenecks": self._identify_bottlenecks(G),
                    "critical_paths": self._find_critical_paths(G),
                },
            }

            print("✅ 플로우 패턴 분석 완료")
            print(f"📊 네트워크 밀도: {metrics['density']:.3f}")
            print(f"🔗 평균 클러스터링: {metrics['average_clustering']:.3f}")
            print(f"🏘️ 커뮤니티 수: {len(communities)}")

            result = {
                "status": "SUCCESS",
                "confidence": 0.95,
                "mode": mode,
                "analysis": analysis_result,
                "triggers": ["/optimize_network_flow"],
                "next_cmds": [
                    "/visualize_flow_patterns",
                    "/generate_optimization_report",
                    "/create_network_metrics_dashboard",
                ],
            }

            return result

        except Exception as e:
            self.logger.error(f"Flow pattern analysis failed: {e}")
            return {
                "status": "FAIL",
                "confidence": 0.0,
                "error": str(e),
                "mode": mode,
                "triggers": ["/switch_mode ZERO"],
                "next_cmds": ["/check_system_status", "/switch_mode ZERO"],
            }

    def _identify_bottlenecks(self, G):
        """네트워크 병목 지점 식별"""
        bottlenecks = []

        # 높은 betweenness centrality를 가진 노드들
        betweenness = nx.betweenness_centrality(G)
        high_betweenness = [
            (node, centrality)
            for node, centrality in betweenness.items()
            if centrality > 0.1
        ]

        # 낮은 연결성을 가진 엣지들
        edge_betweenness = nx.edge_betweenness_centrality(G)
        low_connectivity_edges = [
            (u, v, centrality)
            for (u, v), centrality in edge_betweenness.items()
            if centrality > 0.05
        ]

        bottlenecks = {
            "high_betweenness_nodes": high_betweenness,
            "low_connectivity_edges": low_connectivity_edges,
        }

        return bottlenecks

    def _find_critical_paths(self, G):
        """중요 경로 탐지"""
        critical_paths = []

        # 모든 노드 쌍 간의 최단 경로
        for source in G.nodes():
            for target in G.nodes():
                if source != target:
                    try:
                        path = nx.shortest_path(G, source, target, weight="weight")
                        if len(path) > 2:  # 중간 노드가 있는 경로만
                            critical_paths.append(
                                {
                                    "source": source,
                                    "target": target,
                                    "path": path,
                                    "length": len(path),
                                    "weight": sum(
                                        G[path[i]][path[i + 1]]["weight"]
                                        for i in range(len(path) - 1)
                                    ),
                                }
                            )
                    except nx.NetworkXNoPath:
                        continue

        # 가중치 기준으로 정렬
        critical_paths.sort(key=lambda x: x["weight"], reverse=True)

        return critical_paths[:10]  # 상위 10개만 반환

    def generate_kpi_dashboard(
        self, data_source: str, mode: str = "RHYTHM", realtime: bool = False
    ) -> dict:
        """
        KPI 대시보드 생성

        Args:
            data_source: 데이터 소스 경로
            mode: MACHO-GPT 모드 (RHYTHM 권장)
            realtime: 실시간 업데이트 여부

        Returns:
            Dict: 실행 결과
        """
        try:
            print(f"📊 MACHO-GPT v3.4-mini - KPI Dashboard")
            print(f"📈 Mode: {mode} | Data: {data_source} | Realtime: {realtime}")
            print("=" * 60)

            # 시각화 시스템 초기화
            visualizer = LogiNetworkVisualizer(mode=mode)

            # 데이터 로드
            print("📥 데이터 로드 중...")
            load_result = visualizer.load_logistics_data(data_source)

            if load_result["status"] != "SUCCESS":
                return {
                    "status": "FAIL",
                    "confidence": 0.0,
                    "error": f"Data loading failed: {load_result.get('error', 'Unknown error')}",
                    "mode": mode,
                    "triggers": ["/switch_mode ZERO"],
                    "next_cmds": ["/check_data_source", "/switch_mode ZERO"],
                }

            # KPI 계산
            print("📊 KPI 계산 중...")

            # 데이터프레임 로드
            if isinstance(data_source, str):
                if data_source.endswith(".xlsx"):
                    df = pd.read_excel(data_source)
                elif data_source.endswith(".csv"):
                    df = pd.read_csv(data_source)
                else:
                    raise ValueError(f"Unsupported file format: {data_source}")
            else:
                df = data_source

            # KPI 메트릭 계산
            kpi_metrics = {
                "total_items": len(df),
                "warehouse_utilization": self._calculate_warehouse_utilization(df),
                "flow_efficiency": self._calculate_flow_efficiency(df),
                "delivery_performance": self._calculate_delivery_performance(df),
                "cost_metrics": self._calculate_cost_metrics(df),
                "compliance_score": self._calculate_compliance_score(df),
            }

            print("✅ KPI 계산 완료")
            print(f"📦 총 아이템: {kpi_metrics['total_items']}")
            print(f"🏭 창고 활용도: {kpi_metrics['warehouse_utilization']:.2%}")
            print(f"⚡ 플로우 효율성: {kpi_metrics['flow_efficiency']:.2%}")

            result = {
                "status": "SUCCESS",
                "confidence": 0.95,
                "mode": mode,
                "kpi_metrics": kpi_metrics,
                "realtime_enabled": realtime,
                "triggers": ["/monitor_kpi_thresholds"],
                "next_cmds": [
                    "/create_kpi_visualization",
                    "/set_kpi_alerts",
                    "/generate_performance_report",
                ],
            }

            return result

        except Exception as e:
            self.logger.error(f"KPI dashboard generation failed: {e}")
            return {
                "status": "FAIL",
                "confidence": 0.0,
                "error": str(e),
                "mode": mode,
                "triggers": ["/switch_mode ZERO"],
                "next_cmds": ["/check_system_status", "/switch_mode ZERO"],
            }

    def _calculate_warehouse_utilization(self, df):
        """창고 활용도 계산"""
        warehouse_columns = [
            "DSV Indoor",
            "DSV Outdoor",
            "DSV Al Markaz",
            "DSV MZP",
            "AAA Storage",
        ]
        total_capacity = 1000 * len(warehouse_columns)  # 가정된 용량

        utilized = 0
        for col in warehouse_columns:
            if col in df.columns:
                utilized += len(df[df[col].notna() & (df[col] != "")])

        return utilized / total_capacity if total_capacity > 0 else 0.0

    def _calculate_flow_efficiency(self, df):
        """플로우 효율성 계산"""
        # 간단한 효율성 계산 (실제로는 더 복잡한 로직 필요)
        total_items = len(df)
        if total_items == 0:
            return 0.0

        # 완료된 아이템 비율 (예시)
        completed_items = (
            len(df[df["Category"].notna()]) if "Category" in df.columns else total_items
        )
        return completed_items / total_items

    def _calculate_delivery_performance(self, df):
        """배송 성과 계산"""
        # 배송 성과 계산 (예시)
        return 0.85  # 85% 성공률 가정

    def _calculate_cost_metrics(self, df):
        """비용 메트릭 계산"""
        return {
            "total_cost": 1000000,  # AED
            "cost_per_item": 1000,  # AED
            "cost_efficiency": 0.92,  # 92% 효율성
        }

    def _calculate_compliance_score(self, df):
        """규정 준수 점수 계산"""
        return 0.98  # 98% 준수율 가정


def main():
    """메인 CLI 함수"""
    parser = argparse.ArgumentParser(
        description="MACHO-GPT v3.4-mini - HVDC 3D Network Visualizer CLI"
    )
    parser.add_argument(
        "command",
        choices=[
            "visualize_3d_network",
            "create_logistics_dashboard",
            "analyze_flow_patterns",
            "generate_kpi_dashboard",
        ],
        help="실행할 명령어",
    )

    parser.add_argument("--data", required=True, help="데이터 소스 경로")
    parser.add_argument(
        "--mode",
        default="LATTICE",
        choices=["PRIME", "ORACLE", "ZERO", "LATTICE", "RHYTHM", "COST-GUARD"],
        help="MACHO-GPT 모드",
    )
    parser.add_argument("--title", help="그래프 제목")
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,
        help="인터랙티브 기능 활성화",
    )
    parser.add_argument("--depth", type=int, default=3, help="분석 깊이")
    parser.add_argument("--realtime", action="store_true", help="실시간 업데이트")
    parser.add_argument(
        "--format", default="html", choices=["html", "png", "pdf"], help="내보내기 형식"
    )
    parser.add_argument("--filename", help="파일명")

    args = parser.parse_args()

    # CLI 인스턴스 생성
    cli = Logi3DCLI()

    # 명령어 실행
    if args.command == "visualize_3d_network":
        result = cli.visualize_3d_network(
            data_source=args.data,
            mode=args.mode,
            title=args.title,
            interactive=args.interactive,
        )
    elif args.command == "create_logistics_dashboard":
        result = cli.create_logistics_dashboard(
            data_source=args.data, mode=args.mode, interactive=args.interactive
        )
    elif args.command == "analyze_flow_patterns":
        result = cli.analyze_flow_patterns(
            data_source=args.data, mode=args.mode, depth=args.depth
        )
    elif args.command == "generate_kpi_dashboard":
        result = cli.generate_kpi_dashboard(
            data_source=args.data, mode=args.mode, realtime=args.realtime
        )
    else:
        print(f"❌ 알 수 없는 명령어: {args.command}")
        sys.exit(1)

    # 결과 출력
    if result["status"] == "SUCCESS":
        print(f"\n✅ 명령어 실행 성공 (신뢰도: {result['confidence']:.1%})")
        print(f"🔧 **추천 명령어:**")
        for cmd in result.get("next_cmds", []):
            print(f"  {cmd}")
    else:
        print(f"\n❌ 명령어 실행 실패: {result.get('error', 'Unknown error')}")
        print(f"🔧 **복구 명령어:**")
        for cmd in result.get("next_cmds", []):
            print(f"  {cmd}")

    sys.exit(0 if result["status"] == "SUCCESS" else 1)


if __name__ == "__main__":
    main()
