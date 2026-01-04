# JM-0004 — D-0003 — Summary

FeatureLab (D-0003) adds a leakage-aware features table for `login_attempt` with safe rolling aggregates (user/ip/device × windows) and writes artifacts under `runs/<run_id>/features/` while updating the run manifest.
