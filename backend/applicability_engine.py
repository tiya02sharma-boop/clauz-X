"""Pure, deterministic evaluation of approved rule records only."""
from typing import Any
from .models import BusinessProfile
from .storage import load
from .config import RULES_PATH

def _norm(value: Any) -> str | None:
    return str(value).strip().casefold() if value is not None and str(value).strip() else None

def _condition(field: str, business_value: Any, minimum: Any = None, maximum: Any = None, required: Any = None):
    if required is not None:
        ok = _norm(business_value) == _norm(required)
        return ok, {"business_value": business_value, "required": required, "matched": ok}, f"{field} {'matches' if ok else 'does not match'} required value {required!r}"
    checks, detail, reasons = [], {"business_value": business_value}, []
    if minimum is not None:
        ok = business_value is not None and business_value >= minimum; checks.append(ok); detail["required_minimum"] = minimum; reasons.append(f"meets minimum {minimum}" if ok else f"does not meet minimum {minimum}")
    if maximum is not None:
        ok = business_value is not None and business_value <= maximum; checks.append(ok); detail["required_maximum"] = maximum; reasons.append(f"meets maximum {maximum}" if ok else f"exceeds maximum {maximum}")
    ok = all(checks); detail["matched"] = ok
    return ok, detail, f"{field} " + " and ".join(reasons)

def evaluate_rule(rule: dict[str, Any], business: BusinessProfile | dict[str, Any]) -> dict[str, Any]:
    business = business if isinstance(business, BusinessProfile) else BusinessProfile.model_validate(business)
    matched, failed, messages = {}, {}, []
    for field, min_key, max_key in (("turnover", "turnover_min", "turnover_max"), ("headcount", "headcount_min", "headcount_max")):
        if rule.get(min_key) is not None or rule.get(max_key) is not None:
            ok, detail, message = _condition(field, getattr(business, field), rule.get(min_key), rule.get(max_key)); (matched if ok else failed)[field] = detail; messages.append(message)
    for field in ("sector", "state", "entity_type"):
        if rule.get(field) is not None:
            ok, detail, message = _condition(field, getattr(business, field), required=rule[field]); (matched if ok else failed)[field] = detail; messages.append(message)
    if rule.get("gst_registered") is not None:
        ok = business.gst_registered is rule["gst_registered"]
        detail = {"business_value": business.gst_registered, "required": rule["gst_registered"], "matched": ok}
        (matched if ok else failed)["gst_registered"] = detail
        messages.append("GST registration status matches the rule." if ok else "GST registration status does not match the rule.")
    applicable = not failed
    return {"rule_id": rule.get("rule_id"), "obligation_name": rule.get("obligation_name"), "applicable": applicable,
            "matched_conditions": matched, "failed_conditions": failed,
            "reason": "; ".join(messages) if messages else "No applicability restrictions are defined for this rule.",
            "source_citation": rule.get("source_citation"), "source_url": rule.get("source_url"),
            "description": rule.get("description"), "recurrence": rule.get("recurrence"), "due_day_rule": rule.get("due_day_rule"),
            "penalty_formula": rule.get("penalty_formula")}

def check_applicability(business: BusinessProfile | dict[str, Any], rules_path=RULES_PATH) -> dict[str, Any]:
    profile = business if isinstance(business, BusinessProfile) else BusinessProfile.model_validate(business)
    # Retired/superseded baseline rows remain in the catalog for audit history,
    # but never participate in a live applicability decision.
    results = [evaluate_rule(rule, profile) for rule in load(rules_path, []) if rule.get("active", True)]
    return {"business": profile.model_dump(), "applicable_obligations": [r for r in results if r["applicable"]], "not_applicable": [r for r in results if not r["applicable"]]} 
