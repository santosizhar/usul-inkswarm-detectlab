from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata, util, import_module
import platform
import sys
from typing import Iterable, List


@dataclass
class DiagnosticsSnapshot:
    lines: List[str]
    errors: List[str]


def _version_or_none(package: str) -> str | None:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return None
    except Exception:
        return None


def _format_version_line(label: str, version: str | None) -> str:
    suffix = version if version else "<unavailable>"
    return f"- {label}: {suffix}"


def _threadpool_lines(max_entries: int = 10) -> Iterable[str]:
    if util.find_spec("threadpoolctl") is None:
        yield "- threadpools: <unavailable>"
        return

    threadpoolctl = import_module("threadpoolctl")
    info = threadpoolctl.threadpool_info()
    yield f"- threadpools: {len(info)}"
    for i, row in enumerate(info[:max_entries]):
        lib = row.get("internal_api") or row.get("user_api") or "unknown"
        yield f"  - {i + 1}: {lib} ({row.get('num_threads')})"


def collect_diagnostics(include_threadpools: bool = True) -> DiagnosticsSnapshot:
    lines: List[str] = [
        "DetectLab doctor",
        f"- python: {sys.version.replace(chr(10), ' ')}",
        f"- platform: {platform.platform()}",
    ]
    errors: List[str] = []

    sklearn_version = _version_or_none("scikit-learn")
    pandas_version = _version_or_none("pandas")
    pyarrow_version = _version_or_none("pyarrow")

    lines.append(_format_version_line("sklearn", sklearn_version))
    lines.append(_format_version_line("pandas", pandas_version))
    lines.append(_format_version_line("pyarrow", pyarrow_version))

    if include_threadpools:
        lines.extend(_threadpool_lines())

    if pyarrow_version is None:
        errors.append("pyarrow is required for Parquet support but is not installed.")

    return DiagnosticsSnapshot(lines=lines, errors=errors)


def render_diagnostics(snapshot: DiagnosticsSnapshot, echo) -> None:
    for line in snapshot.lines:
        echo(line)
    if snapshot.errors:
        echo("")
        echo("Detected errors:")
        for err in snapshot.errors:
            echo(f"- {err}")
