"""One Plotly template for every chart. A new client brand = a new palette and font here."""

import plotly.graph_objects as go
import plotly.io as pio

# Accent palette taken from the CKDelta instructions template.
PURPLE, BLUE, GREEN, ORANGE, PINK = "#C77DF0", "#54ABE0", "#A3D140", "#F09145", "#ED739E"
INK, MUTED, GRID, NEUTRAL = "#111111", "#5F6368", "#E6E6E6", "#B8B8B8"
LIGHT, TINT, ACCENT_INK = "#EEEEEE", "#F5F2FF", "#7A2FB0"
FONT = "'Mozilla Text', system-ui, sans-serif"

# Fixed colours per category, so a day or visitor type keeps its colour on every screen.
DAY_COLORS = {"Normal day 2025": NEUTRAL, "Parade 2025": PURPLE, "Parade 2024": BLUE}
VISITOR_TYPE_COLORS = {"Local": BLUE, "Domestic": GREEN, "International": ORANGE}

TEMPLATE = go.layout.Template(
    layout=dict(
        font=dict(family=FONT, size=14, color=INK),
        title=dict(font=dict(size=16), x=0, xanchor="left"),
        colorway=[PURPLE, BLUE, GREEN, ORANGE, PINK],
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(gridcolor=GRID, zeroline=False, linecolor=GRID, ticks=""),
        yaxis=dict(gridcolor=GRID, zeroline=False, linecolor=GRID, ticks=""),
        legend=dict(orientation="h", y=-0.12, yanchor="top", x=0, title_text=""),
        margin=dict(l=8, r=8, t=56, b=40),
        hoverlabel=dict(bgcolor="white", font=dict(family=FONT)),
    )
)


def register() -> None:
    pio.templates["ckdelta"] = TEMPLATE
    pio.templates.default = "plotly_white+ckdelta"
