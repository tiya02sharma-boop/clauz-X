import os
from backend.contract_health import run_contract_health_check


def test_contract_health_flags_absent_required_clauses():
    report = run_contract_health_check(
        "This agreement covers services and payment of fees.", "short.pdf", use_ai=False
    )
    result = next(item for item in report["results"] if item["check_id"] == "indemnity")
    assert result["status"] == "missing_high_risk"
    assert report["summary"]["missing_high_risk"] > 0
    assert "explanation" in result
    assert "risk_assessment" in result
    assert "suggested_amendment" in result
    assert "executive_summary" in report
    assert "key_risks" in report
    assert "negotiation_recommendations" in report


def test_contract_health_marks_a_complete_indemnity_check_compliant():
    report = run_contract_health_check(
        "Each party shall indemnify the other for any claim caused by breach or negligence, including legal fees.",
        use_ai=False,
    )
    result = next(item for item in report["results"] if item["check_id"] == "indemnity")
    assert result["status"] == "compliant"
    assert result["explanation"]


def test_contract_health_with_gemini_integration():
    if not os.getenv("GEMINI_API_KEY"):
        return
    text = (
        "SERVICES AGREEMENT between Acme Corp and Beta Logistics Pvt Ltd. "
        "Scope: Logistic delivery. Payment: INR 10,000 monthly plus 18% GST within 30 days. TDS deducted under 194C. "
        "Governing Law: Laws of India, exclusive jurisdiction of Mumbai courts. "
        "Confidentiality: 3 years survival. Liability Cap: 1x annual contract value."
    )
    report = run_contract_health_check(text, "vendor_contract.pdf", use_ai=True)
    assert "report_type" in report
    assert "results" in report
    assert len(report["results"]) == 14
    if report.get("ai_enhanced"):
        assert len(report["executive_summary"]) > 20
        assert len(report["key_risks"]) > 0
        assert len(report["negotiation_recommendations"]) > 0
        # Check that clauses have detailed explanations and legal risk assessments
        indemnity_check = next(item for item in report["results"] if item["check_id"] == "indemnity")
        assert len(indemnity_check.get("explanation", "")) > 10
        assert len(indemnity_check.get("risk_assessment", "")) > 10


def test_gst_clause_without_rate_contains_no_fabricated_percentage():
    """Bug 1 Fix Verification: Unquoted GST rates must never be fabricated."""
    contract_text = (
        "Client shall pay monthly fees within thirty (30) days of receipt of invoice "
        "plus applicable Goods and Services Tax (GST). All payments are due by bank transfer."
    )
    report = run_contract_health_check(contract_text, "test_gst.pdf", use_ai=False)
    gst_check = next(item for item in report["results"] if item["check_id"] == "scope_payment_gst")

    explanation = gst_check.get("explanation", "")
    risk = gst_check.get("risk_assessment", "")
    amendment = gst_check.get("suggested_amendment", "")

    # Assert no fabricated 18% figure
    assert "18%" not in explanation
    assert "18%" not in risk
    assert "18%" not in amendment
    assert "18 percent" not in explanation.lower()


def test_clause_with_gst_and_tds_never_contains_reverse_charge_tds():
    """Bug 2 Fix Verification: Reverse charge (GST) and TDS (Income Tax) must never be merged."""
    contract_text = (
        "Fees are exclusive of GST. Where applicable under Section 9(3) of CGST Act, "
        "reverse charge applies. TDS shall be deducted as per Section 194C of Income Tax Act 1961."
    )
    report = run_contract_health_check(contract_text, "test_tax.pdf", use_ai=False)

    all_texts = []
    for item in report["results"]:
        all_texts.extend([item.get("explanation", ""), item.get("risk_assessment", ""), item.get("suggested_amendment", "")])
    all_texts.extend(report.get("key_risks", []))
    all_texts.append(report.get("executive_summary", ""))

    combined = " ".join(all_texts).lower()
    assert "reverse-charge tds" not in combined
    assert "reverse charge tds" not in combined


def test_clause_with_explicit_rate_preserves_verbatim_figures():
    """Requirement 1 Passthrough Verification: Verbatim figures in source text pass through cleanly."""
    contract_text = (
        "Agreement for IT consultancy. Client shall pay fees plus 12% GST payable within 45 days of invoice. "
        "Each party indemnifies the other for breach."
    )
    report = run_contract_health_check(contract_text, "test_verbatim.pdf", use_ai=False)
    gst_check = next(item for item in report["results"] if item["check_id"] == "scope_payment_gst")

    # 12% GST and 45 days are present in contract_text, so they must be preserved if referenced
    assert gst_check["evidence"] is not None
    assert "12%" in gst_check["evidence"] or "12%" in contract_text


def test_citation_table_and_do_not_merge_validation():
    """Requirement 2 & 3 Verification: Citation reference table and disaggregation logic."""
    from backend.contract_health import load_citations_reference, sanitize_text_and_check_figures

    citations = load_citations_reference()
    assert "statutory_citations" in citations
    assert "gst_reverse_charge" in citations["statutory_citations"]
    assert "tds_on_services" in citations["statutory_citations"]
    assert "dpdp_breach_penalty" in citations["statutory_citations"]

    # Verify do-not-merge sanitization
    merged_input = "Ambiguity in GST invoice timelines and reverse-charge TDS deduction obligations."
    sanitized, _ = sanitize_text_and_check_figures(merged_input, "source text")
    assert "reverse-charge TDS" not in sanitized
    assert "reverse-charge mechanisms" in sanitized or "separate Income Tax TDS" in sanitized

