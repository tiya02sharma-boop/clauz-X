from pathlib import Path
from .llm_client import structured
from .models import RegulatoryEntries

PROMPT = (Path(__file__).parent / "prompts" / "change_detection_prompt.txt").read_text()

def detect_new_regulatory_entries(current_content: str, previous_content: str) -> list[dict]:
    result = structured(PROMPT.format(current_content=current_content, previous_content=previous_content), RegulatoryEntries)
    parsed = RegulatoryEntries.model_validate(result)
    entries, seen = [], set()
    for entry in parsed.entries:
        if not entry.title or not entry.title.strip():
            continue
        key = (entry.title.casefold(), entry.pdf_url or entry.source_url or "")
        if key not in seen: entries.append(entry.model_dump()); seen.add(key)
    return entries
