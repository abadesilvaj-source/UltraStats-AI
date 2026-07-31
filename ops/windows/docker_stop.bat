@echo off
setlocal

cd /d "%~dp0..\.."

echo.
echo Parando UltraStats AI...
echo.

docker compose down

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel parar o sistema.
    pause
    exit /b 1
)

echo.
echo Sistema parado.
echo Os dados do PostgreSQL foram preservados.
echo.

pause
