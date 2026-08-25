"""Safe git command wrapper."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

from .models import GitInfo


def _git(root: Path, args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def is_git_repo(root: Path) -> bool:
    result = _git(root, ["rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_output(root: Path, args: List[str]) -> Optional[str]:
    result = _git(root, args)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_git_info(root: Path) -> GitInfo:
    if not is_git_repo(root):
        return GitInfo(available=False, error="Not a git repository")

    branch = git_output(root, ["branch", "--show-current"])
    status = git_output(root, ["status", "--porcelain"]) or ""
    dirty = bool(status.strip())
    latest_tag = git_output(root, ["describe", "--tags", "--abbrev=0"])
    latest_tag_date = None
    if latest_tag:
        latest_tag_date = git_output(root, ["log", "-1", "--format=%cs", latest_tag])

    if latest_tag:
        count_raw = git_output(root, ["rev-list", f"{latest_tag}..HEAD", "--count"])
        log_range = f"{latest_tag}..HEAD"
    else:
        count_raw = git_output(root, ["rev-list", "HEAD", "--count"])
        log_range = "HEAD"

    try:
        commits_since_tag = int(count_raw or 0)
    except ValueError:
        commits_since_tag = 0

    log = git_output(root, ["log", "--pretty=format:%h%x09%s", log_range])
    commit_messages = [line for line in (log or "").splitlines() if line.strip()]
    authors = git_output(root, ["log", "--pretty=format:%an", log_range])
    commit_authors = sorted({line for line in (authors or "").splitlines() if line.strip()})
    remote_url = git_output(root, ["config", "--get", "remote.origin.url"])

    return GitInfo(
        available=True,
        branch=branch or None,
        dirty=dirty,
        latest_tag=latest_tag or None,
        latest_tag_date=latest_tag_date or None,
        commits_since_tag=commits_since_tag,
        commit_messages=commit_messages,
        commit_authors=commit_authors,
        remote_url=remote_url or None,
    )
