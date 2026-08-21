from pathlib import Path

from typer.testing import CliRunner

from shipcheck.changelog import analyze_changes, parse_commit_messages, render_github_release
from shipcheck.cli import app
from shipcheck.profiles import resolve_profile
from shipcheck.utils import bump_prerelease


runner = CliRunner()


def test_analyze_changes_detects_major_bump() -> None:
    changes = parse_commit_messages([
        "abc123\tfeat!: change config format",
        "def456\tfix: handle tag lookup",
    ])
    analysis = analyze_changes(changes)
    assert analysis.suggested_bump == "major"
    assert analysis.breaking == 1


def test_bump_prerelease_starts_and_increments() -> None:
    assert bump_prerelease("1.2.3", "beta") == "1.2.3-beta.1"
    assert bump_prerelease("1.2.3-beta.1", "beta") == "1.2.3-beta.2"
    assert bump_prerelease("1.2.3-beta.2", "rc") == "1.2.3-rc.1"


def test_render_github_release_contains_checklist() -> None:
    changes = parse_commit_messages(["abc123\tfeat(cli): add analyze command"])
    text = render_github_release("demo", "1.1.0", changes)
    assert "# demo 1.1.0" in text
    assert "## Before Publishing" in text
    assert "add analyze command" in text


def test_profile_resolution_for_python(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")
    from shipcheck.detector import detect_project

    profile = resolve_profile("auto", detect_project(tmp_path))
    assert profile.name == "python"


def test_cli_analyze_json(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")
    result = runner.invoke(app, ["analyze", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0
    assert '"suggested_bump"' in result.output


def test_cli_profiles() -> None:
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "python" in result.output
    assert "library" in result.output
