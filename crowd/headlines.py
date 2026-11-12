"""One plain sentence per screen, computed from the data, so a non-analyst gets the answer first."""

import pandas as pd

from crowd import config, fmt, metrics

BASELINE = "Normal day 2025"


def crowd(summary: pd.DataFrame, parade: str) -> str:
    # Lead with the location where crowd load grows most against a normal day.
    def load(loc: str) -> float:
        return metrics.ratio(summary, "visitor_hours", loc, parade, BASELINE)

    loc = max(config.LOCATION_NAMES.values(), key=load)
    # Contrast headcount with crowd load: that gap is the story the safety lead needs.
    rows = summary.set_index(["label", "location"])
    heads = metrics.ratio(summary, "visitors", loc, parade, BASELINE)
    return (
        f"At {loc}, the number of people {fmt.moves(heads)} on parade day, "
        f"{_crowd_load_clause(heads, load(loc))}: visitors stay "
        f"{fmt.minutes(rows.loc[(parade, loc), 'avg_stay_minutes'])} on average, against "
        f"{fmt.minutes(rows.loc[(BASELINE, loc), 'avg_stay_minutes'])} on a normal day."
    )


def _crowd_load_clause(heads: float, load: float) -> str:
    # "but" only when headcount and crowd load move in opposite directions (Parade 2025);
    # when both rise (Parade 2024), say that crowd load rises more.
    if heads <= 1 < load:
        return f"but crowd load {fmt.moves(load)}"
    if load > heads:
        return f"and crowd load rises even more, by {fmt.change(load).lstrip('+')}"
    return f"while crowd load {fmt.moves(load)}"


def _where(location: str) -> str:
    # The location filter's value: "all" or one location name. The sentence must say which one it describes.
    return "Across both locations" if location == "all" else f"At {location}"


def stay(long_share: pd.Series, parade: str, location: str) -> str:
    return (
        f"{_where(location)}, {fmt.pct(long_share[parade])} of visitors stay 2 hours or more on parade day, "
        f"against {fmt.pct(long_share[BASELINE])} on a normal day."
    )


def visitors(mix: pd.DataFrame, location: str) -> str:
    intl = mix[mix["visitor_type"] == "International"].set_index("label")["visitors"]
    uplift = intl["Parade 2025"] / intl[BASELINE]
    year_change = intl["Parade 2025"] / intl["Parade 2024"]
    return (
        f"{_where(location)}, the parade draws {fmt.times(uplift)} the international visitors of a normal day, "
        f"but their number {fmt.moves(year_change)} from 2024 to 2025 "
        f"(the 2024 parade fell on a Sunday, 2025 on a Monday)."
    )


def plan(plan_rows: pd.DataFrame) -> str:
    total = int(plan_rows["stewards"].sum())
    split = ", ".join(f"{r.stewards} at {r.location}" for r in plan_rows.itertuples())
    return f"Plan {total} stewards: {split}."
