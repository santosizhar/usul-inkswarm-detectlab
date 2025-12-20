from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

BA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")

def now_ba() -> datetime:
    return datetime.now(tz=BA_TZ)

def ensure_ba(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=BA_TZ)
    return dt.astimezone(BA_TZ)
