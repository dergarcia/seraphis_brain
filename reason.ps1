# reason.ps1 — runs the reasoner via seraphis_api.py
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$script = Join-Path $PSScriptRoot "seraphis_api.py"
python $script reason
