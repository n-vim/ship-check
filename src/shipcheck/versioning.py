"""Version detection and bumping."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

from .changelog import analyze_changes, parse_commit_messages
from .models import VersionInfo
from .utils import bump_prerelease, bump_version, read_json, read_text, write_text


VERSION_LINE_RE = re.compile(r'(?P<prefix>version\s*=\s*["\'])(?P<version>[^"\']+)(?P<suffix>["\'])')
INIT_VERSION_RE = re.compile(r'(?P<prefix>__version__\s*=\s*["\'])(?P<version>[^"\']+)(?P<suffix>["\'])')


def detect_version(root: Path) -> VersionInfo:
    detectors = [
        _detect_pyproject,
        _detect_package_json,
        _detect_cargo,
        _detect_go,
        _detect_init_version,
    ]
    for detector in detectors:
        info = detector(root)
        if info.found:
            return info
    return VersionInfo(current=None)


def _detect_pyproject(root: Path) -> VersionInfo:
    path = root / "pyproject.toml"
    if not path.exists():
        return VersionInfo(current=None)
    try:
        data = tomllib.loads(read_text(path))
        project = data.get("project", {})
        if isinstance(project, dict) and project.get("version"):
            return VersionInfo(str(project["version"]), path, "project.version")
        poetry = data.get("tool", {}).get("poetry", {})
        if isinstance(poetry, dict) and poetry.get("version"):
            return VersionInfo(str(poetry["version"]), path, "tool.poetry.version")
    except Exception:
        match = VERSION_LINE_RE.search(read_text(path))
        if match:
            return VersionInfo(match.group("version"), path, "version")
    return VersionInfo(current=None)


def _detect_package_json(root: Path) -> VersionInfo:
    path = root / "package.json"
    if not path.exists():
        return VersionInfo(current=None)
    try:
        data = read_json(path)
        if data.get("version"):
            return VersionInfo(str(data["version"]), path, "version")
    except Exception:
        return VersionInfo(current=None)
    return VersionInfo(current=None)


def _detect_cargo(root: Path) -> VersionInfo:
    path = root / "Cargo.toml"
    if not path.exists():
        return VersionInfo(current=None)
    try:
        data = tomllib.loads(read_text(path))
        package = data.get("package", {})
        if isinstance(package, dict) and package.get("version"):
            return VersionInfo(str(package["version"]), path, "package.version")
    except Exception:
        return VersionInfo(current=None)
    return VersionInfo(current=None)


def _detect_go(root: Path) -> VersionInfo:
    path = root / "VERSION"
    if path.exists():
        value = read_text(path).strip()
        if value:
            return VersionInfo(value, path, "VERSION")
    return VersionInfo(current=None)


def _detect_init_version(root: Path) -> VersionInfo:
    for path in root.glob("src/**/__init__.py"):
        match = INIT_VERSION_RE.search(read_text(path))
        if match:
            return VersionInfo(match.group("version"), path, "__version__")
    for path in root.glob("*/__init__.py"):
        match = INIT_VERSION_RE.search(read_text(path))
        if match:
            return VersionInfo(match.group("version"), path, "__version__")
    return VersionInfo(current=None)


def update_version(root: Path, level: str, force_version: Optional[str] = None, prerelease_tag: str = "rc") -> VersionInfo:
    info = detect_version(root)
    if not info.found or not info.source or not info.current:
        raise FileNotFoundError("Could not find a supported version field")

    if force_version:
        next_version = force_version
    elif level == "prerelease":
        next_version = bump_prerelease(info.current, prerelease_tag)
    else:
        next_version = bump_version(info.current, level)
    path = info.source

    if path.name == "package.json":
        data = json.loads(read_text(path))
        data["version"] = next_version
        write_text(path, json.dumps(data, indent=2) + "\n")
        return VersionInfo(next_version, path, info.field_name)

    if path.name in {"pyproject.toml", "Cargo.toml"}:
        text = read_text(path)
        new_text, count = VERSION_LINE_RE.subn(lambda m: f'{m.group("prefix")}{next_version}{m.group("suffix")}', text, count=1)
        if count == 0:
            raise ValueError(f"Could not update version in {path}")
        write_text(path, new_text)
        return VersionInfo(next_version, path, info.field_name)

    if path.name == "__init__.py":
        text = read_text(path)
        new_text, count = INIT_VERSION_RE.subn(lambda m: f'{m.group("prefix")}{next_version}{m.group("suffix")}', text, count=1)
        if count == 0:
            raise ValueError(f"Could not update version in {path}")
        write_text(path, new_text)
        return VersionInfo(next_version, path, info.field_name)

    if path.name == "VERSION":
        write_text(path, next_version + "\n")
        return VersionInfo(next_version, path, info.field_name)

    raise ValueError(f"Unsupported version file: {path}")


def choose_bump_from_messages(messages: list[str], default: str = "patch") -> str:
    entries = parse_commit_messages(messages)
    return analyze_changes(entries, default).suggested_bump
