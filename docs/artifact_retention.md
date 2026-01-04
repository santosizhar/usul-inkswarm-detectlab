# Artifact retention and cache hygiene

- Run outputs live under `runs/<RUN_ID>/` (manifests, reports, UI bundles).
- Shared feature cache lives under `runs/_cache/features/`.
- Suggested policy:
  - Keep smoke/MVP runs needed for evidence for 14 days.
  - Prune cache entries older than 30 days: `detectlab cache prune --older-than-days 30 --yes`.
  - Clean up ad-hoc runs after verification: `rm -rf runs/<RUN_ID>`.
- CI/automation: prefer `detectlab sanity --no-tiny-run` to avoid writing artifacts unless explicitly required.
