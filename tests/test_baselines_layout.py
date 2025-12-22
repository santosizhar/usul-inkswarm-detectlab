from __future__ import annotations

from pathlib import Path

import joblib

from inkswarm_detectlab.eval.runner import _discover_baseline_artifacts


def test_discover_baselines_supports_both_layouts(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "login_attempt"
    baselines = model_dir / "baselines"
    baselines.mkdir(parents=True, exist_ok=True)

    # Create dummy artifacts in BOTH layouts
    # v1 legacy
    joblib.dump({"m": 1}, baselines / "label_replicators__logreg.joblib")
    joblib.dump({"m": 2}, baselines / "label_replicators__rf.joblib")

    # v2 preferred
    (baselines / "logreg").mkdir()
    joblib.dump({"m": 3}, baselines / "logreg" / "label_the_mule.joblib")

    artifacts, notes = _discover_baseline_artifacts(model_dir=model_dir, expected_models=("logreg", "rf"))

    assert "logreg" in artifacts
    assert "rf" in artifacts

    assert "label_replicators" in artifacts["logreg"]
    assert "label_replicators" in artifacts["rf"]
    assert "label_the_mule" in artifacts["logreg"]

    # Should not produce "unrecognized filename" notes for the supported cases
    assert not any("Unrecognized artifact filename" in n for n in notes)
