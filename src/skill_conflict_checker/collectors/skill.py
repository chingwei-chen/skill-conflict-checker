from __future__ import annotations

import re
from pathlib import Path

import yaml

from skill_conflict_checker.models import SkillSource

_TRIGGER_PATTERNS = [
    r"(?i)(?:trigger|activate|use when|invoked when|when user)[^\n]*\n((?:[^\n]+\n?){1,5})",
    r"(?i)## (?:trigger|when to use|activation)[^\n]*\n((?:[^\n]+\n?){1,10})",
]


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, parts[2].strip()


def _extract_trigger(content: str) -> str:
    for pat in _TRIGGER_PATTERNS:
        m = re.search(pat, content)
        if m:
            return m.group(1).strip()[:300]
    return ""


class UserSkillCollector:
    """Collects skills installed under ~/.claude/skills/."""

    def __init__(self, skills_dir: Path) -> None:
        self._skills_dir = skills_dir

    @property
    def source_type(self) -> str:
        return "skill"

    def collect(self) -> list[SkillSource]:
        if not self._skills_dir.exists():
            return []
        sources: list[SkillSource] = []
        for skill_path in self._skills_dir.iterdir():
            if not skill_path.is_dir():
                continue
            for filename in ("SKILL.md", "skill.md"):
                fp = skill_path / filename
                if fp.exists():
                    sources.append(self._parse(fp))
                    break
        return sources

    def _parse(self, fp: Path) -> SkillSource:
        raw = fp.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(raw)
        name = meta.get("name") or fp.parent.name
        desc = str(meta.get("description", "")).strip()
        return SkillSource(
            name=name,
            source_type=self.source_type,
            source_path=str(fp),
            description=desc,
            content=body,
            trigger=_extract_trigger(body),
            metadata=meta,
        )
