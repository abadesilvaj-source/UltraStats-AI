# Paper trading e aprendizado automático

## Objetivo

O modo `paper_only` transforma recomendações seguras em apostas fictícias,
acompanha o preço até o início da partida, liquida pelo resultado oficial e
produz evidência para calibração. Ele nunca consulta nem altera bancas,
transações ou bilhetes de usuários.

## Fluxo

1. A cada cinco minutos, o scheduler lê recomendações seguras com odds válidas.
2. Uma restrição única por `opportunity_id` garante idempotência após reinício.
   Reavaliações do mesmo jogo, mercado e seleção são consolidadas em uma única
   aposta fictícia por dia, evitando duplicidade estatística intradiária.
3. A política `automatic-shadow-v2` registra toda recomendação segura, mas só
   executa stake quando ela é `high_confidence`, tem limite inferior de
   probabilidade de ao menos 80%, odd entre 1,60 e 2,99 e kickoff em até 6 horas.
   As demais viram `shadow_observation`, com stake zero.
4. Após o status final, o mesmo avaliador de mercados dos bilhetes reais liquida
   o registro fictício.
5. A última odd anterior ao kickoff calcula CLV; ROI, Brier e drawdown são
   agregados globalmente e por competição/mercado.
6. Só segmentos com ao menos 100 liquidações, ROI positivo, exposição real e
   Brier de no máximo 0,20 ficam elegíveis para atualização de política. O
   modelo só retreina a cada 100 novos resultados.

## Política seletiva v2

- Exposição pendente é reservada antes de uma nova decisão.
- A soma diária é limitada a 3% da banca corrente e cada partida a 1%.
- Kelly usa 10% da fração calculada, com teto de 0,5% por decisão.
- Placar exato, linhas extremas de gols e mercados de escanteios ficam somente
  em observação por padrão.
- Cada carteira é isolada na criação, liquidação, métricas e interface. A v1
  permanece arquivada e liquidável, sem contaminar o saldo ou a avaliação v2.
- Probabilidade de execução usa o limite inferior do intervalo, e não a
  estimativa pontual mais otimista.

## Proteções metodológicas

- A recomendação e suas features são congeladas antes do jogo.
- O resultado da aposta governa seleção, risco e calibração; o treinamento do
  preditor usa o placar posterior e as features temporais, sem duplicar rótulos.
- Uma versão candidata precisa melhorar pelo menos 1% sobre o baseline e ter
  intervalo de confiança de 95% inteiramente positivo.
- Mercados sem ganho comprovado, como um eventual Over 2.5 abaixo de 1%,
  permanecem no baseline e continuam sendo medidos em shadow mode.
- Recomendações fora dos gates permanecem visíveis e são liquidadas com stake
  zero, produzindo evidência sem comprometer a banca fictícia.

## O que o aprendizado automático não resolve sozinho

Mais partidas reduzem variância, mas não corrigem dados atrasados, identidade
incorreta de competições, odds desatualizadas, leakage temporal ou uma função
objetivo inadequada. A promoção exige validação prospectiva, calibração por
mercado/competição/faixa de odds, CLV, Brier, ROI e controle de drawdown. O alvo
operacional é selecionar poucas recomendações bem calibradas e com valor; taxa
de acerto isolada não é suficiente e 100% não é uma meta estatisticamente
realista.

## Operação

- `GET /api/v1/paper-trading` expõe saldo sintético, métricas e apostas recentes.
- Em **Visão técnica → Apostas fictícias**, a interface mostra criações do dia,
  pendentes, liquidadas e o resultado de cada seleção. A tela consulta novamente
  a API a cada 30 segundos.
- A criação e a reconciliação executam a cada cinco minutos durante todos os
  dias. Quando o resultado oficial chega, a liquidação fictícia ocorre na mesma
  transação que encerra apostas reais; a rotina periódica cobre interrupções e
  resultados importados posteriormente.
- `PAPER_TRADING_ENABLED=false` interrompe novos ciclos sem apagar histórico.
- Compactação fica desligada por padrão e exige backup verificado nos últimos
  sete dias. Registros de paper trading e oportunidades vinculadas são protegidos.

Este mecanismo avalia recomendações; ele não garante lucro nem deve ser tratado
como autorização para apostas reais.
