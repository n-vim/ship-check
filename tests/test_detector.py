from pathlib import Path

from shipcheck.detector import detect_project


def test_detect_python_project(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "sample-app"\nversion = "0.1.0"\n', encoding="utf-8")

    project = detect_project(tmp_path)

    assert project.kind == "python"
    assert project.name == "sample-app"
    assert "pyproject.toml" in project.markers


def test_detect_node_project(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "web-app", "version": "1.0.0"}', encoding="utf-8")

    project = detect_project(tmp_path)

    assert project.kind == "node"
    assert project.name == "web-app"


def test_detect_general_project(tmp_path: Path) -> None:
    project = detect_project(tmp_path)

    assert project.kind == "general"
    assert project.name == tmp_path.name
