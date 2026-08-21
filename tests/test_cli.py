from pathlib import Path

from typer.testing import CliRunner

from shipcheck.cli import app

runner = CliRunner()


def test_cli_detect(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")

    result = runner.invoke(app, ["detect", str(tmp_path)])

    assert result.exit_code == 0
    assert "demo" in result.output


def test_cli_status_json(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")

    result = runner.invoke(app, ["status", str(tmp_path), "--format", "json"])

    assert result.exit_code == 0
    assert '"project"' in result.output


def test_cli_init(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / ".shipcheck.yaml").exists()
