from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from ..config import AppConfig
from ..io.paths import run_dir as run_dir_for
from ..io.manifest import read_manifest


UI_SCHEMA_VERSION = 1


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_ui_summary(cfg: AppConfig, *, run_id: str) -> dict[str, Any]:
    """Build a stable UI summary for a given run.

    This is intentionally lightweight:
    - Reads run manifest (if present)
    - Reads baseline metrics/report for login_attempt (if present)

    It does NOT read raw/dataset/features tables (keeps it fast + avoids parquet deps for UI generation).
    """
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    mpath = rdir / "manifest.json"
    manifest: dict[str, Any] = {}
    if mpath.exists():
        try:
            manifest = read_manifest(mpath)
        except Exception:
            # keep best-effort; UI should still render even if manifest is damaged
            manifest = {}

    out: dict[str, Any] = {
        "schema_version": UI_SCHEMA_VERSION,
        "generated_at_utc": _now_utc_iso(),
        "run_id": run_id,
        "timezone": manifest.get("timezone", getattr(cfg, "timezone", None)),
        "signature": {},
        "artifacts": {},
        "baselines": {},
        "eval": {},
        "notes": [],
    }


    # Run signature (helps compare runs without reading logs)
    out["signature"] = {
        "config_hash": manifest.get("config_hash"),
        "github_sha": (manifest.get("code") or {}).get("github_sha"),
        "seed": manifest.get("seed"),
        "schema_version": manifest.get("schema_version"),
    }
    # Baselines (login_attempt)
    metrics_path = rdir / "models" / "login_attempt" / "baselines" / "metrics.json"
    report_path = rdir / "models" / "login_attempt" / "baselines" / "report.md"
    user_report_path = rdir / "reports" / "baselines_login_attempt.md"
    log_path = rdir / "logs" / "baselines.log"
    if metrics_path.exists():
        try:
            metrics = _read_json(metrics_path)
            out["baselines"]["login_attempt"] = {
                "target_fpr": metrics.get("target_fpr"),
                "status": metrics.get("status"),
                "labels": metrics.get("labels", {}),
                "meta": metrics.get("meta", {}),
                "paths": {
                    "metrics_json": str(metrics_path),
                    "report_md": str(user_report_path) if user_report_path.exists() else (str(report_path) if report_path.exists() else None),
                    "baselines_log": str(log_path) if log_path.exists() else None,
                },
            }
            out["artifacts"]["baseline_report_md"] = str(user_report_path) if user_report_path.exists() else (str(report_path) if report_path.exists() else None)
            if metrics.get("status") == "partial":
                out["notes"].append("Baselines status is PARTIAL: one or more fits failed. See baselines log.")
        except Exception as e:
            out["notes"].append(f"Failed to read baselines metrics: {e}")
    else:
        out["notes"].append("Baselines metrics not found (run may be pre-baselines or baselines failed).")


    # Eval diagnostics (login_attempt) — derived from on-disk reports (no parquet read here)
    slices_md = rdir / "reports" / "eval_slices_login_attempt.md"
    stab_md = rdir / "reports" / "eval_stability_login_attempt.md"
    stab_json = rdir / "reports" / "eval_stability_login_attempt.json"
    if slices_md.exists() or stab_md.exists():
        out["eval"]["login_attempt"] = {
            "slices_report": str(slices_md) if slices_md.exists() else None,
            "stability_report": str(stab_md) if stab_md.exists() else None,
            "stability_summary": None,
        }
        if stab_json.exists():
            try:
                payload = _read_json(stab_json)
                # Build a compact table for the UI: label x model on primary split (user_holdout)
                table = []
                for model_name, mobj in (payload.get("models") or {}).items():
                    for label, lobj in (mobj.get("labels") or {}).items():
                        hold = (lobj.get("user_holdout") or {})
                        time = (lobj.get("time_eval") or {})
                        table.append({
                            "label": label,
                            "model": model_name,
                            "train_threshold": lobj.get("train_threshold"),
                            "holdout_pr_auc": hold.get("pr_auc"),
                            "holdout_recall": hold.get("recall_at_train_thr"),
                            "time_pr_auc": time.get("pr_auc"),
                            "time_recall": time.get("recall_at_train_thr"),
                            "delta_recall_hold_minus_time": (hold.get("recall_at_train_thr") or 0.0) - (time.get("recall_at_train_thr") or 0.0),
                        })
                out["eval"]["login_attempt"]["stability_summary"] = {
                    "primary_split": "user_holdout",
                    "rows": table,
                    "status": payload.get("status"),
                }
            except Exception as e:
                out["notes"].append(f"Failed to read eval stability JSON: {e}")

    # Summary report (optional)
    summary_path = rdir / "reports" / "summary.md"
    if summary_path.exists():
        out["artifacts"]["run_summary_md"] = str(summary_path)

    return out


def write_ui_summary(cfg: AppConfig, *, run_id: str, force: bool = False) -> Path:
    """Write runs/<run_id>/ui/ui_summary.json"""
    rdir = run_dir_for(cfg.paths.runs_dir, run_id)
    ui_dir = rdir / "ui"
    ui_dir.mkdir(parents=True, exist_ok=True)
    out_path = ui_dir / "ui_summary.json"
    if out_path.exists() and not force:
        return out_path

    payload = build_ui_summary(cfg, run_id=run_id)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path