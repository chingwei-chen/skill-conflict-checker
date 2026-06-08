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


class PluginSkillCollector:
    """Collects skills from installed plugins (latest version only)."""

    def __init__(self, plugins_cache: Path, installed: dict) -> None:
        self._plugins_cache = plugins_cache
        self._installed = installed

    @property
    def source_type(self) -> str:
        return "plugin_skill"

    def collect(self) -> list[SkillSource]:
        if not self._plugins_cache.exists():
            return []
        sources: list[SkillSource] = []
        for plugin_key, versions in self._installed.get("plugins", {}).items():
            if not versions:
                continue
            latest = max(versions, key=lambda v: v.get("lastUpdated", ""))
            install_path = Path(latest["installPath"])
            for skills_subdir in ("skills", "workflow-skills"):
                d = install_path / skills_subdir
                if d.exists():
                    sources.extend(self._collect_from(d, plugin_key))
        return sources

    def _collect_from(self, skills_dir: Path, plugin_key: str) -> list[SkillSource]:
        sources: list[SkillSource] = []
        for skill_path in skills_dir.iterdir():
            if not skill_path.is_dir():
                continue
            for filename in ("SKILL.md", "skill.md"):
                fp = skill_path / filename
                if fp.exists():
                    sources.append(self._parse(fp, plugin_key))
                    break
        return sources

    def _parse(self, fp: Path, plugin_key: str) -> SkillSource:
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
            metadata={**meta, "plugin": plugin_key},
        )
