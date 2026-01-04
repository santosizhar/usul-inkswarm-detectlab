from typer.testing import CliRunner

from inkswarm_detectlab import cli
from inkswarm_detectlab.diagnostics import DiagnosticsSnapshot

runner = CliRunner()


def test_doctor_emits_versions(monkeypatch):
    fake_snapshot = DiagnosticsSnapshot(
        lines=[
            "DetectLab doctor",
            "- python: 3.12.3",
            "- platform: test-platform",
            "- sklearn: 1.4.0",
            "- pandas: 2.2.2",
            "- pyarrow: 15.0.2",
            "- threadpools: 1",
            "  - 1: testlib (8)",
        ],
        errors=[],
    )

    monkeypatch.setattr(cli, "collect_diagnostics", lambda include_threadpools=True: fake_snapshot)

    result = runner.invoke(cli.app, ["doctor"])
    assert result.exit_code == 0
    for key in ["python", "platform", "sklearn", "pandas", "pyarrow", "threadpools"]:
        assert key in result.stdout


def test_doctor_fails_on_error(monkeypatch):
    fake_snapshot = DiagnosticsSnapshot(
        lines=["DetectLab doctor", "- python: 3.12.3"], errors=["pyarrow is required"]
    )
    monkeypatch.setattr(cli, "collect_diagnostics", lambda include_threadpools=True: fake_snapshot)

    result = runner.invoke(cli.app, ["doctor"])
    assert result.exit_code != 0
    assert "pyarrow" in result.stdout
