# Synthetic dataset and label semantics (MVP)

This project currently ships with a **synthetic dataset generator** ("Skynet")
to let us iterate on pipeline plumbing, evaluation, and reporting before we plug
in real production data.

## Are labels random?

**They are pseudo-random but not arbitrary.**

- The generator uses a seeded RNG to create user/session attributes, campaigns,
  and event patterns.
- Each label is then assigned using rules that *depend on those generated
  attributes*.
- With the same config + seed, the generator is **deterministic** (you should
  get the same dataset again).

So, labels are **synthetic scenarios** that are *correlated with the features*
we generate — they are not "real-world truth", but they are also not pure noise.

## Current label meanings

See `src/inkswarm_detectlab/synthetic/label_defs.py` for the single source of
truth used by reports + notebooks.

High-level intent:

- `label_replicators`: repeated / automated patterns that resemble bot-like
  replication.
- `label_the_mule`: patterns that resemble an account used as a "carrier" (e.g.,
  weird velocity / campaign drift).
- `label_the_chameleon`: patterns that resemble adaptive behavior and shifting
  fingerprints.

## Where to look in code

- Dataset generation: `src/inkswarm_detectlab/synthetic/skynet.py`
- Label definitions (human-readable): `src/inkswarm_detectlab/synthetic/label_defs.py`

## Reporting expectations

Baseline reports intentionally include:

- the **label definitions** section
- the **training preset** (standard vs fast) + effective hyperparameters

This helps keep results shareable and prevents "mystery labels" in screenshots
and stakeholder writeups.

## What changes in D-0022

D-0022 is planned to make dataset scenarios *more policy-relevant*:

- clearer story for each label (what is the attacker doing?)
- knobs for scenario prevalence and difficulty
- explicit mapping between scenario knobs and feature expectations