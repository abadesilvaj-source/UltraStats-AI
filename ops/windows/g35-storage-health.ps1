param(
    [double]$CapacityGB = 36.99,
    [string]$PostgresContainer = "ultrastats-g16-postgres-1",
    [string]$DatabaseUser = "ultrastats_g16",
    [string]$DatabaseName = "ultrastats_g16"
)

$ErrorActionPreference = "Stop"
$rawBytes = docker exec $PostgresContainer psql -U $DatabaseUser -d $DatabaseName -Atqc "select pg_database_size(current_database())"
if ($LASTEXITCODE -ne 0 -or -not $rawBytes) { throw "Nao foi possivel consultar o PostgreSQL." }
$bytes = [int64]$rawBytes
$capacityBytes = [int64]($CapacityGB * 1GB)
$percent = [math]::Round(100 * $bytes / $capacityBytes, 2)
$level = if ($percent -ge 90) { "emergency" } elseif ($percent -ge 85) { "critical" } elseif ($percent -ge 75) { "warning" } else { "healthy" }
[ordered]@{
    checked_at = (Get-Date).ToUniversalTime().ToString("o")
    database_bytes = $bytes; capacity_bytes = $capacityBytes
    usage_percent = $percent; level = $level
    thresholds = @{ warning = 75; critical = 85; emergency = 90 }
} | ConvertTo-Json -Depth 4
