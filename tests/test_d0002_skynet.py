from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip('pyarrow')

from inkswarm_detectlab.config import load_config
from inkswarm_detectlab.pipeline import run_all
from inkswarm_detectlab.io.paths import manifest_path
from inkswarm_detectlab.io.manifest import read_manifest


def _to_dt(series: pd.Series) -> pd.Series:
    # Accept either datetime64[ns, tz] or string.
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    # Keep timezone info if present in strings (we care about BA hour-of-day patterns).
    return pd.to_datetime(series, errors="raise")


def _read_path(path: Path) -> pd.DataFrame:
    """Read a table from an explicit path (.parquet or .csv)."""
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path, low_memory=False)
    raise ValueError(f"Unsupported table suffix: {path}")


def _tiny_cfg(tmp_path: Path):
    """Return a fast config for unit tests (does not change shipped configs)."""
    cfg = load_config(Path("configs/skynet_smoke.yaml")).model_copy(deep=True)

    # Write into tmp instead of repo runs/.
    cfg.paths.runs_dir = tmp_path / "runs"
    # Do not pin run_id for tests.
    cfg.run.run_id = None

    # Keep runtime small but statistically stable.
    cfg.synthetic.skynet.days = 3
    cfg.synthetic.skynet.n_users = 80
    cfg.synthetic.skynet.login_events_per_day = 500
    cfg.synthetic.skynet.checkout_events_per_day = 250

    # Ensure we always get an actual spike for sanity tests.
    cfg.synthetic.skynet.spikes.enabled = True
    cfg.synthetic.skynet.spikes.n_campaigns = 1
    cfg.synthetic.skynet.spikes.duration_hours_min = 1
    cfg.synthetic.skynet.spikes.duration_hours_max = 2
    cfg.synthetic.skynet.spikes.campaign_types = ["VOLUME_SPIKE"]

    return cfg


def test_d0002_pipeline_determinism(tmp_path: Path):
    cfg1 = _tiny_cfg(tmp_path / "r1")
    cfg2 = _tiny_cfg(tmp_path / "r2")

    # Use the same run_id in different output roots.
    rdir1, _ = run_all(cfg1, run_id="TEST_RUN")
    rdir2, _ = run_all(cfg2, run_id="TEST_RUN")

    m1 = read_manifest(manifest_path(rdir1))
    m2 = read_manifest(manifest_path(rdir2))

    a1 = m1["artifacts"]
    a2 = m2["artifacts"]

    # Core content hashes must match.
    for key in [
        "raw/login_attempt",
        "raw/checkout_attempt",
        "dataset/login_attempt/train",
        "dataset/login_attempt/time_eval",
        "dataset/login_attempt/user_holdout",
        "dataset/checkout_attempt/train",
        "dataset/checkout_attempt/time_eval",
        "dataset/checkout_attempt/user_holdout",
    ]:
        assert a1[key]["content_hash"] == a2[key]["content_hash"]
        assert a1[key]["rows"] == a2[key]["rows"]


def test_d0002_leakage_and_sanity(tmp_path: Path):
    cfg = _tiny_cfg(tmp_path)
    rdir, _ = run_all(cfg, run_id="TEST_SANITY")
    m = read_manifest(manifest_path(rdir))

    # Paths in manifest are relative to runs_dir. Resolve them.
    login_path = cfg.paths.runs_dir / m["artifacts"]["raw/login_attempt"]["path"]
    checkout_path = cfg.paths.runs_dir / m["artifacts"]["raw/checkout_attempt"]["path"]
    login = _read_path(login_path)
    checkout = _read_path(checkout_path)

    assert len(login) > 0
    assert len(checkout) > 0
    for col in ["label_replicators", "label_the_mule", "label_the_chameleon", "label_benign"]:
        assert col in login.columns

    attack_any = ~login["label_benign"].astype(bool)
    attack_rate = float(attack_any.mean())
    assert 0.04 <= attack_rate <= 0.08  # 6% ± 2%

    # Loose seasonality gate: hour bucket counts are not near-uniform.
    ts = _to_dt(login["event_ts"])
    hour = ts.dt.hour
    counts = hour.value_counts()
    assert (counts.max() + 1) / (counts.min() + 1) >= 1.2

    # Spike existence (volume spike): max hour count meaningfully above median.
    assert counts.max() >= 1.15 * float(counts.median())

    # Checkout adverse ≈ 0.5% with wide tolerance (small sample).
    adverse = (checkout["checkout_result"] != "success")
    adverse_rate = float(adverse.mean())
    assert 0.0 <= adverse_rate <= 0.02

    # --- Leakage checks ---
    # Load splits and ensure user_holdout users do not appear in train/time_eval.
    def _read_split(event: str, split: str) -> pd.DataFrame:
        p = cfg.paths.runs_dir / m["artifacts"][f"dataset/{event}/{split}"]["path"]
        return _read_path(p)

    lu = _read_split("login_attempt", "user_holdout")
    lt = _read_split("login_attempt", "train")
    le = _read_split("login_attempt", "time_eval")
    holdout_users = set(lu["user_id"].astype(str))
    assert holdout_users
    assert holdout_users.isdisjoint(set(lt["user_id"].astype(str)))
    assert holdout_users.isdisjoint(set(le["user_id"].astype(str)))

    cu = _read_split("checkout_attempt", "user_holdout")
    ct = _read_split("checkout_attempt", "train")
    ce = _read_split("checkout_attempt", "time_eval")
    holdout_users_c = set(cu["user_id"].astype(str))
    assert holdout_users_c
    assert holdout_users_c.isdisjoint(set(ct["user_id"].astype(str)))
    assert holdout_users_c.isdisjoint(set(ce["user_id"].astype(str)))
