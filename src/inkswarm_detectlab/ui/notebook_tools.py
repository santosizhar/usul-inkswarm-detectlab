"""Convenience helpers for interactive notebooks.

These helpers are stdlib-only and geared toward quick iteration:
- locate a run folder by run_id
- print common artifact paths
- tail log files for step visibility
"""

from __future__ import annotations

from pathlib import Path


def find_run_dir(root: str | Path, run_id: str) -> Path:
    """Return <root>/runs/<run_id> (or raise FileNotFoundError)."""
    root_p = Path(root)
    p = root_p / "runs" / run_id
    if not p.exists():
        raise FileNotFoundError(f"Run dir not found: {p}")
    return p


def print_run_tree(run_dir: str | Path) -> None:
    """Print a compact view of the run folder structure."""
    p = Path(run_dir)
    for rel in [
        "share/logs",
        "share/reports",
        "models",
        "reports",
        "logs",
    ]:
        q = p / rel
        print(f"- {rel}: {q} {'(missing)' if not q.exists() else ''}")


def tail_text(path: str | Path, n_lines: int = 200) -> str:
    """Return the last n_lines of a text file (best-effort)."""
    p = Path(path)
    if not p.exists():
        return f"<missing: {p}>"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n_lines:])
    except Exception as e:  # pragma: no cover
        return f"<error reading {p}: {e}>"
