"""St Patrick's Day crowd insights - app shell: navigation, theme, page container."""

import dash
from dash import Dash, Input, Output, callback, dcc, html

from crowd import data, theme

# Before the app is built: make the brand theme the default for every chart, and load the data.
theme.register()
data.load_visits()  # Fail at start-up, not on the first click, if the data file is wrong.

app = Dash(
    __name__,
    use_pages=True,  # Imports every file in pages/; each registers its own URL.
    title="St Patrick's Day crowd insights",
    external_stylesheets=["https://fonts.googleapis.com/css2?family=Mozilla+Text:wght@400;700&display=swap"],
)
server = app.server  # The WSGI entry point a production server (gunicorn, Dash Enterprise) runs.


# The pages registered above, in nav order. The nav is built from this list, so a new page appears by itself.
PAGES = list(dash.page_registry.values())


def nav() -> html.Nav:
    links = [dcc.Link(p["name"], href=p["relative_path"], id=f"nav-{i}", className="nav-link")
             for i, p in enumerate(PAGES)]
    return html.Nav(
        [html.Div([html.Span("St Patrick's Day", className="brand-kicker"),
                   html.Span("Crowd insights", className="brand-name")], className="brand"),
         html.Div(links, className="nav-links")],
        className="nav",
    )


# When the URL changes, mark the matching nav link as the current page.
@callback([Output(f"nav-{i}", "className") for i in range(len(PAGES))], Input("url", "pathname"))
def highlight_current_page(pathname: str):
    return ["nav-link active" if p["relative_path"] == pathname else "nav-link" for p in PAGES]


# The shell shared by all pages. dash.page_container is swapped for the current page's layout().
app.layout = html.Div([
    dcc.Location(id="url"),  # Exposes the browser URL to callbacks.
    nav(),
    html.Main(dash.page_container),
    html.Footer("Dublin City Council · College Green and O'Connell Bridge · "
                "Visitor estimates from telecoms data, fictional dataset for assessment."),
])

if __name__ == "__main__":
    app.run(debug=True, port=8060)
