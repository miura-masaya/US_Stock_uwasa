"""JSON persistence for rumor-analysis results."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_json(records: list[dict[str, Any]], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination
