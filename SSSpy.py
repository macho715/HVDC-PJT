import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
import json
from datetime import datetime, timedelta
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="GraphRAG Dashboard - Samsung C&T HVDC",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 사이드바 스타일
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        background-color: #ffffff;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 헤더
st.markdown(
    """
<div class="main-header">
    <h1>🔗 GraphRAG Dashboard</h1>
    <p>Samsung C&T HVDC Project - Contract & Logistics Flow Analysis</p>
</div>
""",
    unsafe_allow_html=True,
)


# 샘플 GraphRAG 데이터 (삼성물산 HVDC 프로젝트)
@st.cache_data
def load_sample_data():
    nodes_data = [
        {
            "id": "samsung_ct",
            "name": "Samsung C&T",
            "type": "contractor",
            "size": 30,
            "color": "#1f77b4",
            "description": "메인 계약자, HVDC 프로젝트 총괄",
        },
        {
            "id": "dsv",
            "name": "DSV",
            "type": "logistics",
            "size": 25,
            "color": "#ff7f0e",
            "description": "글로벌 물류 운송업체",
        },
        {
            "id": "jopetwil71",
            "name": "JOPETWIL 71",
            "type": "vessel",
            "size": 20,
            "color": "#2ca02c",
            "description": "LCT(Landing Craft Tank) 선박",
        },
        {
            "id": "agi",
            "name": "AGI",
            "type": "destination",
            "size": 25,
            "color": "#d62728",
            "description": "최종 납품지 (섬 현장)",
        },
        {
            "id": "adnoc",
            "name": "ADNOC",
            "type": "client",
            "size": 28,
            "color": "#9467bd",
            "description": "아부다비 국영석유회사 (최종 고객)",
        },
        {
            "id": "al_jaber",
            "name": "AL JABER",
            "type": "contractor",
            "size": 22,
            "color": "#8c564b",
            "description": "2025-06 신규 계약자",
        },
        {
            "id": "dsv_outdoor",
            "name": "DSV OUTDOOR",
            "type": "warehouse",
            "size": 18,
            "color": "#e377c2",
            "description": "야적장 창고시설",
        },
        {
            "id": "hvdc_equipment",
            "name": "HVDC Equipment",
            "type": "cargo",
            "size": 15,
            "color": "#7f7f7f",
            "description": "고압직류송전 장비",
        },
        {
            "id": "project_site",
            "name": "Project Site",
            "type": "location",
            "size": 20,
            "color": "#bcbd22",
            "description": "HVDC 프로젝트 현장",
        },
    ]

    links_data = [
        {
            "source": "samsung_ct",
            "target": "dsv",
            "type": "contract",
            "label": "위탁계약",
            "strength": 2,
            "date": "2024-03-15",
        },
        {
            "source": "dsv",
            "target": "jopetwil71",
            "type": "transport",
            "label": "운송",
            "strength": 1.5,
            "date": "2024-04-20",
        },
        {
            "source": "jopetwil71",
            "target": "agi",
            "type": "delivery",
            "label": "납품",
            "strength": 1.8,
            "date": "2024-05-10",
        },
        {
            "source": "samsung_ct",
            "target": "adnoc",
            "type": "contract",
            "label": "주계약",
            "strength": 3,
            "date": "2024-01-10",
        },
        {
            "source": "samsung_ct",
            "target": "al_jaber",
            "type": "subcontract",
            "label": "하도급",
            "strength": 1.2,
            "date": "2025-06-01",
        },
        {
            "source": "dsv",
            "target": "dsv_outdoor",
            "type": "storage",
            "label": "창고보관",
            "strength": 1,
            "date": "2024-04-01",
        },
        {
            "source": "samsung_ct",
            "target": "hvdc_equipment",
            "type": "supply",
            "label": "공급",
            "strength": 2.5,
            "date": "2024-03-20",
        },
        {
            "source": "hvdc_equipment",
            "target": "jopetwil71",
            "type": "loading",
            "label": "선적",
            "strength": 1.5,
            "date": "2024-04-25",
        },
        {
            "source": "agi",
            "target": "project_site",
            "type": "installation",
            "label": "설치",
            "strength": 2,
            "date": "2024-05-15",
        },
        {
            "source": "adnoc",
            "target": "project_site",
            "type": "ownership",
            "label": "소유",
            "strength": 2.2,
            "date": "2024-01-15",
        },
    ]

    return pd.DataFrame(nodes_data), pd.DataFrame(links_data)


def create_network_graph(nodes_df, links_df, selected_nodes=None, highlight_path=None):
    """네트워크 그래프 생성"""

    # NetworkX 그래프 생성
    G = nx.Graph()

    # 노드 추가
    for _, node in nodes_df.iterrows():
        G.add_node(node["id"], **node.to_dict())

    # 엣지 추가
    for _, link in links_df.iterrows():
        if link["source"] in G.nodes and link["target"] in G.nodes:
            G.add_edge(link["source"], link["target"], **link.to_dict())

    # 레이아웃 계산
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

    # 엣지 트레이스
    edge_x = []
    edge_y = []
    edge_info = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        edge_data = G.edges[edge]
        edge_info.append(f"{edge_data.get('label', 'connection')}")

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    # 노드 트레이스
    node_x = []
    node_y = []
    node_text = []
    node_info = []
    node_colors = []
    node_sizes = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        node_data = G.nodes[node]
        node_text.append(node_data["name"])
        node_info.append(
            f"<b>{node_data['name']}</b><br>"
            + f"Type: {node_data['type']}<br>"
            + f"Description: {node_data.get('description', 'N/A')}"
        )
        node_colors.append(node_data["color"])
        node_sizes.append(node_data["size"])

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        text=node_text,
        textposition="bottom center",
        hovertext=node_info,
        marker=dict(
            size=node_sizes, color=node_colors, line=dict(width=2, color="white")
        ),
    )

    # 레이아웃 설정
    layout = go.Layout(
        title="Samsung C&T HVDC Project - Network Flow",
        titlefont_size=16,
        showlegend=False,
        hovermode="closest",
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[
            dict(
                text="Drag nodes to rearrange | Hover for details",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.005,
                y=-0.002,
                xanchor="left",
                yanchor="bottom",
                font=dict(color="#888", size=12),
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
        height=600,
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
    return fig


def create_timeline_chart(links_df):
    """타임라인 차트 생성"""
    links_df["date"] = pd.to_datetime(links_df["date"])
    timeline_data = links_df.sort_values("date")

    fig = px.timeline(
        timeline_data,
        x_start="date",
        x_end="date",
        y="label",
        color="type",
        title="Project Timeline - Contract & Logistics Events",
        labels={"label": "Event", "date": "Date"},
    )

    fig.update_layout(height=400)
    return fig


def create_stats_charts(nodes_df, links_df):
    """통계 차트 생성"""

    # 노드 타입별 분포
    node_stats = nodes_df["type"].value_counts()
    fig1 = px.pie(
        values=node_stats.values,
        names=node_stats.index,
        title="Entity Types Distribution",
    )

    # 관계 타입별 분포
    link_stats = links_df["type"].value_counts()
    fig2 = px.bar(
        x=link_stats.index,
        y=link_stats.values,
        title="Relationship Types Frequency",
        labels={"x": "Relationship Type", "y": "Count"},
    )

    return fig1, fig2


# 사이드바
with st.sidebar:
    st.header("🎛️ Dashboard Controls")

    # 데이터 로드
    nodes_df, links_df = load_sample_data()

    # 파일 업로드 옵션
    st.subheader("📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload GraphRAG JSON",
        type=["json"],
        help="Upload your GraphRAG_SCT_AGI_Flow_Export.json file",
    )

    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            if "nodes" in data and "links" in data:
                nodes_df = pd.DataFrame(data["nodes"])
                links_df = pd.DataFrame(data["links"])
                st.success("✅ Data loaded successfully!")
            else:
                st.error("❌ Invalid JSON format")
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")

    # 필터 옵션
    st.subheader("🔍 Filters")

    # 노드 타입 필터
    node_types = ["All"] + list(nodes_df["type"].unique())
    selected_type = st.selectbox("Entity Type", node_types)

    # 관계 타입 필터
    link_types = ["All"] + list(links_df["type"].unique())
    selected_relation = st.selectbox("Relationship Type", link_types)

    # 날짜 범위 필터 (만약 date 컬럼이 있다면)
    if "date" in links_df.columns:
        links_df["date"] = pd.to_datetime(links_df["date"])
        date_range = st.date_input(
            "Date Range",
            value=(links_df["date"].min(), links_df["date"].max()),
            min_value=links_df["date"].min(),
            max_value=links_df["date"].max(),
        )

    # 분석 옵션
    st.subheader("🔬 Analysis Options")
    show_timeline = st.checkbox("Show Timeline", value=True)
    show_stats = st.checkbox("Show Statistics", value=True)
    show_path_analysis = st.checkbox("Path Analysis", value=False)

    # 내보내기 옵션
    st.subheader("💾 Export Options")
    if st.button("📊 Generate Report"):
        st.success("Report generation started!")

    if st.button("📁 Export JSON"):
        export_data = {
            "nodes": nodes_df.to_dict("records"),
            "links": links_df.to_dict("records"),
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "total_nodes": len(nodes_df),
                "total_links": len(links_df),
            },
        }
        st.download_button(
            label="Download GraphRAG Export",
            data=json.dumps(export_data, indent=2),
            file_name="GraphRAG_SCT_AGI_Export.json",
            mime="application/json",
        )

# 메인 컨텐츠 영역
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🕸️ Network Visualization")

    # 필터 적용
    filtered_nodes = nodes_df.copy()
    filtered_links = links_df.copy()

    if selected_type != "All":
        filtered_nodes = filtered_nodes[filtered_nodes["type"] == selected_type]

    if selected_relation != "All":
        filtered_links = filtered_links[filtered_links["type"] == selected_relation]

    # 네트워크 그래프 생성 및 표시
    network_fig = create_network_graph(filtered_nodes, filtered_links)
    st.plotly_chart(network_fig, use_container_width=True)

with col2:
    st.subheader("📊 Key Metrics")

    # 메트릭 카드들
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Entities", len(filtered_nodes))
        st.metric("Relationships", len(filtered_links))
    with col_b:
        st.metric("Entity Types", filtered_nodes["type"].nunique())
        st.metric("Relation Types", filtered_links["type"].nunique())

    # 엔티티 리스트
    st.subheader("🏢 Entities")
    for _, node in filtered_nodes.iterrows():
        with st.expander(f"{node['name']} ({node['type']})"):
            st.write(f"**Type:** {node['type']}")
            st.write(f"**Description:** {node.get('description', 'N/A')}")

            # 연결된 관계 표시
            connected_links = filtered_links[
                (filtered_links["source"] == node["id"])
                | (filtered_links["target"] == node["id"])
            ]
            if not connected_links.empty:
                st.write("**Connected Relationships:**")
                for _, link in connected_links.iterrows():
                    st.write(f"• {link['label']} ({link['type']})")

# 하단 차트 섹션
if show_timeline and "date" in links_df.columns:
    st.subheader("📅 Project Timeline")
    timeline_fig = create_timeline_chart(filtered_links)
    st.plotly_chart(timeline_fig, use_container_width=True)

if show_stats:
    st.subheader("📈 Analytics Dashboard")
    col1, col2 = st.columns(2)

    stats_fig1, stats_fig2 = create_stats_charts(filtered_nodes, filtered_links)

    with col1:
        st.plotly_chart(stats_fig1, use_container_width=True)

    with col2:
        st.plotly_chart(stats_fig2, use_container_width=True)

if show_path_analysis:
    st.subheader("🛣️ Path Analysis")

    col1, col2 = st.columns(2)
    with col1:
        start_node = st.selectbox("Start Node", filtered_nodes["name"].tolist())
    with col2:
        end_node = st.selectbox("End Node", filtered_nodes["name"].tolist())

    if st.button("Find Path"):
        st.info(f"Analyzing path from {start_node} to {end_node}...")
        # 여기에 경로 분석 로직을 추가할 수 있습니다

# GraphRAG 쿼리 인터페이스
st.subheader("🤖 GraphRAG Query Interface")
query_input = st.text_input(
    "Natural Language Query",
    placeholder="예: 'Samsung C&T에서 AGI까지의 모든 경로를 보여줘' 또는 'DSV와 연결된 모든 엔티티는?'",
)

if st.button("🔍 Execute Query") and query_input:
    with st.spinner("Processing GraphRAG query..."):
        # 실제 GraphRAG 처리는 여기에 구현
        st.success("Query processed!")

        # 예시 응답
        if "samsung" in query_input.lower() and "agi" in query_input.lower():
            st.write("**Query Result:**")
            st.write("Samsung C&T → DSV (위탁계약) → JOPETWIL 71 (운송) → AGI (납품)")
            st.write("**Alternative Path:**")
            st.write(
                "Samsung C&T → HVDC Equipment (공급) → JOPETWIL 71 (선적) → AGI (납품)"
            )
        elif "dsv" in query_input.lower():
            st.write("**DSV Connected Entities:**")
            st.write("• Samsung C&T (위탁계약)")
            st.write("• JOPETWIL 71 (운송)")
            st.write("• DSV OUTDOOR (창고보관)")
        else:
            st.write(
                "Query processed. Please refine your question for more specific results."
            )

# 푸터
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666;'>
    <p>🔗 GraphRAG Dashboard v1.0 | Samsung C&T HVDC Project Analysis</p>
    <p>Powered by Streamlit + Plotly + NetworkX | Generated: {}</p>
</div>
""".format(
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ),
    unsafe_allow_html=True,
)
