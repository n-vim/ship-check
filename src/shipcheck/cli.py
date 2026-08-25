"""Command-line interface for ShipCheck."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .changelog import analyze_changes, parse_commit_messages, render_github_release, render_release_notes, update_changelog
from .config import create_default_config, load_config
from .core import build_report
from .detector import detect_project
from .profiles import available_profiles, resolve_profile
from .reports import print_detect, print_report, render_checklist, render_json, render_markdown
from .utils import bump_prerelease, bump_version, normalize_root, write_text
from .versioning import detect_version, update_version

app = typer.Typer(
    name="shipcheck",
    help="Check release readiness, generate release notes, and manage version bumps.",
    no_args_is_help=True,
)
console = Console()


OutputFormat = typer.Option("terminal", "--format", "-f", help="Output format: terminal, markdown, or json.")
PathArg = typer.Argument(".", help="Repository path to inspect.")
ProfileOpt = typer.Option(None, "--profile", "-p", help="Release profile: auto, general, python, npm, node, library, cli, rust, or go.")


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show ShipCheck version and exit."),
) -> None:
    if version:
        console.print(f"ShipCheck {__version__}")
        raise typer.Exit()


@app.command()
def status(
    path: str = PathArg,
    profile: Optional[str] = ProfileOpt,
    output_format: str = OutputFormat,
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save report to a file."),
) -> None:
    """Run a complete release readiness report."""
    root = normalize_root(path)
    config = load_config(root)
    report = build_report(root, config, profile)
    _emit_report(report, output_format, output)


@app.command()
def analyze(
    path: str = PathArg,
    profile: Optional[str] = ProfileOpt,
    output_format: str = typer.Option("terminal", "--format", "-f", help="Output format: terminal or json."),
) -> None:
    """Analyze commit messages and suggest a semantic version bump."""
    root = normalize_root(path)
    report = build_report(root, load_config(root), profile)
    analysis = report.analysis or analyze_changes(parse_commit_messages(report.git.commit_messages))
    if output_format == "json":
        console.print_json(data=analysis.to_dict())
        return
    table = Table(title="Conventional Commit Analysis")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Commits analyzed", str(analysis.total))
    table.add_row("Features", str(analysis.features))
    table.add_row("Fixes", str(analysis.fixes))
    table.add_row("Breaking changes", str(analysis.breaking))
    table.add_row("Suggested bump", analysis.suggested_bump)
    table.add_row("Reason", analysis.reason)
    console.print(table)


@app.command()
def checklist(
    path: str = PathArg,
    profile: Optional[str] = ProfileOpt,
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save checklist to a file."),
) -> None:
    """Generate a Markdown release checklist."""
    root = normalize_root(path)
    report = build_report(root, load_config(root), profile)
    content = render_checklist(report)
    if output:
        write_text(output, content)
        console.print(f"[green]Checklist written to {output}[/green]")
    else:
        console.print(content)


@app.command()
def notes(
    path: str = PathArg,
    profile: Optional[str] = ProfileOpt,
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save release notes to a file."),
    github: bool = typer.Option(False, "--github", help="Render a GitHub release draft."),
) -> None:
    """Generate release notes from commits since the latest tag."""
    root = normalize_root(path)
    report = build_report(root, load_config(root), profile)
    version = report.suggested_version or report.version.current
    content = render_github_release(report.project.name, version, report.changes) if github else render_release_notes(report.project.name, version, report.changes)
    if output:
        write_text(output, content)
        console.print(f"[green]Release notes written to {output}[/green]")
    else:
        console.print(content)


@app.command("release-notes")
def release_notes(
    path: str = PathArg,
    profile: Optional[str] = ProfileOpt,
    version: Optional[str] = typer.Option(None, "--version", help="Version to use in the release title."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save release notes to a file."),
) -> None:
    """Generate a GitHub-ready release draft."""
    root = normalize_root(path)
    report = build_report(root, load_config(root), profile)
    target = version or report.suggested_version or report.version.current
    content = render_github_release(report.project.name, target, report.changes)
    if output:
        write_text(output, content)
        console.print(f"[green]GitHub release draft written to {output}[/green]")
    else:
        console.print(content)


@app.command()
def changelog(
    path: str = PathArg,
    profile: Optional[str] = ProfileOpt,
    version: Optional[str] = typer.Option(None, "--version", help="Version heading to add."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write to a custom changelog path."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the changelog entry without writing."),
    force: bool = typer.Option(False, "--force", help="Write changelog even if readiness score is low."),
) -> None:
    """Update CHANGELOG.md with categorized release changes."""
    root = normalize_root(path)
    config = load_config(root)
    report = build_report(root, config, profile)
    target_version = version or report.suggested_version or report.version.current
    if not target_version:
        raise typer.BadParameter("No version found. Pass --version or add a project version.")
    if report.score < config.fail_below and not force and not dry_run:
        raise typer.BadParameter("Release score is low. Use --force if you still want to update the changelog.")
    if dry_run:
        from .changelog import render_changelog_entry

        console.print(render_changelog_entry(report.project.name, target_version, report.changes))
        return
    changelog_path = output or (root / config.changelog_path)
    update_changelog(changelog_path, report.project.name, target_version, report.changes)
    console.print(f"[green]{changelog_path} updated for {target_version}[/green]")


@app.command()
def bump(
    level: str = typer.Argument(..., help="Bump level: patch, minor, major, or prerelease."),
    path: str = PathArg,
    dry_run: bool = typer.Option(False, "--dry-run", help="Show the next version without writing."),
    set_version: Optional[str] = typer.Option(None, "--set", help="Set an exact version instead of bumping."),
    tag: str = typer.Option("rc", "--tag", help="Prerelease tag when level is prerelease."),
) -> None:
    """Bump the detected project version."""
    root = normalize_root(path)
    current = detect_version(root)
    if not current.found or not current.current:
        raise typer.BadParameter("No supported version field found.")
    if dry_run:
        if set_version:
            next_version = set_version
        elif level == "prerelease":
            next_version = bump_prerelease(current.current, tag)
        else:
            next_version = bump_version(current.current, level)
        console.print(Panel(f"{current.current} -> {next_version}", title="Version Preview", border_style="cyan"))
        return
    updated = update_version(root, level, set_version, prerelease_tag=tag)
    console.print(f"[green]Version updated:[/green] {current.current} -> {updated.current}")


@app.command()
def detect(path: str = PathArg) -> None:
    """Detect project type and release metadata."""
    root = normalize_root(path)
    project = detect_project(root)
    print_detect(project.name, project.kind, project.markers)
    version = detect_version(root)
    table = Table(title="Version")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Current", version.current or "not found")
    table.add_row("Source", str(version.source) if version.source else "not found")
    console.print(table)


@app.command()
def profiles() -> None:
    """List available release profiles."""
    table = Table(title="ShipCheck Release Profiles")
    table.add_column("Profile")
    table.add_column("Description")
    for profile in available_profiles():
        table.add_row(profile.name, profile.description)
    console.print(table)


@app.command()
def profile(
    name: str = typer.Argument(..., help="Profile name to inspect."),
) -> None:
    """Show details for a release profile."""
    selected = resolve_profile(name)
    table = Table(title=f"Profile: {selected.name}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Description", selected.description)
    table.add_row("Required files", ", ".join(selected.required_files) or "none")
    table.add_row("Recommended files", ", ".join(selected.recommended_files) or "none")
    table.add_row("Required markers", ", ".join(selected.required_markers) or "none")
    console.print(table)


@app.command()
def init(
    path: str = PathArg,
    force: bool = typer.Option(False, "--force", help="Overwrite an existing config file."),
) -> None:
    """Create a default .shipcheck.yaml config file."""
    root = normalize_root(path)
    created = create_default_config(root, force=force)
    console.print(f"[green]Created {created}[/green]")


@app.command()
def doctor(
    path: str = PathArg,
    profile: Optional[str] = ProfileOpt,
    output_format: str = typer.Option("terminal", "--format", "-f", help="Output format: terminal, markdown, or json."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save report to a file."),
) -> None:
    """Show release blockers and warnings."""
    root = normalize_root(path)
    report = build_report(root, load_config(root), profile)
    if output_format != "terminal" or output:
        _emit_report(report, output_format, output)
        return
    console.print(Panel(f"Status: {report.status}\nScore: {report.score}/100\nProfile: {report.profile}", title="ShipCheck Doctor", border_style="cyan"))
    if report.blockers:
        console.print("[bold red]Blockers[/bold red]")
        for check in report.blockers:
            console.print(f"- {check.title}: {check.message}")
    if report.warnings:
        console.print("[bold yellow]Warnings[/bold yellow]")
        for check in report.warnings:
            console.print(f"- {check.title}: {check.message}")
    if not report.blockers and not report.warnings:
        console.print("[green]No release blockers found.[/green]")


@app.command()
def config(path: str = PathArg) -> None:
    """Show the active ShipCheck configuration."""
    root = normalize_root(path)
    cfg = load_config(root)
    table = Table(title="ShipCheck Configuration")
    table.add_column("Key")
    table.add_column("Value")
    for key, value in cfg.__dict__.items():
        table.add_row(key, str(value))
    console.print(table)


def _emit_report(report, output_format: str, output: Optional[Path]) -> None:
    selected = output_format.lower()
    if selected == "terminal":
        if output:
            write_text(output, render_markdown(report))
            console.print(f"[green]Report written to {output}[/green]")
        else:
            print_report(report)
    elif selected == "markdown":
        content = render_markdown(report)
        if output:
            write_text(output, content)
            console.print(f"[green]Report written to {output}[/green]")
        else:
            console.print(content)
    elif selected == "json":
        content = render_json(report)
        if output:
            write_text(output, content)
            console.print(f"[green]Report written to {output}[/green]")
        else:
            console.print(content)
    else:
        raise typer.BadParameter("Format must be terminal, markdown, or json")
