from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import yaml

from .diagnostics import collect_diagnostics, render_diagnostics
from .schemas import list_schemas, get_schema
from .config import load_config
from .pipeline import generate_raw, build_dataset, run_all
from .features import build_login_features_for_run, build_checkout_features_for_run
from .models import run_login_baselines_for_run
from .ui.summarize import write_ui_summary
from .ui.bundle import export_ui_bundle
from .mvp.orchestrator import run_mvp
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
eval_app = typer.Typer(add_completion=False, help="Evaluation diagnostics (slices + stability)")
cache_app = typer.Typer(add_completion=False, help="Inspect and maintain local caches")


app.add_typer(schemas_app, name="schemas")
app.add_typer(config_app, name="config")
app.add_typer(synthetic_app, name="synthetic")
app.add_typer(dataset_app, name="dataset")
app.add_typer(run_app, name="run")
app.add_typer(features_app, name="features")
app.add_typer(baselines_app, name="baselines")
app.add_typer(ui_app, name="ui")
app.add_typer(eval_app, name="eval")
app.add_typer(cache_app, name="cache")



@app.command("doctor")
def doctor():
    """Print environment diagnostics (useful for crash triage / CI baselines)."""
    snapshot = collect_diagnostics()
    render_diagnostics(snapshot, typer.echo)
    if snapshot.errors:
        raise typer.Exit(code=2)


@app.command("sanity")
def sanity(
    config: Path = typer.Option(
        Path("configs/skynet_smoke.yaml"),
        "--config",
        "-c",
        help="Config YAML (defaults to configs/skynet_smoke.yaml).",
    ),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Optional run id override."),
    tiny_run: bool = typer.Option(
        False,
        "--tiny-run/--no-tiny-run",
        help=(
            "If enabled, runs a small end-to-end wiring test using the step runner (may write artifacts under runs/). "
            "Disabled by default to keep CI runs side-effect free."
        ),
    ),
    force: bool = typer.Option(False, "--force", help="Force overwrite for steps that support it."),
):
    """Sanity check for RR: compile + import + (optional) tiny end-to-end run.

    This is intended to catch obvious breakages quickly without requiring a full RR run.
    """
    import compileall

    typer.echo("DetectLab sanity")

    # 1) compileall (fail-closed)
    try:
        ok = compileall.compile_dir("src", quiet=1)
    except Exception as e:  # noqa: BLE001
        typer.echo(f"[compileall] ERROR: {type(e).__name__}: {e}")
        raise typer.Exit(code=1)
    if not ok:
        typer.echo("[compileall] ERROR: compileall reported failures")
        raise typer.Exit(code=1)
    typer.echo("[compileall] OK")

    # 2) import checks (cheap)
    try:
        from .ui.step_runner import resolve_run_id, wire_check, step_dataset, step_features, step_baselines, step_eval, step_export  # noqa: F401,E501
        from .ui.steps import StepRecorder  # noqa: F401
    except Exception as e:  # noqa: BLE001
        typer.echo(f"[imports] ERROR: {type(e).__name__}: {e}")
        raise typer.Exit(code=1)
    typer.echo("[imports] OK")

    if not tiny_run:
        typer.echo("[tiny-run] skipped")
        return

    # 3) tiny end-to-end using the step runner (best-effort, but fail-closed on exceptions)
    from .ui.step_runner import resolve_run_id, wire_check, step_dataset, step_features, step_baselines, step_eval, step_export
    from .ui.steps import StepRecorder

    cfg, rid = resolve_run_id(config, run_id=run_id)
    typer.echo(f"[tiny-run] run_id={rid}")

    check = wire_check(config, run_id=rid)
    typer.echo(f"[tiny-run] run_dir={check['paths']['run_dir']}")

    rec = StepRecorder()
    # Keep it cheap: reuse_if_exists=True and shared feature cache enabled by default.
    step_dataset(cfg, cfg_path=config, run_id=rid, rec=rec, reuse_if_exists=True, force=force)
    step_features(
        cfg,
        cfg_path=config,
        run_id=rid,
        rec=rec,
        reuse_if_exists=True,
        force=force,
        use_shared_feature_cache=True,
        write_shared_feature_cache=True,
    )
    step_baselines(cfg, cfg_path=config, run_id=rid, rec=rec, reuse_if_exists=True, force=force)
    step_eval(cfg, cfg_path=config, run_id=rid, rec=rec, reuse_if_exists=True, force=force)
    step_export(cfg, cfg_path=config, run_id=rid, rec=rec, reuse_if_exists=True, force=force)

    typer.echo(rec.to_markdown(title="Sanity tiny-run steps"))

    snapshot = collect_diagnostics()
    render_diagnostics(snapshot, typer.echo)
    if snapshot.errors:
        raise typer.Exit(code=2)


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


@config_app.command("check-parquet")
def config_check_parquet():
    """Verify Parquet dependency availability (fail-closed for RR)."""
    try:
        _require_pyarrow()
    except typer.Exit:
        raise
    typer.echo("pyarrow available: Parquet support verified")


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
    event: str = typer.Option(
        "login",
        "--event",
        help="Which event type to build features for: login | checkout | all (default: login).",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite existing feature artifacts."),
):
    """Build feature tables for an existing run_id."""
    _require_pyarrow()
    cfg_path = _resolve_config(config, config_opt)
    cfg = load_config(cfg_path)

    event = event.strip().lower()
    if event not in {"login", "checkout", "all"}:
        raise typer.BadParameter("event must be one of: login, checkout, all")

    rdir = None
    if event in {"login", "all"}:
        rdir = build_login_features_for_run(cfg, run_id=run_id, force=force)
    if event in {"checkout", "all"}:
        rdir = build_checkout_features_for_run(cfg, run_id=run_id, force=force)

    assert rdir is not None
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
    rdir, results = run_login_baselines_for_run(cfg, run_id=run_id, force=force, cfg_path=cfg_path)
    if results.get("status") == "partial":
        typer.echo(
            "WARNING: One or more baseline fits failed. Outputs were written; see runs/<run_id>/logs/baselines.log and metrics.json.",
            err=True,
        )
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




@run_app.command("quick")
def run_quick_cmd(
    *,
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Override run_id (optional). Recommended to omit."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing artifacts where supported."),
    config: Path = typer.Option(Path("configs/skynet_smoke.yaml"), "--config", "-c", help="Path to YAML config (defaults to configs/skynet_smoke.yaml)."),
):
    """Fastest end-to-end path for first-time users.

    Equivalent to `detectlab run mvp -c configs/skynet_smoke.yaml`.
    """
    _require_pyarrow()
    rdir, summary = run_mvp(cfg_path=config, run_id=run_id, force=force)

    typer.echo(str(rdir))
    for row in summary.get("steps", []):
        status = row.get("status")
        name = row.get("name")
        msg = row.get("message") or ""
        if status == "ok":
            typer.echo(f"OK   - {name}{(': '+ msg) if msg else ''}")
        elif status == "skipped":
            typer.echo(f"SKIP - {name}{(': '+ msg) if msg else ''}")
        else:
            typer.echo(f"FAIL - {name}{(': '+ msg) if msg else ''}")

    _print_artifacts(rdir)
    if summary.get("status") != "ok":
        raise typer.Exit(code=1)


@run_app.command("mvp")
def run_mvp_cmd(
    config: Optional[Path] = typer.Argument(None),
    *,
    config_opt: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to YAML config."),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Override run_id (optional). Recommended to omit."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing artifacts where supported."),
):
    """MVP orchestrator: best-effort end-to-end run for non-technical sharing.

    Steps (best effort):
      1) Generate raw + build datasets (SKYNET)
      2) Build features (login only; fastest)
      3) Train baselines (login_attempt: logreg + rf)
      4) Write ui_summary.json
      5) Export shareable HTML bundle
      6) Write stakeholder handover (mvp_handover.md)

    If a step fails, the orchestrator will continue when possible and write a clear failure summary.
    """
    _require_pyarrow()
    cfg_path = _resolve_config(config, config_opt)
    rdir, summary = run_mvp(cfg_path=cfg_path, run_id=run_id, force=force)

    # Console summary (stakeholder-friendly).
    typer.echo(str(rdir))
    for row in summary.get("steps", []):
        status = row.get("status")
        name = row.get("name")
        msg = row.get("message") or ""
        if status == "ok":
            typer.echo(f"OK   - {name}{(': '+ msg) if msg else ''}")
        elif status == "skipped":
            typer.echo(f"SKIP - {name}{(': '+ msg) if msg else ''}")
        else:
            typer.echo(f"FAIL - {name}{(': '+ msg) if msg else ''}")

    _print_artifacts(rdir)
    if summary.get("status") != "ok":
        raise typer.Exit(code=1)




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


@eval_app.command("run")
def eval_run(
    run_id: str = typer.Option(..., "--run-id", help="Run id under runs/") ,
    cfg_path: Optional[Path] = typer.Option(None, "--config", help="Config path (for paths + thresholds)") ,
    force: bool = typer.Option(False, "--force", help="Recompute even if outputs exist") ,
):
    """Compute evaluation diagnostics (slices + stability) for a run."""
    _require_pyarrow()
    if cfg_path is None:
        raise typer.BadParameter("--config is required for eval (needs run paths + thresholds)")
    cfg = load_config(cfg_path)
    out = run_login_eval_for_run(cfg, run_id=run_id, force=force)
    typer.echo(f"Eval status: {out.status}")
    if out.slices_md: typer.echo(f"- slices: {out.slices_md}")
    if out.stability_md: typer.echo(f"- stability: {out.stability_md}")
    if out.notes:
        typer.echo("Notes:")
        for n in out.notes: typer.echo(f"- {n}")


@cache_app.command("list")
def cache_list(
    cfg_path: Optional[Path] = typer.Option(None, "--config", help="Config path (to resolve cache_dir)."),
    cache_dir: Optional[Path] = typer.Option(None, "--cache-dir", help="Direct path to cache root (overrides --config)."),
):
    """List feature-cache entries (newest first)."""
    from .cache.ops import iter_feature_cache_entries

    if cache_dir is None:
        if cfg_path is None:
            raise typer.BadParameter("Provide --cache-dir or --config")
        cfg = load_config(cfg_path)
        cache_dir = Path(cfg.paths.cache_dir)

    entries = iter_feature_cache_entries(Path(cache_dir))
    if not entries:
        typer.echo("No feature-cache entries found.")
        return

    typer.echo("feature_key\tcreated_at\tlast_used_at\tcomplete\tsize_mb")
    for e in entries:
        created = e.created_at.isoformat().replace("+00:00", "Z") if e.created_at else ""
        last = e.last_used_at.isoformat().replace("+00:00", "Z") if e.last_used_at else ""
        size_mb = f"{(e.size_bytes / (1024*1024)):.2f}"
        typer.echo(f"{e.feature_key}\t{created}\t{last}\t{int(e.complete)}\t{size_mb}")


@cache_app.command("prune")
def cache_prune(
    cfg_path: Optional[Path] = typer.Option(None, "--config", help="Config path (to resolve cache_dir)."),
    cache_dir: Optional[Path] = typer.Option(None, "--cache-dir", help="Direct path to cache root (overrides --config)."),
    older_than_days: int = typer.Option(30, "--older-than-days", help="Delete entries older than this many days."),
    keep_latest: int = typer.Option(10, "--keep-latest", help="Always keep N newest entries."),
    yes: bool = typer.Option(False, "--yes", help="Actually delete. Without --yes, this is a dry run."),
):
    """Prune feature-cache entries (safe-by-default)."""
    from .cache.ops import prune_feature_cache

    if cache_dir is None:
        if cfg_path is None:
            raise typer.BadParameter("Provide --cache-dir or --config")
        cfg = load_config(cfg_path)
        cache_dir = Path(cfg.paths.cache_dir)

    res = prune_feature_cache(
        Path(cache_dir),
        older_than_days=older_than_days,
        keep_latest=keep_latest,
        dry_run=not yes,
    )

    if not res.deleted:
        typer.echo("Nothing to prune.")
        return

    mode = "DRY_RUN" if not yes else "DELETED"
    typer.echo(f"{mode}: {len(res.deleted)} entries")
    for p in res.deleted:
        typer.echo(f"- {p}")
