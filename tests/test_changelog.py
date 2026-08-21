from pathlib import Path

from shipcheck.changelog import parse_commit_messages, render_release_notes, update_changelog


def test_parse_conventional_commits_with_hash() -> None:
    entries = parse_commit_messages([
        "abc123\tfeat(cli): add status command",
        "def456\tfix: handle missing tags",
        "docs: improve readme",
    ])

    assert entries[0].category == "feat"
    assert entries[0].scope == "cli"
    assert entries[0].commit_hash == "abc123"
    assert entries[1].category == "fix"
    assert entries[2].category == "docs"


def test_render_release_notes_groups_changes() -> None:
    entries = parse_commit_messages([
        "abc123\tfeat: add markdown output",
        "def456\tfix: handle empty commits",
    ])

    notes = render_release_notes("demo", "1.0.0", entries)

    assert "# demo 1.0.0 Release Notes" in notes
    assert "## Features" in notes
    assert "## Fixes" in notes


def test_update_changelog_creates_file(tmp_path: Path) -> None:
    entries = parse_commit_messages(["abc123\tfeat: add notes"])
    path = tmp_path / "CHANGELOG.md"

    update_changelog(path, "demo", "1.0.0", entries)

    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Changelog")
    assert "1.0.0" in text
    assert "add notes" in text
