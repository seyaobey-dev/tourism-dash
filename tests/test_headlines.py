import pandas as pd

from crowd import headlines


def summary(parade_visitors: float, parade_hours: float) -> pd.DataFrame:
    rows = []
    for loc in ["College Green", "O'Connell Bridge"]:
        rows.append({"label": "Normal day 2025", "location": loc, "visitors": 100, "visitor_hours": 100,
                     "avg_stay_minutes": 60})
        rows.append({"label": "Parade 2025", "location": loc, "visitors": parade_visitors,
                     "visitor_hours": parade_hours, "avg_stay_minutes": 90})
    return pd.DataFrame(rows)


def test_crowd_says_but_when_people_fall_and_crowd_load_rises():
    sentence = headlines.crowd(summary(92, 130), "Parade 2025")
    assert "people falls 8% on parade day, but crowd load rises 30%" in sentence


def test_crowd_says_even_more_when_both_rise():
    sentence = headlines.crowd(summary(115, 174), "Parade 2025")
    assert "people rises 15% on parade day, and crowd load rises even more, by 74%" in sentence


def test_stay_names_the_location_it_describes():
    share = pd.Series({"Parade 2025": 0.41, "Normal day 2025": 0.32})
    assert headlines.stay(share, "Parade 2025", "College Green").startswith("At College Green, 41% of visitors")
    assert headlines.stay(share, "Parade 2025", "all").startswith("Across both locations, 41% of visitors")
