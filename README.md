<div align="center">

# ShipCheck

**A Python CLI for checking release readiness, analyzing commits, generating changelogs, and drafting release notes.**

ShipCheck helps developers prepare clean, confident releases from the command line. It inspects a repository, detects version metadata, reads git history, analyzes conventional commits, suggests a semantic version bump, and generates release-ready Markdown reports.

<br>

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-Typer-0E7C86?style=flat)
![Terminal](https://img.shields.io/badge/Terminal-Rich-4B8BBE?style=flat)
![Config](https://img.shields.io/badge/Config-YAML-yellow?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

</div>

---

## Overview

ShipCheck is a release-readiness assistant for local repositories.

It is designed for developers who want a simple way to answer questions like:

- Is this repository ready for release?
- What version should be released next?
- What changed since the last git tag?
- Do I have a changelog, README, license, tests, and CI?
- Can I generate release notes from commit messages?
- Can I produce a checklist before publishing?

ShipCheck works locally, uses safe git commands, and does not publish anything for you. It gives you clear reports and generated files so you can review everything before releasing.

---

## Features

- Release readiness score out of 100
- Rich terminal report with panels and tables
- Project type detection for Python, Node, Rust, Go, Docker, PHP, and general repos
- Version detection from `pyproject.toml`, `package.json`, `Cargo.toml`, `VERSION`, and `__init__.py`
- Semantic version bump suggestions
- Conventional commit analysis
- Pre-release version bump support such as `alpha`, `beta`, and `rc`
- Changelog generation with categorized sections
- GitHub-ready release notes generation
- Release checklist generation
- Markdown and JSON report export
- Config file support with `.shipcheck.yaml`
- Release profiles for different project types
- Git state checks for dirty worktrees, tags, branches, and commit ranges
- Safe local-only behavior

---

## Installation

Clone the repository:

```bash
git clone https://github.com/n-vim/ship-check.git
cd ship-check
```

Install locally:

```bash
python -m pip install -e .
```

Install with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Check the CLI:

```bash
shipcheck --help
```

You can also use:

```bash
ship-check --help
```

---

## Quick Start

Run a release readiness report:

```bash
shipcheck status .
```

Analyze commits and get a suggested bump:

```bash
shipcheck analyze .
```

Generate release notes:

```bash
shipcheck notes .
```

Generate a GitHub release draft:

```bash
shipcheck release-notes . --output RELEASE.md
```

Generate or update a changelog:

```bash
shipcheck changelog . --force
```

Preview a version bump:

```bash
shipcheck bump patch . --dry-run
```

Create a release checklist:

```bash
shipcheck checklist . --output RELEASE_CHECKLIST.md
```

---

## Commands

| Command | Description |
| --- | --- |
| `status` | Run the full release readiness report |
| `doctor` | Show blockers and warnings |
| `detect` | Detect project type and version source |
| `analyze` | Analyze commit messages and suggest a version bump |
| `notes` | Generate release notes from git commits |
| `release-notes` | Generate a GitHub-ready release draft |
| `changelog` | Create or update `CHANGELOG.md` |
| `bump` | Update the detected project version |
| `checklist` | Generate a release checklist |
| `profiles` | List available release profiles |
| `profile` | Show details for one profile |
| `init` | Create `.shipcheck.yaml` |
| `config` | Show active configuration |

---

## Release Profiles

Profiles let ShipCheck check repositories differently based on release style.

| Profile | Best for |
| --- | --- |
| `auto` | Automatically choose a profile from detected project files |
| `general` | Most repositories |
| `python` | Python packages, APIs, CLIs, and automation tools |
| `node` | Node.js projects |
| `npm` | npm packages |
| `library` | Reusable libraries with stronger docs and changelog expectations |
| `cli` | Command-line tools |
| `rust` | Rust projects |
| `go` | Go modules |

Use a profile:

```bash
shipcheck status . --profile python
```

View profile information:

```bash
shipcheck profile library
```

---

## Conventional Commit Analysis

ShipCheck understands conventional commit messages like:

```text
feat: add markdown export
fix: handle missing tags
docs: improve usage examples
feat!: change config structure
```

It uses these commits to suggest a semantic version bump:

| Commit type | Suggested bump |
| --- | --- |
| `fix:` | patch |
| `perf:` | patch |
| `security:` | patch |
| `feat:` | minor |
| `feat!:` or breaking change | major |

Analyze commits:

```bash
shipcheck analyze .
```

Export analysis as JSON:

```bash
shipcheck analyze . --format json
```

---

## Version Bumping

ShipCheck can detect and update versions from common project files.

Patch bump:

```bash
shipcheck bump patch .
```

Minor bump:

```bash
shipcheck bump minor .
```

Major bump:

```bash
shipcheck bump major .
```

Set an exact version:

```bash
shipcheck bump patch . --set 1.4.0
```

Preview without writing:

```bash
shipcheck bump minor . --dry-run
```

---

## Pre-release Support

ShipCheck supports pre-release versions:

```bash
shipcheck bump prerelease . --tag alpha
shipcheck bump prerelease . --tag beta
shipcheck bump prerelease . --tag rc
```

Examples:

```text
1.2.3 -> 1.2.3-beta.1
1.2.3-beta.1 -> 1.2.3-beta.2
1.2.3-beta.2 -> 1.2.3-rc.1
```

---

## Changelog Generation

Generate a changelog entry from detected commits:

```bash
shipcheck changelog . --force
```

Preview without writing:

```bash
shipcheck changelog . --dry-run
```

Use a custom version heading:

```bash
shipcheck changelog . --version 1.2.0 --force
```

ShipCheck groups changes into readable sections such as:

- Breaking Changes
- Added
- Fixed
- Security
- Performance
- Changed
- Documentation
- Tests
- Build
- CI
- Chores

---

## Release Notes

Generate normal release notes:

```bash
shipcheck notes .
```

Generate a GitHub release draft:

```bash
shipcheck release-notes .
```

Save to a file:

```bash
shipcheck release-notes . --output RELEASE.md
```

---

## Reports

Terminal report:

```bash
shipcheck status .
```

Markdown report:

```bash
shipcheck status . --format markdown --output SHIPCHECK_REPORT.md
```

JSON report:

```bash
shipcheck status . --format json --output shipcheck-report.json
```

Doctor report:

```bash
shipcheck doctor .
```

---

## Configuration

Create a config file:

```bash
shipcheck init .
```

Example `.shipcheck.yaml`:

```yaml
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
```

Show active config:

```bash
shipcheck config .
```

---

## Example Workflow

A normal release workflow can look like this:

```bash
shipcheck status .
shipcheck analyze .
shipcheck bump patch . --dry-run
shipcheck changelog . --dry-run
shipcheck release-notes . --output RELEASE.md
shipcheck checklist . --output RELEASE_CHECKLIST.md
```

After reviewing the output, you can update the version and changelog:

```bash
shipcheck bump patch .
shipcheck changelog . --force
```

Then commit, tag, and publish through your normal release process.

---

## Project Structure

```text
ship-check/
├── src/
│   └── shipcheck/
│       ├── __init__.py
│       ├── __main__.py
│       ├── changelog.py
│       ├── checks.py
│       ├── cli.py
│       ├── config.py
│       ├── core.py
│       ├── detector.py
│       ├── git.py
│       ├── models.py
│       ├── profiles.py
│       ├── reports.py
│       ├── utils.py
│       └── versioning.py
├── tests/
├── docs/
├── .github/
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

---

## Development

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Run type checking:

```bash
mypy src
```

Run the CLI locally:

```bash
shipcheck --help
```

---

## Good Use Cases

ShipCheck is useful for:

- Preparing open-source releases
- Generating changelogs from commit history
- Drafting GitHub release notes
- Checking release readiness before tagging
- Teaching semantic versioning workflows
- Keeping project releases consistent
- Automating release reports in local workflows
- Reviewing repositories before publishing updates

---

## Author

Created by **Nitish Vimal**.

GitHub: [n-vim](https://github.com/n-vim)

---

## License

This project is licensed under the MIT License.

---

<div align="center">

**ShipCheck helps you release cleaner projects with more confidence.**

</div>
