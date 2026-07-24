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

A fase estabelece:

- os limites do domínio;
- os contextos funcionais;
- as entidades canônicas;
- os relacionamentos;
- os agregados;
- as regras de identidade;
- as regras de consistência;
- as fronteiras transacionais;
- a arquitetura de providers;
- a arquitetura de dados;
- a organização da documentação técnica.

### Subfases

```text
G4.A — Arquitetura do Domínio
G4.B — Arquitetura de Providers
G4.C — Arquitetura de Dados
G4.D — Organização da Documentação
```

---

### G4.A — Arquitetura do Domínio

#### G4.A.1 — Visão Geral do Domínio

Escopo:

- definição dos contextos;
- mapa de contexto;
- responsabilidades principais;
- decisões arquiteturais iniciais;
- independência entre domínio e providers.

Documentos relacionados:

```text
docs/architecture/domain-overview.md
docs/architecture/context-map.md
docs/architecture/architecture-decisions.md
```

Status:

```text
CONCLUÍDO
```

---

#### G4.A.2 — Entidades Centrais do Futebol

Escopo:

- domínio central de futebol;
- entidades esportivas principais;
- mapeamentos de identidade;
- ciclo de vida de partidas;
- histórico;
- ADRs relacionadas.

Status:

```text
CONCLUÍDO
```

---

#### G4.A.3 — Modelo Canônico do Domínio

Objetivo:

Definir as entidades, relacionamentos e regras estruturais que formam o modelo
canônico do UltraStats AI.

Documento principal:

```text
docs/architecture/canonical-domain-model.md
```

Escopo concluído:

- entidades geográficas;
- competições;
- temporadas;
- fases;
- rodadas;
- equipes;
- pessoas;
- jogadores;
- treinadores;
- árbitros;
- vínculos;
- inscrições;
- estádios;
- partidas;
- participantes;
- locais;
- oficiais;
- períodos;
- elencos;
- escalações;
- eventos;
- estatísticas;
- interrupções;
- alterações de agenda;
- decisões oficiais;
- revisões;
- confrontos eliminatórios;
- relacionamentos canônicos;
- regras históricas;
- regras de integridade.

Entregas concluídas:

```text
Capítulo 5 — Geography
Capítulo 6 — Competition
Capítulo 7 — Teams and People
Capítulo 8 — Matches and Sporting Calendar
```

Status:

```text
CONCLUÍDO
```

---

#### G4.A.4 — Arquitetura dos Agregados e Regras do Domínio

Objetivo:

Definir as fronteiras comportamentais, transacionais e históricas do domínio
antes da implementação persistente.

Documento principal:

```text
docs/architecture/domain-aggregates-and-rules.md
```

Subetapas:

```text
G4.A.4.1 — Agregados, Bounded Contexts e Value Objects
G4.A.4.2 — Regras de Consistência, Serviços, Políticas e Eventos de Domínio
G4.A.4.3 — Arquitetura Transacional, Histórico e Evolução
```

##### G4.A.4.1 — Agregados, Bounded Contexts e Value Objects

Escopo concluído:

- filosofia do domínio;
- Bounded Contexts;
- responsabilidades dos contextos;
- relações entre contextos;
- Aggregate Roots;
- fronteiras dos agregados;
- entidades internas;
- regras de ownership;
- Value Objects;
- identidade canônica;
- identificadores externos;
- aliases;
- snapshots;
- normalização;
- igualdade por identidade;
- igualdade por valor.

Status:

```text
CONCLUÍDO
```

##### G4.A.4.2 — Regras de Consistência, Serviços, Políticas e Eventos de Domínio

Escopo concluído:

- invariantes;
- consistência forte;
- consistência eventual;
- validações internas;
- validações externas;
- Domain Services;
- Domain Policies;
- Commands;
- Application Services;
- Domain Events;
- Integration Events;
- Transactional Outbox;
- Inbox;
- idempotência;
- retries;
- reprocessamento;
- compensações;
- erros de domínio;
- fluxos de escrita.

Status:

```text
CONCLUÍDO
```

##### G4.A.4.3 — Arquitetura Transacional, Histórico e Evolução

Escopo concluído:

- Unit of Work;
- fronteiras transacionais;
- Optimistic Locking;
- Pessimistic Locking;
- versionamento;
- histórico;
- auditoria;
- retenção;
- exclusão lógica;
- estratégia de identificadores;
- projeções;
- Read Models;
- CQRS seletivo;
- cache;
- Sagas;
- migrations;
- evolução de contratos;
- arquitetura de integração;
- raw payloads;
- Data Lineage;
- arquitetura estatística;
- arquitetura preditiva;
- arquitetura de recomendações;
- arquitetura de banca;
- segurança;
- observabilidade;
- reconciliação;
- backups;
- estratégia de testes.

Status:

```text
CONCLUÍDO
```

Status geral da G4.A.4:

```text
CONCLUÍDO
```

Status geral da G4.A:

```text
CONCLUÍDO
```

---

### G4.B — Arquitetura de Providers

Objetivo:

Definir como fontes externas serão integradas sem acoplar o domínio canônico aos
formatos específicos de cada provider.

Escopo concluído:

- separação entre provider e domínio;
- Provider Client;
- Collector;
- armazenamento de payload bruto;
- validação;
- normalização intermediária;
- rate limiting;
- retries;
- rastreabilidade;
- health check;
- contratos de integração;
- idempotência;
- reprocessamento;
- geração de comandos canônicos.

Decisão arquitetural:

A arquitetura de providers foi consolidada durante a G4.A.4.3, especialmente nas
definições de integração, raw payloads, Data Lineage, idempotência, Outbox,
Inbox e reprocessamento.

Documentos relacionados:

```text
docs/architecture/domain-aggregates-and-rules.md
docs/providers/
```

Status:

```text
CONCLUÍDO
```

---

### G4.C — Arquitetura de Dados

Objetivo:

Definir como dados brutos, normalizados, canônicos, históricos e derivados serão
armazenados, relacionados e reprocessados.

Escopo concluído:

- dados canônicos;
- dados brutos;
- dados normalizados;
- proveniência;
- Data Lineage;
- histórico;
- auditoria;
- dados derivados;
- projeções;
- features;
- previsões;
- versionamento;
- retenção;
- reprocessamento;
- point-in-time correctness.

Decisão arquitetural:

A arquitetura de dados foi consolidada durante a G4.A.4.3, especialmente nas
definições de histórico, raw storage, Data Lineage, arquitetura estatística,
features e modelos preditivos.

Documentos relacionados:

```text
docs/architecture/canonical-domain-model.md
docs/architecture/domain-aggregates-and-rules.md
docs/database/
```

Status:

```text
CONCLUÍDO
```

---

### G4.D — Organização da Documentação

Objetivo:

Manter a documentação técnica sincronizada com as decisões arquiteturais e com
o estado real do projeto.

Escopo:

- organização da pasta `docs/`;
- índice principal;
- roadmap;
- changelog;
- documentação técnica;
- referências cruzadas;
- atualização do README da documentação;
- simplificação do README da raiz;
- verificação de links internos;
- revisão de documentos obsoletos;
- preparação da documentação para o G5.

Entregas concluídas:

- estrutura principal da pasta `docs/`;
- documentação do modelo canônico;
- documentação dos agregados;
- documentação das regras do domínio;
- documentação da arquitetura transacional;
- atualização do roadmap após a conclusão da G4.A.4.

Entregas concluídas:

- estrutura principal da pasta `docs/`;
- documentação do modelo canônico;
- documentação dos agregados;
- documentação das regras do domínio;
- documentação da arquitetura transacional;
- atualização do índice da documentação;
- atualização do README principal;
- atualização do roadmap;
- revisão inicial do changelog;
- preparação formal para o início da G5.

Status:

```text
CONCLUÍDO
```

---

### Status geral da G4

```text
CONCLUÍDO
```

A arquitetura conceitual do UltraStats AI encontra-se oficialmente concluída.

Foram finalizadas:

- Arquitetura do Domínio;
- Modelo Canônico;
- Arquitetura dos Agregados;
- Regras de Domínio;
- Arquitetura de Providers;
- Arquitetura de Dados;
- Organização da Documentação.

A partir deste ponto, alterações estruturais deverão ser realizadas
preferencialmente por meio de novas decisões arquiteturais (ADR) ou pela
evolução controlada da documentação existente.

A próxima fase do projeto será a implementação do domínio canônico (G5).

---

## 7. G5 — Domínio Canônico

### Objetivo

Transformar a arquitetura conceitual definida na G4 em código de domínio,
persistência, migrations e testes automatizados.

O G5 deverá implementar o modelo canônico sem acoplá-lo aos formatos específicos
dos providers.

### Dependências

O início do G5 depende da conclusão de:

```text
G4.A — Arquitetura do Domínio
G4.B — Arquitetura de Providers
G4.C — Arquitetura de Dados
G4.D — Organização da Documentação
```

### Subfases previstas

```text
G5.1  — Estrutura dos Pacotes do Domínio
G5.2  — Base Compartilhada do Domínio
G5.3  — Value Objects e Tipos Canônicos
G5.4  — Enums e Estados do Domínio
G5.5  — Geography e Venue
G5.6  — Competition
G5.7  — People e Team
G5.8  — Match e Tie
G5.9  — Betting, Prediction e Bankroll
G5.10 — Domain Services e Policies
G5.11 — Repositories e Unit of Work
G5.12 — Modelos SQLAlchemy e Mapeamentos
G5.13 — Migrations e Constraints
G5.14 — Testes e Validação Arquitetural
G5.15 — Consolidação do Domínio Canônico
```

---

### G5.1 — Estrutura dos Pacotes do Domínio

Escopo:

- organização dos módulos;
- separação entre domínio, aplicação e infraestrutura;
- convenções de importação;
- prevenção de dependências circulares;
- definição de módulos compartilhados;
- preparação da estrutura de testes.

Status:

```text
CONCLUÍDO
```
Entregas concluídas:

- estrutura principal de pacotes;
- separação entre domínio, aplicação, infraestrutura e interfaces;
- pacotes iniciais dos Bounded Contexts;
- estrutura inicial dos testes;
- arquivos `__init__.py`;
- documentação da estrutura de pacotes;
- regras de dependência;
- regras de importação;
- convenções de nomenclatura.
---

### G5.2 — Base Compartilhada do Domínio

Escopo:

- Entity;
- AggregateRoot;
- ValueObject;
- DomainEvent;
- DomainError;
- Result;
- interfaces de Repository;
- interfaces de Unit of Work;
- suporte a versionamento;
- suporte a eventos pendentes.

Status:

```text
CONCLUÍDO
```
Entregas concluídas:

- abstração `Entity`;
- abstração `AggregateRoot`;
- abstração `ValueObject`;
- abstração `DomainEvent`;
- hierarquia inicial de erros do domínio;
- tipo `Result`;
- contrato base de `Repository`;
- contrato base de `UnitOfWork`;
- exportações do pacote compartilhado;
- testes unitários das abstrações fundamentais.
---

### G5.3 — Biblioteca de Value Objects

```text
EM ANDAMENTO
```

Objetivo:

Construir a biblioteca de tipos canônicos reutilizáveis por todos os contextos
do domínio.

A G5.3 foi dividida para evitar duplicação, inconsistência de validação e criação
desordenada de Value Objects durante a implementação das entidades.

#### G5.3.1 — Identificadores Canônicos

```text
CONCLUÍDO
```

Entregas concluídas:

- base `CanonicalId`;
- base `EntityId`;
- criação de identificadores por UUID;
- reconstrução de identificadores a partir de texto;
- validação de UUID;
- igualdade baseada em tipo e valor;
- identificadores de Geography;
- identificadores de Competition;
- identificadores de People e Team;
- identificadores de Match;
- identificadores de providers;
- identificadores de Betting;
- identificadores de Statistics e Prediction;
- identificadores de Risk e Bankroll;
- testes unitários;
- catálogo de tipos canônicos.

#### G5.3.2 — Tipos Textuais

```text
EM ANDAMENTO
```

Objetivo:

Construir a biblioteca compartilhada de valores textuais canônicos, evitando
duplicação de normalização, validação e regras de comprimento.

##### G5.3.2.1 — Base TextValue

```text
CONCLUÍDO
```

Entregas concluídas:

- base imutável `TextValue`;
- validação do tipo string;
- normalização Unicode NFKC;
- remoção de espaços nas extremidades;
- redução de espaços internos;
- comprimento mínimo configurável;
- comprimento máximo configurável;
- validação opcional por expressão regular;
- mecanismo de validação especializada;
- representação textual;
- suporte a hash;
- base compartilhada `Name`;
- testes unitários;
- documentação arquitetural.

##### G5.3.2.2 — Nomes Canônicos

```text
EM ANDAMENTO
```

Objetivo:

Implementar os tipos de nomes reutilizáveis e suas especializações semânticas
para os diferentes contextos do domínio.

###### G5.3.2.2.1 — Tipos Base de Nomes

```text
CONCLUÍDO
```

Entregas concluídas:

- `ProperName`;
- `DisplayName`;
- `ShortName`;
- limites de comprimento específicos;
- preservação de caracteres Unicode;
- normalização de espaços;
- validação alfanumérica;
- imutabilidade;
- diferenciação semântica por tipo;
- exportações públicas;
- testes unitários;
- documentação arquitetural.

###### G5.3.2.2.2 — Nomes Geográficos

```text
EM ANDAMENTO
```

Objetivo:

Implementar os nomes semânticos utilizados pelos conceitos geográficos e pelos
locais esportivos.

####### G5.3.2.2.2.1 — Geografia Administrativa

```text
CONCLUÍDO
```

Entregas concluídas:

- `CountryName`;
- `RegionName`;
- `CityName`;
- herança de `ProperName`;
- normalização Unicode;
- normalização de espaços;
- diferenciação semântica entre tipos;
- exportações públicas;
- testes unitários;
- documentação arquitetural.

####### G5.3.2.2.2.2 — Reorganização da Biblioteca de Nomes

```text
CONCLUÍDO
```

Objetivo concluído:

Organizar os tipos de nomes em subpacotes sem alterar a API pública do domínio.

Entregas concluídas:

- pacote `domain.shared.names`;
- subpacote `names.base`;
- subpacote `names.geography`;
- migração de `Name`;
- migração de `ProperName`;
- migração de `DisplayName`;
- migração de `ShortName`;
- migração de `CountryName`;
- migração de `RegionName`;
- migração de `CityName`;
- fachada pública em `domain.shared`;
- módulos de compatibilidade para caminhos históricos;
- eliminação das definições duplicadas;
- identidade de classe entre todos os caminhos de importação;
- testes de regressão;
- documentação arquitetural consolidada.

####### G5.3.2.2.2.3 — GeographicName e nomes de locais esportivos

```text
CONCLUÍDO
```

Objetivo concluído:

Introduzir uma base semântica para nomes geográficos e implementar o nome
canônico de locais esportivos.

Entregas concluídas:

- `GeographicName`;
- hierarquia geográfica especializada;
- migração de `CountryName` para `GeographicName`;
- migração de `RegionName` para `GeographicName`;
- migração de `CityName` para `GeographicName`;
- implementação de `VenueName`;
- suporte semântico a estádios;
- suporte semântico a arenas;
- suporte semântico a outros locais esportivos;
- exportação por `domain.shared.names.geography`;
- exportação por `domain.shared.names`;
- exportação pela API pública `domain.shared`;
- testes de herança;
- testes de normalização;
- testes de identidade entre APIs;
- testes de distinção semântica.

####### G5.3.2.2.3 — Nomes de competição

```text
CONCLUÍDO
```

Objetivo concluído:

Implementar o tipo canônico responsável por representar nomes de competições
esportivas.

Entregas concluídas:

- pacote `domain.shared.names.competitions`;
- implementação de `CompetitionName`;
- herança semântica de `ProperName`;
- normalização textual;
- preservação de caracteres Unicode;
- preservação de abreviações;
- distinção semântica em relação aos demais tipos de nomes;
- exportação pelo pacote especializado;
- exportação por `domain.shared.names`;
- exportação pela API pública `domain.shared`;
- testes de identidade entre APIs;
- testes de imutabilidade;
- documentação arquitetural.

Decisão arquitetural:

Os formatos liga, copa e torneio não serão representados por subclasses de
`CompetitionName`.

Esses conceitos serão modelados futuramente como propriedades da competição.

####### G5.3.2.2.4 — Nomes de pessoas

```text
CONCLUÍDO
```

Objetivo concluído:

Implementar o tipo canônico responsável por representar nomes de pessoas.

Entregas concluídas:

- pacote `domain.shared.names.people`;
- implementação de `PersonName`;
- herança semântica de `ProperName`;
- normalização textual;
- suporte a nomes compostos;
- suporte a nomes de apenas uma palavra;
- preservação de caracteres Unicode;
- preservação de hífens;
- preservação de apóstrofos;
- distinção semântica em relação aos demais tipos de nomes;
- exportação pelo pacote especializado;
- exportação por `domain.shared.names`;
- exportação pela API pública `domain.shared`;
- testes de identidade entre APIs;
- testes de imutabilidade;
- documentação arquitetural.

Decisão arquitetural:

Os papéis de jogador, treinador, árbitro, dirigente, agente ou qualquer outra
função exercida por uma pessoa não serão representados por subclasses de
`PersonName`.

Esses papéis serão modelados futuramente nas fases de entidades, agregados e
regras de domínio.

Não serão criados, neste momento:

```text
PlayerName
CoachName
RefereeName
```

####### G5.3.2.2.5 — Nomes de organizações

```text
CONCLUÍDO
```

Objetivo concluído:

Implementar o tipo canônico responsável por representar nomes de organizações.

Entregas concluídas:

- pacote `domain.shared.names.organizations`;
- implementação de `OrganizationName`;
- herança semântica de `ProperName`;
- normalização textual;
- suporte a nomes completos;
- suporte a abreviações;
- preservação de caracteres Unicode;
- preservação de pontuação;
- preservação de sufixos empresariais;
- distinção semântica em relação aos demais tipos de nomes;
- exportação pelo pacote especializado;
- exportação por `domain.shared.names`;
- exportação pela API pública `domain.shared`;
- testes de identidade entre APIs;
- testes de imutabilidade;
- documentação arquitetural.

Decisão arquitetural:

Tipos como clube, federação, associação e empresa não serão representados por
subclasses de `OrganizationName`.

Esses conceitos serão modelados futuramente como propriedades ou tipos
específicos da entidade de organização.

Não serão criados neste momento:

```text
ClubName
FederationName
AssociationName
CompanyName
```

##### G5.3.2.3 — Códigos Canônicos

**Status:** CONCLUÍDA

**Objetivo:** estabelecer a biblioteca de códigos canônicos internos do domínio,
centralizando as regras estruturais compartilhadas e criando especializações
semanticamente distintas para países, competições e organizações.

###### G5.3.2.3.1 — Base CodeValue

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação do pacote `domain.shared.codes`;
- [x] implementação de `CodeValue`;
- [x] normalização por remoção de espaços externos;
- [x] normalização para letras maiúsculas;
- [x] rejeição de valores vazios;
- [x] limite máximo de 64 caracteres;
- [x] restrição a caracteres ASCII;
- [x] aceitação de letras, números, ponto, hífen e underscore;
- [x] igualdade e hash baseados no valor normalizado;
- [x] imutabilidade;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.3.2 — CountryCode

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação de `CountryCode`;
- [x] herança de `CodeValue`;
- [x] normalização herdada da classe-base;
- [x] exigência de exatamente três caracteres;
- [x] aceitação exclusiva de letras ASCII;
- [x] validação estrutural equivalente ao formato alpha-3;
- [x] ausência deliberada de catálogo ISO embarcado;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.3.3 — CompetitionCode

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação de `CompetitionCode`;
- [x] herança integral das regras de `CodeValue`;
- [x] representação de códigos canônicos internos de competições;
- [x] independência em relação a providers externos;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.3.4 — OrganizationCode

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação de `OrganizationCode`;
- [x] herança integral das regras de `CodeValue`;
- [x] representação de códigos canônicos internos de organizações;
- [x] ausência deliberada de especializações como `ClubCode` e `FederationCode`;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.3.5 — Consolidação da Biblioteca de Códigos

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] consolidação da API do pacote `domain.shared.codes`;
- [x] consolidação da API pública de `domain.shared`;
- [x] diferenciação semântica entre os tipos concretos;
- [x] atualização de `canonical-types.md`;
- [x] atualização do roadmap;
- [x] atualização do changelog;
- [x] execução dos testes específicos;
- [x] execução da suíte completa do projeto.

**Resultado final:**

```text
TextValue
└── CodeValue
    ├── CountryCode
    ├── CompetitionCode
    └── OrganizationCode
```

---

##### G5.3.2.4 — Slugs e Aliases

**Status:** CONCLUÍDA

**Objetivo:** estabelecer tipos textuais canônicos para slugs apropriados para URLs e aliases capazes de preservar grafias humanas alternativas.

###### G5.3.2.4.1 — SlugValue

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação do pacote `domain.shared.slugs`;
- [x] implementação de `SlugValue`;
- [x] herança de `TextValue`;
- [x] normalização para letras minúsculas;
- [x] remoção de espaços externos;
- [x] remoção de marcas diacríticas;
- [x] conversão de espaços internos em hífens;
- [x] validação de letras, números e hífens;
- [x] rejeição de hífen inicial;
- [x] rejeição de hífen final;
- [x] rejeição de hífens consecutivos;
- [x] limite máximo de 128 caracteres;
- [x] utilização de `DomainValidationError`;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.4.2 — AliasValue

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação do pacote `domain.shared.aliases`;
- [x] implementação de `AliasValue`;
- [x] herança de `TextValue`;
- [x] normalização Unicode para NFC;
- [x] remoção de espaços externos;
- [x] redução de múltiplos espaços internos;
- [x] preservação de maiúsculas e minúsculas;
- [x] preservação de acentos;
- [x] preservação de pontuação legítima;
- [x] limite máximo de 128 caracteres;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.4.3 — Consolidação

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] consolidação da API de `domain.shared.slugs`;
- [x] consolidação da API de `domain.shared.aliases`;
- [x] consolidação da API pública de `domain.shared`;
- [x] diferenciação semântica entre slug e alias;
- [x] atualização de `canonical-types.md`;
- [x] atualização do roadmap;
- [x] atualização do changelog;
- [x] execução dos testes específicos;
- [x] execução dos testes de `shared`;
- [x] execução da suíte completa.

**Resultado final:**

```text
TextValue
├── Name
├── CodeValue
├── SlugValue
└── AliasValue
```

**API pública consolidada:**

```python
from ultrastats_ai.domain.shared import (
    AliasValue,
    SlugValue,
)
```

---

##### G5.3.2.5 — Identificadores Externos

**Status:** CONCLUÍDA

**Objetivo:** representar identidades pertencentes a providers externos sem confundi-las com os identificadores canônicos internos do UltraStats AI.

###### G5.3.2.5.1 — ProviderNamespace

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação de `ProviderNamespace`;
- [x] herança de `TextValue`;
- [x] normalização para letras minúsculas;
- [x] conversão de espaços internos para underscore;
- [x] validação de segmentos;
- [x] rejeição de separadores consecutivos;
- [x] limite máximo de 64 caracteres;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.5.2 — ExternalIdentifier

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação de `ExternalIdentifier`;
- [x] herança de `TextValue`;
- [x] tratamento do identificador como chave opaca;
- [x] normalização Unicode para NFC;
- [x] remoção de espaços externos;
- [x] preservação de maiúsculas e minúsculas;
- [x] rejeição de espaços internos;
- [x] rejeição de caracteres de controle;
- [x] limite máximo de 128 caracteres;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.5.3 — ExternalIdentity

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação de `ExternalIdentity`;
- [x] composição entre `ProviderNamespace` e `ExternalIdentifier`;
- [x] validação dos tipos componentes;
- [x] igualdade baseada na identidade composta;
- [x] hash estável;
- [x] propriedade `key`;
- [x] uso como chave de dicionário;
- [x] exportação pela API pública;
- [x] testes unitários.

###### G5.3.2.5.4 — Consolidação

**Status:** CONCLUÍDA

Implementações concluídas:

- [x] criação do pacote `domain.shared.external_ids`;
- [x] consolidação da API interna;
- [x] consolidação da API pública de `domain.shared`;
- [x] documentação da identidade externa composta;
- [x] atualização de `canonical-types.md`;
- [x] atualização do roadmap;
- [x] atualização do changelog;
- [x] execução dos testes específicos;
- [x] execução dos testes de `shared`;
- [x] execução da suíte completa.

**Resultado final:**

```text
ExternalIdentity
├── ProviderNamespace
└── ExternalIdentifier
```

**API pública consolidada:**

```python
from ultrastats_ai.domain.shared import (
    ExternalIdentifier,
    ExternalIdentity,
    ProviderNamespace,
)
```

---

##### G5.3.3 — Tipos Numéricos

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] base decimal `DecimalValue`;
- [x] base inteira `IntegerValue`;
- [x] porcentagem com `Percentage`;
- [x] probabilidade com `Probability`;
- [x] valores monetários com `Money`;
- [x] odds decimais com `Odds`;
- [x] posições com `Position`;
- [x] números de rodada com `RoundNumber`;
- [x] números de camisa com `ShirtNumber`;
- [x] altura com `Height`;
- [x] peso com `Weight`;
- [x] idade com `Age`;
- [x] validações específicas;
- [x] imutabilidade;
- [x] API pública;
- [x] testes unitários;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
DecimalValue
├── Percentage
├── Probability
├── Odds
├── Height
└── Weight

IntegerValue
├── Position
├── RoundNumber
├── ShirtNumber
└── Age

Money
```

---

##### G5.3.4 — Tipos Temporais e Geográficos

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] datas do domínio com `DomainDate`;
- [x] timestamps UTC com `UtcTimestamp`;
- [x] intervalos temporais com `TemporalInterval`;
- [x] validação de timezones IANA com `TimeZone`;
- [x] latitude com `Latitude`;
- [x] longitude com `Longitude`;
- [x] coordenadas com `Coordinates`;
- [x] normalização de timestamps para UTC;
- [x] rejeição de datetimes sem timezone;
- [x] intervalos no formato `[start, end)`;
- [x] cálculo de duração;
- [x] verificação de contenção;
- [x] verificação de sobreposição;
- [x] validação de limites geográficos;
- [x] imutabilidade;
- [x] APIs públicas;
- [x] testes unitários;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura temporal resultante:

```text
DomainDate
UtcTimestamp
TimeZone

TemporalInterval
├── start: UtcTimestamp
└── end: UtcTimestamp
```

Estrutura geográfica resultante:

```text
Coordinates
├── Latitude
└── Longitude
```

Critério de conclusão da G5.3:

- [x] biblioteca compartilhada implementada;
- [x] tipos imutáveis;
- [x] validações centralizadas;
- [x] testes unitários concluídos;
- [x] catálogo de tipos atualizado;
- [x] ausência de dependência de infraestrutura.

---

### G5.4 — Enums e Estados do Domínio

Escopo:

- tipos de competição;
- tipos de fase;
- tipos de rodada;
- status de temporada;
- status de partida;
- papéis de participantes;
- papéis de oficiais;
- tipos de eventos;
- tipos de interrupção;
- tipos de decisão;
- tipos de revisão;
- tipos de mercado;
- status de previsão;
- status de recomendação;
- status de aposta;
- tipos de movimentação;
- classificações de risco.

#### G5.4.1 — Infraestrutura e Enums Esportivos

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] criação da classe-base `DomainEnum`;
- [x] conversão segura com `parse`;
- [x] normalização de entradas textuais;
- [x] listagem de valores com `values`;
- [x] listagem de nomes com `names`;
- [x] geração de opções com `choices`;
- [x] verificação com `has_value`;
- [x] tipos de competição com `CompetitionType`;
- [x] tipos de fase com `PhaseType`;
- [x] tipos de rodada com `RoundType`;
- [x] status de temporada com `SeasonStatus`;
- [x] status de partida com `MatchStatus`;
- [x] API pública;
- [x] testes unitários;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
DomainEnum
├── CompetitionType
├── PhaseType
├── RoundType
├── SeasonStatus
└── MatchStatus
```

#### G5.4.2 — Participantes, Arbitragem e Movimentações

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] papéis de participantes com `ParticipantRole`;
- [x] diferenciação entre mandante, visitante e neutro;
- [x] papéis de oficiais com `OfficialRole`;
- [x] representação de árbitro principal;
- [x] representação de árbitros assistentes;
- [x] representação de VAR e AVAR;
- [x] representação de comissário da partida;
- [x] tipos de movimentação com `MovementType`;
- [x] transferências definitivas;
- [x] empréstimos e retornos;
- [x] transferências livres;
- [x] liberações e renovações;
- [x] promoções, rebaixamentos e aposentadorias;
- [x] integração com `DomainEnum`;
- [x] API pública;
- [x] testes unitários;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
DomainEnum
├── ParticipantRole
├── OfficialRole
└── MovementType
```

#### G5.4.3 — Eventos, Interrupções, Decisões e Revisões

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] tipos de eventos com `EventType`;
- [x] gols, gols contra e gols de pênalti;
- [x] cartões e expulsões;
- [x] substituições, faltas, impedimentos e escanteios;
- [x] eventos de início, intervalo e encerramento;
- [x] tipos de interrupção com `InterruptionType`;
- [x] interrupções climáticas;
- [x] interrupções de segurança;
- [x] falhas técnicas e de equipamento;
- [x] interrupções para VAR;
- [x] tipos de decisão com `DecisionType`;
- [x] decisões confirmadas e revertidas;
- [x] decisões administrativas;
- [x] remarcações e deduções de pontos;
- [x] tipos de revisão com `ReviewType`;
- [x] revisões de gol, pênalti e cartão vermelho;
- [x] revisões de impedimento, mão e falta;
- [x] revisões disciplinares e administrativas;
- [x] integração com `DomainEnum`;
- [x] API pública;
- [x] testes unitários;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
DomainEnum
├── EventType
├── InterruptionType
├── DecisionType
└── ReviewType
```
#### G5.4.4 — Mercado, Previsões, Recomendações e Apostas

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] `MarketType`;
- [x] `PredictionStatus`;
- [x] `RecommendationStatus`;
- [x] `BetStatus`;
- [x] `RiskClassification`;
- [x] integração com `DomainEnum`;
- [x] API pública;
- [x] testes unitários;
- [x] documentação arquitetural;
- [x] suíte completa executada.

Resultado:

```text
DomainEnum
├── MarketType
├── PredictionStatus
├── RecommendationStatus
├── BetStatus
└── RiskClassification
```

Resultado da G5.4:

```text
CONCLUÍDA
```


---

Status:

```text
CONCLUÍDO
```

---

### G5.5 — Geography e Venue

Entidades previstas:

```text
Country
Region
City
Stadium
```

Escopo:

- entidades;
- agregados;
- aliases;
- localização;
- regras de identidade;
- histórico;
- persistência;
- testes.

Status:

```text
CONCLUÍDO
```

#### G5.5.1 — Fundação do domínio geográfico

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] criação do pacote `domain.geography`;
- [x] exceção-base `GeographyDomainError`;
- [x] exceção `DuplicateAliasError`;
- [x] exceção `AliasNotFoundError`;
- [x] coleção imutável `Aliases`;
- [x] validação de tipos da coleção;
- [x] prevenção de aliases duplicados;
- [x] inclusão e remoção imutáveis;
- [x] API pública inicial;
- [x] testes unitários;
- [x] testes da API pública;
- [x] execução da suíte completa.

Estrutura inicial:

```text
geography/
├── __init__.py
├── aliases.py
└── errors.py
```

Etapa seguinte concluída:

```text
G5.5.2 — Country
```
---
#### G5.5.2 — Country

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] entidade canônica `Country`;
- [x] identidade baseada em `CanonicalId`;
- [x] código baseado em `CountryCode`;
- [x] nome principal baseado em `Name`;
- [x] aliases baseados em `Aliases`;
- [x] coordenadas geográficas opcionais;
- [x] validação de tipos;
- [x] prevenção de conflito entre nome e alias;
- [x] alteração imutável de nome;
- [x] alteração imutável de código;
- [x] inclusão imutável de alias;
- [x] remoção imutável de alias;
- [x] atualização imutável de coordenadas;
- [x] remoção de coordenadas;
- [x] igualdade por identidade canônica;
- [x] hash por identidade canônica;
- [x] API pública;
- [x] testes unitários;
- [x] testes de imutabilidade;
- [x] testes da API pública;
- [x] execução da suíte completa.

Estrutura resultante:

```text
geography/
├── __init__.py
├── aliases.py
├── country.py
└── errors.py
```

Etapa seguinte concluída:

```text
G5.5.3 — Region
```
---
#### G5.5.3 — Region

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] entidade canônica `Region`;
- [x] identidade baseada em `CanonicalId`;
- [x] vínculo obrigatório com `Country`;
- [x] nome principal baseado em `Name`;
- [x] aliases baseados em `Aliases`;
- [x] coordenadas geográficas opcionais;
- [x] validação de tipos;
- [x] prevenção de conflito entre nome e alias;
- [x] alteração imutável de nome;
- [x] alteração imutável de país;
- [x] inclusão imutável de alias;
- [x] remoção imutável de alias;
- [x] atualização imutável de coordenadas;
- [x] remoção de coordenadas;
- [x] verificação de pertencimento com `belongs_to`;
- [x] igualdade por identidade canônica;
- [x] hash por identidade canônica;
- [x] API pública;
- [x] testes unitários;
- [x] testes de imutabilidade;
- [x] testes de pertencimento;
- [x] testes da API pública;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
geography/
├── __init__.py
├── aliases.py
├── country.py
├── errors.py
└── region.py
```

Etapa seguinte concluída:

G5.5.4 — City

#### G5.5.4 — City

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] entidade canônica `City`;
- [x] identidade baseada em `CanonicalId`;
- [x] vínculo obrigatório com `Region`;
- [x] acesso derivado ao `Country`;
- [x] nome principal baseado em `Name`;
- [x] aliases baseados em `Aliases`;
- [x] coordenadas opcionais;
- [x] validação de tipos;
- [x] prevenção de conflito entre nome e alias;
- [x] alteração imutável de nome;
- [x] alteração imutável de região;
- [x] inclusão imutável de alias;
- [x] remoção imutável de alias;
- [x] atualização imutável de coordenadas;
- [x] remoção de coordenadas;
- [x] verificação de pertencimento à região;
- [x] verificação de pertencimento ao país;
- [x] igualdade por identidade canônica;
- [x] hash por identidade canônica;
- [x] API pública;
- [x] testes unitários;
- [x] testes de imutabilidade;
- [x] testes de relações geográficas;
- [x] testes da API pública;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
geography/
├── __init__.py
├── aliases.py
├── city.py
├── country.py
├── errors.py
└── region.py
```

Etapa seguinte concluída:

```text
G5.5.5 — Stadium
```

#### G5.5.5 — Stadium

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] entidade canônica `Stadium`;
- [x] identidade baseada em `CanonicalId`;
- [x] vínculo obrigatório com `City`;
- [x] acesso derivado à `Region`;
- [x] acesso derivado ao `Country`;
- [x] nome principal baseado em `Name`;
- [x] aliases baseados em `Aliases`;
- [x] coordenadas opcionais;
- [x] validação de tipos;
- [x] prevenção de conflito entre nome e alias;
- [x] alteração imutável de nome;
- [x] alteração imutável de cidade;
- [x] inclusão imutável de alias;
- [x] remoção imutável de alias;
- [x] atualização imutável de coordenadas;
- [x] remoção de coordenadas;
- [x] verificação de pertencimento à cidade;
- [x] verificação de pertencimento à região;
- [x] verificação de pertencimento ao país;
- [x] igualdade por identidade canônica;
- [x] hash por identidade canônica;
- [x] API pública;
- [x] testes unitários;
- [x] testes de imutabilidade;
- [x] testes das relações geográficas;
- [x] testes da API pública;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
geography/
├── __init__.py
├── aliases.py
├── city.py
├── country.py
├── errors.py
├── region.py
└── stadium.py
```

Etapa seguinte concluída:

```text
G5.5.6 — Histórico e Persistência Geográfica
```

#### G5.5.6 — Histórico e Persistência Geográfica

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] enum `GeographyEntityKind`;
- [x] enum `GeographyChangeType`;
- [x] Value Object `GeographyFieldChange`;
- [x] entidade `GeographyHistoryEntry`;
- [x] histórico imutável;
- [x] identificação da entidade alterada;
- [x] identificação do tipo de alteração;
- [x] timestamp UTC;
- [x] validação de campos duplicados;
- [x] exigência de alterações para entradas `UPDATED`;
- [x] consulta de campos alterados;
- [x] consulta individual de alteração;
- [x] protocolo `CountryRepository`;
- [x] protocolo `RegionRepository`;
- [x] protocolo `CityRepository`;
- [x] protocolo `StadiumRepository`;
- [x] protocolo `GeographyHistoryRepository`;
- [x] independência de ORM;
- [x] independência de banco de dados;
- [x] API pública;
- [x] testes unitários do histórico;
- [x] testes dos contratos de repositório;
- [x] testes das exceções;
- [x] testes da API pública;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
geography/
├── __init__.py
├── aliases.py
├── city.py
├── country.py
├── errors.py
├── history.py
├── region.py
├── repositories.py
└── stadium.py
```

Etapa seguinte concluída:

```text
G5.5.7 — Identidade Externa e Reconstrução Geográfica
```

#### G5.5.7 — Identidade Externa e Reconstrução Geográfica

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] mapeamento `GeographyExternalIdentityMapping`;
- [x] vínculo entre identidade externa e identidade canônica;
- [x] identificação do tipo de entidade geográfica;
- [x] acesso ao provider do mapeamento;
- [x] acesso à chave externa;
- [x] verificação de pertencimento à entidade;
- [x] verificação de pertencimento ao provider;
- [x] coleção imutável `GeographyExternalIdentities`;
- [x] prevenção de identidades externas duplicadas;
- [x] inclusão imutável;
- [x] remoção imutável;
- [x] consulta por identidade externa;
- [x] consulta por provider;
- [x] consulta por entidade canônica;
- [x] estado `CountryReconstruction`;
- [x] estado `RegionReconstruction`;
- [x] estado `CityReconstruction`;
- [x] estado `StadiumReconstruction`;
- [x] captura de estado por `from_entity`;
- [x] reconstrução por `restore`;
- [x] preservação da identidade canônica;
- [x] preservação dos relacionamentos;
- [x] preservação dos aliases;
- [x] preservação das coordenadas;
- [x] independência de ORM;
- [x] independência de banco de dados;
- [x] independência de providers concretos;
- [x] API pública;
- [x] testes unitários;
- [x] testes de imutabilidade;
- [x] testes de reconstrução;
- [x] testes de identidades externas;
- [x] testes das exceções;
- [x] testes da API pública;
- [x] documentação arquitetural;
- [x] execução da suíte completa.

Estrutura resultante:

```text
geography/
├── __init__.py
├── aliases.py
├── city.py
├── country.py
├── errors.py
├── external_identity.py
├── history.py
├── reconstruction.py
├── region.py
├── repositories.py
└── stadium.py
```

Próxima fase:

```text
G5.6 — Competition
```
---

### G5.6 — Competition

Objetivo:

Implementar e consolidar o Bounded Context competitivo do UltraStats AI,
representando competições, temporadas, fases, rodadas e confrontos sem
acoplamento aos formatos específicos dos providers.

Entidades implementadas:

```text
Competition
Season
Stage
Round
Tie
TieMatchReference
```

Módulos implementados:

```text
domain.competition.aliases
domain.competition.competition
domain.competition.errors
domain.competition.history
domain.competition.reconstruction
domain.competition.repositories
domain.competition.round
domain.competition.season
domain.competition.stage
domain.competition.tie
domain.competition.tie_match_reference
```

Escopo concluído:

- [x] estrutura do Bounded Context competitivo;
- [x] entidade canônica `Competition`;
- [x] Aggregate Root conceitual `Season`;
- [x] entidade canônica `Stage`;
- [x] entidade canônica `Round`;
- [x] Aggregate Root conceitual `Tie`;
- [x] entidade interna `TieMatchReference`;
- [x] aliases competitivos imutáveis;
- [x] validação de conflitos entre nomes e aliases;
- [x] regras de vigência temporal;
- [x] transições controladas de temporada;
- [x] ordenação de fases, rodadas e partidas;
- [x] validação da hierarquia competitiva;
- [x] relacionamento entre competição e temporada;
- [x] relacionamento entre temporada e fase;
- [x] relacionamento entre temporada, fase e rodada;
- [x] relacionamento entre confronto, competição, temporada e fase;
- [x] prevenção de partidas duplicadas em confrontos;
- [x] prevenção de sequências duplicadas em confrontos;
- [x] igualdade baseada em identidade canônica;
- [x] hash baseado em identidade canônica;
- [x] imutabilidade das entidades e agregados;
- [x] histórico imutável do contexto competitivo;
- [x] estados de reconstrução;
- [x] contratos de repositório;
- [x] API pública;
- [x] independência de ORM;
- [x] independência de banco de dados;
- [x] independência de providers concretos;
- [x] configuração central do pytest no `pyproject.toml`;
- [x] migração de `testpaths`;
- [x] migração de `pythonpath`;
- [x] migração dos padrões de arquivos de teste;
- [x] migração dos padrões de funções de teste;
- [x] configuração de cobertura de linhas;
- [x] configuração de cobertura de branches;
- [x] configuração do relatório HTML;
- [x] definição da cobertura mínima obrigatória em 100%;
- [x] remoção do arquivo legado `pytest.ini`;
- [x] ampliação da suíte unitária do contexto Competition;
- [x] testes de validações e caminhos de erro;
- [x] testes de hierarquia;
- [x] testes de identidade e hash;
- [x] testes de imutabilidade;
- [x] testes de transições de estado;
- [x] testes de reconstrução;
- [x] testes de histórico;
- [x] testes dos contratos de repositório;
- [x] testes da API pública.

Validação concluída:

- [x] toda a suíte do contexto executada sem falhas;
- [x] cobertura integral de linhas confirmada;
- [x] cobertura integral de branches confirmada;
- [x] configuração carregada pelo `pyproject.toml`;
- [x] arquivo legado `pytest.ini` removido;
- [x] relatório HTML gerado em `htmlcov`;
- [x] relatório JSON gerado em `coverage-competition.json`;
- [x] ausência de linhas não cobertas;
- [x] ausência de branches parcialmente cobertos;
- [x] ausência de alterações nos módulos de produção para alcançar a cobertura.

Resultado final:

```text
409 testes aprovados
0 testes falhando
0 erros
673 statements cobertos
228 branches cobertos
0 linhas ausentes
0 branches parcialmente cobertos
100,00% de cobertura de linhas e branches
```

Status:

```text
CONCLUÍDO
```

Próxima sprint:

```text
G5.7 — People e Team
```

---

### G5.7 — People e Team

Entidades previstas:

```text
Person
Player
Coach
Referee
Team
TeamMembership
SquadRegistration
```

Escopo:

- identidade compartilhada de pessoas;
- especializações profissionais;
- equipes;
- vínculos;
- inscrições;
- aliases;
- vigência;
- histórico;
- persistência;
- testes.

Status:

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] contexto canônico `domain.people`;
- [x] entidades `Person`, `Player`, `Coach` e `Referee`;
- [x] aliases, perfis profissionais, estados e histórico de pessoas;
- [x] reconstrução de pessoas preservando identidade;
- [x] contexto canônico `domain.team`;
- [x] Aggregate Root `Team`;
- [x] entidades `TeamMembership` e `SquadRegistration`;
- [x] aliases, estados, vigência, vínculos e inscrições;
- [x] APIs públicas explícitas para People e Team;
- [x] documentação arquitetural dos dois contextos;
- [x] portão global de cobertura integrado ao comando padrão do pytest;
- [x] 100% de cobertura de linhas e branches do domínio canônico;
- [x] remoção de artefatos de cobertura do versionamento.

Resultado final:

```text
2182 testes aprovados
0 testes falhando
3566 statements cobertos
1092 branches cobertos
0 linhas ausentes
0 branches parcialmente cobertos
100,00% de cobertura de linhas e branches
```

---

### G5.8 — Match e Tie

Entidades previstas:

```text
Match
MatchParticipant
MatchVenue
MatchOfficial
MatchPeriod
MatchSquad
Lineup
LineupEntry
MatchEvent
MatchStatistic
MatchInterruption
MatchScheduleChange
MatchDecision
MatchRevision
Tie
TieMatchReference
```

Escopo:

- ciclo de vida da partida;
- participantes;
- local;
- oficiais;
- períodos;
- elenco da partida;
- escalação;
- eventos;
- estatísticas oficiais;
- interrupções;
- alterações de agenda;
- decisões oficiais;
- revisões;
- confrontos;
- invariantes;
- histórico;
- persistência;
- testes.

Status:

```text
CONCLUÍDO
```

#### G5.8.A — Match Foundation

Entregas concluídas:

- [x] identificador canônico `MatchParticipantId`;
- [x] enum `MatchType`;
- [x] enum `MatchParticipantStatus`;
- [x] entidade interna `MatchParticipant`;
- [x] Aggregate Root `Match`;
- [x] referência a competição, temporada, fase e rodada por identidade;
- [x] exatamente dois participantes por partida;
- [x] papéis obrigatórios `HOME` e `AWAY`;
- [x] ownership de participantes pelo Match;
- [x] suporte a participantes ainda não definidos;
- [x] prevenção de identidades, equipes, papéis e ordens duplicadas;
- [x] programação por data esportiva ou timestamp UTC;
- [x] substituição imutável do estado de participantes;
- [x] API pública explícita do contexto;
- [x] documentação arquitetural inicial;
- [x] cobertura integral de linhas e branches.

Resultado validado:

```text
2248 testes aprovados
0 testes falhando
3774 statements cobertos
1186 branches cobertos
0 linhas ausentes
0 branches parcialmente cobertos
100,00% de cobertura de linhas e branches
```

Status:

```text
CONCLUÍDO
```

Próxima fatia:

```text
G5.8.B — Match Lifecycle e Schedule History
```

#### G5.8.B — Match Lifecycle e Schedule History

Entregas concluídas:

- [x] expansão canônica de `MatchStatus`;
- [x] matriz explícita de transições válidas do ciclo de vida;
- [x] rejeição de transições inválidas e de mudanças após estados terminais;
- [x] identificador canônico `MatchScheduleChangeId`;
- [x] entidade imutável `MatchScheduleChange`;
- [x] histórico ordenado de alterações de data e horário no agregado;
- [x] preservação do `MatchId` em reagendamentos;
- [x] validação de motivo, diferença efetiva, ownership e identidades duplicadas;
- [x] API pública explícita do ciclo de vida e do histórico;
- [x] documentação arquitetural atualizada;
- [x] cobertura integral de linhas e branches.

Resultado validado:

```text
2296 testes aprovados
0 testes falhando
3857 statements cobertos
1222 branches cobertos
0 linhas ausentes
0 branches parcialmente cobertos
100,00% de cobertura de linhas e branches
```

Status:

```text
CONCLUÍDO
```

Próxima fatia:

```text
G5.8.C — Match Venue
```

#### G5.8.C — Match Venue

Entregas concluídas:

- [x] identificador canônico `MatchVenueId`;
- [x] entidade interna imutável `MatchVenue`;
- [x] enums de papel, status, superfície, condição e clima;
- [x] referência contextual a estádio e cidade;
- [x] sincronização controlada entre `Match.stadium_id` e o local principal;
- [x] histórico de locais anteriores com validade temporal;
- [x] garantia de apenas um local principal vigente;
- [x] troca coordenada de local preservando o `MatchId`;
- [x] contexto de campo neutro, local alternativo e temporário;
- [x] condições ambientais, superfície, capacidades e público;
- [x] validações de ownership, duplicidade, confirmação e consistência operacional;
- [x] API pública e documentação arquitetural atualizadas;
- [x] cobertura integral de linhas e branches.

Resultado validado:

```text
2357 testes aprovados
0 testes falhando
4067 statements cobertos
1294 branches cobertos
0 linhas ausentes
0 branches parcialmente cobertos
100,00% de cobertura de linhas e branches
```

Status:

```text
CONCLUÍDO
```

Próxima fatia:

```text
G5.8.D — Match Officials
```

#### G5.8.D–G5.8.H — Sprint de conclusão do Match Context

Entregas concluídas:

- [x] `MatchOfficial` com nomeações identificadas ou TBD;
- [x] `MatchPeriod` com ordem, duração, acréscimos, placar e intervalo real;
- [x] `MatchSquad` com limites e lista oficial por participante;
- [x] `Lineup` versionada e `LineupEntry` contextual;
- [x] `MatchEvent` cronológico, relacionável e com placar posterior;
- [x] sincronização do placar resumido do agregado por eventos;
- [x] `MatchStatistic` por escopo, unidade e valor canônico;
- [x] `MatchInterruption` com início, retomada, período e motivo;
- [x] `MatchDecision` esportiva ou administrativa;
- [x] `MatchRevision` versionada, auditável e aplicável;
- [x] identificadores canônicos para todas as entidades internas;
- [x] ownership, identidade única e coleções imutáveis no agregado;
- [x] integração preservada com `Tie` por `TieMatchReference` e `MatchId`;
- [x] API pública integral do Match Context;
- [x] documentação arquitetural e roadmap consolidados;
- [x] cobertura integral de linhas e branches.

Resultado final validado:

```text
2388 testes aprovados
0 testes falhando
4494 statements cobertos
1372 branches cobertos
0 linhas ausentes
0 branches parcialmente cobertos
100,00% de cobertura de linhas e branches
```

Status:

```text
CONCLUÍDO
```

Resultado da G5.8:

```text
Match e Tie concluídos
```

---

### G5.9 — Betting, Prediction e Bankroll

Entidades previstas:

```text
Bookmaker
BettingMarket
BettingSelection
OddsSnapshot
Prediction
PredictionResult
PredictionExplanation
Recommendation
Bankroll
BankrollTransaction
Bet
BetLeg
Settlement
```

Escopo:

- mercados;
- seleções;
- odds;
- previsões;
- resultados preditivos;
- explicações;
- recomendações;
- banca;
- ledger;
- apostas;
- liquidação;
- histórico;
- persistência;
- testes.

Status:

```text
CONCLUÍDO
```

Entregas concluídas:

- [x] Aggregate Root `Bookmaker`;
- [x] mercados canônicos e seleções com ownership;
- [x] snapshots imutáveis e históricos de odds;
- [x] Aggregate Root `Prediction`;
- [x] resultados probabilísticos e odd justa;
- [x] explicações auditáveis;
- [x] recomendações com EV, confiança, stake e risco;
- [x] Aggregate Root `Bankroll`;
- [x] ledger derivável por `BankrollTransaction`;
- [x] apostas simples e múltiplas por `Bet` e `BetLeg`;
- [x] liquidação auditável por `Settlement`;
- [x] saldo e exposição derivados;
- [x] precisão decimal por `Money`, `Odds`, `Probability` e `Percentage`;
- [x] APIs públicas e documentação arquitetural;
- [x] cobertura integral de linhas e branches.

Resultado final validado:

```text
2423 testes aprovados
0 testes falhando
4807 statements cobertos
1456 branches cobertos
0 linhas ausentes
0 branches parcialmente cobertos
100,00% de cobertura de linhas e branches
```

Resultado da G5.9:

```text
Betting, Prediction e Bankroll concluídos
```

---

### G5.10 — Domain Services e Policies

Domain Services previstos:

```text
IdentityResolutionService
DataFusionService
MatchResultService
TieResolutionService
ProbabilityCalibrationService
FairOddCalculationService
ExpectedValueCalculationService
RecommendationEvaluationService
StakeCalculationService
BetSettlementService
```

Domain Policies previstas:

```text
ProviderPriorityPolicy
ConflictResolutionPolicy
AutoMatchThresholdPolicy
ManualReviewThresholdPolicy
MatchWinnerPolicy
AwayGoalsPolicy
MinimumExpectedValuePolicy
MinimumConfidencePolicy
MaximumStakePolicy
DailyExposurePolicy
KellyFractionPolicy
```

Status:

```text
CONCLUÍDO
```

---

### G5.11 — Repositories e Unit of Work

Escopo:

- contratos de repositories;
- repositories por Aggregate Root;
- Unit of Work;
- transações;
- carregamento de agregados;
- persistência de eventos;
- controle de concorrência;
- isolamento entre domínio e SQLAlchemy.

Status:

```text
CONCLUÍDO
```

---

### G5.12 — Modelos SQLAlchemy e Mapeamentos

Escopo:

- modelos persistentes;
- mapeamento entre domínio e banco;
- UUID;
- Decimal;
- timezone;
- relacionamentos;
- composites;
- versionamento;
- auditoria;
- soft delete;
- Optimistic Locking.

Status:

```text
CONCLUÍDO
```

---

### G5.13 — Migrations e Constraints

Escopo:

- migrations com Alembic;
- tabelas;
- chaves estrangeiras;
- índices;
- constraints;
- unicidade;
- checks;
- Outbox;
- Inbox;
- Audit Log;
- dados iniciais;
- validação de upgrade;
- validação de downgrade.

Status:

```text
CONCLUÍDO
```

---

### G5.14 — Testes e Validação Arquitetural

Escopo:

- testes de Value Objects;
- testes de entidades;
- testes de agregados;
- testes de invariantes;
- testes de Domain Services;
- testes de policies;
- testes de repositories;
- testes de Unit of Work;
- testes de migrations;
- testes de concorrência;
- testes de idempotência;
- testes de contratos.

Status:

```text
CONCLUÍDO
```

---

### G5.15 — Consolidação do Domínio Canônico

Escopo:

- revisão dos módulos;
- revisão das dependências;
- revisão do banco;
- revisão de migrations;
- revisão de testes;
- revisão da documentação;
- atualização do roadmap;
- preparação do G6.

Status:

```text
CONCLUÍDO
```

---

### Status geral da G5

```text
CONCLUÍDO
```

A implementação do domínio canônico está concluída e preparada para a G6.

Etapas concluídas:

```text
G5.1 — Estrutura dos Pacotes do Domínio
G5.2 — Base Compartilhada do Domínio
G5.3 — Biblioteca de Value Objects
G5.4 — Enums e Estados do Domínio
G5.5 — Geography e Venue
G5.6 — Competition
G5.7 — People e Team
G5.8 — Match e Tie
G5.9 — Betting, Prediction e Bankroll
G5.10 — Domain Services e Policies
G5.11 — Repositories e Unit of Work
G5.12 — Modelos SQLAlchemy e Mapeamentos
G5.13 — Migrations e Constraints
G5.14 — Testes e Validação Arquitetural
G5.15 — Consolidação do Domínio Canônico
```

Próxima etapa:

```text
G6 — Integração com Providers
```

Último resultado validado:

```text
G5 — Domínio Canônico

2439 testes aprovados
100,00% de cobertura de linhas e branches
0 linhas ausentes
0 branches parcialmente cobertos
```

Próximo objetivo:

```text
Integrar providers externos por adapters, mantendo o domínio e a persistência
canônica independentes das APIs de terceiros.
```


A implementação continuará respeitando os documentos:

```text
docs/architecture/canonical-domain-model.md
docs/architecture/domain-aggregates-and-rules.md
docs/architecture/canonical-types.md
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
CONCLUÍDO
```

Entregas concluídas:

- contrato e configuração comum;
- cliente HTTP resiliente e rate limiting;
- tratamento uniforme de erros;
- adapter Football-Data.org v4;
- collectors e preservação idempotente de payload bruto;
- health check e contrato de snapshot para dashboard.
- persistência SQLAlchemy durável de payloads e health checks;
- deduplicação por fingerprint SHA-256;
- registry e factory configurável por ambiente;
- migration reversível `8b6a6d20e002`;
- dashboard Streamlit de providers;
- 2.445 testes com 100% de cobertura.

Próxima etapa: G7 — Resolução de Identidade e Data Fusion.

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
CONCLUÍDO
```

Entregas concluídas:

- normalização Unicode determinística;
- aliases e candidatos por entidade canônica;
- matching automático com confiança;
- thresholds para associação e revisão manual;
- decisões auditáveis, rejeição e quarentena reprocessável;
- observações com rastreabilidade ao payload bruto;
- fusão por campo com prioridade de provider;
- detecção e registro de conflitos.
- persistência de decisões, evidências, fusões e conflitos;
- fila ordenada de revisão manual;
- quarentena durável e idempotente;
- pipeline de validação, resolução e reprocessamento;
- migration reversível `9c7b7e30f003`;
- dashboard de revisão e auditoria;
- 2.458 testes com 100% de cobertura.

Próxima etapa: G8 — Motor Estatístico.

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
CONCLUÍDO
```

Entregas concluídas:

- forma recente com peso temporal;
- desempenho como mandante e visitante;
- força de calendário e impacto de ausências;
- gols e gols esperados;
- médias, variância, mínimos e máximos;
- tendências temporais;
- contextos de competição, treinador e árbitro;
- distribuição de Poisson;
- tamanho efetivo e confiabilidade da amostra;
- proteção contra vazamento de dados futuros;
- snapshots SQLAlchemy idempotentes;
- migration reversível `a18c8f40a004`;
- dashboard do Motor Estatístico;
- 2.464 testes com 100% de cobertura.

Próxima etapa: G9 — Modelos Preditivos.

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
Fase principal atual:
G5 — Domínio Canônico

Última subfase concluída:
G5.7 — People e Team

Última entrega concluída:
Implementação, testes e consolidação documental dos Bounded Contexts People e
Team.

Resultado da última entrega:
2182 testes aprovados
100,00% de cobertura de linhas e branches
0 linhas ausentes
0 branches parcialmente cobertos

Subfase atual:
G5.8 — Match e Tie

Próximo objetivo:
Implementar o Match Context sem acoplamento aos formatos específicos dos
providers.
```

---

## 20. Atualização deste documento

A atualização do roadmap faz parte do desenvolvimento do UltraStats AI e deverá
ser tratada como uma entrega da fase de documentação.

Este documento deverá ser atualizado sempre que:

- uma etapa for iniciada;
- uma etapa for concluída;
- uma etapa for dividida;
- uma nova etapa for criada;
- o escopo for alterado;
- uma funcionalidade for adicionada;
- uma funcionalidade for removida;
- uma decisão arquitetural alterar a ordem do desenvolvimento;
- uma dependência entre fases for modificada;
- o início da próxima fase for autorizado.

Cada atualização deverá revisar, no mínimo:

- status da fase principal;
- status das subfases;
- etapa atual;
- última etapa concluída;
- próxima etapa;
- entregas realizadas;
- entregas pendentes;
- documentos relacionados;
- dependências para avanço.

O roadmap não deverá indicar uma etapa como concluída enquanto ainda existirem
entregas obrigatórias de documentação, revisão ou validação associadas a ela.
---

## Histórico de marcos

```text
✔ G1 concluído
✔ G2 concluído
✔ G3 concluído
✔ G4 concluído
◉ G5 em andamento

Subfases concluídas da G5:

✔ G5.1 — Estrutura dos Pacotes do Domínio
✔ G5.2 — Base Compartilhada do Domínio
✔ G5.3 — Biblioteca de Value Objects
✔ G5.4 — Enums e Estados do Domínio
✔ G5.5 — Geography e Venue
✔ G5.6 — Competition
✔ G5.7 — People e Team

Próxima subfase:

G5.8 — Match e Tie
```

A G4 representa o congelamento da arquitetura do UltraStats AI.

Toda implementação realizada a partir da G5 deverá respeitar a arquitetura
definida nos documentos oficiais do domínio.
