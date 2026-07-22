# Changelog

Todas as alterações relevantes do UltraStats AI serão registradas neste arquivo.

O formato deste documento é baseado em categorias de alteração e deverá
acompanhar a evolução oficial do roadmap.

---

## [Unreleased]

### Added

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

### Fixed

- indicação incorreta da G4.A.3 como próxima etapa;
- inconsistência entre a documentação arquitetural e o roadmap;
- ausência dos novos documentos no índice da documentação;
- ausência de fluxo oficial de leitura;
- descrição desatualizada do G5.

### Documentation

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