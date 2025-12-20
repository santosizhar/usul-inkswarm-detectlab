Param(
  [string]$Config = "configs/skynet_mvp.yaml",
  # Base run id; script will execute TWO runs: <RunId>_A and <RunId>_B
  [string]$RunId = $("RR_MVP_{0}_001" -f (Get-Date -Format "yyyyMMdd"))
)

$ErrorActionPreference = "Stop"

$runA = "${RunId}_A"
$runB = "${RunId}_B"

$evidenceDir = Join-Path -Path "rr_evidence" -ChildPath (Join-Path "RR-0001" $RunId)
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null

$logPath = Join-Path $evidenceDir "rr_mvp.log"
$errPath = Join-Path $evidenceDir "rr_error.txt"

function Cleanup-RunFolder([string]$rid) {
  $p = Join-Path "runs" $rid
  if (Test-Path $p) {
    try { Remove-Item -Recurse -Force $p } catch { }
  }
}

function Require-Artifact([string]$path) {
  if (-not (Test-Path $path)) {
    throw "Missing required artifact: $path"
  }
}

function Run-One([string]$rid) {
  Write-Host "RR MVP: config=$Config run_id=$rid"
  & detectlab run skynet -c $Config --run-id $rid
  if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): detectlab run skynet" }

  & detectlab features build -c $Config --run-id $rid --force
  if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): detectlab features build" }

  & detectlab baselines run -c $Config --run-id $rid --force
  if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): detectlab baselines run" }

  Write-Host "RR MVP: verifying key artifacts for $rid..."
  Require-Artifact "runs/$rid/manifest.json"
  Require-Artifact "runs/$rid/reports/summary.md"
  Require-Artifact "runs/$rid/features/login_attempt/features.parquet"
  Require-Artifact "runs/$rid/models/login_attempt/baselines/metrics.json"
  Require-Artifact "runs/$rid/models/login_attempt/baselines/report.md"
}

try {
  # Preflight (cheap)
  Write-Host "RR MVP: preflight (doctor + parquet engine)"
  python -m inkswarm_detectlab doctor | Tee-Object -FilePath $logPath

  # Capture everything else into the same log
  Start-Transcript -Path $logPath -Append | Out-Null

  # Run A
  Run-One $runA
  & python -m inkswarm_detectlab.tools.rr_signature --run-id $runA --out (Join-Path $evidenceDir "signature_A.json")
  if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): rr_signature A" }

  # Run B
  Run-One $runB
  & python -m inkswarm_detectlab.tools.rr_signature --run-id $runB --out (Join-Path $evidenceDir "signature_B.json")
  if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): rr_signature B" }

  # Compare signatures (determinism sanity)
  # v2 rr_signature normalizes run_id-sensitive fields and emits a stable signature_digest.
  $sigAPath = (Join-Path $evidenceDir "signature_A.json")
  $sigBPath = (Join-Path $evidenceDir "signature_B.json")
  $sigA = Get-Content $sigAPath -Raw
  $sigB = Get-Content $sigBPath -Raw

  try {
    $aObj = $sigA | ConvertFrom-Json
    $bObj = $sigB | ConvertFrom-Json
    if ($aObj.signature_digest -and $bObj.signature_digest) {
      if ($aObj.signature_digest -ne $bObj.signature_digest) {
        throw "Determinism check failed: signature_digest mismatch"
      }
    } else {
      # Fallback: exact JSON equality (older schema)
      if ($sigA -ne $sigB) {
        throw "Determinism check failed: signature_A.json != signature_B.json"
      }
    }
  } catch {
    # If parsing fails, fallback to exact equality
    if ($sigA -ne $sigB) {
      throw "Determinism check failed: signature_A.json != signature_B.json"
    }
  }


  # Export stakeholder UI bundle (self-contained HTML; compares runs)
  $uiOut = Join-Path $evidenceDir "ui_bundle"
  & python -m inkswarm_detectlab ui export -c $Config --run-ids "$runA,$runB" --out-dir $uiOut --force
  if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): ui export" }

  # Evidence summary into journals
  $evidenceMd = "journals/inkswarm-detectlab__RR_EVIDENCE__RR-0001__${RunId}.md"
  & python -m inkswarm_detectlab.tools.rr_evidence_md --base-run-id $RunId --run-a $runA --run-b $runB --sig-a (Join-Path $evidenceDir "signature_A.json") --sig-b (Join-Path $evidenceDir "signature_B.json") --out $evidenceMd
  if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE): rr_evidence_md" }

  Write-Host "RR MVP OK: $RunId (two-run determinism OK)"
}
catch {
  $msg = $_.Exception.Message
  Write-Host "RR MVP FAILED: $msg"
  "RR MVP FAILED ($RunId): $msg`nLog: $logPath" | Set-Content -Path $errPath

  # Cleanup (keep evidence only)
  Cleanup-RunFolder $runA
  Cleanup-RunFolder $runB

  try { Stop-Transcript | Out-Null } catch { }
  exit 2
}
finally {
  try { Stop-Transcript | Out-Null } catch { }
}
