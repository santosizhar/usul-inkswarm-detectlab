# Secrets hygiene

Before committing, run a secrets scan locally to avoid accidental leaks.

Recommended tools (pick one):
- `gitleaks detect --no-git` (fast, works on working tree)
- `detect-secrets scan > .secrets.baseline` (and audit before committing)

Workflow suggestion:
1. Run `gitleaks detect --no-git` from the repo root.
2. If findings appear, rotate the affected secret, remove the file or line, and re-run.
3. For CI, add a job that executes the same command and fails on findings.

Ignore rules:
- Do not ignore findings globally unless vetted; prefer targeted allowlists.
- Generated artifacts under `runs/` should generally be excluded from scans.
