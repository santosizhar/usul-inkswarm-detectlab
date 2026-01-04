from typer.testing import CliRunner

from inkswarm_detectlab import cli


runner = CliRunner()


def test_check_parquet_pass(monkeypatch):
    called = {}

    def _ok():
        called["yes"] = True

    monkeypatch.setattr(cli, "_require_pyarrow", _ok)

    result = runner.invoke(cli.app, ["config", "check-parquet"])
    assert result.exit_code == 0
    assert "Parquet support verified" in result.stdout
    assert called["yes"]


def test_check_parquet_fail(monkeypatch):
    def _fail():
        raise cli.typer.Exit(code=2)

    monkeypatch.setattr(cli, "_require_pyarrow", _fail)

    result = runner.invoke(cli.app, ["config", "check-parquet"])
    assert result.exit_code == 2
