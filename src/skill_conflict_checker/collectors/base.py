from __future__ import annotations

from typing import Protocol, runtime_checkable

from skill_conflict_checker.models import SkillSource


@runtime_checkable
class AbstractCollector(Protocol):
    """Collects SkillSource entries from one type of source.

    Interface Segregation: each implementation is responsible for exactly
    one source type (user skills, plugin skills, MCP servers, CLAUDE.md).
    Open/Closed: new source types extend this Protocol without modifying
    existing collectors.
    """

    @property
    def source_type(self) -> str:
        """Human-readable label for this source category."""
        ...

    def collect(self) -> list[SkillSource]:
        """Scan and return all SkillSource entries for this source type."""
        ...
