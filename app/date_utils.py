# app/date_utils.py
# ONE TRUTH. ONE FUNCTION. USED EVERYWHERE.
from datetime import date, timedelta

def get_iso_week_for_goal(year: int, month: int, day: int) -> int:
    """
    EXACT SAME LOGIC AS THE ORIGINAL iso_week_filter
    - Sunday → next week (your rule)
    - Dec 29–31 → week 53 if ISO says next year
    - Jan 1–3 → week 1 if ISO says previous year
    This is the sacred WFM ISO week algorithm.
    """
    d = date(year, month, day)

    # Sunday → belongs to next week
    if d.weekday() == 6:  # Sunday
        d = d + timedelta(days=1)

    iso_year, iso_week, _ = d.isocalendar()

    # Dec 29–31 bias: if ISO says next year → force week 53
    if month == 12 and iso_year == year + 1:
        return 53

    # Jan 1–3 bias: if ISO says previous year → force week 1
    if month == 1 and iso_year == year - 1:
        return 1

    return iso_week


def get_iso_year_for_goal(year: int, month: int, day: int) -> int:
    """Return the ISO year after applying Sunday → next week rule"""
    d = date(year, month, day)
    if d.weekday() == 6:
        d = d + timedelta(days=1)
    return d.isocalendar()[0]