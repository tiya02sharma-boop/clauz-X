from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator

class BusinessProfile(BaseModel):
    business_id: str | None = None
    business_name: str | None = None
    turnover: float | None = None
    headcount: int | None = None
    sector: str | None = None
    state: str | None = None
    entity_type: str | None = None
    gst_registered: bool | None = None
    gst_filing_scheme: str | None = None
    agm_date: str | None = None
    whatsapp_number: str | None = None

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
