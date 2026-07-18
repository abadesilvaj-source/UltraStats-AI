# UltraStats AI — Registro de Decisões Arquiteturais

Este documento registra decisões consideradas oficiais para o produto.

---

## ADR-001 — Produto exclusivamente de futebol

Status: Aprovada

O UltraStats AI será especializado exclusivamente em futebol.

Não serão criadas abstrações para basquete, tênis, automobilismo, eSports ou
outros esportes.

Consequência:

Os modelos poderão utilizar conceitos específicos de futebol, como equipes,
jogadores, treinadores, árbitros, escalações, formações, gols, escanteios e
cartões.

---

## ADR-002 — Arquitetura com múltiplos provedores

Status: Aprovada

O sistema utilizará múltiplas fontes de dados.

Nenhum provedor será considerado dono exclusivo da verdade.

Consequência:

Será necessário implementar normalização, resolução de entidades, fusão,
confiança e rastreabilidade.

---

## ADR-003 — Armazenamento de payload bruto

Status: Aprovada

Respostas recebidas dos provedores serão preservadas antes do processamento.

Consequência:

Será possível reprocessar dados, investigar erros e evoluir regras de fusão sem
realizar novamente todas as chamadas externas.

---

## ADR-004 — Separação entre modelo normalizado e modelo canônico

Status: Aprovada

Modelos normalizados representarão dados adaptados de um provedor.

Modelos canônicos representarão a visão consolidada do UltraStats AI.

Consequência:

Detalhes específicos de APIs não poderão atravessar para os módulos
estatísticos e preditivos.

---

## ADR-005 — Mercados representados de forma flexível

Status: Aprovada

Não será criada uma classe exclusiva para cada mercado.

Os mercados serão representados por composição de tipo, período, escopo,
participante, linha e seleção.

Consequência:

O sistema poderá representar grande quantidade de mercados sem crescimento
descontrolado do código.

---

## ADR-006 — Histórico imutável de previsões

Status: Aprovada

Toda previsão será registrada com dados, odds, modelo e configuração existentes
no momento da geração.

Consequência:

Previsões antigas não poderão ser sobrescritas com informações futuras.

---

## ADR-007 — Probabilidade e risco são conceitos diferentes

Status: Aprovada

A probabilidade representa a estimativa de ocorrência de um evento.

O risco representa a incerteza e exposição associadas à oportunidade.

Consequência:

Uma seleção com probabilidade elevada não será automaticamente classificada
como conservadora.

---

## ADR-008 — Perfil do usuário não altera probabilidades

Status: Aprovada

Preferências e perfil de risco do usuário não alteram as probabilidades
objetivas calculadas.

Consequência:

O perfil influencia filtros, apresentação, stakes e recomendações, mas não o
modelo probabilístico original.

---

## ADR-009 — Closing Line Value fora do escopo

Status: Rejeitada para o produto

O UltraStats AI não implementará Closing Line Value.

Consequência:

Não serão criados modelos, métricas ou telas dedicadas a CLV.

---

## ADR-010 — Canais de notificação limitados

Status: Aprovada

Os canais oficiais serão:

- aplicação;
- push notification.

Não serão utilizados e-mail, Telegram, WhatsApp ou Discord.

---

## ADR-011 — Interface simples e avançada

Status: Aprovada

O produto terá dois níveis de visualização.

O modo simples será direcionado a usuários que desejam objetividade.

O modo avançado exibirá detalhes técnicos, estatísticos e preditivos.

---

## ADR-012 — Indicadores de atualização discretos

Status: Aprovada

Informações temporais deverão estar disponíveis sem poluir a interface.

Consequência:

Detalhes poderão ser exibidos por texto reduzido, ícone, tooltip ou área
expandida.

---

## ADR-013 — Recomendações explicáveis

Status: Aprovada

Toda recomendação deverá apresentar os principais fatores que contribuíram
para sua geração.

Consequência:

O sistema não apresentará apenas uma seleção e uma porcentagem sem contexto.

---

## ADR-014 — Backtesting sem vazamento temporal

Status: Aprovada

Backtests deverão utilizar exclusivamente dados e odds conhecidos no momento
histórico analisado.

Consequência:

Dados futuros não poderão participar do treinamento ou simulação do passado.

---

## ADR-015 — Suporte futuro a análises ao vivo

Status: Aprovada

O produto final incluirá probabilidades e recomendações durante partidas.

Consequência:

A arquitetura deverá prever snapshots temporais, eventos ao vivo e
reprocessamento incremental.

---

## ADR-016 — Gestão de banca integrada

Status: Aprovada

O sistema incluirá banca, stakes, exposição, limites, lucro, prejuízo, ROI,
yield e drawdown.

Consequência:

Dados financeiros do usuário deverão ter segurança e controle de acesso
reforçados.

---

## ADR-017 — Sem garantia de resultado

Status: Aprovada

Probabilidades e recomendações serão apresentadas como estimativas.

Consequência:

A interface deverá incluir comunicação de risco e recursos de jogo
responsável.