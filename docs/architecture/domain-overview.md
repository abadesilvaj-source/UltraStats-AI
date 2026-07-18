# UltraStats AI — Arquitetura do Domínio

## 1. Visão do produto

O UltraStats AI é uma plataforma exclusivamente voltada para futebol.

O sistema agrega dados de múltiplos provedores, normaliza e combina essas
informações, apresenta estatísticas completas, calcula probabilidades para
mercados de apostas e produz recomendações explicáveis classificadas por
níveis de risco.

O produto também oferece ferramentas de comparação de odds, gestão de banca,
portfólio de apostas, simulação de estratégias, alertas, notificações push,
análises pré-jogo e análises ao vivo.

O sistema não suporta outros esportes.

---

## 2. Objetivos principais

O UltraStats AI deverá:

1. Consolidar dados de múltiplos provedores.
2. Detectar conflitos e inconsistências.
3. Manter rastreabilidade sobre a origem de cada dado.
4. Apresentar estatísticas de futebol.
5. Representar mercados de apostas de forma flexível.
6. Comparar odds entre casas de apostas.
7. Calcular probabilidades próprias.
8. Calcular odd justa e valor esperado.
9. Classificar oportunidades por confiança e risco.
10. Explicar previsões e recomendações.
11. Manter histórico imutável das previsões.
12. Permitir backtesting e simulação de estratégias.
13. Auxiliar na gestão de banca e exposição.
14. Produzir análises pré-jogo e ao vivo.
15. Oferecer interface simples e avançada.
16. Enviar alertas dentro da aplicação e por notificações push.

---

## 3. Princípios arquiteturais

### 3.1 Separação entre dados observados e dados calculados

O sistema deverá distinguir claramente:

- dados coletados de provedores;
- dados normalizados;
- dados canônicos;
- estatísticas derivadas;
- probabilidades calculadas;
- recomendações geradas;
- decisões tomadas pelo usuário.

Esses conceitos não deverão ser armazenados como se fossem a mesma coisa.

### 3.2 Nenhum provedor grava diretamente no domínio canônico

O fluxo obrigatório será:

Provider
→ Raw Payload
→ Validation
→ Normalization
→ Entity Resolution
→ Data Fusion
→ Canonical Domain
→ Statistics
→ Predictions
→ Recommendations

### 3.3 Histórico imutável

Previsões, probabilidades, odds utilizadas e recomendações deverão ser
armazenadas com o estado existente no momento da geração.

Uma previsão histórica não poderá ser recalculada silenciosamente com dados
futuros.

### 3.4 Explicabilidade

Toda previsão e recomendação deverá poder informar:

- dados utilizados;
- versão do modelo;
- fatores principais;
- qualidade dos dados;
- nível de confiança;
- nível de risco;
- limitações conhecidas.

### 3.5 Degradação segura

Quando uma fonte estiver indisponível, o sistema deverá continuar funcionando
com os recursos possíveis.

Informações desatualizadas ou incompletas deverão ser identificadas.

Recomendações que dependam de dados críticos ausentes deverão ser suspensas.

### 3.6 Futebol como domínio exclusivo

Toda a modelagem será especializada em futebol.

Não serão criadas abstrações genéricas para outros esportes.

---

## 4. Contextos do domínio

O domínio do UltraStats AI será dividido nos seguintes contextos:

1. Providers
2. Ingestion
3. Fusion
4. Football
5. Statistics
6. Betting
7. Prediction
8. Recommendation
9. Bankroll
10. Strategy
11. Live
12. User Experience
13. Notification
14. Audit
15. Platform

---

## 5. Provider Context

Responsável pela comunicação com fontes externas.

Principais responsabilidades:

- autenticação;
- chamadas HTTP;
- timeout;
- retry;
- rate limiting;
- headers;
- controle de disponibilidade;
- adaptação de respostas;
- identificação de capacidades do provedor.

Exemplos de provedores:

- Football-Data.org;
- API-Football;
- The Odds API;
- Understat;
- FBref;
- futuros provedores comerciais.

Este contexto não decide qual dado é verdadeiro.

---

## 6. Ingestion Context

Responsável por receber e preservar os dados coletados.

Principais responsabilidades:

- armazenar payloads brutos;
- calcular checksum;
- impedir duplicação desnecessária;
- validar estrutura básica;
- registrar horário da coleta;
- registrar endpoint;
- controlar processamento;
- permitir reprocessamento;
- encaminhar dados inválidos para quarentena.

Este contexto preserva exatamente o que foi recebido.

---

## 7. Fusion Context

Responsável por transformar múltiplas representações em uma visão consolidada.

Principais responsabilidades:

- normalização;
- resolução de entidades;
- aliases;
- mapeamentos externos;
- detecção de duplicidade;
- detecção de conflitos;
- seleção da melhor fonte;
- cálculo de confiança por dado;
- rastreabilidade da decisão;
- criação e atualização de entidades canônicas.

Este contexto determina qual informação entra no domínio canônico.

---

## 8. Football Context

Responsável pelos elementos esportivos centrais.

Principais entidades:

- Country;
- Competition;
- Season;
- Stage;
- Round;
- Team;
- Player;
- Coach;
- Referee;
- Stadium;
- Match;
- Lineup;
- Formation;
- MatchEvent;
- Injury;
- Suspension.

Este contexto representa fatos sobre futebol.

Não contém probabilidades de aposta nem recomendações.

---

## 9. Statistics Context

Responsável por estatísticas observadas e derivadas.

Principais responsabilidades:

- estatísticas de partida;
- estatísticas de equipe;
- estatísticas de jogador;
- forma recente;
- desempenho como mandante;
- desempenho como visitante;
- confrontos diretos;
- força do calendário;
- métricas por competição;
- métricas por treinador;
- métricas por árbitro;
- xG;
- xA;
- médias móveis;
- tendências;
- agregações temporais.

Este contexto não decide se uma aposta deve ser realizada.

---

## 10. Betting Context

Responsável por casas, mercados, seleções, linhas e odds.

Principais entidades:

- Bookmaker;
- BettingMarket;
- MarketDefinition;
- MarketSelection;
- MarketLine;
- MarketQuote;
- OddsSnapshot;
- OddsMovement;
- BettingEvent.

Principais responsabilidades:

- representar mercados;
- comparar odds;
- armazenar histórico;
- calcular probabilidade implícita;
- calcular margem da casa;
- identificar melhor odd;
- representar mercados pré-jogo e ao vivo.

O Closing Line Value não fará parte do produto.

---

## 11. Prediction Context

Responsável por calcular probabilidades.

Principais responsabilidades:

- modelos estatísticos;
- modelos de machine learning;
- Poisson;
- Dixon-Coles;
- Elo;
- modelos por competição;
- modelos por treinador;
- modelos por árbitro;
- consensus model;
- Monte Carlo;
- probabilidades condicionais;
- calibração;
- intervalos de confiança;
- detecção de mudança de regime;
- versionamento de modelos;
- explicação das previsões.

Principais entidades:

- PredictiveModel;
- ModelVersion;
- PredictionRun;
- MarketPrediction;
- PredictionFactor;
- CalibrationMetric;
- SimulationRun.

Este contexto calcula probabilidades, mas não decide a stake do usuário.

---

## 12. Recommendation Context

Responsável por transformar probabilidades e odds em oportunidades analisáveis.

Principais responsabilidades:

- cálculo de odd justa;
- cálculo de valor esperado;
- classificação de risco;
- classificação de confiança;
- Opportunity Score;
- geração de sugestões;
- explicação das sugestões;
- correlação entre mercados;
- detecção de mercados redundantes;
- suspensão de recomendações inseguras.

Principais entidades:

- Recommendation;
- RecommendationReason;
- RiskAssessment;
- ConfidenceAssessment;
- OpportunityScore;
- CorrelationAssessment.

Uma recomendação não representa garantia de resultado.

---

## 13. Bankroll Context

Responsável pela gestão financeira informada pelo usuário.

Principais responsabilidades:

- banca;
- saldo;
- depósitos;
- retiradas;
- apostas;
- stakes;
- exposição;
- limites;
- lucro;
- prejuízo;
- ROI;
- yield;
- drawdown;
- Kelly fracionado;
- controle por período;
- controle por competição;
- controle por mercado.

Principais entidades:

- Bankroll;
- BankrollTransaction;
- UserBet;
- BetSelection;
- StakeSuggestion;
- ExposureLimit;
- BankrollSnapshot.

O sistema não realizará apostas automaticamente nesta etapa arquitetural.

---

## 14. Strategy Context

Responsável por estratégias e simulações.

Principais responsabilidades:

- criação de estratégias;
- definição de filtros;
- backtesting;
- prevenção de vazamento de dados futuros;
- simulação de estratégias;
- portfólio de apostas;
- análise de correlação;
- limites de exposição;
- comparação entre estratégias;
- análise de desempenho histórico.

Principais entidades:

- BettingStrategy;
- StrategyRule;
- BacktestRun;
- BacktestResult;
- BettingPortfolio;
- PortfolioSelection.

---

## 15. Live Context

Responsável por informações e cálculos durante a partida.

Principais responsabilidades:

- eventos ao vivo;
- placar;
- tempo de jogo;
- cartões;
- substituições;
- estatísticas em tempo real;
- odds ao vivo;
- atualização de probabilidades;
- probabilidades condicionais;
- recomendações ao vivo;
- linha do tempo da partida.

Principais entidades:

- LiveMatchState;
- LiveEvent;
- LiveStatisticsSnapshot;
- LiveOddsSnapshot;
- LivePrediction;
- LiveRecommendation.

---

## 16. User Experience Context

Responsável pela personalização e experiência do usuário.

Principais responsabilidades:

- perfil;
- preferências;
- perfil de risco;
- favoritos;
- watchlist;
- filtros;
- modo simples;
- modo avançado;
- pesquisa em linguagem natural;
- relatórios;
- histórico de navegação relevante;
- interface personalizada.

Principais entidades:

- UserProfile;
- RiskProfile;
- Favorite;
- Watchlist;
- SavedFilter;
- UserPreference;
- GeneratedReport.

O perfil do usuário não altera a probabilidade objetiva calculada pelo modelo.

Ele influencia apenas a apresentação, filtragem, stake e recomendações adequadas
ao perfil.

---

## 17. Notification Context

Responsável pelos alertas e notificações.

Canais permitidos:

- notificações dentro da aplicação;
- notificações push.

Canais não previstos:

- e-mail;
- Telegram;
- WhatsApp;
- Discord.

Principais alertas:

- mudança de odd;
- nova oportunidade;
- alteração de probabilidade;
- escalação confirmada;
- ausência importante;
- partida iniciando;
- mudança de risco;
- limite de exposição;
- atualização relevante.

Principais entidades:

- AlertRule;
- AlertEvent;
- InAppNotification;
- PushSubscription;
- PushNotificationDelivery.

---

## 18. Audit Context

Responsável pela rastreabilidade.

Principais responsabilidades:

- origem dos dados;
- regra de fusão aplicada;
- fonte vencedora;
- valores descartados;
- versão do modelo;
- parâmetros utilizados;
- horário da decisão;
- usuário responsável;
- alterações em entidades;
- confiança do dado;
- eventos de segurança.

Principais entidades:

- AuditEvent;
- DataProvenance;
- FusionDecision;
- EntityChange;
- ModelExecutionAudit;
- SecurityAuditEvent.

---

## 19. Platform Context

Responsável pela infraestrutura operacional.

Principais responsabilidades:

- configuração;
- logging;
- scheduler;
- filas;
- jobs;
- health checks;
- heartbeat;
- métricas;
- cache;
- segurança;
- autenticação;
- autorização;
- backups;
- recuperação;
- monitoramento;
- tratamento de falhas.

---

## 20. Fluxo principal dos dados

O fluxo principal será:

1. Um provider coleta dados.
2. O payload bruto é armazenado.
3. O payload é validado.
4. Os dados são normalizados.
5. As entidades são resolvidas.
6. O motor de fusão escolhe os valores canônicos.
7. O domínio de futebol é atualizado.
8. Estatísticas são calculadas.
9. Odds são associadas aos mercados.
10. Modelos calculam probabilidades.
11. Probabilidades são calibradas.
12. Recomendações são avaliadas.
13. Risco e confiança são calculados.
14. Oportunidades são exibidas.
15. O usuário pode registrar uma aposta.
16. O desempenho é acompanhado.
17. Todo o processo permanece auditável.

---

## 21. Dependências permitidas

Fluxo recomendado:

Providers
→ Ingestion
→ Fusion
→ Football

Football
→ Statistics

Football + Statistics + Betting
→ Prediction

Prediction + Betting
→ Recommendation

Recommendation + User Experience
→ Bankroll

Recommendation + Bankroll
→ Strategy

Football + Statistics + Betting
→ Live

Todos os contextos relevantes
→ Audit

Platform oferece infraestrutura para todos os contextos.

---

## 22. Dependências proibidas

As seguintes dependências deverão ser evitadas:

- Provider gravando diretamente em Football.
- Statistics criando entidades de Football.
- Recommendation alterando probabilidades calculadas.
- User Experience alterando fatos esportivos.
- Bankroll alterando resultados de previsões.
- Interface consultando payload bruto diretamente.
- Modelos preditivos lendo respostas específicas de APIs.
- Odds sendo armazenadas sem referência temporal.
- Previsões históricas sendo sobrescritas.
- Dados inválidos entrando diretamente no domínio canônico.

---

## 23. Modos da interface

### Modo simples

Deverá priorizar:

- sugestão;
- probabilidade;
- odd;
- risco;
- confiança;
- explicação resumida.

### Modo avançado

Poderá apresentar:

- modelos utilizados;
- estatísticas detalhadas;
- qualidade das fontes;
- histórico de odds;
- distribuição de probabilidades;
- calibração;
- intervalos de confiança;
- fatores da previsão;
- auditoria e rastreabilidade.

Indicadores de atualização deverão ser discretos e não deverão poluir a
interface.

---

## 24. Jogo responsável

O sistema deverá apresentar claramente que:

- probabilidades não são certezas;
- modelos podem errar;
- dados podem estar incompletos;
- odds podem mudar;
- apostas envolvem risco financeiro;
- nenhuma recomendação representa garantia de lucro.

O sistema deverá permitir:

- limite de exposição;
- limite de stake;
- limite diário;
- alertas de perda;
- alertas de comportamento de risco;
- acompanhamento de drawdown.

---

## 25. Fora do escopo

Não fazem parte do produto:

- outros esportes;
- Closing Line Value;
- notificações por e-mail;
- notificações por Telegram;
- notificações por WhatsApp;
- notificações por Discord;
- promessas de lucro;
- previsões tratadas como certezas;
- gravação direta de payloads externos no domínio canônico.