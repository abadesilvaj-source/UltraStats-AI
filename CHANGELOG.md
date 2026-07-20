# Changelog

Todas as alterações relevantes do UltraStats AI serão registradas neste arquivo.

O formato deste documento é baseado em categorias de alteração e deverá
acompanhar a evolução oficial do roadmap.

---

## [Unreleased]

### Added

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