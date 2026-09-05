import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = BASE_DIR / "documents"
SNAPSHOTS_DIR = DATA_DIR / "source_snapshots"
RULES_PATH = DATA_DIR / "rules.json"
BASELINE_RULES_PATH = DATA_DIR / "baseline_rules.json"
BASELINE_MANIFEST_PATH = DATA_DIR / "baseline_manifest.json"
QUEUE_PATH = DATA_DIR / "pending_review_queue.json"
STATE_PATH = DATA_DIR / "source_state.json"
SOURCES_PATH = DATA_DIR / "sources.json"
AUDIT_PATH = DATA_DIR / "audit_log.json"
UPDATES_PATH = DATA_DIR / "regulatory_update_queue.json"
BUSINESSES_PATH = DATA_DIR / "businesses.json"
REMINDERS_PATH = DATA_DIR / "reminder_logs.json"
LEGAL_CORPUS_PATH = DATA_DIR / "legal_corpus.json"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
REQUEST_TIMEOUT = int(os.getenv("MONITOR_REQUEST_TIMEOUT", "20"))
MAX_DOCUMENT_BYTES = int(os.getenv("MAX_DOCUMENT_BYTES", "15000000"))
# Background monitoring is deliberately opt-in. Production deployments should run
# this process once (for example through a platform scheduler), not per web worker.
ENABLE_REGULATORY_MONITOR = os.getenv("ENABLE_REGULATORY_MONITOR", "false").lower() == "true"
MONITOR_INTERVAL_MINUTES = max(5, int(os.getenv("MONITOR_INTERVAL_MINUTES", "360")))

# WhatsApp Provider — WaSenderAPI
WASENDER_API_KEY = os.getenv("WASENDER_API_KEY")  # Bearer token from wasenderapi.com dashboard

def ensure_storage() -> None:
    for directory in (DATA_DIR, DOCUMENTS_DIR, SNAPSHOTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    for path, empty in (
        (RULES_PATH, []),
        (BASELINE_RULES_PATH, []),
        (BASELINE_MANIFEST_PATH, {"version": "0.0.0", "status": "awaiting_internal_release"}),
        (QUEUE_PATH, []),
        (STATE_PATH, {}),
        (AUDIT_PATH, []),
        (UPDATES_PATH, []),
        (BUSINESSES_PATH, []),
        (REMINDERS_PATH, []),
        (LEGAL_CORPUS_PATH, []),
    ):
        if not path.exists():
            path.write_text(__import__("json").dumps(empty, indent=2), encoding="utf-8")
