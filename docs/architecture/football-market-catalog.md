# Catálogo de mercados de futebol

O UltraStats AI mantém um catálogo dinâmico alinhado às famílias de
mercados encontradas em casas como a Betano. A disponibilidade concreta
continua variando por partida, competição, momento e provedor.

## Mercados modelados automaticamente

- resultado da partida, chance dupla e empate anula;
- ambas as equipes marcam, clean sheet e ímpar/par;
- totais de gols e totais de gols por equipe;
- total exato de gols e placar exato;
- totais de escanteios e escanteios por equipe;
- totais de cartões e cartões por equipe.

As linhas são geradas programaticamente. O catálogo atual possui 125
mercados e produz 165 seleções preditivas por partida. Probabilidades de
gols e placares usam a distribuição de Poisson calibrada; escanteios e
cartões usam as taxas contextuais atualizadas pelo pipeline de
aprendizado.

## Mercados externos ou especiais

Mercados de jogadores, períodos específicos, combinações promocionais e
outros mercados que não possuam insumos estruturados nas APIs não recebem
probabilidade inventada. Eles podem ser incluídos manualmente no bilhete,
com nome da seleção e odd da casa escolhida. O sistema:

1. identifica o mercado como sem vínculo local;
2. permite concluir o bilhete;
3. persiste o nome e a odd informada;
4. mantém o alerta de previsão ausente;
5. não usa esse registro para treinar um alvo incompatível.

## Liquidação

Os mercados modelados têm regras automáticas para placar, totais, chance
dupla, empate anula, ambas marcam, clean sheet, escanteios e cartões.
Mercados especiais manuais exigem confirmação manual caso o dado de
liquidação não esteja disponível nos provedores.

## Concorrência e desempenho

A criação do catálogo é idempotente e protegida contra execuções
simultâneas do scheduler e de operações manuais. A consulta de detalhes
calcula recomendações somente para a partida aberta, evitando varrer o
catálogo de todas as partidas em cada navegação.
