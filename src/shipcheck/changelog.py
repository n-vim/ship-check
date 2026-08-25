"""Commit parsing and changelog generation."""

from __future__ import annotations

import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Iterable, List, Sequence

from .models import ChangeEntry, CommitAnalysis
from .utils import read_text, write_text


CONVENTIONAL_RE = re.compile(
    r"^(?:(?P<hash>[0-9a-f]{5,40})\s+)?(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<message>.+)$"
)

CATEGORY_TITLES = {
    "breaking": "Breaking Changes",
    "feat": "Added",
    "fix": "Fixed",
    "security": "Security",
    "perf": "Performance",
    "refactor": "Changed",
    "docs": "Documentation",
    "test": "Tests",
    "build": "Build",
    "ci": "CI",
    "chore": "Chores",
    "style": "Style",
    "revert": "Reverts",
    "other": "Other Changes",
}

LEGACY_TITLES = {
    "feat": "Features",
    "fix": "Fixes",
}

CATEGORY_ORDER = [
    "breaking",
    "feat",
    "fix",
    "security",
    "perf",
    "refactor",
    "docs",
    "test",
    "build",
    "ci",
    "chore",
    "style",
    "revert",
    "other",
]


def parse_commit_messages(messages: Iterable[str]) -> List[ChangeEntry]:
    entries: List[ChangeEntry] = []
    for raw in messages:
        line = raw.strip()
        if not line:
            continue

        commit_hash = None
        message_text = line
        parts = line.split("\t", 1)
        if len(parts) == 2 and re.fullmatch(r"[0-9a-f]{5,40}", parts[0]):
            commit_hash = parts[0]
            message_text = parts[1].strip()

        match = CONVENTIONAL_RE.match(message_text)
        if match:
            kind = match.group("type").lower()
            message = match.group("message").strip()
            is_breaking = bool(match.group("breaking")) or "BREAKING CHANGE" in message_text.upper()
            entries.append(
                ChangeEntry(
                    category=kind,
                    message=message,
                    scope=match.group("scope"),
                    breaking=is_breaking,
                    commit_hash=commit_hash or match.group("hash"),
                    raw=line,
                )
            )
        else:
            entries.append(ChangeEntry(category="other", message=message_text, commit_hash=commit_hash, raw=line))
    return entries


def analyze_changes(changes: Sequence[ChangeEntry], default: str = "patch") -> CommitAnalysis:
    counts = Counter(_normalize_category(entry.category) for entry in changes)
    breaking = sum(1 for entry in changes if entry.breaking)
    if breaking:
        bump = "major"
        reason = f"{breaking} breaking change{'s' if breaking != 1 else ''} detected"
    elif counts["feat"]:
        bump = "minor"
        reason = f"{counts['feat']} feature commit{'s' if counts['feat'] != 1 else ''} detected"
    elif counts["fix"] or counts["security"] or counts["perf"]:
        bump = "patch"
        reason = "fix, security, or performance changes detected"
    else:
        bump = default if default in {"patch", "minor", "major"} else "patch"
        reason = "no release-driving conventional commits found"

    return CommitAnalysis(
        total=len(changes),
        features=counts["feat"],
        fixes=counts["fix"],
        breaking=breaking,
        docs=counts["docs"],
        tests=counts["test"],
        chores=counts["chore"] + counts["build"] + counts["ci"] + counts["style"],
        other=counts["other"],
        suggested_bump=bump,
        reason=reason,
    )


def render_release_notes(project_name: str, version: str | None, changes: List[ChangeEntry]) -> str:
    title_version = version or "Unreleased"
    lines = [f"# {project_name} {title_version} Release Notes", ""]
    if not changes:
        lines.extend([
            "No commits were found for this release range.",
            "",
            "Review the repository manually before publishing a release.",
            "",
        ])
        return "\n".join(lines)

    analysis = analyze_changes(changes)
    lines.extend([
        "## Summary",
        "",
        f"- Suggested bump: **{analysis.suggested_bump}**",
        f"- Reason: {analysis.reason}",
        f"- Commits analyzed: {analysis.total}",
        "",
        "## Highlights",
        "",
    ])
    highlights = _highlights(changes)
    if highlights:
        lines.extend(f"- {entry}" for entry in highlights)
    else:
        lines.append("- Maintenance and repository updates.")
    lines.append("")

    lines.extend(_grouped_change_lines(changes, legacy_titles=True))
    return "\n".join(lines).rstrip() + "\n"


def render_github_release(project_name: str, version: str | None, changes: List[ChangeEntry]) -> str:
    title_version = version or "Unreleased"
    analysis = analyze_changes(changes)
    lines = [
        f"# {project_name} {title_version}",
        "",
        "## Release Summary",
        "",
        f"ShipCheck analyzed {analysis.total} commit{'s' if analysis.total != 1 else ''} for this release.",
        f"Suggested release type: **{analysis.suggested_bump}**.",
        "",
        "## What Changed",
        "",
    ]
    if changes:
        lines.extend(_grouped_change_lines(changes, legacy_titles=False))
    else:
        lines.append("No commits were found for this release range.")
        lines.append("")
    lines.extend([
        "## Before Publishing",
        "",
        "- [ ] Confirm the version number is correct",
        "- [ ] Confirm tests and release checks pass",
        "- [ ] Review changelog and release notes",
        "- [ ] Create or push the release tag",
        "- [ ] Publish the GitHub release",
        "",
    ])
    return "\n".join(lines).rstrip() + "\n"


def render_changelog_entry(project_name: str, version: str, changes: List[ChangeEntry]) -> str:
    del project_name
    lines = [f"## {version} - {date.today().isoformat()}", ""]
    if not changes:
        lines.append("- Release prepared with no detected commit entries.")
        lines.append("")
        return "\n".join(lines)
    lines.extend(_grouped_change_lines(changes, legacy_titles=False))
    return "\n".join(lines).rstrip() + "\n"


def update_changelog(path: Path, project_name: str, version: str, changes: List[ChangeEntry]) -> None:
    entry = render_changelog_entry(project_name, version, changes)
    if path.exists():
        existing = read_text(path)
        if existing.startswith("# Changelog"):
            lines = existing.splitlines()
            if len(lines) >= 1:
                new_text = lines[0] + "\n\n" + entry + "\n" + "\n".join(lines[1:]).lstrip() + "\n"
            else:
                new_text = "# Changelog\n\n" + entry
        else:
            new_text = "# Changelog\n\n" + entry + "\n" + existing
    else:
        new_text = "# Changelog\n\n" + entry
    write_text(path, new_text.rstrip() + "\n")


def _grouped_change_lines(changes: Sequence[ChangeEntry], legacy_titles: bool) -> List[str]:
    lines: List[str] = []
    for category in CATEGORY_ORDER:
        if category == "breaking":
            grouped = [entry for entry in changes if entry.breaking]
        else:
            grouped = [entry for entry in changes if _normalize_category(entry.category) == category]
            if category != "other":
                grouped = [entry for entry in grouped if not (entry.breaking and category != "breaking")]
        if not grouped:
            continue
        title = LEGACY_TITLES.get(category) if legacy_titles else None
        lines.append(f"## {title or CATEGORY_TITLES.get(category, category.title())}")
        lines.append("")
        for entry in grouped:
            scope = f"**{entry.scope}:** " if entry.scope else ""
            breaking = " **BREAKING**" if entry.breaking and category != "breaking" else ""
            suffix = f" ({entry.commit_hash})" if entry.commit_hash else ""
            lines.append(f"- {scope}{entry.message}{breaking}{suffix}")
        lines.append("")
    return lines


def _highlights(changes: Sequence[ChangeEntry]) -> List[str]:
    important = [entry for entry in changes if entry.breaking or _normalize_category(entry.category) in {"feat", "fix", "security"}]
    return [entry.message for entry in important[:5]]


def _normalize_category(category: str) -> str:
    category = category.lower()
    if category in CATEGORY_TITLES:
        return category
    return "other"
