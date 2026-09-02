"""Gemini-powered candidate extraction. This module never writes live rules."""
import re
from pathlib import Path
from .config import DEMO_MODE
from .llm_client import structured
from .models import ExtractedRule

PROMPT = (Path(__file__).parent / "prompts" / "rule_extraction_prompt.txt").read_text()

def simulate_extraction(notification_text: str) -> dict:
    """Clearly labelled offline demo candidate; it remains subject to review."""
    headcount = re.search(r"(\d+)\s+(?:or more\s+)?(?:employees|persons)", notification_text, re.I)
    return ExtractedRule(obligation_name="Demo regulatory obligation", headcount_min=int(headcount.group(1)) if headcount else None,
        description="Simulated extraction; human verification required.", source_citation=None,
        extraction_confidence=0.0, fields_needing_human_verification=["all_fields"]).model_dump()

def semantic_validate(candidate: dict, source_text: str) -> dict:
    rule = ExtractedRule.model_validate(candidate).model_dump()
    flags = set(rule["fields_needing_human_verification"])
    for field in ("turnover_min", "turnover_max", "headcount_min", "headcount_max", "effective_from", "effective_to"):
        value = rule.get(field)
        if value is not None and str(value) not in source_text:
            rule[field] = None; flags.add(field)
    if not rule.get("obligation_name"): flags.add("obligation_name")
    rule["fields_needing_human_verification"] = sorted(flags)
    return rule

def call_gemini_extraction(notification_text: str) -> dict:
    try:
        result = structured(PROMPT.format(notification_text=notification_text), ExtractedRule)
        return {**semantic_validate(result, notification_text), "extraction_method": "gemini", "simulated": False}
    except Exception:
        if not DEMO_MODE: raise
        return {**simulate_extraction(notification_text), "extraction_method": "simulation", "simulated": True}
