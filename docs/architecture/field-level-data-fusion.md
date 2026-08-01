# Fusão de dados por campo

## Objetivo

Remover a dependência de uma API dominante sem assumir que todas as fontes
oferecem os mesmos recursos. A unidade de autoridade passa a ser o campo, não o
provedor inteiro.

## Fluxo

1. Os coletores preservam todo payload bruto e sua impressão digital.
2. Adaptadores convertem cada formato em uma contribuição de partida.
3. A resolução de identidade procura vínculo persistido ou compara horário,
   mandante e visitante.
4. Uma partida ausente pode ser criada por fonte secundária.
5. O motor escolhe cada campo por consenso, qualidade e atualidade.
6. Valores, procedência e conflitos são armazenados em `fusion_results`.
7. Resultados históricos do Football-Data.co.uk atualizam ratings de ataque,
   defesa e gols uma única vez por dataset.
8. Previsões são recalculadas depois do enriquecimento.

## Autoridade inicial

| Fonte | Qualidade-base |
|---|---:|
| API-Football | 0,96 |
| football-data.org | 0,92 |
| OpenLigaDB | 0,84 |
| Football-Data.co.uk | 0,78 |

Consenso de duas ou mais fontes supera prioridade simples para placar e status.
Um status terminal também prevalece sobre um registro antigo marcado como ao
vivo.

## Segurança

- correspondências abaixo de 0,78 não são unidas automaticamente;
- mandante/visitante invertidos recebem penalidade;
- datasets históricos não sobrescrevem partidas fora da janela operacional;
- um fingerprint impede reaplicação dos mesmos dados de treinamento;
- divergências permanecem auditáveis e nunca são descartadas silenciosamente.
