# D-0015 — UI bundle polish v2 (bundle)

This bundle contains:
- `src/inkswarm_detectlab/ui/bundle.py` (UPDATED)
- `patches/D-0015__ui_bundle_polish_v2.patch` (unified diff vs CF-0003 snapshot)

## How to apply

### Option A — Copy file (fastest)
Copy the included file into your repo, overwriting:
- `src/inkswarm_detectlab/ui/bundle.py`

### Option B — Apply patch (git)
From repo root:
```bash
git apply patches/D-0015__ui_bundle_polish_v2.patch
```

## What changed (high-level)
- More explicit truth-split messaging (user_holdout primary, time_eval drift).
- "Go to run" dropdown that scrolls to the selected run.
- Signature pills fail-soft:
  - Code hash missing => "Code: (no git)"
  - Config hash missing => "Config: —"
- Run sections now have anchors for direct navigation.
