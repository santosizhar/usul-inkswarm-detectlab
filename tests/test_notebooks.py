from __future__ import annotations

from pathlib import Path
import pytest

nbformat = pytest.importorskip("nbformat")
nbclient = pytest.importorskip("nbclient")
NotebookClient = nbclient.NotebookClient
pytest.importorskip("pyarrow")

def _exec_notebook(path: Path) -> None:
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(nb, timeout=120, kernel_name="python3")
    client.execute()

def test_notebooks_execute():
    nb_dir = Path("notebooks")
    for nb_path in [nb_dir / "00_schema_preview.ipynb", nb_dir / "01_placeholder_data_inspection.ipynb"]:
        assert nb_path.exists()
        _exec_notebook(nb_path)
