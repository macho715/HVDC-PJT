import pandas as pd
import networkx as nx
import plotly.graph_objs as go
import numpy as np

# 1. 데이터 로드 (엑셀 예시)
df = pd.read_excel("data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
# 노드/엣지 추출 예시 (컬럼명에 맞게 수정)
if "From" in df.columns and "To" in df.columns:
    nodes = set(df["From"]).union(set(df["To"]))
    edges = list(zip(df["From"], df["To"]))
else:
    # 샘플 데이터 생성 (컬럼이 없을 경우)
    nodes = [f"N{i}" for i in range(20)]
    edges = [(nodes[i], nodes[(i + 1) % 20]) for i in range(20)]

g = nx.Graph()
g.add_nodes_from(nodes)
g.add_edges_from(edges)

# 중심성 계산 (Betweenness)
centrality = nx.betweenness_centrality(g)
max_central = max(centrality.values()) if centrality else 1

# 3D 레이아웃
pos = nx.spring_layout(g, dim=3, seed=42)
node_x, node_y, node_z = zip(*[pos[n] for n in g.nodes()])

# 노드 크기/색상 (중심성 기반)
node_sizes = [
    18 + 32 * (centrality[n] / max_central if max_central else 0) for n in g.nodes()
]
node_colors = [
    f"rgba(255,{180+int(60*(centrality[n]/max_central if max_central else 0))},0,0.95)"
    for n in g.nodes()
]

# Glow 효과
glow_trace = go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode="markers",
    marker=dict(
        size=[s * 2.2 for s in node_sizes],
        color="rgba(255,200,0,0.08)",
        opacity=0.18,
        symbol="circle",
    ),
    showlegend=False,
)

# 노드 trace
node_trace = go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode="markers",
    marker=dict(
        size=node_sizes,
        color=node_colors,
        line=dict(width=2, color="white"),
        opacity=0.98,
        symbol="circle",
    ),
    text=[f"{n} (중심성: {centrality[n]:.2f})" for n in g.nodes()],
    hoverinfo="text",
)


def bezier(p0, p1, p2, t):
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t**2 * p2


edge_traces = []
for u, v in g.edges():
    x0, y0, z0 = pos[u]
    x1, y1, z1 = pos[v]
    mx, my, mz = (
        (x0 + x1) / 2 + np.random.uniform(-0.08, 0.08),
        (y0 + y1) / 2 + np.random.uniform(-0.08, 0.08),
        (z0 + z1) / 2 + np.random.uniform(-0.08, 0.08),
    )
    t = np.linspace(0, 1, 16)
    bx = bezier(x0, mx, x1, t)
    by = bezier(y0, my, y1, t)
    bz = bezier(z0, mz, z1, t)
    edge_color = "rgba(255,200,80,0.45)"
    edge_traces.append(
        go.Scatter3d(
            x=bx,
            y=by,
            z=bz,
            mode="lines",
            line=dict(width=1.5, color=edge_color),
            hoverinfo="none",
        )
    )

# 애니메이션 프레임 (중심성 변화 예시)
frames = []
for t in range(10):
    anim_sizes = [s * (1 + 0.2 * np.sin(t + i)) for i, s in enumerate(node_sizes)]
    anim_colors = [
        f"rgba(255,{180+int(60*(centrality[n]/max_central if max_central else 0))},0,{0.7+0.3*np.sin(t+i):.2f})"
        for i, n in enumerate(g.nodes())
    ]
    frames.append(
        go.Frame(
            data=[
                glow_trace,
                go.Scatter3d(
                    x=node_x,
                    y=node_y,
                    z=node_z,
                    mode="markers",
                    marker=dict(
                        size=anim_sizes,
                        color=anim_colors,
                        line=dict(width=2, color="white"),
                        opacity=0.98,
                    ),
                ),
            ]
        )
    )

layout = go.Layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,1)",
    plot_bgcolor="rgba(0,0,0,1)",
    showlegend=False,
    margin=dict(l=0, r=0, b=0, t=0),
    scene=dict(
        xaxis=dict(showbackground=False, showticklabels=False, visible=False),
        yaxis=dict(showbackground=False, showticklabels=False, visible=False),
        zaxis=dict(showbackground=False, showticklabels=False, visible=False),
    ),
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            buttons=[dict(label="Play", method="animate", args=[None])],
        )
    ],
)

fig = go.Figure(
    data=edge_traces + [glow_trace, node_trace], layout=layout, frames=frames
)
fig.show()
