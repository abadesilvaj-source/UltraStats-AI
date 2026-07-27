# Operação local full-stack

## Inicialização

```powershell
docker compose -p ultrastats-g16 `
  -f docker-compose.staging.yml `
  --env-file .env.staging.g16.local `
  up -d --build --wait
```

Serviços:

| Serviço | URL |
|---|---|
| Frontend React | http://localhost:8516 |
| Backend FastAPI | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Dashboard legado | http://localhost:8517 |

## Verificação

```powershell
docker compose -p ultrastats-g16 -f docker-compose.staging.yml ps
curl.exe -fsS http://localhost:8000/api/v1/health
curl.exe -fsS http://localhost:8516/healthz
```

## Variáveis relevantes

| Variável | Padrão | Uso |
|---|---:|---|
| `DEFAULT_USER_TIMEZONE` | `America/Sao_Paulo` | Horário retornado pela API |
| `FRONTEND_PORT` | `8516` | Interface principal |
| `BACKEND_PORT` | `8000` | API |
| `LEGACY_DASHBOARD_PORT` | `8517` | Streamlit administrativo |
| `AUTO_STATS_MAX_PER_SYNC` | `1` | Estatísticas finais por ciclo |
| `SYNC_INTERVAL_MINUTES` | `60` | Intervalo do scheduler |

## Recuperação

Os jobs são idempotentes. Após falha de provider, aguarde o próximo ciclo ou
execute uma sincronização manual pelo console legado. Não remova payloads
brutos: eles são necessários para auditoria e reprocessamento.
