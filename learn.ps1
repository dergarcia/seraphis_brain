param(
  [Parameter(Mandatory=$true)][string]$q,
  [string]$category = "operations",
  [double]$score    = 7.7,
  [int]$chunk       = 10
)

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5057/learn" `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{
    query    = $q
    category = $category
    score    = $score
    chunk_id = $chunk
  } | ConvertTo-Json -Depth 5)
