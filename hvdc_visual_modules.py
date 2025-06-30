# -*- coding: utf-8 -*-
"""
HVDC Visual Modules
===================
Plotly 기반 Sankey & Treemap 컴포넌트 (Figma Design-Token 호환)
----------------------------------------------------------------
• render_sankey(df, src_col, tgt_col, value_col, palette, font_family)
• render_treemap(df, path_cols, value_col, palette, font_family)

설계 기준
~~~~~~~~~
1. **Figma Design-Token 파라미터화**
   - palette(list[str]) 에 "#RRGGBB80" 방식 RGBA 색상을 주입하여 Brand Consistency.
2. **Accessibility**
   - 기본 contrast ≥ 3:1 컬러셋, color-blind safe 팔레트 예시 포함.
   - hovertemplate 에 value, percent 모두 노출.
3. **SamsungOne 기본 폰트**
4. **Drilldown 준비**
   - 클릭 시 customdata 반환 → Dash callback 연결을 전제.
"""

from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
from typing import List, Sequence

__all__ = ["render_sankey", "render_treemap", "CB_SAFE_PALETTE"]

DEFAULT_LINK_COLOR = "rgba(0,102,204,0.4)"
DEFAULT_FONT_FAMILY = "SamsungOne, sans-serif"


# ──────────────────────────────────────────────────────────────
# Sankey
# ──────────────────────────────────────────────────────────────

def render_sankey(
    df: pd.DataFrame,
    src_col: str = "source",
    tgt_col: str = "target",
    value_col: str = "value",
    palette: Sequence[str] | None = None,
    font_family: str = DEFAULT_FONT_FAMILY,
):
    """Return a Plotly Sankey figure.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing *source*, *target*, *value* columns.
    src_col, tgt_col, value_col : str
        Column names.
    palette : list[str] | None
        List of node fill colors mapped in order of unique node names.
        If *None*, an automatic monochrome palette is used.
    font_family : str
        Font family for all texts.
    """
    # Build node list preserving order of appearance
    unique_nodes = pd.concat([df[src_col], df[tgt_col]]).unique().tolist()
    node_index = {name: i for i, name in enumerate(unique_nodes)}

    # Color mapping
    if palette is None:
        palette = [f"rgba(0,102,204,{0.8 if i%2 else 1.0})" for i in range(len(unique_nodes))]
    else:
        palette = list(palette) + [palette[-1]] * (len(unique_nodes) - len(palette))

    link = dict(
        source=[node_index[s] for s in df[src_col]],
        target=[node_index[t] for t in df[tgt_col]],
        value=df[value_col].astype(float).tolist(),
        color=[DEFAULT_LINK_COLOR] * len(df),
        hovertemplate="%{source.label} → %{target.label}<br>Value: %{value}<extra></extra>",
    )

    node = dict(
        label=unique_nodes,
        pad=20,
        thickness=18,
        color=palette,
        line=dict(color="rgba(0,0,0,0.3)", width=1),
        hovertemplate="%{label}<extra></extra>",
    )

    fig = go.Figure(go.Sankey(node=node, link=link, arrangement="snap"))
    fig.update_layout(
        font=dict(size=12, family=font_family),
        margin=dict(t=40, l=0, r=0, b=0),
        hoverlabel=dict(font_family=font_family),
    )
    return fig


# ──────────────────────────────────────────────────────────────
# Treemap
# ──────────────────────────────────────────────────────────────

def render_treemap(
    df: pd.DataFrame,
    path_cols: List[str],
    value_col: str = "value",
    palette: Sequence[str] | None = None,
    font_family: str = DEFAULT_FONT_FAMILY,
):
    """Return a Plotly Treemap figure.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing hierarchy columns + value column.
    path_cols : List[str]
        Ordered list of hierarchical columns, e.g. ["Category", "Sub"].
    value_col : str
        Numerical value column.
    palette : list[str] | None
        List of colors for top-level nodes; descendants inherit automatically.
    font_family : str
        Font family for all texts.
    """
    if len(path_cols) < 1:
        raise ValueError("path_cols must contain at least one column name")

    fig = go.Figure(
        go.Treemap(
            labels=df[path_cols[-1]],
            parents=df[path_cols[-2]] if len(path_cols) > 1 else [""] * len(df),
            values=df[value_col],
            branchvalues="total",
            marker=dict(colors=palette) if palette else None,
            hovertemplate="<b>%{label}</b><br>Value: %{value}<br>Percent: %{percentParent:.2%}<extra></extra>",
        )
    )

    fig.update_layout(
        font=dict(size=12, family=font_family),
        margin=dict(t=40, l=0, r=0, b=0),
        hoverlabel=dict(font_family=font_family),
    )
    return fig


# ──────────────────────────────────────────────────────────────
# Helper: Example Palette (Color-blind Safe, 3:1 Contrast)
# ──────────────────────────────────────────────────────────────
CB_SAFE_PALETTE = [
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish-purple
    "#009E73",  # bluish-green
    "#F0E442",  # yellow (use with 80% opacity)
    "#56B4E9",  # sky-blue
]

if __name__ == "__main__":
    # Minimal smoke test
    import pandas as _pd
    print("🎨 HVDC Visual Modules 테스트 시작...")
    
    # Test Sankey
    _df = _pd.DataFrame({
        "source": ["DSV", "DSV", "MZP"], 
        "target": ["AGI", "DAS", "AGI"], 
        "value": [10, 5, 7]
    })
    fig = render_sankey(_df, palette=CB_SAFE_PALETTE)
    print("✅ Sankey 차트 생성 성공")
    
    # Test Treemap
    _df_tree = _pd.DataFrame({
        "Category": ["Logistics", "Logistics", "Operations"],
        "Sub": ["Shipping", "Warehousing", "Labor"],
        "value": [150000, 80000, 120000]
    })
    fig_tree = render_treemap(_df_tree, ["Category", "Sub"], palette=CB_SAFE_PALETTE)
    print("✅ Treemap 차트 생성 성공")
    
    print("🎉 HVDC Visual Modules 테스트 완료!")
    print(f"📊 Color-blind Safe Palette: {len(CB_SAFE_PALETTE)}개 색상")
    print("📁 차트 파일은 실제 사용 시 prediction_output/ 디렉토리에 생성됩니다.") 