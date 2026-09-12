import os
import re
import json
import tempfile
import hashlib
from pathlib import Path
import sys
import io
import uuid
from flask import Flask, jsonify, request, send_file
from pydantic import ValidationError
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend import config
    from backend.applicability_engine import check_applicability
    from backend.calendar_service import (
        compute_obligations_calendar,
        get_business,
        list_businesses,
        recompute_business_calendar,
        save_or_update_business,
        save_compliance_check,
        list_compliance_checks,
    )
    from backend.models import BusinessProfile, ExtractedRule
    from backend.pdf_extractor import extract_pdf_text
    from backend.contract_health import run_contract_health_check
    from backend.pdf_report_generator import build_contract_health_pdf
    from backend.reminder_scheduler import run_reminder_cycle
    from backend.storage import audit, load, now, save
    from backend.whatsapp_sender import get_wasender_status, send_contract_health_report_whatsapp, send_onboarding_summary
else:
    from . import config
    from .applicability_engine import check_applicability
    from .calendar_service import (
        compute_obligations_calendar,
        get_business,
        list_businesses,
        recompute_business_calendar,
        save_or_update_business,
        save_compliance_check,
        list_compliance_checks,
    )
    from .models import BusinessProfile, ExtractedRule
    from .pdf_extractor import extract_pdf_text
    from .contract_health import run_contract_health_check
    from .pdf_report_generator import build_contract_health_pdf
    from .reminder_scheduler import run_reminder_cycle
    from .storage import audit, load, now, save
    from .whatsapp_sender import get_wasender_status, send_contract_health_report_whatsapp, send_onboarding_summary

app = Flask(__name__)
config.ensure_storage()

def bootstrap_product_baseline() -> None:
    """Install a vetted product release only when live rules have not yet been initialized."""
    live_rules = load(config.RULES_PATH, [])
    baseline = load(config.BASELINE_RULES_PATH, [])
    if live_rules or not baseline:
        return
    save(config.RULES_PATH, baseline)
    manifest = load(config.BASELINE_MANIFEST_PATH, {})
    audit(config.AUDIT_PATH, "product_baseline_installed", version=manifest.get("version"), rule_count=len(baseline))

bootstrap_product_baseline()
# Monitoring pulls in optional embedding dependencies. Keep the lightweight
# contract dashboard usable without them unless monitoring is deliberately on.
if config.ENABLE_REGULATORY_MONITOR:
    if __package__ in (None, ""):
        from backend.monitor_scheduler import start_monitor_scheduler
    else:
        from .monitor_scheduler import start_monitor_scheduler
    start_monitor_scheduler()

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = app.make_default_options_response()
        origin = request.headers.get("Origin")
        if origin and ("localhost" in origin or "127.0.0.1" in origin):
            res.headers["Access-Control-Allow-Origin"] = origin
        else:
            res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        return res

@app.after_request
def allow_local_frontend(response):
    """Permit the separately served local React UI to call this API."""
    origin = request.headers.get("Origin")
    if origin and ("localhost" in origin or "127.0.0.1" in origin):
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    return response

def error(code, message, status=400): return jsonify({"error": {"code": code, "message": message}}), status

@app.get("/api/health")
def health_check():
    """Lightweight readiness endpoint used by Render and deployment checks."""
    return jsonify({"status": "ok", "service": "clauzx-backend"}), 200


@app.get("/api/whatsapp/status")
def whatsapp_status():
    """Read-only WaSender connection diagnostic; never returns the API key."""
    return jsonify(get_wasender_status()), 200

@app.get("/")
def api_home():
    return jsonify({
        "service": "Clauz X backend API",
        "frontend": "http://127.0.0.1:5173",
        "monitor_status": "/admin/monitor/status",
        "applicability": "POST /api/applicability/check"
    })

@app.post("/api/applicability/check")
def applicability():
    try:
        profile = BusinessProfile.model_validate(request.get_json(force=True))
        result = check_applicability(profile); audit(config.AUDIT_PATH, "applicability_checked")
        return jsonify(result)
    except (ValidationError, TypeError) as exc: return error("INVALID_BUSINESS_PROFILE", str(exc))

@app.post("/api/ask")
def ask_clauz():
    # Retrieval dependencies (Chroma and the embedding model) are optional for
    # the contract-review workflow, so load them only when this AI endpoint is used.
    if __package__ in (None, ""):
        from backend.llm_client import grounded_answer
        from backend.rag_assistant import is_compliance_question, retrieve
    else:
        from .llm_client import grounded_answer
        from .rag_assistant import is_compliance_question, retrieve
    question = str((request.get_json(silent=True) or {}).get("question", "")).strip()
    if not question: return error("QUESTION_REQUIRED", "Please enter a compliance question.")
    if not is_compliance_question(question):
        return jsonify({"status": "out_of_scope", "answer": "I can help only with Indian business compliance questions, such as GST, MCA filings, ESI/PF, MSME rules, and regulatory deadlines.", "sources": []})
    passages = retrieve(question)
    if not passages:
        return jsonify({"status": "no_verified_source", "answer": "I could not find enough verified material in the Clauz X legal library for that question. Please ask a more specific compliance question.", "sources": []})
    try:
        answer = grounded_answer(question, passages)
    except Exception as exc:
        # The verified library remains useful if the optional AI provider is not
        # configured or is temporarily unavailable.  Do not claim that this was
        # an AI-generated answer: return the retrieved source passages verbatim.
        excerpts = " ".join(item["text"] for item in passages)
        provider_state = "not configured" if "GEMINI_API_KEY" in str(exc) else "temporarily unavailable"
        return jsonify({
            "status": "retrieval_only",
            "answer": f"The AI assistant is {provider_state}. Here is the relevant information from Clauz X's reviewed legal library: {excerpts}",
            "sources": passages,
        })
    audit(config.AUDIT_PATH, "grounded_question_answered", retrieved_sources=len(passages))
    return jsonify({"status": "grounded", "answer": answer, "sources": passages})


@app.get("/admin/review-queue")
def review_queue():
    queue = load(config.QUEUE_PATH, [])
    return jsonify([{k: item.get(k) for k in ("candidate_id", "status", "extraction_confidence", "fields_needing_human_verification", "document")} | {"obligation_name": item.get("candidate_rule", {}).get("obligation_name")} for item in queue])

@app.get("/admin/review-queue/<candidate_id>")
def review_detail(candidate_id):
    item = next((x for x in load(config.QUEUE_PATH, []) if x.get("candidate_id") == candidate_id), None)
    return jsonify(item) if item else error("CANDIDATE_NOT_FOUND", "Candidate was not found.", 404)

def _get_candidate(candidate_id):
    queue = load(config.QUEUE_PATH, []); index = next((i for i, x in enumerate(queue) if x.get("candidate_id") == candidate_id), None)
    return queue, index

@app.post("/admin/approve/<candidate_id>")
def approve(candidate_id):
    queue, index = _get_candidate(candidate_id)
    if index is None: return error("CANDIDATE_NOT_FOUND", "Candidate was not found.", 404)
    candidate = queue[index]
    if candidate["status"] != "pending_human_review": return error("INVALID_CANDIDATE_STATUS", "Only pending candidates can be approved.", 409)
    try: rule = ExtractedRule.model_validate(candidate["candidate_rule"]).model_dump()
    except ValidationError as exc: return error("INVALID_CANDIDATE", str(exc))
    if not candidate.get("document", {}).get("source_url") or not (rule.get("source_citation") or rule.get("source_title")):
        return error("MISSING_SOURCE_METADATA", "Approval requires source URL and source citation or title.", 422)
    rules = load(config.RULES_PATH, [])
    rule_id = rule.get("rule_id") or f"rule_{candidate_id.removeprefix('candidate_')}"
    if any(x.get("rule_id") == rule_id for x in rules): return error("DUPLICATE_RULE", "A rule with this ID already exists.", 409)
    rule.update({"rule_id": rule_id, "created_at": now(), "updated_at": now()}); rules.append(rule)
    reviewer = (request.get_json(silent=True) or {}).get("reviewer", "admin")
    candidate.update({"status": "approved", "approved_by": reviewer, "reviewed_at": now(), "review_notes": (request.get_json(silent=True) or {}).get("review_notes")})
    save(config.RULES_PATH, rules); save(config.QUEUE_PATH, queue); audit(config.AUDIT_PATH, "candidate_approved", candidate_id=candidate_id, rule_id=rule_id, user=reviewer)
    return jsonify({"candidate_id": candidate_id, "rule_id": rule_id, "status": "approved"})

@app.post("/admin/reject/<candidate_id>")
def reject(candidate_id):
    queue, index = _get_candidate(candidate_id)
    if index is None: return error("CANDIDATE_NOT_FOUND", "Candidate was not found.", 404)
    if queue[index]["status"] != "pending_human_review": return error("INVALID_CANDIDATE_STATUS", "Only pending candidates can be rejected.", 409)
    body = request.get_json(silent=True) or {}; queue[index].update({"status": "rejected", "approved_by": body.get("reviewer", "admin"), "reviewed_at": now(), "review_notes": body.get("review_notes")}); save(config.QUEUE_PATH, queue); audit(config.AUDIT_PATH, "candidate_rejected", candidate_id=candidate_id, user=queue[index]["approved_by"])
    return jsonify({"candidate_id": candidate_id, "status": "rejected"})

@app.post("/admin/monitor/run")
def monitor_run():
    if __package__ in (None, ""):
        from backend.monitor import run_monitor_cycle
    else:
        from .monitor import run_monitor_cycle
    return jsonify(run_monitor_cycle(dry_run=bool((request.get_json(silent=True) or {}).get("dry_run", False))))

@app.get("/admin/monitor/status")
def monitor_status():
    sources, state, queue = load(config.SOURCES_PATH, []), load(config.STATE_PATH, {}), load(config.QUEUE_PATH, [])
    return jsonify({"configured_sources": len(sources), "active_sources": sum(bool(s.get("active")) for s in sources), "sources": [{**source, "state": state.get(source.get("source_id"), {})} for source in sources], "latest_candidates": queue[-10:]})

@app.get("/admin/sources")
def sources():
    """Configured official sources; activation remains a deliberate file/config action."""
    return jsonify(load(config.SOURCES_PATH, []))

@app.get("/admin/regulatory-updates")
def regulatory_updates():
    """Official alert/feed records awaiting internal regulatory-operations triage."""
    return jsonify(load(config.UPDATES_PATH, []))

@app.post("/admin/regulatory-updates")
def intake_regulatory_update():
    """Receive a permitted official alert or licensed-feed update for internal triage."""
    body = request.get_json(force=True) or {}
    required = ("source_id", "title", "source_url")
    if any(not isinstance(body.get(key), str) or not body[key].strip() for key in required):
        return error("INVALID_UPDATE", "source_id, title, and source_url are required.")
    if not body["source_url"].startswith(("https://", "http://")):
        return error("INVALID_UPDATE", "source_url must be an HTTP(S) URL.")
    updates = load(config.UPDATES_PATH, [])
    fingerprint = hashlib.sha256(f"{body['source_id']}|{body['title']}|{body['source_url']}".encode()).hexdigest()[:16]
    if any(item.get("update_id") == f"update_{fingerprint}" for item in updates):
        return error("DUPLICATE_UPDATE", "This regulatory update is already queued.", 409)
    record = {
        "update_id": f"update_{fingerprint}", "source_id": body["source_id"], "title": body["title"],
        "source_url": body["source_url"], "pdf_url": body.get("pdf_url"), "reference_number": body.get("reference_number"),
        "published_date": body.get("published_date"), "summary": body.get("summary"),
        "received_via": body.get("received_via", "official_alert"), "received_at": now(),
        "status": "pending_internal_triage", "triaged_by": None, "triaged_at": None, "notes": None
    }
    updates.append(record); save(config.UPDATES_PATH, updates); audit(config.AUDIT_PATH, "regulatory_update_received", update_id=record["update_id"], source_id=record["source_id"])
    return jsonify(record), 201

@app.post("/internal/rules/drafts")
def create_internal_rule_draft():
    """Internal regulatory operations seeds a source-backed candidate; approval remains mandatory."""
    body = request.get_json(force=True) or {}
    try: rule = ExtractedRule.model_validate(body.get("candidate_rule", body)).model_dump()
    except ValidationError as exc: return error("INVALID_RULE_DRAFT", str(exc))
    if not rule.get("obligation_name") or not rule.get("source_url") or not (rule.get("source_citation") or rule.get("source_title")):
        return error("MISSING_SOURCE_METADATA", "A draft needs obligation_name, source_url, and source_citation or source_title.", 422)
    queue = load(config.QUEUE_PATH, [])
    source_url = rule["source_url"]
    fingerprint = hashlib.sha256(f"{rule['obligation_name']}|{source_url}|{rule.get('effective_from')}".encode()).hexdigest()[:16]
    candidate_id = f"candidate_ca_{fingerprint}"
    if any(item.get("candidate_id") == candidate_id for item in queue): return error("DUPLICATE_DRAFT", "An equivalent internal rule draft already exists.", 409)
    candidate = {**rule, "extraction_method": "internal_regulatory_operations", "simulated": False}
    entry = {"candidate_id": candidate_id, "candidate_rule": candidate,
        "document": {"title": rule.get("source_title"), "pdf_path": None, "source_url": source_url, "pdf_hash": None},
        "extracted_at": now(), "extraction_method": "internal_regulatory_operations", "simulated": False,
        "extraction_confidence": None, "fields_needing_human_verification": rule.get("fields_needing_human_verification", []),
        "status": "pending_human_review", "approved_by": None, "reviewed_at": None, "review_notes": body.get("review_notes")}
    queue.append(entry); save(config.QUEUE_PATH, queue); audit(config.AUDIT_PATH, "internal_rule_draft_created", candidate_id=candidate_id)
    return jsonify(entry), 201

@app.get("/internal/rule-catalog/status")
def rule_catalog_status():
    manifest = load(config.BASELINE_MANIFEST_PATH, {})
    return jsonify({"baseline": manifest, "live_rule_count": len(load(config.RULES_PATH, [])), "review_candidates": len(load(config.QUEUE_PATH, []))})

# --- Compliance Calendar & Business Endpoints ---

@app.get("/api/compliance/businesses")
def get_businesses():
    """List all businesses and their profiles."""
    return jsonify(list_businesses())

@app.post("/api/compliance/businesses")
def create_or_update_business():
    """Create or update a business profile and send its sign-in compliance summary."""
    try:
        body = request.get_json(force=True) or {}
        as_of = request.args.get("as_of") or body.get("as_of")
        record = save_or_update_business(body, as_of=as_of)
        audit(config.AUDIT_PATH, "business_saved", business_id=record["business_id"])

        # Send the sign-in summary after applicability is evaluated.
        # Enforce a 65s cooldown per phone number to respect WaSender free tier (1 msg/min) limit
        notification = None
        whatsapp_number = body.get("whatsapp_number") or (record.get("profile") or {}).get("whatsapp_number")
        business_name = body.get("business_name") or (record.get("profile") or {}).get("business_name") or "Your Business"
        obligations = record.get("obligations", [])
        if whatsapp_number:
            import time
            global _last_onboarding_sent
            if "_last_onboarding_sent" not in globals():
                _last_onboarding_sent = {}
            normalized_key = str(whatsapp_number).strip()
            last_ts = _last_onboarding_sent.get(normalized_key, 0.0)
            now_ts = time.time()

            if (now_ts - last_ts) >= 65:
                result = send_onboarding_summary(business_name, whatsapp_number, obligations)
                if result.status == "sent":
                    _last_onboarding_sent[normalized_key] = now_ts
                notification = result.model_dump()
                audit(config.AUDIT_PATH, "onboarding_whatsapp_dispatch",
                      business_id=record["business_id"],
                      status=result.status,
                      sid=result.sid,
                      error_code=result.error_code,
                      error_message=result.error_message)
            else:
                notification = {
                    "status": "throttled",
                    "reason": f"Cooldown active ({int(65 - (now_ts - last_ts))}s remaining to respect WaSender rate limit)"
                }

        return jsonify({**record, "whatsapp_notification": notification}), 200
    except (ValidationError, ValueError, TypeError) as exc:
        return error("INVALID_BUSINESS_PAYLOAD", str(exc))

@app.get("/api/compliance/businesses/<business_id>")
def get_business_detail(business_id):
    """Retrieve details and obligation calendar for a specific business."""
    biz = get_business(business_id)
    if not biz:
        return error("BUSINESS_NOT_FOUND", "Business was not found.", 404)
    return jsonify(biz)

@app.get("/api/compliance/businesses/<business_id>/calendar")
def get_business_calendar(business_id):
    """Retrieve computed compliance calendar entries for a business, with optional as_of date."""
    biz = get_business(business_id)
    if not biz:
        return error("BUSINESS_NOT_FOUND", "Business was not found.", 404)
    as_of = request.args.get("as_of")
    obligations = compute_obligations_calendar(biz.get("profile", {}), as_of=as_of)
    return jsonify({
        "business_id": business_id,
        "as_of": as_of or now()[:10],
        "obligations": [ob.model_dump() for ob in obligations]
    })

@app.post("/api/compliance/businesses/<business_id>/recompute")
def recompute_calendar_endpoint(business_id):
    """Trigger recomputation of calendar obligations against live rules."""
    body = request.get_json(silent=True) or {}
    as_of = body.get("as_of") or request.args.get("as_of")
    biz = recompute_business_calendar(business_id, as_of=as_of)
    if not biz:
        return error("BUSINESS_NOT_FOUND", "Business was not found.", 404)
    audit(config.AUDIT_PATH, "calendar_recomputed", business_id=business_id)
    return jsonify(biz)

# --- WhatsApp Deadline Reminders Endpoints ---

@app.post("/api/compliance/reminders/run")
def trigger_reminder_cycle():
    """Trigger an idempotent deadline reminder cycle, with optional as_of_date override."""
    body = request.get_json(silent=True) or {}
    as_of_date = body.get("as_of_date") or request.args.get("as_of_date")
    result = run_reminder_cycle(as_of_date=as_of_date)
    audit(config.AUDIT_PATH, "reminder_cycle_executed", as_of_date=result["as_of_date"], candidates=result["candidates_found"], sent=result["reminders_sent"], simulated=result["reminders_simulated"])
    return jsonify(result), 200

@app.get("/api/compliance/reminders/log")
def get_reminder_logs():
    """Admin / ops view of recent reminder logs."""
    logs = load(config.REMINDERS_PATH, [])
    # Support query filters
    status_filter = request.args.get("status")
    biz_filter = request.args.get("business_id")
    date_filter = request.args.get("date")
    limit = int(request.args.get("limit", 100))

    filtered = logs
    if status_filter:
        filtered = [l for l in filtered if l.get("status") == status_filter]
    if biz_filter:
        filtered = [l for l in filtered if l.get("business_id") == biz_filter]
    if date_filter:
        filtered = [l for l in filtered if l.get("date") == date_filter]

    # Return newest first
    filtered.reverse()
    return jsonify({
        "total": len(logs),
        "count": len(filtered[:limit]),
        "logs": filtered[:limit]
    })


# --- Compliance document verification ---

def _verification_profile(payload: dict) -> BusinessProfile:
    """Validate a JSON business profile consistently across verification routes."""
    return BusinessProfile.model_validate(payload)


# --- Contract Health Report ---

@app.post("/api/contracts/health")
def contract_health():
    """Run the India-focused first-pass template suite with Gemini analysis against text."""
    body = request.get_json(silent=True) or {}
    use_ai = str(body.get("use_ai", request.args.get("ai", "true"))).lower() != "false"
    try:
        report = run_contract_health_check(
            str(body.get("contract_text", "")), body.get("filename"), use_ai=use_ai
        )
        audit(config.AUDIT_PATH, "contract_health_check_run", filename=body.get("filename"), risk=report["overall_risk"])
        return jsonify(report), 200
    except ValueError as exc:
        return error("INVALID_CONTRACT", str(exc))


@app.post("/api/contracts/health/upload")
def contract_health_upload():
    """Extract a single PDF and return its Contract Health Report with Gemini analysis."""
    temporary_path: str | None = None
    use_ai = request.args.get("ai", "true").lower() != "false"
    try:
        uploaded = request.files.get("contract")
        if not uploaded or not uploaded.filename:
            return error("CONTRACT_REQUIRED", "Upload one contract PDF.")
        if not uploaded.filename.lower().endswith(".pdf"):
            return error("INVALID_FILE_TYPE", "Contract Health Report currently accepts PDF files only.")
        handle = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        temporary_path = handle.name
        handle.close()
        uploaded.save(temporary_path)
        if os.path.getsize(temporary_path) > config.MAX_DOCUMENT_BYTES:
            return error("FILE_TOO_LARGE", "The contract exceeds the size limit.", 413)
        extracted = extract_pdf_text(temporary_path)
        report = run_contract_health_check(extracted.get("text", ""), uploaded.filename, use_ai=use_ai)
        audit(config.AUDIT_PATH, "contract_health_check_uploaded", filename=uploaded.filename, risk=report["overall_risk"])
        return jsonify(report), 200
    except ValueError as exc:
        return error("INVALID_CONTRACT", str(exc))
    except Exception as exc:
        return error("CONTRACT_HEALTH_FAILED", f"Contract review could not complete: {exc}", 502)
    finally:
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass


@app.post("/api/contracts/health/pdf")
def contract_health_pdf():
    """Generate a structured, professional PDF for a Contract Health Report."""
    body = request.get_json(silent=True) or {}
    report = body.get("report")
    if not report:
        contract_text = body.get("contract_text")
        if not contract_text:
            return error("REPORT_OR_TEXT_REQUIRED", "Provide a 'report' object or 'contract_text' in request body.")
        use_ai = str(body.get("use_ai", "true")).lower() != "false"
        try:
            report = run_contract_health_check(contract_text, body.get("filename"), use_ai=use_ai)
        except ValueError as exc:
            return error("INVALID_CONTRACT", str(exc))

    try:
        pdf_bytes = build_contract_health_pdf(report)
        filename = report.get("filename") or "contract"
        clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(filename).stem)
        download_filename = f"Contract_Health_Report_{clean_name}.pdf"
        audit(config.AUDIT_PATH, "contract_health_pdf_generated", filename=filename)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=download_filename,
        )
    except Exception as exc:
        return error("PDF_GENERATION_FAILED", f"Could not generate PDF: {exc}", 500)


@app.get("/api/contracts/health/pdf/download/<report_id>.pdf")
def download_contract_health_pdf(report_id: str):
    """Serve a saved Contract Health Report PDF."""
    pdf_path = config.DOCUMENTS_DIR / "reports" / f"{report_id}.pdf"
    if not pdf_path.exists():
        return error("FILE_NOT_FOUND", "Requested Contract Health Report PDF was not found.", 404)
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Contract_Health_Report_{report_id}.pdf",
    )


@app.post("/api/contracts/health/whatsapp")
def contract_health_whatsapp():
    """Generate Contract Health PDF and send report summary + PDF download link via WhatsApp."""
    body = request.get_json(silent=True) or {}
    whatsapp_number = body.get("whatsapp_number") or body.get("to")
    if not whatsapp_number:
        return error("PHONE_NUMBER_REQUIRED", "Provide a 'whatsapp_number' in request body.")

    report = body.get("report")
    if not report:
        contract_text = body.get("contract_text")
        if not contract_text:
            return error("REPORT_OR_TEXT_REQUIRED", "Provide a 'report' object or 'contract_text' in request body.")
        use_ai = str(body.get("use_ai", "true")).lower() != "false"
        try:
            report = run_contract_health_check(contract_text, body.get("filename"), use_ai=use_ai)
        except ValueError as exc:
            return error("INVALID_CONTRACT", str(exc))

    try:
        pdf_bytes = build_contract_health_pdf(report)
        report_id = report.get("id") or f"rep_{uuid.uuid4().hex[:12]}"
        reports_dir = config.DOCUMENTS_DIR / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        pdf_file_path = reports_dir / f"{report_id}.pdf"
        pdf_file_path.write_bytes(pdf_bytes)

        base_url = (config.PUBLIC_BASE_URL or request.host_url).rstrip('/')
        download_url = f"{base_url}/api/contracts/health/pdf/download/{report_id}.pdf"

        send_res = send_contract_health_report_whatsapp(
            whatsapp_number=whatsapp_number,
            report=report,
            pdf_download_url=download_url,
        )

        audit(
            config.AUDIT_PATH,
            "contract_health_whatsapp_sent",
            filename=report.get("filename"),
            whatsapp_number=whatsapp_number,
            status=send_res.status,
            sid=send_res.sid,
        )

        return jsonify({
            "success": send_res.status in ("sent", "simulated"),
            "status": send_res.status,
            "sid": send_res.sid,
            "pdf_download_url": download_url,
            "error_code": send_res.error_code,
            "error_message": send_res.error_message,
        }), 200

    except Exception as exc:
        return error("WHATSAPP_SEND_FAILED", f"Could not process WhatsApp report request: {exc}", 500)


@app.post("/api/compliance/check")
def compliance_check():
    if __package__ in (None, ""):
        from backend.verification_engine import run_compliance_check
    else:
        from .verification_engine import run_compliance_check
    body = request.get_json(silent=True) or {}
    try:
        profile = _verification_profile(body.get("business_profile") or {})
        docs = body.get("uploaded_docs") or {}
        if not isinstance(docs, dict):
            return error("INVALID_UPLOADED_DOCS", "uploaded_docs must map obligation IDs to extracted document text.")
        report = run_compliance_check(profile, docs, body.get("verification_date"))
        stored = save_compliance_check(report.model_dump())
        audit(config.AUDIT_PATH, "compliance_check_run", business_id=profile.business_id, score=report.compliance_score, risk=report.risk_level)
        return jsonify(stored), 200
    except (ValidationError, TypeError, ValueError) as exc:
        return error("INVALID_COMPLIANCE_CHECK", str(exc))
    except Exception as exc:
        return error("COMPLIANCE_CHECK_FAILED", f"Compliance verification could not complete: {exc}", 502)


@app.post("/api/compliance/check/upload")
def compliance_check_upload():
    """Extract text from PDF uploads keyed by obligation ID, then verify them."""
    if __package__ in (None, ""):
        from backend.verification_engine import run_compliance_check
    else:
        from .verification_engine import run_compliance_check
    temporary_paths: list[str] = []
    try:
        profile_data = json.loads(request.form.get("business_profile", "{}"))
        profile = _verification_profile(profile_data)
        manifest = json.loads(request.form.get("manifest", "{}"))
        if not isinstance(manifest, dict):
            return error("INVALID_MANIFEST", "manifest must map upload field names to obligation IDs.")
        documents: dict[str, str] = {}
        for field, uploaded in request.files.items():
            if not uploaded.filename:
                continue
            if not uploaded.filename.lower().endswith(".pdf"):
                return error("INVALID_FILE_TYPE", f"File '{uploaded.filename}' is not a PDF.")
            handle = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            temporary_paths.append(handle.name); handle.close(); uploaded.save(handle.name)
            if os.path.getsize(handle.name) > config.MAX_DOCUMENT_BYTES:
                return error("FILE_TOO_LARGE", f"File '{uploaded.filename}' exceeds the size limit.", 413)
            extracted = extract_pdf_text(handle.name)
            documents[manifest.get(field, field)] = extracted.get("text", "")
        report = run_compliance_check(profile, documents, request.form.get("verification_date"))
        stored = save_compliance_check(report.model_dump())
        audit(config.AUDIT_PATH, "compliance_check_uploaded", business_id=profile.business_id, uploaded_files=len(documents), score=report.compliance_score)
        return jsonify(stored), 200
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        return error("INVALID_COMPLIANCE_UPLOAD", str(exc))
    except Exception as exc:
        return error("COMPLIANCE_CHECK_FAILED", f"Upload compliance verification failed: {exc}", 502)
    finally:
        for path in temporary_paths:
            try: os.unlink(path)
            except OSError: pass


@app.post("/api/compliance/check/reverify")
def compliance_check_reverify():
    if __package__ in (None, ""):
        from backend.verification_engine import reverify_obligation
    else:
        from .verification_engine import reverify_obligation
    body = request.get_json(silent=True) or {}
    try:
        obligation_id = body.get("obligation_id")
        if not obligation_id:
            return error("OBLIGATION_ID_REQUIRED", "obligation_id is required.")
        profile_data = body.get("business_profile")
        if not profile_data and body.get("business_id"):
            business = get_business(body["business_id"])
            profile_data = business and business.get("profile")
        if not profile_data:
            return error("BUSINESS_PROFILE_REQUIRED", "business_profile or a valid business_id is required.")
        profile = _verification_profile(profile_data)
        previous = next(iter(list_compliance_checks(profile.business_id)), None)
        report = reverify_obligation(obligation_id, profile, body.get("document_text", ""), previous, body.get("verification_date"))
        stored = save_compliance_check(report.model_dump())
        audit(config.AUDIT_PATH, "obligation_reverified", business_id=profile.business_id, obligation_id=obligation_id)
        return jsonify(stored), 200
    except (ValidationError, TypeError, ValueError) as exc:
        return error("INVALID_REVERIFY_REQUEST", str(exc))
    except Exception as exc:
        return error("REVERIFY_FAILED", f"Re-verification failed: {exc}", 502)


@app.get("/api/compliance/businesses/<business_id>/checks")
def get_business_compliance_checks(business_id):
    checks = list_compliance_checks(business_id)
    return jsonify({"business_id": business_id, "total": len(checks), "checks": checks})

if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=False)
