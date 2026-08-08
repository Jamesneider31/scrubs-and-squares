"""Shared NCLEX topic rotation for the daily puzzle routine."""

from datetime import date


TOPIC_ROTATION = {
    0: "Pharmacology Monday",
    1: "Prioritization Tuesday",
    2: "Maternal/Newborn Wednesday",
    3: "Med-Surg Thursday",
    4: "Fundamentals Friday",
    5: "Pediatrics Saturday",
    6: "Mixed Review Sunday",
}


def topic_for_date(day=None):
    """Return the intended theme for a datetime.date (or today)."""
    return TOPIC_ROTATION[(day or date.today()).weekday()]
