"""Release readiness checks."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .config import ShipCheckConfig
from .models import CheckResult, GitInfo, ProjectInfo, ReleaseProfile, VersionInfo
from .profiles import match_any_marker
from .utils import any_exists, contains_any_file


def run_checks(
    root: Path,
    project: ProjectInfo,
    version: VersionInfo,
    git: GitInfo,
    config: ShipCheckConfig,
    profile: ReleaseProfile,
) -> List[CheckResult]:
    checks = [
        _check_readme(root),
        _check_license(root),
        _check_version(version),
        _check_changelog(root, config),
        _check_tests(root, project, config),
        _check_ci(root, config),
        _check_security(root, config),
        _check_git(git, config),
        _check_release_branch(git, config),
        _check_tags(git, config),
        _check_commit_range(git),
        _check_profile_markers(project, profile),
        _check_profile_required_files(root, profile),
        _check_profile_recommended_files(root, profile),
    ]
    return checks


def score_checks(checks: List[CheckResult]) -> int:
    total = sum(check.weight for check in checks)
    if total <= 0:
        return 0
    earned = sum(check.weight for check in checks if check.passed)
    return round((earned / total) * 100)


def status_from_score(score: int, config: ShipCheckConfig) -> str:
    if score < config.fail_below:
        return "Needs work"
    if score < config.warn_below:
        return "Ready with warnings"
    return "Release ready"


def _check_readme(root: Path) -> CheckResult:
    found = any_exists(root, ["README.md", "README.rst", "README.txt"])
    return CheckResult(
        key="readme",
        title="README found",
        passed=found,
        weight=12,
        message="A README file is present." if found else "No README file was found.",
        suggestion="Add a clear README before publishing a release.",
    )


def _check_license(root: Path) -> CheckResult:
    found = any_exists(root, ["LICENSE", "LICENSE.md", "COPYING"])
    return CheckResult(
        key="license",
        title="License found",
        passed=found,
        weight=10,
        message="A license file is present." if found else "No license file was found.",
        suggestion="Add a license file so users know how the project can be used.",
    )


def _check_version(version: VersionInfo) -> CheckResult:
    found = version.found
    return CheckResult(
        key="version",
        title="Version detected",
        passed=found,
        weight=14,
        message=f"Version {version.current} found in {version.source.name}." if found and version.source else "No supported version field was found.",
        suggestion="Add a version to pyproject.toml, package.json, Cargo.toml, VERSION, or __init__.py.",
        severity="error" if not found else "warning",
    )


def _check_changelog(root: Path, config: ShipCheckConfig) -> CheckResult:
    if not config.require_changelog:
        return CheckResult("changelog", "Changelog found", True, 6, "Changelog check is disabled.")
    path = root / config.changelog_path
    found = path.exists()
    return CheckResult(
        key="changelog",
        title="Changelog found",
        passed=found,
        weight=8,
        message=f"{config.changelog_path} is present." if found else f"{config.changelog_path} is missing.",
        suggestion="Add a changelog or let ShipCheck generate one.",
    )


def _check_tests(root: Path, project: ProjectInfo, config: ShipCheckConfig) -> CheckResult:
    if not config.require_tests:
        return CheckResult("tests", "Tests configured", True, 8, "Test checks are disabled.")
    patterns = ["**/test_*.py", "**/*_test.py", "**/*.test.js", "**/*.spec.ts", "**/*_test.go", "**/*.rs"]
    found = any((root / pattern).exists() for pattern in ["tests", "test", "spec"]) or contains_any_file(root, patterns)
    return CheckResult(
        key="tests",
        title="Tests found",
        passed=found,
        weight=10,
        message="Test files or folders were found." if found else "No tests were found.",
        suggestion=f"Add tests for the {project.kind} project before release.",
    )


def _check_ci(root: Path, config: ShipCheckConfig) -> CheckResult:
    if not config.require_ci:
        return CheckResult("ci", "CI configured", True, 8, "CI checks are disabled.")
    found = contains_any_file(root, [".github/workflows/*.yml", ".github/workflows/*.yaml", ".gitlab-ci.yml", "azure-pipelines.yml"])
    return CheckResult(
        key="ci",
        title="CI workflow found",
        passed=found,
        weight=10,
        message="A CI workflow was found." if found else "No CI workflow was found.",
        suggestion="Add a CI workflow to run tests before release.",
    )


def _check_security(root: Path, config: ShipCheckConfig) -> CheckResult:
    found = any_exists(root, ["SECURITY.md", ".github/SECURITY.md"])
    return CheckResult(
        key="security",
        title="Security policy found",
        passed=found or not config.require_security_policy,
        weight=6,
        message="A security policy is present." if found else "No security policy was found.",
        suggestion="Add SECURITY.md for responsible vulnerability reporting.",
        severity="error" if config.require_security_policy else "warning",
    )


def _check_git(git: GitInfo, config: ShipCheckConfig) -> CheckResult:
    if not git.available:
        return CheckResult(
            key="git",
            title="Git repository detected",
            passed=False,
            weight=10,
            message="This folder is not a git repository.",
            suggestion="Initialize git or run ShipCheck inside a repository.",
            severity="error",
        )
    if config.require_clean_worktree and git.dirty:
        return CheckResult(
            key="clean-worktree",
            title="Clean git worktree",
            passed=False,
            weight=12,
            message="Git has uncommitted changes.",
            suggestion="Commit, stash, or discard changes before release.",
            severity="error",
        )
    return CheckResult(
        key="clean-worktree",
        title="Clean git worktree",
        passed=True,
        weight=12,
        message="Git worktree is clean." if not git.dirty else "Git worktree has changes, but this check is disabled.",
    )


def _check_release_branch(git: GitInfo, config: ShipCheckConfig) -> CheckResult:
    if not git.available:
        return CheckResult("release-branch", "Release branch", False, 5, "Git branch could not be detected.", "Run inside a git repository.")
    allowed = {config.release_branch, "master", "main"}
    passed = bool(git.branch and git.branch in allowed)
    return CheckResult(
        key="release-branch",
        title="Release branch",
        passed=passed,
        weight=5,
        message=f"Current branch is {git.branch}." if git.branch else "No branch was detected.",
        suggestion=f"Release from {config.release_branch} or update .shipcheck.yaml.",
    )


def _check_tags(git: GitInfo, config: ShipCheckConfig) -> CheckResult:
    if not git.available:
        return CheckResult("tags", "Previous release tag", False, 5, "Git tags could not be checked.", "Run inside a git repository.")
    found = bool(git.latest_tag)
    return CheckResult(
        key="tags",
        title="Previous release tag",
        passed=found or not config.require_previous_tag,
        weight=5,
        message=f"Latest tag is {git.latest_tag}." if found else "No previous git tag was found.",
        suggestion="Create tags for releases so changelogs can use clean ranges.",
        severity="error" if config.require_previous_tag else "warning",
    )


def _check_commit_range(git: GitInfo) -> CheckResult:
    if not git.available:
        return CheckResult("commits", "Commits available", False, 5, "Commit history could not be checked.", "Run inside a git repository.")
    found = git.commits_since_tag > 0
    return CheckResult(
        key="commits",
        title="Release commits found",
        passed=found,
        weight=6,
        message=f"{git.commits_since_tag} commit(s) found since latest tag." if found else "No commits were found for the release range.",
        suggestion="Make release-worthy changes or check your latest tag.",
    )


def _check_profile_markers(project: ProjectInfo, profile: ReleaseProfile) -> CheckResult:
    if not profile.required_markers:
        return CheckResult("profile-markers", "Profile markers", True, 4, f"The {profile.name} profile has no required markers.")
    passed = match_any_marker(project.markers, profile.required_markers)
    return CheckResult(
        key="profile-markers",
        title=f"{profile.name} profile markers",
        passed=passed,
        weight=6,
        message="Required profile markers were found." if passed else f"Missing markers for the {profile.name} profile.",
        suggestion=f"Add one of: {', '.join(profile.required_markers)}.",
    )


def _check_profile_required_files(root: Path, profile: ReleaseProfile) -> CheckResult:
    missing = [name for name in profile.required_files if not (root / name).exists()]
    return CheckResult(
        key="profile-required-files",
        title=f"{profile.name} required files",
        passed=not missing,
        weight=8,
        message="All required profile files are present." if not missing else f"Missing: {', '.join(missing)}.",
        suggestion="Add the required files before release.",
        severity="error" if missing else "warning",
    )


def _check_profile_recommended_files(root: Path, profile: ReleaseProfile) -> CheckResult:
    missing = [name for name in profile.recommended_files if not (root / name).exists()]
    return CheckResult(
        key="profile-recommended-files",
        title=f"{profile.name} recommended files",
        passed=not missing,
        weight=4,
        message="All recommended profile files are present." if not missing else f"Recommended files missing: {', '.join(missing)}.",
        suggestion="Add recommended files for a more complete release process.",
    )
