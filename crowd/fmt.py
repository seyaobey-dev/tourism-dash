"""Number formatting shared by headlines, cards and hovers."""


def people(n: float) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}m"
    if n >= 1_000:
        return f"{n / 1_000:.0f}k"
    return f"{n:.0f}"


def times(r: float) -> str:
    return f"{r:.2f}×"


def change(r: float) -> str:
    pct = (r - 1) * 100
    return f"{pct:+.0f}%"


def moves(r: float) -> str:
    """A ratio in words: 'rises 22%', 'falls 8%', 'stays level'."""
    pct_change = round((r - 1) * 100)
    if pct_change == 0:
        return "stays level"
    return f"{'rises' if pct_change > 0 else 'falls'} {abs(pct_change)}%"


def pct(share: float) -> str:
    return f"{share * 100:.0f}%"


def minutes(m: float) -> str:
    hours, mins = divmod(round(m), 60)
    return f"{hours}h {mins:02d}m" if hours else f"{mins} min"
