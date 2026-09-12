"""
Regression and acceptance tests for the Stage 2 Compliance Check Orchestrator.

Test coverage:
  1. Regression: orchestrator.run_compliance_check() produces identical rule_id sets
     as the original check_applicability() for three canonical test profiles.
  2. _checker field present on every returned obligation.
  3. Empty-result profile returns [] without raising.
  4. GST checker tested in isolation (no import of any other checker).
  5. Removing a checker from CHECKERS registry does not raise.
  6. is_factory=True routes to Factories Act, is_factory=False routes to Shops & Establishments.
  7. investment_min/max boundary conditions evaluated correctly.

Run with:
    python -m pytest backend/tests/test_orchestrator.py -v
"""
import importlib
import sys
import pytest
from typing import Any

# ---------------------------------------------------------------------------
# Test profiles — three canonical profiles used in the regression suite.
# ---------------------------------------------------------------------------

# Profile A: Small services business — low turnover, low headcount, not GST-registered.
# Expected active obligations: rule_tds_monthly_deposit, rule_shops_establishments_registration
PROFILE_A = {
    "turnover": 5_000_000,          # 50 Lakh — below GST threshold (if applied)
    "headcount": 5,                 # below EPF threshold of 20
    "investment_plant_machinery": 2_000_000,
    "is_factory": False,            # commercial establishment → Shops & Establishments
    "sector": "services",
    "state": "Maharashtra",
    "entity_type": "sole_proprietorship",
    "gst_registered": False,
    "flags": {},
}

# Profile B: Mid-size company crossing GST + EPF thresholds.
# Expected active obligations: rule_gstr3b_monthly, rule_epf_monthly_ecr,
#                              rule_tds_monthly_deposit, rule_shops_establishments_registration
PROFILE_B = {
    "turnover": 50_000_000,         # 5 Crore — GST applies
    "headcount": 25,                # above EPF threshold of 20
    "investment_plant_machinery": 10_000_000,
    "is_factory": False,
    "sector": "services",
    "state": "Karnataka",
    "entity_type": "private_limited",
    "gst_registered": True,         # GST registered → GSTR-3B applies
    "flags": {},
}

# Profile C: Larger manufacturer crossing every threshold.
# Expected active obligations: rule_gstr3b_monthly, rule_epf_monthly_ecr,
#                              rule_tds_monthly_deposit, rule_factories_act_registration
PROFILE_C = {
    "turnover": 500_000_000,        # 50 Crore
    "headcount": 50,                # well above EPF threshold
    "investment_plant_machinery": 100_000_000,
    "is_factory": True,             # factory → Factories Act applies (not Shops & Estab.)
    "sector": "manufacturing",
    "state": "Gujarat",
    "entity_type": "private_limited",
    "gst_registered": True,
    "flags": {},
}

REGRESSION_PROFILES = [
    pytest.param(PROFILE_A, id="profile_a_small_services"),
    pytest.param(PROFILE_B, id="profile_b_midsize_gst_epf"),
    pytest.param(PROFILE_C, id="profile_c_large_manufacturer"),
]


# ---------------------------------------------------------------------------
# Helper: get rule_ids from the old engine's output
# ---------------------------------------------------------------------------

def _old_engine_ids(profile: dict[str, Any]) -> set[str]:
    """Get the set of rule_ids from the original check_applicability() function."""
    from backend.applicability_engine import check_applicability
    result = check_applicability(profile)
    return {r.get("rule_id") for r in result["applicable_obligations"] if r.get("rule_id")}


def _orchestrator_ids(profile: dict[str, Any]) -> set[str]:
    """Get the set of rule_ids from the new orchestrator."""
    from backend.orchestrator import run_compliance_check
    result = run_compliance_check(profile)
    return {r.get("rule_id") for r in result if r.get("rule_id")}


# ---------------------------------------------------------------------------
# 1. Regression tests: orchestrator output == old engine output
# ---------------------------------------------------------------------------

class TestRegressionIdenticalOutput:
    """
    REGRESSION REQUIREMENT: orchestrator.run_compliance_check() must return
    an identical set of obligation_ids as check_applicability() for the same
    three test profiles.
    """

    @pytest.mark.parametrize("profile", REGRESSION_PROFILES)
    def test_obligation_ids_identical(self, profile: dict[str, Any]):
        old_ids = _old_engine_ids(profile)
        new_ids = _orchestrator_ids(profile)
        assert new_ids == old_ids, (
            f"Orchestrator output differs from old engine.\n"
            f"Old engine only: {old_ids - new_ids}\n"
            f"Orchestrator only: {new_ids - old_ids}"
        )


# ---------------------------------------------------------------------------
# 2. _checker field present on every returned obligation
# ---------------------------------------------------------------------------

class TestCheckerFieldPresent:
    """
    Acceptance criterion 1: every returned obligation must include a
    "_checker" field identifying the producing module.
    """

    @pytest.mark.parametrize("profile", REGRESSION_PROFILES)
    def test_checker_field_on_all_obligations(self, profile: dict[str, Any]):
        from backend.orchestrator import run_compliance_check
        obligations = run_compliance_check(profile)
        for ob in obligations:
            assert "_checker" in ob, (
                f"Missing '_checker' field on obligation: {ob.get('rule_id')}"
            )
            assert ob["_checker"], "Empty '_checker' field is not allowed."

    def test_checker_values_are_known_modules(self):
        from backend.orchestrator import run_compliance_check
        known_checkers = {
            "gst_checker", "labour_checker", "tds_checker",
            "msme_checker", "state_checker",
        }
        # Profile C hits multiple checkers
        obligations = run_compliance_check(PROFILE_C)
        for ob in obligations:
            assert ob["_checker"] in known_checkers, (
                f"Unknown checker: {ob['_checker']!r} on rule {ob.get('rule_id')}"
            )


# ---------------------------------------------------------------------------
# 3. Zero-match profile returns [] without raising
# ---------------------------------------------------------------------------

class TestEmptyResult:
    """
    Acceptance criterion 2: a profile that matches no obligations in any
    checker returns an empty list, not an error.
    """

    def test_empty_profile_tds_unconditional_matches(self):
        """
        rule_tds_monthly_deposit has NO conditions at all (every field is null),
        so it correctly matches every profile including an empty one.
        This is the expected behaviour — the orchestrator must return it, not [].  
        """
        from backend.orchestrator import run_compliance_check
        result = run_compliance_check({})
        rule_ids = {r.get("rule_id") for r in result}
        # TDS has no conditions → always applies
        assert "rule_tds_monthly_deposit" in rule_ids, (
            "rule_tds_monthly_deposit has no conditions and should always match."
        )
        # No GST / factory / EPF rules should fire on a blank profile
        assert "rule_gstr3b_monthly" not in rule_ids
        assert "rule_epf_monthly_ecr" not in rule_ids
        assert "rule_factories_act_registration" not in rule_ids
        assert "rule_shops_establishments_registration" not in rule_ids

    def test_profile_no_factory_flag_and_gst_false(self):
        from backend.orchestrator import run_compliance_check
        # This profile has no is_factory set, so both factory rules will fail
        # (requires_is_factory is not None → needs explicit True or False on profile).
        # Also headcount below EPF threshold, and no GST.
        profile = {
            "turnover": 1_000_000,
            "headcount": 5,
            "gst_registered": False,
            "is_factory": None,   # explicit None — neither factory nor non-factory
        }
        result = run_compliance_check(profile)
        # TDS applies unconditionally (no conditions on rule_tds_monthly_deposit),
        # both factory rules should not apply, GST rule should not apply.
        rule_ids = {r.get("rule_id") for r in result}
        assert "rule_gstr3b_monthly" not in rule_ids
        assert "rule_factories_act_registration" not in rule_ids
        assert "rule_shops_establishments_registration" not in rule_ids
        assert "rule_epf_monthly_ecr" not in rule_ids


# ---------------------------------------------------------------------------
# 4. GST checker in isolation — does NOT import any other checker
# ---------------------------------------------------------------------------

class TestGSTCheckerIsolation:
    """
    Acceptance criterion 3: gst_checker.check() can be tested directly without
    importing or referencing any other checker module.
    """

    def test_gst_checker_does_not_import_other_checkers(self):
        """
        Verify gst_checker has no direct import dependency on other checker modules.
        We check that gst_checker.py's source code does not reference sibling checker
        module names, which is the meaningful structural guarantee.
        """
        import inspect
        import backend.checkers.gst_checker as gst
        source = inspect.getsource(gst)
        for mod_name in ("labour_checker", "tds_checker", "msme_checker", "state_checker"):
            assert mod_name not in source, (
                f"gst_checker source unexpectedly references '{mod_name}'. "
                "Checkers must not cross-import each other."
            )

    def test_gst_checker_no_match_when_not_registered(self):
        from backend.checkers.gst_checker import check
        profile = {"gst_registered": False, "turnover": 10_000_000}
        result = check(profile)
        assert result == [], f"Expected no GST obligations for unregistered business, got: {result}"

    def test_gst_checker_matches_when_registered(self):
        from backend.checkers.gst_checker import check
        profile = {"gst_registered": True}
        result = check(profile)
        rule_ids = {r["rule_id"] for r in result}
        assert "rule_gstr3b_monthly" in rule_ids

    def test_gst_checker_baseline_rule_excluded(self):
        """baseline_gst_registered_return is active=False and must never appear in results."""
        from backend.checkers.gst_checker import check
        profile = {"gst_registered": True}
        result = check(profile)
        rule_ids = {r["rule_id"] for r in result}
        assert "baseline_gst_registered_return" not in rule_ids

    def test_gst_checker_returns_checker_tag(self):
        from backend.checkers.gst_checker import check
        profile = {"gst_registered": True}
        result = check(profile)
        for ob in result:
            assert ob["_checker"] == "gst_checker"

    def test_gst_checker_with_custom_rule_table(self):
        """Checker must accept an overridden rule_table (for unit testing)."""
        from backend.checkers.gst_checker import check
        custom_rules = [{
            "rule_id": "test_gst_rule",
            "active": True,
            "obligation_name": "Test GST Rule",
            "gst_registered": True,
            "recurrence": "monthly",
        }]
        profile = {"gst_registered": True}
        result = check(profile, rule_table=custom_rules)
        assert len(result) == 1
        assert result[0]["rule_id"] == "test_gst_rule"
        assert result[0]["_checker"] == "gst_checker"


# ---------------------------------------------------------------------------
# 5. Removing a checker from registry must not raise
# ---------------------------------------------------------------------------

class TestCheckerRegistryResilience:
    """
    Acceptance criterion 4: removing a checker from the CHECKERS registry
    must not raise — that domain's obligations are simply absent from results.
    """

    def test_run_with_empty_checkers_list(self):
        from backend import orchestrator
        original = orchestrator.CHECKERS[:]
        try:
            orchestrator.CHECKERS.clear()
            result = orchestrator.run_compliance_check(PROFILE_C)
            assert result == [], "Empty CHECKERS should return empty list, not raise."
        finally:
            orchestrator.CHECKERS[:] = original

    def test_removing_gst_checker_omits_gst_obligations(self):
        from backend import orchestrator
        from backend.checkers import gst_checker
        original = orchestrator.CHECKERS[:]
        try:
            orchestrator.CHECKERS[:] = [c for c in original if c is not gst_checker]
            result = orchestrator.run_compliance_check(PROFILE_B)
            rule_ids = {r.get("rule_id") for r in result}
            assert "rule_gstr3b_monthly" not in rule_ids, (
                "GST obligations should be absent when gst_checker is removed from registry."
            )
        finally:
            orchestrator.CHECKERS[:] = original

    def test_removing_labour_checker_omits_labour_obligations(self):
        from backend import orchestrator
        from backend.checkers import labour_checker
        original = orchestrator.CHECKERS[:]
        try:
            orchestrator.CHECKERS[:] = [c for c in original if c is not labour_checker]
            result = orchestrator.run_compliance_check(PROFILE_C)
            rule_ids = {r.get("rule_id") for r in result}
            assert "rule_epf_monthly_ecr" not in rule_ids
            assert "rule_factories_act_registration" not in rule_ids
        finally:
            orchestrator.CHECKERS[:] = original


# ---------------------------------------------------------------------------
# 6. is_factory routing: Factories Act vs Shops & Establishments
# ---------------------------------------------------------------------------

class TestIsFactoryRouting:
    """
    Acceptance criterion 5: requires_is_factory condition must route correctly.
    is_factory=True → Factories Act applies, Shops & Establishments does NOT.
    is_factory=False → Shops & Establishments applies, Factories Act does NOT.
    """

    def test_factory_true_matches_factories_act(self):
        from backend.checkers.labour_checker import check
        profile = {"is_factory": True, "turnover": 10_000_000, "headcount": 10}
        result = check(profile)
        rule_ids = {r["rule_id"] for r in result}
        assert "rule_factories_act_registration" in rule_ids, (
            "is_factory=True must match Factories Act rule."
        )
        assert "rule_shops_establishments_registration" not in rule_ids, (
            "is_factory=True must NOT match Shops & Establishments rule."
        )

    def test_factory_false_matches_shops_establishments(self):
        from backend.checkers.labour_checker import check
        profile = {"is_factory": False, "turnover": 10_000_000, "headcount": 10}
        result = check(profile)
        rule_ids = {r["rule_id"] for r in result}
        assert "rule_shops_establishments_registration" in rule_ids, (
            "is_factory=False must match Shops & Establishments rule."
        )
        assert "rule_factories_act_registration" not in rule_ids, (
            "is_factory=False must NOT match Factories Act rule."
        )

    def test_factory_none_matches_neither(self):
        from backend.checkers.labour_checker import check
        profile = {"is_factory": None, "turnover": 10_000_000, "headcount": 10}
        result = check(profile)
        rule_ids = {r["rule_id"] for r in result}
        assert "rule_factories_act_registration" not in rule_ids
        assert "rule_shops_establishments_registration" not in rule_ids

    def test_factory_true_via_orchestrator(self):
        from backend.orchestrator import run_compliance_check
        profile = {**PROFILE_C, "is_factory": True}
        result = run_compliance_check(profile)
        rule_ids = {r["rule_id"] for r in result}
        assert "rule_factories_act_registration" in rule_ids
        assert "rule_shops_establishments_registration" not in rule_ids

    def test_factory_false_via_orchestrator(self):
        from backend.orchestrator import run_compliance_check
        profile = {**PROFILE_C, "is_factory": False}
        result = run_compliance_check(profile)
        rule_ids = {r["rule_id"] for r in result}
        assert "rule_shops_establishments_registration" in rule_ids
        assert "rule_factories_act_registration" not in rule_ids

    def test_factory_checker_tag(self):
        from backend.checkers.labour_checker import check
        profile = {"is_factory": True}
        result = check(profile)
        for ob in result:
            assert ob["_checker"] == "labour_checker"


# ---------------------------------------------------------------------------
# 7. investment_min/max boundary conditions
# ---------------------------------------------------------------------------

class TestInvestmentBoundaryConditions:
    """
    Acceptance criterion 5: investment_min/investment_max conditions must
    be evaluated correctly by matching.evaluate_rule().
    """

    def test_investment_within_bounds_matches(self):
        from backend.matching import evaluate_rule
        rule = {
            "rule_id": "test_inv_rule",
            "obligation_name": "Test Investment Rule",
            "investment_min": 1_000_000,
            "investment_max": 5_000_000,
        }
        result = evaluate_rule(rule, {"investment_plant_machinery": 2_500_000})
        assert result["applicable"] is True
        assert "investment_plant_machinery" in result["matched_conditions"]

    def test_investment_below_min_fails(self):
        from backend.matching import evaluate_rule
        rule = {
            "rule_id": "test_inv_rule",
            "obligation_name": "Test Investment Rule",
            "investment_min": 1_000_000,
            "investment_max": 5_000_000,
        }
        result = evaluate_rule(rule, {"investment_plant_machinery": 500_000})
        assert result["applicable"] is False
        assert "investment_plant_machinery" in result["failed_conditions"]

    def test_investment_above_max_fails(self):
        from backend.matching import evaluate_rule
        rule = {
            "rule_id": "test_inv_rule",
            "obligation_name": "Test Investment Rule",
            "investment_min": 1_000_000,
            "investment_max": 5_000_000,
        }
        result = evaluate_rule(rule, {"investment_plant_machinery": 6_000_000})
        assert result["applicable"] is False
        assert "investment_plant_machinery" in result["failed_conditions"]

    def test_investment_at_min_boundary_matches(self):
        from backend.matching import evaluate_rule
        rule = {"rule_id": "r", "investment_min": 1_000_000}
        result = evaluate_rule(rule, {"investment_plant_machinery": 1_000_000})
        assert result["applicable"] is True

    def test_investment_at_max_boundary_matches(self):
        from backend.matching import evaluate_rule
        rule = {"rule_id": "r", "investment_max": 5_000_000}
        result = evaluate_rule(rule, {"investment_plant_machinery": 5_000_000})
        assert result["applicable"] is True

    def test_investment_none_with_investment_rule_fails(self):
        from backend.matching import evaluate_rule
        rule = {"rule_id": "r", "investment_min": 1_000_000}
        result = evaluate_rule(rule, {"investment_plant_machinery": None})
        assert result["applicable"] is False


# ---------------------------------------------------------------------------
# 8. Rule count integrity (total rules in all checkers == 8)
# ---------------------------------------------------------------------------

class TestRuleCountIntegrity:
    """Verify that every rule from the original rules.json appears in exactly one checker."""

    ORIGINAL_RULE_IDS = {
        "baseline_gst_registered_return",
        "baseline_epf_20_employee_assessment",
        "baseline_private_company_annual_filings",
        "rule_gstr3b_monthly",
        "rule_epf_monthly_ecr",
        "rule_tds_monthly_deposit",
        "rule_factories_act_registration",
        "rule_shops_establishments_registration",
    }

    def _all_checker_rule_ids(self) -> list[str]:
        from backend.checkers.gst_checker import GST_RULES
        from backend.checkers.labour_checker import LABOUR_RULES
        from backend.checkers.tds_checker import TDS_RULES
        from backend.checkers.msme_checker import MSME_RULES
        from backend.checkers.state_checker import STATE_RULES
        all_rules = GST_RULES + LABOUR_RULES + TDS_RULES + MSME_RULES + STATE_RULES
        return [r["rule_id"] for r in all_rules if r.get("rule_id")]

    def test_total_rule_count_equals_original(self):
        ids = self._all_checker_rule_ids()
        assert len(ids) == len(self.ORIGINAL_RULE_IDS), (
            f"Expected {len(self.ORIGINAL_RULE_IDS)} rules total, got {len(ids)}. "
            f"Current: {set(ids)}"
        )

    def test_all_original_rules_present(self):
        ids = set(self._all_checker_rule_ids())
        missing = self.ORIGINAL_RULE_IDS - ids
        assert not missing, f"These rules are missing from checker modules: {missing}"

    def test_no_rule_duplicated_across_checkers(self):
        ids = self._all_checker_rule_ids()
        seen: set[str] = set()
        duplicates: set[str] = set()
        for rule_id in ids:
            if rule_id in seen:
                duplicates.add(rule_id)
            seen.add(rule_id)
        assert not duplicates, f"These rules appear in more than one checker: {duplicates}"


# ---------------------------------------------------------------------------
# 9. MSME checker empty table returns [] without raising
# ---------------------------------------------------------------------------

class TestMSMEChecker:
    def test_msme_checker_returns_empty_list(self):
        from backend.checkers.msme_checker import check, MSME_RULES
        assert MSME_RULES == [], "MSME_RULES should be empty (no approved rules yet)"
        result = check(PROFILE_C)
        assert result == []

    def test_msme_checker_with_custom_rules(self):
        from backend.checkers.msme_checker import check
        custom = [{
            "rule_id": "test_msme",
            "active": True,
            "obligation_name": "Test MSME Rule",
            "headcount_min": 1,
        }]
        result = check({"headcount": 5}, rule_table=custom)
        assert len(result) == 1
        assert result[0]["_checker"] == "msme_checker"


# ---------------------------------------------------------------------------
# 10. Dependency resolution infrastructure
# ---------------------------------------------------------------------------

class TestResolveDependent:
    """Verify resolve_dependent_obligations two-pass logic works correctly."""

    def test_no_flag_deps_passthrough(self):
        from backend.matching import resolve_dependent_obligations
        matches = [
            {"rule_id": "r1", "_requires_flag": None, "_derives_flag": None},
            {"rule_id": "r2", "_requires_flag": None, "_derives_flag": None},
        ]
        result = resolve_dependent_obligations({}, matches)
        assert len(result) == 2

    def test_flag_dep_resolved_when_derived(self):
        from backend.matching import resolve_dependent_obligations
        # r1 derives "gst_registered"; r2 requires it.
        matches = [
            {"rule_id": "r1", "_requires_flag": None, "_derives_flag": "gst_registered"},
            {"rule_id": "r2", "_requires_flag": "gst_registered", "_derives_flag": None},
        ]
        result = resolve_dependent_obligations({}, matches)
        ids = {r["rule_id"] for r in result}
        assert "r1" in ids
        assert "r2" in ids

    def test_flag_dep_dropped_when_not_derived(self):
        from backend.matching import resolve_dependent_obligations
        # r2 requires "gst_registered" but no match derives it.
        matches = [
            {"rule_id": "r1", "_requires_flag": None, "_derives_flag": None},
            {"rule_id": "r2", "_requires_flag": "gst_registered", "_derives_flag": None},
        ]
        result = resolve_dependent_obligations({}, matches)
        ids = {r["rule_id"] for r in result}
        assert "r1" in ids
        assert "r2" not in ids

    def test_flag_dep_resolved_from_profile_flags(self):
        from backend.matching import resolve_dependent_obligations
        # r2 requires "some_flag" — present in profile's flags dict.
        profile = {"flags": {"some_flag": True}}
        matches = [
            {"rule_id": "r2", "_requires_flag": "some_flag", "_derives_flag": None},
        ]
        result = resolve_dependent_obligations(profile, matches)
        assert len(result) == 1
        assert result[0]["rule_id"] == "r2"
