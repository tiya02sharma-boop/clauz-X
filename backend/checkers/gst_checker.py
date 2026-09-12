"""
GST domain checker for Clauz X.

Owns all GST-related compliance rules:
  - baseline_gst_registered_return  (active: false — audit history only)
  - rule_gstr3b_monthly             (active: true)

The check() function filters the rule table for active rules, evaluates each
rule against the profile, and returns matched obligations tagged with
_checker="gst_checker".

No cross-checker logic, no dependency resolution — those happen in the
orchestrator after all checkers have run.
"""
from typing import Any

from ..matching import evaluate_rule

_CHECKER_NAME = "gst_checker"

# ---------------------------------------------------------------------------
# Domain rule table — migrated verbatim from rules.json (GST rows only).
# Do NOT alter threshold values, penalty formulas, citations, or due_day_rule
# text during this refactor.
# ---------------------------------------------------------------------------

GST_RULES: list[dict[str, Any]] = [
    {
        "rule_id": "baseline_gst_registered_return",
        "active": False,
        "obligation_name": "GST return filing and tax payment",
        "gst_registered": True,
        "turnover_min": None,
        "turnover_max": None,
        "headcount_min": None,
        "headcount_max": None,
        "sector": None,
        "state": None,
        "entity_type": None,
        "recurrence": "periodic",
        "due_day_rule": "Filing frequency and due date depend on the taxpayer's GST return scheme.",
        "description": "A GST-registered business must meet the return and tax-payment obligations applicable to its registration and filing scheme.",
        "source_title": "Central Goods and Services Tax Act, 2017",
        "source_url": "https://cbic-gst.gov.in/",
        "source_citation": "Central Goods and Services Tax Act, 2017, sections 37 and 39; applicable CGST Rules and CBIC notifications.",
        "penalty_formula": None,
        "effective_from": None,
        "effective_to": None,
        "created_at": "2026-09-02T00:00:00+00:00",
        "updated_at": "2026-09-02T00:00:00+00:00",
    },
    {
        "rule_id": "rule_gstr3b_monthly",
        "active": True,
        "obligation_name": "GSTR-3B Monthly Return & Tax Payment",
        "gst_registered": True,
        "turnover_min": None,
        "turnover_max": None,
        "headcount_min": None,
        "headcount_max": None,
        "sector": None,
        "state": None,
        "entity_type": None,
        "recurrence": "monthly",
        "due_day_rule": "20th of following month",
        "description": "Monthly summary return of inward and outward supplies and payment of GST liability.",
        "source_title": "Central Goods and Services Tax Act, 2017",
        "source_url": "https://cbic-gst.gov.in/",
        "source_citation": "Section 39(1) of CGST Act, 2017 read with Rule 61(5) of CGST Rules, 2017",
        "penalty_formula": "₹50/day (₹20/day for NIL) late fee u/s 47 + 18% p.a. interest on unpaid tax u/s 50",
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
    rule_table: list[dict[str, Any]] = GST_RULES,
) -> list[dict[str, Any]]:
    """
    Evaluate the profile against GST rules and return matched obligations.

    Only active rules participate (rules with active=False are kept in the table
    for audit history but are excluded from live applicability decisions — matching
    the existing engine's filter: ``rule.get("active", True)``).

    Each returned obligation dict is tagged with:
      - ``_checker``: "gst_checker"
      - ``_requires_flag``: the rule's requires_flag value (None for most GST rules)
      - ``_derives_flag``: "gst_registered" if the match implies GST registration

    Parameters
    ----------
    profile:
        Raw business profile dict or BusinessProfile instance.
    rule_table:
        Rule list to evaluate against; defaults to GST_RULES. Overridable in tests.

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
            # A GST registration rule match implies the gst_registered flag for
            # downstream dependent obligations (two-pass resolution hook).
            evaluation["_derives_flag"] = "gst_registered" if rule.get("gst_registered") else None
            results.append(evaluation)
    return results
