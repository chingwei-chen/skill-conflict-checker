from __future__ import annotations

import subprocess
from pathlib import Path

from skill_conflict_checker.models import SkillSource

_RUNNABLE_EVENTS = {"SessionStart"}
_HOOK_TIMEOUT = 8


def _run_hook(command: str) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=_HOOK_TIMEOUT,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


class HookCollector:
    """Reads settings.json hooks and captures what each injects into Claude's context.

    SessionStart hooks are actually executed to capture their stdout (the real
    system-reminder content). Other hooks are described by command only, since
    running them outside their trigger context is unsafe.
    """

    def __init__(self, hooks: dict) -> None:
        self._hooks = hooks

    @property
    def source_type(self) -> str:
        return "hook"

    def collect(self) -> list[SkillSource]:
        sources: list[SkillSource] = []
        for event_name, matchers in self._hooks.items():
            for matcher_entry in matchers:
                matcher = matcher_entry.get("matcher", "*")
                for hook in matcher_entry.get("hooks", []):
                    if hook.get("type") != "command":
                        continue
                    command = hook.get("command", "")
                    sources.append(self._build(event_name, matcher, command))
        return sources

    def _build(self, event: str, matcher: str, command: str) -> SkillSource:
        injected = ""
        if event in _RUNNABLE_EVENTS:
            injected = _run_hook(command)

        label = f"{event}" if matcher == "*" else f"{event}[{matcher}]"
        content_parts = [f"Hook event: {event}", f"Matcher: {matcher}", f"Command: {command}"]
        if injected:
            content_parts += ["", "Actual injected content (stdout):", injected]
        else:
            content_parts += ["", "(Content only available at runtime — not a SessionStart hook)"]

        return SkillSource(
            name=f"hook:{label}",
            source_type=self.source_type,
            source_path="settings.json[hooks]",
            description=f"Hook injected into Claude context on {event} event (matcher: {matcher})",
            content="\n".join(content_parts),
        )
