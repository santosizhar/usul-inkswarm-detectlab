# J-0014 — D-L001 — Lore Bible v1 + Docs Polish Sweep v1

Date: 2025-12-18  
NS: inkswarm-detectlab

## Goal
Deliver **Lore Bible v1** (optional narrative layer) and perform a **repo-wide markdown polish pass** so the documentation is:
- non-technical reader friendly,
- non-redundant,
- free of incomplete placeholders and broken fences,
- navigable (single canonical MVP guide).

Scope includes **all `.md` files**.

## What was done

### 1) Canonical user-facing documentation
- Added a single canonical guide for non-technical readers:
  - `docs/mvp_user_guide.md`
- Converted `docs/mvp_usage.md` into a short redirect to avoid broken links.
- Rebuilt `docs/index.md` as a navigation hub that points to the canonical guide first.

### 2) Cleaned and normalized core docs
Rewrote to remove incomplete blocks, reduce redundancy, and match current pipeline reality:
- `docs/getting_started.md`
- `docs/pipeline_overview.md`
- `docs/release_readiness_mvp.md`
- `docs/baselines.md`

### 3) Lore Bible v1 (separate from technical docs)
Expanded the lore area while keeping it optional and low-profile:
- `docs/lore/world_bible.md` (entry page + stable anchors)
- `docs/lore/lore_bible_v1.md`
- `docs/lore/glossary.md`
- `docs/lore/season_1.md`

### 4) Repo-wide markdown hygiene
- Removed stray unfinished placeholder fragments and fixed incomplete instructions where found.
- Fixed RR journal template completeness and linked it to the canonical MVP user guide:
  - `journals/inkswarm-detectlab__J-0012__RR-0001__mvp-release-readiness.md`

### 5) Automated docs lint in CI
Added a conservative docs lint step:
- Script: `scripts/lint_docs.py`
- CI: `.github/workflows/ci.yml` now runs docs lint before tests.

### 6) mkdocs navigation updated
- `mkdocs.yml` now includes the MVP User Guide and keeps Lore accessible under `Lore`.

## Acceptance criteria (met)
- Single canonical MVP guide exists and is linked from the docs index.
- Lore v1 exists with glossary mapping lore → technical components.
- Markdown files contain no standalone unfinished placeholder lines and code fences are balanced.
- Docs lint passes locally and runs in CI.

## Notes
Lore is deliberately “opt-in.” Stakeholders can ignore the Lore section and still follow the MVP guide end-to-end.
