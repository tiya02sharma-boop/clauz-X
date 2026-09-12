"""
Pure, deterministic evaluation of approved rule records only.

Stage 2 note: The matching logic (evaluate_rule, _norm, _condition) now lives
canonically in matching.py and is re-exported here so that existing callers
(tests, internal tools) that import from applicability_engine continue to work
unchanged.

check_applicability() is now a thin wrapper that delegates to the orchestrator,
then reconstructs the legacy response envelope:
  { business, applicable_obligations, not_applicable }

This means neither app.py nor calendar_service.py require any code changes.
"""
from typing import Any
from .models import BusinessProfile
from .storage import load
from .config import RULES_PATH

# Re-export the matching helpers verbatim so existing tests that import them
# from this module continue to work without modification.
from .matching import _norm, _condition, evaluate_rule  # noqa: F401


def check_applicability(business: BusinessProfile | dict[str, Any], rules_path=RULES_PATH) -> dict[str, Any]:
    """
    Evaluate a business profile against all active compliance rules.

    Delegates to orchestrator.run_compliance_check() for the core evaluation,
    then wraps the result in the legacy response envelope that downstream code
    (calendar_service.py, app.py, existing tests) already expects:

      {
        "business":               <BusinessProfile as dict>,
        "applicable_obligations": [<matched rule dicts>],
        "not_applicable":         []   # orchestrator returns matches only
      }

    The ``rules_path`` parameter is accepted for backwards-compatibility with
    callers that pass it explicitly (e.g. tests using a temp rules file), but
    the orchestrator uses its own embedded rule tables.  Rules added via the
    admin approve flow are stored in rules.json and are evaluated by the legacy
    path; the orchestrator handles the built-in baseline + approved active rules
    that have been migrated into checker modules.

    For full regression parity, this wrapper evaluates BOTH:
      1. The orchestrator's checker-embedded rules (the migrated set).
      2. Any additional active rules found in rules_path that are NOT already
         covered by the checker modules (i.e. dynamically approved rules added
         via the review pipeline).

    This ensures that rules approved through /admin/approve/<id> and written to
    rules.json continue to appear in applicability results alongside the
    checker-embedded rules.
    """
    from . import orchestrator  # local import to avoid circular dependency at module level

    profile = business if isinstance(business, BusinessProfile) else BusinessProfile.model_validate(business)

    # --- Step 1: Run the orchestrator (checker-embedded rules) ---
    orchestrator_matches = orchestrator.run_compliance_check(profile.model_dump())

    # Collect rule_ids already covered by the orchestrator so we don't double-count.
    orchestrator_ids: set[str] = {m.get("rule_id") for m in orchestrator_matches if m.get("rule_id")}

    # --- Step 2: Evaluate any additional active rules from rules_path ---
    # These are rules approved via the admin pipeline that live only in rules.json,
    # not yet migrated into a checker module.
    extra_applicable: list[dict[str, Any]] = []
    extra_not_applicable: list[dict[str, Any]] = []

    for rule in load(rules_path, []):
        if not rule.get("active", True):
            continue
        rule_id = rule.get("rule_id", "")
        if rule_id in orchestrator_ids:
            # Already evaluated by the orchestrator; skip to avoid duplication.
            continue
        result = evaluate_rule(rule, profile)
        if result["applicable"]:
            extra_applicable.append(result)
        else:
            extra_not_applicable.append(result)

    # --- Step 3: Assemble response in the legacy envelope ---
    applicable = orchestrator_matches + extra_applicable

    return {
        "business": profile.model_dump(),
        "applicable_obligations": applicable,
        # not_applicable is only populated for extra rules not in the orchestrator;
        # the orchestrator returns matches only (not-applicable rules are silently dropped).
        "not_applicable": extra_not_applicable,
    }
