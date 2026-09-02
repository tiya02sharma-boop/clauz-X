import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def now() -> str: return datetime.now(timezone.utc).isoformat()

def load(path: Path, default: Any):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except (json.JSONDecodeError, OSError):
        return default

def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.stem}_{os.getpid()}_{uuid.uuid4().hex[:8]}{path.suffix}.tmp")
    try:
        temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        temp.replace(path)
    except Exception:
        # Fallback to direct write if atomic rename is unavailable
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        if temp.exists():
            try: temp.unlink()
            except OSError: pass

def audit(path: Path, action: str, **details: Any) -> None:
    try:
        events = load(path, [])
        events.append({"timestamp": now(), "action": action, **details})
        save(path, events)
    except Exception as e:
        # Audit logging failure should not crash the request
        pass

