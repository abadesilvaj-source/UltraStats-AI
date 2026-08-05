param(
    [string]$OutputDirectory = "reports/generated/backups",
    [int]$RetentionDays = 14,
    [string]$PostgresContainer = "ultrastats-g16-postgres-1",
    [string]$DatabaseUser = "ultrastats_g16",
    [string]$DatabaseName = "ultrastats_g16"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$outputPath = Join-Path $projectRoot $OutputDirectory
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$dumpName = "ultrastats-$stamp.dump"
$dumpPath = Join-Path $outputPath $dumpName
$temporaryDatabase = "ultrastats_g35_restore_$stamp" -replace "-", "_"

if (-not $temporaryDatabase.StartsWith("ultrastats_g35_restore_")) {
    throw "Nome do banco temporario recusado."
}

try {
    docker inspect $PostgresContainer | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Container PostgreSQL nao encontrado." }
    docker exec $PostgresContainer pg_dump -U $DatabaseUser -d $DatabaseName -Fc -f "/tmp/$dumpName"
    if ($LASTEXITCODE -ne 0) { throw "pg_dump falhou." }
    docker cp "${PostgresContainer}:/tmp/$dumpName" $dumpPath
    if ((Get-Item $dumpPath).Length -le 0) { throw "Backup vazio." }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $dumpPath).Hash.ToLowerInvariant()
    Set-Content -LiteralPath "$dumpPath.sha256" -Value "$hash  $dumpName"

    docker exec $PostgresContainer createdb -U $DatabaseUser $temporaryDatabase
    docker exec $PostgresContainer pg_restore -U $DatabaseUser -d $temporaryDatabase --no-owner --no-privileges "/tmp/$dumpName"

    $tables = @("matches", "predictions", "odds_snapshots", "paper_bets", "users")
    $counts = @{}
    foreach ($table in $tables) {
        $source = docker exec $PostgresContainer psql -U $DatabaseUser -d $DatabaseName -Atqc "select count(*) from $table"
        $restored = docker exec $PostgresContainer psql -U $DatabaseUser -d $temporaryDatabase -Atqc "select count(*) from $table"
        if ([int64]$source -ne [int64]$restored) { throw "Contagem divergente em $table." }
        $counts[$table] = [int64]$source
    }
    $evidence = [ordered]@{
        status = "verified"; created_at = (Get-Date).ToUniversalTime().ToString("o")
        dump = $dumpName; sha256 = $hash; size_bytes = (Get-Item $dumpPath).Length
        critical_counts = $counts; restore_database = $temporaryDatabase
    }
    $evidence | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputPath "g35-restore-$stamp.json")

    Get-ChildItem -LiteralPath $outputPath -File |
        Where-Object { $_.LastWriteTimeUtc -lt (Get-Date).ToUniversalTime().AddDays(-$RetentionDays) } |
        Where-Object { $_.Name -match '^ultrastats-\d{8}-\d{6}\.dump(\.sha256)?$|^g35-restore-\d{8}-\d{6}\.json$' } |
        Remove-Item -Force
    $evidence | ConvertTo-Json -Depth 5
}
finally {
    docker exec $PostgresContainer dropdb -U $DatabaseUser --if-exists $temporaryDatabase | Out-Null
    docker exec $PostgresContainer sh -c "rm -f '/tmp/$dumpName'" | Out-Null
}
