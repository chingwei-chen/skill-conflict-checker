from pathlib import Path

from skill_conflict_checker.models import Conflict, ConflictingPair, Severity
from skill_conflict_checker.reporters.markdown import MarkdownReporter


def make_conflict():
    return Conflict(
        severity=Severity.HIGH,
        category="language",
        title="Language conflict",
        description="Desc",
        sources=ConflictingPair(source_a="a", source_b="b"),
        recommendation="Pick one",
    )


def test_write_markdown(tmp_path):
    out = tmp_path / "report.md"
    reporter = MarkdownReporter(str(out))
    reporter.report([make_conflict()], source_count=3)
    text = out.read_text()
    assert "# Skill Conflict Report" in text
    assert "Language conflict" in text
    assert "Pick one" in text


def test_no_conflicts(tmp_path):
    out = tmp_path / "empty.md"
    reporter = MarkdownReporter(str(out))
    reporter.report([], source_count=2)
    text = out.read_text()
    assert "No conflicts detected" in text
