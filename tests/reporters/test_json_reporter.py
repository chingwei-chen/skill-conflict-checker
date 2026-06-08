import json
from pathlib import Path

from skill_conflict_checker.models import Conflict, ConflictingPair, Severity
from skill_conflict_checker.reporters.json_reporter import JsonReporter


def make_conflict():
    return Conflict(
        severity=Severity.MEDIUM,
        category="tool_usage",
        title="Tool conflict",
        description="Desc",
        sources=ConflictingPair(source_a="x", source_b="y"),
        recommendation="Resolve",
    )


def test_write_to_file(tmp_path):
    out = tmp_path / "report.json"
    reporter = JsonReporter(str(out))
    reporter.report([make_conflict()], source_count=2)
    data = json.loads(out.read_text())
    assert data["conflict_count"] == 1
    assert data["source_count"] == 2
    assert data["conflicts"][0]["severity"] == "medium"


def test_empty_conflicts(tmp_path):
    out = tmp_path / "empty.json"
    reporter = JsonReporter(str(out))
    reporter.report([], source_count=5)
    data = json.loads(out.read_text())
    assert data["conflicts"] == []
    assert data["source_count"] == 5
