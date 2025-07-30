# retrieve.ps1 — forwards all args to seraphis_api.py retrieve
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$script = Join-Path $PSScriptRoot "seraphis_api.py"
python $script retrieve @args
