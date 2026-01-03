from pathlib import Path

from inkswarm_detectlab.ui.step_runner import _read_json_dict as _step_read
from inkswarm_detectlab.ui.summarize import _read_json_dict as _sum_read


def test_read_json_dict_handles_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"

    assert _step_read(missing) == {}
    assert _sum_read(missing) == {}


def test_read_json_dict_handles_invalid(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")

    assert _step_read(bad) == {}
    assert _sum_read(bad) == {}


def test_read_json_dict_reads_content(tmp_path: Path) -> None:
    good = tmp_path / "good.json"
    good.write_text('{"a": 1, "b": "two"}', encoding="utf-8")

    assert _step_read(good) == {"a": 1, "b": "two"}
    assert _sum_read(good) == {"a": 1, "b": "two"}
