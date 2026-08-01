@echo off
setlocal

cd /d "%~dp0..\.."

echo.
echo ============================================================
echo UltraStats AI - Migracoes do banco
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: Ambiente virtual nao encontrado.
    pause
    exit /b 1
)

docker exec ultrastats_postgres pg_isready -U ultrastats -d ultrastats_db >nul 2>&1

if errorlevel 1 (
    echo ERRO: O PostgreSQL nao esta pronto.
    pause
    exit /b 1
)

echo Aplicando migracoes...
echo.

pushd backend
"..\.venv\Scripts\python.exe" -m alembic upgrade head
popd

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel aplicar as migracoes.
    pause
    exit /b 1
)

echo.
echo Migracoes aplicadas com sucesso.
