@echo off
setlocal

cd /d "%~dp0.."

echo.
echo ============================================================
echo UltraStats AI - Inicializacao do PostgreSQL
echo ============================================================
echo.

docker version >nul 2>&1

if errorlevel 1 (
    echo ERRO: O Docker nao esta disponivel.
    echo.
    echo Abra o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

echo Docker encontrado.
echo Iniciando o PostgreSQL...
echo.

docker compose up -d postgres

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel iniciar o PostgreSQL.
    pause
    exit /b 1
)

echo.
echo Aguardando o banco ficar pronto...

set /a ATTEMPTS=0
set /a MAX_ATTEMPTS=30

:CHECK_DATABASE
docker exec ultrastats_postgres pg_isready -U ultrastats -d ultrastats_db >nul 2>&1

if not errorlevel 1 (
    echo.
    echo PostgreSQL esta pronto.
    exit /b 0
)

set /a ATTEMPTS+=1

if %ATTEMPTS% GEQ %MAX_ATTEMPTS% (
    echo.
    echo ERRO: O PostgreSQL nao ficou pronto no tempo esperado.
    echo Consulte os logs com:
    echo docker logs ultrastats_postgres
    pause
    exit /b 1
)

echo Tentativa %ATTEMPTS% de %MAX_ATTEMPTS%...
timeout /t 2 /nobreak >nul

goto CHECK_DATABASE