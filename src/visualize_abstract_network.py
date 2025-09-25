import networkx as nx
import plotly.graph_objs as go
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# 1. 네트워크 생성 및 좌표
graph_size = 30
G = nx.random_geometric_graph(graph_size, 0.4, dim=3)
pos = nx.spring_layout(G, dim=3, seed=42)

# 2. 노드별 그룹/카테고리 지정 (예시)
for i, n in enumerate(G.nodes()):
    G.nodes[n]["group"] = i % 5  # 5개 그룹

groups = [G.nodes[n]["group"] for n in G.nodes()]
norm = mcolors.Normalize(vmin=min(groups), vmax=max(groups))
cmap = cm.get_cmap("plasma")
node_colors = [
    f"rgba{tuple(int(255*x) for x in cmap(norm(g))[:3]) + (0.9,)}" for g in groups
]


# 3. 곡선(베지어) 엣지 + 엣지별 색상/두께
def bezier(p0, p1, p2, t):
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t**2 * p2


edge_traces = []
for edge in G.edges(data=True):
    x0, y0, z0 = pos[edge[0]]
    x1, y1, z1 = pos[edge[1]]
    mx, my, mz = (
        (x0 + x1) / 2 + np.random.uniform(-0.1, 0.1),
        (y0 + y1) / 2 + np.random.uniform(-0.1, 0.1),
        (z0 + z1) / 2 + np.random.uniform(-0.1, 0.1),
    )
    t = np.linspace(0, 1, 20)
    bx = bezier(x0, mx, x1, t)
    by = bezier(y0, my, y1, t)
    bz = bezier(z0, mz, z1, t)
    # 엣지별 두께/색상 (랜덤 가중치)
    weight = np.random.uniform(0.5, 2.5)
    color = f"rgba({int(255*weight/2.5)},100,255,{0.3+0.5*weight/2.5:.2f})"
    edge_traces.append(
        go.Scatter3d(
            x=bx,
            y=by,
            z=bz,
            mode="lines",
            line=dict(width=2 + weight * 2, color=color),
            hoverinfo="none",
        )
    )

# 4. Glow 효과 (노드 뒤에 투명 marker)
node_x, node_y, node_z = zip(*pos.values())
glow_trace = go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode="markers",
    marker=dict(size=28, color="rgba(255,255,255,0.08)", opacity=0.2, symbol="circle"),
    showlegend=False,
)

# 5. 노드 trace (노드별 색상)
node_trace = go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode="markers",
    marker=dict(
        size=14,
        color=node_colors,
        line=dict(width=2, color="white"),
        opacity=0.95,
        symbol="circle",
    ),
    text=[f"Node {n} (Group {g})" for n, g in zip(G.nodes(), groups)],
    hoverinfo="text",
)

# 6. 애니메이션 프레임 (노드 위치 변화 예시)
frames = []
for t in range(20):
    new_x = [x + np.sin(t / 3 + i) * 0.04 for i, x in enumerate(node_x)]
    frames.append(
        go.Frame(
            data=[
                glow_trace,
                go.Scatter3d(
                    x=new_x,
                    y=node_y,
                    z=node_z,
                    mode="markers",
                    marker=dict(
                        size=14,
                        color=node_colors,
                        line=dict(width=2, color="white"),
                        opacity=0.95,
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
