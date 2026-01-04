# D-0024.12 — RR Patch: Fix __future__ import placement

Fixes SyntaxError in `src/inkswarm_detectlab/ui/step_runner.py`:
`from __future__ import annotations` must appear at the top of the file (after docstring/comments).

Apply: unzip over repo, restart kernel.
