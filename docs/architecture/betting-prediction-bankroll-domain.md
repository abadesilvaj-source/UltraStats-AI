# Betting, Prediction and Bankroll Domains

## 1. Estado

A G5.9 conclui o modelo canônico de mercados, previsões, recomendações e gestão
financeira. Os contextos não dependem de ORM, providers ou dos serviços legados
em `app`.

## 2. Betting

`Bookmaker` representa a identidade de uma casa de apostas.

`BettingMarket` pertence a uma partida por `MatchId` e contém uma ou mais
`BettingSelection`. O agregado de mercado garante ownership, chaves únicas e
identidades únicas. Linhas são opcionais para permitir mercados sem handicap ou
total.

`OddsSnapshot` preserva uma observação imutável de odd, relacionando bookmaker,
mercado, seleção e instante UTC. Novas observações geram novos snapshots.

## 3. Prediction

`Prediction` representa uma execução de modelo identificada por
`PredictionModelId` e versão textual. Ela controla:

- `PredictionResult`, com mercado, seleção, probabilidade e odd justa;
- `PredictionExplanation`, com fator, impacto e narrativa.

A odd justa deve corresponder ao inverso da probabilidade. Uma previsão
concluída exige resultado e não aceita novos resultados ou explicações; uma nova
execução deve produzir outra identidade.

## 4. Recommendation

`Recommendation` referencia uma previsão e seu resultado. Ela preserva odd
oferecida, probabilidade, valor esperado, confiança, percentual sugerido de
stake, risco e estado.

O valor esperado é validado pela fórmula:

```text
EV = probabilidade × odd oferecida − 1
```

Isso impede divergência entre a recomendação publicada e os dados que a
originaram.

## 5. Bankroll

`Bankroll` é a raiz financeira. O saldo é derivado do saldo inicial e do ledger
imutável de `BankrollTransaction`; ele nunca é ajustado silenciosamente.

O agregado controla:

- `Bet`, com bookmaker, stake, odd combinada e estado;
- `BetLeg`, com mercado, seleção e odd registrada;
- `Settlement`, com resultado, retorno, regra e instante.

Uma aposta só pode ser registrada com saldo suficiente e uma movimentação
`BET_STAKE` equivalente. A odd combinada deve corresponder ao produto das odds
das pernas.

A liquidação exige uma aposta conhecida e ainda não liquidada. Retornos
positivos exigem uma movimentação `BET_RETURN` equivalente; resultados sem
retorno não permitem crédito. O estado da aposta, o saldo e a exposição aberta
são derivados de registros auditáveis.

## 6. Precisão e fronteiras

Valores financeiros utilizam `Money`; odds usam `Odds`; probabilidades usam
`Probability`; percentuais usam `Percentage`. Todos são decimais imutáveis.

As relações entre Match, mercados, previsões e banca ocorrem exclusivamente por
identificadores canônicos. Nenhum desses agregados controla o ciclo de vida de
outro contexto.

## 7. Validação

Os testes ficam em `tests/unit/domain/betting`,
`tests/unit/domain/prediction` e `tests/unit/domain/bankroll`. A suíte padrão
mantém a exigência global de 100% de linhas e branches. A validação final da
G5.9 concluiu 2.423 testes, 4.807 statements e 1.456 branches.
