from pathlib import Path

from shipcheck.utils import bump_version
from shipcheck.versioning import choose_bump_from_messages, detect_version, update_version


def test_bump_version_levels() -> None:
    assert bump_version("1.2.3", "patch") == "1.2.4"
    assert bump_version("1.2.3", "minor") == "1.3.0"
    assert bump_version("1.2.3", "major") == "2.0.0"


def test_detect_pyproject_version(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\nname = "demo"\nversion = "0.4.0"\n', encoding="utf-8")

    info = detect_version(tmp_path)

    assert info.current == "0.4.0"
    assert info.source == path


def test_update_package_json_version(tmp_path: Path) -> None:
    path = tmp_path / "package.json"
    path.write_text('{"name": "demo", "version": "1.0.0"}', encoding="utf-8")

    info = update_version(tmp_path, "minor")

    assert info.current == "1.1.0"
    assert '"version": "1.1.0"' in path.read_text(encoding="utf-8")


def test_choose_bump_from_messages() -> None:
    assert choose_bump_from_messages(["abcde\tfix: repair bug"], "patch") == "patch"
    assert choose_bump_from_messages(["abcde\tfeat: add output"], "patch") == "minor"
    assert choose_bump_from_messages(["abcde\tfeat!: replace schema"], "patch") == "major"
