Param(
  [Parameter(Mandatory=$true)]
  [string]$RunId
)

$ErrorActionPreference = "Stop"

$shareDir = Join-Path -Path "runs" -ChildPath (Join-Path $RunId "share")
if (-not (Test-Path $shareDir)) {
  throw "Missing share dir: $shareDir"
}

$outZip = "${RunId}__share.zip"
if (Test-Path $outZip) { Remove-Item $outZip -Force }

Compress-Archive -Path (Join-Path $shareDir "*") -DestinationPath $outZip -Force
Write-Host "OK: wrote $outZip"
