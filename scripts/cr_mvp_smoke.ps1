Param(
  [string]$Config = "configs\skynet_smoke.yaml",
  [string]$RunId = $("CR4_SMOKE_{0}_01" -f (Get-Date -Format "yyyyMMdd"))
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$repoRoot = Get-Location
$runDir = Join-Path -Path $repoRoot -ChildPath ("runs\{0}" -f $RunId)
$logDir = Join-Path -Path $runDir -ChildPath "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$logPath = Join-Path $logDir "cr_mvp_smoke.log"

Write-Host ("Running MVP smoke: {0}" -f $RunId)

# Run with output redirected to log (keep console clean)
& python -m inkswarm_detectlab run mvp -c $Config --run-id $RunId --force *> $logPath
if ($LASTEXITCODE -ne 0) {
  Write-Host "MVP smoke FAILED. Open log:"
  Write-Host ("  {0}" -f $logPath)
  exit 2
}

Write-Host "MVP smoke OK."
Write-Host "Open these files:"
Write-Host ("  UI:            {0}" -f (Join-Path $runDir "share\ui_bundle\index.html"))
Write-Host ("  Exec summary:  {0}" -f (Join-Path $runDir "share\EXEC_SUMMARY.html"))
Write-Host ("  Full summary:  {0}" -f (Join-Path $runDir "share\summary.html"))
Write-Host ("  Open-me doc:   {0}" -f (Join-Path $runDir "share\OPEN_ME_FIRST.md"))
Write-Host "Logs:"
Write-Host ("  {0}" -f $logPath)
