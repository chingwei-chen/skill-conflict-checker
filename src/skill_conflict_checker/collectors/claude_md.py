from __future__ import annotations

from pathlib import Path

from skill_conflict_checker.models import SkillSource


class ClaudeMdCollector:
    """Loads CLAUDE.md as the global session rules source."""

    def __init__(self, claude_dir: Path) -> None:
        self._claude_dir = claude_dir

    @property
    def source_type(self) -> str:
        return "claude_md"

    def collect(self) -> list[SkillSource]:
        claude_md = self._claude_dir / "CLAUDE.md"
        if not claude_md.exists():
            return []
        content = claude_md.read_text(encoding="utf-8")
        return [
            SkillSource(
                name="CLAUDE.md (global instructions)",
                source_type=self.source_type,
                source_path=str(claude_md),
                description="Global user instructions injected into every Claude Code session",
                content=content,
            )
        ]
