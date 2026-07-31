# Operação local full-stack

## Inicialização

```powershell
docker compose -p ultrastats-g16 `
  -f docker-compose.staging.yml `
  --env-file .env.staging.g16.local `
  up -d --build --wait
```

| Serviço | URL |
|---|---|
| Frontend React | http://localhost:8516 |
| Backend FastAPI | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |

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
| `AUTO_STATS_MAX_PER_SYNC` | `2` | Estatísticas finais por ciclo |
| `AUTO_LINEUPS_MAX_PER_SYNC` | `1` | Escalações por ciclo |
| `SYNC_INTERVAL_MINUTES` | `360` | Ciclo multifonte completo |
| `LIVE_SYNC_INTERVAL_MINUTES` | `30` | Ciclo ao vivo |

Os intervalos devem respeitar as cotas contratadas. Falhas de um provedor
degradam a execução sem desfazer dados já conciliados. Coleta bruta, fusão,
previsões, estatísticas e inteligência possuem limites transacionais
independentes.

## Recuperação

Os jobs são idempotentes. Após falha de provedor, aguarde o próximo ciclo ou
execute o scheduler novamente. Não remova payloads brutos: eles são necessários
para auditoria e reprocessamento.

Verifique `/api/v1/health`, `/api/v1/maturity/status` e a execução
`multi_provider_live` para diagnosticar atualização ao vivo.
