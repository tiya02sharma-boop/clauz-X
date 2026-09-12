"""
State / corporate domain checker for Clauz X.

Owns state-specific and corporate-compliance rules:
  - baseline_private_company_annual_filings (active: false — audit history only)

Future additions for this checker:
  - Professional Tax (state-by-state)
  - State-specific GST overrides
  - Other state regulatory obligations

The check() function filters the rule table for active rules, evaluates each
rule against the profile, and returns matched obligations tagged with
_checker="state_checker".

No cross-checker logic, no dependency resolution — those happen in the
orchestrator after all checkers have run.
"""
from typing import Any

from ..matching import evaluate_rule

_CHECKER_NAME = "state_checker"

# ---------------------------------------------------------------------------
# Domain rule table — migrated verbatim from rules.json (state/corporate rows).
# Do NOT alter threshold values, penalty formulas, citations, or due_day_rule
# text during this refactor.
# ---------------------------------------------------------------------------

STATE_RULES: list[dict[str, Any]] = [
    {
        "rule_id": "baseline_private_company_annual_filings",
        "active": False,
        "obligation_name": "Private company annual financial statements and annual return filing",
        "turnover_min": None,
        "turnover_max": None,
        "headcount_min": None,
        "headcount_max": None,
        "sector": None,
        "state": None,
        "entity_type": "private_limited",
        "recurrence": "annual",
        "due_day_rule": "Due dates are calculated from the company's AGM and applicable statutory requirements.",
        "description": "A private company must complete applicable annual financial-statement and annual-return filings with the Registrar of Companies.",
        "source_title": "Companies Act, 2013",
        "source_url": "https://www.mca.gov.in/",
        "source_citation": "Companies Act, 2013, sections 92 and 137, with applicable rules and MCA notifications.",
        "penalty_formula": "₹100 per day of default under Section 403 of Companies Act, 2013",
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
    rule_table: list[dict[str, Any]] = STATE_RULES,
) -> list[dict[str, Any]]:
    """
    Evaluate the profile against state/corporate rules and return matched obligations.

    Only active rules participate (rules with active=False are kept in the table
    for audit history but are excluded from live applicability decisions — matching
    the existing engine's filter: ``rule.get("active", True)``).

    Each returned obligation dict is tagged with:
      - ``_checker``: "state_checker"
      - ``_requires_flag``: the rule's requires_flag value (None for current state rules)
      - ``_derives_flag``: None (no state rule currently derives a flag)

    Parameters
    ----------
    profile:
        Raw business profile dict or BusinessProfile instance.
    rule_table:
        Rule list to evaluate against; defaults to STATE_RULES. Overridable in tests.

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
