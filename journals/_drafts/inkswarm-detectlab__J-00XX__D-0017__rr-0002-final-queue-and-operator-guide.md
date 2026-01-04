# inkswarm-detectlab__J-00XX__D-0017__rr-0002-final-queue-and-operator-guide.md

# J-00XX — D-0017 — RR-0002 Final Queue + Operator Guide

**Date:** 2025-12-19  
**Scope:** Consolidate RR into a single fail-closed procedure that includes the final manual confirmation and interpretation guidance.

## Delivered
- `docs/release_readiness/RR-0002__Final-Queue_and_Operator-Guide.md`
- `docs/release_readiness/RR-0002__recording_template.md`

## Locked decisions (from BQ/AQ)
- RR covers both modes and records them separately:
  - Git checkout mode (code SHA expected)
  - Unpacked zip mode (no `.git`; UI shows “(no git)”)
- RR runs two configs:
  - MVP: `configs/skynet_mvp.yaml`
  - Smoke: `configs/skynet_smoke.yaml`
- HARD PASS determinism requires:
  - signature match (config_hash + code_sha where applicable)
  - headline metrics identical where present
- Evidence location:
  - `docs/rr_evidence/RR-0002/YYYYMMDD/`
- Manual confirmation is the final RR step (no separate MT ritual).

## Notes
- Bundle includes sandbox RR-0001 evidence as a **format reference only** (not Windows certification).

## Outcome
**D-0017 COMPLETE.**
