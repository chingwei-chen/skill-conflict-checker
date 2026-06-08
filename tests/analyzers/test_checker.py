from unittest.mock import MagicMock

from skill_conflict_checker.checker import ConflictChecker
from skill_conflict_checker.models import Conflict, ConflictingPair, Severity, SkillSource


def make_source(name: str) -> SkillSource:
    return SkillSource(
        name=name,
        source_type="skill",
        source_path="/fake",
        description="",
        content="Rules here.",
    )


def make_conflict() -> Conflict:
    return Conflict(
        severity=Severity.HIGH,
        category="response_style",
        title="X",
        description="D",
        sources=ConflictingPair(source_a="a", source_b="b"),
        recommendation="R",
    )


def test_checker_calls_all_collectors():
    c1 = MagicMock()
    c1.collect.return_value = [make_source("s1")]
    c2 = MagicMock()
    c2.collect.return_value = [make_source("s2")]

    analyzer = MagicMock()
    analyzer.analyze.return_value = []
    reporter = MagicMock()

    checker = ConflictChecker([c1, c2], analyzer, [reporter])
    checker.run()

    c1.collect.assert_called_once()
    c2.collect.assert_called_once()
    analyzer.analyze.assert_called_once()
    sources = analyzer.analyze.call_args[0][0]
    assert len(sources) == 2


def test_checker_passes_conflicts_to_reporters():
    collector = MagicMock()
    collector.collect.return_value = [make_source("s1"), make_source("s2")]

    conflict = make_conflict()
    analyzer = MagicMock()
    analyzer.analyze.return_value = [conflict]

    r1 = MagicMock()
    r2 = MagicMock()

    checker = ConflictChecker([collector], analyzer, [r1, r2])
    result = checker.run()

    assert result == [conflict]
    r1.report.assert_called_once_with([conflict], 2)
    r2.report.assert_called_once_with([conflict], 2)


def test_checker_returns_empty_when_no_conflicts():
    collector = MagicMock()
    collector.collect.return_value = [make_source("a"), make_source("b")]
    analyzer = MagicMock()
    analyzer.analyze.return_value = []
    reporter = MagicMock()

    checker = ConflictChecker([collector], analyzer, [reporter])
    assert checker.run() == []
