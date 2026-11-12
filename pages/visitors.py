"""Screen 3 - who the parade attracts and where they come from."""

import dash
from dash import Input, Output, callback, html

from crowd import charts, components as ui, data, headlines, metrics

dash.register_page(__name__, path="/visitors", name="Who comes", order=2)


def layout():
    return html.Div([
        ui.page_header("Who comes", "Who does the parade attract, and where from?"),
        ui.filter_bar(ui.location_filter("visitors-location")),
        ui.insight("visitors-headline"),
        html.Div([ui.graph("visitors-mix"), ui.graph("visitors-countries")], className="grid-2"),
        ui.note("Local = Dublin area, Domestic = rest of Ireland, International = abroad. "
                "Gender and age are not shown: 87% of records have no gender and 49% no age band."),
    ])


# Runs on page load and when the location changes: sentence, visitor-type mix, top countries.
@callback(
    Output("visitors-headline", "children"),
    Output("visitors-mix", "figure"),
    Output("visitors-countries", "figure"),
    Input("visitors-location", "value"),
)
def update(location: str):
    df = data.load_visits()
    if location != "all":
        df = df[df["location"] == location]
    mix = metrics.visitor_mix(df)
    return headlines.visitors(mix, location), charts.visitor_mix(mix), charts.top_countries(metrics.top_countries(df))
