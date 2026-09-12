"""
Shared, deterministic rule-matching logic for the Clauz X compliance engine.

This module is the single source of truth for the matching predicate and
dependency-resolution pass.  Every checker imports from here; no checker
contains its own matching logic.

Design principles (Stage 2):
- Pure functions only — no I/O, no side-effects.
- No LLM calls, no scoring, no probabilistic logic.
- Verbatim copy of evaluate_rule() from the original applicability_engine so
  that outputs are byte-for-byte identical for the same (profile, rule) pair.
"""
from typing import Any

from .models import BusinessProfile


# ---------------------------------------------------------------------------
# Internal helpers (verbatim from applicability_engine.py)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Public matching predicate (verbatim from applicability_engine.evaluate_rule)
# ---------------------------------------------------------------------------

def evaluate_rule(rule: dict[str, Any], business: "BusinessProfile | dict[str, Any]") -> dict[str, Any]:
    """
    Evaluate a single rule against a business profile.

    Returns a rich dict:
      { rule_id, obligation_name, applicable, matched_conditions,
        failed_conditions, reason, source_citation, source_url,
        description, recurrence, due_day_rule, penalty_formula }

    This function is an **exact verbatim copy** of evaluate_rule() from
    applicability_engine.py so both code paths produce identical output.
    Do not alter logic here without making the same change in applicability_engine.py.
    """
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


# ---------------------------------------------------------------------------
# Two-pass dependency resolution
# ---------------------------------------------------------------------------

def resolve_dependent_obligations(
    profile: "BusinessProfile | dict[str, Any]",
    all_matches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Apply a two-pass dependency resolution over a merged list of raw checker matches.

    Pass 1 — obligations with no flag dependency (requires_flag is None in the
              originating rule).  These are collected as the unconditional set.

    Pass 2 — obligations that depend on a flag being true.  The flags dict is
              augmented with flags derived from pass-1 results (e.g. any match
              tagged _derives_flag="gst_registered" implies gst_registered=True),
              then requires_flag obligations are re-evaluated against the enriched
              flags dict.

    Currently no rules in the live rule set use requires_flag, so this function
    acts as a transparent pass-through for existing data.  The infrastructure is
    correct and ready for future dependent-obligation rules.

    Parameters
    ----------
    profile:
        The business profile (BusinessProfile or raw dict).
    all_matches:
        Raw matches from all checkers — each dict must have been produced by
        evaluate_rule() and tagged with ``_checker``, ``_requires_flag``, and
        optionally ``_derives_flag`` by the checker.

    Returns
    -------
    list[dict]
        Final resolved list of applicable obligations.
    """
    if isinstance(profile, dict):
        bp = BusinessProfile.model_validate(profile)
    else:
        bp = profile

    # Separate matches that carry a requires_flag dependency from those that don't.
    no_dep: list[dict[str, Any]] = []
    has_dep: list[dict[str, Any]] = []
    for match in all_matches:
        if match.get("_requires_flag") is None:
            no_dep.append(match)
        else:
            has_dep.append(match)

    # If nothing has a flag dependency, return as-is.
    if not has_dep:
        return no_dep

    # Derive flags from pass-1 results (augment the profile's flags dict).
    derived_flags: dict[str, bool] = {}
    for match in no_dep:
        flag = match.get("_derives_flag")
        if flag:
            derived_flags[flag] = True

    # Merge with the profile's existing flags.
    base_flags: dict[str, Any] = dict(bp.flags or {})
    merged_flags = {**base_flags, **derived_flags}

    # Pass 2: re-check requires_flag obligations against enriched flags.
    resolved_dep: list[dict[str, Any]] = []
    for match in has_dep:
        flag_name = match["_requires_flag"]
        if merged_flags.get(flag_name):
            resolved_dep.append(match)

    return no_dep + resolved_dep
