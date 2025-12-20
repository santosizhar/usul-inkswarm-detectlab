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


def _write_parquet_or_fail(df: pd.DataFrame, parquet_path: Path) -> str:
    """Write parquet (D-0005: parquet is mandatory)."""
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        write_parquet(df, parquet_path)
    except ImportError as e:
        raise ImportError(
            "Parquet is mandatory for placeholder generation. Install pyarrow and retry."
        ) from e
    return "parquet"


def generate(run_id: str = PLACEHOLDER_RUN_ID, n_rows: int = 64, runs_dir: Path = Path("runs")) -> dict:
    run_dir = runs_dir / run_id
    raw_dir(run_dir).mkdir(parents=True, exist_ok=True)

    base_ts = datetime(2025, 12, 15, 9, 0, 0, tzinfo=BA_TZ)

    login = pd.DataFrame(
        {
            "run_id": [run_id] * n_rows,
            "event_id": [f"login_{i:04d}" for i in range(n_rows)],
            "event_ts": [base_ts + timedelta(minutes=i) for i in range(n_rows)],
            "user_id": [f"user_{i%16:03d}" for i in range(n_rows)],
            "session_id": [f"sess_{i%8:03d}" for i in range(n_rows)],
            "ip_hash": [f"ip_{i%10:03d}" for i in range(n_rows)],
            "device_fingerprint_hash": [f"dev_{i%12:03d}" for i in range(n_rows)],
            "country": ["AR"] * n_rows,
            "label_replicators": [bool(i % 21 == 0) for i in range(n_rows)],
            "label_the_mule": [bool(i % 37 == 0) for i in range(n_rows)],
            "label_the_chameleon": [bool(i % 29 == 0) for i in range(n_rows)],
            "label_benign": [True] * n_rows,
            "is_fraud": [False] * n_rows,
            "metadata_json": [json.dumps({"note": "placeholder"})] * n_rows,
            "login_result": [random.choice(["success", "failure", "challenge"]) for _ in range(n_rows)],
            "failure_reason": [random.choice([None, "bad_password", "unknown_user", "mfa_failed"]) for _ in range(n_rows)],
            "username_present": [True] * n_rows,
            "mfa_used": [bool(i % 3 == 0) for i in range(n_rows)],
            "mfa_result": [random.choice([None, "pass", "fail", "not_applicable"]) for _ in range(n_rows)],
            "support_contacted": [bool(i % 5 == 0) for i in range(n_rows)],
            "support_channel": [random.choice(["none", "chat", "email", "in_app"]) for _ in range(n_rows)],
            "support_responder_type": [random.choice(["none", "agent", "bot"]) for _ in range(n_rows)],
            "support_wait_seconds": [random.choice([None, 30, 60, 120, 240]) for _ in range(n_rows)],
            "support_handle_seconds": [random.choice([None, 60, 180, 300, 600]) for _ in range(n_rows)],
            "support_cost_usd": [random.choice([None, 0.5, 1.0, 2.0, 5.0]) for _ in range(n_rows)],
            "support_resolution": [random.choice(["none", "resolved", "unresolved", "escalated"]) for _ in range(n_rows)],
            "support_offset_seconds": [random.choice([None, 0, 60, 600]) for _ in range(n_rows)],
        }
    )

    # Make benign/fraud consistent.
    any_attack = login[["label_replicators", "label_the_mule", "label_the_chameleon"]].any(axis=1)
    login.loc[:, "label_benign"] = ~any_attack
    login.loc[:, "is_fraud"] = any_attack
    login_fmt = _write_parquet_or_fail(login, raw_table_path(run_dir, "login_attempt", fmt="parquet"))

    checkout = pd.DataFrame(
        {
            "run_id": [run_id] * n_rows,
            "event_id": [f"checkout_{i:04d}" for i in range(n_rows)],
            "event_ts": [base_ts + timedelta(minutes=i) for i in range(n_rows)],
            "user_id": [f"user_{i%16:03d}" for i in range(n_rows)],
            "session_id": [f"sess_{i%8:03d}" for i in range(n_rows)],
            "ip_hash": [f"ip_{i%10:03d}" for i in range(n_rows)],
            "device_fingerprint_hash": [f"dev_{i%12:03d}" for i in range(n_rows)],
            "country": ["AR"] * n_rows,
            "is_fraud": [False] * n_rows,
            "metadata_json": [json.dumps({"note": "placeholder"})] * n_rows,
            "payment_value": [float((i % 10) + 1) * 9.99 for i in range(n_rows)],
            "basket_size": [int((i % 5) + 1) for i in range(n_rows)],
            "is_first_time_user": [bool(i % 4 == 0) for i in range(n_rows)],
            "is_premium_user": [bool(i % 6 == 0) for i in range(n_rows)],
            "credit_card_hash": [None if i % 3 == 0 else f"cc_{i%20:03d}" for i in range(n_rows)],
            "checkout_result": [random.choice(["success", "failure", "review"]) for _ in range(n_rows)],
            "decline_reason": [random.choice([None, "insufficient_funds", "suspected_fraud", "network_error", "other"]) for _ in range(n_rows)],
        }
    )
    checkout_fmt = _write_parquet_or_fail(checkout, raw_table_path(run_dir, "checkout_attempt", fmt="parquet"))

    manifest = {
        "run_id": run_id,
        "schema_version": "v1",
        "timezone": "America/Argentina/Buenos_Aires",
        "row_counts": {"login_attempt": n_rows, "checkout_attempt": n_rows},
        "formats": {"login_attempt": login_fmt, "checkout_attempt": checkout_fmt},
        "note": "Committed placeholder run for notebooks/tests (Parquet mandatory as of D-0005).",
    }

    manifest_path(run_dir).parent.mkdir(parents=True, exist_ok=True)
    manifest_path(run_dir).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))
