from pathlib import Path

from shipcheck.core import build_report
from shipcheck.reports import render_json, render_markdown, render_checklist


def _project(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")
    return tmp_path


def test_render_markdown_report(tmp_path: Path) -> None:
    report = build_report(_project(tmp_path))
    markdown = render_markdown(report)
    assert "# ShipCheck Release Report" in markdown
    assert "demo" in markdown


def test_render_json_report(tmp_path: Path) -> None:
    report = build_report(_project(tmp_path))
    text = render_json(report)
    assert '"project"' in text
    assert '"demo"' in text


def test_render_checklist(tmp_path: Path) -> None:
    report = build_report(_project(tmp_path))
    text = render_checklist(report)
    assert "# Release Checklist" in text
    assert "Project: demo" in text
