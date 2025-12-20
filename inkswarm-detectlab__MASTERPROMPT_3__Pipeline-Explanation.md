# MASTERPROMPT 3 — Pipeline Explanation — Inkswarm DetectLab

This document explains how MP1/MP2/MP4 work together, what “fail-closed” means, and how deliverables + ceremonies + journaling are enforced.

## How the masterprompts relate
- **MP1 (Prompt-Pack Generator)**: Used in Chat 1 only (planning-only). It forces a strict 0→4 step design process with gates.
- **MP2 (Steps Pack)**: Used in Chat 2 (execution). It is the operational ruleset: step gates, deliverables, ceremonies, journaling, naming, and locked project decisions.
- **MP4 (Project Kickoff Prompt)**: The only prompt you paste into Chat 2. It tells the assistant to read MP1/MP2/MP3, ask for Start-coding vs No-code mode, generate MP5, then execute using MP2’s step system.
- **MP5 (Unified Kickoff)**: Generated in Chat 2. It compiles the process rules + all locked project decisions into a single handover prompt for future restarts.

## What “fail-closed” means
Fail-closed = the assistant must not “guess and run ahead”.
- No skipping steps.
- No merging steps.
- No implementation without explicit OK gates.
- If inputs are missing, the assistant must stop at the correct gate and ask only the allowed questions.

## The step gate mechanics (0–4)
For each step:
1) Ask exactly 3 **Before Questions** (BQ1–BQ3) and stop.
2) Produce the step output with no questions inside.
3) Ask exactly 3 **After Questions** (AQ1–AQ3) and stop.
4) After answers, provide:
   - a concise summary (≤10 bullets)
   - the explicit OK question:
     “Do you OK Step N so we can move to Step N+1?”
Proceed only after explicit OK.

If the user requests a revision after AQs:
- revise without asking new questions
- re-ask the same OK question until approved.

## Deliverables and the ceremony cadence
Work is organized into deliverables:
- D-0001, D-0002, D-0003, …

Ceremony cadence:
- **Planning Ceremony (CP)** happens before every odd deliverable starting at D-0003 (before D-0003, D-0005, …).
- **Retro + Code Review (CR)** happens after every even deliverable (after D-0002, D-0004, …).
- **Change Control (CC)** happens whenever scope/architecture changes after being OK’d.
- **Release Readiness (RR)** happens before any release event.
- **Code Freeze (CF)** is mandatory after MVP release is published.

Ceremonies do not count as deliverables. Deliverables alone drive the “every 2 deliverables” cadence.

## Journaling (J + JM) is mandatory and immediate after OK
Every deliverable and every ceremony produces:
- a journal file `J-####`
- a companion handover masterprompt `JM-####`

Critical timing rule:
- **Ceremony → OK → immediately write the ceremony’s J + JM**.

No journals are generated upfront. Only generate them when the deliverable/ceremony occurs.

## Naming discipline
All generated files are prefixed with:
- `inkswarm-detectlab__`

J/JM numbering is strictly sequential across the whole project.

## Distribution defaults
- The repo is hosted on GitHub.
- Docs are produced with MkDocs in `docs/` and published via GitHub Pages.
- SemVer is used from day one; MVP release target is `0.1.0`.
- Data artifact storage choice is deferred until sizes are measured; keep the repo clean and fast.

## The project’s “world bible” rule
The project includes heavy fictional lore, but it must not pollute technical documentation:
- Lore lives in a standalone document: `docs/lore/world_bible.md`.
- Technical docs may reference lore by anchor links only (e.g., WB::REPLICATORS).

This preserves professional credibility while still delivering a strong narrative layer.
