# Changelog

Todas as alterações relevantes do UltraStats AI serão registradas neste arquivo.

O formato deste documento é baseado em categorias de alteração e deverá
acompanhar a evolução oficial do roadmap.

---

## [Unreleased]

### Added

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

### Changed

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