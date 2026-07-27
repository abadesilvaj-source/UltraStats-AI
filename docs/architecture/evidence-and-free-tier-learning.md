# Evidência e aprendizado dentro das cotas gratuitas

## Princípio

O número de partidas encerradas não é usado como sinônimo de estatísticas
detalhadas. O ciclo separa três níveis de informação:

1. placar final, suficiente para resultado, gols, dupla chance e mercados
   derivados do placar;
2. ficha estatística, necessária para escanteios, cartões, finalizações,
   impedimentos, posse e xG;
3. escalações e odds, usadas como evidência complementar, nunca como única
   medida de maturidade.

## Aprendizado incremental

`AUTO_SCORE_LEARNING_MAX_PER_SYNC` limita quantas partidas finalizadas são
revisitadas em cada sincronização. A busca seleciona somente partidas com
previsões ainda não auditadas, permitindo avançar no histórico sem repetir
trabalho e sem consumir chamadas externas.

Partidas sem ficha detalhada não geram resultados artificiais para mercados de
cartões ou escanteios. Esses mercados permanecem sem auditoria até que uma fonte
compatível entregue os dados.

## Evidência por mercado

O nível de evidência de cada previsão combina:

- amostras auditadas daquele mercado;
- histórico anterior das duas equipes;
- partidas anteriores com estatísticas detalhadas;
- quantidade de casas com odds para a partida;
- cobertura e confirmação das escalações.

O resultado é classificado como baixo, médio ou alto. Assim, uma escalação
isolada não transforma uma previsão sem histórico em evidência alta, e mercados
com dados históricos suficientes podem amadurecer mesmo quando uma escalação
ainda não foi publicada.

## Neutralidade dos provedores

API-Football e Sportmonks podem fornecer estatísticas e escalações conforme a
cobertura de seus planos. Football-Data, Football-Data.co.uk, TheSportsDB,
OpenLigaDB, StatsBomb e The Odds API continuam contribuindo nos campos que
realmente oferecem.

O relatório do dataset registra todos os recursos observados por provedor com o
papel `equal_contributor`. A fusão escolhe valores por consenso e recência do
campo, sem peso fixo por marca.

Quando um provedor informa indisponibilidade ou esgotamento de cota, nenhum
endpoint detalhado desse provedor é chamado novamente no mesmo ciclo. Os demais
estágios continuam operando de forma degradada.

## Validação do modelo

A validação exige no mínimo `MODEL_MIN_GLOBAL_SAMPLES` auditorias e usa:

- Brier Score;
- Brier recente em janela walk-forward;
- Expected Calibration Error em dez faixas;
- detecção de drift;
- métricas separadas por mercado.

`MODEL_MAX_RECENT_BRIER` define o limite para o desempenho recente. Uma
recomendação pode continuar visível quando o modelo não passa no gate, mas não
é marcada como segura.

Cada mercado também possui seu próprio gate, configurado por
`MODEL_MIN_MARKET_SAMPLES`, `MODEL_MAX_MARKET_BRIER` e
`MODEL_MAX_MARKET_CALIBRATION_ERROR`. O modelo global aprovado não autoriza
automaticamente um mercado com poucas amostras ou desempenho ruim.
