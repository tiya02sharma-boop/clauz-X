"""
MSME domain checker for Clauz X.

Owns MSME-specific compliance rules (e.g. MSME-1 delayed payment reporting).

Currently no approved rules exist for this domain — MSME_RULES is intentionally
empty.  This checker module is included to:
  1. Demonstrate the extensibility of the checker architecture.
  2. Allow future MSME rules to be added here without touching orchestrator.py,
     matching.py, or any other checker file.

Adding a new MSME rule:
  Append a rule dict to MSME_RULES following the standard rule schema and set
  "active": True.  No other files need to change.
"""
from typing import Any

_CHECKER_NAME = "msme_checker"

# ---------------------------------------------------------------------------
# Domain rule table — no approved MSME rules yet.
# ---------------------------------------------------------------------------

MSME_RULES: list[dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Public checker interface
# ---------------------------------------------------------------------------

def check(
    profile: dict[str, Any],
    rule_table: list[dict[str, Any]] = MSME_RULES,
) -> list[dict[str, Any]]:
    """
    Evaluate the profile against MSME rules and return matched obligations.

    Currently always returns an empty list because MSME_RULES is empty.
    This is intentional — the checker is future-ready, not a stub.

    Parameters
    ----------
    profile:
        Raw business profile dict or BusinessProfile instance.
    rule_table:
        Rule list to evaluate against; defaults to MSME_RULES. Overridable in tests.

    Returns
    -------
    list[dict]
        Empty list until MSME rules are approved and added to MSME_RULES.
    """
    # Import deferred to avoid circular dependency when rule_table is empty;
    # evaluate_rule is imported only if there are rules to evaluate.
    if not rule_table:
        return []

    from ..matching import evaluate_rule  # noqa: PLC0415

    results: list[dict[str, Any]] = []
    for rule in rule_table:
        if not rule.get("active", True):
            continue
        evaluation = evaluate_rule(rule, profile)
        if evaluation["applicable"]:
            evaluation["_checker"] = _CHECKER_NAME
            evaluation["_requires_flag"] = rule.get("requires_flag")
            evaluation["_derives_flag"] = None
            results.append(evaluation)
    return results
