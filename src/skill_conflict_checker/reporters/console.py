from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from skill_conflict_checker.models import Conflict, Severity

_SEVERITY_STYLE = {
    Severity.HIGH: "bold red",
    Severity.MEDIUM: "bold yellow",
    Severity.LOW: "bold green",
}

_SEVERITY_BORDER = {
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "green",
}


class ConsoleReporter:
    """Renders conflict results to the terminal using Rich."""

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def report(self, conflicts: list[Conflict], source_count: int) -> None:
        self._console.rule("[bold blue]Skill Conflict Checker")
        self._console.print(
            f"\nScanned [bold]{source_count}[/bold] sources, "
            f"found [bold]{len(conflicts)}[/bold] conflict(s).\n"
        )

        if not conflicts:
            self._console.print("[bold green]No conflicts detected.[/bold green]")
            return

        for i, conflict in enumerate(conflicts, 1):
            self._render_conflict(i, conflict)

        self._render_summary(conflicts)

    def _render_conflict(self, index: int, conflict: Conflict) -> None:
        style = _SEVERITY_STYLE.get(conflict.severity, "white")
        title = (
            f"{conflict.severity.emoji} [{style}]"
            f"[{conflict.severity.value.upper()}][/{style}] "
            f"#{index}: {conflict.title}"
        )
        body = (
            f"[dim]Category:[/dim] {conflict.category}\n"
            f"[dim]Sources:[/dim] {conflict.sources.source_a} ↔ {conflict.sources.source_b}\n\n"
            f"[dim]Description:[/dim]\n{conflict.description}\n\n"
            f"[dim]Recommendation:[/dim]\n[italic]{conflict.recommendation}[/italic]"
        )
        self._console.print(Panel(body, title=title, border_style=_SEVERITY_BORDER[conflict.severity]))

    def _render_summary(self, conflicts: list[Conflict]) -> None:
        table = Table(title="Summary", box=box.SIMPLE_HEAVY)
        table.add_column("Severity")
        table.add_column("Count", justify="right")

        for sev in (Severity.HIGH, Severity.MEDIUM, Severity.LOW):
            count = sum(1 for c in conflicts if c.severity == sev)
            if count:
                style = _SEVERITY_STYLE[sev]
                table.add_row(
                    f"{sev.emoji} [{style}]{sev.value.upper()}[/{style}]",
                    str(count),
                )
        self._console.print(table)
