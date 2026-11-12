"""Screen 1 - parade day against a normal day: where does crowd pressure grow?"""

import dash
from dash import Input, Output, callback, html

from crowd import components as ui, config, data, fmt, headlines, metrics, theme

# Registers this file as a page: its URL, its name in the nav, and its position there.
dash.register_page(__name__, path="/", name="Parade vs normal day", order=0)

PARADES = ["Parade 2025", "Parade 2024"]
MEASURES = [("visitor_hours", "Crowd load (visitor-hours)"), ("visitors", "People counted")]


# What the screen shows. Elements with an id are empty here and filled by the callback below.
def layout():
    return html.Div([
        ui.page_header("Parade vs normal day", "Where does crowd pressure grow on parade day?"),
        ui.filter_bar(ui.segmented("crowd-parade", "Compare the normal day with", PARADES, "Parade 2025")),
        ui.insight("crowd-headline"),
        html.Div(id="crowd-blocks", className="location-blocks"),
        ui.note("Crowd load = visitor-hours = people × time they stayed, using the middle of each stay band. "
                "It shows how many people are in the area at once, which headcount alone hides. "
                "Bars share one scale per measure, so the two locations can be compared. "
                "Parade 2024 is compared with a 2025 normal day: no 2024 normal day exists in the data."),
    ])


# Runs on page load and every time the radio button changes; its return fills the two Outputs, in order.
@callback(Output("crowd-headline", "children"), Output("crowd-blocks", "children"), Input("crowd-parade", "value"))
def update(parade: str):
    # 1. All numbers for this screen: 6 rows, one per day and location (the data itself is cached).
    summary = metrics.day_summary(data.load_visits())
    days = [headlines.BASELINE, parade]
    rows = summary[summary["label"].isin(days)].set_index(["label", "location"])
    # 2. The longest bar of each measure, across both locations, sets that measure's scale.
    longest = rows[[field for field, _ in MEASURES]].max()
    key = ui.legend([(day, theme.DAY_COLORS[day]) for day in days])

    def block(loc: str):
        measures = [
            ui.measure(label, fmt.change(metrics.ratio(summary, field, loc, parade, headlines.BASELINE)),
                       [(day, fmt.people(rows.loc[(day, loc), field]), rows.loc[(day, loc), field] / longest[field],
                         theme.DAY_COLORS[day]) for day in days])
            for field, label in MEASURES
        ]
        stays = " → ".join(fmt.minutes(rows.loc[(day, loc), "avg_stay_minutes"]) for day in days)
        return ui.location_block(loc, key, measures, f"Average stay {stays}")

    # 3. Back to the browser: the sentence, then one block per location.
    return headlines.crowd(summary, parade), [block(loc) for loc in config.LOCATION_NAMES.values()]
