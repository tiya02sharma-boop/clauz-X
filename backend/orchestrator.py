"""
Compliance Check Orchestrator for Clauz X.

Dispatches compliance evaluation to all registered domain checkers, aggregates
their results, and applies cross-checker dependency resolution.

Design principles:
  - The orchestrator contains ZERO per-domain logic.
  - It only dispatches to checkers and aggregates results.
  - Adding a new domain = add its module to the CHECKERS list only.
    matching.py and existing checker files are never modified for this.
  - All matching logic lives in matching.py.
  - All dependency resolution lives in matching.resolve_dependent_obligations().

Usage:
    from backend.orchestrator import run_compliance_check

    obligations = run_compliance_check(profile)
    # Returns list of matched obligation dicts, each with a "_checker" field.
"""
from typing import Any

from . import matching
from .checkers import (
    gst_checker,
    labour_checker,
    msme_checker,
    state_checker,
    tds_checker,
)

# ---------------------------------------------------------------------------
# Checker registry — the ONLY place that changes when a new domain is added.
# To disable a domain, remove its entry from this list; no other file changes.
# ---------------------------------------------------------------------------

CHECKERS = [
    gst_checker,
    labour_checker,
    tds_checker,
    msme_checker,
    state_checker,
]


# ---------------------------------------------------------------------------
# Public orchestrator interface
# ---------------------------------------------------------------------------

def run_compliance_check(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run a full compliance check across all registered domain checkers.

    Steps:
      a. Call .check(profile) on every checker in the CHECKERS registry.
      b. Concatenate all returned matches into a single merged list.
      c. Pass the merged list through matching.resolve_dependent_obligations()
         to resolve any requires_flag dependencies that span checker boundaries.
      d. Return the final aggregated, dependency-resolved obligation list.

    Each obligation in the returned list includes a ``_checker`` field
    identifying which module produced it.

    Removing a checker from CHECKERS will not raise — that domain's obligations
    will simply be absent from the result (acceptance criterion 4).

    Parameters
    ----------
    profile:
        Business profile dict (must be compatible with BusinessProfile schema).

    Returns
    -------
    list[dict]
        Applicable obligations from all active checkers, dependency-resolved,
        each tagged with ``_checker``, ``_requires_flag``, and ``_derives_flag``.
        Returns an empty list if no obligations match across any checker.
    """
    all_raw_matches: list[dict[str, Any]] = []

    for checker in CHECKERS:
        checker_matches = checker.check(profile)
        all_raw_matches.extend(checker_matches)

    # Two-pass dependency resolution across all checker boundaries.
    return matching.resolve_dependent_obligations(profile, all_raw_matches)
