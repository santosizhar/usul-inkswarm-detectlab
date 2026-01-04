from __future__ import annotations

from pathlib import Path

from inkswarm_detectlab.mvp.handover import write_mvp_handover


def test_write_mvp_handover(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    rid = "RUN_X"
    rdir = runs_dir / rid
    (rdir / "share" / "ui_bundle").mkdir(parents=True, exist_ok=True)
    # minimal placeholder index.html for relative path check
    (rdir / "share" / "ui_bundle" / "index.html").write_text("<html></html>", encoding="utf-8")

    out = write_mvp_handover(
        runs_dir=runs_dir,
        run_id=rid,
        ui_bundle_dir=(rdir / "share" / "ui_bundle"),
        summary={"steps": [{"name": "x", "status": "ok"}]},
    )

    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert "MVP Handover" in txt
    assert "share/ui_bundle/index.html" in txt
