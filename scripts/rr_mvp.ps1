Param(
  [string]$Config = "configs/skynet_mvp.yaml",
  [string]$RunId = $("RR_MVP_{0}_001" -f (Get-Date -Format "yyyyMMdd"))
)

Write-Host "RR MVP: config=$Config run_id=$RunId"

try { python -m inkswarm_detectlab doctor } catch { }

# Windows reproducibility defaults (caller can override)
if (-not $env:OMP_NUM_THREADS) { $env:OMP_NUM_THREADS = "1" }
if (-not $env:MKL_NUM_THREADS) { $env:MKL_NUM_THREADS = "1" }
if (-not $env:OPENBLAS_NUM_THREADS) { $env:OPENBLAS_NUM_THREADS = "1" }
if (-not $env:NUMEXPR_NUM_THREADS) { $env:NUMEXPR_NUM_THREADS = "1" }

detectlab run skynet -c $Config --run-id $RunId

detectlab features build -c $Config --run-id $RunId --force

detectlab baselines run -c $Config --run-id $RunId --force

Write-Host "RR MVP: verifying key artifacts..."
$paths = @(
  "runs/$RunId/manifest.json",
  "runs/$RunId/reports/summary.md",
  "runs/$RunId/features/login_attempt/features.parquet",
  "runs/$RunId/models/login_attempt/baselines/metrics.json",
  "runs/$RunId/models/login_attempt/baselines/report.md"
)
foreach ($p in $paths) {
  if (-not (Test-Path $p)) { throw "Missing required artifact: $p" }
}

Write-Host "RR MVP OK: $RunId"
