# Changelog

Todas as alterações relevantes do UltraStats AI serão registradas neste arquivo.

O formato deste documento é baseado em categorias de alteração e deverá
acompanhar a evolução oficial do roadmap.

---

## [Unreleased]

### Added

- conclusão integral da G16 e promoção da primeira versão estável `v0.1.0`;
- API-Football Free homologada com fixtures, odds e estatísticas reais;
- Football-Data.org mantida como fonte complementar opcional até o token;

- gate auditável da G16 para serviços, providers, dashboard, carga, backup,
  segurança, rollback, observação e aceite humano;
- homologação real das fontes públicas OpenLigaDB, Football-Data.co.uk e
  StatsBomb Open Data;
- evidência de staging da RC2 com bloqueio explícito de promoção sem tokens;

- conclusão integral da G15.1 — Motor Multi-Provider Real;
- adapters para API-Football, Football-Data.co.uk, StatsBomb Open Data e OpenLigaDB;
- matriz de capacidades, fallback degradado, prioridade e snapshots temporais de odds;
- conclusão integral da G15.2 — Dataset, Backtesting e Calibração;
- split temporal/rolling, Brier, log loss, ECE, acurácia, ROI e gate de modelos;
- release candidate `v0.1.0-rc.2` com 2.629 testes e 100% de cobertura;

- conclusão integral da G15 — Release Candidate e Validação Integrada;
- release gate, CI, staging, smoke test e manifesto reproduzível;
- migration full-chain e E2E de todos os contextos G8–G14;
- primeira release candidate `v0.1.0-rc.1`;
- 2.609 testes com 100% de cobertura;
- conclusão integral da G14 — Produção, Segurança e Escalabilidade;
- autenticação, PBKDF2, RBAC, proteção de segredos e segurança de API;
- métricas, alertas, backup/restore, cache, filas e circuit breaker;
- auditoria encadeada, retenção, autoscaling, carga e revisão de dependências;
- persistência operacional, migration reversível, dashboard e runbook;
- conclusão do roadmap principal G1–G14;
- conclusão integral da G13 — Motor ao Vivo;
- ingestão idempotente e snapshots revisionados de partidas;
- placar, relógio, estatísticas, odds, probabilidades e recomendações ao vivo;
- suspensão, retomada, degradação controlada e detecção de anomalias;
- fila push, persistência, migration reversível e dashboard operacional;
- conclusão integral da G12 — Experiência do Usuário;
- hub com modos simples e avançado e navegação unificada;
- perfil acessível, favoritos, alertas, cenários, timeline e busca natural;
- relatórios automáticos, notificações internas e assinaturas push;
- indicador discreto de atualização, migration reversível e persistência;
- conclusão integral da G11 — Gestão de Risco e Portfólio;
- Kelly integral e fracionado com perfis conservador, moderado e agressivo;
- limites por aposta, dia, competição, mercado e correlação;
- otimização de portfólio e simulador de estratégia;
- ROI, yield, drawdown, perfis e snapshots persistentes;
- migration reversível e dashboard de risco e portfólio;
- conclusão integral da G10 — Motor de Recomendações;
- cálculo de odds justas, EV, edge, confiança, risco e Opportunity Score;
- comparação de odds, ranking e diversificação de recomendações correlacionadas;
- filtros de segurança, explicações, histórico e auditoria persistentes;
- migration reversível e dashboard de recomendações seguras;
- conclusão integral da G9 — Modelos Preditivos;
- modelos de placar e contagem para todo o catálogo inicial de mercados;
- ensembles, calibração, backtesting, Monte Carlo e mudança de regime;
- registry versionado, forecasts imutáveis, comparação e dashboard de modelos;
- conclusão integral da G8 — Motor Estatístico;
- forma recente, splits casa/fora, xG, calendário, tendências e contextos;
- distribuições, Poisson, peso temporal e confiabilidade de amostra;
- snapshots estatísticos idempotentes, migration e dashboard operacional;
- conclusão integral da G7 com normalização, matching, revisão e Data Fusion;
- decisões de identidade, quarentena reprocessável e observações rastreáveis;
- fusão por campo com prioridade de provider e conflitos auditáveis;
- persistência SQLAlchemy, migration, fila de revisão, reprocessamento
  idempotente e dashboard operacional de identidade;
- conclusão integral da G6 com framework canônico e adapter Football-Data.org;
- cliente HTTP com autenticação, rate limiting, retries e erros uniformes;
- collectors idempotentes, payload bruto, health check e snapshot operacional;
- stores SQLAlchemy de payloads e health checks, registry, factory por ambiente,
  migration reversível e dashboard Streamlit de providers;
- conclusão integral da G5.10–G5.15 e, consequentemente, de toda a G5;
- dez Domain Services e onze Domain Policies determinísticos;
- repository SQLAlchemy genérico para snapshots de Aggregate Roots;
- Unit of Work transacional com Outbox;
- modelos canônicos com UUID, JSON, timezone, auditoria, soft delete e
  optimistic locking;
- tabelas de Outbox, Inbox e Audit Log com índices, checks, unicidade e FKs;
- migration reversível `7a5f5c10d001`;
- testes de concorrência, idempotência e upgrade/downgrade;
- conclusão integral da G5.9 — Betting, Prediction e Bankroll;
- `Bookmaker`, `BettingMarket`, `BettingSelection` e `OddsSnapshot`;
- `Prediction`, `PredictionResult` e `PredictionExplanation` imutáveis;
- `Recommendation` com validação decimal de valor esperado;
- Aggregate Root `Bankroll` com ledger, saldo e exposição derivados;
- `Bet`, `BetLeg` e `Settlement` com liquidação auditável;
- identificadores canônicos para snapshots, pernas, liquidações e resultados;
- conclusão integral do Match Context e da etapa G5.8;
- entidades `MatchOfficial`, `MatchPeriod`, `MatchSquad`, `Lineup`,
  `LineupEntry`, `MatchEvent`, `MatchStatistic`, `MatchInterruption`,
  `MatchDecision` e `MatchRevision`;
- identificadores e enums operacionais para todas as entidades internas;
- coleções imutáveis com ownership e identidades únicas no agregado;
- registro de eventos com sincronização do placar resumido;
- validações de convocação, escalação, cronologia, estatísticas, decisões e
  revisões;
- integração final com `Tie` por referência canônica de `MatchId`;
- entidade contextual `MatchVenue` e identificador `MatchVenueId`;
- papéis e estados de local, superfícies, condições do gramado e clima;
- sincronização entre o estádio atual da partida e seu local principal;
- histórico de mudanças de estádio com encerramento temporal do local anterior;
- contexto operacional de campo neutro, capacidades, público e ambiente;
- ciclo de vida explícito do agregado `Match`, com transições validadas;
- estados canônicos completos de preparação, jogo, interrupção e resultado;
- entidade imutável `MatchScheduleChange` e seu identificador canônico;
- histórico ordenado e auditável de reagendamentos, preservando o `MatchId`;
- validações de motivo, alteração efetiva, ownership e duplicidade no histórico;
- fundação do contexto canônico `domain.match`;
- Aggregate Root `Match` e entidade interna `MatchParticipant`;
- identificador canônico `MatchParticipantId`;
- enums `MatchType` e `MatchParticipantStatus`;
- regras de ownership e composição obrigatória de participantes;
- suporte a participantes definidos e placeholders;
- programação canônica por data ou timestamp UTC;
- testes integrais e documentação inicial do Match Context;
- contextos canônicos `domain.people` e `domain.team`;
- entidades `Person`, `Player`, `Coach`, `Referee`, `Team`,
  `TeamMembership` e `SquadRegistration`;
- aliases imutáveis e erros específicos para pessoas e equipes;
- enums de perfis, funções, categorias, estados, vínculos e inscrições;
- histórico e reconstrução do contexto People;
- Aggregate Root `Team` com controle de membros e inscrições;
- APIs públicas explícitas para os contextos People e Team;
- documentação arquitetural `people-domain.md` e `team-domain.md`;
- testes unitários de entidades, aliases, enums, erros, histórico,
  reconstrução, invariantes e APIs públicas;
- cobertura obrigatória integrada ao comando padrão do pytest;
- testes dos caminhos defensivos compartilhados, geográficos e de Unit of Work;
- contexto canônico `domain.competition`;
- entidade canônica `Competition`;
- Aggregate Root conceitual `Season`;
- entidade canônica `Stage`;
- entidade canônica `Round`;
- Aggregate Root conceitual `Tie`;
- entidade interna `TieMatchReference`;
- coleção imutável `CompetitionAliases`;
- erros específicos do contexto competitivo;
- regras de vigência temporal para temporadas, fases e rodadas;
- transições controladas de `SeasonStatus`;
- ordenação de fases, rodadas e partidas de confrontos;
- validação da hierarquia entre `Competition`, `Season`, `Stage`, `Round` e `Tie`;
- validação da identidade das partidas de um confronto;
- validação da sequência das partidas de um confronto;
- histórico imutável do contexto competitivo;
- estados de reconstrução para `Competition`, `Season`, `Stage`, `Round` e `Tie`;
- contratos de persistência do contexto competitivo;
- API pública de `ultrastats_ai.domain.competition`;
- testes unitários de aliases, entidades, agregados, histórico, reconstrução, repositórios e API pública;
- testes de validações, hierarquia, identidade, hash, imutabilidade e transições;
- cobertura integral dos módulos do contexto competitivo;
- documentação arquitetural `docs/architecture/competition-domain.md`;
- Added `GeographyExternalIdentityMapping` for geographic provider mappings.
- Added the immutable `GeographyExternalIdentities` collection.
- Added duplicate and missing external identity errors.
- Added provider and canonical entity queries for geographic external identities.
- Added reconstruction states for countries, regions, cities and stadiums.
- Added entity state capture and identity-preserving restoration.
- Added unit tests for geographic external identities and reconstruction.
- Added canonical geographic history types.
- Added `GeographyEntityKind` and `GeographyChangeType`.
- Added immutable `GeographyFieldChange` and `GeographyHistoryEntry`.
- Added duplicate field and empty update validations for geographic history.
- Added repository protocols for countries, regions, cities, stadiums and geographic history.
- Added unit tests for geographic history and persistence contracts.
- Added the canonical `Stadium` entity linked to `City`.
- Added derived region and country access through the stadium geographic hierarchy.
- Added immutable stadium operations for name, city, aliases and coordinates.
- Added city, region and country membership checks for stadiums.
- Added `StadiumNameAliasConflictError`.
- Added unit and public API tests for `Stadium`.
- Added the canonical `City` entity linked to `Region`.
- Added derived country access through the city region hierarchy.
- Added immutable city operations for name, region, aliases and coordinates.
- Added region and country membership checks for cities.
- Added `CityNameAliasConflictError`.
- Added unit and public API tests for `City`.
- Added the canonical `Region` entity linked to `Country`.
- Added immutable region state transitions for name, country, aliases and coordinates.
- Added `belongs_to` identity-based country membership validation.
- Added `RegionNameAliasConflictError`.
- Added unit and public API tests for `Region`.
- Added the canonical `Country` entity with immutable state transitions.
- Added country identity, code, name, aliases and optional coordinates.
- Added country name and alias conflict validation.
- Added identity-based equality and hashing for countries.
- Added unit and public API tests for `Country`.
- Added the initial `domain.geography` package.
- Added immutable `Aliases` collection for geographic entities.
- Added geography-specific alias validation errors.
- Added unit and public API tests for the geography foundation.
- Added canonical `MarketType` enum for betting markets.
- Added canonical `PredictionStatus`, `RecommendationStatus` and `BetStatus` enums.
- Added canonical `RiskClassification` enum for recommendation risk levels.
- Completed the first version of the canonical domain enum library.
- Added canonical `EventType` values for goals, cards, substitutions and match lifecycle events.
- Added canonical `InterruptionType` values for operational, medical, security and weather interruptions.
- Added canonical `DecisionType` values for sporting and administrative decisions.
- Added canonical `ReviewType` values for video, disciplinary and administrative reviews.
- Added unit tests for match event, interruption, decision and review enums.
- Added canonical `ParticipantRole` values for home, away and neutral participants.
- Added canonical `OfficialRole` values for referees, assistants, video officials and match commissioners.
- Added canonical `MovementType` values for transfers, loans, releases, renewals and career movements.
- Added unit tests for participant, official and movement domain enums.
- Added reusable `DomainEnum` infrastructure for canonical string enums.
- Added parsing, normalization, value listing, choices and membership utilities for domain enums.
- Added canonical `CompetitionType`, `PhaseType` and `RoundType` enums.
- Added canonical `SeasonStatus` and `MatchStatus` enums.
- Added unit tests for the first domain enum family.
- Added canonical `DomainDate` values for timezone-independent domain dates.
- Added UTC-normalized `UtcTimestamp` values with timezone awareness validation.
- Added `TemporalInterval` values with duration, containment and overlap operations.
- Added IANA `TimeZone` validation using the standard library `zoneinfo`.
- Added canonical `Latitude`, `Longitude` and composite `Coordinates` values.
- Added comprehensive unit tests for temporal and geographic Value Objects.
- Added canonical numeric Value Objects for percentages, probabilities, money, odds, positions, rounds, shirt numbers, height, weight and age.
- Added reusable `DecimalValue` and `IntegerValue` base classes.
- Added decimal normalization based on Python `Decimal`.
- Added implied probability calculation for decimal odds.
- Added same-currency addition and subtraction operations for monetary values.
- Added comprehensive unit tests for the numeric Value Object library.
- Added canonical `ProviderNamespace` for stable external provider namespaces.
- Added opaque `ExternalIdentifier` values for provider-owned identifiers.
- Added composite `ExternalIdentity` values combining provider namespace and external identifier.
- Added the `domain.shared.external_ids` package and public API exports.
- Added unit tests for provider namespaces, external identifiers and composite external identities.
- Added canonical `SlugValue` for normalized URL-safe textual identifiers.
- Added canonical `AliasValue` for human-readable alternative entity names.
- Added dedicated `domain.shared.slugs` and `domain.shared.aliases` packages.
- Exported `SlugValue` and `AliasValue` through the shared domain public API.
- Added unit tests for slug normalization, alias normalization, validation, equality and immutability.
- Added canonical `CountryCode` with structural alpha-3 validation.
- Added canonical `CompetitionCode` for stable internal competition codes.
- Added canonical `OrganizationCode` for stable internal organization codes.
- Consolidated the canonical codes public API through `ultrastats_ai.domain.shared`.
- Added unit tests for the specialized canonical code types.
- adicionado o pacote `domain.shared.codes`;
- adicionado `CodeValue` como base para códigos canônicos internos;
- adicionado o pacote `domain.shared.names.organizations`;
- adicionado `OrganizationName` para representar nomes canônicos de organizações;
- adicionado o pacote `domain.shared.names.people`;
- adicionado `PersonName` para representar nomes canônicos de pessoas;
- adicionado o pacote `domain.shared.names.competitions`;
- adicionado `CompetitionName` para representar nomes canônicos de competições esportivas;
- adicionado `GeographicName` como base semântica para nomes geográficos;
- adicionado `VenueName` para estádios, arenas e outros locais esportivos;
- estrutura inicial do pacote `domain.shared.names`;
- subpacote `names.base` para os tipos fundamentais de nomes;
- subpacote `names.geography` para nomes geográficos;
- planejamento da migração incremental da biblioteca de nomes.
- Value Object `CountryName` para nomes oficiais de países;
- Value Object `RegionName` para nomes de regiões administrativas;
- Value Object `CityName` para nomes de cidades;
- diferenciação semântica entre nomes geográficos;
- testes unitários dos nomes da geografia administrativa.
- Value Object `ProperName` para nomes oficiais;
- Value Object `DisplayName` para nomes de apresentação;
- Value Object `ShortName` para nomes compactos;
- regras específicas de comprimento para categorias de nomes;
- diferenciação semântica entre nomes oficiais, de exibição e curtos;
- testes unitários dos tipos base de nomes.
- infraestrutura compartilhada `TextValue` para valores textuais;
- normalização Unicode NFKC para tipos textuais;
- normalização de espaços em valores textuais;
- validações configuráveis de comprimento;
- validação textual opcional por expressão regular;
- mecanismo para regras textuais específicas;
- Value Object base `Name`;
- testes unitários da infraestrutura textual e de nomes.
- biblioteca de identificadores canônicos baseada em UUID;
- identificadores específicos para Geography;
- identificadores específicos para Competition;
- identificadores específicos para People e Team;
- identificadores específicos para Match;
- identificadores específicos para providers e resolução de identidade;
- identificadores específicos para Betting;
- identificadores específicos para Statistics e Prediction;
- identificadores específicos para Risk e Bankroll;
- testes unitários dos identificadores canônicos;
- catálogo arquitetural de tipos canônicos.
- documentação do modelo canônico do domínio;
- documentação dos Bounded Contexts;
- definição dos Aggregate Roots;
- definição das entidades internas;
- definição das regras de ownership;
- catálogo inicial de Value Objects;
- regras de identidade canônica;
- regras de identificadores externos;
- regras de aliases;
- regras de snapshots;
- definição de invariantes;
- definição de consistência forte;
- definição de consistência eventual;
- catálogo inicial de Domain Services;
- catálogo inicial de Domain Policies;
- definição de Commands;
- definição de Domain Events;
- definição de Integration Events;
- arquitetura de Transactional Outbox;
- arquitetura de Inbox;
- regras de idempotência;
- regras de reprocessamento;
- regras de compensação;
- arquitetura de Unit of Work;
- estratégia de Optimistic Locking;
- regras de histórico;
- regras de auditoria;
- estratégia de Read Models;
- adoção seletiva de CQRS;
- arquitetura de Sagas;
- estratégia de evolução de schemas;
- arquitetura de raw payloads;
- arquitetura de Data Lineage;
- arquitetura estatística;
- arquitetura de features;
- arquitetura de modelos preditivos;
- arquitetura de recomendações;
- arquitetura de gestão de banca;
- estratégia de observabilidade;
- estratégia de reconciliação;
- estratégia de testes arquiteturais;
- novo índice da documentação;
- fluxo recomendado de leitura;
- atualização do README principal;
- atualização do roadmap para refletir o estado real da G4.
- base compartilhada do domínio;
- abstração `Entity`;
- abstração `AggregateRoot`;
- abstração `ValueObject`;
- abstração `DomainEvent`;
- hierarquia inicial de erros do domínio;
- tipo `Result`;
- contrato base de `Repository`;
- contrato base de `UnitOfWork`;
- testes unitários da base compartilhada.


### Changed

- centralizada a configuração do pytest no arquivo `pyproject.toml`;
- migradas as configurações `testpaths`, `pythonpath`, `python_files` e `python_functions`;
- adotada a pasta `src` como raiz de importação do pacote `ultrastats_ai`;
- habilitada a medição de cobertura de linhas e branches;
- configurado o relatório de cobertura HTML em `htmlcov`;
- configurado o relatório JSON em `coverage-competition.json`;
- definida cobertura mínima obrigatória de 100%;
- ampliada a suíte unitária do contexto `domain.competition`;
- consolidadas em uma única sprint G5.6 a implementação, a configuração de testes e a validação do contexto competitivo;
- atualizado o fluxo oficial do roadmap para iniciar a G5.7 após a conclusão da G5.6;
- Centralizada a configuração do pytest no arquivo `pyproject.toml`.
- Migradas as configurações `testpaths`, `pythonpath`, `python_files` e `python_functions`.
- Adotada a pasta `src` como raiz de importação do pacote `ultrastats_ai`.
- Configurada cobertura de linhas e branches pelo Coverage.py.
- Definida cobertura mínima obrigatória de 100%.
- Configurado relatório de cobertura HTML em `htmlcov`.
- códigos canônicos internos passaram a utilizar normalização em letras maiúsculas e uma política restrita de caracteres;
- tipos como clube, federação, associação e empresa passaram a ser tratados separadamente do nome da organização;
- papéis como jogador, treinador e árbitro passaram a ser tratados como conceitos separados do nome da pessoa;
- `CountryName`, `RegionName` e `CityName` passaram a herdar de `GeographicName`;
- reorganizada a biblioteca de nomes canônicos em subpacotes semânticos;
- movidos os tipos base para `domain.shared.names.base`;
- movidos os nomes geográficos para `domain.shared.names.geography`;
- consolidada a API pública dos nomes por meio de `domain.shared`;
- preservados os caminhos históricos por módulos de compatibilidade;
- eliminadas as definições duplicadas das classes de nomes.
- reorganização da fase G4 no roadmap;
- conclusão da G4.A;
- consolidação da arquitetura de providers na G4.B;
- consolidação da arquitetura de dados na G4.C;
- expansão do G5 em subetapas de implementação;
- atualização das entidades previstas para o domínio canônico;
- atualização da ordem oficial de desenvolvimento;
- definição da documentação como parte obrigatória das entregas;
- atualização do README principal para representar a arquitetura atual.

### Removed

- arquivo legado `pytest.ini`, substituído pela configuração centralizada no `pyproject.toml`;
- subdivisão documental `G5.6.1`, incorporada à sprint consolidada G5.6;

### Fixed

- duplicação do título `Changed` no changelog;
- status desatualizado da fase G5 no roadmap;
- indicação incorreta da G5.5 como última subfase concluída;
- indicação incorreta da G5.6 como próxima subfase;
- separação indevida da qualidade de testes em uma sprint `G5.6.1`;
- blocos de código Markdown não fechados no roadmap;
- indicação incorreta da G4.A.3 como próxima etapa;
- inconsistência entre a documentação arquitetural e o roadmap;
- ausência dos novos documentos no índice da documentação;
- ausência de fluxo oficial de leitura;
- descrição desatualizada do G5.

### Documentation

- consolidada a documentação da sprint G5.6 em uma única entrega;
- removida do roadmap a subdivisão `G5.6.1`;
- documentada a migração definitiva do pytest para o `pyproject.toml`;
- documentada a ampliação da suíte unitária do contexto Competition;
- registrada a execução de 409 testes do contexto competitivo;
- registrada a cobertura de 100,00% das linhas e branches do contexto competitivo;
- registrados 673 statements e 228 branches integralmente cobertos;
- registrada a ausência de linhas não cobertas e branches parcialmente cobertos;
- atualizado o status geral da G5 para refletir a conclusão da G5.6;
- definida a G5.7 — People e Team como próxima subfase;
- Documented geographic external identity mappings and reconstruction.
- Marked G5.5.7 as completed.
- Marked G5.5 Geography and Venue as completed.
- Updated G5.6 Competition as the next planned subphase.
- Corrected the global roadmap status to reflect the current project stage.
- Documented geographic history and repository contracts.
- Updated the roadmap to mark G5.5.6 as completed.
- Documented the canonical `Stadium` entity and its geographic hierarchy.
- Updated the roadmap to mark G5.5.5 Stadium as completed.
- Documented the canonical `City` entity and its geographic relationships.
- Updated the roadmap to mark G5.5.4 City as completed.
- Documented the canonical `Region` entity and its public API.
- Updated the roadmap to mark G5.5.3 Region as completed.
- Updated the roadmap to mark G5.5.2 Country as completed.
- Updated the roadmap to start G5.5 Geography and Venue.
- Documented analytical domain enums for betting, predictions and recommendations.
- Updated the roadmap to mark G5.4 as completed.
- Documented match event, interruption, decision and review enums.
- Updated the development roadmap to mark G5.4.3 as completed.
- Documented participant roles, official roles and movement types.
- Updated the development roadmap to mark G5.4.2 as completed.
- Documented the canonical domain enum infrastructure and sports enums.
- Updated the development roadmap to mark G5.4.1 as completed.
- Documented the canonical temporal and geographic Value Object libraries.
- Updated the development roadmap to mark G5.3.4 and the G5.3 library as completed.
- Documented the canonical numeric Value Object library.
- Updated the roadmap to mark G5.3.3 as completed.
- Documented the external identifier library in `canonical-types.md`.
- Updated the development roadmap to mark G5.3.2.5 as completed.
- Documented the distinction between internal canonical IDs and provider-owned external identities.
- Documented the canonical slug and alias libraries in `canonical-types.md`.
- Updated the development roadmap to mark G5.3.2.4 as completed.
- Documented the semantic difference between URL slugs and human-readable aliases.
- Rebuilt `docs/architecture/canonical-types.md` as the official architectural catalog of canonical types.
- Updated `docs/development/roadmap.md` to mark G5.3.2.3 as completed.
- Documented the canonical code hierarchy and public API.
- criado ou atualizado `docs/architecture/canonical-domain-model.md`;
- criado ou atualizado `docs/architecture/domain-aggregates-and-rules.md`;
- atualizado `docs/development/roadmap.md`;
- atualizado `docs/README.md`;
- atualizado `README.md`;
- atualizado `CHANGELOG.md`.

---

## Convenções

As alterações deverão ser organizadas nas seguintes categorias:

```text
Added
Changed
Deprecated
Removed
Fixed
Security
Documentation
```

### Added

Novas funcionalidades, módulos, documentos ou recursos.

### Changed

Alterações no comportamento, arquitetura, estrutura ou planejamento.

### Deprecated

Funcionalidades mantidas temporariamente, mas planejadas para remoção.

### Removed

Funcionalidades, módulos, documentos ou contratos removidos.

### Fixed

Correções de comportamento, documentação ou inconsistências.

### Security

Alterações relacionadas à segurança.

### Documentation

Alterações exclusivamente documentais ou que afetem documentação oficial.

---

## Versionamento futuro

Quando o projeto iniciar versões publicadas, as seções deverão seguir o formato:

```text
## [1.0.0] - AAAA-MM-DD
```

Até a primeira versão oficial, as alterações permanecerão registradas em:

```text
[Unreleased]
```
