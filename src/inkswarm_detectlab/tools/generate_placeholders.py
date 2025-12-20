from __future__ import annotations

from pathlib import Path
import json
import random
from datetime import datetime, timedelta

import pandas as pd

from ..utils.run_id import PLACEHOLDER_RUN_ID
from ..utils.time import BA_TZ
from ..io.paths import raw_dir, raw_table_path, manifest_path
from ..io.tables import write_parquet

def _write(df: pd.DataFrame, parquet_path: Path) -> str:
    """Write Parquet (mandatory as of D-0005). Returns 'parquet'."""
    write_parquet(df, parquet_path)
    return "parquet"

def generate(run_id: str = PLACEHOLDER_RUN_ID, n_rows: int = 64, runs_dir: Path = Path("runs")) -> dict:
    run_dir = runs_dir / run_id
    raw_dir(run_dir).mkdir(parents=True, exist_ok=True)

    base_ts = datetime(2025, 12, 15, 9, 0, 0, tzinfo=BA_TZ)

    login = pd.DataFrame({
        "run_id": [run_id]*n_rows,
        "event_id": [f"login_{i:04d}" for i in range(n_rows)],
        "event_ts": [base_ts + timedelta(minutes=i) for i in range(n_rows)],
        "user_id": [f"user_{i%16:03d}" for i in range(n_rows)],
        "session_id": [f"sess_{i%8:03d}" for i in range(n_rows)],
        "ip_hash": [f"ip_{i%10:03d}" for i in range(n_rows)],
        "device_fingerprint_hash": [f"dev_{i%12:03d}" for i in range(n_rows)],
        "country": ["AR"]*n_rows,
        "label_replicators": [bool(i % 21 == 0) for i in range(n_rows)],
        "label_the_mule": [bool(i % 37 == 0) for i in range(n_rows)],
        "label_the_chameleon": [bool(i % 29 == 0) for i in range(n_rows)],
        "label_benign": [True] * n_rows,
        "is_fraud": [False] * n_rows,
        "metadata_json": [json.dumps({"note":"placeholder"})]*n_rows,
        "login_result": [random.choice(["success","failure","challenge"]) for _ in range(n_rows)],
        "failure_reason": [random.choice([None,"bad_password","unknown_user","mfa_failed"]) for _ in range(n_rows)],
        "username_present": [True]*n_rows,
        "mfa_used": [bool(i % 3 == 0) for i in range(n_rows)],
        "mfa_result": [random.choice([None,"pass","fail","not_applicable"]) for _ in range(n_rows)],
        "support_contacted": [bool(i % 5 == 0) for i in range(n_rows)],
        "support_channel": [random.choice(["none","chat","email","in_app"]) for _ in range(n_rows)],
        "support_responder_type": [random.choice(["none","agent","bot"]) for _ in range(n_rows)],
        "support_wait_seconds": [random.choice([None, 30, 60, 120, 240]) for _ in range(n_rows)],
        "support_handle_seconds": [random.choice([None, 60, 180, 300, 600]) for _ in range(n_rows)],
        "support_cost_usd": [random.choice([None, 0.5, 1.0, 2.0, 5.0]) for _ in range(n_rows)],
        "support_resolution": [random.choice(["none","resolved","unresolved","escalated"]) for _ in range(n_rows)],
        "support_offset_seconds": [random.choice([None, 0, 60, 600]) for _ in range(n_rows)],
    })
    # make benign/fraud consistent
    any_attack = login[["label_replicators","label_the_mule","label_the_chameleon"]].any(axis=1)
    login.loc[:, "label_benign"] = ~any_attack
    login.loc[:, "is_fraud"] = any_attack
    login_fmt = _write(login, raw_table_path(run_dir, "login_attempt", fmt="parquet"))

    checkout = pd.DataFrame({
        "run_id": [run_id]*n_rows,
        "event_id": [f"checkout_{i:04d}" for i in range(n_rows)],
        "event_ts": [base_ts + timedelta(minutes=i) for i in range(n_rows)],
        "user_id": [f"user_{i%16:03d}" for i in range(n_rows)],
        "session_id": [f"sess_{i%8:03d}" for i in range(n_rows)],
        "ip_hash": [f"ip_{i%10:03d}" for i in range(n_rows)],
        "device_fingerprint_hash": [f"dev_{i%12:03d}" for i in range(n_rows)],
        "country": ["AR"]*n_rows,
        "is_fraud": [False] * n_rows,
        "metadata_json": [json.dumps({"note":"placeholder"})]*n_rows,
        "payment_value": [float((i%10)+1) * 9.99 for i in range(n_rows)],
        "basket_size": [int((i%5)+1) for i in range(n_rows)],
        "is_first_time_user": [bool(i % 4 == 0) for i in range(n_rows)],
        "is_premium_user": [bool(i % 6 == 0) for i in range(n_rows)],
        "credit_card_hash": [None if i % 3 == 0 else f"cc_{i%20:03d}" for i in range(n_rows)],
        "checkout_result": [random.choice(["success","failure","review"]) for _ in range(n_rows)],
        "decline_reason": [random.choice([None,"insufficient_funds","suspected_fraud","network_error","other"]) for _ in range(n_rows)],
    })
    checkout_fmt = _write(checkout, raw_table_path(run_dir, "checkout_attempt", fmt="parquet"))

    manifest = {
        "run_id": run_id,
        "schema_version": "v1",
        "timezone": "America/Argentina/Buenos_Aires",
        "row_counts": {"login_attempt": n_rows, "checkout_attempt": n_rows},
        "formats": {"login_attempt": login_fmt, "checkout_attempt": checkout_fmt},
        "note": "Committed placeholder run for notebooks/tests (format may be csv if parquet engine unavailable).",
    }
    manifest_path(run_dir).parent.mkdir(parents=True, exist_ok=True)
    manifest_path(run_dir).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))
