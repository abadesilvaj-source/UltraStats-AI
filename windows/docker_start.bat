@echo off
setlocal

cd /d "%~dp0.."

echo.
echo ============================================================
echo Iniciando UltraStats AI com Docker
echo ============================================================
echo.

docker compose up -d --build

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel iniciar o UltraStats AI.
    echo Confirme se o Docker Desktop esta aberto.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Status dos containers
echo ============================================================
echo.

docker compose ps

echo.
echo Dashboard disponivel em:
echo http://localhost:8501
echo.

pause