# Security Policy

ShipCheck is a local developer tool that reads repository metadata, git history, and project files to generate release readiness reports. It should be safe to run inside local repositories and should never expose secrets or execute project code.

---

## Supported Versions

Security fixes are handled for the latest release and the current `main` branch.

| Version | Supported |
| --- | --- |
| Latest release | Yes |
| `main` branch | Yes |
| Older releases | No |

---

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Use GitHub private vulnerability reporting if it is available for this repository. If private reporting is not available, open a public issue asking for a private contact method, but do not include exploit details, proof-of-concept code, secrets, tokens, or private repository content.

A useful report should include:

- Short summary
- Affected command or module
- Version or commit tested
- Operating system
- Python version
- Safe reproduction steps
- Possible impact
- Suggested fix, if known

---

## Security Scope

Security issues may include:

- Unsafe path handling
- Writing outside the target path
- Printing secret values in reports
- Reading files that should be ignored
- Unexpected command execution
- Unsafe git command usage
- Crashes from crafted file names or repository structures
- Dependency vulnerabilities that affect normal ShipCheck usage

---

## Out of Scope

The following are usually not security vulnerabilities:

- Normal bugs without security impact
- Missing features
- Formatting issues
- Documentation typos
- False positives in checks
- Performance issues without security impact

Please report those as normal GitHub issues.

---

## Security Principles

ShipCheck should:

- Work locally by default
- Avoid network access for normal scans
- Never execute scanned project code
- Never install project dependencies automatically
- Never print secret values
- Avoid writing outside requested output paths
- Handle unusual file names safely
- Keep dependencies minimal
- Fail with clear and safe error messages

---

## Sensitive Files

Repositories may contain sensitive files such as:

- `.env`
- `.env.local`
- Private keys
- API tokens
- Credentials
- Deployment secrets
- Local databases

ShipCheck may warn about risky files, but it should not print secret values or sensitive file contents.

---

## Responsible Disclosure

Please allow reasonable time to investigate and fix valid security issues before public disclosure.

A responsible process is:

1. Report privately.
2. Allow time for review.
3. Help verify the fix if possible.
4. Avoid publishing exploit details before a fix is available.

---

## Thank You

Thank you for helping keep ShipCheck safe and trustworthy.
