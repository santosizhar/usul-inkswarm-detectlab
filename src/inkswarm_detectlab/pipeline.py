from __future__ import annotations

# Executive summary markers (used by reports.exec_summary to inject stakeholder blurb)
EXEC_SUMMARY_START = "<!-- EXEC_SUMMARY:START -->"
EXEC_SUMMARY_END = "<!-- EXEC_SUMMARY:END -->"


from dataclasses import dataclass
from pathlib import Path
from typing import Any

import os

import numpy as np
import pandas as pd

from .config import AppConfig
from .dataset import build_splits
from .io.paths import (
    run_dir as run_dir_for,
    raw_table_basepath,
    dataset_split_basepath,
    manifest_path,
    summary_path,
    reports_dir,
    raw_dir,
)
from .io.tables import read_auto, write_auto
from .io.manifest import write_manifest, read_manifest
from .synthetic import generate_skynet
from .utils.hashing import stable_hash_dict, stable_hash_df
from .utils.run_id import make_run_id
from .utils.canonical import canonicalize_df
from .schemas import get_schema


@dataclass(frozen=True)
class ArtifactMeta:
    name: str
    path: str
    format: str
    rows: int
    content_hash: str
    note: str | None = None


def _config_fingerprint(cfg: AppConfig) -> tuple[str, str]:
    d = cfg.model_dump()
    # exclude run_id (may be None or pinned for fixtures)
    if isinstance(d.get("run"), dict):
        d["run"].pop("run_id", None)
    h = stable_hash_dict(d)
    return h, h[:8]


def _write_summary(
    run_dir: Path,
    manifest: dict[str, Any],
    login_df: pd.DataFrame,
    checkout_df: pd.DataFrame,
    split_boundary: pd.Timestamp,
    holdout_users: set[str],
) -> None:
    reports_dir(run_dir).mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Inkswarm DetectLab — Run Summary")
    lines.append("")
    lines.append("## Identity")
    lines.append(f"- run_id: `{run_dir.name}`")
    lines.append(f"- timezone: `America/Argentina/Buenos_Aires`")
    lines.append(f"- schema_version: `{manifest.get('schema_version')}`")
    lines.append("")

    lines.append("## Raw tables")
    lines.append(f"- login_attempt rows: {len(login_df):,}")
    lines.append(f"- checkout_attempt rows: {len(checkout_df):,}")
    lines.append("")

    if not login_df.empty and "label_benign" in login_df.columns:
        attack_any = ~login_df["label_benign"].astype(bool)
        attack_rate = float(attack_any.mean()) if len(login_df) else 0.0
        lines.append("## Labels (login_attempt)")
        lines.append(f"- overall attack prevalence (any label): {attack_rate:.4f}")
        for col in ["label_replicators", "label_the_mule", "label_the_chameleon"]:
            if col in login_df.columns:
                lines.append(f"- {col}: {float(login_df[col].mean()):.4f}")
        if all(c in login_df.columns for c in ["label_replicators", "label_the_mule", "label_the_chameleon"]):
            r = login_df["label_replicators"].astype(bool)
            m = login_df["label_the_mule"].astype(bool)
            c = login_df["label_the_chameleon"].astype(bool)
            lines.append("")
            lines.append("### Overlaps")
            lines.append(f"- REPLICATORS & THE_MULE: {int((r & m).sum()):,}")
            lines.append(f"- REPLICATORS & THE_CHAMELEON: {int((r & c).sum()):,}")
            lines.append(f"- THE_MULE & THE_CHAMELEON: {int((m & c).sum()):,}")
            lines.append(f"- triple overlap: {int((r & m & c).sum()):,}")
        lines.append("")

    if not checkout_df.empty and "checkout_result" in checkout_df.columns:
        adverse = (checkout_df["checkout_result"] != "success")
        lines.append("## Checkout (checkout_attempt)")
        lines.append(f"- adverse rate (failure or review): {float(adverse.mean()):.4f}")
        lines.append("")

    lines.append("## Dataset splits")
    lines.append(f"- time boundary (America/Argentina/Buenos_Aires): {split_boundary.isoformat()}")
    total_users = int(pd.Series(login_df["user_id"]).astype(str).nunique()) if (not login_df.empty and "user_id" in login_df.columns) else 0
    holdout_pct = (len(holdout_users) / total_users) if total_users else 0.0
    lines.append(f"- holdout users: {len(holdout_users):,} ({holdout_pct:.1%} of {total_users:,} unique users)")
    lines.append("")

    # Outputs written / formats
    artifacts: dict[str, Any] = manifest.get("artifacts", {}) or {}
    if artifacts:
        lines.append("## Outputs written")
        for key in sorted(artifacts.keys()):
            a = artifacts[key]
            path = a.get("path")
            fmt = a.get("format")
            rows = a.get("rows")
            note = a.get("note")
            suffix = f" — {rows:,} rows" if isinstance(rows, int) else ""
            if note:
                lines.append(f"- {key}: `{path}` ({fmt}; {note}){suffix}")
            else:
                lines.append(f"- {key}: `{path}` ({fmt}){suffix}")
        lines.append("")

    summary_path(run_dir).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _artifact_entry(
    *,
    cfg: AppConfig,
    df: pd.DataFrame,
    rel_path: Path,
    fmt: str,
    note: str | None,
    schema_name: str,
) -> dict[str, Any]:
    schema = get_schema(schema_name)
    # Hash exactly what we write: canonical ordering + stable columns
    canonical = canonicalize_df(df, sort_keys=cfg.dataset.build.canonical_sort_keys, schema=schema)
    return {
        "path": str(rel_path),
        "format": fmt,
        "note": note,
        "rows": int(len(canonical)),
        "content_hash": stable_hash_df(
            canonical,
            sort_keys=cfg.dataset.build.canonical_sort_keys,
            column_order=list(canonical.columns),
        ),
    }


def generate_raw(cfg: AppConfig, run_id: str | None = None) -> tuple[Path, dict[str, Any]]:
    """Generate raw SKYNET tables and write a partial manifest."""
    cfg_hash, cfg_hash8 = _config_fingerprint(cfg)
    rid = run_id or cfg.run.run_id or make_run_id(cfg_hash8)
    rdir = run_dir_for(cfg.paths.runs_dir, rid)
    raw_dir(rdir).mkdir(parents=True, exist_ok=True)

    login_df, checkout_df, meta = generate_skynet(cfg, run_id=rid)

    # Canonicalize before write (tight determinism).
    login_df = canonicalize_df(login_df, sort_keys=cfg.dataset.build.canonical_sort_keys, schema=get_schema("login_attempt"))
    checkout_df = canonicalize_df(checkout_df, sort_keys=cfg.dataset.build.canonical_sort_keys, schema=get_schema("checkout_attempt"))

    artifacts: dict[str, Any] = {}

    lp, lfmt, lnote = write_auto(login_df, raw_table_basepath(rdir, "login_attempt"))
    cp, cfmt, cnote = write_auto(checkout_df, raw_table_basepath(rdir, "checkout_attempt"))

    artifacts["raw/login_attempt"] = _artifact_entry(
        cfg=cfg,
        df=login_df,
        rel_path=lp.relative_to(cfg.paths.runs_dir),
        fmt=lfmt,
        note=lnote,
        schema_name="login_attempt",
    )
    artifacts["raw/checkout_attempt"] = _artifact_entry(
        cfg=cfg,
        df=checkout_df,
        rel_path=cp.relative_to(cfg.paths.runs_dir),
        fmt=cfmt,
        note=cnote,
        schema_name="checkout_attempt",
    )

    manifest: dict[str, Any] = {
        "run_id": rid,
        "schema_version": cfg.run.schema_version,
        "timezone": cfg.run.timezone,
        "seed": cfg.run.seed,
        "config_hash": cfg_hash,
        "artifacts": artifacts,
        "generator_meta": meta,
        "code": {"github_sha": os.environ.get("GITHUB_SHA")},
    }
    write_manifest(manifest_path(rdir), manifest)
    return rdir, manifest


def build_dataset(cfg: AppConfig, run_id: str) -> tuple[Path, dict[str, Any]]:
    """Build datasets for an existing run_id and update manifest + summary."""
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    mpath = manifest_path(rdir)
    manifest = read_manifest(mpath) if mpath.exists() else {
        "run_id": run_id,
        "schema_version": cfg.run.schema_version,
        "timezone": cfg.run.timezone,
        "seed": cfg.run.seed,
        "config_hash": _config_fingerprint(cfg)[0],
        "artifacts": {},
    }

    login_df = read_auto(raw_table_basepath(rdir, "login_attempt"))
    checkout_df = read_auto(raw_table_basepath(rdir, "checkout_attempt"))

    # Canonicalize raw tables for determinism.
    login_df = canonicalize_df(login_df, sort_keys=cfg.dataset.build.canonical_sort_keys, schema=get_schema("login_attempt"))
    checkout_df = canonicalize_df(checkout_df, sort_keys=cfg.dataset.build.canonical_sort_keys, schema=get_schema("checkout_attempt"))

    rng = np.random.default_rng(cfg.run.seed + 12345)
    split_cfg = cfg.dataset.build

    splits_login = build_splits(login_df, split_cfg, rng)
    splits_checkout = build_splits(checkout_df, split_cfg, rng)

    artifacts = manifest.get("artifacts", {}) or {}

    def _write_split(event: str, split_name: str, sdf: pd.DataFrame):
        schema = get_schema(event)
        sdf2 = canonicalize_df(sdf, sort_keys=split_cfg.canonical_sort_keys, schema=schema)
        p, fmt, note = write_auto(sdf2, dataset_split_basepath(rdir, event, split_name))
        artifacts[f"dataset/{event}/{split_name}"] = _artifact_entry(
            cfg=cfg,
            df=sdf2,
            rel_path=p.relative_to(cfg.paths.runs_dir),
            fmt=fmt,
            note=note,
            schema_name=event,
        )

    for split_name, sdf in [("train", splits_login.train), ("time_eval", splits_login.time_eval), ("user_holdout", splits_login.user_holdout)]:
        _write_split("login_attempt", split_name, sdf)
    for split_name, sdf in [("train", splits_checkout.train), ("time_eval", splits_checkout.time_eval), ("user_holdout", splits_checkout.user_holdout)]:
        _write_split("checkout_attempt", split_name, sdf)

    manifest["artifacts"] = artifacts
    manifest["dataset"] = {
        "time_split": split_cfg.time_split,
        "user_holdout": split_cfg.user_holdout,
        "canonical_sort_keys": split_cfg.canonical_sort_keys,
        "login_attempt": {
            "boundary_ts_ba": splits_login.boundary_ts.isoformat(),
            "holdout_users": len(splits_login.holdout_users),
        },
        "checkout_attempt": {
            "boundary_ts_ba": splits_checkout.boundary_ts.isoformat(),
            "holdout_users": len(splits_checkout.holdout_users),
        },
    }

    write_manifest(mpath, manifest)
    _write_summary(rdir, manifest, login_df, checkout_df, splits_login.boundary_ts, splits_login.holdout_users)

    return rdir, manifest


def run_all(cfg: AppConfig, run_id: str | None = None) -> tuple[Path, dict[str, Any]]:
    rdir, _ = generate_raw(cfg, run_id=run_id)
    return build_dataset(cfg, run_id=rdir.name)


def _ensure_exec_markers(summary_text: str) -> str:
    """Ensure summary.md contains EXEC_SUMMARY markers at the top (stable injection point)."""
    if EXEC_SUMMARY_START in summary_text and EXEC_SUMMARY_END in summary_text:
        return summary_text
    header = "\n".join([EXEC_SUMMARY_START, EXEC_SUMMARY_END, ""])
    return header + summary_text
