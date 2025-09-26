# ---------------------------
# file: data_loader.py
# ---------------------------
"""Data loading and caching utilities for GraphRAG dashboard."""

import streamlit as st


import json
from pathlib import Path
from typing import Tuple, Union

import pandas as pd


__all__ = ["load_graph_data", "load_sample_data"]


@st.cache_data(show_spinner=False)
def load_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return built‑in sample GraphRAG dataset (nodes, links)."""
    sample_path = Path(__file__).with_suffix("").parent / "sample_graphrag.json"
    return load_graph_data(sample_path)


@st.cache_data(max_entries=10, ttl=3600)
def load_graph_data(src: Union[Path, str, bytes]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load GraphRAG JSON and return nodes / links DataFrames.

    Parameters
    ----------
    src : Path | str | bytes
        File path or bytes‑like object returned from Streamlit uploader.

    Returns
    -------
    (nodes_df, links_df)
    """

    if isinstance(src, (str, Path)):
        data = json.loads(Path(src).read_text(encoding="utf‑8"))
    else:
        data = json.loads(src)

    if not {"nodes", "links"}.issubset(data):
        raise ValueError("Invalid GraphRAG JSON – expecting keys: 'nodes', 'links'.")

    nodes_df = pd.DataFrame(data["nodes"])
    links_df = pd.DataFrame(data["links"])

    return nodes_df, links_df


# ---------------------------
# file: graph_visualization.py
# ---------------------------
"""Plotly visualisation helpers + Path/Bottleneck analysis for GraphRAG."""

from functools import lru_cache
from typing import List, Tuple, Sequence, Optional

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

__all__ = [
    "create_network_graph",
    "create_timeline_chart",
    "create_stats_charts",
    "shortest_path",
    "top_bottlenecks",
]

# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────


@lru_cache(maxsize=32)
def _compute_layout(
    nodes_json: str, links_json: str, k: float = 2.5
) -> dict[str, Tuple[float, float]]:
    """Heavy NetworkX spring layout cached by JSON strings for performance."""
    G = nx.Graph()
    for node in pd.read_json(nodes_json, orient="records").to_dict("records"):
        G.add_node(node["id"], **node)
    for link in pd.read_json(links_json, orient="records").to_dict("records"):
        G.add_edge(link["source"], link["target"], **link)
    return nx.spring_layout(G, k=k, iterations=40, seed=42)


def _build_graph(nodes_df: pd.DataFrame, links_df: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    for _, node in nodes_df.iterrows():
        G.add_node(node["id"], **node.to_dict())
    for _, link in links_df.iterrows():
        if link["source"] in G.nodes and link["target"] in G.nodes:
            G.add_edge(link["source"], link["target"], **link.to_dict())
    return G


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ──────────────────────────────────────────────────────────────────────────────


def shortest_path(
    nodes_df: pd.DataFrame,
    links_df: pd.DataFrame,
    source: str,
    target: str,
    weight: Optional[str] = None,
) -> List[str]:
    """Return list of node ids forming the shortest path between *source* and *target*.

    If *weight* column exists in links_df, it will be used as edge weight.
    Raises NetworkXNoPath if no path exists.
    """
    G = _build_graph(nodes_df, links_df)
    if weight and weight not in links_df.columns:
        weight = None  # fallback if invalid weight column
    return nx.shortest_path(G, source=source, target=target, weight=weight)


def top_bottlenecks(
    nodes_df: pd.DataFrame,
    links_df: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """Return *top_n* edges with highest betweenness centrality (bottlenecks)."""
    G = _build_graph(nodes_df, links_df)
    eb_cent = nx.edge_betweenness_centrality(G, normalized=True)
    df = (
        pd.DataFrame(
            [{"edge": edge, "score": score} for edge, score in eb_cent.items()]
        )
        .sort_values("score", ascending=False)
        .head(top_n)
    )
    return df


def create_network_graph(
    nodes_df: pd.DataFrame,
    links_df: pd.DataFrame,
    highlight_edges: Optional[Sequence[Tuple[str, str]]] = None,
) -> go.Figure:
    """Return interactive Plotly network graph with optional *highlight_edges*."""
    pos = _compute_layout(nodes_df.to_json(), links_df.to_json())
    G = _build_graph(nodes_df, links_df)

    # Prepare edge traces – highlight if in path/bottlenecks
    edge_x, edge_y, edge_colors, edge_widths = [], [], [], []
    highlight_set = set(tuple(sorted(e)) for e in (highlight_edges or []))
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        if tuple(sorted((u, v))) in highlight_set:
            edge_colors.append("#d62728")  # red
            edge_widths.append(4)
        else:
            edge_colors.append("#888")
            edge_widths.append(1.5)

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=edge_widths, color=edge_colors),
        hoverinfo="none",
    )

    # Node trace
    node_x, node_y, node_text, node_hover, node_colors, node_sizes = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        nd = G.nodes[node]
        node_text.append(nd["name"])
        node_hover.append(
            f"<b>{nd['name']}</b><br>Type: {nd['type']}<br>Description: {nd.get('description', 'N/A')}"
        )
        node_colors.append(nd["color"])
        node_sizes.append(nd["size"])

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        hovertext=node_hover,
        text=node_text,
        textposition="bottom center",
        marker=dict(
            size=node_sizes, color=node_colors, line=dict(width=2, color="white")
        ),
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="Samsung C&T HVDC Project – Network Flow (Path/Bottleneck Analysis)",
        showlegend=False,
        hovermode="closest",
        margin=dict(b=20, l=5, r=5, t=40),
        plot_bgcolor="white",
        height=600,
    )
    return fig


# Existing timeline & stats functions remain unchanged


def create_timeline_chart(links_df: pd.DataFrame) -> go.Figure:
    df = links_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    fig = px.timeline(
        df,
        x_start="date",
        x_end="date",
        y="label",
        color="type",
        title="Project Timeline – Contract & Logistics Events",
    )
    fig.update_layout(height=400)
    return fig


def create_stats_charts(
    nodes_df: pd.DataFrame, links_df: pd.DataFrame
) -> Tuple[go.Figure, go.Figure]:
    node_counts = nodes_df["type"].value_counts()
    link_counts = links_df["type"].value_counts()
    fig_entities = px.pie(
        values=node_counts.values,
        names=node_counts.index,
        title="Entity Types Distribution",
    )
    fig_relations = px.bar(
        x=link_counts.index,
        y=link_counts.values,
        labels=dict(x="Relationship Type", y="Count"),
        title="Relationship Types Frequency",
    )
    return fig_entities, fig_relations


# ---------------------------
# file: ui_components.py
# ---------------------------
"""Reusable Streamlit UI components."""

from typing import Tuple

import streamlit as st
import pandas as pd

__all__ = [
    "render_header",
    "render_sidebar_controls",
]


def render_header() -> None:
    st.markdown(
        """
        <style>
            .main-header {background: linear-gradient(90deg, #1f77b4, #ff7f0e); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="main-header">
            <h1>🔗 GraphRAG Dashboard</h1>
            <p>Samsung C&T HVDC Project – Contract & Logistics Flow Analysis</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls(nodes_df: pd.DataFrame, links_df: pd.DataFrame):
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")

        st.subheader("🔍 Filters")
        node_types = ["All"] + sorted(nodes_df["type"].unique())
        link_types = ["All"] + sorted(links_df["type"].unique())

        sel_type = st.selectbox("Entity Type", node_types)
        sel_rel = st.selectbox("Relationship Type", link_types)

        if "date" in links_df.columns:
            links_df["date"] = pd.to_datetime(links_df["date"], errors="coerce")
            min_dt, max_dt = links_df["date"].min(), links_df["date"].max()
            date_range = st.date_input(
                "Date Range", value=(min_dt, max_dt), min_value=min_dt, max_value=max_dt
            )
        else:
            date_range = None

        st.subheader("🔬 Analysis Options")
        path_analysis = st.checkbox("Path / Bottleneck Analysis", value=False)
        opts = {
            "timeline": st.checkbox("Show Timeline", value=True),
            "stats": st.checkbox("Show Statistics", value=True),
            "path": path_analysis,
        }

        path_params = {}
        if path_analysis:
            st.markdown("---")
            st.subheader("Path Analysis Settings")
            all_nodes = sorted(nodes_df["id"].tolist())
            src = st.selectbox("Source Node", all_nodes)
            dst = st.selectbox("Target Node", all_nodes, index=len(all_nodes) - 1)
            top_n = st.slider("Top Bottlenecks (edge betweenness)", 1, 10, 5)
            path_params = {"src": src, "dst": dst, "top_n": top_n}

    # Apply filters
    if sel_type != "All":
        nodes_df = nodes_df[nodes_df["type"] == sel_type]
    if sel_rel != "All":
        links_df = links_df[links_df["type"] == sel_rel]
    if date_range and "date" in links_df.columns:
        start, end = date_range
        mask = (links_df["date"] >= pd.to_datetime(start)) & (
            links_df["date"] <= pd.to_datetime(end)
        )
        links_df = links_df[mask]

    return nodes_df, links_df, opts, path_params


# ---------------------------
# file: app.py (entry point)
# ---------------------------
"""Streamlit entry‑point for GraphRAG Dashboard (refactored with Path Analysis)."""

import streamlit as st
import pandas as pd


render_header()

# Load data (sample by default)
nodes_df, links_df = load_sample_data()

# Allow user upload
uploaded = st.file_uploader(
    "Upload GraphRAG JSON",
    type=["json"],
    help="Export generated by /logi-master or Palantir Ontology",
)
if uploaded:
    try:
        nodes_df, links_df = load_graph_data(uploaded.getvalue())
        st.success("✅ JSON loaded!")
    except Exception as e:
        st.error(f"❌ Failed to load JSON: {e}")

# Sidebar filters & options
nodes_df, links_df, opts, path_params = render_sidebar_controls(nodes_df, links_df)

highlight_edges = []
if opts["path"]:
    try:
        spath = shortest_path(
            nodes_df, links_df, path_params["src"], path_params["dst"]
        )
        highlight_edges = [(spath[i], spath[i + 1]) for i in range(len(spath) - 1)]
        st.sidebar.success(f"Shortest path length: {len(spath) - 1}")

        # Bottleneck edges by betweenness centrality
        b_df = top_bottlenecks(nodes_df, links_df, top_n=path_params["top_n"])
        st.sidebar.markdown("### 🔥 Top Bottlenecks")
        st.sidebar.table(b_df)
        highlight_edges += b_df["edge"].tolist()
    except Exception as e:
        st.sidebar.error(f"Path analysis failed: {e}")

# Main visualisation
col_net, col_right = st.columns([2, 1])
with col_net:
    st.subheader("🌐 Network Graph")
    fig_net = create_network_graph(nodes_df, links_df, highlight_edges=highlight_edges)
    st.plotly_chart(fig_net, use_container_width=True)

with col_right:
    if opts["timeline"] and "date" in links_df.columns:
        st.subheader("📅 Timeline")
        st.plotly_chart(create_timeline_chart(links_df), use_container_width=True)
    if opts["stats"]:
        st.subheader("📊 Statistics")
        fig1, fig2 = create_stats_charts(nodes_df, links_df)
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#666;'>🔗 GraphRAG Dashboard v1.2 (Path Analysis) | Generated: {pd.Timestamp.utcnow():%Y-%m-%d %H:%M %Z}</div>",
    unsafe_allow_html=True,
)
