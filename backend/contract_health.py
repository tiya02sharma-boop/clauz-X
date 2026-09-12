"""Deterministic and Gemini AI-powered health checks for Indian commercial contracts.

Provides first-pass screening and detailed legal clause explanations,
risk assessments, executive summaries, and drafting guidance under Indian law.
"""
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from .config import CONTRACT_LEGAL_CITATIONS_PATH, GEMINI_MODEL
from .storage import load

logger = logging.getLogger(__name__)

DO_NOT_MERGE_REPLACEMENTS = [
    (re.compile(r'\breverse[- ]charge\s+tds\s+deduction\s+obligations\b', re.IGNORECASE), "GST reverse-charge mechanisms and separate Income Tax TDS deduction obligations"),
    (re.compile(r'\breverse[- ]charge\s+tds\s+deduction\b', re.IGNORECASE), "GST reverse-charge mechanisms and Income Tax TDS deduction"),
    (re.compile(r'\breverse[- ]charge\s+tds\b', re.IGNORECASE), "GST reverse charge and Income Tax TDS"),
    (re.compile(r'\bgst\s+tds\s+credit\b', re.IGNORECASE), "GST input tax credit and TDS credit certificate"),
    (re.compile(r'\bstatutory\s+indemnity\s+penalty\b', re.IGNORECASE), "statutory penalty provisions and contractual indemnity"),
    (re.compile(r'\bmsme\s+gst\s+registration\b', re.IGNORECASE), "MSME registration and GST registration"),
]


def load_citations_reference() -> dict[str, Any]:
    if CONTRACT_LEGAL_CITATIONS_PATH.exists():
        try:
            return json.loads(CONTRACT_LEGAL_CITATIONS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "statutory_citations": {},
        "allowed_statutory_numbers": [1872, 1948, 1952, 1961, 1996, 2013, 2017, 2023, 2025, 6, 7, 8, 9, 30, 33, 39, 72, 73, 124, 194, 250]
    }


def sanitize_text_and_check_figures(
    text: str,
    source_text: str,
    evidence: str | None = None,
    allowed_numbers: set[int] | None = None
) -> tuple[str, bool]:
    """
    Sanitize text against do-not-merge pairs and validate numerals/percentages against
    source document text and allowed reference numbers.

    Returns (sanitized_text, contains_unfounded_numeral).
    """
    if not text:
        return text, False

    sanitized = text
    # 1. Apply Do-Not-Merge Substitutions
    for pattern, replacement in DO_NOT_MERGE_REPLACEMENTS:
        sanitized = pattern.sub(replacement, sanitized)

    if allowed_numbers is None:
        citations = load_citations_reference()
        allowed_numbers = set(citations.get("allowed_statutory_numbers", []))

    combined_source = (source_text or "") + " " + (evidence or "")

    unfounded_found = False

    # 2. Check for percentage figures (e.g. 18%, 18 percent)
    pct_matches = list(re.finditer(r'\b(\d+(?:\.\d+)?)\s*(?:%|percent)\b', sanitized, flags=re.IGNORECASE))
    for match in reversed(pct_matches):
        pct_str = match.group(0)
        num_str = match.group(1)
        try:
            num_val = float(num_str) if '.' in num_str else int(num_str)
        except ValueError:
            continue

        if (pct_str.lower() not in combined_source.lower()) and (num_str not in combined_source) and (num_val not in allowed_numbers):
            unfounded_found = True
            start, end = match.span()
            after_text = sanitized[end:end+10]
            if re.match(r'^\s*(?:gst|tax)', after_text, flags=re.IGNORECASE):
                sub_end = end + len(re.match(r'^\s*(?:gst|tax)', after_text, flags=re.IGNORECASE).group(0))
                sanitized = sanitized[:start] + "GST (rate not specified in the reviewed clause)" + sanitized[sub_end:]
            else:
                sanitized = sanitized[:start] + "(rate not specified in the reviewed clause)" + sanitized[end:]

    # 3. Check for standalone numerals that are unfounded
    num_matches = list(re.finditer(r'\b\d+(?:\.\d+)?\b', sanitized))
    for match in num_matches:
        num_str = match.group(0)
        try:
            val = float(num_str) if '.' in num_str else int(num_str)
        except ValueError:
            continue

        if (num_str in combined_source) or (val in allowed_numbers):
            continue

        unfounded_found = True

    return sanitized, unfounded_found


def _template(
    check_id: str, title: str, required: bool, groups: list[list[str]], description: str
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "title": title,
        "required": required,
        "keyword_groups": groups,
        "description": description,
    }


# The 14 ClauseGuard / Clauz X standard clause templates for Indian commercial contracts.
CONTRACT_TEMPLATES = [
    _template("party_authority", "Parties and signing authority", True,
              [["party", "parties", "company"], ["authorised", "authorized", "signature", "signatory"]],
              "Names the parties and indicates who can bind them."),
    _template("scope_payment_gst", "Scope, payment and GST/TDS", True,
              [["scope", "services", "deliverables"], ["payment", "invoice", "fees"], ["gst", "tax", "tds"]],
              "Defines work, commercial terms, and Indian tax treatment."),
    _template("indemnity", "Indemnity", True,
              [["indemn"], ["breach", "negligence", "claim"], ["legal fees", "attorney", "costs"]],
              "Checks for meaningful indemnity coverage and claim costs."),
    _template("liability_cap", "Limitation of liability", True,
              [["liabilit"], ["cap", "limited", "fees paid"], ["consequential", "indirect", "special damages"]],
              "Looks for a monetary cap and excluded consequential loss."),
    _template("termination", "Termination", True,
              [["terminat"], ["notice", "30 days", "thirty days"], ["cure", "breach"]],
              "Looks for termination rights, notice, and a breach cure process."),
    _template("confidentiality", "Confidentiality", True,
              [["confidential"], ["disclos", "use"], ["surviv", "three years", "3 years"]],
              "Checks confidentiality use restrictions and survival."),
    _template("governing_law", "Indian governing law and disputes", True,
              [["governing law", "laws of india", "indian law"], ["court", "jurisdiction", "arbitration"], ["india", "mumbai", "delhi", "bengaluru", "bangalore", "chennai", "hyderabad"]],
              "Sets Indian law and a court or arbitration forum."),
    _template("data_protection_india", "India data protection and security", True,
              [["personal data", "data protection", "dpdp", "privacy"], ["security", "encrypt", "safeguard"], ["breach", "incident"], ["delete", "deletion", "return"]],
              "Screens for DPDP-aligned data handling, security, incident, and deletion terms."),
    _template("ip_assignment", "IP ownership and assignment", False,
              [["intellectual property", "ip", "work product"], ["own", "assign", "licence", "license"]],
              "Clarifies ownership of deliverables and pre-existing IP."),
    _template("force_majeure", "Force majeure", False,
              [["force majeure", "beyond reasonable control"], ["notice", "notify"], ["terminat", "60 days", "sixty days"]],
              "Covers exceptional events, notice, and long-stop termination."),
    _template("warranties_remedies", "Warranties and remedies", True,
              [["warrant"], ["remed", "repair", "replace", "service credit"]],
              "Sets performance promises and what happens if they are missed."),
    _template("assignment_subcontracting", "Assignment and subcontracting", True,
              [["assign"], ["consent", "approval"], ["subcontract", "sub-processor", "subprocessor"]],
              "Controls transfer of the deal and use of subcontractors."),
    _template("notices_precedence", "Notices and document precedence", False,
              [["notice"], ["address", "email"], ["entire agreement", "order of precedence"]],
              "Makes formal notices and conflicting documents manageable."),
    _template("anti_bribery", "Compliance and anti-bribery", False,
              [["anti-bribery", "anti bribery", "corruption"], ["applicable law", "compliance"]],
              "Flags whether basic legal-compliance commitments are present."),
]


class GeminiClauseAnalysis(BaseModel):
    check_id: str = Field(description="One of the standard 14 check IDs")
    status: str = Field(description="'compliant', 'needs_review', or 'missing_high_risk'")
    evidence: str | None = Field(default=None, description="Verbatim quote or relevant excerpt if present, or null")
    explanation: str = Field(description="Clear explanation in plain English of the clause's effect or why absence is a concern")
    risk_assessment: str = Field(description="Specific legal and business exposure under Indian commercial laws (e.g. Contract Act, DPDP, GST)")
    suggested_amendment: str = Field(description="Actionable drafting guidance or amendment proposal to negotiate")


class GeminiContractReport(BaseModel):
    executive_summary: str = Field(description="2-3 paragraph executive summary of agreement, parties, commercial purpose, and health status")
    overall_risk: str = Field(description="'low', 'medium', or 'high'")
    health_score: int = Field(description="Contract health score 0-100 based on standard Indian commercial contracting")
    key_risks: list[str] = Field(description="Top 3-5 critical risks, missing protections, or one-sided terms")
    negotiation_recommendations: list[str] = Field(description="Top 3-5 tactical negotiation priorities before execution")
    clauses: list[GeminiClauseAnalysis] = Field(description="Detailed analysis for the standard contract checks")


def _snippet(text: str, keyword: str) -> str | None:
    match = re.search(re.escape(keyword), text, flags=re.IGNORECASE)
    if not match:
        return None
    start = max(0, text.rfind(".", 0, match.start()) + 1)
    end = text.find(".", match.end())
    excerpt = text[start:end if end != -1 else min(len(text), match.end() + 220)].strip()
    return (excerpt[:280] + "…") if len(excerpt) > 280 else excerpt


def _run_template(template: dict[str, Any], text: str) -> dict[str, Any]:
    normalized = text.lower()
    matches: list[str] = []
    missing: list[str] = []
    evidence: str | None = None
    for index, alternatives in enumerate(template["keyword_groups"], start=1):
        hit = next((term for term in alternatives if term.lower() in normalized), None)
        if hit:
            matches.append(hit)
            evidence = evidence or _snippet(text, hit)
        else:
            missing.append(f"requirement {index}")

    if not missing:
        status = "compliant"
        reason = "The contract contains the expected signals for this check."
    elif matches:
        status = "needs_review"
        reason = f"Found {', '.join(matches)}, but {', '.join(missing)} needs a human review."
    elif template["required"]:
        status = "missing_high_risk"
        reason = "No matching clause was found for this required check."
    else:
        status = "needs_review"
        reason = "No matching clause was found. This is advisory for this first-pass playbook."

    default_risk = (
        "High commercial and compliance exposure under Indian law if unaddressed."
        if template["required"] and status != "compliant"
        else "Advisory check to ensure balanced commercial and operational clarity."
    )
    default_amendment = f"Incorporate a standard Indian commercial clause defining {template['title'].lower()}."

    return {
        "check_id": template["check_id"],
        "title": template["title"],
        "required": template["required"],
        "status": status,
        "reason": reason,
        "explanation": reason,
        "risk_assessment": default_risk,
        "suggested_amendment": default_amendment,
        "evidence": evidence,
        "matched_terms": matches,
    }


def analyze_contract_with_gemini(contract_text: str, filename: str | None = None) -> dict[str, Any]:
    """Invoke Gemini to perform deep structured contract review with Indian legal rationale."""
    prompt_path = Path(__file__).parent / "prompts" / "contract_health_prompt.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"contract_health_prompt.txt not found at {prompt_path}")

    prompt = prompt_path.read_text(encoding="utf-8").format(
        filename=filename or "contract_document.pdf",
        contract_text=contract_text[:45000],
    )

    try:
        from .llm_client import get_client
        client = get_client()
    except Exception as exc:
        raise RuntimeError(f"Could not initialize Gemini client: {exc}") from exc

    # Attempt primary model and fast fallback
    models_to_try = [GEMINI_MODEL, "gemini-3.5-flash-lite"]
    last_err: Exception | None = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={"response_mime_type": "application/json", "response_schema": GeminiContractReport}
            )
            parsed = getattr(response, "parsed", None)
            if parsed is not None:
                if isinstance(parsed, GeminiContractReport):
                    return parsed.model_dump()
                elif isinstance(parsed, dict):
                    return parsed
        except Exception as exc:
            logger.warning("Gemini contract analysis with model %s failed: %s", model_name, exc)
            last_err = exc
            continue

    raise RuntimeError(f"Gemini contract analysis failed on all models: {last_err}")


def run_contract_health_check(
    contract_text: str, filename: str | None = None, use_ai: bool = True
) -> dict[str, Any]:
    """Run contract review, combining deterministic template validation with Gemini AI analysis."""
    text = (contract_text or "").strip()
    if not text:
        raise ValueError("No readable contract text was found in the uploaded document.")

    # 1. Deterministic baseline check
    results = [_run_template(template, text) for template in CONTRACT_TEMPLATES]

    ai_report: dict[str, Any] | None = None
    ai_enhanced = False

    # 2. Try Gemini AI analysis if enabled and key exists
    if use_ai and os.getenv("GEMINI_API_KEY"):
        try:
            ai_report = analyze_contract_with_gemini(text, filename)
            ai_enhanced = True
        except Exception as exc:
            logger.warning("Contract AI analysis unavailable, using deterministic results: %s", exc)

    if ai_enhanced and ai_report:
        clause_map = {c.get("check_id"): c for c in ai_report.get("clauses", []) if isinstance(c, dict)}
        for item in results:
            cid = item["check_id"]
            if cid in clause_map:
                ai_c = clause_map[cid]
                # If AI returned valid status, adopt it
                ai_status = ai_c.get("status")
                if ai_status in ("compliant", "needs_review", "missing_high_risk"):
                    item["status"] = ai_status
                if ai_c.get("explanation"):
                    item["explanation"] = ai_c["explanation"]
                    item["reason"] = ai_c["explanation"]
                if ai_c.get("risk_assessment"):
                    item["risk_assessment"] = ai_c["risk_assessment"]
                if ai_c.get("suggested_amendment"):
                    item["suggested_amendment"] = ai_c["suggested_amendment"]
                if ai_c.get("evidence"):
                    item["evidence"] = ai_c["evidence"]

        compliant = sum(item["status"] == "compliant" for item in results)
        review = sum(item["status"] == "needs_review" for item in results)
        high_risk = sum(item["status"] == "missing_high_risk" for item in results)
        score = ai_report.get("health_score") if isinstance(ai_report.get("health_score"), int) else round(100 * compliant / len(results))
        overall = ai_report.get("overall_risk") or ("high" if high_risk else "medium" if review else "low")
        executive_summary = ai_report.get("executive_summary", "")
        key_risks = ai_report.get("key_risks", [])
        negotiation_recommendations = ai_report.get("negotiation_recommendations", [])
    else:
        compliant = sum(item["status"] == "compliant" for item in results)
        review = sum(item["status"] == "needs_review" for item in results)
        high_risk = sum(item["status"] == "missing_high_risk" for item in results)
        score = round(100 * compliant / len(results))
        overall = "high" if high_risk else "medium" if review else "low"
        executive_summary = (
            "Automated first-pass keyword review completed. To generate deep clause-by-clause legal "
            "risk explanations and custom negotiation guidance, connect your Gemini API key."
        )
        key_risks = [item["title"] for item in results if item["status"] == "missing_high_risk"]
        negotiation_recommendations = [
            f"Review and negotiate {item['title'].lower()} to mitigate Indian legal liability."
            for item in results if item["status"] != "compliant"
        ][:4]

    # --- 3. Self-Check Pass: Sanitize fabricated figures & disaggregate do-not-merge pairs ---
    citations = load_citations_reference()
    allowed_numbers = set(citations.get("allowed_statutory_numbers", []))

    for item in results:
        ev = item.get("evidence")
        san_exp, exp_unfounded = sanitize_text_and_check_figures(item.get("explanation", ""), text, ev, allowed_numbers)
        item["explanation"] = san_exp
        item["reason"] = san_exp

        san_risk, risk_unfounded = sanitize_text_and_check_figures(item.get("risk_assessment", ""), text, ev, allowed_numbers)
        item["risk_assessment"] = san_risk

        san_amend, amend_unfounded = sanitize_text_and_check_figures(item.get("suggested_amendment", ""), text, ev, allowed_numbers)
        item["suggested_amendment"] = san_amend

        if exp_unfounded or risk_unfounded or amend_unfounded:
            item["status"] = "needs_review"

    executive_summary, _ = sanitize_text_and_check_figures(executive_summary, text, None, allowed_numbers)
    key_risks = [sanitize_text_and_check_figures(r, text, None, allowed_numbers)[0] for r in key_risks]
    negotiation_recommendations = [sanitize_text_and_check_figures(r, text, None, allowed_numbers)[0] for r in negotiation_recommendations]

    compliant = sum(item["status"] == "compliant" for item in results)
    review = sum(item["status"] == "needs_review" for item in results)
    high_risk = sum(item["status"] == "missing_high_risk" for item in results)

    return {
        "report_type": "Contract Health Report",
        "filename": filename,
        "disclaimer": (
            "First-pass automated screening and AI-assisted analysis only, not legal advice or contract approval. "
            "Have Indian legal counsel approve the playbook and material agreements."
        ),
        "ai_enhanced": ai_enhanced,
        "ai_model": GEMINI_MODEL if ai_enhanced else None,
        "executive_summary": executive_summary,
        "key_risks": key_risks,
        "negotiation_recommendations": negotiation_recommendations,
        "overall_risk": overall,
        "health_score": score,
        "summary": {
            "compliant": compliant,
            "needs_review": review,
            "missing_high_risk": high_risk,
            "total_checks": len(results),
        },
        "results": results,
        "checked_templates": [
            {key: item[key] for key in ("check_id", "title", "required", "description")}
            for item in CONTRACT_TEMPLATES
        ],
    }
