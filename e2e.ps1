# e2e.ps1 — End‑to‑end test through the kilo adapter -> local HTTP server
$ErrorActionPreference = "Stop"

# Always resolve paths relative to this script
$root = $PSScriptRoot
Set-Location -LiteralPath $root

$tailStart = "C:\Users\degarcia\Seraphis\Tools\tail_server_start.ps1"
$tailStop  = "C:\Users\degarcia\Seraphis\Tools\tail_server_stop.ps1"
$serverLog = Join-Path $root "artifacts\server.log"
$adapter   = Join-Path $root "kilo_seraphis_adapter.py"

Write-Host "1) Check server"
try {
    $pong = Invoke-RestMethod -Uri "http://127.0.0.1:5057/ping" -Method Get
    Write-Host "   Server OK = $($pong.ok)"
} catch {
    Write-Host "   Server is not running. In another window run:  python .\seraphis_server.py"
    throw
}

Write-Host "`n2) Start background tail"
& "$tailStart" | Out-Host

Write-Host "`n3) Learn via adapter"
# single line avoids backtick/whitespace gotchas
python "$adapter" learn --query "Draft a weekly QA smoke checklist for Seraphis." --category operations --score 7.7 --chunk-id 10

Write-Host "`n4) Retrieve via adapter"
python "$adapter" retrieve --query "smoke checklist" --top-k 5

Write-Host "`n5) Reason via adapter"
python "$adapter" reason

Write-Host "`n6) Last 40 server log lines"
Get-Content -LiteralPath "$serverLog" -Tail 40

Write-Host "`n7) Stop background tail"
& "$tailStop" | Out-Host

Write-Host "`nE2E complete."
