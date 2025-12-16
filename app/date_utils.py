# app/date_utils.py
# ONE TRUTH. ONE FUNCTION. USED EVERYWHERE.
from datetime import date, timedelta

# app/date_utils.py
from calendar import monthrange

def get_iso_week_for_goal(year: int, month: int, day: int) -> int:
    """
    Sacred WFM ISO week algorithm — now bulletproof against invalid days.
    If day is out of range (e.g., 32 in Dec), rolls to next month/year.
    """
    year = int(year)
    month = int(month)
    day = int(day)

    # Normalize day if out of range
    while True:
        days_in_month = monthrange(year, month)[1]
        if 1 <= day <= days_in_month:
            break
        if day > days_in_month:
            day -= days_in_month
            month += 1
            if month > 12:
                month = 1
                year += 1
        elif day < 1:
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            day += monthrange(year, month)[1]

    d = date(year, month, day)

    # Sunday → next week rule
    if d.weekday() == 6:  # Sunday
        d = d + timedelta(days=1)

    iso_year, iso_week, _ = d.isocalendar()

    # Dec 29–31 bias
    if month == 12 and iso_year == year + 1:
        return 53

    # Jan 1–3 bias
    if month == 1 and iso_year == year - 1:
        return 1

    return iso_week


def get_iso_year_for_goal(year: int, month: int, day: int) -> int:
    """Return the ISO year after applying Sunday → next week rule"""
    d = date(year, month, day)
    if d.weekday() == 6:
        d = d + timedelta(days=1)
    return d.isocalendar()[0]


"""
Date helpers for calendar views — Sunday-first week, month-first day.
Used by calendar_routes API for reflection notes keying.
"""
from datetime import date, timedelta

def get_sunday_of_week(year: int, month: int, day: int) -> date:
    """
    Return the Sunday date of the week containing the given year/month/day.
    Matches our Sunday-first calendar — eternal consistency.
    """
    d = date(year, month, day)
    # weekday(): Mon=0 ... Sun=6 → subtract to reach Sunday
    return d - timedelta(days=(d.weekday() + 1) % 7)

def get_first_of_month(year: int, month: int) -> date:
    """Return YYYY-MM-01 for the given year/month."""
    return date(year, month, 1)