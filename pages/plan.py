"""Screen 4 - turn the data into a staffing decision for the next parade."""

import dash
from dash import Input, Output, callback, dcc, html

from crowd import charts, components as ui, data, headlines, metrics

dash.register_page(__name__, path="/plan", name="Plan the next parade", order=3)


def field(label: str, control) -> html.Label:
    return html.Label([html.Span(label, className="control-label"), control], className="field")


def visitors_on(base: str) -> float:
    return metrics.day_summary(data.load_visits()).query("label == @base")["visitors"].sum()


def layout():
    # The settings come in two parts: what happened on a past parade, then what is expected next time.
    based_on = html.Div([
        html.Span("Based on", className="panel-title"),
        html.Div([
            field("Parade", html.Div([ui.segmented("plan-base", "", ["Parade 2025", "Parade 2024"], "Parade 2025"),
                                      html.Span(id="plan-base-visitors", className="panel-fact")], className="inline")),
            field("Stewards on duty that day",
                  dcc.Input(id="plan-stewards", type="number", min=1, step=1, value=100)),
        ], className="panel-row"),
    ], className="panel panel-past")
    next_parade = html.Div([
        html.Span("Next parade", className="panel-title"),
        # Pre-filled with Parade 2025's attendance, rounded to the nearest thousand.
        field("Visitors expected", dcc.Input(id="plan-expected", type="number", min=0, step=1000,
                                             value=int(round(visitors_on("Parade 2025"), -3)))),
    ], className="panel panel-next")
    return html.Div([
        ui.page_header("Plan the next parade", "How many stewards will the next parade need, and at which location?"),
        ui.filter_bar(html.Div([based_on, html.Span("→", className="plan-arrow"), next_parade],
                               className="plan-form")),
        ui.insight("plan-headline"),
        ui.graph("plan-chart"),
        ui.note("How it works: stewards grow in line with expected visitors, and are split by each location's share "
                "of crowd load (visitor-hours) on the chosen parade. It assumes visitors spread and stay as they did "
                "that day. The council's own staffing sets the scale; the data only sets the ratios."),
        ui.note("When: the data has no time of day, so this plan covers the whole parade day. "
                "Peak hours need hourly data."),
    ])


# The visitors who came to the chosen parade: what "visitors expected" is compared with.
@callback(Output("plan-base-visitors", "children"), Input("plan-base", "value"))
def show_base_visitors(base: str) -> str:
    return f"{visitors_on(base):,.0f} visitors"


# Runs whenever any of the three inputs changes, so the plan updates as the user types.
@callback(
    Output("plan-headline", "children"),
    Output("plan-chart", "figure"),
    Input("plan-base", "value"),
    Input("plan-stewards", "value"),
    Input("plan-expected", "value"),
)
def update(base: str, stewards: int | None, expected: float | None):
    if not stewards or not expected:
        # Inputs are empty while the user is typing: keep the screen as it is.
        raise dash.exceptions.PreventUpdate
    # One row per location: expected visitors, share of crowd load, stewards.
    rows = metrics.plan(data.load_visits(), base, expected, int(stewards))
    return headlines.plan(rows), charts.steward_split(rows)
