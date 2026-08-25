"""Data models used by ShipCheck."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ProjectInfo:
    """Detected information about a project."""

    root: Path
    name: str
    kind: str
    markers: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class VersionInfo:
    """Version details detected from a project manifest."""

    current: Optional[str]
    source: Optional[Path] = None
    field_name: Optional[str] = None

    @property
    def found(self) -> bool:
        return bool(self.current and self.source)


@dataclass(frozen=True)
class GitInfo:
    """A safe snapshot of git repository state."""

    available: bool
    branch: Optional[str] = None
    dirty: bool = False
    latest_tag: Optional[str] = None
    latest_tag_date: Optional[str] = None
    commits_since_tag: int = 0
    commit_messages: List[str] = field(default_factory=list)
    commit_authors: List[str] = field(default_factory=list)
    remote_url: Optional[str] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class ChangeEntry:
    """A parsed commit or changelog entry used for release notes."""

    category: str
    message: str
    scope: Optional[str] = None
    breaking: bool = False
    commit_hash: Optional[str] = None
    raw: Optional[str] = None


@dataclass(frozen=True)
class CommitAnalysis:
    """Summary of commit messages and the suggested semantic release level."""

    total: int
    features: int
    fixes: int
    breaking: int
    docs: int
    tests: int
    chores: int
    other: int
    suggested_bump: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ReleaseProfile:
    """Profile-specific release expectations."""

    name: str
    description: str
    required_files: List[str] = field(default_factory=list)
    recommended_files: List[str] = field(default_factory=list)
    required_markers: List[str] = field(default_factory=list)
    checklist_items: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CheckResult:
    """A release readiness check result."""

    key: str
    title: str
    passed: bool
    weight: int
    message: str
    suggestion: Optional[str] = None
    severity: str = "warning"


@dataclass(frozen=True)
class ReleaseReport:
    """Complete release readiness report."""

    project: ProjectInfo
    version: VersionInfo
    git: GitInfo
    checks: List[CheckResult]
    changes: List[ChangeEntry]
    score: int
    status: str
    suggested_bump: str
    suggested_version: Optional[str]
    profile: str = "auto"
    analysis: Optional[CommitAnalysis] = None

    @property
    def passed_checks(self) -> List[CheckResult]:
        return [check for check in self.checks if check.passed]

    @property
    def failed_checks(self) -> List[CheckResult]:
        return [check for check in self.checks if not check.passed]

    @property
    def blockers(self) -> List[CheckResult]:
        return [check for check in self.failed_checks if check.severity == "error"]

    @property
    def warnings(self) -> List[CheckResult]:
        return [check for check in self.failed_checks if check.severity != "error"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project": {
                "name": self.project.name,
                "kind": self.project.kind,
                "root": str(self.project.root),
                "markers": self.project.markers,
            },
            "version": {
                "current": self.version.current,
                "source": str(self.version.source) if self.version.source else None,
                "field_name": self.version.field_name,
            },
            "git": {
                "available": self.git.available,
                "branch": self.git.branch,
                "dirty": self.git.dirty,
                "latest_tag": self.git.latest_tag,
                "latest_tag_date": self.git.latest_tag_date,
                "commits_since_tag": self.git.commits_since_tag,
                "commit_messages": self.git.commit_messages,
                "commit_authors": self.git.commit_authors,
                "remote_url": self.git.remote_url,
                "error": self.git.error,
            },
            "score": self.score,
            "status": self.status,
            "profile": self.profile,
            "suggested_bump": self.suggested_bump,
            "suggested_version": self.suggested_version,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "checks": [check.__dict__ for check in self.checks],
            "changes": [change.__dict__ for change in self.changes],
        }
