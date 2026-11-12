"""Small layout pieces every page reuses, so screens stay consistent."""

from dash import dcc, html

from crowd import config


def page_header(title: str, question: str) -> html.Header:
    return html.Header([html.H1(title), html.P(question, className="question")], className="page-header")


def filter_bar(*controls) -> html.Section:
    # The controls that drive the page sit in one visible bar, above everything they change.
    return html.Section(list(controls), className="filter-bar", **{"aria-label": "Filters"})


def segmented(id_: str, label: str, options: list, value: str) -> html.Div:
    return html.Div(
        # The id is what a page callback listens to: Input(id_, "value").
        [*([html.Span(label, className="control-label")] if label else []),
         dcc.RadioItems(options, value, id=id_, inline=True, className="segmented")],
        className="control",
    )


def location_filter(id_: str) -> html.Div:
    options = [{"label": "Both locations", "value": "all"}] + [
        {"label": name, "value": name} for name in config.LOCATION_NAMES.values()
    ]
    return segmented(id_, "Location", options, "all")


def insight(id_: str) -> html.Section:
    # Filled by a callback with one plain sentence: the answer before the chart.
    return html.Section(
        [html.Span("Key insight", className="insight-kicker"), html.P(id=id_, className="insight-text")],
        className="insight", **{"aria-live": "polite"},
    )


def swatch(color: str) -> html.Span:
    return html.Span(className="swatch", style={"background": color})


def legend(items: list[tuple[str, str]]) -> html.Span:
    return html.Span([html.Span([swatch(color), name]) for name, color in items], className="legend")


def measure(label: str, change: str, bars: list[tuple[str, str, float, str]]) -> html.Div:
    # One measure with one column per day. Each bar is (day, value text, height as a share of the scale, colour).
    # The 22px kept free above the tallest bar is room for its value label.
    columns = [
        html.Div([html.Span(value, className="bar-value"),
                  html.Div(className="bar", style={"height": f"calc((100% - 22px) * {height:.3f})", "background": color})],
                 className="bar-col", title=f"{day}: {value}")
        for day, value, height, color in bars
    ]
    return html.Div([html.Div([html.Span(label), html.Strong(change)], className="measure-head"),
                     html.Div(columns, className="bars")], className="measure")


def location_block(title: str, key: html.Span, measures: list, footer: str) -> html.Div:
    # A card that is also a small chart: the change in words, and the bars that show it.
    return html.Div(
        [html.Div([html.Span(title, className="block-title"), key], className="block-head"),
         html.Div(measures, className="measures"), html.Span(footer, className="stat-detail")],
        className="stat location-block",
    )


def note(text: str) -> html.P:
    return html.P(text, className="note")


def graph(id_: str) -> dcc.Graph:
    return dcc.Graph(id=id_, config={"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"]})
