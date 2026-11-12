import pandas as pd
import pytest

from crowd import data, metrics


def raw(rows: list[tuple]) -> pd.DataFrame:
    cols = ["location", "event_date", "gender", "age_band", "dwell_time", "visitors", "country_of_origin", "visitor_type"]
    return pd.DataFrame(rows, columns=cols)


SAMPLE = raw([
    ("College Green", "10/03/2025", "N", None, "0-10 min", 100.0, "Ireland", "Local"),
    ("College Green", "17/03/2025", "M", "25-34", "60-120 min", 100.0, "France", "International"),
    ("College Green", "17/03/2025", "F", "18-24", None, 50.0, "Ireland", "Domestic"),
    ("O'Connel Bridge", "17/03/2025", "N", None, "> 600 min", 10.0, "USA", "International"),
])


def test_clean_fixes_names_and_labels_missing_values():
    df = data.clean(SAMPLE)
    assert set(df["location"]) == {"College Green", "O'Connell Bridge"}
    assert df["age_band"].iloc[0] == "Not stated"
    assert df["gender"].tolist() == ["Not stated", "Male", "Female", "Not stated"]
    assert df["label"].iloc[1] == "Parade 2025"


def test_unknown_date_is_an_error():
    with pytest.raises(ValueError, match="EVENT_DAYS"):
        data.clean(raw([("College Green", "01/01/2025", "N", None, "0-10 min", 1.0, "Ireland", "Local")]))


def test_visitor_hours_use_band_midpoints_and_skip_unknown_stays():
    df = data.clean(SAMPLE)
    assert df["visitor_hours"].tolist() == pytest.approx([100 * 5 / 60, 100 * 90 / 60, 0, 10 * 660 / 60])


def test_day_summary_counts_unknown_stay_in_headcount_but_not_in_average():
    s = metrics.day_summary(data.clean(SAMPLE)).set_index(["label", "location"])
    row = s.loc[("Parade 2025", "College Green")]
    assert row["visitors"] == 150
    assert row["avg_stay_minutes"] == pytest.approx(90)


def test_ratio_compares_a_day_to_its_baseline():
    s = metrics.day_summary(data.clean(SAMPLE))
    assert metrics.ratio(s, "visitor_hours", "College Green", "Parade 2025", "Normal day 2025") == pytest.approx(18)


def test_plan_scales_last_years_stewards_and_splits_by_crowd_load():
    # Parade 2025 sample: 160 visitors; College Green 150 visitor-hours, O'Connell Bridge 110.
    p = metrics.plan(data.clean(SAMPLE), "Parade 2025", expected_visitors=320, base_stewards=10).set_index("location")
    assert p["stewards"].sum() == 20
    assert p.loc["College Green", "visitors"] == pytest.approx(300)
    assert p.loc["College Green", "load_share"] == pytest.approx(150 / 260)
    assert p["stewards"].tolist() == [12, 8]


def test_split_always_adds_up():
    assert metrics._split(7, [1 / 3, 1 / 3, 1 / 3]) == [3, 2, 2]
