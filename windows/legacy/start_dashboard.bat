@echo off
setlocal

cd /d "%~dp0.."

title UltraStats AI - Dashboard

echo.
echo ============================================================
echo UltraStats AI - Dashboard
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: Ambiente virtual nao encontrado.
    echo Caminho esperado:
    echo .venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

echo Verificando PostgreSQL...

docker exec ultrastats_postgres pg_isready -U ultrastats -d ultrastats_db >nul 2>&1

if errorlevel 1 (
    echo ERRO: O PostgreSQL nao esta pronto.
    echo Execute primeiro:
    echo windows\start_database.bat
    echo.
    pause
    exit /b 1
)

echo PostgreSQL esta pronto.
echo Iniciando Dashboard...
echo.

".venv\Scripts\python.exe" -m streamlit run dashboard\Home.py

if errorlevel 1 (
    echo.
    echo O Dashboard foi encerrado com erro.
    pause
    exit /b 1
)

echo.
echo Dashboard encerrado.