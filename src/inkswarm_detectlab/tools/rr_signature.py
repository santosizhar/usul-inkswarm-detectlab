# ruff: noqa
"""RR-0001 determinism signature.

This tool writes a diff-friendly JSON signature intended to be identical across
multiple runs executed with the same config + seed, even if the **run_id** differs.

Key behavior
- Normalizes run_id-sensitive values by setting `run_id` in the signature to a
  constant placeholder, and by recomputing hashes from key parquet artifacts
  after dropping the `run_id` column.
- Parses BaselineLab metrics from the current metrics.json structure.

Fail-closed
- Missing required artifacts -> raises and exits non-zero.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import typer

from ..io.manifest import read_manifest
from ..io.paths import manifest_path
from ..io.paths import run_dir as run_dir_for
from ..schemas import get_schema
from ..utils.canonical import canonicalize_df
from ..utils.hashing import stable_hash_df, stable_hash_dict
from ..utils.safe_io import read_json_strict

app = typer.Typer(add_completion=False, help="Write a normalized RR determinism signature JSON.")


def _must_exist(p: Path, label: str) -> Path:
    if not p.exists():
        raise FileNotFoundError(f"Missing required {label}: {p}")
    return p


def _norm_parquet_hash(
    *,
    parquet_path: Path,
    sort_keys: list[str],
    drop_cols: list[str] | None = None,
    schema_name: str | None = None,
) -> str:
    """Hash parquet contents after optional schema canonicalization.

    - Drops `drop_cols` if present.
    - If `schema_name` is known, canonicalizes via repo schema (types + columns).
    - If `schema_name` is unknown (e.g. features tables), falls back to a generic
      stable sort + stable column order.
    """
    df = pd.read_parquet(parquet_path)

    drop_cols = drop_cols or []
    for c in drop_cols:
        if c in df.columns:
            df = df.drop(columns=[c])

    keys = [k for k in sort_keys if k in df.columns]

    schema = None
    if schema_name is not None:
        try:
            schema = get_schema(schema_name)
        except KeyError:
            schema = None

    if schema is not None:
        df = canonicalize_df(df, sort_keys=sort_keys, schema=schema)
        col_order = list(df.columns)
    else:
        if keys:
            df = df.sort_values(keys, kind="mergesort").reset_index(drop=True)
        col_order = sorted(df.columns)
        df = df[col_order]

    return stable_hash_df(df, sort_keys=keys, column_order=col_order)


def _features_numeric_summary(features_path: Path) -> dict[str, Any]:
    """Small, stable numeric summary for features parquet (digest only)."""
    df = pd.read_parquet(features_path)

    # Drop obvious identifier columns if present.
    drop = [
        "run_id",
        "event_id",
        "event_ts",
        "user_id",
        "ip_hash",
        "device_fingerprint_hash",
        "session_id",
        "metadata_json",
        "country",
    ]
    for c in drop:
        if c in df.columns:
            df = df.drop(columns=[c])

    num = df.select_dtypes(include=["number", "bool"]).copy()
    if num.empty:
        return {"n_rows": int(len(df)), "n_numeric_cols": 0, "digest": stable_hash_dict({})}

    # booleans -> int for stable aggregation
    for c in num.columns:
        if str(num[c].dtype) == "bool":
            num[c] = num[c].astype(int)

    means = {c: float(round(num[c].mean(), 12)) for c in num.columns}
    stds = {c: float(round(num[c].std(ddof=0), 12)) for c in num.columns}

    return {
        "n_rows": int(len(num)),
        "n_numeric_cols": int(num.shape[1]),
        "digest": stable_hash_dict({"means": means, "stds": stds}),
    }


def _parse_baselines_metrics(metrics_path: Path) -> dict[str, Any]:
    """Parse BaselineLab metrics.json into a stable, comparable structure."""
    data = read_json_strict(metrics_path)

    out: dict[str, Any] = {}

    # Current schema: {"labels": {<label>: {<model>: {"status":..., "time_eval":..., ...}}}}
    labels = data.get("labels")
    if isinstance(labels, dict):
        for label, models in labels.items():
            if not isinstance(models, dict):
                continue
            out[label] = {}
            for model_name, payload in models.items():
                if not isinstance(payload, dict):
                    continue

                model_out: dict[str, Any] = {"status": payload.get("status")}
                for split in ("train", "user_holdout", "time_eval"):
                    v = payload.get(split)
                    if isinstance(v, dict):
                        model_out[split] = {
                            k: float(v[k])
                            for k in ("roc_auc", "pr_auc", "precision", "recall", "fpr")
                            if k in v and isinstance(v[k], (int, float))
                        }
                        if "threshold_used" in v and isinstance(v["threshold_used"], (int, float)):
                            model_out[split]["threshold_used"] = float(v["threshold_used"])

                out[label][model_name] = model_out

        # Label-level digest for quick compare
        for label in list(out.keys()):
            out[label]["_digest"] = stable_hash_dict(out[label])

    return out


def build_signature(*, repo_root: Path, run_id: str) -> dict[str, Any]:
    runs_dir = repo_root / "runs"
    run_dir = run_dir_for(runs_dir, run_id)

    mpath = _must_exist(manifest_path(run_dir), "manifest.json")
    manifest = read_manifest(mpath)

    # Sort keys used across the repo.
    sort_keys = ["event_ts", "user_id", "event_id"]

    # Required artifacts
    raw_login = _must_exist(run_dir / "raw" / "login_attempt.parquet", "raw login_attempt")
    raw_checkout = _must_exist(run_dir / "raw" / "checkout_attempt.parquet", "raw checkout_attempt")
    features_login = _must_exist(run_dir / "features" / "login_attempt" / "features.parquet", "features login_attempt")
    metrics_login = _must_exist(run_dir / "models" / "login_attempt" / "baselines" / "metrics.json", "baselines metrics")

    hashes = {
        "raw_login_attempt": _norm_parquet_hash(
            parquet_path=raw_login,
            schema_name="login_attempt",
            sort_keys=sort_keys,
            drop_cols=["run_id"],
        ),
        "raw_checkout_attempt": _norm_parquet_hash(
            parquet_path=raw_checkout,
            schema_name="checkout_attempt",
            sort_keys=sort_keys,
            drop_cols=["run_id"],
        ),
        "features_login_attempt": _norm_parquet_hash(
            parquet_path=features_login,
            schema_name=None,
            sort_keys=sort_keys,
            drop_cols=[],
        ),
    }

    features_summary = _features_numeric_summary(features_login)
    baselines = _parse_baselines_metrics(metrics_login)

    signature = {
        "run_id": "<NORMALIZED>",
        "actual_run_id": "<NORMALIZED>",
        "schema_version": manifest.get("schema_version"),
        "timezone": manifest.get("timezone"),
        "seed": manifest.get("seed"),
        "config_hash": manifest.get("config_hash"),
        "code": manifest.get("code", {}),
        "hashes": hashes,
        "hashes_digest": stable_hash_dict(hashes),
        "features_digest": features_summary.get("digest"),
        "baselines": baselines,
        "baselines_digest": stable_hash_dict(baselines),
        "signature_digest": stable_hash_dict(
            {
                "schema_version": manifest.get("schema_version"),
                "timezone": manifest.get("timezone"),
                "seed": manifest.get("seed"),
                "config_hash": manifest.get("config_hash"),
                "hashes_digest": stable_hash_dict(hashes),
                "features_digest": features_summary.get("digest"),
                "baselines_digest": stable_hash_dict(baselines),
            }
        ),
    }

    return signature


@app.command()
def main(
    run_id: str = typer.Option(..., "--run-id", help="Run id under runs/<run_id>"),
    out: Path = typer.Option(..., "--out", help="Output JSON path"),
) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    sig = build_signature(repo_root=repo_root, run_id=run_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sig, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    typer.echo(json.dumps(sig, indent=2, sort_keys=True))


if __name__ == "__main__":
    app()
