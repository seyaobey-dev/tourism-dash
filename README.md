# St Patrick's Day crowd insights

A Plotly Dash app for Dublin City Council. It compares two St Patrick's Day parades with a normal day at College Green and O'Connell Bridge. The aim is to help the council plan crowd management for the next parade.

## A note on AI

I paired with an AI coding assistant to write the code, because Python and Dash are not my usual stack. That let me put my time into framing the problem, the architecture and the product decisions.

I steered every step. I decided what each screen answers, what to show and what to leave out, and how the code is layered. I rejected options that looked fine but didn't hold up. I checked every figure on screen against the raw data.

## Run it

You need Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python app.py
```

Open http://localhost:8060. To run the tests:

```bash
uv run pytest
```

## How the code is organised

```
app.py          the app shell: navigation and page container
pages/          one file per screen: its layout and its callbacks
crowd/
  config.py     what the dataset contains: dates, locations, stay-band minutes
  data.py       loads and cleans the CSV once, then caches it
  metrics.py    every calculation: pure pandas, no Dash
  headlines.py  turns figures into the one-line insights
  charts.py     Plotly figures
  components.py shared layout pieces
  theme.py      one Plotly template: palette, font, colours per category
assets/         CSS
tests/          pytest for metrics and headlines
```

## Architecture

```
pages  ──▶  headlines, charts, components
              │
              ▼
           metrics  ──▶  data  ──▶  config
```

Each layer only calls the layers below it. A page lays out the screen and wires its callback, and nothing else. Every number has one home in `metrics.py`, and charts and sentences only present what it returns.

The browser holds no data. When a control changes, Dash sends the new value to the server. The page's callback runs in Python and sends back the new sentence and the figure as JSON, which Plotly.js draws.

## Key decisions

**Data handling**
- The CSV is loaded and cleaned once per process and kept in memory (`lru_cache`). It's 13 MB, so every interaction stays fast.
- `config.py` describes the dataset: its dates, its locations and the minutes in each stay band. A date or location it doesn't know stops the app at start-up instead of being dropped silently. Missing visitors would distort every figure without anyone noticing.
- The main measure is **crowd load**: visitors × hours on site. Parade-day head counts are almost flat, but people stay longer. Crowding is about how many people are there at once, so head counts alone would mislead.

**Callbacks**
- Each screen has one main callback. It takes the screen's controls as inputs and returns the sentence and the chart together, so the two can never disagree.
- Callbacks stay thin: filter the data, call `metrics`, pass the result to `headlines` and `charts`. The logic can be tested without a browser.
- The planner updates as the user types. Empty inputs raise `PreventUpdate`, so the screen keeps its last plan instead of flashing an error.

**Structure**
- There's one page per question, using Dash Pages. Each answer has its own URL to share, and each screen is one file a developer can find.
- The calculations are pure functions with unit tests. The council's numbers are the thing that must not be wrong.

**Design**
- Each screen opens with one plain sentence that answers its question. The chart below shows the figures behind it.
- One chart per screen. Gender and age are left out: 87% of gender and 49% of age values are missing, so a chart would look precise and be wrong.
- The client's palette and font are applied in one place (`theme.py` plus CSS variables). A new brand means changing one file.

## The four screens

| Screen | Question it answers | Decision it supports |
| --- | --- | --- |
| Parade vs normal day | Where does crowd pressure grow on parade day? | Which location gets priority |
| How long people stay | Do parade visitors pass through, or settle in? | Toilets, water and barriers for long stays |
| Who comes | Who does the parade attract, and where from? | Signage and multilingual stewards |
| Plan the next parade | How many stewards will the next parade need, and at which location? | The staffing plan |

## What the data says

- Head counts are almost the same on parade day and on a normal day: 777,589 against 775,103. People stay much longer on parade day, though, so crowd load is 25% higher.
- O'Connell Bridge counts 8% fewer people on parade day, but its crowd load rises 30%. A plan based on head counts would under-staff it.
- 41% of parade visitors stay 2 hours or more, against 27% on a normal day. Past two hours, people need toilets, water and food.
- The parade draws 1.7 times the international visitors of a normal day. Their number fell 59% between 2024 and 2025, but the 2024 parade fell on a Sunday and the 2025 parade on a Monday.

## Issues found in the data

- **Only one normal day.** The file has three dates: 17 March 2024, 17 March 2025 and 10 March 2025. The data dictionary says it covers "normal days across multiple years". So every comparison is against the one normal day, Monday 10 March 2025. There's no normal Sunday to compare with the 2024 parade.
- **No time of day.** Stays are known only as bands (for example 2-4 hours). That shows how long people stay, but not when the peak happens. The planner therefore covers the whole day.
- **Bands, not minutes.** To turn a band into hours, the app uses the middle of the band. Using the lower or upper edge instead moves the crowd-load figures by a few points, but the conclusions stay the same.
- **Missing values.** 1.9% of rows have no stay band (written as `null`). They count towards head counts but are left out of stay figures, which is 0.3% of visitors.
- **Spelling.** The file spells the location "O'Connel Bridge". The app maps it to the correct name.

## On Dash Enterprise

- **Sign-in:** council staff log in with their existing accounts (SSO). The app can read who is viewing, for example to limit the planner to operations staff.
- **Deployment:** `app.py` exposes `server` for gunicorn, so the app deploys with `de deploy` as it is, with no code change.
- **Data:** a managed Postgres database replaces the CSV. Only `data.py` changes.
- **Heavier work:** background callbacks (Celery and Redis) for long queries over a full season of data. Scheduled snapshots could send a PDF briefing to the events team before each parade.
- **Embedding:** a screen can be embedded in a council portal.

## Scaling to a larger product

- **New events and locations are configuration.** Adding a festival or a third location is a line in `config.py`, and every screen picks it up.
- **The numbers can serve other front ends.** `metrics.py` has no Dash code, so it can sit behind an API. A React app or a report would then show exactly the same figures.
- **Charts are already data.** They are Plotly figure JSON, which `react-plotly.js` draws unchanged.
- **The UI pieces are named.** The filter bar, insight card and location block map onto the first components of a design system.
- **Multi-client.** The theme lives in one module, and the dataset is described in config, so the same product could serve another city with its own brand and data.

## Next steps

1. **Hourly counts.** This is the most useful next dataset. It would show when the crowd peaks, so stewards could be planned by hour.
2. **Check the planner against real staffing.** Compare its numbers with the stewards the council actually deployed, then adjust.
3. **More locations and more normal days**, including a normal Sunday.
4. **Test it with council staff** to find out which questions they actually ask.
