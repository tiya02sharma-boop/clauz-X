"""Compliance calendar builder and business profile registry service."""
from datetime import date, datetime
from pathlib import Path
from typing import Any
import uuid

from . import config
from .applicability_engine import check_applicability
from .due_date_parser import calculate_due_from_config, calculate_next_due_date
from .models import Business, BusinessProfile, ObligationCalendarEntry
from .storage import load, now, save


def compute_obligations_calendar(
    profile: BusinessProfile | dict[str, Any],
    as_of: date | str | None = None,
    rules_path: Path = config.RULES_PATH,
) -> list[ObligationCalendarEntry]:
    """
    Evaluate applicable obligations for a business profile and compute live next_due dates.
    """
    business_prof = profile if isinstance(profile, BusinessProfile) else BusinessProfile.model_validate(profile)
    applicability_result = check_applicability(business_prof, rules_path=rules_path)
    applicable_rules = applicability_result.get("applicable_obligations", [])

    entries: list[ObligationCalendarEntry] = []
    for rule in applicable_rules:
        obligation_id = rule.get("rule_id") or rule.get("obligation_id") or f"ob_{uuid.uuid4().hex[:8]}"
        name = rule.get("obligation_name") or "Statutory Compliance Obligation"
        recurrence = rule.get("recurrence")
        due_day_rule = rule.get("due_day_rule")
        penalty_formula = rule.get("penalty_formula")
        source_citation = rule.get("source_citation")
        description = rule.get("description")
        source_url = rule.get("source_url")

        due_config = rule.get("due_date_config")
        if due_config:
            next_due, needs_manual = calculate_due_from_config(due_config, business_prof.model_dump(), as_of=as_of)
        else:
            next_due, needs_manual = calculate_next_due_date(due_day_rule, recurrence, as_of=as_of)

        entry = ObligationCalendarEntry(
            obligation_id=obligation_id,
            name=name,
            recurrence=recurrence,
            next_due=next_due,
            penalty_formula=penalty_formula,
            source_citation=source_citation,
            due_day_rule=due_day_rule,
            needs_manual_date_entry=needs_manual,
            description=description,
            source_url=source_url,
        )
        entries.append(entry)

    # Sort entries by next_due date (nulls last)
    entries.sort(key=lambda x: (x.next_due is None, x.next_due or ""))
    return entries


def list_businesses(businesses_path: Path = config.BUSINESSES_PATH) -> list[dict[str, Any]]:
    """Return all stored businesses."""
    return load(businesses_path, [])


def get_business(business_id: str, businesses_path: Path = config.BUSINESSES_PATH) -> dict[str, Any] | None:
    """Retrieve a single business by ID."""
    businesses = load(businesses_path, [])
    return next((b for b in businesses if b.get("business_id") == business_id), None)


def save_or_update_business(
    business_payload: dict[str, Any] | BusinessProfile,
    as_of: date | str | None = None,
    businesses_path: Path = config.BUSINESSES_PATH,
    rules_path: Path = config.RULES_PATH,
) -> dict[str, Any]:
    """
    Create or update a business profile and recompute its obligation calendar.
    """
    if isinstance(business_payload, BusinessProfile):
        profile_dict = business_payload.model_dump()
        business_id = business_payload.business_id
    elif isinstance(business_payload, dict):
        if "profile" in business_payload and isinstance(business_payload["profile"], dict):
            profile_dict = business_payload["profile"]
            business_id = business_payload.get("business_id") or profile_dict.get("business_id")
        else:
            profile_dict = business_payload
            business_id = business_payload.get("business_id")
    else:
        raise ValueError("Invalid business payload")

    business_profile = BusinessProfile.model_validate(profile_dict)
    business_id = business_id or business_profile.business_id or f"biz_{uuid.uuid4().hex[:8]}"
    business_profile.business_id = business_id

    # Recompute calendar obligations
    obligations = compute_obligations_calendar(business_profile, as_of=as_of, rules_path=rules_path)
    obligations_data = [ob.model_dump() for ob in obligations]

    businesses = load(businesses_path, [])
    existing_index = next((i for i, b in enumerate(businesses) if b.get("business_id") == business_id), None)

    current_time = now()
    if existing_index is not None:
        created_at = businesses[existing_index].get("created_at", current_time)
        business_record = {
            "business_id": business_id,
            "profile": business_profile.model_dump(),
            "obligations": obligations_data,
            "created_at": created_at,
            "updated_at": current_time,
        }
        businesses[existing_index] = business_record
    else:
        business_record = {
            "business_id": business_id,
            "profile": business_profile.model_dump(),
            "obligations": obligations_data,
            "created_at": current_time,
            "updated_at": current_time,
        }
        businesses.append(business_record)

    save(businesses_path, businesses)
    return business_record


def recompute_business_calendar(
    business_id: str,
    as_of: date | str | None = None,
    businesses_path: Path = config.BUSINESSES_PATH,
    rules_path: Path = config.RULES_PATH,
) -> dict[str, Any] | None:
    """Recompute calendar obligations for an existing business record."""
    business = get_business(business_id, businesses_path=businesses_path)
    if not business:
        return None
    return save_or_update_business(
        business,
        as_of=as_of,
        businesses_path=businesses_path,
        rules_path=rules_path,
    )


def save_compliance_check(
    report: dict[str, Any], checks_path: Path | None = None
) -> dict[str, Any]:
    """Persist a verification report, assigning its audit identifiers if needed."""
    checks_path = checks_path or config.COMPLIANCE_CHECKS_PATH
    checks = load(checks_path, [])
    stored = dict(report)
    if not stored.get("check_id"):
        stored["check_id"] = f"chk_{uuid.uuid4().hex[:12]}"
    if not stored.get("created_at"):
        stored["created_at"] = now()
    checks.append(stored)
    save(checks_path, checks)
    return stored


def list_compliance_checks(
    business_id: str | None = None, checks_path: Path | None = None
) -> list[dict[str, Any]]:
    checks_path = checks_path or config.COMPLIANCE_CHECKS_PATH
    checks = load(checks_path, [])
    if business_id:
        checks = [check for check in checks if check.get("business_id") == business_id]
    return list(reversed(checks))
