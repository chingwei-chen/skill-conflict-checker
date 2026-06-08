from __future__ import annotations

from skill_conflict_checker.analyzers.base import AbstractAnalyzer
from skill_conflict_checker.collectors.base import AbstractCollector
from skill_conflict_checker.models import Conflict, SkillSource
from skill_conflict_checker.reporters.base import AbstractReporter


class ConflictChecker:
    """Orchestrates collection, analysis, and reporting.

    Dependency Inversion: receives all collaborators via constructor —
    no direct dependency on concrete implementations.
    Single Responsibility: only coordinates the pipeline, does no parsing/analysis/rendering.
    """

    def __init__(
        self,
        collectors: list[AbstractCollector],
        analyzer: AbstractAnalyzer,
        reporters: list[AbstractReporter],
    ) -> None:
        self._collectors = collectors
        self._analyzer = analyzer
        self._reporters = reporters

    def run(self) -> list[Conflict]:
        sources = self._gather_sources()
        conflicts = self._analyzer.analyze(sources)
        for reporter in self._reporters:
            reporter.report(conflicts, len(sources))
        return conflicts

    def _gather_sources(self) -> list[SkillSource]:
        sources: list[SkillSource] = []
        for collector in self._collectors:
            sources.extend(collector.collect())
        return sources
