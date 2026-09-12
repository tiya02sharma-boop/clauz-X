"""Auditable document verification over obligations selected by the rules engine."""
import os
from datetime import date
from pathlib import Path
from typing import Any

from . import config
from .applicability_engine import check_applicability
from .embeddings import embed_texts
from .llm_client import structured
from .models import (
    BusinessProfile, ComplianceCheckReport, ComplianceVerificationResult,
    DocumentFileValidation, RegulatoryRequirement,
)
from .pdf_extractor import extract_pdf_text

# Tunable semantic similarity threshold for document pre-filtering
DOC_SIMILARITY_THRESHOLD = float(os.getenv("DOC_VERIFICATION_SIMILARITY_THRESHOLD", "0.50"))

_PROMPTS = Path(__file__).parent / "prompts"
FILE_VALIDATION_PROMPT = (_PROMPTS / "document_file_validation_prompt.txt").read_text()
DOCUMENT_VERIFICATION_PROMPT = (_PROMPTS / "document_verification_prompt.txt").read_text()


def _requirements(profile: BusinessProfile) -> list[RegulatoryRequirement]:
    applicable = check_applicability(profile, rules_path=config.RULES_PATH).get("applicable_obligations", [])
    return [RegulatoryRequirement(
        obligation_id=rule.get("rule_id") or rule.get("obligation_id"),
        title=rule.get("obligation_name") or "Statutory Compliance Obligation",
        description=rule.get("description"), required_evidence=rule.get("required_evidence") or [],
        legal_source=rule.get("source_citation") or rule.get("source_url"),
        conditions=rule.get("conditions") or [],
    ) for rule in applicable if rule.get("rule_id") or rule.get("obligation_id")]


def evaluate_condition(condition: Any, profile: BusinessProfile) -> tuple[bool | None, str | None]:
    """Evaluate structured catalog conditions; defer prose/unknown conditions to a human."""
    if not isinstance(condition, dict):
        return None, str(condition)
    field, operator, expected = condition.get("field"), str(condition.get("op", "equals")).lower(), condition.get("value")
    if not field or field not in type(profile).model_fields:
        return None, f"Condition field '{field}' does not exist on BusinessProfile"
    actual = getattr(profile, field)
    try:
        if operator in ("equals", "==", "eq"):
            matched = actual.strip().lower() == expected.strip().lower() if isinstance(actual, str) and isinstance(expected, str) else actual == expected
        elif operator in ("not_equals", "!=", "neq"):
            matched = actual.strip().lower() != expected.strip().lower() if isinstance(actual, str) and isinstance(expected, str) else actual != expected
        elif operator in ("in", "contains_value"):
            matched = actual in expected if isinstance(expected, (list, tuple, set)) else str(actual).lower() in str(expected).lower()
        elif operator in (">", "greater_than", "gt"): matched = actual is not None and actual > expected
        elif operator in (">=", "greater_than_or_equal", "gte"): matched = actual is not None and actual >= expected
        elif operator in ("<", "less_than", "lt"): matched = actual is not None and actual < expected
        elif operator in ("<=", "less_than_or_equal", "lte"): matched = actual is not None and actual <= expected
        elif operator in ("is_null", "none"): matched = actual is None
        elif operator in ("is_not_null", "not_none"): matched = actual is not None
        else: return None, f"Unsupported condition operator '{operator}'"
    except (TypeError, ValueError):
        return None, f"Condition '{field}' could not be evaluated"
    return matched, None if matched else f"{field} is '{actual}', expected '{expected}'"


def validate_uploaded_document(document_text: str | None = None, file_path: str | Path | None = None, verification_date: str | None = None) -> DocumentFileValidation:
    method = "direct"
    if document_text is None and file_path is not None:
        extracted = extract_pdf_text(file_path)
        method = extracted.get("extraction_method", method)
        if extracted.get("extraction_failed"):
            return DocumentFileValidation(reason=extracted.get("error") or "The uploaded file could not be read.", apparent_status="invalid", issues=["unreadable_file"], extraction_method=method)
        document_text = extracted.get("text", "")
    text = (document_text or "").strip()
    if not text:
        return DocumentFileValidation(reason="No document text was supplied.", apparent_status="invalid", issues=["empty_document"], extraction_method=method)
    result = structured(FILE_VALIDATION_PROMPT.format(document_text=text, verification_date=verification_date or date.today().isoformat()), DocumentFileValidation)
    result.extraction_method = result.extraction_method or method
    return result


def compute_document_similarity(obligation_text: str, document_text: str) -> float:
    """Compute cosine similarity between obligation description and document text."""
    if not obligation_text.strip() or not document_text.strip():
        return 0.0
    vecs = embed_texts([obligation_text, document_text], task_instruction=None)
    if len(vecs) < 2:
        return 0.0
    import numpy as np
    v1, v2 = np.array(vecs[0]), np.array(vecs[1])
    norm1, norm2 = float(np.linalg.norm(v1)), float(np.linalg.norm(v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def verify_document(requirement: RegulatoryRequirement, document_text: str, profile: BusinessProfile, validation: DocumentFileValidation) -> ComplianceVerificationResult:
    if validation.apparent_status == "invalid":
        return ComplianceVerificationResult(obligation_id=requirement.obligation_id, verdict="missing", reason=validation.reason, document_validation_status="invalid", legal_source=requirement.legal_source, extraction_method=validation.extraction_method)
    if validation.apparent_status == "needs_review":
        return ComplianceVerificationResult(obligation_id=requirement.obligation_id, verdict="needs_review", reason=validation.reason, evidence=validation.evidence, document_validation_status="needs_review", legal_source=requirement.legal_source, extraction_method=validation.extraction_method)

    # Pre-filter similarity check before expensive LLM verification call
    obligation_desc = f"{requirement.title} {requirement.description or ''} {' '.join(requirement.required_evidence or [])}".strip()
    similarity = compute_document_similarity(obligation_desc, document_text)
    if similarity < DOC_SIMILARITY_THRESHOLD:
        return ComplianceVerificationResult(
            obligation_id=requirement.obligation_id,
            verdict="needs_review",
            reason="Document content does not appear related to this obligation",
            evidence=f"Semantic similarity score ({similarity:.3f}) fell below verification threshold ({DOC_SIMILARITY_THRESHOLD})",
            document_validation_status="usable",
            legal_source=requirement.legal_source,
            extraction_method=validation.extraction_method,
        )

    result = structured(DOCUMENT_VERIFICATION_PROMPT.format(obligation_json=requirement.model_dump_json(), document_text=document_text, business_profile_json=profile.model_dump_json()), ComplianceVerificationResult)
    return ComplianceVerificationResult(obligation_id=requirement.obligation_id, verdict=result.verdict, reason=result.reason, evidence=result.evidence, document_validation_status="usable", legal_source=requirement.legal_source, extraction_method=validation.extraction_method)


def _score(results: list[ComplianceVerificationResult], total: int) -> int:
    return 100 if not total else round(100 * sum(item.verdict == "pass" for item in results) / total)


def _risk(score: int) -> str:
    return "low" if score >= 80 else "medium" if score >= 50 else "high"


def _coverage(requirements: list[RegulatoryRequirement]) -> str:
    titles = ", ".join(item.title for item in requirements)
    return f"Checked against {len(requirements)} obligation{'s' if len(requirements) != 1 else ''} currently in ClauzX's verified rule catalog" + (f" ({titles})." if titles else ".")


def run_compliance_check(business_profile: BusinessProfile | dict[str, Any], uploaded_docs: dict[str, str] | None = None, verification_date: str | None = None) -> ComplianceCheckReport:
    profile = business_profile if isinstance(business_profile, BusinessProfile) else BusinessProfile.model_validate(business_profile)
    requirements, docs, results, review, conflicts = _requirements(profile), uploaded_docs or {}, [], [], []
    for requirement in requirements:
        evaluations = [evaluate_condition(condition, profile) for condition in requirement.conditions]
        unresolved = [reason for met, reason in evaluations if met is None and reason]
        failed = [reason for met, reason in evaluations if met is False and reason]
        if unresolved or failed:
            reason = "Conditional requirements need review: " + "; ".join(unresolved or failed)
            results.append(ComplianceVerificationResult(obligation_id=requirement.obligation_id, verdict="needs_review", reason=reason, legal_source=requirement.legal_source)); review.append(requirement.obligation_id); continue
        text = docs.get(requirement.obligation_id, "")
        if not str(text).strip():
            results.append(ComplianceVerificationResult(obligation_id=requirement.obligation_id, verdict="missing", reason="No document uploaded for this obligation.", legal_source=requirement.legal_source)); continue
        verified = verify_document(requirement, str(text), profile, validate_uploaded_document(str(text), verification_date=verification_date))
        results.append(verified)
        if verified.verdict == "needs_review": review.append(requirement.obligation_id)
        if verified.verdict == "fail": conflicts.append(f"{requirement.obligation_id}: {verified.reason}")
    score = _score(results, len(requirements))
    return ComplianceCheckReport(business_id=profile.business_id, business_name=profile.business_name, applicable_requirements=requirements, results=results, compliance_score=score, risk_level=_risk(score), human_verification_required=review, conflicts_detected=conflicts, coverage_note=_coverage(requirements))


def reverify_obligation(obligation_id: str, business_profile: BusinessProfile | dict[str, Any], document_text: str, previous_report: ComplianceCheckReport | dict[str, Any] | None = None, verification_date: str | None = None) -> ComplianceCheckReport:
    profile = business_profile if isinstance(business_profile, BusinessProfile) else BusinessProfile.model_validate(business_profile)
    prior = previous_report if isinstance(previous_report, ComplianceCheckReport) else ComplianceCheckReport.model_validate(previous_report) if previous_report else None
    requirements = _requirements(profile)
    target = next((item for item in requirements if item.obligation_id == obligation_id), None)
    if not target:
        return run_compliance_check(profile, {}, verification_date)
    replacement = verify_document(target, document_text, profile, validate_uploaded_document(document_text, verification_date=verification_date))
    old_results = {item.obligation_id: item for item in (prior.results if prior else [])}
    results = []
    for requirement in requirements:
        results.append(replacement if requirement.obligation_id == obligation_id else old_results.get(
            requirement.obligation_id,
            ComplianceVerificationResult(obligation_id=requirement.obligation_id, verdict="missing", reason="No document uploaded for this obligation.", legal_source=requirement.legal_source),
        ))
    score = _score(results, len(requirements))
    return ComplianceCheckReport(
        business_id=profile.business_id, business_name=profile.business_name,
        applicable_requirements=requirements, results=results, compliance_score=score,
        risk_level=_risk(score),
        human_verification_required=[item.obligation_id for item in results if item.verdict == "needs_review"],
        conflicts_detected=[f"{item.obligation_id}: {item.reason}" for item in results if item.verdict == "fail"],
        coverage_note=_coverage(requirements),
    )
