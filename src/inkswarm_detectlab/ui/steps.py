"""Lightweight step tracking for CLI + notebooks.

This is intentionally dependency-light (stdlib only) so notebooks can import it
without extra setup.

Typical usage:

    from inkswarm_detectlab.ui.steps import StepRecorder

    rec = StepRecorder(logger)
    with rec.step("Load dataset"):
        ...
    with rec.step("Train baselines", details={"preset": "fast"}):
        ...

    print(rec.to_markdown())

The recorder also logs stable, greppable lines:

    [STEP_START] <name> key=value ...
    [STEP_END]   <name> duration_s=... status=ok
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
import time


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fmt_kv(details: Optional[Dict[str, Any]]) -> str:
    if not details:
        return ""
    parts: List[str] = []
    for k in sorted(details.keys()):
        v = details[k]
        if v is None:
            continue
        s = str(v)
        s = s.replace("\n", " ")
        parts.append(f"{k}={s}")
    return " ".join(parts)


@dataclass
class StepEvent:
    name: str
    start_utc: str
    end_utc: Optional[str] = None
    duration_s: Optional[float] = None
    status: str = "running"  # running|ok|error
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StepRecorder:
    """Records step events and optionally logs to a logger."""

    def __init__(self, logger: Optional[Any] = None):
        self._logger = logger
        self.events: List[StepEvent] = []

    def log(self, msg: str) -> None:
        if self._logger is None:
            return
        # prefer .info; fall back to print
        fn = getattr(self._logger, "info", None)
        if callable(fn):
            fn(msg)
        else:
            print(msg)

    @contextmanager
    def step(self, name: str, details: Optional[Dict[str, Any]] = None):
        ev = StepEvent(name=name, start_utc=_utc_now_iso(), details=details)
        self.events.append(ev)
        self.log(f"[STEP_START] {name} {_fmt_kv(details)}")
        t0 = time.perf_counter()
        try:
            yield ev
        except Exception as e:  # noqa: BLE001
            ev.status = "error"
            ev.error = f"{type(e).__name__}: {e}"
            raise
        finally:
            ev.end_utc = _utc_now_iso()
            ev.duration_s = round(time.perf_counter() - t0, 3)
            if ev.status != "error":
                ev.status = "ok"
            self.log(
                f"[STEP_END] {name} duration_s={ev.duration_s} status={ev.status}"
                + (f" error={ev.error}" if ev.error else "")
            )

    def to_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for ev in self.events:
            rows.append(
                {
                    "step": ev.name,
                    "status": ev.status,
                    "duration_s": ev.duration_s,
                    "start_utc": ev.start_utc,
                    "end_utc": ev.end_utc,
                    "details": _fmt_kv(ev.details),
                    "error": ev.error,
                }
            )
        return rows

    def to_markdown(self, title: str = "Step summary") -> str:
        rows = self.to_rows()
        if not rows:
            return f"### {title}\n\n(no steps recorded)\n"

        # Simple markdown table (no external deps)
        headers = ["step", "status", "duration_s", "details"]
        lines = [f"### {title}", "", "| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        for r in rows:
            vals = [str(r.get(h, "") or "") for h in headers]
            lines.append("| " + " | ".join(vals) + " |")
        lines.append("")
        return "\n".join(lines)
