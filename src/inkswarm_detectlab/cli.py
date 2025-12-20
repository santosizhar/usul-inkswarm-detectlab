from __future__ import annotations

from pathlib import Path
import typer

from .schemas import list_schemas, get_schema
from .config import load_config

app = typer.Typer(add_completion=False, help="Inkswarm DetectLab CLI")

schemas_app = typer.Typer(add_completion=False, help="Schema utilities")
config_app = typer.Typer(add_completion=False, help="Config utilities")

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

def main():
    app()

if __name__ == "__main__":
    main()
