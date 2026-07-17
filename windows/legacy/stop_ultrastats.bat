@echo off
setlocal

cd /d "%~dp0.."

echo.
echo ============================================================
echo UltraStats AI - Encerramento
echo ============================================================
echo.

echo Encerrando processos do Dashboard e Scheduler...

taskkill /FI "WINDOWTITLE eq UltraStats AI - Scheduler*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq UltraStats AI - Dashboard*" /T /F >nul 2>&1

echo Processos encerrados.
echo.

set /p STOP_DATABASE="Deseja parar tambem o PostgreSQL? (S/N): "

if /I "%STOP_DATABASE%"=="S" (
    echo.
    echo Parando PostgreSQL...

    docker compose stop postgres

    if errorlevel 1 (
        echo Nao foi possivel parar o PostgreSQL.
    ) else (
        echo PostgreSQL parado.
    )
)

echo.
echo Encerramento concluido.
pause