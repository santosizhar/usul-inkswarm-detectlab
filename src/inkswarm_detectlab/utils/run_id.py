from __future__ import annotations
from datetime import datetime
from .time import BA_TZ

PLACEHOLDER_RUN_ID = "PLACEHOLDER_RUN_0001"

def make_run_id(prefix: str = "RUN") -> str:
    ts = datetime.now(tz=BA_TZ).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}"
