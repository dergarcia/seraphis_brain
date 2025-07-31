param(
  [Parameter(Mandatory=$true)][string]$q,
  [int]$k = 5
)

# URL‑encode the query to be safe
$encoded = [uri]::EscapeDataString($q)

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5057/retrieve?query=$encoded&top_k=$k" `
  -Method Get
