@echo off
setlocal

cd /d "%~dp0..\.."

echo.
echo ============================================================
echo UltraStats AI - Status
echo ============================================================
echo.

docker compose ps

echo.
pause
