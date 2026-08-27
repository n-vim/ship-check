"""Shared helpers for ShipCheck."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional


SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z.-]+))?$"
)


@dataclass(frozen=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    def base(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __str__(self) -> str:
        value = self.base()
        if self.prerelease:
            value += f"-{self.prerelease}"
        if self.build:
            value += f"+{self.build}"
        return value


def normalize_root(path: str | Path) -> Path:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")
    return root


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def safe_relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def first_existing(root: Path, names: Iterable[str]) -> Optional[Path]:
    for name in names:
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def any_exists(root: Path, names: Iterable[str]) -> bool:
    return first_existing(root, names) is not None


def list_existing(root: Path, names: Iterable[str]) -> List[str]:
    return [name for name in names if (root / name).exists()]


def contains_any_file(root: Path, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if any(root.glob(pattern)):
            return True
    return False


def parse_semver_full(version: str) -> SemanticVersion:
    match = SEMVER_RE.fullmatch(version.strip())
    if not match:
        raise ValueError(f"Invalid semantic version: {version}")
    return SemanticVersion(
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        prerelease=match.group("prerelease"),
        build=match.group("build"),
    )


def parse_semver(version: str) -> tuple[int, int, int]:
    parsed = parse_semver_full(version)
    return parsed.major, parsed.minor, parsed.patch


def bump_version(version: str, level: str) -> str:
    parsed = parse_semver_full(version)
    if level == "major":
        return f"{parsed.major + 1}.0.0"
    if level == "minor":
        return f"{parsed.major}.{parsed.minor + 1}.0"
    if level == "patch":
        return f"{parsed.major}.{parsed.minor}.{parsed.patch + 1}"
    if level == "prerelease":
        return bump_prerelease(version)
    raise ValueError("Bump level must be one of: patch, minor, major, prerelease")


def bump_prerelease(version: str, tag: str = "rc") -> str:
    parsed = parse_semver_full(version)
    tag = _safe_prerelease_tag(tag)
    if not parsed.prerelease:
        return f"{parsed.major}.{parsed.minor}.{parsed.patch}-{tag}.1"

    parts = parsed.prerelease.split(".")
    current_tag = parts[0]
    if current_tag != tag:
        return f"{parsed.major}.{parsed.minor}.{parsed.patch}-{tag}.1"

    number = 1
    if len(parts) > 1 and parts[-1].isdigit():
        number = int(parts[-1]) + 1
    return f"{parsed.major}.{parsed.minor}.{parsed.patch}-{tag}.{number}"


def _safe_prerelease_tag(tag: str) -> str:
    value = tag.strip().lower()
    if not re.fullmatch(r"[0-9a-z][0-9a-z.-]*", value):
        raise ValueError("Prerelease tag must contain only letters, numbers, dots, and hyphens")
    return value


def markdown_escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()
