Param(
  [string]$Config = "configs/skynet_smoke.yaml",
  [string]$RunId = "RUN_SAMPLE_SMOKE_0001"
)

$ErrorActionPreference = "Stop"

Write-Host "== D-0004 Deferred Validation (Parquet-mandatory as of D-0005) ==" -ForegroundColor Cyan
Write-Host "Config: $Config"
Write-Host "RunId : $RunId"

# If the run contains legacy CSV artifacts, migrate them to Parquet first.
detectlab dataset parquetify -c $Config --run-id $RunId --force

pytest -q

detectlab features build -c $Config --run-id $RunId --force
detectlab baselines run -c $Config --run-id $RunId --force

Write-Host "Done. Check runs/$RunId/models/login_attempt/reports/baseline_report.md" -ForegroundColor Green
