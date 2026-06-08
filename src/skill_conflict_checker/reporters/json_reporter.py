from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from skill_conflict_checker.models import Conflict


class JsonReporter:
    """Writes conflict results as JSON to a file or stdout."""

    def __init__(self, output_path: str | None = None) -> None:
        self._output_path = Path(output_path) if output_path else None

    def report(self, conflicts: list[Conflict], source_count: int) -> None:
        payload = {
            "source_count": source_count,
            "conflict_count": len(conflicts),
            "conflicts": [self._serialize(c) for c in conflicts],
        }
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        if self._output_path:
            self._output_path.write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text + "\n")

    def _serialize(self, conflict: Conflict) -> dict:
        return {
            "severity": conflict.severity.value,
            "category": conflict.category,
            "title": conflict.title,
            "description": conflict.description,
            "source_a": conflict.sources.source_a,
            "source_b": conflict.sources.source_b,
            "recommendation": conflict.recommendation,
        }
