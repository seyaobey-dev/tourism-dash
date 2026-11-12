"""Screen 2 - how long people stay, and how parade day changes it."""

import dash
from dash import Input, Output, callback, html

from crowd import charts, components as ui, config, data, headlines, metrics

dash.register_page(__name__, path="/stay", name="How long people stay", order=1)

# "Long stay" = 2 hours or more: past that, people need toilets, water and food.
LONG_STAY_MINUTES, LONG_STAY_LABEL = 120, "2 hours"
# The first band whose minutes reach the threshold (120-240 min): the chart is shaded from there.
FIRST_LONG_BAND = next(band for band, minutes in config.DWELL_MINUTES.items() if minutes >= LONG_STAY_MINUTES)


def layout():
    return html.Div([
        ui.page_header("How long people stay", "Do parade visitors pass through, or settle in?"),
        ui.filter_bar(ui.location_filter("stay-location")),
        ui.insight("stay-headline"),
        ui.graph("stay-chart"),
        ui.note("Stays are reported in bands, not exact minutes. The shaded zone adds up the bands of 2 hours "
                "or more for each day. 1.9% of records have no stay band: they are left out of these shares."),
    ])


# Runs on page load and when the location changes: the sentence and the chart for the chosen location.
@callback(Output("stay-headline", "children"), Output("stay-chart", "figure"), Input("stay-location", "value"))
def update(location: str):
    df = data.load_visits()
    if location != "all":
        df = df[df["location"] == location]
    long_share = metrics.share_staying_at_least(df, LONG_STAY_MINUTES)
    figure = charts.stay_distribution(metrics.dwell_distribution(df), config.DAY_ORDER, FIRST_LONG_BAND,
                                      LONG_STAY_LABEL, long_share)
    return headlines.stay(long_share, "Parade 2025", location), figure
