from __future__ import annotations

import json
from pathlib import Path

from inkswarm_detectlab.config import load_config
from inkswarm_detectlab.ui.bundle import export_ui_bundle


def _write_dummy_metrics(run_dir: Path) -> None:
    out = run_dir / "models" / "login_attempt" / "baselines"
    out.mkdir(parents=True, exist_ok=True)
    metrics = {
        "run_id": run_dir.name,
        "target_fpr": 0.01,
        "labels": {
            "is_fraud": {
                "logreg": {
                    "status": "ok",
                    "train": {"pr_auc": 0.5, "threshold_for_fpr": 0.9, "fpr": 0.01, "recall": 0.1, "precision": 0.2},
                    "time_eval": {"pr_auc": 0.4, "roc_auc": 0.6, "threshold_used": 0.9, "fpr": 0.01, "recall": 0.08, "precision": 0.18},
                    "user_holdout": {"pr_auc": 0.35, "roc_auc": 0.58, "threshold_used": 0.9, "fpr": 0.01, "recall": 0.07, "precision": 0.17},
                },
                "rf": {
                    "status": "ok",
                    "train": {"pr_auc": 0.55, "threshold_for_fpr": 0.8, "fpr": 0.01, "recall": 0.12, "precision": 0.22},
                    "time_eval": {"pr_auc": 0.45, "roc_auc": 0.62, "threshold_used": 0.8, "fpr": 0.01, "recall": 0.09, "precision": 0.19},
                    "user_holdout": {"pr_auc": 0.38, "roc_auc": 0.6, "threshold_used": 0.8, "fpr": 0.01, "recall": 0.08, "precision": 0.18},
                },
            }
        },
        "meta": {"env": {"python": "3.12.0", "platform": "Windows"}},
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


def test_export_ui_bundle(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()

    r1 = runs_dir / "RUN_A"
    r2 = runs_dir / "RUN_B"
    r1.mkdir()
    r2.mkdir()
    _write_dummy_metrics(r1)
    _write_dummy_metrics(r2)

    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text("paths:\n  runs_dir: runs\n", encoding="utf-8")
    cfg = load_config(cfg_path)

    out_dir = tmp_path / "ui_bundle"
    export_ui_bundle(cfg, run_ids=["RUN_A", "RUN_B"], out_dir=out_dir, force=True)

    assert (out_dir / "index.html").exists()
    html = (out_dir / "index.html").read_text(encoding="utf-8")
    assert "MVP Results Viewer" in html
    js = (out_dir / "app.js").read_text(encoding="utf-8")
    assert "RUN_A" in js and "RUN_B" in js


def test_export_ui_bundle_max5(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    for i in range(6):
        r = runs_dir / f"R{i}"
        r.mkdir()
        _write_dummy_metrics(r)

    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text("paths:\n  runs_dir: runs\n", encoding="utf-8")
    cfg = load_config(cfg_path)

    try:
        export_ui_bundle(cfg, run_ids=[f"R{i}" for i in range(6)], out_dir=tmp_path / "out", force=True)
        assert False, "Expected ValueError for >5 runs"
    except ValueError:
        assert True
