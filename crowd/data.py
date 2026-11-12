"""Load the visitor file once, clean it, and add the columns every view needs."""

from functools import lru_cache
from pathlib import Path

import pandas as pd

from crowd import config


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    # 1. Dates: the file uses dd/mm/yyyy, config keys use yyyy-mm-dd.
    df["date"] = pd.to_datetime(df["event_date"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")

    # 2. Fail fast: anything config doesn't describe would silently distort every figure.
    unknown_dates = sorted(set(df["date"]) - set(config.EVENT_DAYS))
    if unknown_dates:
        raise ValueError(f"Dates not described in config.EVENT_DAYS: {unknown_dates}")
    unknown_locations = sorted(set(df["location"]) - set(config.LOCATION_NAMES))
    if unknown_locations:
        raise ValueError(f"Locations not described in config.LOCATION_NAMES: {unknown_locations}")

    # 3. Add readable labels from config, fix the misspelt location, name the missing values.
    for field in ("label", "day_type", "year"):
        df[field] = df["date"].map(lambda d: config.EVENT_DAYS[d][field])
    df["location"] = df["location"].map(config.LOCATION_NAMES)
    df["gender"] = df["gender"].map(config.GENDER_NAMES).fillna(config.NOT_STATED)
    df["age_band"] = df["age_band"].fillna(config.NOT_STATED)
    df["dwell_time"] = df["dwell_time"].fillna(config.NOT_STATED)

    # Rows with an unknown stay still count as visitors, but add nothing to visitor-hours.
    df["dwell_minutes"] = df["dwell_time"].map(config.DWELL_MINUTES)
    df["visitor_hours"] = df["visitors"] * df["dwell_minutes"].fillna(0) / 60

    # 4. Ordered categories keep the same order (days, stay bands) in every chart and table.
    df["dwell_time"] = pd.Categorical(df["dwell_time"], [*config.DWELL_MINUTES, config.NOT_STATED], ordered=True)
    df["label"] = pd.Categorical(df["label"], config.DAY_ORDER, ordered=True)
    df["visitor_type"] = pd.Categorical(df["visitor_type"], config.VISITOR_TYPE_ORDER, ordered=True)
    return df.drop(columns=["event_date"])


@lru_cache(maxsize=1)
def load_visits(path: Path = config.DATA_FILE) -> pd.DataFrame:
    # Cached: the file is read once per process, every callback reuses the same frame.
    return clean(pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False, na_values=["", "N/A"]))
