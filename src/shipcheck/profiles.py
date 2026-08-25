"""Release profiles for different project types."""

from __future__ import annotations

from typing import Dict, Iterable, List

from .models import ProjectInfo, ReleaseProfile


PROFILES: Dict[str, ReleaseProfile] = {
    "general": ReleaseProfile(
        name="general",
        description="General repository release checks for most projects.",
        required_files=["README.md", "LICENSE"],
        recommended_files=["CHANGELOG.md", "SECURITY.md", ".github/workflows/ci.yml"],
        checklist_items=[
            "Confirm public documentation is current",
            "Confirm license and security policy are present",
            "Create a release tag",
        ],
    ),
    "python": ReleaseProfile(
        name="python",
        description="Python project checks for packages, APIs, CLIs, and automation tools.",
        required_files=["README.md", "LICENSE", "pyproject.toml"],
        recommended_files=["CHANGELOG.md", "tests", ".github/workflows/ci.yml", "SECURITY.md"],
        required_markers=["pyproject.toml"],
        checklist_items=[
            "Run pytest",
            "Run linting and type checks if configured",
            "Confirm pyproject.toml has the release version",
            "Build the package locally before publishing",
        ],
    ),
    "npm": ReleaseProfile(
        name="npm",
        description="Node and npm package release checks.",
        required_files=["README.md", "LICENSE", "package.json"],
        recommended_files=["CHANGELOG.md", "package-lock.json", ".github/workflows/ci.yml"],
        required_markers=["package.json"],
        checklist_items=[
            "Run npm test if available",
            "Confirm package.json version is correct",
            "Confirm package files are ready for publishing",
        ],
    ),
    "node": ReleaseProfile(
        name="node",
        description="Node project release checks.",
        required_files=["README.md", "LICENSE", "package.json"],
        recommended_files=["CHANGELOG.md", ".github/workflows/ci.yml"],
        required_markers=["package.json"],
        checklist_items=[
            "Run test and build scripts",
            "Confirm package metadata is correct",
            "Draft the GitHub release notes",
        ],
    ),
    "library": ReleaseProfile(
        name="library",
        description="Reusable library checks with stronger documentation and changelog expectations.",
        required_files=["README.md", "LICENSE", "CHANGELOG.md"],
        recommended_files=["SECURITY.md", "CONTRIBUTING.md", "tests", ".github/workflows/ci.yml"],
        checklist_items=[
            "Confirm public API changes are documented",
            "Confirm breaking changes are highlighted",
            "Confirm examples are still correct",
        ],
    ),
    "cli": ReleaseProfile(
        name="cli",
        description="Command-line tool checks for release notes, help output, and install guidance.",
        required_files=["README.md", "LICENSE"],
        recommended_files=["CHANGELOG.md", "tests", ".github/workflows/ci.yml"],
        checklist_items=[
            "Run the CLI help command",
            "Test common command examples from the README",
            "Confirm install instructions are accurate",
        ],
    ),
    "rust": ReleaseProfile(
        name="rust",
        description="Rust crate and application release checks.",
        required_files=["README.md", "LICENSE", "Cargo.toml"],
        recommended_files=["CHANGELOG.md", ".github/workflows/ci.yml"],
        required_markers=["Cargo.toml"],
        checklist_items=[
            "Run cargo test",
            "Run cargo clippy if configured",
            "Confirm Cargo.toml version is correct",
        ],
    ),
    "go": ReleaseProfile(
        name="go",
        description="Go module release checks.",
        required_files=["README.md", "LICENSE", "go.mod"],
        recommended_files=["CHANGELOG.md", ".github/workflows/ci.yml"],
        required_markers=["go.mod"],
        checklist_items=[
            "Run go test ./...",
            "Confirm module path is correct",
            "Create a semantic git tag",
        ],
    ),
}


ALIASES = {
    "auto": "auto",
    "js": "node",
    "javascript": "node",
    "typescript": "node",
    "python-cli": "cli",
    "package": "library",
}


def available_profiles() -> List[ReleaseProfile]:
    return [PROFILES[name] for name in sorted(PROFILES)]


def resolve_profile(name: str, project: ProjectInfo | None = None) -> ReleaseProfile:
    selected = ALIASES.get(name.lower(), name.lower())
    if selected == "auto":
        selected = _auto_profile(project)
    if selected not in PROFILES:
        choices = ", ".join(["auto", *sorted(PROFILES)])
        raise KeyError(f"Unknown profile '{name}'. Available profiles: {choices}")
    return PROFILES[selected]


def profile_names() -> List[str]:
    return ["auto", *sorted(PROFILES)]


def _auto_profile(project: ProjectInfo | None) -> str:
    if project is None:
        return "general"
    if project.kind == "python":
        return "python"
    if project.kind == "node":
        return "node"
    if project.kind in {"rust", "go"}:
        return project.kind
    return "general"


def match_any_marker(markers: Iterable[str], required: Iterable[str]) -> bool:
    marker_set = set(markers)
    return any(item in marker_set for item in required)
