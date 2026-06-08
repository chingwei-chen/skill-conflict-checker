import pytest

from skill_conflict_checker.models import Conflict, ConflictingPair, Severity, SkillSource


@pytest.fixture
def sample_sources() -> list[SkillSource]:
    return [
        SkillSource(
            name="verbose-mode",
            source_type="skill",
            source_path="/fake/verbose-mode/SKILL.md",
            description="Always provide detailed explanations",
            content="## Rules\nAlways be verbose.\nExplain every step in detail.\nNever omit context.",
            trigger="when user asks for explanation",
        ),
        SkillSource(
            name="caveman-mode",
            source_type="skill",
            source_path="/fake/caveman-mode/SKILL.md",
            description="Respond in terse caveman style",
            content="## Rules\nDrop all filler words.\nUse fragments.\nNo articles.",
            trigger="when caveman mode active",
        ),
        SkillSource(
            name="CLAUDE.md (global instructions)",
            source_type="claude_md",
            source_path="/fake/.claude/CLAUDE.md",
            description="Global instructions",
            content="## Rules\nUse formal language.\nAlways greet user.\nBe polite.",
        ),
    ]


@pytest.fixture
def sample_conflict() -> Conflict:
    return Conflict(
        severity=Severity.HIGH,
        category="response_style",
        title="Verbosity contradiction",
        description="verbose-mode requires detailed output; caveman-mode demands terse fragments",
        sources=ConflictingPair(source_a="verbose-mode", source_b="caveman-mode"),
        recommendation="Disable one of these skills or add a priority rule",
    )
