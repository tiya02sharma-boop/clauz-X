import argparse, hashlib, logging, re, sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import requests
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend import config
    from backend.change_detector import detect_new_regulatory_entries
    from backend.extract_rule import call_gemini_extraction
    from backend.pdf_extractor import extract_pdf_text
    from backend.storage import audit, load, now, save
else:
    from . import config
    from .change_detector import detect_new_regulatory_entries
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
                if not entry.get("pdf_url"): continue
                try:
                    pdf_path, pdf_hash = _download_pdf(sid, entry["pdf_url"]); summary["pdfs_downloaded"] += 1; audit(config.AUDIT_PATH, "pdf_downloaded", source_id=sid, pdf_hash=pdf_hash)
                    extracted = extract_pdf_text(pdf_path)
                    if extracted["extraction_failed"]: audit(config.AUDIT_PATH, "pdf_extraction_failed", source_id=sid, pdf_hash=pdf_hash); continue
                    summary["ai_calls"] += 1; candidate = call_gemini_extraction(extracted["text"]); summary["rules_extracted"] += 1
                    doc = {"title": entry.get("title"), "pdf_path": str(pdf_path), "source_url": entry.get("source_url") or entry.get("pdf_url"), "pdf_hash": pdf_hash}
                    # Preserve entry-level traceability even when the document did not
                    # explicitly provide a citation. Reviewers still decide promotion.
                    if not candidate.get("source_title"): candidate["source_title"] = entry.get("title")
                    if not candidate.get("source_url"): candidate["source_url"] = doc["source_url"]
                    if not _candidate_exists(queue, doc, candidate) and not dry_run:
                        cid = "candidate_" + hashlib.sha256((pdf_hash + str(candidate)).encode()).hexdigest()[:12]
                        queue.append({"candidate_id": cid, "candidate_rule": candidate, "document": doc, "extracted_at": now(), "extraction_method": candidate["extraction_method"], "simulated": candidate["simulated"], "extraction_confidence": candidate.get("extraction_confidence"), "fields_needing_human_verification": candidate.get("fields_needing_human_verification", []), "status": "pending_human_review", "approved_by": None, "reviewed_at": None, "review_notes": None}); summary["review_candidates_created"] += 1; audit(config.AUDIT_PATH, "candidate_created", candidate_id=cid)
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
