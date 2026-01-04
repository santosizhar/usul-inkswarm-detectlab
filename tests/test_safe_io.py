from pathlib import Path

import pytest

from inkswarm_detectlab.utils.safe_io import read_json_strict, safe_read_json, safe_read_text


def test_safe_read_text_missing_returns_default(tmp_path: Path) -> None:
    target = tmp_path / "missing.txt"
    assert safe_read_text(target) is None
    assert safe_read_text(target, default="fallback") == "fallback"


def test_safe_read_json_handles_invalid_and_missing(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    assert safe_read_json(missing, default={}) == {}

    bad = tmp_path / "bad.json"
    bad.write_text("not-json", encoding="utf-8")
    assert safe_read_json(bad, default={}) == {}


def test_safe_read_json_reads_valid_payload(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text("{\"a\": 1}", encoding="utf-8")
    assert safe_read_json(target) == {"a": 1}


def test_read_json_strict_surfaces_missing(tmp_path: Path) -> None:
    target = tmp_path / "missing.json"
    with pytest.raises(RuntimeError):
        read_json_strict(target)


def test_read_json_strict_surfaces_invalid(tmp_path: Path) -> None:
    target = tmp_path / "bad.json"
    target.write_text("{not json}", encoding="utf-8")
    with pytest.raises(RuntimeError):
        read_json_strict(target)
