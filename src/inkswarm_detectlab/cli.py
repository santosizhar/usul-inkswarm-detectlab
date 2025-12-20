from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import yaml

from .schemas import list_schemas, get_schema
from .config import load_config
from .pipeline import generate_raw, build_dataset, run_all
from .features import build_login_features_for_run
from .models import run_login_baselines_for_run
from .utils.parquetify import parquetify_run
from .reports import generate_final_report_for_run
from .io.manifest import read_manifest
from .io.paths import manifest_path

app = typer.Typer(
    add_completion=False,
    help=(
        "Inkswarm DetectLab CLI\n\n"
        "Happy path:\n"
        "  1) Validate config:  detectlab config validate <config.yaml>\n"
        "  2) Show config:      detectlab config show <config.yaml>\n"
        "  3) Run smoke:        detectlab run skynet <config.yaml>\n"
        "     (or: detectlab run skynet --config <config.yaml>)\n"
    ),
)

schemas_app = typer.Typer(add_completion=False, help="Schema utilities")
config_app = typer.Typer(add_completion=False, help="Config utilities")
synthetic_app = typer.Typer(add_completion=False, help="Synthetic data generation")
dataset_app = typer.Typer(add_completion=False, help="Dataset building")
run_app = typer.Typer(add_completion=False, help="End-to-end pipeline")
features_app = typer.Typer(add_completion=False, help="Feature building")
baselines_app = typer.Typer(add_completion=False, help="Baseline models")
report_app = typer.Typer(add_completion=False, help="Reporting utilities")

app.add_typer(schemas_app, name="schemas")
app.add_typer(config_app, name="config")
app.add_typer(synthetic_app, name="synthetic")
app.add_typer(dataset_app, name="dataset")
app.add_typer(run_app, name="run")
app.add_typer(features_app, name="features")
app.add_typer(baselines_app, name="baselines")
app.add_typer(report_app, name="report")


def _resolve_config(arg: Optional[Path], opt: Optional[Path]) -> Path:
    if opt is not None:
        return opt
    if arg is not None:
        return arg
    raise typer.BadParameter("Missing config path. Provide as positional arg or via --config.")


def _print_artifacts(rdir: Path) -> None:
    m = read_manifest(manifest_path(rdir))
    artifacts = m.get("artifacts", {}) or {}
    if not artifacts:
        return
    typer.echo("")
    typer.echo("Outputs written:")
    for k in sorted(artifacts.keys()):
        a = artifacts[k]
        note = a.get("note")
        if note:
            typer.echo(f"- {k}: {a.get('path')} ({a.get('format')}; {note})")
        else:
            typer.echo(f"- {k}: {a.get('path')} ({a.get('format')})")


@schemas_app.command("list")
def schemas_list():
    """List available schemas."""
    for s in list_schemas():
        typer.echo(s)


@schemas_app.command("show")
def schemas_show(name: str):
    """Print a schema as Markdown."""
    schema = get_schema(name)
    typer.echo(schema.to_markdown())


@config_app.command("validate")
def config_validate(path: Path):
    """Validate a YAML config via Pydantic (prints OK on success)."""
    _ = load_config(path)
    typer.echo("OK")


@config_app.command("show")
def config_show(path: Path):
    """Print the fully-resolved config (defaults applied) as YAML."""
    cfg = load_config(path)
    d = cfg.model_dump()
    typer.echo(yaml.safe_dump(d, sort_keys=False))


@synthetic_app.command("skynet")
def synthetic_skynet(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Override run_id (optional)."),
):
    """Generate raw SKYNET tables (login_attempt + checkout_attempt) and write a partial manifest."""
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    rdir, _ = generate_raw(cfg, run_id=run_id)
    typer.echo(str(rdir))
    _print_artifacts(rdir)


@dataset_app.command("build")
def dataset_build(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: str = typer.Option(..., "--run-id", help="Existing run_id to build datasets for."),
):
    """Build leakage-aware datasets for an existing run_id and update manifest + summary."""
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    rdir, _ = build_dataset(cfg, run_id=run_id)
    typer.echo(str(rdir))
    _print_artifacts(rdir)

@dataset_app.command("parquetify")
def dataset_parquetify(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: str = typer.Option(..., "--run-id", help="Existing run_id to convert CSV artifacts to Parquet."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing Parquet artifacts if present."),
):
    """Migrate a legacy run that contains CSV artifacts to Parquet.

This writes `.parquet` files next to existing `.csv` files, updates the run manifest to
point to Parquet paths, and keeps the CSV files (migration keeps originals).
"""
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    rdir = parquetify_run(cfg, run_id=run_id, force=force)
    typer.echo(str(rdir))
    _print_artifacts(rdir)




@features_app.command("build")
def features_build(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: str = typer.Option(..., "--run-id", help="Existing run_id to build features for."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing feature artifacts."),
):
    """Build login_attempt feature table for an existing run_id."""
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    rdir = build_login_features_for_run(cfg, run_id=run_id, force=force)
    typer.echo(str(rdir))
    _print_artifacts(rdir)


@baselines_app.command("run")
def baselines_run(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: str = typer.Option(..., "--run-id", help="Existing run_id to train baselines for."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing baseline artifacts."),
):
    """Train baseline models for login_attempt (writes under runs/<run_id>/models/...)."""
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    rdir = run_login_baselines_for_run(cfg, run_id=run_id, force=force)
    typer.echo(str(rdir))
    _print_artifacts(rdir)

@report_app.command("generate")
def report_generate(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: str = typer.Option(..., "--run-id", help="Existing run_id to generate report for."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing report artifacts."),
):
    """Generate a stitched final report (D-0006) for a run."""
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    out = generate_final_report_for_run(cfg, run_id=run_id, force=force)
    typer.echo(str(out))

@run_app.command("skynet")
def run_skynet(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Override run_id (optional)."),
):
    """End-to-end: generate raw SKYNET tables + build datasets + write manifest + summary."""
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    rdir, _ = run_all(cfg, run_id=run_id)
    typer.echo(str(rdir))
    _print_artifacts(rdir)


def main():
    app()


if __name__ == "__main__":
    main()
