# Ciclo operacional de estatística, análise e aprendizagem

## Coleta pós-jogo

A fila consulta partidas finalizadas sem estatísticas nos últimos 14 dias. Cada
execução:

1. prioriza partidas com apostas pendentes;
2. resolve o identificador da API-Football pela identidade canônica;
3. tenta até cinco partidas;
4. registra `received`, `empty` ou `failed`;
5. continua a fila mesmo quando uma resposta é vazia;
6. aguarda 12 horas antes de tentar novamente a mesma partida sem dados.

Esses valores são configuráveis por `AUTO_STATS_MAX_PER_SYNC`,
`AUTO_STATS_LOOKBACK_DAYS` e `AUTO_STATS_RETRY_HOURS`.

## Aprendizagem

Quando uma estatística é persistida, o ciclo automático:

- liquida apostas simples e múltiplas;
- audita todas as previsões da partida;
- calcula o erro de Brier;
- recalibra probabilidades com suavização bayesiana após amostra suficiente;
- atualiza ratings ofensivo, defensivo, de gols, cartões e escanteios;
- recalcula as previsões das partidas ativas;
- cria um dataset imutável;
- executa backtest e os gates de validação;
- materializa oportunidades de recomendação.

Uma nova versão não é considerada aprovada quando possui menos de 20 resultados,
Brier Score acima de 0,30 ou erro de calibração acima de 0,20.

## Recomendações

Cada recomendação persistida informa probabilidade, odds, valor esperado,
confiança, risco, motivos de bloqueio e explicações. Partidas finalizadas não
participam da consulta. Uma oportunidade só é acionável quando passa pelos
critérios persistidos; previsões sem odds continuam visíveis como pistas do
modelo, não como apostas de valor. Evidência baixa é apresentada como alerta
e mantém a classificação de risco alta, mas não bloqueia sozinha uma
oportunidade com odds conciliadas e valor esperado positivo.

## Observabilidade

- `GET /api/v1/health` inclui o bloco `intelligence`;
- `GET /api/v1/intelligence/status` expõe cobertura estatística, auditorias,
  datasets, validação e recomendações;
- `GET /api/v1/recommendations` apresenta motivos de bloqueio e score.
