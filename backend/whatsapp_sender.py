"""WhatsApp messaging layer using WaSenderAPI, with simulation fallback when credentials are missing."""
import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid

from . import config
from .models import WhatsAppSendResult

logger = logging.getLogger(__name__)

WASENDER_SEND_URL = "https://www.wasenderapi.com/api/send-message"


def normalize_phone_number(number: str | None) -> str | None:
    """Normalize phone number to E.164 format (e.g. '+919896603656')."""
    if not number or not isinstance(number, str):
        return None
    cleaned = number.strip()
    # Strip any 'whatsapp:' prefix from legacy Twilio format
    if cleaned.lower().startswith("whatsapp:"):
        cleaned = cleaned[9:].strip()
    digits_and_plus = re.sub(r"[^\d+]", "", cleaned)
    if not digits_and_plus:
        return None
    if not digits_and_plus.startswith("+"):
        if len(digits_and_plus) == 10:
            digits_and_plus = f"+91{digits_and_plus}"
        else:
            digits_and_plus = f"+{digits_and_plus}"
    return digits_and_plus


def normalize_whatsapp_number(number: str | None) -> str | None:
    """Normalize phone number; returns 'whatsapp:+<digits>' for WhatsApp format or None."""
    e164 = normalize_phone_number(number)
    return f"whatsapp:{e164}" if e164 else None


_ERROR_CODE_MAP = {
    21211: "INVALID_NUMBER",
    21408: "INVALID_NUMBER",
    21614: "INVALID_NUMBER",
    63012: "INVALID_NUMBER",
    63024: "INVALID_NUMBER",
    63007: "RECIPIENT_NOT_OPTED_IN",
    63015: "RECIPIENT_NOT_OPTED_IN",
    63028: "RECIPIENT_NOT_OPTED_IN",
    63029: "RECIPIENT_NOT_OPTED_IN",
    63016: "TEMPLATE_REQUIRED",
    63032: "TEMPLATE_REQUIRED",
    63040: "TEMPLATE_REQUIRED",
    21610: "TEMPLATE_REQUIRED",
}


def map_provider_error(code: int | str | None, message: str = "") -> str:
    """Map provider error codes to stable application error codes."""
    if code is not None:
        try:
            c = int(code)
            if c in _ERROR_CODE_MAP:
                return _ERROR_CODE_MAP[c]
        except (ValueError, TypeError):
            pass
    msg = (message or "").lower()
    if "opt" in msg or "not opted in" in msg:
        return "RECIPIENT_NOT_OPTED_IN"
    if "invalid" in msg or "not a valid" in msg or "unreachable" in msg:
        return "INVALID_NUMBER"
    if "template" in msg or "24-hour" in msg:
        return "TEMPLATE_REQUIRED"
    return "WHATSAPP_SEND_FAILED"


def send_whatsapp_message(
    to: str,
    message: str,
    api_key: str | None = None,
    content_variables: dict | None = None,
    account_sid: str | None = None,
    auth_token: str | None = None,
    from_number: str | None = None,
    **kwargs,
) -> WhatsAppSendResult:
    """
    Send a WhatsApp message via WaSenderAPI or simulate if credentials are missing.

    Endpoint: POST https://www.wasenderapi.com/api/send-message
    Headers:  Authorization: Bearer <WASENDER_API_KEY>
    Body:     { "to": "+919xxxxxxxxx", "text": "..." }

    Guaranteed:
    - Never disables TLS verification.
    - Never raises unhandled exceptions to callers.
    - Missing credentials result in a successful simulated send (status='simulated').
    """
    normalized_to = normalize_phone_number(to)
    if not normalized_to or not re.fullmatch(r"\+[1-9]\d{7,14}", normalized_to):
        return WhatsAppSendResult(
            status="failed",
            sid=None,
            error_code="INVALID_NUMBER",
            error_message=f"The phone number '{to}' is not a valid international format.",
        )

    # Determine the API key to use
    key = api_key or config.WASENDER_API_KEY

    # If no key is configured or explicitly simulated, fallback to simulation
    if not key or str(key).strip().lower() in ("", "none", "your_api_key_here") or kwargs.get("simulate"):
        sim_sid = f"sim_{uuid.uuid4().hex[:16]}"
        print(f"\n[SIMULATED WASENDER SEND]")
        print(f"To: {normalized_to}")
        print(f"Body:\n{message}")
        print(f"Simulated SID: {sim_sid}\n")
        logger.info("Simulated WaSender message to %s (SID: %s)", normalized_to, sim_sid)
        return WhatsAppSendResult(
            status="simulated",
            sid=sim_sid,
            error_code=None,
            error_message=None,
        )


    # Real WaSenderAPI call
    payload = json.dumps({"to": normalized_to, "text": message}).encode("utf-8")
    req = urllib.request.Request(
        WASENDER_SEND_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "ClauzX-ComplianceEngine/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode("utf-8")
            data = json.loads(resp_body)
            # WaSenderAPI returns { "success": true, "message": "...", ... }
            sid = data.get("id") or data.get("messageId") or f"WS_{uuid.uuid4().hex[:16]}"
            logger.info("WaSender message sent to %s (id: %s)", normalized_to, sid)
            return WhatsAppSendResult(status="sent", sid=sid, error_code=None, error_message=None)

    except urllib.error.HTTPError as http_err:
        try:
            err_json = json.loads(http_err.read().decode("utf-8"))
            err_msg = err_json.get("message") or err_json.get("error") or str(http_err)
        except Exception:
            err_msg = str(http_err)
        logger.warning("WaSender send failed (HTTP %s): %s", http_err.code, err_msg)
        return WhatsAppSendResult(
            status="failed", sid=None,
            error_code="WHATSAPP_SEND_FAILED", error_message=err_msg,
        )
    except Exception as exc:
        logger.error("WaSender connection error: %s", exc)
        return WhatsAppSendResult(
            status="failed", sid=None,
            error_code="WHATSAPP_SEND_FAILED", error_message=str(exc),
        )


def send_onboarding_summary(business_name: str, whatsapp_number: str, obligations: list) -> WhatsAppSendResult:
    """
    Send an instant welcome + compliance summary message when a business is registered.
    Called immediately after the applicability engine runs on user sign-in / profile save.
    """
    if not obligations:
        body = (
            f"👋 *Welcome to Clauz X!*\n\n"
            f"🏢 *{business_name}* has been registered.\n\n"
            f"✅ No compliance obligations matched your current profile. "
            f"Update your profile anytime to re-run the applicability check."
        )
        return send_whatsapp_message(to=whatsapp_number, message=body)

    lines = []
    for i, ob in enumerate(obligations[:10], start=1):
        name = ob.get("obligation_name") or ob.get("name") or "Obligation"
        due = ob.get("next_due") or "—"
        recurrence = (ob.get("recurrence") or "").capitalize()
        penalty = ob.get("penalty_formula") or ob.get("penalty") or ""
        entry = f"*{i}. {name}*"
        if recurrence:
            entry += f" ({recurrence})"
        entry += f"\n   📅 Next Due: {due}"
        if penalty:
            entry += f"\n   ⚠️ Penalty: {penalty}"
        lines.append(entry)

    overflow_note = ""
    if len(obligations) > 10:
        overflow_note = f"\n\n_...and {len(obligations) - 10} more. Visit your Clauz X dashboard for the full list._"

    body = (
        f"👋 *Welcome to Clauz X!*\n\n"
        f"🏢 *{business_name}* has been registered successfully.\n"
        f"Here are your *{len(obligations)} applicable compliance obligations*:\n\n"
        + "\n\n".join(lines)
        + overflow_note
        + "\n\n📲 You will receive reminders *7, 3, and 1 day* before each deadline.\n"
        f"_Powered by Clauz X — MSME Compliance Assistant_"
    )

    return send_whatsapp_message(to=whatsapp_number, message=body)


def send_contract_health_report_whatsapp(
    whatsapp_number: str,
    report: dict,
    pdf_download_url: str | None = None,
) -> WhatsAppSendResult:
    """Format and dispatch a Contract Health Review report via WhatsApp."""
    filename = report.get("filename") or "Contract"
    score = report.get("health_score", 0)
    risk = str(report.get("overall_risk", "medium")).upper()
    exec_summary = report.get("executive_summary") or "First-pass legal risk audit screening completed."
    key_risks = report.get("key_risks") or []
    recommendations = report.get("negotiation_recommendations") or []

    results = report.get("results") or []
    compliant_count = sum(1 for r in results if r.get("status") == "compliant")
    needs_review_count = sum(1 for r in results if r.get("status") == "needs_review")
    high_risk_count = sum(1 for r in results if r.get("status") == "missing_high_risk")

    risk_emoji = "🟢" if "LOW" in risk else ("🟡" if "MEDIUM" in risk else "🔴")

    msg_lines = [
        f"📄 *CLAUZ X CONTRACT HEALTH & RISK AUDIT*",
        f"📁 *Contract:* {filename}",
        f"🛡️ *Overall Risk:* {risk_emoji} {risk} (Health Score: {score}/100)",
        f"📊 *Compliance:* ✅ {compliant_count} Compliant | ⚠️ {needs_review_count} Review | 🚨 {high_risk_count} High Risk",
        "",
        f"📝 *Executive Summary:*",
        f"_{exec_summary}_",
    ]

    if key_risks:
        msg_lines.extend(["", "🚨 *Key Red Flags & Statutory Risks:*"])
        for r in key_risks[:4]:
            msg_lines.append(f"• {r}")

    if recommendations:
        msg_lines.extend(["", "💡 *Recommended Negotiation Covenants:*"])
        for rec in recommendations[:3]:
            msg_lines.append(f"• {rec}")

    if pdf_download_url:
        msg_lines.extend(["", f"📥 *Download Full PDF Audit Report:*", pdf_download_url])

    msg_lines.extend(["", "_Powered by Clauz X — India Legal & Contract AI_"])

    body = "\n".join(msg_lines)
    return send_whatsapp_message(to=whatsapp_number, message=body)

