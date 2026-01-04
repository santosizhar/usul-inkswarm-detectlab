from __future__ import annotations

import json
from pathlib import Path

from inkswarm_detectlab.share.evidence import export_evidence_bundle


def test_export_evidence_bundle_creates_manifest(tmp_path: Path) -> None:
    # Minimal fake run layout
    run_dir = tmp_path / "runs" / "R0001"
    (run_dir / "share" / "ui_bundle").mkdir(parents=True, exist_ok=True)
    (run_dir / "share" / "ui_bundle" / "index.html").write_text("<html></html>", encoding="utf-8")
    (run_dir / "share" / "ui_bundle" / "app.js").write_text("console.log('ok')", encoding="utf-8")
    (run_dir / "share" / "ui_bundle" / "style.css").write_text("body {}", encoding="utf-8")

    (run_dir / "reports").mkdir(parents=True, exist_ok=True)
    (run_dir / "reports" / "summary.md").write_text("# Summary\n", encoding="utf-8")

    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs" / "baselines.log").write_text("[baselines] ok\n", encoding="utf-8")

    (run_dir / "ui").mkdir(parents=True, exist_ok=True)
    (run_dir / "ui" / "ui_summary.json").write_text("{}", encoding="utf-8")

    (run_dir / "manifest.json").write_text("{\"schema_version\": 1}\n", encoding="utf-8")

    out = export_evidence_bundle(run_dir=run_dir, force=True)
    assert out.exists()
    manifest_path = out / "evidence_manifest.json"
    assert manifest_path.exists()

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    paths = [f["path"] for f in payload["files"]]

    # Evidence manifest must not include itself
    assert "evidence_manifest.json" not in paths

    # Core artifacts must be present and hashed
    assert "README_SHARE.md" in paths
    assert "ui_bundle/index.html" in paths
    assert "reports/summary.md" in paths
    assert "logs/baselines.log" in paths
    assert "meta/manifest.json" in paths
    assert "meta/ui_summary.json" in paths
