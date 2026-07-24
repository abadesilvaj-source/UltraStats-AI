# Documentação do UltraStats AI

Este diretório concentra a documentação técnica, arquitetural, operacional e de
desenvolvimento do UltraStats AI.

A documentação deverá permanecer sincronizada com:

- o roadmap;
- o código-fonte;
- o banco de dados;
- as migrations;
- os contratos de integração;
- as decisões arquiteturais;
- os fluxos operacionais;
- os modelos estatísticos e preditivos.

---

## 1. Objetivo

A documentação do UltraStats AI possui os seguintes objetivos:

- registrar decisões arquiteturais;
- definir o domínio canônico;
- documentar integrações;
- organizar o desenvolvimento;
- orientar implementações futuras;
- facilitar manutenção;
- facilitar revisão técnica;
- reduzir decisões implícitas;
- preservar o histórico do projeto;
- permitir rastreabilidade entre arquitetura e código.

A documentação não deverá ser tratada apenas como material complementar.

Ela faz parte das entregas oficiais do projeto.

---

## 2. Estrutura da documentação

```text
docs/
├── README.md
├── api/
├── architecture/
├── database/
├── deployment/
├── development/
├── images/
└── providers/
```

Cada diretório possui uma responsabilidade específica.

---

## 3. Arquitetura

Diretório:

```text
docs/architecture/
```

Contém a definição conceitual e estrutural do UltraStats AI.

Documentos principais:

```text
docs/architecture/domain-overview.md
docs/architecture/context-map.md
docs/architecture/architecture-decisions.md
docs/architecture/canonical-domain-model.md
docs/architecture/canonical-persistence.md
docs/architecture/identity-resolution-data-fusion.md
docs/architecture/statistical-engine.md
docs/architecture/predictive-models.md
docs/architecture/domain-aggregates-and-rules.md
docs/architecture/package-structure.md
docs/architecture/canonical-types.md
docs/architecture/people-domain.md
docs/architecture/team-domain.md
docs/architecture/match-domain.md
```

### 3.1 Domain Overview

Arquivo:

```text
docs/architecture/domain-overview.md
```

Responsabilidade:

- apresentar o domínio;
- definir os principais objetivos;
- apresentar os módulos centrais;
- registrar os limites iniciais do sistema;
- contextualizar a arquitetura.

---

### 3.2 Context Map

Arquivo:

```text
docs/architecture/context-map.md
```

Responsabilidade:

- apresentar os Bounded Contexts;
- demonstrar relações entre contextos;
- identificar dependências;
- registrar responsabilidades;
- orientar integrações internas.

---

### 3.3 Architecture Decisions

Arquivo:

```text
docs/architecture/architecture-decisions.md
```

Responsabilidade:

- registrar decisões arquiteturais;
- apresentar alternativas consideradas;
- documentar consequências;
- preservar justificativas;
- evitar repetição de decisões já avaliadas.

---

### 3.4 Canonical Domain Model

Arquivo:

```text
docs/architecture/canonical-domain-model.md
```

Responsabilidade:

- definir as entidades canônicas;
- definir os relacionamentos;
- definir os ciclos de vida;
- registrar regras estruturais;
- organizar o modelo esportivo;
- separar o domínio dos formatos dos providers.

Conteúdo principal:

```text
Geography
Competition
Teams and People
Matches and Sporting Calendar
```

O documento descreve o que existe no domínio.

---

### 3.5 Domain Aggregates and Rules

Arquivo:

```text
docs/architecture/domain-aggregates-and-rules.md
```

Responsabilidade:

- definir Bounded Contexts;
- definir Aggregate Roots;
- definir entidades internas;
- estabelecer ownership;
- definir Value Objects;
- definir regras de identidade;
- definir invariantes;
- definir Domain Services;
- definir Domain Policies;
- definir Domain Events;
- definir consistência;
- definir transações;
- definir concorrência;
- definir histórico;
- definir auditoria;
- definir integração;
- definir reprocessamento;
- definir arquitetura estatística;
- definir arquitetura preditiva.

O documento descreve como o domínio se comporta.
---
---

### 3.6 Package Structure

Arquivo:

```text
docs/architecture/package-structure.md
```

Responsabilidade:

- definir a estrutura dos pacotes Python;
- definir a separação entre camadas;
- definir a direção das dependências;
- registrar dependências proibidas;
- organizar os Bounded Contexts;
- orientar a estrutura dos testes.

Este documento estabelece a organização física do código-fonte e as regras de
dependência entre os módulos da aplicação.

Ele complementa a arquitetura definida em:

```text
canonical-domain-model.md
domain-aggregates-and-rules.md
```

Enquanto esses documentos definem **o domínio**, o `package-structure.md`
define **como o código será organizado para implementá-lo**.
---

### 3.7 Canonical Types

Arquivo:

```text
docs/architecture/canonical-types.md
```

Responsabilidade:

- catalogar identificadores canônicos;
- catalogar Value Objects;
- catalogar enums;
- registrar regras de validação;
- registrar regras de igualdade;
- documentar tipos compartilhados;
- impedir mistura de conceitos semanticamente diferentes.

O documento será atualizado durante as etapas G5.3 e G5.4.

## 4. Relação entre os documentos de arquitetura

Os documentos arquiteturais deverão ser lidos na seguinte ordem:

```text
1. domain-overview.md
2. context-map.md
3. architecture-decisions.md
4. canonical-domain-model.md
5. domain-aggregates-and-rules.md
```

A relação entre os dois documentos principais é:

```text
canonical-domain-model.md
    ↓
define entidades, atributos e relacionamentos

domain-aggregates-and-rules.md
    ↓
define agregados, ownership, invariantes e comportamento
```

Nenhum dos documentos substitui o outro.

Eles formam conjuntamente a especificação arquitetural do domínio.

---

## 5. API

Diretório:

```text
docs/api/
```

Responsabilidade:

- documentar endpoints;
- documentar autenticação;
- documentar requests;
- documentar responses;
- documentar códigos de erro;
- documentar versionamento;
- documentar contratos públicos;
- documentar exemplos de uso.

A documentação da API deverá ser atualizada juntamente com as alterações nos
contratos HTTP.

---

## 6. Banco de dados

Diretório:

```text
docs/database/
```

Responsabilidade:

- documentar estrutura do banco;
- registrar convenções;
- documentar tabelas;
- documentar relacionamentos;
- documentar índices;
- documentar constraints;
- documentar migrations;
- registrar estratégias de backup;
- registrar estratégias de restauração;
- registrar retenção de dados.

O banco de dados deverá refletir o modelo canônico, mas não deverá substituir a
documentação do domínio.

---

## 7. Providers

Diretório:

```text
docs/providers/
```

Responsabilidade:

- documentar providers externos;
- registrar autenticação;
- registrar endpoints;
- registrar limites;
- registrar paginação;
- registrar rate limits;
- registrar schemas;
- registrar particularidades;
- registrar mapeamentos;
- registrar health checks;
- registrar falhas conhecidas.

Cada provider deverá possuir documentação própria.

A documentação do provider não deverá alterar diretamente o modelo canônico.

---

## 8. Desenvolvimento

Diretório:

```text
docs/development/
```

Responsabilidade:

- organizar o desenvolvimento;
- registrar o roadmap;
- registrar convenções;
- registrar fluxos de trabalho;
- registrar decisões operacionais;
- orientar contribuições;
- acompanhar etapas concluídas e pendentes.

Documentos principais:

```text
docs/development/roadmap.md
```

---

### 8.1 Roadmap

Arquivo:

```text
docs/development/roadmap.md
```

Responsabilidade:

- registrar as fases do projeto;
- indicar a etapa atual;
- indicar etapas concluídas;
- indicar próximas etapas;
- registrar dependências;
- registrar entregas;
- registrar alterações de escopo;
- manter a sequência oficial do desenvolvimento.

A atualização do roadmap é uma etapa oficial do projeto.

O roadmap deverá ser atualizado quando:

- uma etapa começar;
- uma etapa terminar;
- uma etapa for dividida;
- uma nova etapa surgir;
- uma dependência mudar;
- o escopo for alterado;
- uma decisão arquitetural mudar a ordem das entregas.

---

## 9. Deployment

Diretório:

```text
docs/deployment/
```

Responsabilidade:

- documentar ambientes;
- documentar instalação;
- documentar configuração;
- documentar variáveis de ambiente;
- documentar containers;
- documentar banco;
- documentar deploy;
- documentar rollback;
- documentar observabilidade;
- documentar recuperação.

---

## 10. Imagens

Diretório:

```text
docs/images/
```

Responsabilidade:

- armazenar diagramas;
- armazenar fluxogramas;
- armazenar modelos visuais;
- armazenar imagens utilizadas pela documentação.

As imagens deverão possuir nomes descritivos.

Exemplo:

```text
context-map.png
canonical-domain-overview.png
provider-processing-flow.png
match-aggregate.png
```

---

## 11. Fluxo recomendado de leitura

### 11.1 Para compreender o projeto

```text
README.md da raiz
    ↓
docs/README.md
    ↓
docs/architecture/domain-overview.md
    ↓
docs/architecture/context-map.md
```

---

### 11.2 Para compreender o domínio

```text
docs/architecture/canonical-domain-model.md
    ↓
docs/architecture/domain-aggregates-and-rules.md
```

---

### 11.3 Para acompanhar o desenvolvimento

```text
docs/development/roadmap.md
```

---

### 11.4 Para implementar integrações

```text
docs/architecture/domain-aggregates-and-rules.md
    ↓
docs/providers/
    ↓
docs/api/
```

---

### 11.5 Para implementar persistência

```text
docs/architecture/canonical-domain-model.md
    ↓
docs/architecture/domain-aggregates-and-rules.md
    ↓
docs/database/
```

---

## 12. Regras de manutenção

Toda alteração relevante no projeto deverá verificar se exige atualização da
documentação.

Deverão ser revisados:

- roadmap;
- README da raiz;
- README da documentação;
- documentos arquiteturais;
- documentação da API;
- documentação do banco;
- documentação de providers;
- documentação de deployment.

---

### 12.1 Alterações de domínio

Quando uma entidade, regra ou relacionamento mudar, revisar:

```text
docs/architecture/canonical-domain-model.md
docs/architecture/domain-aggregates-and-rules.md
docs/development/roadmap.md
```

---

### 12.2 Alterações de integração

Quando um provider ou fluxo de integração mudar, revisar:

```text
docs/providers/
docs/architecture/domain-aggregates-and-rules.md
docs/development/roadmap.md
```

---

### 12.3 Alterações de banco

Quando tabelas, constraints ou migrations mudarem, revisar:

```text
docs/database/
docs/architecture/canonical-domain-model.md
docs/development/roadmap.md
```

---

### 12.4 Alterações de API

Quando endpoints ou contratos mudarem, revisar:

```text
docs/api/
docs/development/roadmap.md
```

---

### 12.5 Alterações de deployment

Quando ambiente, configuração ou infraestrutura mudar, revisar:

```text
docs/deployment/
docs/development/roadmap.md
```

---

## 13. Convenções dos documentos

Os documentos deverão:

- utilizar Markdown;
- possuir título principal;
- utilizar seções numeradas quando necessário;
- utilizar nomes consistentes;
- utilizar caminhos relativos;
- evitar informações duplicadas;
- indicar documentos relacionados;
- registrar decisões importantes;
- preservar compatibilidade de links;
- utilizar exemplos claros;
- evitar depender de conhecimento implícito.

---

## 14. Links internos

Links entre documentos deverão utilizar caminhos relativos.

Exemplo:

```markdown
[Roadmap](development/roadmap.md)

[Motor de Recomendações](architecture/recommendation-engine.md)

[Gestão de Risco e Portfólio](architecture/risk-and-portfolio.md)

[Experiência do Usuário](architecture/user-experience.md)

[Motor ao Vivo](architecture/live-engine.md)

[Produção, Segurança e Escalabilidade](architecture/production-security-scalability.md)

[Runbook de Produção](operations/production-runbook.md)

[Release Candidate e Validação](architecture/release-candidate-validation.md)

[Release v0.1.0-rc.1](releases/v0.1.0-rc.1.md)

[Release v0.1.0-rc.2](releases/v0.1.0-rc.2.md)
```

Exemplo dentro de uma subpasta:

```markdown
[Modelo Canônico](../architecture/canonical-domain-model.md)
```

Não deverão ser utilizados caminhos absolutos do computador local.

Exemplo proibido:

```text
C:\Users\usuario\projeto\docs\arquivo.md
```

---

## 15. Estado atual da documentação

```text
G4.A — Arquitetura do Domínio
CONCLUÍDO

G4.B — Arquitetura de Providers
CONCLUÍDO

G4.C — Arquitetura de Dados
CONCLUÍDO

G4.D — Organização da Documentação
CONCLUÍDO

G5.7 — People e Team
CONCLUÍDO
```

Documentos arquiteturais principais concluídos:

```text
docs/architecture/canonical-domain-model.md
docs/architecture/domain-aggregates-and-rules.md
```

Documento de acompanhamento atualizado:

```text
docs/development/roadmap.md
```

Atividade documental atual:

```text
Evoluir a documentação juntamente com as fatias da G5.8 — Match e Tie.
```

---

## 16. Próxima etapa técnica

Após a conclusão da G5.7, a próxima etapa será:

```text
G5.8 — Match e Tie
```

O Match Context será construído sobre os contextos canônicos já consolidados de
Geography, Competition, People e Team.

---

## 17. Documentos principais

| Área | Documento |
|---|---|
| Visão geral | `architecture/domain-overview.md` |
| Contextos | `architecture/context-map.md` |
| Decisões arquiteturais | `architecture/architecture-decisions.md` |
| Modelo canônico | `architecture/canonical-domain-model.md` |
| Agregados e regras | `architecture/domain-aggregates-and-rules.md` |
| People | `architecture/people-domain.md` |
| Team | `architecture/team-domain.md` |
| Match | `architecture/match-domain.md` |
| Roadmap | `development/roadmap.md` |

---

## 18. Regra final

A documentação deverá evoluir juntamente com o projeto.

Uma funcionalidade não deverá ser considerada completamente concluída quando
existirem alterações obrigatórias de documentação ainda pendentes.
