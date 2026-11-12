"""Figure builders. They take tidy frames from `metrics` and never compute business numbers."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from crowd import config, fmt, theme


def stay_distribution(dist: pd.DataFrame, days: list[str], highlight_from: str, label: str,
                      long_share: pd.Series) -> go.Figure:
    """Share of visitors per stay band and day. The bands from `highlight_from` upwards are shaded, and the
    shaded zone's label gives each day's total for them (`long_share`): the insight sentence's numbers."""
    rows = dist[dist["label"].isin(days)]
    fig = px.bar(
        rows, x="dwell_time", y="share", color="label", barmode="group",
        color_discrete_map=theme.DAY_COLORS, category_orders={"label": config.DAY_ORDER},
        labels={"dwell_time": "Time spent in the area", "share": "Share of visitors", "label": ""},
        custom_data=["label"],
    )
    fig.update_yaxes(tickformat=".0%")
    fig.update_traces(hovertemplate="%{customdata[0]}<br>%{x}: %{y:.1%}<extra></extra>")
    # Bands sit at positions 0, 1, 2...: shade from the first highlighted band to the last one.
    bands = list(config.DWELL_MINUTES)
    totals = "".join(f"<br><span style='color:{theme.DAY_COLORS[day]}'>■</span> {day}: <b>{fmt.pct(long_share[day])}</b>"
                     for day in days if day in long_share.index)
    # Label in the top-right corner, above the short bars of the longest bands.
    fig.add_vrect(x0=bands.index(highlight_from) - 0.5, x1=len(bands) - 0.5, fillcolor=theme.TINT, line_width=0,
                  layer="below", annotation_text=f"<b>{label} or more, all shaded bands:</b>{totals}",
                  annotation_position="top right", annotation_align="left",
                  annotation_font=dict(color=theme.INK, size=13))
    # The x-axis title needs the space the template gives the legend: push the legend lower.
    return fig.update_layout(title="Detail per stay band", legend_y=-0.22, margin_b=70)


def visitor_mix(mix: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        mix, y="label", x="share", color="visitor_type", orientation="h",
        color_discrete_map=theme.VISITOR_TYPE_COLORS,
        category_orders={"label": config.DAY_ORDER, "visitor_type": config.VISITOR_TYPE_ORDER},
        labels={"label": "", "share": "", "visitor_type": ""}, custom_data=["visitors"],
        text=mix["share"].map(fmt.pct),
    )
    fig.update_xaxes(tickformat=".0%", range=[0, 1])
    fig.update_traces(textposition="inside", hovertemplate="%{y}<br>%{x:.1%} · %{customdata[0]:,.0f} people<extra></extra>")
    return fig.update_layout(title="Who visits: local, domestic, international")


def top_countries(countries: pd.DataFrame) -> go.Figure:
    # Biggest country at the top of the chart.
    order = countries.groupby("country_of_origin")["visitors"].sum().sort_values().index.tolist()
    fig = px.bar(
        countries, y="country_of_origin", x="visitors", color="label", barmode="group", orientation="h",
        color_discrete_map=theme.DAY_COLORS,
        category_orders={"label": config.DAY_ORDER, "country_of_origin": order[::-1]},
        labels={"country_of_origin": "", "visitors": "", "label": ""},
    )
    fig.update_xaxes(tickformat="~s")
    return fig.update_layout(title="Where international visitors come from", height=460)


def steward_split(plan: pd.DataFrame) -> go.Figure:
    """Stewards per location. The hover explains each number: its share of crowd load and expected visitors."""
    rows = plan.assign(load_text=plan["load_share"].map(fmt.pct), visitors_text=plan["visitors"].map(fmt.people))
    fig = px.bar(
        rows, x="stewards", y="location", orientation="h", text="stewards",
        labels={"stewards": "Stewards", "location": ""}, color_discrete_sequence=[theme.PURPLE],
        category_orders={"location": list(config.LOCATION_NAMES.values())},
        custom_data=["load_text", "visitors_text"],
    )
    fig.update_traces(textposition="outside", cliponaxis=False,
                      hovertemplate="%{y}: %{x} stewards<br>%{customdata[0]} of crowd load · "
                                    "~%{customdata[1]} visitors expected<extra></extra>")
    return fig.update_layout(title="Suggested stewards per location", height=260)
