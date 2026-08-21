from pathlib import Path

from shipcheck.core import build_report


def test_build_report_for_basic_project(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")

    report = build_report(tmp_path)

    assert report.project.name == "demo"
    assert report.version.current == "0.1.0"
    assert 0 <= report.score <= 100
    assert report.suggested_version == "0.1.1"
