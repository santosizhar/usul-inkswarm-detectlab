from types import SimpleNamespace
from pathlib import Path

from inkswarm_detectlab.ui import step_runner
from inkswarm_detectlab.ui.step_contract import ReuseDecision
from inkswarm_detectlab.ui.steps import StepRecorder


def _dummy_cfg(tmp_path: Path):
    return SimpleNamespace(
        paths=SimpleNamespace(runs_dir=str(tmp_path)),
        run=SimpleNamespace(schema_version="test", timezone="UTC", seed=1),
    )


def _reuse_decision(**kwargs):  # noqa: ANN003
    return ReuseDecision(mode="reuse", reason="test", used_manifest=False, forced=False)


def test_step_runner_reuse_path(tmp_path, monkeypatch):
    cfg = _dummy_cfg(tmp_path)
    run_dir = Path(tmp_path) / "RUN_TEST_0001"

    # Precreate expected artifacts so reuse branches are taken.
    for rel in [
        "raw/login_attempt.parquet",
        "raw/checkout_attempt.parquet",
        "dataset/login_attempt/train.parquet",
        "dataset/login_attempt/time_eval.parquet",
        "dataset/login_attempt/user_holdout.parquet",
        "features/login_attempt/features.parquet",
        "models/login_attempt/baselines/metrics.json",
        "models/login_attempt/baselines/model.joblib",
        "reports/eval_slices_login_attempt.json",
        "reports/eval_stability_login_attempt.json",
        "reports/eval_slices_login_attempt.md",
        "reports/eval_stability_login_attempt.md",
    ]:
        target = run_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}")

    monkeypatch.setattr(step_runner, "_config_fingerprint", lambda cfg: ("hash", "hash8"))
    monkeypatch.setattr(step_runner, "decide_reuse", _reuse_decision)

    rec = StepRecorder()

    ds = step_runner.step_dataset(cfg, run_id=run_dir.name, rec=rec)
    assert ds.status == "skipped"

    feats = step_runner.step_features(cfg, run_id=run_dir.name, rec=rec)
    assert feats.status == "skipped"

    baselines = step_runner.step_baselines(cfg, run_id=run_dir.name, rec=rec)
    assert baselines.status == "skipped"

    eval_result = step_runner.step_eval(cfg, run_id=run_dir.name, rec=rec)
    assert eval_result.status == "skipped"
