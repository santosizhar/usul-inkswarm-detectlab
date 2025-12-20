from __future__ import annotations

import json
from pathlib import Path

import pytest

from inkswarm_detectlab.config import AppConfig
from inkswarm_detectlab.io.manifest import write_manifest
from inkswarm_detectlab.reports import generate_final_report_for_run


def test_generate_final_report_without_baselines(tmp_path: Path):
    # Arrange a minimal run directory with manifest + feature manifest.
    cfg = AppConfig()
    cfg.paths.runs_dir = tmp_path / "runs"

    run_id = "RUN_TEST_REPORT_0001"
    rdir = cfg.paths.runs_dir / run_id
    (rdir / "features" / "login_attempt").mkdir(parents=True, exist_ok=True)

    write_manifest(
        rdir,
        {
            "schema_version": "v1",
            "artifacts": {
                "login_attempt_raw": {"path": "raw/login_attempt.parquet"},
                "login_attempt_dataset": {"path": "dataset/login_attempt/events.parquet"},
            },
        },
    )

    fman = {
        "rows": 123,
        "cols": 45,
        "params": {"windows": ["1h", "6h", "24h", "7d"], "groups": ["user", "ip", "device"], "strict_past_only": True},
    }
    (rdir / "features" / "login_attempt" / "feature_manifest.json").write_text(json.dumps(fman), encoding="utf-8")

    # Act
    out = generate_final_report_for_run(cfg, run_id, force=True)

    # Assert
    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert "Final Report (D-0006)" in txt
    assert f"run_id: `{run_id}`" in txt
    assert "FeatureLab v0 summary" in txt
    assert "Baselines were not found" in txt
