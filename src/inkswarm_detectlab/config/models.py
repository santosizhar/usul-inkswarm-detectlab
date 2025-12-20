from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field

DEFAULT_SCHEMA_VERSION = "v1"

class RunPaths(BaseModel):
    runs_dir: Path = Field(default=Path("runs"), description="Base directory for all runs.")
    run_id: str = Field(default="RUN", description="Run id (set by orchestrator).")

    def run_dir(self) -> Path:
        return self.runs_dir / self.run_id

class RunConfig(BaseModel):
    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION)
    timezone: str = Field(default="America/Argentina/Buenos_Aires")
    seed: int = Field(default=1337, ge=0)

class AppConfig(BaseModel):
    run: RunConfig = Field(default_factory=RunConfig)
    paths: RunPaths = Field(default_factory=RunPaths)
