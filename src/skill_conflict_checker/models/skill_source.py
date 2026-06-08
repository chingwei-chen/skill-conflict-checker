from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SkillSource:
    """A single rule-bearing source loaded into a Claude Code session."""

    name: str
    source_type: str  # "skill" | "plugin_skill" | "mcp" | "claude_md"
    source_path: str
    description: str
    content: str
    trigger: str = ""
    metadata: dict = field(default_factory=dict)

    def summary(self, max_chars: int = 500) -> str:
        body = self.content[:max_chars]
        if len(self.content) > max_chars:
            body += "…"
        return body
