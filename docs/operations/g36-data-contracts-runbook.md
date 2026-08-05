# G36 — contratos de dados, odds e identidade

Implementação concluída em 03/08/2026.

## Contrato versionado

`g36-v1` separa numerador e denominador bruto, elegível e realmente coberto pelo
provedor. As contagens são persistidas em `operational_metrics`, com versão,
capacidade, janela e papel (`numerator`/`denominator`). O catálogo-alvo lista,
por competição, fixtures, resultados, odds, escalações, jogadores, eventos e
estatísticas.

Estados de capacidade: `available`, `stale` e `unavailable`. Odds usam SLA por
horizonte: 10 minutos ao vivo; 2 horas até 6h do início; 8 horas até 48h; 48
horas para partidas mais distantes. Uma fixture conhecida não é tratada como
coberta por odds sem evidência temporal do provedor.

## Integridade

- identidade de competição inclui país; ligas homônimas de países diferentes
  não compartilham competição nem candidatos de partida;
- snapshots preservam abertura e movimento; `odds.is_closing` preserva closing;
- `g36-odds-v1` recusa provedor, bookmaker, mercado ou seleção vazios, partida
  inválida, preço fora de 1.001–1000 e timestamp futuro;
- rejeições entram idempotentemente em `data_quarantine` e
  `data_quality_incidents`, com motivo verificável;
- o pipeline de identidade oferece reprocessamento e resolução da quarentena.

## Painel e priorização

A Visão técnica apresenta gates, frescor por capacidade, causas de ausência,
quarentena, erro amostrado de identidade e requisições por entidade útil.
Lacunas são ordenadas por impacto: odds/EV, estatísticas/features e depois
escalações/jogadores.

## Evidência observada

Aceite final de 04/08/2026: estatísticas elegíveis 100%, odds frescas 85,80%,
previsões 94,80%, dois snapshots 98,77% e identidade com zero erro em 2.000
decisões. Todos os cinco gates retornaram `true`. O provedor comprovava cobertura
de odds para 162 partidas, 139 delas frescas segundo o horizonte, e 23 estavam
vencidas. As 391 fixtures sem evidência de cobertura permanecem explicitamente
fora do denominador do provedor e visíveis como causa.

O contrato isolou 481 observações com `decimal_odds_out_of_range`; nenhuma foi
associada ao modelo canônico. Isso é evidência de funcionamento da quarentena,
não perda de registros. Um refresh integral anterior adicionou cerca de 52 mil
snapshots, durou 798,65s e foi corretamente marcado como violação do SLO de
300s.

Aceite operacional:

```powershell
docker exec ultrastats-g16-backend-1 python -c "from app.database.session import SessionLocal; from app.services.maturity_service import MaturityService; s=SessionLocal(); print(MaturityService(s).report()['data_contracts']['gates']); s.close()"
```

Todos os gates retornaram `true` no aceite. A consulta não altera dados.
