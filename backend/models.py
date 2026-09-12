from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

MICRO_INVESTMENT_MAX = 25_000_000      # Rs. 2.5 Crore (2,50,00,000)
MICRO_TURNOVER_MAX = 100_000_000       # Rs. 10 Crore (10,00,00,000)
SMALL_INVESTMENT_MAX = 250_000_000     # Rs. 25 Crore (25,00,00,000)
SMALL_TURNOVER_MAX = 1_000_000_000     # Rs. 100 Crore (100,00,00,000)
MEDIUM_INVESTMENT_MAX = 1_250_000_000  # Rs. 125 Crore (1,25,00,00,000)
MEDIUM_TURNOVER_MAX = 5_000_000_000    # Rs. 500 Crore (500,00,00,000)

def compute_msme_classification(investment: float | int | None, turnover: float | int | None) -> str:
    """
    Composite criteria classification (April 2025 thresholds):
    Both investment AND turnover must satisfy the threshold for a tier.
    If EITHER exceeds a tier's threshold, the business cannot be in that tier.
    """
    if investment is None or turnover is None:
        return "Not MSME"
    try:
        inv = float(investment)
        t_over = float(turnover)
    except (ValueError, TypeError):
        return "Not MSME"

    if inv <= MICRO_INVESTMENT_MAX and t_over <= MICRO_TURNOVER_MAX:
        return "Micro"
    if inv <= SMALL_INVESTMENT_MAX and t_over <= SMALL_TURNOVER_MAX:
        return "Small"
    if inv <= MEDIUM_INVESTMENT_MAX and t_over <= MEDIUM_TURNOVER_MAX:
        return "Medium"
    return "Not MSME"

class BusinessProfile(BaseModel):
    business_id: str | None = None
    business_name: str | None = None
    turnover: float | None = None
    headcount: int | None = None
    investment_plant_machinery: float | None = None
    is_factory: bool | None = None
    msme_classification: str | None = None
    sector: str | None = None
    state: str | None = None
    entity_type: str | None = None
    gst_registered: bool | None = None
    gst_filing_scheme: str | None = None
    agm_date: str | None = None
    whatsapp_number: str | None = None
    flags: dict[str, Any] | None = None

    @model_validator(mode="after")
    def set_derived_msme_classification(self):
        # Always recompute derived msme_classification; never let it go stale
        self.msme_classification = compute_msme_classification(
            self.investment_plant_machinery, self.turnover
        )
        return self


class ObligationCalendarEntry(BaseModel):
    obligation_id: str
    name: str
    recurrence: str | None = None
    next_due: str | None = None  # ISO format YYYY-MM-DD or None
    penalty_formula: str | None = None
    source_citation: str | None = None
    due_day_rule: str | None = None
    due_date_config: dict[str, Any] | None = None
    needs_manual_date_entry: bool = False
    description: str | None = None
    source_url: str | None = None

class Business(BaseModel):
    business_id: str
    profile: BusinessProfile
    obligations: list[ObligationCalendarEntry] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None

class ReminderLogEntry(BaseModel):
    business_id: str
    business_name: str | None = None
    obligation_id: str
    obligation_name: str
    window: Literal[7, 3, 1]
    date: str  # ISO date string YYYY-MM-DD reminder was sent for
    to: str  # WhatsApp number
    status: Literal["sent", "simulated", "failed"]
    sid: str | None = None
    error_code: Literal["INVALID_NUMBER", "RECIPIENT_NOT_OPTED_IN", "TEMPLATE_REQUIRED", "WHATSAPP_SEND_FAILED"] | None = None
    sent_at: str  # ISO 8601 timestamp

class WhatsAppSendResult(BaseModel):
    status: Literal["sent", "simulated", "failed"]
    sid: str | None = None
    error_code: Literal["INVALID_NUMBER", "RECIPIENT_NOT_OPTED_IN", "TEMPLATE_REQUIRED", "WHATSAPP_SEND_FAILED"] | None = None
    error_message: str | None = None

class RegulatoryEntry(BaseModel):
    title: str | None = None
    date: str | None = None
    reference_number: str | None = None
    summary: str | None = None
    pdf_url: str | None = None
    source_url: str | None = None

    @field_validator("pdf_url", "source_url")
    @classmethod
    def valid_url(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith(("http://", "https://")):
            raise ValueError("URL must use http or https")
        return value

class RegulatoryEntries(BaseModel):
    entries: list[RegulatoryEntry] = Field(default_factory=list)

class ExtractedRule(BaseModel):
    obligation_name: str | None = None
    turnover_min: float | None = None
    turnover_max: float | None = None
    headcount_min: int | None = None
    headcount_max: int | None = None
    investment_min: float | None = None
    investment_max: float | None = None
    requires_is_factory: bool | None = None
    sector: str | None = None
    state: str | None = None
    entity_type: str | None = None
    recurrence: str | None = None
    due_day_rule: str | None = None
    penalty_formula: str | None = None
    description: str | None = None
    source_title: str | None = None
    source_url: str | None = None
    source_citation: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    extraction_confidence: float | None = Field(default=None, ge=0, le=1)
    fields_needing_human_verification: list[str] = Field(default_factory=list)
    evidence: dict[str, str] = Field(default_factory=dict)
    change_type: Literal["new", "amendment", "replacement", "unknown"] = "unknown"
    previous_rule_id: str | None = None


class DocumentFileValidation(BaseModel):
    document_type: str | None = None
    readable: bool = False
    complete_enough_for_review: bool = False
    apparent_status: Literal["usable", "needs_review", "invalid"] = "needs_review"
    reason: str
    evidence: str | None = None
    identifiers_found: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    expiry_date: str | None = None
    extraction_method: str | None = None


class RegulatoryRequirement(BaseModel):
    obligation_id: str
    title: str
    description: str | None = None
    applicable: bool = True
    required_evidence: list[str] = Field(default_factory=list)
    legal_source: str | None = None
    conditions: list[Any] = Field(default_factory=list)


class ComplianceVerificationResult(BaseModel):
    obligation_id: str
    verdict: Literal["pass", "fail", "missing", "needs_review"]
    reason: str
    evidence: str | None = None
    document_validation_status: str | None = None
    legal_source: str | None = None
    extraction_method: str | None = None


class ComplianceCheckReport(BaseModel):
    check_id: str | None = None
    business_id: str | None = None
    business_name: str | None = None
    created_at: str | None = None
    applicable_requirements: list[RegulatoryRequirement] = Field(default_factory=list)
    results: list[ComplianceVerificationResult] = Field(default_factory=list)
    compliance_score: int = 0
    risk_level: Literal["low", "medium", "high"] = "high"
    human_verification_required: list[str] = Field(default_factory=list)
    conflicts_detected: list[str] = Field(default_factory=list)
    coverage_note: str | None = None
