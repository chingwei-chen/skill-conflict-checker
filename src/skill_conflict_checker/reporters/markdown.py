from __future__ import annotations

from pathlib import Path

from skill_conflict_checker.models import Conflict, Severity


class MarkdownReporter:
    """Writes conflict results as a Markdown report to a file."""

    def __init__(self, output_path: str) -> None:
        self._output_path = Path(output_path)

    def report(self, conflicts: list[Conflict], source_count: int) -> None:
        lines: list[str] = [
            "# Skill Conflict Report\n",
            f"**Sources scanned:** {source_count}  ",
            f"**Conflicts found:** {len(conflicts)}\n",
        ]

        if not conflicts:
            lines.append("_No conflicts detected._\n")
        else:
            for sev in (Severity.HIGH, Severity.MEDIUM, Severity.LOW):
                section = [c for c in conflicts if c.severity == sev]
                if section:
                    lines.append(f"## {sev.emoji} {sev.value.upper()} Severity\n")
                    for c in section:
                        lines.extend(self._conflict_block(c))

        self._output_path.write_text("\n".join(lines), encoding="utf-8")

    def _conflict_block(self, conflict: Conflict) -> list[str]:
        return [
            f"### {conflict.title}",
            f"- **Category:** {conflict.category}",
            f"- **Sources:** `{conflict.sources.source_a}` ↔ `{conflict.sources.source_b}`",
            f"\n{conflict.description}\n",
            f"**Recommendation:** {conflict.recommendation}\n",
            "---\n",
        ]
