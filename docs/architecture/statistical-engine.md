# Motor Estatístico

## Objetivo

O Motor Estatístico transforma partidas históricas em snapshots temporais
imutáveis para consumo pelos modelos preditivos. Apenas partidas anteriores ao
`reference_at` participam do cálculo, prevenindo data leakage.

## Amostras

Cada `MatchSample` contém gols, xG, pontos, mando, força do adversário,
competição, treinador, árbitro e impacto de ausências. Valores negativos e
pontuações incompatíveis com futebol são rejeitados.

## Indicadores

- forma recente ponderada;
- médias de gols e xG a favor e contra;
- performance em casa e fora;
- força do calendário;
- impacto médio de ausências;
- variância, mínimo e máximo;
- tendências lineares;
- forma contextual por competição, treinador e árbitro;
- probabilidades de gols pela distribuição de Poisson.

Pesos exponenciais tornam partidas recentes mais relevantes. O tamanho efetivo
da amostra considera a concentração desses pesos; a confiabilidade é limitada
ao intervalo de zero a um em relação à amostra-alvo.

## Persistência

`StatisticalSnapshotStore` grava um snapshot por equipe e instante de
referência, com atualização idempotente. A migration `a18c8f40a004` cria
`statistical_snapshots`, sua constraint de unicidade e índice temporal.

## Validação

A G8 foi concluída com 2.464 testes e 100% de cobertura de linhas e branches.
Upgrade e downgrade da migration são executados em banco descartável.
