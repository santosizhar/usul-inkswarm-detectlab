from __future__ import annotations
from pathlib import Path
import yaml
from .models import AppConfig

def load_config(path: Path) -> AppConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        data = {}
    return AppConfig.model_validate(data)
