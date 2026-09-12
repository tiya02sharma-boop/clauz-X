"""Unit and integration tests for Qwen3-Embedding-0.6B integration and Chroma semantic retrieval."""
import pytest
from backend import config
from backend.embeddings import (
    DEFAULT_EMBEDDING_DIM,
    DEFAULT_TASK_INSTRUCTION,
    embed_texts,
)
from backend.rag_assistant import (
    DOCUMENT_INSTRUCTION,
    QUERY_INSTRUCTION,
    format_chunk_text,
    index_legal_corpus,
    retrieve,
)
from backend.app import app


@pytest.fixture(scope="module", autouse=True)
def setup_indexed_corpus():
    """Ensure the legal corpus is indexed in Chroma before tests run."""
    config.ensure_storage()
    count = index_legal_corpus()
    assert count > 0, "Corpus must have at least 1 document indexed for testing"
    yield


def test_embed_texts_expected_dimensions():
    """Confirm embed_texts() returns vectors of the expected dimension for batch and configurable dims."""
    samples = [
        "Central Goods and Services Tax Act return filing requirements.",
        "Employees State Insurance Act coverage and registration thresholds.",
        "Director KYC verification through DIN under Companies Act.",
    ]

    # Test default dimension (768)
    default_vectors = embed_texts(samples)
    assert len(default_vectors) == 3
    for vec in default_vectors:
        assert isinstance(vec, list)
        assert len(vec) == DEFAULT_EMBEDDING_DIM
        assert len(vec) == 768
        assert all(isinstance(val, float) for val in vec)

    # Test configurable dimension: 512
    dim_512_vectors = embed_texts(samples, dimension=512)
    assert len(dim_512_vectors) == 3
    for vec in dim_512_vectors:
        assert len(vec) == 512

    # Test configurable dimension: 256
    dim_256_vectors = embed_texts(samples, dimension=256)
    assert len(dim_256_vectors) == 3
    for vec in dim_256_vectors:
        assert len(vec) == 256

    # Test empty list
    empty_vectors = embed_texts([])
    assert empty_vectors == []


def test_query_and_ingestion_code_path_parity():
    """Confirm query-time and ingestion-time embeddings use the exact same code path without drift."""
    test_text = "Section 15 of the MSMED Act deals with the time limit for payment to a micro enterprise."

    # Both ingestion and query must call embed_texts
    ingest_vecs = embed_texts([test_text], task_instruction=DOCUMENT_INSTRUCTION, dimension=config.EMBEDDING_DIM)
    query_vecs = embed_texts([test_text], task_instruction=QUERY_INSTRUCTION, dimension=config.EMBEDDING_DIM)

    # Same vector dimensions and types
    assert len(ingest_vecs) == 1
    assert len(query_vecs) == 1
    assert len(ingest_vecs[0]) == config.EMBEDDING_DIM
    assert len(query_vecs[0]) == config.EMBEDDING_DIM

    # Same code path with identical instruction produces bit-for-bit identical vectors
    run1 = embed_texts([test_text], task_instruction="Custom Instruction:", dimension=768)
    run2 = embed_texts([test_text], task_instruction="Custom Instruction:", dimension=768)
    assert run1 == run2, "Repeated embeddings of identical text and parameters must be bitwise identical"


def test_end_to_end_retrieval_known_answers():
    """Ask questions with known answers in the corpus; confirm top retrieved chunk is the expected one."""
    # Test 1: Board meeting quorum
    q_board = "How many board meetings must every company hold in a year and what is the required quorum?"
    results_board = retrieve(q_board, limit=3)
    assert len(results_board) > 0, "Expected at least one matching passage"
    top_board = results_board[0]
    assert top_board["id"] == "board-meetings"
    assert "Companies Act, 2013, sections 173(1) and 174" in top_board["citation"]
    assert "quorum" in top_board["text"].lower()

    # Test 2: MSME 45-day delayed payments
    q_msme = "What is the 45-day payment rule for micro and small suppliers under MSMED Act?"
    results_msme = retrieve(q_msme, limit=3)
    assert len(results_msme) > 0, "Expected at least one matching passage"
    top_msme = results_msme[0]
    assert top_msme["id"] == "msme-payments"
    assert "MSMED Act, 2006, section 15" in top_msme["citation"]

    # Test 3: GST returns
    q_gst = "What section governs furnishing returns like GSTR-3B and outward supplies under GST?"
    results_gst = retrieve(q_gst, limit=3)
    assert len(results_gst) > 0, "Expected at least one matching passage"
    top_gst = results_gst[0]
    assert top_gst["id"] == "gst-returns"
    assert "Central Goods and Services Tax Act" in top_gst["title"]


def test_unrelated_question_triggers_no_source_found():
    """Confirm a question with no relevant corpus content triggers empty retrieval and no_verified_source."""
    irrelevant_question = "What are the rules and regulations for operating civilian drones over national parks?"
    passages = retrieve(irrelevant_question)
    assert passages == [], f"Expected empty passages for irrelevant question, but got {passages}"

    # Test end-to-end via Flask test client for Ask Clauz X endpoint
    client = app.test_client()
    resp = client.post("/api/ask", json={"question": irrelevant_question})
    assert resp.status_code == 200
    data = resp.get_json()

    # Either out_of_scope (if domain keyword filter intercepts) or no_verified_source (if retrieved passages empty)
    assert data["status"] in {"out_of_scope", "no_verified_source"}
    assert data["sources"] == []
    assert "could not find enough verified material" in data["answer"] or "out of scope" in data["status"] or "Indian business compliance" in data["answer"]


def test_document_verification_prefilter_gate_short_circuits_llm(monkeypatch):
    """Stretch Goal A: Confirm unrelated document is caught by similarity pre-filter and never reaches LLM."""
    from unittest.mock import MagicMock
    from backend.verification_engine import verify_document, DOC_SIMILARITY_THRESHOLD
    from backend.models import RegulatoryRequirement, BusinessProfile, DocumentFileValidation, ComplianceVerificationResult

    # Mock structured (the LLM call)
    mock_structured = MagicMock()
    monkeypatch.setattr("backend.verification_engine.structured", mock_structured)

    requirement = RegulatoryRequirement(
        obligation_id="rule_gstr3b_monthly",
        title="Monthly GSTR-3B Return Filing",
        description="Filing monthly summary return of outward and inward supplies and tax payment under CGST Act.",
        required_evidence=["GSTR-3B filing ARN acknowledgment receipt", "Challan PMT-06 payment receipt"],
        legal_source="CGST Act, 2017, Section 39",
    )
    profile = BusinessProfile(
        business_id="biz_test",
        business_name="Test Enterprise Pvt Ltd",
        turnover=15000000.0,
        headcount=15,
        sector="services",
        state="Maharashtra",
        entity_type="Private Limited",
    )
    usable_validation = DocumentFileValidation(
        apparent_status="usable",
        reason="Document contains readable text.",
        extraction_method="direct",
    )

    # 1. Unrelated document (pizza order delivery invoice)
    unrelated_doc = (
        "Domino's Pizza order delivery receipt. Order #48292. "
        "Items: 2 Cheese Margherita Pizzas, 1 Garlic Bread, 2 Cokes. "
        "Total Paid: Rs 840 via UPI. Thank you for dining with us!"
    )

    result_unrelated = verify_document(requirement, unrelated_doc, profile, usable_validation)
    assert result_unrelated.verdict == "needs_review"
    assert "Document content does not appear related to this obligation" in result_unrelated.reason
    # Ensure LLM was NEVER called
    assert mock_structured.call_count == 0, f"Expected 0 LLM calls for unrelated doc, but got {mock_structured.call_count}"

    # 2. Matching document (actual GST return)
    matching_doc = (
        "Form GSTR-3B [See rule 61(5)] Monthly Return for August 2026. "
        "GSTIN: 27AABCT1234F1Z5. Legal Name: Test Enterprise Pvt Ltd. "
        "Table 3.1: Details of Outward Supplies and inward supplies liable to reverse charge. "
        "Total Taxable Value: 12,50,000 INR. Integrated Tax: 2,25,000 INR. "
        "Acknowledgment Reference Number (ARN): AA2708260019283."
    )
    mock_structured.return_value = ComplianceVerificationResult(
        obligation_id="rule_gstr3b_monthly",
        verdict="pass",
        reason="GSTR-3B filing acknowledgment verified for the required period.",
    )

    result_matching = verify_document(requirement, matching_doc, profile, usable_validation)
    assert result_matching.verdict == "pass"
    # Ensure LLM WAS called for matching document
    assert mock_structured.call_count == 1, "Expected exactly 1 LLM call for matching document"


def test_notification_relevance_filter_historical_titles():
    """Stretch Goal B: Confirm at least 5 real historical titles are classified accurately."""
    from backend.monitor import ai_read_and_filter

    test_titles = [
        ("Notification No. 25/2026 - Central Tax: Due date extension for GSTR-1 quarterly filers", True),
        ("Advisory on GST portal maintenance downtime on 14th September 2026", False),
        ("Clarification on penalty waiver under Section 128 of CGST Act", True),
        ("Toll-free helpdesk number temporarily changed due to line shifting", False),
        ("Order under Section 15 of MSMED Act regarding delayed payments to MSEs", True),
    ]

    for title, expected in test_titles:
        classified = ai_read_and_filter(title)
        assert classified == expected, f"Failed for '{title}': expected {expected}, got {classified}"

