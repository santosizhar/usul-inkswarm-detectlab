from pathlib import Path
from inkswarm_detectlab.config import load_config

def test_load_minimal_config():
    p = Path("src/inkswarm_detectlab/config/examples/minimal.yaml")
    cfg = load_config(p)
    assert cfg.run.schema_version == "v1"
    assert cfg.run.timezone == "America/Argentina/Buenos_Aires"
    assert str(cfg.paths.runs_dir) == "runs"
