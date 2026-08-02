# Modelos Preditivos

## Implementação operacional vigente

Além dos contratos canônicos da G9, o pipeline operacional possui o modelo
supervisionado `temporal_logistic`, versão `temporal-logit-v1`, para resultado
da partida, total acima/abaixo de 2,5 gols e ambas as equipes marcam.

As features de forma, ataque, defesa, xG, finalizações no alvo, escanteios,
cartões, descanso e confiabilidade usam somente partidas anteriores ao kickoff.
O conjunto é limitado às 5.000 observações mais recentes e dividido em ordem
temporal: 70% treino, 15% calibração e 15% teste. Padronização usa apenas o
treino; temperature scaling usa apenas o holdout de calibração.

O modelo só é aprovado quando seu log loss no teste supera o baseline. Amostra
insuficiente ou reprovação preservam o baseline sem interromper previsões.

O champion de resultados combina Poisson (45%), Elo (25%) e ML (30%); gols e
BTTS combinam Poisson (65%) e ML (35%). Challengers com maior peso de ML rodam
em shadow. Os pesos serão calibrados fora da amostra na G29.

## Contexto individual de jogadores (G33)

Antes da projeção de Poisson, `PlayerImpactService` calcula um contexto
estritamente temporal usando somente payloads coletados até o instante da
previsão. O índice individual (0–100) combina minutos, amostra, nota, produção
ofensiva e contribuição defensiva, com ponderação específica para goleiros,
defensores, meio-campistas e atacantes.

A força da equipe usa os onze confirmados quando disponíveis. Sem escalação
oficial, usa uma escalação provável formada pelos atletas mais relevantes; com
menos de sete perfis confiáveis, retorna estado `unknown`. Lesões são ponderadas
pela importância do atleta e nunca apenas contadas.

O sinal só altera o xG quando a cobertura conjunta atinge o limiar configurado.
O ajuste é limitado por lado e o pipeline volta ao cálculo coletivo anterior
quando a camada está desligada ou insuficiente. Os forecasts registram o
contexto utilizado, permitindo auditoria e comparação futura.

Parâmetros operacionais:

- `PLAYER_IMPACT_ENABLED` — chave de ativação e rollback imediato;
- `PLAYER_IMPACT_MIN_COVERAGE` — cobertura mínima, padrão 45%;
- `PLAYER_IMPACT_MAX_XG_ADJUSTMENT` — teto absoluto por equipe, padrão 0,12.

## Arquitetura

A G9 utiliza distribuições probabilísticas como contrato comum. Modelos são
identificados por nome, versão, competição e mercado. Seus parâmetros ficam
registrados para reprodução das previsões.

## Mercados

O `PoissonScoreModel` gera uma distribuição de placares e a projeta para:

- 1X2, Double Chance e Draw No Bet;
- Asian e European Handicap;
- Over/Under e Both Teams To Score;
- Team Goals e Halftime;
- First Goal e Last Goal.

`CountMarketModel` atende escanteios, cartões, estatísticas e mercados de
jogadores. Combinações são calculadas por probabilidade condicional.

## Modelagem e avaliação

- ensembles combinam modelos compatíveis com pesos positivos;
- calibração por potência preserva a soma unitária;
- backtests produzem Brier score, log loss, acurácia e erro de calibração;
- Monte Carlo usa seed explícita para reprodutibilidade;
- mudança de regime compara janelas consecutivas;
- explicações preservam as contribuições de xG e diferença de forças.

## Imutabilidade

Uma previsão publicada é única por partida, modelo, versão e mercado. O registry
aceita múltiplas versões sem sobrescrever o histórico. Backtests permanecem
associados à versão avaliada.

## Persistência

A migration `b29d9040b005` cria:

- `predictive_models`;
- `predictive_forecasts`;
- `model_backtests`.

## Validação

A G9 foi concluída com 2.472 testes e 100% de cobertura de linhas e branches,
incluindo upgrade/downgrade, compatibilidade pública, casos extremos
probabilísticos e imutabilidade.
