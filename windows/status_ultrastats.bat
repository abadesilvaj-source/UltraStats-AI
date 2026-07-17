@echo off
setlocal

cd /d "%~dp0.."

echo.
echo ============================================================
echo UltraStats AI - Status
echo ============================================================
echo.

echo PostgreSQL:
docker ps --filter "name=ultrastats_postgres" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Scheduler registrado no banco:
echo.

docker exec ultrastats_postgres psql -U ultrastats -d ultrastats_db -c "SELECT instance_name, status, active, provider, last_heartbeat_at, last_job_status FROM scheduler_heartbeats ORDER BY id;"

echo.
echo Ultimas sincronizacoes:
echo.

docker exec ultrastats_postgres psql -U ultrastats -d ultrastats_db -c "SELECT id, source, status, triggered_by, started_at, finished_at FROM sync_runs ORDER BY id DESC LIMIT 5;"

echo.
pause