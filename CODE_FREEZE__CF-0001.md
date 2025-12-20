# CODE FREEZE — CF-0001 — Inkswarm DetectLab (inkswarm-detectlab)

Date: 2025-12-17
Status: **Frozen snapshot for handoff / restart**

## What this Code Freeze is
This repository snapshot is intended to be a stable handoff point.
It includes deliverables through **D-0004** and the documentation/journals needed to restart work in a new chat.

## What is DONE
- **D-0001**: repo skeleton + docs structure + CI scaffold
- **D-0002**: SKYNET synthetic generator + dataset build (train/time_eval/user_holdout), manifests, summaries
- **CR-0001**: determinism tightening, canonicalization, improved CLI help + config show/validate, CI smoke run
- **D-0003**: FeatureLab v0 for `login_attempt` only
  - safe aggregate features for keys: `user_id`, `ip_hash`, `device_fingerprint_hash`
  - windows: `1h`, `6h`, `24h`, `7d`
- **D-0004**: BaselineLab v0 (sklearn baselines + reporting) — **validation deferred** via CC-0001

## What is NOT done
- Deferred Validation for D-0004 (must be run later on a local machine)
- Parquet-only enforcement (arrives later in D-0005)

## FeatureLab + BaselineLab (manual run)
```bash
# after you have a run_id
detectlab features build -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
detectlab baselines run -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
```

## Explicit Parquet conversion (legacy runs)
```bash
# convert legacy CSV artifacts to Parquet for a run (only needed for older runs)
detectlab dataset parquetify -c configs/skynet_smoke.yaml --run-id RUN_SAMPLE_SMOKE_0001
```
