[CmdletBinding()]
param(
    [string]$ProjectName = "ultrastats-g16",
    [string]$ComposeFile = "docker-compose.staging.yml",
    [string]$EnvFile = ".env.staging.g16.local"
)

$ErrorActionPreference = "Stop"
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backupRoot = (Resolve-Path $PSScriptRoot).Path
$parts = @(Get-ChildItem -LiteralPath $backupRoot -Filter "ultrastats_full.dump.part*" | Sort-Object Name)

if ($parts.Count -eq 0) {
    throw "Nenhuma parte do dump PostgreSQL foi encontrada."
}

Push-Location $repositoryRoot
try {
    $checksumFile = Join-Path $backupRoot "SHA256SUMS.txt"
    if (-not (Test-Path -LiteralPath $checksumFile)) {
        throw "Arquivo SHA256SUMS.txt ausente."
    }

    $expectedHashes = @{}
    foreach ($line in Get-Content -LiteralPath $checksumFile) {
        if ($line -match '^([A-Fa-f0-9]{64})\s+\*(.+)$') {
            $expectedHashes[$matches[2]] = $matches[1].ToUpperInvariant()
        }
    }

    foreach ($part in $parts) {
        $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $part.FullName).Hash
        $expectedHash = $expectedHashes[$part.Name]
        if (-not $expectedHash -or $actualHash -ne $expectedHash) {
            throw "Checksum inválido para $($part.Name)."
        }
    }

    $combinedDump = Join-Path $env:TEMP "ultrastats_full.dump"
    $output = [System.IO.File]::Create($combinedDump)
    try {
        foreach ($part in $parts) {
            $input = [System.IO.File]::OpenRead($part.FullName)
            try {
                $input.CopyTo($output)
            }
            finally {
                $input.Dispose()
            }
        }
    }
    finally {
        $output.Dispose()
    }

    docker compose --env-file $EnvFile -f $ComposeFile -p $ProjectName up -d postgres
    if ($LASTEXITCODE -ne 0) { throw "Falha ao iniciar o PostgreSQL." }

    $container = docker compose --env-file $EnvFile -f $ComposeFile -p $ProjectName ps -q postgres
    if (-not $container) { throw "Container PostgreSQL não encontrado." }

    docker cp $combinedDump "${container}:/tmp/ultrastats_full.dump"
    if ($LASTEXITCODE -ne 0) { throw "Falha ao copiar o dump para o container." }

    $containerEnvironment = docker inspect $container --format '{{range .Config.Env}}{{println .}}{{end}}'
    $databaseUser = (($containerEnvironment | Where-Object { $_ -like 'POSTGRES_USER=*' }) -split '=', 2)[1]
    $databaseName = (($containerEnvironment | Where-Object { $_ -like 'POSTGRES_DB=*' }) -split '=', 2)[1]
    if (-not $databaseUser -or -not $databaseName) { throw "Configuração do PostgreSQL não encontrada." }

    docker exec $container pg_restore -U $databaseUser -d $databaseName --clean --if-exists --no-owner /tmp/ultrastats_full.dump
    if ($LASTEXITCODE -ne 0) { throw "Falha ao restaurar o PostgreSQL." }

    Write-Host "Banco UltraStats restaurado com sucesso."
}
finally {
    Pop-Location
}
