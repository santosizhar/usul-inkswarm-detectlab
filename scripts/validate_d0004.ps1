Param(
  [string]$Config = "configs/skynet_smoke.yaml",
  [string]$RunId = "RUN_SAMPLE_SMOKE_0001"
)

$ErrorActionPreference = "Stop"

Write-Host "== D-0004 Deferred Validation ==" -ForegroundColor Cyan
Write-Host "Config: $Config"
Write-Host "RunId : $RunId"

pytest -q

detectlab features build -c $Config --run-id $RunId --force
detectlab baselines run -c $Config --run-id $RunId --force

# optional: parquet conversion (requires pyarrow)
detectlab dataset parquetify -c $Config --run-id $RunId --force

Write-Host "Done. Check runs/$RunId/models/login_attempt/baselines/report.md" -ForegroundColor Green
