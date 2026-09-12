"""
TDS domain checker for Clauz X.

Owns all TDS-related compliance rules:
  - rule_tds_monthly_deposit (active: true)

The check() function filters the rule table for active rules, evaluates each
rule against the profile, and returns matched obligations tagged with
_checker="tds_checker".

No cross-checker logic, no dependency resolution — those happen in the
orchestrator after all checkers have run.
"""
from typing import Any

from ..matching import evaluate_rule

_CHECKER_NAME = "tds_checker"

# ---------------------------------------------------------------------------
# Domain rule table — migrated verbatim from rules.json (TDS rows only).
# Do NOT alter threshold values, penalty formulas, citations, or due_day_rule
# text during this refactor.
# ---------------------------------------------------------------------------

TDS_RULES: list[dict[str, Any]] = [
    {
        "rule_id": "rule_tds_monthly_deposit",
        "active": True,
        "obligation_name": "TDS Monthly Challan Deposit (Challan 281)",
        "turnover_min": None,
        "turnover_max": None,
        "headcount_min": None,
        "headcount_max": None,
        "sector": None,
        "state": None,
        "entity_type": None,
        "recurrence": "monthly",
        "due_day_rule": "7th of following month",
        "description": "Monthly deposit of Tax Deducted at Source (TDS) under Income Tax Act.",
        "source_title": "Income Tax Act, 1961",
        "source_url": "https://incometaxindia.gov.in/",
        "source_citation": "Section 200(1) of Income Tax Act, 1961 read with Rule 30 of Income Tax Rules, 1962",
        "penalty_formula": "1.5% per month interest u/s 201(1A) from deduction date + penalty u/s 271C",
        "effective_from": None,
        "effective_to": None,
        "created_at": "2026-09-02T00:00:00+00:00",
        "updated_at": "2026-09-02T00:00:00+00:00",
    },
]


# ---------------------------------------------------------------------------
# Public checker interface
# ---------------------------------------------------------------------------

def check(
    profile: dict[str, Any],
    rule_table: list[dict[str, Any]] = TDS_RULES,
) -> list[dict[str, Any]]:
    """
    Evaluate the profile against TDS rules and return matched obligations.

    Only active rules participate (rules with active=False are kept in the table
    for audit history but are excluded from live applicability decisions — matching
    the existing engine's filter: ``rule.get("active", True)``).

    Each returned obligation dict is tagged with:
      - ``_checker``: "tds_checker"
      - ``_requires_flag``: the rule's requires_flag value (None for current TDS rules)
      - ``_derives_flag``: None (no TDS rule currently derives a flag)

    Parameters
    ----------
    profile:
        Raw business profile dict or BusinessProfile instance.
    rule_table:
        Rule list to evaluate against; defaults to TDS_RULES. Overridable in tests.

    Returns
    -------
    list[dict]
        Matched obligation dicts (applicable == True, active == True only),
        each augmented with _checker, _requires_flag, _derives_flag.
    """
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
