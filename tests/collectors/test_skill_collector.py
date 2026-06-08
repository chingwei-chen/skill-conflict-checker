import textwrap
from pathlib import Path

import pytest

from skill_conflict_checker.collectors.skill import UserSkillCollector


@pytest.fixture
def skills_dir(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        textwrap.dedent("""\
            ---
            name: my-skill
            description: A test skill
            ---

            ## Rules
            Always do X.
            ## Trigger
            When user asks about Y.
        """),
        encoding="utf-8",
    )
    return tmp_path


def test_collect_returns_skills(skills_dir):
    collector = UserSkillCollector(skills_dir)
    sources = collector.collect()
    assert len(sources) == 1
    assert sources[0].name == "my-skill"
    assert sources[0].source_type == "skill"
    assert "Always do X" in sources[0].content


def test_collect_empty_dir(tmp_path):
    collector = UserSkillCollector(tmp_path)
    assert collector.collect() == []


def test_collect_missing_dir(tmp_path):
    collector = UserSkillCollector(tmp_path / "nonexistent")
    assert collector.collect() == []


def test_source_type():
    collector = UserSkillCollector(Path("/fake"))
    assert collector.source_type == "skill"


def test_collect_no_frontmatter(tmp_path):
    skill_dir = tmp_path / "bare-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("## Rules\nDo something.", encoding="utf-8")
    collector = UserSkillCollector(tmp_path)
    sources = collector.collect()
    assert sources[0].name == "bare-skill"
    assert "Do something" in sources[0].content
