from __future__ import annotations

from typing import Protocol, runtime_checkable

from skill_conflict_checker.models import Conflict, SkillSource


@runtime_checkable
class AbstractAnalyzer(Protocol):
    """Detects conflicts between a list of SkillSources.

    Dependency Inversion: ConflictChecker depends on this abstraction,
    not on any concrete LLM implementation.
    """

    def analyze(self, sources: list[SkillSource]) -> list[Conflict]:
        """Return all detected conflicts across the given sources."""
        ...
