#!/usr/bin/env python3
"""
Lightweight docs lint.

Goals:
- Keep markdown readable and "finished" (no stray '...' placeholder lines).
- Catch obviously broken relative links.
- Keep files reasonably short (soft check; split if very long).

This is intentionally conservative: it flags only high-confidence issues.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MD_GLOBS = [
    "README.md",
    "*.md",
    "docs/**/*.md",
    "journals/**/*.md",
]

# High-confidence "unfinished" patterns
ELLIPSIS_LINE = re.compile(r"^\s*\.\.\.\s*$")
BROKEN_CODE_FENCE = re.compile(r"^```")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

MAX_LINES_SOFT = 250


def iter_md_files() -> list[Path]:
    out: list[Path] = []
    for g in MD_GLOBS:
        out.extend(REPO_ROOT.glob(g))
    # de-dup while keeping stable ordering
    seen = set()
    uniq = []
    for p in sorted(set(out)):
        if p.is_file() and p.suffix.lower() == ".md":
            rp = p.resolve()
            if rp not in seen:
                uniq.append(p)
                seen.add(rp)
    return uniq


def strip_anchor(path: str) -> str:
    return path.split("#", 1)[0]


def is_external(href: str) -> bool:
    return href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:")


def is_anchor_only(href: str) -> bool:
    return href.startswith("#")


def check_links(md_path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for m in LINK_RE.finditer(text):
        href = m.group(2).strip()
        if not href:
            continue
        if is_external(href) or is_anchor_only(href):
            continue

        href_no_anchor = strip_anchor(href)

        # ignore mkdocs-style page links like "getting_started.md"
        # Resolve relative to the file location.
        target = (md_path.parent / href_no_anchor).resolve()

        # If link points outside repo, treat as error.
        try:
            target.relative_to(REPO_ROOT.resolve())
        except Exception:
            errors.append(f"link points outside repo: {href}")
            continue

        if href_no_anchor.endswith("/"):
            # allow directory links if directory exists
            if not target.exists():
                errors.append(f"broken link: {href}")
            continue

        # Accept links without extension that refer to mkdocs pages? (rare)
        if not target.exists():
            # try adding .md
            if target.suffix == "" and (target.with_suffix(".md")).exists():
                continue
            errors.append(f"broken link: {href}")
    return errors


def main() -> int:
    md_files = iter_md_files()
    failures: list[str] = []

    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()

        # Flag standalone '...' lines
        for i, line in enumerate(lines, start=1):
            if ELLIPSIS_LINE.match(line):
                failures.append(f"{p.relative_to(REPO_ROOT)}:{i}: standalone '...' placeholder line")

        # Soft length check (warning only)
        if len(lines) > MAX_LINES_SOFT:
            failures.append(f"{p.relative_to(REPO_ROOT)}: file is {len(lines)} lines (> {MAX_LINES_SOFT}); consider splitting")

        # Link checks
        for err in check_links(p, text):
            failures.append(f"{p.relative_to(REPO_ROOT)}: {err}")

        # Balanced code fences check (high confidence)
        fence_count = sum(1 for l in lines if l.strip().startswith("```"))
        if fence_count % 2 != 0:
            failures.append(f"{p.relative_to(REPO_ROOT)}: unbalanced code fences (``` count is odd)")

    if failures:
        print("DOCS LINT FAILED:")
        for f in failures:
            print(" -", f)
        return 1

    print("DOCS LINT PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
