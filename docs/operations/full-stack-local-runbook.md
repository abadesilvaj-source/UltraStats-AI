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
| `AUTO_STATS_MAX_PER_SYNC` | `2` | Estatísticas finais API-Football por ciclo |
| `AUTO_LINEUPS_MAX_PER_SYNC` | `1` | Escalações API-Football por ciclo |
| `SYNC_INTERVAL_MINUTES` | `360` | Ciclo multifonte completo |
| `LIVE_SYNC_INTERVAL_MINUTES` | `30` | Ciclo leve API-Football/Sportmonks ao vivo |

Os intervalos acima mantêm margem dentro da cota gratuita da API-Football.
O ciclo ao vivo consulta apenas fontes com essa capacidade. Provedores de
odds, resultados atrasados e dados históricos continuam no ciclo completo,
sem chamadas artificiais a endpoints que eles não oferecem.

Uma resposta HTTP 200 da API-Football que contenha `errors` é tratada como
falha de provider, inclusive quando a cota diária termina. Nesse cenário o
Sportmonks continua sendo consultado e a execução fica degradada, não
falsamente saudável.

Coleta bruta, fusão, previsões, estatísticas e inteligência usam limites
transacionais separados. Uma falha do modelo não desfaz partidas ou placares
que já foram coletados.

## Recuperação

Os jobs são idempotentes. Após falha de provider, aguarde o próximo ciclo ou
execute uma sincronização manual pelo console legado. Não remova payloads
brutos: eles são necessários para auditoria e reprocessamento.

Para confirmar a atualização ao vivo, verifique a execução mais recente com
`source=multi_provider_live`, a disponibilidade individual dos providers em
`/api/v1/health` e `freshness.latest_live` em
`/api/v1/maturity/status`. Zero partidas é válido quando todas as fontes
disponíveis responderem sem observações; não é válido quando a cota ou uma
falha de rede estiver mascarada.
