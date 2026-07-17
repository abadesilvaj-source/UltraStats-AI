@echo off
setlocal

cd /d "%~dp0.."

title UltraStats AI - Inicializador

echo.
echo ============================================================
echo UltraStats AI - Inicializacao completa
echo ============================================================
echo.

call windows\start_database.bat

if errorlevel 1 (
    echo.
    echo ERRO: A inicializacao foi interrompida.
    pause
    exit /b 1
)

call windows\run_migrations.bat

if errorlevel 1 (
    echo.
    echo ERRO: As migracoes falharam.
    pause
    exit /b 1
)

echo.
echo Abrindo o scheduler em uma nova janela...

start "UltraStats AI - Scheduler" cmd /k call windows\start_scheduler.bat

timeout /t 3 /nobreak >nul

echo Abrindo o Dashboard em uma nova janela...

start "UltraStats AI - Dashboard" cmd /k call windows\start_dashboard.bat

echo.
echo ============================================================
echo UltraStats AI iniciado
echo ============================================================
echo.
echo PostgreSQL: Docker
echo Scheduler: nova janela
echo Dashboard: nova janela
echo.
echo Dashboard:
echo http://localhost:8501
echo.

pause