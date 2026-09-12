"""
Labour domain checker for Clauz X.

Owns all labour/factory-related compliance rules:
  - baseline_epf_20_employee_assessment    (active: false — audit history only)
  - rule_epf_monthly_ecr                   (active: true)
  - rule_factories_act_registration        (active: true)
  - rule_shops_establishments_registration (active: true)

The check() function filters the rule table for active rules, evaluates each
rule against the profile, and returns matched obligations tagged with
_checker="labour_checker".

No cross-checker logic, no dependency resolution — those happen in the
orchestrator after all checkers have run.

Note on is_factory routing:
  rule_factories_act_registration has requires_is_factory=True   → matches only factories
  rule_shops_establishments_registration has requires_is_factory=False → matches only non-factories
  This routing is handled entirely by matching.evaluate_rule(); no special logic here.
"""
from typing import Any

from ..matching import evaluate_rule

_CHECKER_NAME = "labour_checker"

# ---------------------------------------------------------------------------
# Domain rule table — migrated verbatim from rules.json (labour rows only).
# Do NOT alter threshold values, penalty formulas, citations, or due_day_rule
# text during this refactor.
# ---------------------------------------------------------------------------

LABOUR_RULES: list[dict[str, Any]] = [
    {
        "rule_id": "baseline_epf_20_employee_assessment",
        "active": False,
        "obligation_name": "EPF coverage and contribution compliance",
        "turnover_min": None,
        "turnover_max": None,
        "headcount_min": 20,
        "headcount_max": None,
        "sector": None,
        "state": None,
        "entity_type": None,
        "recurrence": "monthly",
        "due_day_rule": "Confirm the current statutory due date and establishment coverage before filing.",
        "description": "Establishments at or above the employee threshold should assess EPF coverage and meet applicable contribution and return obligations.",
        "source_title": "Employees' Provident Funds and Miscellaneous Provisions Act, 1952",
        "source_url": "https://www.epfindia.gov.in/",
        "source_citation": "Employees' Provident Funds and Miscellaneous Provisions Act, 1952, section 1(3), subject to applicable notifications and establishment coverage.",
        "penalty_formula": None,
        "effective_from": None,
        "effective_to": None,
        "created_at": "2026-09-02T00:00:00+00:00",
        "updated_at": "2026-09-02T00:00:00+00:00",
    },
    {
        "rule_id": "rule_epf_monthly_ecr",
        "active": True,
        "obligation_name": "EPF Monthly Electronic Challan cum Return (ECR)",
        "turnover_min": None,
        "turnover_max": None,
        "headcount_min": 20,
        "headcount_max": None,
        "sector": None,
        "state": None,
        "entity_type": None,
        "recurrence": "monthly",
        "due_day_rule": "15th of following month",
        "description": "Monthly deposit of provident fund contributions and submission of ECR for covered employees.",
        "source_title": "Employees' Provident Funds and Miscellaneous Provisions Act, 1952",
        "source_url": "https://www.epfindia.gov.in/",
        "source_citation": "EPF Scheme 1952, Paragraph 38(1) & Section 6 of EPF & MP Act, 1952",
        "penalty_formula": "12% p.a. simple interest u/s 7Q + penal damages u/s 14B up to 25% p.a.",
        "effective_from": None,
        "effective_to": None,
        "created_at": "2026-09-02T00:00:00+00:00",
        "updated_at": "2026-09-02T00:00:00+00:00",
    },
    {
        "rule_id": "rule_factories_act_registration",
        "active": True,
        "obligation_name": "Factories Act Registration & Licensing",
        "turnover_min": None,
        "turnover_max": None,
        "headcount_min": None,
        "headcount_max": None,
        "investment_min": None,
        "investment_max": None,
        "requires_is_factory": True,
        "sector": None,
        "state": None,
        "entity_type": None,
        "recurrence": "annual",
        "due_day_rule": "Annual renewal before commencement or expiration of calendar year (needs manual date entry).",
        "description": (
            "Statutory registration and licensing of manufacturing premises employing workers and power machinery "
            "under the Factories Act, 1948. [PLACEHOLDER: State-specific worker thresholds and renewal timelines "
            "require legal verification before production use]."
        ),
        "source_title": "Factories Act, 1948",
        "source_url": "https://labour.gov.in/",
        "source_citation": (
            "Factories Act, 1948, Section 6 read with State Factory Rules "
            "[PLACEHOLDER: Verify state amendment and license fee schedule]."
        ),
        "penalty_formula": (
            "Imprisonment up to 2 years or fine up to ₹1,00,000 under Section 92 of Factories Act, 1948 "
            "[PLACEHOLDER: Legal verification required]."
        ),
        "effective_from": None,
        "effective_to": None,
        "created_at": "2026-09-02T00:00:00+00:00",
        "updated_at": "2026-09-02T00:00:00+00:00",
    },
    {
        "rule_id": "rule_shops_establishments_registration",
        "active": True,
        "obligation_name": "Shops & Commercial Establishments Registration",
        "turnover_min": None,
        "turnover_max": None,
        "headcount_min": None,
        "headcount_max": None,
        "investment_min": None,
        "investment_max": None,
        "requires_is_factory": False,
        "sector": None,
        "state": None,
        "entity_type": None,
        "recurrence": "annual",
        "due_day_rule": "Renewal timeline as specified by State Shops & Establishments Act (needs manual date entry).",
        "description": (
            "Statutory registration for non-factory commercial establishments, offices, and shops under State law. "
            "[PLACEHOLDER: State-specific registration criteria and renewal deadlines require legal verification "
            "before production use]."
        ),
        "source_title": "State Shops and Commercial Establishments Act",
        "source_url": "https://labour.gov.in/",
        "source_citation": (
            "State Shops and Commercial Establishments Act (e.g. Maharashtra Shops & Establishments Act, 2017) "
            "[PLACEHOLDER: Verify applicable State Act rules]."
        ),
        "penalty_formula": (
            "Monetary fines ranging from ₹1,00,000 depending on state schedule "
            "[PLACEHOLDER: Legal verification required]."
        ),
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
    rule_table: list[dict[str, Any]] = LABOUR_RULES,
) -> list[dict[str, Any]]:
    """
    Evaluate the profile against labour rules and return matched obligations.

    Only active rules participate (rules with active=False are kept in the table
    for audit history but are excluded from live applicability decisions — matching
    the existing engine's filter: ``rule.get("active", True)``).

    Each returned obligation dict is tagged with:
      - ``_checker``: "labour_checker"
      - ``_requires_flag``: the rule's requires_flag value (None for all current labour rules)
      - ``_derives_flag``: None (no labour rule currently derives a flag)

    Parameters
    ----------
    profile:
        Raw business profile dict or BusinessProfile instance.
    rule_table:
        Rule list to evaluate against; defaults to LABOUR_RULES. Overridable in tests.

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
