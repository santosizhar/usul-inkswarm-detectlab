from __future__ import annotations
from datetime import datetime
from .time import BA_TZ

PLACEHOLDER_RUN_ID = "PLACEHOLDER_RUN_0001"

def make_run_id(config_hash8: str, prefix: str = "RUN") -> str:
    """Autogenerate run ids as RUN_<YYYYMMDD-HHMMSS>_<configHash8>."""
    ts = datetime.now(tz=BA_TZ).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}_{ts}_{config_hash8}"
