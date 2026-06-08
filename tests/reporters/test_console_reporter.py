from io import StringIO

import pytest
from rich.console import Console

from skill_conflict_checker.models import Conflict, ConflictingPair, Severity
from skill_conflict_checker.reporters.console import ConsoleReporter


@pytest.fixture
def console_capture():
    buf = StringIO()
    return Console(file=buf, highlight=False), buf


def make_conflict(severity=Severity.HIGH):
    return Conflict(
        severity=severity,
        category="response_style",
        title="Test conflict",
        description="Desc",
        sources=ConflictingPair(source_a="a", source_b="b"),
        recommendation="Fix it",
    )


def test_no_conflicts(console_capture):
    console, buf = console_capture
    reporter = ConsoleReporter(console)
    reporter.report([], source_count=3)
    assert "No conflicts detected" in buf.getvalue()


def test_conflict_rendered(console_capture):
    console, buf = console_capture
    reporter = ConsoleReporter(console)
    reporter.report([make_conflict()], source_count=2)
    out = buf.getvalue()
    assert "Test conflict" in out
    assert "Fix it" in out


def test_summary_shows_severity(console_capture):
    console, buf = console_capture
    reporter = ConsoleReporter(console)
    reporter.report(
        [make_conflict(Severity.HIGH), make_conflict(Severity.LOW)],
        source_count=3,
    )
    out = buf.getvalue()
    assert "HIGH" in out
    assert "LOW" in out
