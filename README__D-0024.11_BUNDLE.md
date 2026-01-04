# D-0024.11 — RR Patch: Pre-flight self-heal imports

Fixes NameError issues when users run cells out-of-order (e.g., step cells without running imports).

Adds:
- A PRE-FLIGHT cell after the toggles cell that imports required symbols and initializes cfg/run_id.
- A one-line import guard in the Step 1 dataset cell for extra resilience.

Apply: unzip over repo, restart kernel, run notebook top-down.
