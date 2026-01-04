"""Remove generated files from the repo working tree.

This is intended to be run before packaging a deliverable zip.
It deletes:
- __pycache__ directories
- *.pyc / *.pyo
- .ipynb_checkpoints
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def _rm_tree(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p, ignore_errors=True)


def _rm_file(p: Path) -> None:
    try:
        p.unlink()
    except FileNotFoundError:
        return


def clean(root: Path) -> int:
    removed = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # remove cache dirs
        for d in list(dirnames):
            if d == "__pycache__" or d == ".ipynb_checkpoints":
                _rm_tree(Path(dirpath) / d)
                removed += 1
                dirnames.remove(d)
        for f in filenames:
            if f.endswith((".pyc", ".pyo")):
                _rm_file(Path(dirpath) / f)
                removed += 1
    return removed


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    n = clean(repo_root)
    print(f"Removed {n} generated artifacts.")
