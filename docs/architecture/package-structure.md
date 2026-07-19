# Estrutura de Pacotes do UltraStats AI

Este documento define a organização inicial dos pacotes Python do UltraStats AI.

A estrutura foi criada durante:

```text
G5.1 — Estrutura dos Pacotes do Domínio
```

---

## 1. Objetivo

A estrutura de pacotes deverá:

- separar regras de negócio de detalhes técnicos;
- evitar acoplamento entre domínio e frameworks;
- representar os Bounded Contexts;
- facilitar testes;
- facilitar manutenção;
- permitir evolução independente;
- reduzir dependências circulares.

---

## 2. Estrutura principal

```text
src/
└── ultrastats_ai/
    ├── application/
    ├── domain/
    ├── infrastructure/
    ├── interfaces/
    └── shared/
```

---

## 3. Domain

Diretório:

```text
src/ultrastats_ai/domain/
```

Responsabilidade:

- entidades;
- Aggregate Roots;
- Value Objects;
- enums;
- invariantes;
- Domain Services;
- Domain Policies;
- Domain Events;
- contratos de repositories.

O domínio não deverá depender de:

```text
application
infrastructure
interfaces
SQLAlchemy
FastAPI
providers externos
```

Contextos iniciais:

```text
domain/
├── shared/
├── geography/
├── competition/
├── people/
├── team/
├── match/
├── identity/
├── data_fusion/
├── betting/
├── statistics/
├── prediction/
├── recommendation/
├── risk/
└── bankroll/
```

---

## 4. Application

Diretório:

```text
src/ultrastats_ai/application/
```

Responsabilidade:

- casos de uso;
- commands;
- queries;
- DTOs;
- orquestração;
- controle transacional;
- publicação de eventos;
- portas de entrada e saída.

Estrutura inicial:

```text
application/
├── commands/
├── queries/
├── services/
├── dto/
└── ports/
```

A camada de aplicação poderá depender do domínio.

A camada de aplicação não deverá depender diretamente de implementações
concretas de infraestrutura.

---

## 5. Infrastructure

Diretório:

```text
src/ultrastats_ai/infrastructure/
```

Responsabilidade:

- banco de dados;
- SQLAlchemy;
- repositories concretos;
- Unit of Work concreto;
- providers externos;
- cache;
- mensageria;
- observabilidade;
- configurações.

Estrutura inicial:

```text
infrastructure/
├── database/
│   ├── models/
│   ├── repositories/
│   ├── mappers/
│   ├── unit_of_work/
│   └── types/
├── providers/
├── messaging/
├── cache/
├── observability/
└── settings/
```

---

## 6. Interfaces

Diretório:

```text
src/ultrastats_ai/interfaces/
```

Responsabilidade:

- receber solicitações externas;
- validar formatos de entrada;
- converter entradas em commands ou queries;
- chamar a camada de aplicação;
- converter resultados em respostas externas.

Estrutura inicial:

```text
interfaces/
├── api/
│   ├── routes/
│   ├── schemas/
│   └── dependencies/
├── cli/
└── workers/
```

---

## 7. Shared técnico

Diretório:

```text
src/ultrastats_ai/shared/
```

Responsabilidade:

- componentes técnicos genéricos;
- logging;
- exceções técnicas;
- tipos auxiliares;
- utilitários sem regras do domínio.

Este pacote não deverá se transformar em um diretório genérico para qualquer
código sem classificação.

---

## 8. Domain Shared

Diretório:

```text
src/ultrastats_ai/domain/shared/
```

Responsabilidade:

- abstrações fundamentais do domínio;
- Entity;
- AggregateRoot;
- ValueObject;
- DomainEvent;
- DomainError;
- identificadores canônicos;
- contratos compartilhados pelo domínio.

Esses componentes serão implementados durante:

```text
G5.2 — Base Compartilhada do Domínio
G5.3 — Value Objects e Tipos Canônicos
```

---

## 9. Direção permitida das dependências

```text
interfaces
    ↓
application
    ↓
domain
```

A infraestrutura pode implementar contratos necessários pelas camadas internas:

```text
infrastructure
    ↓
application ports
    ↓
domain contracts
```

O domínio deverá permanecer no centro da arquitetura.

---

## 10. Dependências proibidas

São proibidas dependências como:

```text
domain → infrastructure
domain → interfaces
domain → application

application → interfaces
application → implementação concreta de repository

infrastructure → regras privadas de interfaces
```

Também será proibido importar modelos SQLAlchemy diretamente dentro das
entidades do domínio.

---

## 11. Regras de importação

Os imports deverão seguir o pacote completo.

Exemplo:

```python
from ultrastats_ai.domain.shared.entity import Entity
```

Evitar imports relativos profundos como:

```python
from ../../../shared.entity import Entity
```

Imports relativos simples poderão ser utilizados dentro do mesmo módulo quando
não prejudicarem a compreensão.

---

## 12. Organização dos testes

Estrutura inicial:

```text
tests/
├── unit/
│   ├── domain/
│   └── application/
├── integration/
│   ├── database/
│   └── providers/
├── application/
├── domain/
└── infrastructure/
```

### Testes unitários

Devem testar componentes isolados:

- Value Objects;
- entidades;
- agregados;
- serviços;
- policies;
- casos de uso.

### Testes de integração

Devem testar:

- banco de dados;
- repositories;
- migrations;
- providers;
- cache;
- mensageria.

---

## 13. Convenções de nomenclatura

Diretórios e arquivos Python deverão utilizar:

```text
snake_case
```

Classes deverão utilizar:

```text
PascalCase
```

Funções, métodos e variáveis deverão utilizar:

```text
snake_case
```

Constantes deverão utilizar:

```text
UPPER_SNAKE_CASE
```

---

## 14. Regras de evolução

Novos pacotes somente deverão ser criados quando:

- existir uma responsabilidade clara;
- o código não pertencer adequadamente a um pacote existente;
- a separação reduzir acoplamento;
- houver justificativa arquitetural;
- a alteração estiver alinhada ao roadmap.

Não deverão ser criados antecipadamente módulos vazios para todas as entidades
futuras.

A estrutura deverá evoluir conforme as etapas do G5 forem implementadas.

---

## 15. Estado da implementação

```text
G5.1 — Estrutura dos Pacotes do Domínio
CONCLUÍDO

G5.2 — Base Compartilhada do Domínio
PRÓXIMA ETAPA
```

A G5.1 define apenas a organização inicial.

A implementação das abstrações fundamentais começará na G5.2.