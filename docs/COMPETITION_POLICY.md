# Política de competições

O UltraStats separa as competições em três grupos:

- **Núcleo:** Série A e Série B do Brasil, Copa do Brasil, Libertadores, Sul-Americana,
  Premier League, La Liga, Champions League, Europa League, Bundesliga,
  Serie A italiana, Ligue 1, Eredivisie e Primeira Liga.
- **Seleções:** Copa do Mundo e eliminatórias, Copa América, Eurocopa,
  UEFA Nations League, Copa Africana de Nações, Copa da Ásia, Copa Ouro
  e CONCACAF Nations League.
- **Observação:** demais competições podem ser coletadas e exibidas, mas
  não geram novas previsões nem alimentam o aprendizado operacional.

Aliases dos diferentes provedores são convertidos para códigos canônicos.
As métricas devem ser acompanhadas por competição e mercado antes de uma
seleção ser promovida a recomendação segura. A disponibilidade efetiva
continua limitada à cobertura e à cota gratuita de cada provedor.

## Promoção automática

Competições em **Observação** são avaliadas automaticamente no ciclo de
maturidade. Elas passam primeiro a **Candidata** e são promovidas ao **Núcleo**
quando sustentam, por sete dias, todos os critérios abaixo na janela móvel de
30 dias:

- ao menos 20 partidas encerradas;
- cobertura estatística mínima de 90%;
- ao menos cinco partidas futuras elegíveis para odds;
- cobertura de odds recentes mínima de 80%.

Os limites são configuráveis pelas variáveis `AUTO_CORE_*`. Competições do
catálogo fixo não participam dessa avaliação e mantêm seu grupo original. Uma
promoção concluída não sofre rebaixamento automático por uma oscilação
temporária; o estado e as métricas ficam persistidos em `competitions` para
auditoria.
