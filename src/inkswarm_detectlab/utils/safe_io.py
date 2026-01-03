"""Best-effort I/O helpers shared across modules."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, TypeVar

T = TypeVar("T")


def safe_read_text(path: Path, *, default: Optional[str] = None, encoding: str = "utf-8") -> Optional[str]:
    """Return file contents or ``default`` when missing/unreadable."""
    try:
        return path.read_text(encoding=encoding)
    except Exception:
        return default


def safe_read_json(path: Path, *, default: Optional[T] = None, encoding: str = "utf-8") -> Optional[T]:
    """Return parsed JSON or ``default`` when missing/unreadable."""
    try:
        return json.loads(path.read_text(encoding=encoding))
    except Exception:
        return default


__all__ = ["safe_read_text", "safe_read_json"]


def read_json_strict(path: Path, *, encoding: str = "utf-8") -> Any:
    """Read JSON and raise a helpful error when it fails.

    This is intended for fail-closed surfaces (e.g., RR tooling) where best-effort
    defaults could mask broken artifacts. Exceptions carry file context so callers
    can surface actionable error messages.
    """
    try:
        raw = path.read_text(encoding=encoding)
    except Exception as exc:  # pragma: no cover - exercised in tests
        raise RuntimeError(f"Unable to read JSON file: {path}") from exc

    try:
        return json.loads(raw)
    except Exception as exc:
        raise RuntimeError(f"Invalid JSON in file: {path}") from exc


__all__.append("read_json_strict")
