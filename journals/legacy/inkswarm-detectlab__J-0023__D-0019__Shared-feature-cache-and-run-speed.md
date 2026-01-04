# Inkswarm DetectLab — J-0023 — D-0019
**Title:** Shared feature cache + faster iterative MVP runs  
**Date:** 2025-12-21

## Context
MVP runs can take a long time (or crash) when we repeatedly rebuild the same:
- `raw/` extraction
- `dataset/` splits
- `features/` parquet artifacts

A common workflow is: run → inspect → tweak modeling/eval → run again.  
Rebuilding the same data+features each time is wasteful and increases failure risk.

## What changed
### 1) Shared cache directory
A new config path was added:
- `paths.cache_dir` (default: `runs/_cache`)

This directory is intended for **cross-run reuse** of deterministic artifacts.

### 2) Cross-run restore/write for dataset+features (+raw optional)
New module:
- `src/inkswarm_detectlab/cache/feature_cache.py`

It:
- Computes a stable cache key from the config (excluding run-id variability)
- Restores `dataset/` + `features/` (and `raw/` if present) into a new run folder if a matching cache exists
- Writes a fresh cache entry after successful feature generation (best-effort; never blocks a run)

### 3) Orchestrator integration
`run_mvp()` now:
- Generates a `run_id` early if one is not provided (so cache restore can happen *before* heavy steps)
- Attempts a cache restore **before** running `run_all()` / feature generation
- Writes cache after `features(login)` finishes (unless a cache hit)

## How to use
- Default behavior is ON:
  - `features.use_cache: true`
  - `features.write_cache: true`
- To disable cache temporarily (for debugging):
  - set `features.use_cache: false` in your YAML
- Cache is best-effort and safe:
  - If a cache entry is missing or incomplete → it is ignored (fail-closed)
  - If cache write fails → the run still completes

## Notes
- Cache entries are keyed to config content, not run_id.
- If you change feature definitions / splits / windows, the cache key changes automatically.

