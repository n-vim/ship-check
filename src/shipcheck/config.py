"""Configuration loading for ShipCheck."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping

import yaml

from .utils import write_text


CONFIG_FILE = ".shipcheck.yaml"


@dataclass(frozen=True)
class ShipCheckConfig:
    """User configurable release readiness settings."""

    release_branch: str = "main"
    warn_below: int = 80
    fail_below: int = 60
    default_bump: str = "patch"
    default_profile: str = "auto"
    require_clean_worktree: bool = True
    require_tests: bool = True
    require_ci: bool = True
    require_changelog: bool = True
    require_security_policy: bool = False
    require_previous_tag: bool = False
    changelog_path: str = "CHANGELOG.md"
    release_notes_path: str = "RELEASE_NOTES.md"
    changelog_style: str = "keepachangelog"
    release_note_style: str = "github"
    ignored_paths: List[str] = field(default_factory=lambda: [
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "__pycache__",
        ".pytest_cache",
    ])
    custom_rules: Mapping[str, bool] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShipCheckConfig":
        defaults = cls()
        release = _dict(data.get("release"))
        checks = _dict(data.get("checks"))
        changelog = _dict(data.get("changelog"))
        report = _dict(data.get("report"))
        return cls(
            release_branch=str(_pick(data, release, "release_branch", defaults.release_branch)),
            warn_below=int(_pick(data, report, "warn_below", defaults.warn_below)),
            fail_below=int(_pick(data, report, "fail_below", defaults.fail_below)),
            default_bump=str(_pick(data, release, "default_bump", defaults.default_bump)),
            default_profile=str(_pick(data, release, "default_profile", defaults.default_profile)),
            require_clean_worktree=bool(_pick(data, checks, "require_clean_worktree", defaults.require_clean_worktree)),
            require_tests=bool(_pick(data, checks, "require_tests", defaults.require_tests)),
            require_ci=bool(_pick(data, checks, "require_ci", defaults.require_ci)),
            require_changelog=bool(_pick(data, checks, "require_changelog", defaults.require_changelog)),
            require_security_policy=bool(_pick(data, checks, "require_security_policy", defaults.require_security_policy)),
            require_previous_tag=bool(_pick(data, checks, "require_previous_tag", defaults.require_previous_tag)),
            changelog_path=str(_pick(data, changelog, "changelog_path", defaults.changelog_path)),
            release_notes_path=str(_pick(data, release, "release_notes_path", defaults.release_notes_path)),
            changelog_style=str(_pick(data, changelog, "style", defaults.changelog_style)),
            release_note_style=str(_pick(data, release, "release_note_style", defaults.release_note_style)),
            ignored_paths=list(data.get("ignored_paths", defaults.ignored_paths)),
            custom_rules=_dict(data.get("rules")),
        )


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _pick(primary: Mapping[str, Any], secondary: Mapping[str, Any], key: str, default: Any) -> Any:
    if key in primary:
        return primary[key]
    if key in secondary:
        return secondary[key]
    return default


def load_config(root: Path) -> ShipCheckConfig:
    path = root / CONFIG_FILE
    if not path.exists():
        return ShipCheckConfig()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return ShipCheckConfig()
    return ShipCheckConfig.from_dict(raw)


def default_config_text() -> str:
    return """# ShipCheck configuration
release:
  default_profile: auto
  default_bump: patch
  release_branch: main
  release_notes_path: RELEASE_NOTES.md
  release_note_style: github

checks:
  require_clean_worktree: true
  require_tests: true
  require_ci: true
  require_changelog: true
  require_security_policy: false
  require_previous_tag: false

changelog:
  changelog_path: CHANGELOG.md
  style: keepachangelog

report:
  warn_below: 80
  fail_below: 60

ignored_paths:
  - .git
  - .venv
  - venv
  - node_modules
  - dist
  - build
  - __pycache__
  - .pytest_cache
"""


def create_default_config(root: Path, force: bool = False) -> Path:
    path = root / CONFIG_FILE
    if path.exists() and not force:
        raise FileExistsError(f"Config already exists: {path}")
    write_text(path, default_config_text())
    return path
