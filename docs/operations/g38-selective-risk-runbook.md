# G38 — Recomendação seletiva, paper trading e risco

Atualizado em 4 de agosto de 2026.

## Princípio

A G38 não tenta maximizar o número de apostas. Ela converte somente previsões
com preço recente, incerteza aceitável e exposição disponível em execução
fictícia. O restante permanece como `shadow_observation`, com stake zero.

## Reserva e concorrência

A carteira ativa é bloqueada transacionalmente antes do cálculo de exposição.
Cada oportunidade é idempotente e os limites são recalculados dentro da mesma
transação. Padrões da política v2:

- 3% da carteira por dia;
- 1% por partida;
- 1,5% por competição;
- 1,5% por mercado;
- 1% por grupo de correlação.

O menor saldo disponível entre esses limites determina a stake final. Valores
abaixo de R$ 0,01 viram observação sem exposição.

## Preço e validade

A execução exige odd entre 1,60 e 2,99, idade máxima de 30 minutos e prazo
anterior ao início da partida. A odd mínima específica é calculada como
`1,03 / limite_inferior_da_probabilidade`, incorporando margem conservadora de
3%. O aplicativo exibe odd mínima e instante de expiração.

## Circuit breakers

Novas stakes são bloqueadas quando:

- drawdown da carteira alcança 10%;
- a governança G37 detecta drift de dados;
- a calibração entra em drift;
- a cobertura perde o contrato aprovado.

O bloqueio não apaga previsões nem apostas. As oportunidades continuam em shadow
para diagnóstico e aprendizado sem risco.

## Risco e promoção

Com pelo menos 30 liquidações no segmento competição/mercado, o rótulo de risco
passa a usar a perda observada: baixo até 20%, moderado até 35% e alto acima
disso. Antes da amostra mínima, o rótulo anterior permanece marcado como
provisório.

Um segmento somente pode ser promovido com amostra mínima, ROI positivo, CLV
disponível e não negativo, Brier até 0,20 e circuit breaker fechado. Toda falha
é registrada explicitamente em `promotion_gate_failures`.

## Liquidação e correções

Resultado, placar e estatísticas formam uma assinatura. Se o provedor corrigir o
resultado em até 14 dias, a aposta é reavaliada, a mudança `from/to` é registrada
e a carteira inteira é recalculada a partir do saldo inicial. Void devolve a
stake. Nenhuma evidência anterior é removida.

## Aceite

- testes unitários de limites, stale odds, drawdown, perda, void e correção;
- suíte funcional completa aprovada;
- build web aprovado;
- execução real registra `circuit_breaker`, `cohorts` e limites;
- backend, scheduler, frontend, mobile e PostgreSQL permanecem saudáveis.
