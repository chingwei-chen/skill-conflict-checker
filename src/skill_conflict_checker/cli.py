from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console

from skill_conflict_checker.analyzers.claude import ClaudeAnalyzer
from skill_conflict_checker.analyzers.claude_cli import ClaudeCliAnalyzer
from skill_conflict_checker.checker import ConflictChecker
from skill_conflict_checker.collectors.claude_md import ClaudeMdCollector
from skill_conflict_checker.collectors.hook import HookCollector
from skill_conflict_checker.collectors.mcp import McpCollector
from skill_conflict_checker.collectors.plugin import PluginSkillCollector
from skill_conflict_checker.collectors.project_claude_md import ProjectClaudeMdCollector
from skill_conflict_checker.collectors.skill import UserSkillCollector
from skill_conflict_checker.reporters.console import ConsoleReporter
from skill_conflict_checker.reporters.json_reporter import JsonReporter
from skill_conflict_checker.reporters.markdown import MarkdownReporter

load_dotenv()

_DEFAULT_CLAUDE_DIR = Path.home() / ".claude"


def _load_settings(claude_dir: Path) -> dict:
    settings_path = claude_dir / "settings.json"
    if not settings_path.exists():
        return {}
    try:
        return json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _load_installed(claude_dir: Path) -> dict:
    installed_path = claude_dir / "installed-plugins.json"
    if not installed_path.exists():
        return {}
    try:
        return json.loads(installed_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


@click.command()
@click.option(
    "--claude-dir",
    default=str(_DEFAULT_CLAUDE_DIR),
    show_default=True,
    help="Path to .claude configuration directory.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["console", "json", "markdown"], case_sensitive=False),
    default="console",
    show_default=True,
    help="Output format.",
)
@click.option("--output", "-o", default=None, help="Output file path (for json/markdown formats).")
@click.option("--model", default="claude-haiku-4-5-20251001", show_default=True, help="Claude model to use.")
@click.option("--use-cli", is_flag=True, default=True, show_default=True, help="Use local claude CLI (subscription auth) instead of API key.")
@click.option("--use-api", is_flag=True, default=False, help="Use Anthropic API key instead of claude CLI.")
@click.option(
    "--no-skills", is_flag=True, default=False, help="Skip user skill collection."
)
@click.option(
    "--no-plugins", is_flag=True, default=False, help="Skip plugin skill collection."
)
@click.option(
    "--no-mcp", is_flag=True, default=False, help="Skip MCP server collection."
)
@click.option(
    "--no-claude-md", is_flag=True, default=False, help="Skip CLAUDE.md collection."
)
@click.option(
    "--no-hooks", is_flag=True, default=False, help="Skip lifecycle hook collection."
)
@click.option(
    "--project-dir",
    default=None,
    help="Scan project CLAUDE.md files from this directory upward (default: current dir).",
)
@click.option(
    "--no-project-claude-md", is_flag=True, default=False, help="Skip project CLAUDE.md collection."
)
def main(
    claude_dir: str,
    output_format: str,
    output: str | None,
    model: str,
    use_cli: bool,
    use_api: bool,
    no_skills: bool,
    no_plugins: bool,
    no_mcp: bool,
    no_claude_md: bool,
    no_hooks: bool,
    project_dir: str | None,
    no_project_claude_md: bool,
) -> None:
    """Detect rule conflicts between Claude Code skills, plugins, and MCP configurations."""
    claude_path = Path(claude_dir)
    settings = _load_settings(claude_path)
    installed = _load_installed(claude_path)

    collectors = []
    if not no_skills:
        collectors.append(UserSkillCollector(claude_path / "skills"))
    if not no_plugins:
        collectors.append(
            PluginSkillCollector(claude_path / "plugins" / "cache", installed)
        )
    if not no_mcp:
        mcp_servers = settings.get("mcpServers", {})
        collectors.append(McpCollector(mcp_servers))
    if not no_claude_md:
        collectors.append(ClaudeMdCollector(claude_path))
    if not no_hooks:
        hooks = settings.get("hooks", {})
        if hooks:
            collectors.append(HookCollector(hooks))
    if not no_project_claude_md:
        start = Path(project_dir) if project_dir else Path.cwd()
        collectors.append(ProjectClaudeMdCollector(start))

    if not collectors:
        click.echo("No collectors enabled. Use --help for options.", err=True)
        sys.exit(1)

    console = Console()
    reporters = []
    if output_format == "console":
        reporters.append(ConsoleReporter(console))
    elif output_format == "json":
        reporters.append(JsonReporter(output))
    elif output_format == "markdown":
        if not output:
            click.echo("--output required for markdown format.", err=True)
            sys.exit(1)
        reporters.append(MarkdownReporter(output))

    if use_api:
        analyzer = ClaudeAnalyzer(model=model)
    else:
        analyzer = ClaudeCliAnalyzer(model=model)
    checker = ConflictChecker(collectors=collectors, analyzer=analyzer, reporters=reporters)

    try:
        conflicts = checker.run()
        sys.exit(1 if conflicts else 0)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        sys.exit(2)
