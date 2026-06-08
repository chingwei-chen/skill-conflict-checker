from pathlib import Path

from skill_conflict_checker.collectors.claude_md import ClaudeMdCollector


def test_collect_with_claude_md(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# Instructions\nBe helpful.", encoding="utf-8")
    collector = ClaudeMdCollector(tmp_path)
    sources = collector.collect()
    assert len(sources) == 1
    assert sources[0].source_type == "claude_md"
    assert "Be helpful" in sources[0].content


def test_collect_missing_claude_md(tmp_path):
    collector = ClaudeMdCollector(tmp_path)
    assert collector.collect() == []


def test_source_type(tmp_path):
    collector = ClaudeMdCollector(tmp_path)
    assert collector.source_type == "claude_md"
