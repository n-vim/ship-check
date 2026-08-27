"""Report rendering for terminal, Markdown, and JSON output."""

from __future__ import annotations

import json
from typing import Iterable

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from .models import ReleaseReport
from .profiles import resolve_profile
from .utils import markdown_escape_table


console = Console()


def print_report(report: ReleaseReport) -> None:
    title = Text("ShipCheck Release Report", style="bold cyan")
    summary = (
        f"Project: [bold]{report.project.name}[/bold]\n"
        f"Type: [bold]{report.project.kind}[/bold]\n"
        f"Profile: [bold]{report.profile}[/bold]\n"
        f"Current version: [bold]{report.version.current or 'not found'}[/bold]\n"
        f"Suggested bump: [bold]{report.suggested_bump}[/bold]\n"
        f"Suggested version: [bold]{report.suggested_version or 'not available'}[/bold]\n"
        f"Status: [bold]{report.status}[/bold]\n"
        f"Score: [bold]{report.score}/100[/bold]"
    )
    console.print(Panel(summary, title=title, border_style=_status_color(report.score)))
    console.print(_score_table(report))
    console.print(_checks_table(report))
    if report.analysis:
        console.print(_analysis_table(report))
    if report.changes:
        console.print(_changes_table(report))
    if report.blockers or report.warnings:
        console.print(_next_steps_table(report))


def _score_table(report: ReleaseReport) -> Table:
    table = Table.grid(expand=True)
    table.add_column(ratio=1)
    table.add_column(ratio=4)
    progress = ProgressBar(total=100, completed=report.score, width=40, pulse=False)
    table.add_row("Readiness", progress)
    return table


def _checks_table(report: ReleaseReport) -> Table:
    table = Table(title="Readiness Checks", box=box.SIMPLE_HEAVY)
    table.add_column("State", style="bold", no_wrap=True)
    table.add_column("Check")
    table.add_column("Message")
    table.add_column("Suggestion")
    for check in report.checks:
        state = "PASS" if check.passed else "WARN" if check.severity != "error" else "FAIL"
        table.add_row(
            state,
            check.title,
            check.message,
            check.suggestion or "-",
            style="green" if check.passed else "red" if check.severity == "error" else "yellow",
        )
    return table


def _analysis_table(report: ReleaseReport) -> Table:
    analysis = report.analysis
    table = Table(title="Commit Analysis", box=box.SIMPLE)
    table.add_column("Metric")
    table.add_column("Value")
    if analysis is None:
        table.add_row("Commits", "0")
        return table
    table.add_row("Commits analyzed", str(analysis.total))
    table.add_row("Features", str(analysis.features))
    table.add_row("Fixes", str(analysis.fixes))
    table.add_row("Breaking changes", str(analysis.breaking))
    table.add_row("Suggested bump", analysis.suggested_bump)
    table.add_row("Reason", analysis.reason)
    return table


def _changes_table(report: ReleaseReport) -> Table:
    changes = Table(title="Detected Changes", box=box.SIMPLE)
    changes.add_column("Type", no_wrap=True)
    changes.add_column("Scope", no_wrap=True)
    changes.add_column("Message")
    for entry in report.changes[:30]:
        marker = "breaking" if entry.breaking else entry.category
        changes.add_row(marker, entry.scope or "-", entry.message)
    return changes


def _next_steps_table(report: ReleaseReport) -> Table:
    table = Table(title="Next Steps", box=box.SIMPLE)
    table.add_column("Priority")
    table.add_column("Action")
    for check in report.blockers:
        table.add_row("Blocker", check.suggestion or check.message, style="red")
    for check in report.warnings[:6]:
        table.add_row("Warning", check.suggestion or check.message, style="yellow")
    return table


def render_markdown(report: ReleaseReport) -> str:
    lines = [
        "# ShipCheck Release Report",
        "",
        f"Project: **{report.project.name}**",
        f"Type: **{report.project.kind}**",
        f"Profile: **{report.profile}**",
        f"Current version: **{report.version.current or 'not found'}**",
        f"Suggested bump: **{report.suggested_bump}**",
        f"Suggested version: **{report.suggested_version or 'not available'}**",
        f"Status: **{report.status}**",
        f"Score: **{report.score}/100**",
        "",
        "## Commit Analysis",
        "",
    ]
    if report.analysis:
        lines.extend([
            f"- Commits analyzed: **{report.analysis.total}**",
            f"- Features: **{report.analysis.features}**",
            f"- Fixes: **{report.analysis.fixes}**",
            f"- Breaking changes: **{report.analysis.breaking}**",
            f"- Suggested bump reason: {report.analysis.reason}",
            "",
        ])
    else:
        lines.extend(["No commit analysis was available.", ""])

    lines.extend([
        "## Readiness Checks",
        "",
        "| State | Check | Message | Suggestion |",
        "| --- | --- | --- | --- |",
    ])
    for check in report.checks:
        state = "PASS" if check.passed else "FAIL" if check.severity == "error" else "WARN"
        lines.append(
            "| "
            + " | ".join([
                state,
                markdown_escape_table(check.title),
                markdown_escape_table(check.message),
                markdown_escape_table(check.suggestion or "-"),
            ])
            + " |"
        )
    lines.extend(["", "## Detected Changes", ""])
    if report.changes:
        for entry in report.changes:
            scope = f"**{entry.scope}:** " if entry.scope else ""
            marker = "breaking" if entry.breaking else entry.category
            lines.append(f"- `{marker}` {scope}{entry.message}")
    else:
        lines.append("No changes detected for the current release range.")
    lines.append("")
    return "\n".join(lines)


def render_json(report: ReleaseReport) -> str:
    return json.dumps(report.to_dict(), indent=2) + "\n"


def render_checklist(report: ReleaseReport) -> str:
    profile = resolve_profile(report.profile, report.project)
    lines = ["# Release Checklist", "", f"Project: {report.project.name}", f"Profile: {report.profile}", ""]
    for check in report.checks:
        marker = "x" if check.passed else " "
        lines.append(f"- [{marker}] {check.title} - {check.message}")
    lines.extend(["", "## Profile Steps", ""])
    for item in profile.checklist_items:
        lines.append(f"- [ ] {item}")
    lines.extend([
        "",
        "## Manual Steps",
        "",
        "- [ ] Review generated release notes",
        "- [ ] Confirm version bump",
        "- [ ] Run the full test suite",
        "- [ ] Push release commit",
        "- [ ] Create git tag",
        "- [ ] Publish GitHub release",
        "",
    ])
    return "\n".join(lines)


def print_detect(project_name: str, project_type: str, markers: Iterable[str]) -> None:
    table = Table(title="Detected Project", box=box.SIMPLE)
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Name", project_name)
    table.add_row("Type", project_type)
    table.add_row("Markers", ", ".join(markers) if markers else "none")
    console.print(table)


def _status_color(score: int) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"
