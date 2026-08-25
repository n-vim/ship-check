"""Project type and metadata detection."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

from .models import ProjectInfo
from .utils import read_json


MARKERS = {
    "python": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"],
    "node": ["package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json"],
    "rust": ["Cargo.toml", "Cargo.lock"],
    "go": ["go.mod", "go.sum"],
    "php": ["composer.json", "composer.lock"],
    "docker": ["Dockerfile", "docker-compose.yml", "compose.yaml"],
}


def detect_project(root: Path) -> ProjectInfo:
    found: dict[str, list[str]] = {}
    for kind, names in MARKERS.items():
        matches = [name for name in names if (root / name).exists()]
        if matches:
            found[kind] = matches

    if "python" in found:
        kind = "python"
    elif "node" in found:
        kind = "node"
    elif "rust" in found:
        kind = "rust"
    elif "go" in found:
        kind = "go"
    elif "php" in found:
        kind = "php"
    elif "docker" in found:
        kind = "docker"
    else:
        kind = "general"

    markers = [marker for values in found.values() for marker in values]
    return ProjectInfo(root=root, name=detect_project_name(root, kind), kind=kind, markers=markers)


def detect_project_name(root: Path, kind: str) -> str:
    if kind == "python":
        name = _name_from_pyproject(root / "pyproject.toml")
        if name:
            return name
    if kind == "node":
        name = _name_from_package_json(root / "package.json")
        if name:
            return name
    if kind == "rust":
        name = _name_from_cargo(root / "Cargo.toml")
        if name:
            return name
    if kind == "go":
        name = _name_from_go_mod(root / "go.mod")
        if name:
            return name
    return root.name


def _name_from_pyproject(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        if isinstance(project, dict) and project.get("name"):
            return str(project["name"])
        poetry = data.get("tool", {}).get("poetry", {})
        if isinstance(poetry, dict) and poetry.get("name"):
            return str(poetry["name"])
    except Exception:
        return None
    return None


def _name_from_package_json(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    try:
        name = read_json(path).get("name")
        return str(name) if name else None
    except Exception:
        return None


def _name_from_cargo(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        package = data.get("package", {})
        if isinstance(package, dict) and package.get("name"):
            return str(package["name"])
    except Exception:
        return None
    return None


def _name_from_go_mod(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        if first_line.startswith("module "):
            return first_line.removeprefix("module ").split("/")[-1]
    except Exception:
        return None
    return None
