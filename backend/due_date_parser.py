"""Due date calculation engine for statutory MSME compliance obligations."""
import calendar
from datetime import date, datetime
import re
from typing import Tuple

# Pattern matching "20th of following month", "15th of next month", "7th of the following month", "last day of following month"
_MONTHLY_NTH_PATTERN = re.compile(
    r"(?:(?:by|on|before|by\s+the|on\s+the|before\s+the)\s+)?"
    r"(?:(\d{1,2})(?:st|nd|rd|th)?|last)\s+(?:day\s+)?"
    r"of\s+(?:the\s+)?(?:following|next|each|every)\s+month",
    re.IGNORECASE,
)

_QUARTERLY_NTH_PATTERN = re.compile(
    r"(?:(?:by|on|before|by\s+the|on\s+the|before\s+the)\s+)?"
    r"(?:(\d{1,2})(?:st|nd|rd|th)?|last)\s+(?:day\s+)?"
    r"of\s+(?:the\s+)?(?:month\s+following\s+(?:the\s+)?(?:quarter|quarter\s*end)|following\s+quarter)",
    re.IGNORECASE,
)


def _extract_day_number(text: str) -> int | None:
    """Extract day number (1-31) or 99 for 'last day' from rule text."""
    if not text:
        return None
    cleaned = text.strip()
    match = _MONTHLY_NTH_PATTERN.search(cleaned) or _QUARTERLY_NTH_PATTERN.search(cleaned)
    if not match:
        return None
    day_str = match.group(1)
    if day_str is None:  # matched 'last'
        return 99
    try:
        val = int(day_str)
        if 1 <= val <= 31:
            return val
    except ValueError:
        pass
    return None


def calculate_next_due_date(
    due_day_rule: str | None,
    recurrence: str | None,
    as_of: date | str | None = None,
) -> Tuple[str | None, bool]:
    """
    Parse due_day_rule and return (next_due_iso_date_or_none, needs_manual_date_entry).
    
    Strictly follows zero-guessing policy:
    - Resolves common "Nth of following month" for monthly / quarterly obligations.
    - For unparseable, one-time, half-yearly, annual or irregular rules, returns (None, True).
    """
    if not due_day_rule or not isinstance(due_day_rule, str):
        return None, True

    if as_of is None:
        ref_date = date.today()
    elif isinstance(as_of, str):
        try:
            ref_date = date.fromisoformat(as_of.split("T")[0])
        except ValueError:
            ref_date = date.today()
    elif isinstance(as_of, datetime):
        ref_date = as_of.date()
    elif isinstance(as_of, date):
        ref_date = as_of
    else:
        ref_date = date.today()

    rec = (recurrence or "").strip().lower()
    
    # Recurrence types that require manual entry or cannot be computed via simple following-month rule
    if rec in ("one_time", "one-time", "event_based", "event-based", "half_yearly", "half-yearly", "annual", "yearly"):
        return None, True

    day_num = _extract_day_number(due_day_rule)
    if day_num is None:
        # Check if the text matches basic "Nth of following month" even if recurrence wasn't explicit
        return None, True

    # Compute next due date for Monthly
    if rec in ("monthly", "periodic", ""):
        # Check candidate in current month
        days_in_current_month = calendar.monthrange(ref_date.year, ref_date.month)[1]
        target_day_current = min(day_num, days_in_current_month) if day_num != 99 else days_in_current_month
        candidate_current = date(ref_date.year, ref_date.month, target_day_current)

        if candidate_current >= ref_date:
            return candidate_current.isoformat(), False
        
        # If candidate in current month has passed, roll to next month
        if ref_date.month == 12:
            next_year = ref_date.year + 1
            next_month = 1
        else:
            next_year = ref_date.year
            next_month = ref_date.month + 1

        days_in_next_month = calendar.monthrange(next_year, next_month)[1]
        target_day_next = min(day_num, days_in_next_month) if day_num != 99 else days_in_next_month
        candidate_next = date(next_year, next_month, target_day_next)
        return candidate_next.isoformat(), False

    # Compute next due date for Quarterly
    if rec == "quarterly":
        # Standard calendar quarters end on Mar 31, Jun 30, Sep 30, Dec 31
        # Due in Apr (month 4), Jul (month 7), Oct (month 10), Jan (month 1 of next year)
        candidates = []
        for year_offset in (0, 1):
            target_year = ref_date.year + year_offset
            for due_month in (1, 4, 7, 10):
                days_in_m = calendar.monthrange(target_year, due_month)[1]
                target_d = min(day_num, days_in_m) if day_num != 99 else days_in_m
                c_date = date(target_year, due_month, target_d)
                if c_date >= ref_date:
                    candidates.append(c_date)
        if candidates:
            candidates.sort()
            return candidates[0].isoformat(), False
        return None, True

    # Any other unrecognized recurrence
    return None, True


def calculate_due_from_config(config: dict | None, profile: dict, as_of: date | str | None = None) -> Tuple[str | None, bool]:
    """Calculate approved event-relative dates; missing inputs are never guessed."""
    if not config or config.get("type") != "days_after_profile_date":
        return None, True
    value = profile.get(config.get("field"))
    if not isinstance(value, str):
        return None, True
    try:
        return (date.fromisoformat(value) + __import__("datetime").timedelta(days=int(config["days"]))).isoformat(), False
    except (ValueError, TypeError, KeyError):
        return None, True
