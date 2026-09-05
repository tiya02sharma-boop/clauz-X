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
    for field, min_key, max_key in (
        ("turnover", "turnover_min", "turnover_max"),
        ("headcount", "headcount_min", "headcount_max"),
        ("investment_plant_machinery", "investment_min", "investment_max"),
    ):
        if rule.get(min_key) is not None or rule.get(max_key) is not None:
            ok, detail, message = _condition(field, getattr(business, field, None), rule.get(min_key), rule.get(max_key))
            (matched if ok else failed)[field] = detail
            messages.append(message)
    for field in ("sector", "state", "entity_type"):
        if rule.get(field) is not None:
            ok, detail, message = _condition(field, getattr(business, field, None), required=rule[field])
            (matched if ok else failed)[field] = detail
            messages.append(message)
    if rule.get("gst_registered") is not None:
        ok = business.gst_registered is rule["gst_registered"]
        detail = {"business_value": business.gst_registered, "required": rule["gst_registered"], "matched": ok}
        (matched if ok else failed)["gst_registered"] = detail
        messages.append("GST registration status matches the rule." if ok else "GST registration status does not match the rule.")
    if rule.get("requires_is_factory") is not None:
        required_factory = bool(rule["requires_is_factory"])
        biz_factory = getattr(business, "is_factory", None)
        ok = biz_factory is not None and bool(biz_factory) is required_factory
        detail = {"business_value": biz_factory, "required": required_factory, "matched": ok}
        (matched if ok else failed)["requires_is_factory"] = detail
        if ok:
            if required_factory:
                messages.append("Applies because your business operates as a factory under the Factories Act, not a commercial establishment.")
            else:
                messages.append("Applies because your business operates as a commercial establishment under the Shops and Establishments Act, not a factory.")
        else:
            if required_factory:
                messages.append("Does not apply because your business does not operate as a factory under the Factories Act.")
            else:
                messages.append("Does not apply because your business operates as a factory, not a commercial establishment.")
    if rule.get("requires_flag") is not None:
        flag_name = rule["requires_flag"]
        flags = getattr(business, "flags", None) or {}
        ok = bool(flags.get(flag_name))
        detail = {"business_value": flags.get(flag_name), "required_flag": flag_name, "matched": ok}
        (matched if ok else failed)["requires_flag"] = detail
        messages.append(f"Flag {flag_name!r} is {'present' if ok else 'missing'}.")
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
