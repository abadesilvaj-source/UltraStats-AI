# Operação API-Football Ultra

## Objetivo

O plano Ultra acelera a coleta sem alterar a neutralidade canônica. Todos os
provedores continuam com peso-base 1.0; cada campo é conciliado por consenso,
recência e qualidade.

## Workers independentes

- `sports_data_sync` (60 min): agenda, fusão e inteligência completa;
- `live_scores_sync` (60 s): placares, eventos, estatísticas e odds ao vivo;
- `statistics_backfill` (10 min): histórico reiniciável de estatísticas e
  jogadores;
- `odds_refresh` (15 min): fixtures e odds em janela móvel de 14 dias.

O backfill e as odds possuem travas próprias. Uma carga histórica demorada não
impede a atualização de uma partida ao vivo.

## Configuração recomendada

```env
LIVE_SYNC_INTERVAL_SECONDS=60
API_FOOTBALL_DAILY_BUDGET=67500
API_FOOTBALL_MIN_REMAINING=10000

BACKFILL_ENABLED=true
BACKFILL_SEPARATE_WORKER=true
BACKFILL_INTERVAL_MINUTES=10
AUTO_BACKFILL_REQUESTS_PER_CYCLE=2500
AUTO_BACKFILL_SEASONS=3

ODDS_SYNC_ENABLED=true
ODDS_SYNC_INTERVAL_MINUTES=15
ODDS_SYNC_WINDOW_DAYS=14
AUTO_TARGETED_ODDS_MAX_PER_SYNC=300
```

O coletor lê os cabeçalhos `x-ratelimit-*`. Tarefas históricas param antes da
reserva diária, deixando capacidade para jogos atuais e ao vivo.

## Backfill e retentativas

O processo descobre temporadas que realmente anunciam estatísticas, prioriza o
catálogo do UltraStats e grava checkpoints por liga/temporada. Respostas vazias
são tentadas novamente após `BACKFILL_EMPTY_RETRY_HOURS`, até
`BACKFILL_MAX_EMPTY_ATTEMPTS`.

Execução manual opcional:

```powershell
python -m scripts.backfill_api_football --seasons 3 --budget 5000
```

## Odds

- respostas paginadas da API-Football são percorridas integralmente;
- coleta em lote por data antecede consultas direcionadas;
- API-Football e The Odds API são promovidas pelo mesmo contrato canônico;
- linhas de total de gols de 0.5 a 5.5 são normalizadas dinamicamente;
- cada preço promovido gera snapshot por provedor, casa, mercado e seleção;
- odds antigas não participam do cálculo de valor esperado;
- snapshots permitem movimento de preço, odd de fechamento e CLV.

## Observabilidade

O relatório de maturidade expõe cobertura elegível, quantidade de snapshots em
14 dias, provedores, casas, mercados e partidas elegíveis ainda sem odds.

## Uso pelos motores

- estatísticas finais alimentam auditoria, calibração e ratings;
- jogadores, lesões e escalações ajustam força e confiança;
- odds reais habilitam valor esperado conservador e Kelly;
- previsões nativas de qualquer provedor permanecem sinais complementares;
- nenhum provedor recebe autoridade fixa sobre os demais.
