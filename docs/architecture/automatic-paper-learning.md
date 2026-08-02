# Paper trading e aprendizado automático

## Objetivo

O modo `paper_only` transforma recomendações seguras em apostas fictícias,
acompanha o preço até o início da partida, liquida pelo resultado oficial e
produz evidência para calibração. Ele nunca consulta nem altera bancas,
transações ou bilhetes de usuários.

## Fluxo

1. A cada cinco minutos, o scheduler lê recomendações seguras com odds válidas.
2. Uma restrição única por `opportunity_id` garante idempotência após reinício.
3. O stake sintético usa Kelly fracionado com teto de 1%, reduzido por risco.
4. Após o status final, o mesmo avaliador de mercados dos bilhetes reais liquida
   o registro fictício.
5. A última odd anterior ao kickoff calcula CLV; ROI, Brier e drawdown são
   agregados globalmente e por competição/mercado.
6. Só segmentos com ao menos 100 liquidações ficam elegíveis para atualização
   de política. O modelo só retreina a cada 100 novos resultados.

## Proteções metodológicas

- A recomendação e suas features são congeladas antes do jogo.
- O resultado da aposta governa seleção, risco e calibração; o treinamento do
  preditor usa o placar posterior e as features temporais, sem duplicar rótulos.
- Uma versão candidata precisa melhorar pelo menos 1% sobre o baseline e ter
  intervalo de confiança de 95% inteiramente positivo.
- Mercados sem ganho comprovado, como um eventual Over 2.5 abaixo de 1%,
  permanecem no baseline e continuam sendo medidos em shadow mode.
- Alto risco é simulado com stake reduzido e permanece visível para revisão.

## Operação

- `GET /api/v1/paper-trading` expõe saldo sintético, métricas e apostas recentes.
- `PAPER_TRADING_ENABLED=false` interrompe novos ciclos sem apagar histórico.
- Compactação fica desligada por padrão e exige backup verificado nos últimos
  sete dias. Registros de paper trading e oportunidades vinculadas são protegidos.

Este mecanismo avalia recomendações; ele não garante lucro nem deve ser tratado
como autorização para apostas reais.
