import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from backend import config
from backend.app import app
from backend.models import BusinessProfile, ComplianceVerificationResult, DocumentFileValidation
from backend.verification_engine import run_compliance_check


RULE = {
    "rule_id": "gst_registration", "obligation_name": "GST Registration",
    "gst_registered": True, "required_evidence": ["GSTIN"],
}


def _rules_path():
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump([RULE], handle); handle.close()
    return Path(handle.name)


def test_missing_document_is_deterministic_and_does_not_call_llm():
    with patch.object(config, "RULES_PATH", _rules_path()), patch("backend.verification_engine.structured") as structured:
        report = run_compliance_check(BusinessProfile(business_name="Test", gst_registered=True), {})
    structured.assert_not_called()
    assert report.results[0].verdict == "missing"
    assert report.compliance_score == 0
    assert report.risk_level == "high"


def test_check_api_persists_a_structured_result(tmp_path):
    checks_path = tmp_path / "checks.json"
    checks_path.write_text("[]")
    validation = DocumentFileValidation(reason="Readable GST certificate", readable=True, complete_enough_for_review=True, apparent_status="usable")
    verified = ComplianceVerificationResult(obligation_id="gst_registration", verdict="pass", reason="GSTIN is present", evidence="GSTIN: 27ABCDE1234F1Z5")
    with patch.object(config, "RULES_PATH", _rules_path()), patch.object(config, "COMPLIANCE_CHECKS_PATH", checks_path), patch("backend.verification_engine.structured", side_effect=[validation, verified]):
        app.config["TESTING"] = True
        response = app.test_client().post("/api/compliance/check", json={
            "business_profile": {"business_id": "verification-test", "business_name": "Test", "gst_registered": True},
            "uploaded_docs": {"gst_registration": "GST Registration Certificate GSTIN: 27ABCDE1234F1Z5"},
        })
    assert response.status_code == 200
    result = next(item for item in response.get_json()["results"] if item["obligation_id"] == "gst_registration")
    assert result["verdict"] == "pass"
    assert response.get_json()["check_id"].startswith("chk_")
