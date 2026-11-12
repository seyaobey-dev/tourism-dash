"""Everything that describes the dataset lives here, so a new event or location is a config change."""

from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tourism_sample_2026.csv"

# Source spelling -> display spelling.
LOCATION_NAMES = {"College Green": "College Green", "O'Connel Bridge": "O'Connell Bridge"}

# Every date the app knows about. A date in the file that isn't listed here is an error, not silently dropped.
EVENT_DAYS = {
    "2024-03-17": {"label": "Parade 2024", "day_type": "Parade day", "year": 2024, "weekday": "Sunday"},
    "2025-03-10": {"label": "Normal day 2025", "day_type": "Normal day", "year": 2025, "weekday": "Monday"},
    "2025-03-17": {"label": "Parade 2025", "day_type": "Parade day", "year": 2025, "weekday": "Monday"},
}
DAY_ORDER = ["Normal day 2025", "Parade 2025", "Parade 2024"]

# Dwell bands in order, with the minutes we assume for each (band midpoint).
# "> 600 min" has no upper bound: 660 is our stated assumption.
DWELL_MINUTES = {
    "0-10 min": 5,
    "10-30 min": 20,
    "30-60 min": 45,
    "60-120 min": 90,
    "120-240 min": 180,
    "240-480 min": 360,
    "480-600 min": 540,
    "> 600 min": 660,
}

AGE_ORDER = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
VISITOR_TYPE_ORDER = ["Local", "Domestic", "International"]
GENDER_NAMES = {"M": "Male", "F": "Female", "N": "Not stated"}
NOT_STATED = "Not stated"
