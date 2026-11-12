"""The numbers the app shows. Pure functions on the cleaned frame: no Dash, easy to test."""

import math

import pandas as pd


def _share(frame: pd.DataFrame, by: list[str], within: list[str]) -> pd.Series:
    # Visitors per `by` group, as a share of their `within` total (e.g. each stay band's share of its day).
    totals = frame.groupby(by, observed=True)["visitors"].sum()
    return totals / totals.groupby(level=within, observed=True).transform("sum")


def day_summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per day and location: headcount, visitor-hours, average stay."""
    # Headcount uses every row; stay averages use only rows with a known stay band.
    known = df[df["dwell_minutes"].notna()]
    keys = ["label", "location"]
    out = df.groupby(keys, observed=True).agg(visitors=("visitors", "sum"), visitor_hours=("visitor_hours", "sum"))
    known_visitors = known.groupby(keys, observed=True)["visitors"].sum()
    # Average stay = visitor-hours back to minutes, per visitor.
    out["avg_stay_minutes"] = known.groupby(keys, observed=True)["visitor_hours"].sum() * 60 / known_visitors
    return out.reset_index()


def ratio(summary: pd.DataFrame, measure: str, location: str, day: str, baseline: str) -> float:
    """How many times bigger `measure` is on `day` than on `baseline`, at one location."""
    rows = summary.set_index(["label", "location"])[measure]
    return rows[(day, location)] / rows[(baseline, location)]


def dwell_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Share of visitors in each stay band, per day. Unknown stays are left out of the shares."""
    known = df[df["dwell_minutes"].notna()]
    return _share(known, ["label", "dwell_time"], ["label"]).rename("share").reset_index()


def share_staying_at_least(df: pd.DataFrame, minutes: int) -> pd.Series:
    """Per day, the share of visitors (with a known stay) whose band is `minutes` or longer."""
    known = df[df["dwell_minutes"].notna()]
    long = known[known["dwell_minutes"] >= minutes].groupby("label", observed=True)["visitors"].sum()
    return long / known.groupby("label", observed=True)["visitors"].sum()


def visitor_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Visitors and share by visitor type (Local / Domestic / International), per day."""
    counts = df.groupby(["label", "visitor_type"], observed=True)["visitors"].sum().rename("visitors")
    share = _share(df, ["label", "visitor_type"], ["label"]).rename("share")
    return pd.concat([counts, share], axis=1).reset_index()


def top_countries(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    """International visitors per country and day, for the n biggest countries across all days."""
    intl = df[df["visitor_type"] == "International"]
    by_day = intl.groupby(["label", "country_of_origin"], observed=True)["visitors"].sum().rename("visitors")
    top = by_day.groupby(level="country_of_origin").sum().nlargest(n).index
    return by_day.reset_index().query("country_of_origin in @top")


def plan(df: pd.DataFrame, base_day: str, expected_visitors: float, base_stewards: int) -> pd.DataFrame:
    """Scale the stewards used on a past parade to next year's expected attendance.

    The data supplies ratios only; the absolute number comes from the council's own staffing.
    Assumes next year's visitors split across locations and stay as long as on `base_day`,
    so crowd load grows in line with attendance and is shared by each location's visitor-hours.
    """
    base = day_summary(df).query("label == @base_day")
    # How many stewards in total: last time's stewards, grown or shrunk with attendance.
    scale = expected_visitors / base["visitors"].sum()
    total = round(base_stewards * scale)
    # Where they go: each location's share of crowd load (visitor-hours) on the base day.
    load_share = base["visitor_hours"] / base["visitor_hours"].sum()
    out = base[["location"]].reset_index(drop=True)
    out["visitors"] = (base["visitors"] * scale).to_numpy()
    out["load_share"] = load_share.to_numpy()
    out["stewards"] = _split(total, out["load_share"].tolist())
    return out


def _split(total: int, shares: list[float]) -> list[int]:
    # Largest remainder: whole stewards per location that always add up to the total.
    raw = [total * s for s in shares]
    whole = [math.floor(r) for r in raw]
    by_remainder = sorted(range(len(raw)), key=lambda i: raw[i] - whole[i], reverse=True)
    for i in by_remainder[: total - sum(whole)]:
        whole[i] += 1
    return whole
