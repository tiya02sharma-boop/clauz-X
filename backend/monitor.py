import argparse, hashlib, logging, re, sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend import config
    from backend.change_detector import detect_new_regulatory_entries
    from backend.embeddings import embed_texts
    from backend.extract_rule import call_gemini_extraction
    from backend.pdf_extractor import extract_pdf_text
    from backend.storage import audit, load, now, save
else:
    from . import config
    from .change_detector import detect_new_regulatory_entries
    from .embeddings import embed_texts
    from .extract_rule import call_gemini_extraction
    from .pdf_extractor import extract_pdf_text
    from .storage import audit, load, now, save

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

class SourceFetchError(RuntimeError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)

class _RegulatoryPageText(HTMLParser):
    """Keeps human-visible text plus document links; drops script/style noise."""
    def __init__(self):
        super().__init__(); self.parts = []; self._ignored = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}: self._ignored += 1
        if tag == "a" and not self._ignored:
            href = dict(attrs).get("href")
            if href: self.parts.append(f" [link:{href}] ")
    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self._ignored: self._ignored -= 1
    def handle_data(self, data):
        if not self._ignored: self.parts.append(data)

def normalize_content(content: str) -> str:
    parser = _RegulatoryPageText()
    try:
        parser.feed(content); content = " ".join(parser.parts)
    except Exception:
        # Malformed government HTML must not break the whole monitoring cycle.
        content = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<[^>]+>", " ", content, flags=re.I | re.S)
    return re.sub(r"\s+", " ", content).strip()

def fetch_source(url: str) -> dict:
    try:
        response = requests.get(url, timeout=config.REQUEST_TIMEOUT, headers={
            "User-Agent": "ClauzX-RegulatoryMonitor/1.0 (regulatory monitoring; contact required before production use)",
            "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9"
        })
    except requests.exceptions.SSLError as error:
        raise SourceFetchError("TLS_VERIFICATION_FAILED", "The source TLS certificate could not be verified. Do not disable TLS verification; use the regulator's supported feed or resolve its certificate chain.") from error
    except requests.exceptions.Timeout as error:
        raise SourceFetchError("SOURCE_TIMEOUT", "The source did not respond before the configured timeout.") from error
    except requests.exceptions.RequestException as error:
        raise SourceFetchError("SOURCE_CONNECTION_FAILED", "The source could not be reached from this environment.") from error
    if response.status_code in (401, 403):
        raise SourceFetchError("SOURCE_ACCESS_DENIED", "The regulator rejected automated access. Use an official API/RSS/download feed or obtain permission; the monitor will not bypass access controls.")
    if response.status_code == 404:
        raise SourceFetchError("SOURCE_URL_NOT_FOUND", "The configured source URL returned 404. Update it to the regulator's current notices or circulars listing.")
    try: response.raise_for_status()
    except requests.exceptions.HTTPError as error: raise SourceFetchError("SOURCE_HTTP_ERROR", f"The source returned HTTP {response.status_code}.") from error
    if not response.text.strip(): raise ValueError("Source returned empty content")
    return {"url": url, "status_code": response.status_code, "raw_content": response.text, "fetched_at": now()}

def _snapshot_path(source_id: str, content_hash: str) -> Path: return config.SNAPSHOTS_DIR / f"{source_id}-{content_hash}.json"

def _download_pdf(source_id: str, url: str) -> tuple[Path, str]:
    response = requests.get(url, timeout=config.REQUEST_TIMEOUT, stream=True, headers={"User-Agent": "ClauzX-RegulatoryMonitor/1.0"}); response.raise_for_status()
    chunks, total = [], 0
    for chunk in response.iter_content(65536):
        total += len(chunk)
        if total > config.MAX_DOCUMENT_BYTES: raise ValueError("Document exceeds configured size limit")
        chunks.append(chunk)
    blob = b"".join(chunks); digest = hashlib.sha256(blob).hexdigest(); path = config.DOCUMENTS_DIR / source_id / f"{digest}.pdf"; path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists(): path.write_bytes(blob)
    return path, digest

def _candidate_exists(queue: list, document: dict, candidate: dict) -> bool:
    for item in queue:
        old = item.get("document", {}); rule = item.get("candidate_rule", {})
        if document.get("pdf_hash") and document.get("pdf_hash") == old.get("pdf_hash"): return True
        if document.get("source_url") and document.get("source_url") == old.get("source_url") and candidate.get("obligation_name") == rule.get("obligation_name"): return True
    return False

def _absolute_url(url: str | None, page_url: str) -> str | None:
    """Turn an AI-detected relative link into a traceable HTTP(S) URL."""
    if not url:
        return None
    resolved = urljoin(page_url, url)
    return resolved if urlparse(resolved).scheme in {"http", "https"} else None

def _entry_document_text(entry: dict) -> tuple[str | None, Path | None, str | None]:
    """Prefer an official linked PDF, falling back to the website notice itself."""
    if entry.get("pdf_url"):
        pdf_path, pdf_hash = _download_pdf(entry["source_id"], entry["pdf_url"])
        extracted = extract_pdf_text(pdf_path)
        return (None if extracted["extraction_failed"] else extracted["text"]), pdf_path, pdf_hash
    text = "\n".join(part for part in (entry.get("title"), entry.get("summary")) if part)
    return (text or None), None, None

def _queue_candidate(queue: list, candidate: dict, document: dict) -> bool:
    if _candidate_exists(queue, document, candidate):
        return False
    fingerprint = document.get("pdf_hash") or f"{document.get('source_url')}|{candidate.get('obligation_name')}"
    cid = "candidate_" + hashlib.sha256(fingerprint.encode()).hexdigest()[:12]
    queue.append({"candidate_id": cid, "candidate_rule": candidate, "document": document,
                  "extracted_at": now(), "extraction_method": candidate["extraction_method"],
                  "simulated": candidate["simulated"], "extraction_confidence": candidate.get("extraction_confidence"),
                  "fields_needing_human_verification": candidate.get("fields_needing_human_verification", []),
                  "status": "pending_human_review", "approved_by": None, "reviewed_at": None,
                  "review_notes": None})
    audit(config.AUDIT_PATH, "candidate_created", candidate_id=cid)
    return True

# Administrative noise keywords (fallback / secondary signal)
ADMINISTRATIVE_NOISE_KEYWORDS = [
    "helpdesk", "portal maintenance", "scheduled downtime", "server maintenance",
    "call center", "toll free", "user manual", "system upgrade", "technical glitch",
    "portal unavailable", "holiday notice", "office closed", "grievance redressal"
]

RELEVANT_NOTIFICATION_EXAMPLES = [
    "Notification No. 12/2026: Extension of due date for filing Form GSTR-3B for August 2026",
    "Circular No. 04/2026: Clarification on applicability of Tax Deducted at Source on e-commerce operators",
    "MCA Notification: Amendments to Companies Rules regarding annual DIR-3 KYC",
    "EPFO Circular: Revision of wage ceiling for Employees Provident Fund coverage",
    "CBIC Notification: Mandatory e-invoicing for businesses with turnover exceeding 5 Crore",
]

NOISE_NOTIFICATION_EXAMPLES = [
    "Advisory: GST Portal will remain unavailable for scheduled maintenance on Sunday",
    "Helpdesk contact numbers updated for technical assistance during filing",
    "Circular regarding office holidays and non-working days for year 2026",
    "Tender notice for procurement of office laptops and computer peripherals",
    "User manual released for navigating newly designed MCA21 portal interface",
]

_REF_EMBEDDINGS = None


def _get_reference_embeddings():
    global _REF_EMBEDDINGS
    if _REF_EMBEDDINGS is None:
        rel_vecs = embed_texts(RELEVANT_NOTIFICATION_EXAMPLES, task_instruction=None)
        noise_vecs = embed_texts(NOISE_NOTIFICATION_EXAMPLES, task_instruction=None)
        _REF_EMBEDDINGS = (rel_vecs, noise_vecs)
    return _REF_EMBEDDINGS


def ai_read_and_filter(title: str) -> bool:
    """Filter out administrative noise notices using semantic embeddings with keyword fallback.

    Returns True if the notice is relevant, False if it is administrative noise.
    """
    if not title or not title.strip():
        return False

    t_lower = title.lower()
    keyword_hit = any(kw in t_lower for kw in ADMINISTRATIVE_NOISE_KEYWORDS)

    try:
        rel_vecs, noise_vecs = _get_reference_embeddings()
        title_vec = embed_texts([title], task_instruction=None)[0]
        import numpy as np
        t_arr = np.array(title_vec)
        t_norm = float(np.linalg.norm(t_arr)) or 1.0

        rel_sims = [float(np.dot(t_arr, np.array(r)) / (t_norm * (float(np.linalg.norm(r)) or 1.0))) for r in rel_vecs]
        noise_sims = [float(np.dot(t_arr, np.array(n)) / (t_norm * (float(np.linalg.norm(n)) or 1.0))) for n in noise_vecs]

        max_rel = max(rel_sims)
        max_noise = max(noise_sims)

        # Classified as noise if semantic similarity to noise examples is higher
        if max_noise > max_rel:
            return False
        # Fallback check
        if keyword_hit:
            return False
        return True
    except Exception as exc:
        log.warning("Embedding similarity check failed for notice '%s', falling back to keyword filter: %s", title, exc)
        return not keyword_hit


def run_monitor_cycle(dry_run: bool = False, sources=None) -> dict:
    config.ensure_storage(); sources = sources if sources is not None else load(config.SOURCES_PATH, [])
    state, queue = load(config.STATE_PATH, {}), load(config.QUEUE_PATH, [])
    summary = {"sources_checked": 0, "sources_changed": 0, "ai_calls": 0, "new_entries_found": 0, "pdfs_downloaded": 0, "rules_extracted": 0, "review_candidates_created": 0, "failures": []}
    for source in (s for s in sources if s.get("active")):
        summary["sources_checked"] += 1; sid = source["source_id"]
        try:
            fetched = fetch_source(source["url"]); normalized = normalize_content(fetched["raw_content"]); digest = hashlib.sha256(normalized.encode()).hexdigest(); old = state.get(sid, {}); previous_hash = old.get("last_hash")
            snapshot = {"source_id": sid, "timestamp": now(), "hash": digest, "normalized_content": normalized}; save(_snapshot_path(sid, digest), snapshot); audit(config.AUDIT_PATH, "source_fetched", source_id=sid, hash=digest)
            if not previous_hash:
                state[sid] = {"url": source["url"], "last_hash": digest, "last_checked": now(), "last_status": "baseline_created"}; log.info("Initial baseline created for %s", sid); audit(config.AUDIT_PATH, "source_baselined", source_id=sid)
                continue
            if digest == previous_hash:
                state[sid].update({"last_checked": now(), "last_status": "unchanged"}); log.info("Source unchanged — Gemini skipped: %s", sid); audit(config.AUDIT_PATH, "source_unchanged", source_id=sid); continue
            summary["sources_changed"] += 1; previous = load(_snapshot_path(sid, previous_hash), {}).get("normalized_content", ""); summary["ai_calls"] += 1; audit(config.AUDIT_PATH, "ai_change_detection_started", source_id=sid)
            entries = detect_new_regulatory_entries(normalized, previous); summary["new_entries_found"] += len(entries); audit(config.AUDIT_PATH, "ai_change_detection_completed", source_id=sid, entries=len(entries))
            for entry in entries:
                filter_text = " ".join(part for part in (entry.get("title"), entry.get("summary")) if part)
                if not ai_read_and_filter(filter_text):
                    log.info("Filtered administrative/noise notice: %s", filter_text)
                    continue
                try:
                    entry = {**entry, "source_id": sid,
                             "pdf_url": _absolute_url(entry.get("pdf_url"), source["url"]),
                             "source_url": _absolute_url(entry.get("source_url"), source["url"]) or source["url"]}
                    notice_text, pdf_path, pdf_hash = _entry_document_text(entry)
                    if pdf_path:
                        summary["pdfs_downloaded"] += 1; audit(config.AUDIT_PATH, "pdf_downloaded", source_id=sid, pdf_hash=pdf_hash)
                    if not notice_text:
                        if pdf_hash: audit(config.AUDIT_PATH, "pdf_extraction_failed", source_id=sid, pdf_hash=pdf_hash)
                        continue
                    summary["ai_calls"] += 1; candidate = call_gemini_extraction(notice_text); summary["rules_extracted"] += 1
                    doc = {"title": entry.get("title"), "pdf_path": str(pdf_path) if pdf_path else None, "source_url": entry["source_url"], "pdf_hash": pdf_hash}
                    # Preserve entry-level traceability even when the document did not
                    # explicitly provide a citation. Reviewers still decide promotion.
                    if not candidate.get("source_title"): candidate["source_title"] = entry.get("title")
                    if not candidate.get("source_url"): candidate["source_url"] = doc["source_url"]
                    if not dry_run and _queue_candidate(queue, candidate, doc):
                        summary["review_candidates_created"] += 1
                except Exception as error: summary["failures"].append({"source_id": sid, "entry": entry.get("title"), "error": str(error)})
            state[sid] = {"url": source["url"], "last_hash": digest, "last_checked": now(), "last_status": "changed"}
        except SourceFetchError as error:
            failure = {"source_id": sid, "code": error.code, "error": str(error)}
            summary["failures"].append(failure); state.setdefault(sid, {"url": source.get("url")}).update({"last_checked": now(), "last_status": "failed", "failure": failure}); audit(config.AUDIT_PATH, "source_failed", source_id=sid, code=error.code)
        except Exception as error:
            failure = {"source_id": sid, "code": "MONITOR_PROCESSING_FAILED", "error": str(error)}
            summary["failures"].append(failure); state.setdefault(sid, {"url": source.get("url")}).update({"last_checked": now(), "last_status": "failed", "failure": failure}); audit(config.AUDIT_PATH, "source_failed", source_id=sid, code="MONITOR_PROCESSING_FAILED")
    if not dry_run: save(config.STATE_PATH, state); save(config.QUEUE_PATH, queue)
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--once", action="store_true"); parser.add_argument("--dry-run", action="store_true"); args = parser.parse_args(); print(run_monitor_cycle(dry_run=args.dry_run))
