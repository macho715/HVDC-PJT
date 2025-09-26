import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_io

# Dash 앱 초기화
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "HVDC Logistics Dashboard"

# 데이터 로드
df = load_io()

# ── 그래프 생성 함수 ──────────────────────────
def sankey_fig(df):
    """Sankey 다이어그램 생성"""
    flow = (df.groupby(["stage_from", "stage_to"])
              .agg(value=("teu", "sum")).reset_index())
    
    nodes = list(pd.unique(flow[["stage_from", "stage_to"]].values.ravel()))
    node_map = {n: i for i, n in enumerate(nodes)}
    
    # 색상 설정
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    node_colors = [colors[i % len(colors)] for i in range(len(nodes))]
    
    fig = go.Figure(go.Sankey(
        node=dict(
            label=nodes,
            pad=15,
            thickness=20,
            color=node_colors
        ),
        link=dict(
            source=flow["stage_from"].map(node_map),
            target=flow["stage_to"].map(node_map),
            value=flow["value"],
            color='rgba(0,0,0,0.2)'
        )
    ))
    
    fig.update_layout(
        title="Logistics Flow (TEU)",
        font_size=12,
        height=400
    )
    
    return fig

def stock_area(df):
    """재고 수준 영역 차트 생성"""
    stock = (df.groupby(["date", "warehouse"])
               .net.sum().groupby(level=1).cumsum()
               .reset_index())
    
    fig = px.area(stock, x="date", y="net", color="warehouse",
                  title="Warehouse Stock Level (TEU)",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    
    # 경고선 추가 (최대값의 90%)
    if not stock.empty and stock.net.max() > 0:
        fig.add_hline(y=0.9 * stock.net.max(), 
                     line_dash="dash", 
                     line_color="red",
                     annotation_text="Warning Level (90%)")
    
    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Cumulative Stock (TEU)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_kpi_cards(df):
    """KPI 카드 생성"""
    total_teu = df['teu'].sum()
    avg_daily_teu = df.groupby('date')['teu'].sum().mean()
    num_warehouses = df['warehouse'].nunique()
    
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_teu:,.0f}", className="card-title"),
                    html.P("Total TEU", className="card-text")
                ])
            ], color="primary", outline=True)
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_daily_teu:,.0f}", className="card-title"),
                    html.P("Avg Daily TEU", className="card-text")
                ])
            ], color="success", outline=True)
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{num_warehouses}", className="card-title"),
                    html.P("Active Warehouses", className="card-text")
                ])
            ], color="info", outline=True)
        ], md=4)
    ], className="mb-4")
    
    return cards

# ── 레이아웃 ──────────────────────────────────
app.layout = dbc.Container([
    # 헤더
    dbc.Row([
        dbc.Col([
            html.H1("🚢 HVDC Logistics Dashboard", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    # KPI 카드
    create_kpi_cards(df),
    
    # 날짜 선택기
    dbc.Row([
        dbc.Col([
            html.Label("Select Date Range:", className="fw-bold"),
            dcc.DatePickerRange(
                id="date-range",
                min_date_allowed=df.date.min(),
                max_date_allowed=df.date.max(),
                start_date=df.date.min(),
                end_date=df.date.max(),
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            )
        ], md=6),
        dbc.Col([
            html.Label("Select Warehouse:", className="fw-bold"),
            dcc.Dropdown(
                id="warehouse-dropdown",
                options=[{'label': 'All Warehouses', 'value': 'all'}] + 
                        [{'label': w, 'value': w} for w in df['warehouse'].unique()],
                value='all',
                clearable=False
            )
        ], md=6)
    ], className="mb-4"),
    
    # 메인 그래프
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="flow-graph", figure=sankey_fig(df))
        ], md=6),
        dbc.Col([
            dcc.Graph(id="stock-graph", figure=stock_area(df))
        ], md=6)
    ]),
    
    # 추가 정보
    dbc.Row([
        dbc.Col([
            html.Div(id="summary-stats", className="mt-4")
        ])
    ])
], fluid=True)

# ── 콜백 (날짜 필터) ─────────────────────────────
@app.callback(
    [Output("flow-graph", "figure"),
     Output("stock-graph", "figure"),
     Output("summary-stats", "children")],
    [Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("warehouse-dropdown", "value")]
)
def update_graphs(start, end, warehouse):
    """그래프 업데이트 콜백"""
    # 날짜 필터링
    dff = df[(df.date >= start) & (df.date <= end)]
    
    # 창고 필터링
    if warehouse != 'all':
        dff = dff[dff.warehouse == warehouse]
    
    # 요약 통계
    if not dff.empty:
        summary = dbc.Alert([
            html.H5("📊 Summary Statistics"),
            html.P(f"Selected Period: {start} to {end}"),
            html.P(f"Total TEU: {dff['teu'].sum():,.0f}"),
            html.P(f"Average Daily TEU: {dff.groupby('date')['teu'].sum().mean():,.0f}"),
            html.P(f"Peak Day TEU: {dff.groupby('date')['teu'].sum().max():,.0f}")
        ], color="light")
    else:
        summary = dbc.Alert("No data available for selected filters", color="warning")
    
    return sankey_fig(dff), stock_area(dff), summary

if __name__ == "__main__":
    print("Starting HVDC Logistics Dashboard...")
    print("Dashboard will be available at: http://localhost:8050")
    app.run_server(host="0.0.0.0", port=8050, debug=True)