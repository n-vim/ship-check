# Contributing to ShipCheck

Thank you for your interest in contributing to ShipCheck.

ShipCheck is a Python CLI that helps developers check release readiness, analyze commits, generate changelogs, draft release notes, and prepare release checklists. The project should stay practical, lightweight, readable, and safe to run on local repositories.

---

## Ways to Contribute

You can help by:

- Fixing bugs
- Improving release readiness checks
- Adding new release profiles
- Improving conventional commit analysis
- Improving changelog output
- Improving release notes formatting
- Adding tests
- Improving documentation
- Improving CLI messages
- Suggesting useful release workflow features

Small improvements are welcome.

---

## Development Setup

Clone the repository:

```bash
git clone https://github.com/n-vim/ship-check.git
cd ship-check
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the CLI:

```bash
shipcheck --help
```

---

## Running Tests

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run a single test file:

```bash
pytest tests/test_versioning.py
```

Please make sure tests pass before opening a pull request.

---

## Code Quality

Run linting:

```bash
ruff check .
```

Run type checking:

```bash
mypy src
```

Keep code readable and direct. Avoid adding heavy dependencies unless they clearly improve the project.

---

## Pull Request Guidelines

Before opening a pull request:

- Keep the change focused
- Explain what changed and why
- Add tests for new behavior
- Update docs when commands or output change
- Avoid committing cache or build files
- Avoid unrelated formatting changes
- Keep CLI behavior safe and predictable

A good pull request should be easy to review and easy to test.

---

## Adding a New Check

When adding a release readiness check:

1. Add clear check logic.
2. Give the check a useful message.
3. Provide an actionable suggestion.
4. Add tests for passing and failing cases.
5. Keep severity reasonable.
6. Avoid noisy checks that do not help users release better software.

---

## Adding a New Profile

Release profiles should represent real release workflows.

A good profile includes:

- Required files
- Recommended files
- Expected project markers
- Practical release checklist items

Profiles should stay useful without being overly strict.

---

## Commit Messages

Use clear commit messages.

Good examples:

```text
feat: add profile command
fix: handle projects without tags
docs: improve changelog examples
test: add prerelease version tests
```

Avoid unclear messages like:

```text
update
changes
fix stuff
final
```

---

## What to Avoid

Please avoid:

- Running scanned project code
- Adding network behavior to normal scans
- Printing secret values
- Adding large dependencies without discussion
- Making the CLI complicated
- Adding unrelated files
- Committing generated cache folders

ShipCheck should remain safe, local, and easy to understand.

---

## License

By contributing to ShipCheck, you agree that your contributions will be licensed under the MIT License.
