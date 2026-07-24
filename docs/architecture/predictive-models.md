# Modelos Preditivos

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
