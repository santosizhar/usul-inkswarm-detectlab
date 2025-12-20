from datetime import datetime
from inkswarm_detectlab.utils.time import BA_TZ, ensure_ba

def test_ba_timezone_constant():
    assert str(BA_TZ) == "America/Argentina/Buenos_Aires"

def test_ensure_ba_naive():
    dt = datetime(2025, 1, 1, 0, 0, 0)  # naive
    dt2 = ensure_ba(dt)
    assert dt2.tzinfo is not None
    assert dt2.tzinfo.key == "America/Argentina/Buenos_Aires"
