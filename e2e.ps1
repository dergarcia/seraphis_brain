# e2e.ps1 — End-to-end smoke via kilo adapter -> local HTTP server
# Examples:
#   .\e2e.ps1                              # default smoke
#   .\e2e.ps1 -q "smoke checklist" -k 5    # change params

param(
  [string]$q = "smoke checklist",
  [int]$k = 5
)

$ErrorActionPreference = "Stop"

# Robust script root (works in PS 5/7 and different invocation styles)
$ROOT = if ($PSScriptRoot) {
  $PSScriptRoot
} elseif ($MyInvocation.MyCommand.Path) {
  Split-Path -Path $MyInvocation.MyCommand.Path -Parent
} else {
  (Get-Location).Path
}

function Write-Step([string]$msg) {
  Write-Host "`n==> $msg" -ForegroundColor Cyan
}

function Test-Server {
  try {
    $pong = Invoke-RestMethod -Uri "http://127.0.0.1:5057/ping" -Method Get -TimeoutSec 5
    return [bool]$pong.ok
  } catch { return $false }
}

function Start-Server-IfNeeded {
  if (Test-Server) {
    Write-Host "Server OK = True" -ForegroundColor Green
    return
  }

  Write-Host "Server not running. Starting seraphis_server.py..." -ForegroundColor Yellow
  $py = (Get-Command python.exe -ErrorAction Stop).Source
  $server = Join-Path $ROOT "seraphis_server.py"
  # Start minimized (separate window) and do not block this shell
  Start-Process -FilePath $py -ArgumentList @($server) -WindowStyle Minimized | Out-Null

  # Wait up to 20s for /ping to come alive
  $deadline = (Get-Date).AddSeconds(20)
  do {
    Start-Sleep -Milliseconds 500
    if (Test-Server) {
      Write-Host "Server OK = True" -ForegroundColor Green
      return
    }
  } while ((Get-Date) -lt $deadline)

  throw "Server failed to start within 20s."
}

function Start-Tail {
  $tailStart = "C:\Users\degarcia\Seraphis\Tools\tail_server_start.ps1"
  if (-not (Test-Path $tailStart)) { throw "Tail start script not found: $tailStart" }
  Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoProfile","-ExecutionPolicy","Bypass","-File",$tailStart
  ) -WindowStyle Hidden | Out-Null
  Start-Sleep -Seconds 1
}

function Stop-Tail {
  $tailStop = "C:\Users\degarcia\Seraphis\Tools\tail_server_stop.ps1"
  if (Test-Path $tailStop) {
    Start-Process -FilePath "powershell" -ArgumentList @(
      "-NoProfile","-ExecutionPolicy","Bypass","-File",$tailStop
    ) -WindowStyle Hidden -Wait | Out-Null
  }
}

function Show-Log([int]$lines=80) {
  $log = Join-Path $ROOT "artifacts\server.log"
  if (Test-Path $log) {
    Write-Host "`n--- Last $lines server.log lines ---"
    Get-Content $log -Tail $lines
  } else {
    Write-Host "No server log at $log yet."
  }
}

# Safe Python runner (avoids REPL/AttributeError hang)
function Run-Py {
  param([string[]]$pyArgs)

  $py = (Get-Command python.exe -ErrorAction Stop).Source
  $toShow = ($pyArgs | ForEach-Object { if ($_ -match '\s') { '"{0}"' -f $_ } else { $_ } }) -join ' '
  Write-Host "[RUN] python $toShow"
  & $py $pyArgs
  if ($LASTEXITCODE -ne 0) { throw "python failed exit=$LASTEXITCODE" }
}

# --- Main ---
$ok = $false
try {
  Write-Step "1) Check server"
  Start-Server-IfNeeded

  Write-Step "2) Start background tail"
  Start-Tail
  Write-Host "Tail started. Use tail_server_stop.ps1 to stop."

  Write-Step "3) Learn via adapter"
  Run-Py (Join-Path $ROOT "kilo_seraphis_adapter.py") "learn" `
         "--query"   "Draft a weekly QA smoke checklist for Seraphis." `
         "--category" "operations" `
         "--score"   "7.7" `
         "--chunk-id" "10"

  Write-Step "4) Retrieve via adapter"
  Run-Py (Join-Path $ROOT "kilo_seraphis_adapter.py") "retrieve" `
         "--query" $q `
         "--top-k" $k

  Write-Step "5) Reason via adapter"
  Run-Py (Join-Path $ROOT "kilo_seraphis_adapter.py") "reason"

  Show-Log 80
  $ok = $true
}
catch {
  Write-Host "E2E FAILED: $($_.Exception.Message)" -ForegroundColor Red
  Show-Log 80
  throw
}
finally {
  Write-Step "7) Stop background tail"
  try { Stop-Tail } catch { Write-Host "Tail stop error: $($_.Exception.Message)" -ForegroundColor DarkYellow }

  if ($ok) { Write-Host "`nE2E ✅  complete." -ForegroundColor Green }
  else     { Write-Host "`nE2E ❌  failed."   -ForegroundColor Red }
}
