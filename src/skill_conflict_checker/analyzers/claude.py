from __future__ import annotations

import json
import os
import re

import anthropic

from skill_conflict_checker.models import Conflict, SkillSource

_SYSTEM_PROMPT = """\
You are an expert at detecting rule conflicts between Claude Code configuration sources.
Analyze the provided skill and configuration sources and identify ALL conflicts where:
1. Rules directly contradict each other (e.g., "always be verbose" vs "drop filler words")
2. Trigger conditions overlap and instructions diverge
3. Tool usage policies conflict (one enables a tool, another restricts it)
4. Persistence/memory behaviors conflict
5. Language/tone requirements contradict
6. Priority/ordering rules conflict

Return ONLY a JSON object with a "conflicts" array. Each conflict object must have:
- severity: "high" | "medium" | "low"
- category: one of [response_style, trigger_overlap, tool_usage, persistence, language, priority, other]
- title: short descriptive title (max 80 chars)
- description: clear explanation of why these rules conflict
- source_a: name of first conflicting source
- source_b: name of second conflicting source
- recommendation: concrete action to resolve the conflict

Example:
{"conflicts": [{"severity": "high", "category": "response_style", "title": "Verbosity contradiction", "description": "...", "source_a": "verbose-skill", "source_b": "caveman-mode", "recommendation": "..."}]}

If no conflicts, return: {"conflicts": []}
"""

_MAX_SOURCE_CHARS = 3000


def _build_sources_block(sources: list[SkillSource]) -> str:
    parts: list[str] = []
    for src in sources:
        parts.append(
            f"--- SOURCE: {src.name} [{src.source_type}] ---\n"
            f"Path: {src.source_path}\n"
            f"Description: {src.description}\n"
            f"Trigger: {src.trigger or '(none)'}\n"
            f"Content:\n{src.content[:_MAX_SOURCE_CHARS]}\n"
        )
    return "\n".join(parts)


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"conflicts": []}
    try:
        return json.loads(m.group())
    except json.JSONDecodeError:
        return {"conflicts": []}


class ClaudeAnalyzer:
    """Uses Claude API with adaptive thinking to detect conflicts."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-opus-4-8",
    ) -> None:
        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = anthropic.Anthropic(api_key=key)
        self._model = model

    def analyze(self, sources: list[SkillSource]) -> list[Conflict]:
        if len(sources) < 2:
            return []

        user_message = (
            f"Analyze these {len(sources)} configuration sources for conflicts:\n\n"
            + _build_sources_block(sources)
        )

        full_text = self._call_claude(user_message)
        data = _extract_json(full_text)
        conflicts: list[Conflict] = []
        for raw in data.get("conflicts", []):
            try:
                conflicts.append(Conflict.from_dict(raw))
            except (KeyError, ValueError):
                continue
        return conflicts

    def _call_claude(self, user_message: str) -> str:
        chunks: list[str] = []
        with self._client.messages.stream(
            model=self._model,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            for event in stream:
                if (
                    hasattr(event, "type")
                    and event.type == "content_block_delta"
                    and hasattr(event, "delta")
                    and hasattr(event.delta, "text")
                ):
                    chunks.append(event.delta.text)
        return "".join(chunks)
