"""Idempotent deadline reminder scheduler with WaSenderAPI WhatsApp integration."""
from datetime import date, datetime
import logging
from pathlib import Path
from typing import Any

from . import config
from .calendar_service import compute_obligations_calendar
from .models import ObligationCalendarEntry, ReminderLogEntry
from .storage import load, now, save
from .whatsapp_sender import normalize_phone_number, send_whatsapp_message

logger = logging.getLogger(__name__)


def compose_reminder_message(
    business_name: str | None,
    obligation_name: str,
    due_date: str,
    days_left: int,
    penalty_formula: str | None,
    source_citation: str | None,
) -> str:
    """Format statutory compliance deadline reminder message."""
    biz_display = business_name or "Your Business"
    penalty_display = penalty_formula or "Statutory late fees and interest apply as per relevant Act."
    citation_display = source_citation or "Applicable statutory rules and regulations."
    
    day_str = "tomorrow (1 day left)" if days_left == 1 else f"in {days_left} days"

    lines = [
        "🚨 *Clauz X Compliance Deadline Reminder*",
        "",
        f"🏢 *Entity:* {biz_display}",
        f"📋 *Obligation:* {obligation_name}",
        f"📅 *Due Date:* {due_date} ({day_str})",
        "",
        f"⚠️ *Penalty Risk:* {penalty_display}",
        f"📖 *Statutory Grounding:* {citation_display}",
        "",
        "Please ensure timely submission with the relevant statutory authority.",
    ]
    return "\n".join(lines)


def run_reminder_cycle(
    as_of_date: date | str | None = None,
    businesses_path: Path = config.BUSINESSES_PATH,
    reminders_path: Path = config.REMINDERS_PATH,
    rules_path: Path = config.RULES_PATH,
) -> dict[str, Any]:
    """
    Execute an idempotent deadline reminder cycle for all businesses.
    
    Accepts:
    - as_of_date: Date to evaluate against (defaults to today).
    
    Evaluates:
    - Days left in {7, 3, 1}.
    - Ignores unparseable / null next_due obligations.
    - Skips duplicate sends if already logged for (business_id, obligation_id, window, date).
    - Logs every send attempt (sent, simulated, failed).
    """
    if as_of_date is None:
        ref_date = date.today()
    elif isinstance(as_of_date, str):
        try:
            ref_date = date.fromisoformat(as_of_date.split("T")[0])
        except ValueError:
            ref_date = date.today()
    elif isinstance(as_of_date, datetime):
        ref_date = as_of_date.date()
    elif isinstance(as_of_date, date):
        ref_date = as_of_date
    else:
        ref_date = date.today()

    as_of_iso = ref_date.isoformat()
    businesses = load(businesses_path, [])
    existing_logs = load(reminders_path, [])

    # Index existing logs by (business_id, obligation_id, window, date)
    sent_keys = {
        (
            log.get("business_id"),
            log.get("obligation_id"),
            log.get("window"),
            log.get("date"),
        )
        for log in existing_logs
        if log.get("status") in ("sent", "simulated")
    }

    summary = {
        "as_of_date": as_of_iso,
        "businesses_evaluated": len(businesses),
        "candidates_found": 0,
        "reminders_sent": 0,
        "reminders_simulated": 0,
        "reminders_failed": 0,
        "reminders_skipped_duplicate": 0,
        "details": [],
    }

    new_logs: list[dict[str, Any]] = []

    for business in businesses:
        biz_id = business.get("business_id")
        profile = business.get("profile", {})
        biz_name = profile.get("business_name") or business.get("business_name")
        raw_whatsapp = profile.get("whatsapp_number") or business.get("whatsapp_number")

        # Skip if no phone number provided
        if not raw_whatsapp or not str(raw_whatsapp).strip():
            continue

        normalized_phone = normalize_phone_number(str(raw_whatsapp))
        if not normalized_phone:
            continue

        # Recompute calendar dynamically against the given as_of_date
        obligations = compute_obligations_calendar(profile, as_of=ref_date, rules_path=rules_path)

        for ob in obligations:
            # Skip unparseable or null dates
            if not ob.next_due or ob.needs_manual_date_entry:
                continue

            try:
                due_d = date.fromisoformat(ob.next_due)
            except ValueError:
                continue

            days_left = (due_d - ref_date).days

            # Check if days_left matches one of our trigger windows: 7, 3, or 1
            if days_left not in (7, 3, 1):
                continue

            window = days_left
            summary["candidates_found"] += 1
            dedup_key = (biz_id, ob.obligation_id, window, as_of_iso)

            # Idempotency check: skip if already sent for this business, obligation, window, and as_of date
            if dedup_key in sent_keys:
                summary["reminders_skipped_duplicate"] += 1
                summary["details"].append({
                    "business_id": biz_id,
                    "obligation_id": ob.obligation_id,
                    "window": window,
                    "status": "skipped_duplicate",
                    "reason": "Reminder already dispatched for this date & window",
                })
                continue

            # Compose message
            msg_text = compose_reminder_message(
                business_name=biz_name,
                obligation_name=ob.name,
                due_date=ob.next_due,
                days_left=days_left,
                penalty_formula=ob.penalty_formula,
                source_citation=ob.source_citation,
            )

            # Dispatch via WhatsApp layer
            send_result = send_whatsapp_message(
                to=normalized_phone,
                message=msg_text,
            )

            # Record log entry
            log_entry = ReminderLogEntry(
                business_id=biz_id,
                business_name=biz_name,
                obligation_id=ob.obligation_id,
                obligation_name=ob.name,
                window=window,
                date=as_of_iso,
                to=normalized_phone,
                status=send_result.status,
                sid=send_result.sid,
                error_code=send_result.error_code,
                sent_at=now(),
            )
            entry_dict = log_entry.model_dump()
            new_logs.append(entry_dict)
            sent_keys.add(dedup_key)

            if send_result.status == "sent":
                summary["reminders_sent"] += 1
            elif send_result.status == "simulated":
                summary["reminders_simulated"] += 1
            elif send_result.status == "failed":
                summary["reminders_failed"] += 1

            summary["details"].append({
                "business_id": biz_id,
                "obligation_id": ob.obligation_id,
                "window": window,
                "status": send_result.status,
                "sid": send_result.sid,
                "error_code": send_result.error_code,
            })

    # Save newly generated log entries
    if new_logs:
        all_logs = existing_logs + new_logs
        save(reminders_path, all_logs)

    return summary
