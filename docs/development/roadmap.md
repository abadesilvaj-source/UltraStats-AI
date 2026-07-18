# UltraStats AI — Roadmap Oficial

## 1. Objetivo

Este documento apresenta a evolução planejada do UltraStats AI.

O roadmap organiza o desenvolvimento em grandes fases, permitindo acompanhar o
que já foi concluído, o que está em andamento e o que ainda será implementado.

O UltraStats AI é uma plataforma focada exclusivamente em futebol, com ênfase em:

- dados esportivos;
- estatística;
- probabilidades;
- odds;
- recomendações;
- gestão de risco;
- auditoria;
- modelos preditivos;
- análise para apostas esportivas.

---

## 2. Visão geral das fases

```text
G1  — Fundação do Projeto
G2  — Persistência e Banco de Dados
G3  — Serviços, Dashboard e Operação
G4  — Arquitetura do Domínio
G5  — Domínio Canônico
G6  — Integração com Providers
G7  — Resolução de Identidade e Data Fusion
G8  — Motor Estatístico
G9  — Modelos Preditivos
G10 — Motor de Recomendações
G11 — Gestão de Risco e Portfólio
G12 — Experiência do Usuário
G13 — Motor ao Vivo
G14 — Produção, Segurança e Escalabilidade
```

---

## 3. G1 — Fundação do Projeto

### Objetivo

Criar a base inicial do UltraStats AI.

### Escopo

- estrutura do projeto;
- ambiente virtual;
- organização de pacotes;
- configuração centralizada;
- variáveis de ambiente;
- logging inicial;
- Git;
- testes iniciais.

### Status

```text
CONCLUÍDO
```

---

## 4. G2 — Persistência e Banco de Dados

### Objetivo

Implementar a persistência dos dados da aplicação.

### Escopo

- PostgreSQL;
- SQLAlchemy;
- SessionLocal;
- modelos iniciais;
- repositories;
- migrations com Alembic;
- integridade de dados;
- testes de persistência;
- auditoria básica.

### Status

```text
CONCLUÍDO
```

---

## 5. G3 — Serviços, Dashboard e Operação

### Objetivo

Criar os fluxos operacionais iniciais da aplicação.

### Escopo

- camada de serviços;
- dashboard em Streamlit;
- criação de bancas;
- movimentações financeiras;
- criação de apostas;
- liquidação de apostas;
- scheduler;
- heartbeat;
- sincronizações;
- logs;
- scripts para Windows;
- Docker;
- Docker Compose;
- provider mock.

### Status

```text
CONCLUÍDO
```

---

## 6. G4 — Arquitetura do Domínio

### Objetivo

Definir a arquitetura conceitual que servirá de base para todo o domínio do
UltraStats AI.

### Subfases

```text
G4.A — Arquitetura do Domínio
G4.B — Arquitetura de Providers
G4.C — Arquitetura de Dados
G4.D — Organização da Documentação
```

### G4.A — Arquitetura do Domínio

#### G4.A.1 — Visão geral do domínio

- definição dos contextos;
- mapa de contexto;
- decisões arquiteturais iniciais.

Status:

```text
CONCLUÍDO
```

#### G4.A.2 — Entidades Centrais do Futebol

- domínio central de futebol;
- mapeamentos de identidade;
- ciclo de vida de partidas;
- ADRs relacionadas.

Status:

```text
CONCLUÍDO
```

#### G4.A.3 — Modelo Canônico do Domínio

- entidades definitivas;
- relacionamentos;
- agregados;
- value objects;
- regras de identidade;
- regras de histórico;
- regras de integridade.

Status:

```text
PRÓXIMO
```

### G4.D — Organização da Documentação

- organização da pasta `docs/`;
- índice principal;
- roadmap;
- changelog;
- documentação técnica;
- simplificação do README da raiz.

Status:

```text
EM ANDAMENTO
```

---

## 7. G5 — Domínio Canônico

### Objetivo

Transformar a arquitetura conceitual em modelos persistentes e regras de
negócio reais.

### Entidades previstas

```text
Country
Competition
Season
Stage
Round
Team
Player
Coach
Referee
Stadium
Match
MatchScheduleHistory
MatchStatusHistory
Formation
Lineup
LineupPlayer
MatchEvent
MatchStatistics
Injury
Suspension
Bookmaker
BettingMarket
BettingSelection
Odd
Prediction
BetRecommendation
```

### Escopo

- modelos SQLAlchemy;
- schemas;
- repositories;
- services;
- migrations;
- constraints;
- índices;
- histórico;
- auditoria;
- testes.

### Status

```text
PLANEJADO
```

---

## 8. G6 — Integração com Providers

### Objetivo

Integrar provedores reais de dados de futebol.

### Escopo

- contrato comum de providers;
- configuração de credenciais;
- cliente HTTP;
- rate limiting;
- retries;
- tratamento de erros;
- armazenamento de payloads brutos;
- collectors;
- primeiro provider real;
- provider health check;
- dashboard de providers.

### Primeira integração prevista

```text
Football-Data.org
```

### Status

```text
PLANEJADO
```

---

## 9. G7 — Resolução de Identidade e Data Fusion

### Objetivo

Consolidar dados de múltiplos provedores em entidades canônicas únicas.

### Escopo

- normalização;
- aliases;
- matching automático;
- confiança de mapeamento;
- revisão manual;
- conflitos;
- quarentena;
- rastreabilidade;
- prioridade por provedor;
- regras de fusão;
- auditoria das decisões;
- reprocessamento de payloads.

### Fluxo esperado

```text
Raw Payload
    ↓
Validation
    ↓
Normalization
    ↓
Entity Resolution
    ↓
Data Fusion
    ↓
Canonical Domain
```

### Status

```text
PLANEJADO
```

---

## 10. G8 — Motor Estatístico

### Objetivo

Criar a camada estatística responsável por transformar dados históricos em
indicadores úteis.

### Escopo

- forma recente;
- desempenho como mandante;
- desempenho como visitante;
- força de calendário;
- gols esperados;
- médias;
- distribuições;
- tendências;
- peso temporal;
- contexto da competição;
- contexto do treinador;
- contexto do árbitro;
- impacto de ausências;
- confiabilidade das amostras.

### Status

```text
PLANEJADO
```

---

## 11. G9 — Modelos Preditivos

### Objetivo

Estimar probabilidades para diferentes mercados de futebol.

### Escopo

- modelos por competição;
- modelos por mercado;
- ensembles;
- calibração;
- backtesting;
- versionamento;
- histórico imutável de previsões;
- comparação entre modelos;
- explicabilidade;
- Monte Carlo;
- probabilidades condicionais;
- detecção de mudança de regime.

### Mercados previstos

```text
1X2
Double Chance
Draw No Bet
Asian Handicap
European Handicap
Over/Under
Both Teams To Score
Team Goals
First Goal
Last Goal
Halftime
Corners
Cards
Player Markets
Match Statistics
Combined Markets
```

### Status

```text
PLANEJADO
```

---

## 12. G10 — Motor de Recomendações

### Objetivo

Transformar probabilidades em recomendações claras e auditáveis.

### Escopo

- probabilidade implícita;
- probabilidade do modelo;
- odd justa;
- valor esperado;
- confiança;
- risco;
- Opportunity Score;
- explicação da recomendação;
- filtros;
- comparação de odds;
- histórico da recomendação;
- recomendações correlacionadas;
- bloqueio de recomendações inseguras.

### Classificações de risco previstas

```text
Conservador
Moderado
Agressivo
Alto risco
Especulativo
```

### Status

```text
PLANEJADO
```

---

## 13. G11 — Gestão de Risco e Portfólio

### Objetivo

Ajudar o usuário a controlar exposição e risco financeiro.

### Escopo

- bankroll;
- Kelly Criterion;
- Kelly fracionado;
- limites por aposta;
- limites diários;
- exposição por competição;
- exposição por mercado;
- correlação entre apostas;
- otimização de portfólio;
- simulador de estratégia;
- perfil de risco do usuário;
- drawdown;
- ROI;
- yield.

### Status

```text
PLANEJADO
```

---

## 14. G12 — Experiência do Usuário

### Objetivo

Criar uma interface moderna, intuitiva e acessível.

### Escopo

- modo simples;
- modo avançado;
- home;
- partidas;
- mercados;
- análises;
- sugestões;
- equipes;
- competições;
- favoritos;
- alertas;
- perfil;
- comparação de cenários;
- linha do tempo;
- busca em linguagem natural;
- relatórios automáticos;
- notificações dentro da aplicação;
- notificações push;
- indicador discreto de atualização dos dados.

### Restrições de notificação

Não serão utilizados:

```text
email
Telegram
Discord
WhatsApp
```

### Status

```text
PLANEJADO
```

---

## 15. G13 — Motor ao Vivo

### Objetivo

Atualizar probabilidades e recomendações durante as partidas.

### Escopo

- ingestão de eventos ao vivo;
- atualização contínua;
- placar;
- tempo de jogo;
- estatísticas ao vivo;
- odds ao vivo;
- probabilidades ao vivo;
- recomendações ao vivo;
- suspensão automática;
- retomada;
- degradação controlada;
- detecção de anomalias;
- notificações push.

### Status

```text
PLANEJADO
```

---

## 16. G14 — Produção, Segurança e Escalabilidade

### Objetivo

Preparar o sistema para uso contínuo e seguro.

### Escopo

- autenticação;
- autorização;
- proteção de credenciais;
- observabilidade;
- métricas;
- alertas operacionais;
- backups;
- recuperação;
- filas;
- cache;
- escalabilidade;
- testes de carga;
- resiliência;
- auditoria;
- política de retenção;
- segurança da API;
- revisão de dependências.

### Status

```text
PLANEJADO
```

---

## 17. Funcionalidades fora do escopo

O UltraStats AI não terá como objetivo oferecer análise de outros esportes.

Também não será incluída a métrica:

```text
Closing Line Value
CLV
```

Toda referência antiga a CLV deverá ser removida gradualmente da documentação e
da interface.

---

## 18. Princípios do roadmap

O desenvolvimento deverá seguir estes princípios:

- avançar em etapas pequenas;
- documentar antes de implementar estruturas críticas;
- preservar histórico;
- evitar dependência de um único provider;
- manter o domínio independente de APIs externas;
- registrar decisões arquiteturais;
- priorizar rastreabilidade;
- priorizar explicabilidade;
- evitar garantias de resultado;
- considerar jogo responsável;
- manter testes automatizados;
- evitar grandes mudanças sem commit intermediário.

---

## 19. Status atual

```text
Fase atual:
G4.D — Organização da Documentação

Próxima fase principal:
G4.A.3 — Modelo Canônico do Domínio
```

---

## 20. Atualização deste documento

Este roadmap deverá ser atualizado sempre que:

- uma etapa for concluída;
- uma nova etapa for criada;
- o escopo mudar;
- uma funcionalidade for removida;
- uma decisão arquitetural alterar a ordem de desenvolvimento.