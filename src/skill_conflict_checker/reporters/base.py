from __future__ import annotations

from typing import Protocol, runtime_checkable

from skill_conflict_checker.models import Conflict


@runtime_checkable
class AbstractReporter(Protocol):
    """Renders conflict results in a specific output format."""

    def report(self, conflicts: list[Conflict], source_count: int) -> None:
        """Render and output the conflict results."""
        ...
