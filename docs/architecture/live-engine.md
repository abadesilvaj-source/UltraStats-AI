# Motor ao Vivo

## Objetivo

A G13 atualiza o estado, as probabilidades e as recomendações durante uma
partida, preservando idempotência, rastreabilidade e segurança diante de feeds
atrasados ou inconsistentes.

## Fluxo

```text
evento do provider
       |
       v
validação + idempotência + ordenação temporal
       |
       v
placar / relógio / estatísticas / odds
       |
       v
probabilidades + EV + recomendações ao vivo
       |
       v
snapshot revisionado + anomalias + fila push
```

## Eventos e estado

O motor aceita eventos de:

- placar;
- relógio;
- estatística;
- odds;
- suspensão;
- retomada;
- encerramento;
- heartbeat.

Cada evento possui identidade global, partida, instante de ocorrência, instante
de recebimento e payload. Eventos repetidos não alteram o estado. Cada mudança
aceita incrementa a revisão e produz um snapshot imutável.

O estado contém fase, saúde do feed, minuto, placar, estatísticas, odds,
probabilidades, recomendações, anomalias e mensagens push.

## Segurança

As recomendações só existem quando a partida está ao vivo e o feed está
saudável. O motor detecta:

- eventos fora de ordem;
- regressão de placar;
- regressão do relógio;
- saltos anormais de odds;
- eventos atrasados;
- timeout do feed;
- eventos recebidos depois do encerramento.

Regressões, desordem e saltos de odds suspendem automaticamente a partida.
Atrasos moderados colocam o feed em degradação controlada e removem
recomendações. Timeout crítico bloqueia o motor até uma retomada explícita.

## Projeções

Placar e minuto atualizam uma distribuição normalizada para casa, empate e
fora. Odds válidas são comparadas às probabilidades e só geram recomendações
quando o EV mínimo é atendido. Mercados desconhecidos são ignorados com
segurança.

## Persistência e push

A migration reversível `f6d12483f339` cria:

- `live_events`;
- `live_snapshots`;
- `live_anomalies`;
- `live_push_deliveries`.

Eventos são append-only, snapshots são únicos por partida e revisão, anomalias
são auditáveis e mensagens de gol, suspensão, retomada, encerramento e
recomendação entram em uma fila push persistente.

O painel `17_Motor_ao_Vivo.py` mostra partidas, placar, minuto, saúde, fase,
recomendações, anomalias e push pendentes.

## Garantias

A G13 foi concluída com 2.557 testes e 100% de cobertura de linhas e branches.
Os testes cobrem todos os eventos, validações, idempotência, projeções,
recomendações, suspensão, retomada, degradação, anomalias, persistência, fila
push e reversão da migration.
