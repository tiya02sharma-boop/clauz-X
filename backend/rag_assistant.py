"""Small, auditable retrieval layer for Ask Clauz X."""
import re
from typing import Any
from . import config
from .storage import load

DOMAIN_TERMS = {"gst", "gstr", "tax", "tds", "mca", "roc", "company", "director", "esi", "esic", "pf", "epf", "msme", "filing", "return", "registration", "compliance", "penalty", "due", "deadline"}

def _tokens(value: str) -> set[str]: return set(re.findall(r"[a-z0-9]+", value.lower()))
def is_compliance_question(question: str) -> bool: return bool(_tokens(question) & DOMAIN_TERMS)
def retrieve(question: str, limit: int = 3) -> list[dict[str, Any]]:
    query = _tokens(question); ranked = []
    for item in load(config.LEGAL_CORPUS_PATH, []):
        text = " ".join(str(item.get(key, "")) for key in ("title", "citation", "text", "tags"))
        score = len(query & _tokens(text))
        if score >= 2: ranked.append((score, item))
    return [item for _, item in sorted(ranked, key=lambda entry: entry[0], reverse=True)[:limit]]
