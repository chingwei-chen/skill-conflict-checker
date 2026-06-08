from __future__ import annotations

from pathlib import Path

from skill_conflict_checker.models import SkillSource

_MAX_EXPAND_DEPTH = 5


def _expand_at_refs(content: str, base_dir: Path, depth: int = 0) -> str:
    """Recursively expand @filename references, mirroring Claude Code's behaviour."""
    if depth >= _MAX_EXPAND_DEPTH:
        return content
    lines: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("@") and len(stripped) > 1:
            ref_path = base_dir / stripped[1:]
            ref_path = Path(str(ref_path).replace("~", str(Path.home())))
            if ref_path.exists() and ref_path.is_file():
                try:
                    ref_content = ref_path.read_text(encoding="utf-8")
                    expanded = _expand_at_refs(ref_content, ref_path.parent, depth + 1)
                    lines.append(f"# [expanded from {ref_path.name}]")
                    lines.append(expanded)
                    continue
                except OSError:
                    pass
        lines.append(line)
    return "\n".join(lines)


class ClaudeMdCollector:
    """Loads ~/.claude/CLAUDE.md as the global session rules source.

    Expands @file references the same way Claude Code does at runtime,
    so the conflict analyzer sees the actual assembled instruction text.
    """

    def __init__(self, claude_dir: Path) -> None:
        self._claude_dir = claude_dir

    @property
    def source_type(self) -> str:
        return "claude_md"

    def collect(self) -> list[SkillSource]:
        claude_md = self._claude_dir / "CLAUDE.md"
        if not claude_md.exists():
            return []
        raw = claude_md.read_text(encoding="utf-8")
        expanded = _expand_at_refs(raw, self._claude_dir)
        return [
            SkillSource(
                name="CLAUDE.md (global instructions)",
                source_type=self.source_type,
                source_path=str(claude_md),
                description="Global user instructions injected into every Claude Code session (@-refs expanded)",
                content=expanded,
            )
        ]
