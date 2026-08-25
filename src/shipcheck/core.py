"""Core orchestration for ShipCheck."""

from __future__ import annotations

from pathlib import Path

from .changelog import analyze_changes, parse_commit_messages
from .checks import run_checks, score_checks, status_from_score
from .config import ShipCheckConfig, load_config
from .detector import detect_project
from .git import get_git_info
from .models import ReleaseReport
from .profiles import resolve_profile
from .utils import bump_version
from .versioning import detect_version


def build_report(root: Path, config: ShipCheckConfig | None = None, profile_name: str | None = None) -> ReleaseReport:
    config = config or load_config(root)
    project = detect_project(root)
    version = detect_version(root)
    git = get_git_info(root)
    changes = parse_commit_messages(git.commit_messages)
    profile = resolve_profile(profile_name or config.default_profile, project)
    analysis = analyze_changes(changes, config.default_bump)
    checks = run_checks(root, project, version, git, config, profile)
    score = score_checks(checks)
    status = status_from_score(score, config)
    bump = analysis.suggested_bump
    suggested_version = bump_version(version.current, bump) if version.current else None
    return ReleaseReport(
        project=project,
        version=version,
        git=git,
        checks=checks,
        changes=changes,
        score=score,
        status=status,
        suggested_bump=bump,
        suggested_version=suggested_version,
        profile=profile.name,
        analysis=analysis,
    )
