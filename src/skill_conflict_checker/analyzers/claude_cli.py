from __future__ import annotations

import json
import re
import subprocess

from skill_conflict_checker.models import Conflict, SkillSource

_SYSTEM_PROMPT = """\
You are an expert at detecting rule conflicts between Claude Code configuration sources.
Analyze the provided skill and configuration sources and identify ALL conflicts where:
1. Rules directly contradict each other (e.g., "always be verbose" vs "drop all filler words")
2. Trigger conditions overlap and instructions diverge
3. Tool usage policies conflict
4. Persistence/memory behaviors conflict
5. Language/tone requirements contradict
6. Priority/ordering rules conflict

Return ONLY a JSON object with a "conflicts" array. Each conflict must have:
- severity: "high" | "medium" | "low"
- category: one of [response_style, trigger_overlap, tool_usage, persistence, language, priority, other]
- title: short descriptive title (max 80 chars)
- description: clear explanation of why these rules conflict
- source_a: name of first conflicting source
- source_b: name of second conflicting source
- recommendation: concrete action to resolve the conflict

If no conflicts found, return: {"conflicts": []}
Return ONLY the JSON object, no markdown fences, no prose."""

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


class ClaudeCliAnalyzer:
    """Uses the local `claude` CLI (subscription auth) to detect conflicts."""

    def __init__(self, model: str = "claude-haiku-4-5-20251001") -> None:
        self._model = model

    def analyze(self, sources: list[SkillSource]) -> list[Conflict]:
        if len(sources) < 2:
            return []

        user_message = (
            f"Analyze these {len(sources)} configuration sources for rule conflicts:\n\n"
            + _build_sources_block(sources)
        )

        full_text = self._call_cli(user_message)
        data = _extract_json(full_text)
        conflicts: list[Conflict] = []
        for raw in data.get("conflicts", []):
            try:
                conflicts.append(Conflict.from_dict(raw))
            except (KeyError, ValueError):
                continue
        return conflicts

    def _call_cli(self, user_message: str) -> str:
        result = subprocess.run(
            [
                "claude",
                "--print",
                "--model", self._model,
                "--system-prompt", _SYSTEM_PROMPT,
                "--output-format", "text",
                user_message,
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            raise RuntimeError(f"claude CLI failed: {result.stderr.strip()}")
        return result.stdout
