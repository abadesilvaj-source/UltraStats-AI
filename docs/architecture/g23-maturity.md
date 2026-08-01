# G23 — Maturidade operacional e preditiva

## Objetivo

A G23 conecta os componentes já existentes de fusão, escalações, validação,
risco, múltiplas e motor ao vivo ao ciclo operacional executado pelo scheduler.
O objetivo não é aumentar artificialmente a quantidade de recomendações, mas
separar previsões exploratórias de oportunidades utilizáveis.

## Qualidade e cobertura

O `MaturityService` calcula, em janela móvel de 14 dias:

- cobertura de estatísticas para partidas encerradas;
- cobertura de odds, previsões e escalações para partidas ativas;
- atualidade de odds e snapshots ao vivo;
- disponibilidade e latência dos provedores;
- índice consolidado de qualidade;
- alertas de cobertura ou feeds vencidos.

Os resultados são persistidos em `operational_metrics` e
`operational_alerts`. O diagnóstico atual está disponível em
`GET /api/v1/maturity/status` e na tela **Sistema**.

## Escalações e jogadores

O coletor utiliza todas as fontes habilitadas que oferecem escalações.
API-Football continua sendo normalizada para a interface e Sportmonks é
armazenada como fonte complementar. O modelo operacional considera:

- presença das duas escalações;
- confirmação de onze titulares;
- continuidade dos titulares em relação à escalação anterior;
- diferença de continuidade na projeção de gols;
- evidência, confiança, confluência e risco resultantes.

Sem dados individuais suficientes, o sistema não inventa impacto de jogador:
ausência de histórico permanece indicada como baixa evidência.

As estatísticas finais usam API-Football como primeira tentativa e Sportmonks
como complemento para partidas conciliadas. A normalização Sportmonks cobre
placar, escanteios, cartões, chutes, impedimentos, posse e xG quando esses
campos estiverem disponíveis no plano contratado.

## Validação temporal e modelos

Cada novo dataset de auditorias gera:

- métricas gerais e por mercado;
- divisão temporal 70/30 para validação walk-forward;
- Brier Score e erro de calibração;
- detecção de drift pela deterioração do Brier recente;
- modelo campeão e challenger registrados no catálogo;
- gate automático que impede recomendações quando o modelo falha.

O challenger é promovível apenas quando obtiver qualidade temporal superior ao
campeão. O limiar de drift pode ser configurado por
`MODEL_DRIFT_BRIER_DELTA`.

## Recomendações e risco

Cada oportunidade passa a registrar:

- intervalo de incerteza de 95%;
- probabilidade conservadora;
- EV conservador;
- idade da odd;
- amostra do mercado;
- Kelly fracionado em 25%;
- alertas e motivos de bloqueio.

Uma oportunidade acionável exige modelo aprovado, odd recente e EV conservador
acima de `RECOMMENDATION_MIN_CONSERVATIVE_EV`. A validade da odd é controlada
por `ODDS_MAX_AGE_HOURS`.

## Múltiplas

O endpoint `POST /api/v1/bet-slips/analyze` calcula:

- probabilidade conjunta;
- penalidade por pernas correlacionadas;
- EV conjunto;
- limite sugerido da banca;
- alertas de quantidade, correlação ou previsões ausentes.

São permitidos até dois mercados diferentes da mesma partida. Seleções
duplicadas, mercados contraditórios e mais de duas pernas correlacionadas são
bloqueados.

## Motor ao vivo

O ciclo restaura o último snapshot antes de processar novos eventos. Revisões,
placar e minuto não voltam ao estado inicial após uma sincronização. Eventos
duplicados são ignorados e o identificador incorpora minuto e placar. Um novo
snapshot só é salvo quando há mudança real de revisão.

## Configuração

```env
RECOMMENDATION_MIN_CONSERVATIVE_EV=0.02
ODDS_MAX_AGE_HOURS=6
MODEL_DRIFT_BRIER_DELTA=0.08
```
