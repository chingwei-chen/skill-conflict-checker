from __future__ import annotations

from pathlib import Path

from skill_conflict_checker.models import SkillSource

_MAX_EXPAND_DEPTH = 5


def _expand_at_refs(content: str, base_dir: Path, depth: int = 0) -> str:
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


class ProjectClaudeMdCollector:
    """Finds CLAUDE.md files from project directory up to root, expanding @-references.

    This captures the actual assembled instructions Claude receives for a given
    project — including project-level overrides that aren't in ~/.claude/CLAUDE.md.
    """

    def __init__(self, start_dir: Path) -> None:
        self._start_dir = start_dir

    @property
    def source_type(self) -> str:
        return "project_claude_md"

    def collect(self) -> list[SkillSource]:
        sources: list[SkillSource] = []
        seen: set[Path] = set()
        current = self._start_dir.resolve()

        while True:
            candidate = current / "CLAUDE.md"
            if candidate not in seen and candidate.exists():
                seen.add(candidate)
                sources.append(self._parse(candidate))
            if current == current.parent:
                break
            current = current.parent

        return sources

    def _parse(self, path: Path) -> SkillSource:
        raw = path.read_text(encoding="utf-8")
        expanded = _expand_at_refs(raw, path.parent)
        return SkillSource(
            name=f"CLAUDE.md ({path.parent.name}/)",
            source_type=self.source_type,
            source_path=str(path),
            description=f"Project-level Claude instructions at {path}",
            content=expanded,
        )
