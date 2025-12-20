from __future__ import annotations

from pathlib import Path
import typer

from .schemas import list_schemas, get_schema
from .config import load_config
from .pipeline import generate_raw, build_dataset, run_all

app = typer.Typer(add_completion=False, help="Inkswarm DetectLab CLI")

schemas_app = typer.Typer(add_completion=False, help="Schema utilities")
config_app = typer.Typer(add_completion=False, help="Config utilities")
synthetic_app = typer.Typer(add_completion=False, help="Synthetic data generation")
dataset_app = typer.Typer(add_completion=False, help="Dataset building")
run_app = typer.Typer(add_completion=False, help="End-to-end pipeline")

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
    """Validate a YAML config via Pydantic and print the resolved config."""
    cfg = load_config(path)
    typer.echo(cfg.model_dump_json(indent=2))

app.add_typer(schemas_app, name="schemas")
app.add_typer(config_app, name="config")
app.add_typer(synthetic_app, name="synthetic")
app.add_typer(dataset_app, name="dataset")
app.add_typer(run_app, name="run")


@synthetic_app.command("skynet")
def synthetic_skynet(config: Path, run_id: str | None = None):
    """Generate raw SKYNET tables (login_attempt + checkout_attempt) and write a partial manifest."""
    cfg = load_config(config)
    rdir, manifest = generate_raw(cfg, run_id=run_id)
    typer.echo(str(rdir))


@dataset_app.command("build")
def dataset_build(config: Path, run_id: str):
    """Build leakage-aware datasets for an existing run_id and update manifest + summary."""
    cfg = load_config(config)
    rdir, _ = build_dataset(cfg, run_id=run_id)
    typer.echo(str(rdir))


@run_app.command("skynet")
def run_skynet(config: Path, run_id: str | None = None):
    """End-to-end: generate raw SKYNET tables + build datasets + write manifest + summary."""
    cfg = load_config(config)
    rdir, _ = run_all(cfg, run_id=run_id)
    typer.echo(str(rdir))

def main():
    app()

if __name__ == "__main__":
    main()
