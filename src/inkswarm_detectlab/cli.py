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
from .ui.summarize import write_ui_summary
from .ui.bundle import export_ui_bundle
from .utils.parquetify import parquetify_run
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


def _require_pyarrow() -> None:
    """Fail-closed if Parquet engine is unavailable.

    D-0005 makes Parquet mandatory. This check is intentionally cheap (single import)
    and provides a clear, actionable error.
    """
    try:
        import pyarrow  # noqa: F401
    except Exception as e:
        typer.echo(
            "ERROR: Parquet is mandatory but 'pyarrow' is not available. "
            "Install deps (pip install -e .[dev]) and re-run. "
            f"Import error: {e}"
        )
        raise typer.Exit(code=2)

schemas_app = typer.Typer(add_completion=False, help="Schema utilities")
config_app = typer.Typer(add_completion=False, help="Config utilities")
synthetic_app = typer.Typer(add_completion=False, help="Synthetic data generation")
dataset_app = typer.Typer(add_completion=False, help="Dataset building")
run_app = typer.Typer(add_completion=False, help="End-to-end pipeline")
features_app = typer.Typer(add_completion=False, help="Feature building")
baselines_app = typer.Typer(add_completion=False, help="Baseline models")
ui_app = typer.Typer(add_completion=False, help="Shareable UI bundles (static HTML)")


app.add_typer(schemas_app, name="schemas")
app.add_typer(config_app, name="config")
app.add_typer(synthetic_app, name="synthetic")
app.add_typer(dataset_app, name="dataset")
app.add_typer(run_app, name="run")
app.add_typer(features_app, name="features")
app.add_typer(baselines_app, name="baselines")
app.add_typer(ui_app, name="ui")



@app.command("doctor")
def doctor():
    """Print environment diagnostics (useful for crash triage / CI baselines)."""
    import sys
    import platform

    typer.echo("DetectLab doctor")
    typer.echo(f"- python: {sys.version.replace(chr(10), ' ')}")
    typer.echo(f"- platform: {platform.platform()}")
    try:
        import sklearn  # type: ignore

        typer.echo(f"- sklearn: {getattr(sklearn, '__version__', None)}")
    except Exception:
        typer.echo("- sklearn: <unavailable>")
    try:
        import pandas as pd  # type: ignore

        typer.echo(f"- pandas: {getattr(pd, '__version__', None)}")
    except Exception:
        typer.echo("- pandas: <unavailable>")
    try:
        import pyarrow as pa  # type: ignore

        typer.echo(f"- pyarrow: {getattr(pa, '__version__', None)}")
    except Exception:
        typer.echo("- pyarrow: <unavailable>")
    try:
        from threadpoolctl import threadpool_info  # type: ignore

        info = threadpool_info()
        typer.echo(f"- threadpools: {len(info)}")
        for i, row in enumerate(info[:10]):
            lib = row.get('internal_api') or row.get('user_api') or 'unknown'
            typer.echo(f"  - {i+1}: {lib} ({row.get('num_threads')})")
    except Exception:
        typer.echo("- threadpools: <unavailable>")


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
    _require_pyarrow()
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
    _require_pyarrow()
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
    """Explicit conversion to Parquet (ramping toward Parquet-mandatory milestone)."""
    _require_pyarrow()
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
    _require_pyarrow()
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
    _require_pyarrow()
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    rdir = run_login_baselines_for_run(cfg, run_id=run_id, force=force, cfg_path=cfg_path)
    typer.echo(str(rdir))
    _print_artifacts(rdir)
@run_app.command("skynet")
def run_skynet(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Override run_id (optional)."),
):
    """End-to-end: generate raw SKYNET tables + build datasets + write manifest + summary."""
    _require_pyarrow()
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)
    rdir, _ = run_all(cfg, run_id=run_id)
    typer.echo(str(rdir))
    _print_artifacts(rdir)




@ui_app.command("summarize")
def ui_summarize(
    config: Path = typer.Option(..., "--config", "-c", help="Path to YAML config."),
    run_id: str = typer.Option(..., "--run-id", help="Run id to summarize."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing ui_summary.json."),
):
    """Write runs/<run_id>/ui/ui_summary.json for stable UI consumption."""
    cfg = load_config(config)
    out = write_ui_summary(cfg, run_id=run_id, force=force)
    typer.echo(str(out))


@ui_app.command("export")
def ui_export(
    config: Path = typer.Option(..., "--config", "-c", help="Path to YAML config."),
    run_ids: str = typer.Option(..., "--run-ids", help="Comma-separated list of run ids (nmax=5)."),
    out_dir: Path = typer.Option(Path("ui_bundle"), "--out-dir", help="Output folder for static HTML bundle."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing ui_summary.json and bundle files."),
):
    """Export a self-contained static HTML viewer for up to 5 runs.

    Open the resulting index.html directly in a browser (no server required).
    """
    cfg = load_config(config)
    rids = [r.strip() for r in run_ids.split(",") if r.strip()]
    export_ui_bundle(cfg, run_ids=rids, out_dir=out_dir, force=force)
    typer.echo(str(out_dir))


def main():
    app()


if __name__ == "__main__":
    main()
