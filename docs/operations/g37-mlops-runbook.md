# G37 — Laboratório estatístico, ML e MLOps

Atualizado em 4 de agosto de 2026.

## Objetivo

Impedir que um modelo seja promovido por ajuste retrospectivo ou por uma média
global que esconda segmentos ruins. O fluxo preserva o modelo campeão e limita
qualquer desafiante aprovado a 5% de canário.

## Artefatos auditáveis

- `training_datasets`: consulta lógica, cutoff UTC, features, alvos e SHA-256;
- `predictive_models.parameters.model_card`: amostra, validade, limitações e
  segmentos proibidos;
- `model_backtests`: gates G37, benchmark de mercado, ablações e drift;
- `model_deployments`: campeão, shadow/canário, tráfego e validade;
- `prediction_explanations.decision.provenance`: modelo, dataset, cutoff,
  feature set e qualidade observada.

## Validação

O treino usa ordem cronológica 70/15/15. O bloco intermediário calibra a
temperatura; o teste final nunca seleciona hiperparâmetros nem calibra o modelo.
O relatório walk-forward expande a janela e explicita temporada, competição,
família de mercado e horizonte. Resultados com pouca amostra ou drift continuam
visíveis e não entram na média de aprovação.

Baselines obrigatórios: Poisson para gols/placar, Elo para resultado e frequência
empírica para todos os alvos. Quando houver odds liquidadas, o Brier do modelo é
comparado à probabilidade implícita sem margem disponível.

## Promoção segura

Um desafiante somente entra em canário se estiver aprovado, melhorar o baseline
fora da amostra e possuir limite inferior do intervalo de 95% acima de zero.
Isso não o promove a campeão: o canário recebe 5%, tem validade de 30 dias e o
campeão continua ativo.

## Rollback

`MLOpsGovernanceService.rollback(<família>)` devolve todo canário da família a
`shadow`, registra o instante no gate e mantém o campeão ativo. Nenhum modelo,
dataset, backtest ou previsão é apagado. Meta operacional: menos de dois minutos.

## Gates de aceite

1. ganho fora da amostra com intervalo aceitável;
2. segmentos limitados ou em drift explicitamente reportados;
3. checksum e cutoff reproduzíveis;
4. rollback preservando o campeão;
5. proveniência completa em novas previsões e backfill das existentes.

O painel **Modelos e aprendizado** mostra o estado dos gates. Um gate pendente é
um bloqueio de promoção, não uma autorização para reduzir as salvaguardas.
