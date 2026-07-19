# UltraStats AI

O UltraStats AI é uma plataforma de análise estatística, modelagem preditiva e
avaliação de oportunidades em partidas de futebol.

O projeto foi estruturado para reunir dados esportivos provenientes de múltiplas
fontes, transformá-los em um modelo canônico independente de providers e
utilizá-los na produção de estatísticas, probabilidades, previsões e
recomendações.

---

## 1. Objetivo do projeto

O objetivo do UltraStats AI é construir uma plataforma capaz de:

- coletar dados de múltiplos providers;
- armazenar payloads brutos;
- normalizar dados externos;
- resolver identidades;
- consolidar informações conflitantes;
- manter um domínio canônico de futebol;
- produzir estatísticas históricas;
- gerar features;
- executar modelos preditivos;
- calcular probabilidades próprias;
- calcular odds justas;
- identificar oportunidades;
- avaliar risco;
- registrar apostas e movimentações de banca;
- acompanhar o desempenho das previsões;
- preservar histórico, auditoria e proveniência.

---

## 2. Princípios arquiteturais

O UltraStats AI segue os seguintes princípios:

- domínio independente de providers;
- separação entre dados brutos, normalizados, canônicos e derivados;
- identidade canônica própria;
- histórico preservado;
- proveniência rastreável;
- processamento idempotente;
- integração orientada a eventos;
- consistência forte dentro dos agregados;
- consistência eventual entre contextos;
- modelos preditivos versionados;
- previsões imutáveis;
- documentação sincronizada com o desenvolvimento.

---

## 3. Arquitetura geral

O fluxo principal de dados será:

```text
Providers externos
    ↓
Collectors
    ↓
Raw Payloads
    ↓
Validação
    ↓
Normalização
    ↓
Resolução de identidade
    ↓
Fusão de dados
    ↓
Domínio canônico
    ↓
Estatísticas e features
    ↓
Modelos preditivos
    ↓
Previsões
    ↓
Recomendações
    ↓
Gestão de risco e banca
```

---

## 4. Contextos principais

A arquitetura foi dividida em contextos responsáveis por áreas específicas do
domínio.

```text
Geography
Competition
People
Team
Match
Identity Resolution
Data Fusion
Betting Market
Statistics
Prediction
Recommendation
Risk and Portfolio
Provider Integration
```

Cada contexto possui responsabilidades próprias e não deverá alterar diretamente
dados pertencentes a outro contexto.

---

## 5. Domínio canônico

O domínio canônico representa a visão oficial dos dados dentro do UltraStats AI.

Ele não deverá utilizar diretamente:

- nomes de campos específicos de providers;
- identificadores externos como identificadores principais;
- status exclusivos de uma API;
- estruturas particulares de payloads;
- regras implícitas de uma única fonte.

Os providers serão integrados por meio de:

- identificadores externos;
- normalização;
- resolução de identidade;
- fusão de dados;
- proveniência;
- comandos canônicos.

---

## 6. Documentação

A documentação principal está localizada em:

```text
docs/
```

Índice da documentação:

```text
docs/README.md
```

Roadmap:

```text
docs/development/roadmap.md
```

Documentos arquiteturais principais:

```text
docs/architecture/domain-overview.md
docs/architecture/context-map.md
docs/architecture/architecture-decisions.md
docs/architecture/canonical-domain-model.md
docs/architecture/domain-aggregates-and-rules.md
```

---

## 7. Ordem recomendada de leitura

Para compreender o projeto:

```text
README.md
    ↓
docs/README.md
    ↓
docs/architecture/domain-overview.md
    ↓
docs/architecture/context-map.md
```

Para compreender o domínio:

```text
docs/architecture/canonical-domain-model.md
    ↓
docs/architecture/domain-aggregates-and-rules.md
```

Para acompanhar o desenvolvimento:

```text
docs/development/roadmap.md
```

---

## 8. Estrutura principal do projeto

A estrutura poderá evoluir durante o desenvolvimento, mas deverá preservar a
separação entre domínio, aplicação, infraestrutura, integrações, testes e
documentação.

```text
ultrastats-ai/
├── src/
├── tests/
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── database/
│   ├── deployment/
│   ├── development/
│   ├── images/
│   └── providers/
├── scripts/
├── migrations/
├── README.md
└── CHANGELOG.md
```

A estrutura real do código será consolidada durante:

```text
G5.1 — Estrutura dos Pacotes do Domínio
```

---

## 9. Tecnologias previstas

As tecnologias deverão ser confirmadas durante as etapas de implementação.

Base prevista:

- Python;
- PostgreSQL;
- SQLAlchemy;
- Alembic;
- Pydantic;
- Pytest;
- Docker;
- APIs HTTP;
- processamento assíncrono;
- modelos estatísticos e de machine learning.

A adoção definitiva de bibliotecas deverá ser registrada na documentação
arquitetural ou em decisões específicas.

---

## 10. Estado atual

```text
G1 — Fundação do Projeto
CONCLUÍDO

G2 — Banco de Dados
CONCLUÍDO

G3 — Coleta de Dados
CONCLUÍDO

G4 — Arquitetura do Domínio
EM ANDAMENTO

G4.A — Arquitetura do Domínio
CONCLUÍDO

G4.B — Arquitetura de Providers
CONCLUÍDO

G4.C — Arquitetura de Dados
CONCLUÍDO

G4.D — Organização da Documentação
EM ANDAMENTO

G5 — Domínio Canônico
PLANEJADO
```

A arquitetura técnica principal da G4 está concluída.

A atividade atual é finalizar a organização documental antes do início da
implementação do domínio canônico.

---

## 11. Próxima fase técnica

Após a conclusão da G4.D, será iniciada:

```text
G5 — Domínio Canônico
```

Primeira etapa:

```text
G5.1 — Estrutura dos Pacotes do Domínio
```

O G5 transformará a arquitetura em:

- módulos Python;
- entidades;
- Aggregate Roots;
- Value Objects;
- enums;
- Domain Services;
- Domain Policies;
- repositories;
- Unit of Work;
- modelos SQLAlchemy;
- migrations;
- constraints;
- testes automatizados.

---

## 12. Roadmap

O roadmap oficial está disponível em:

[Roadmap do UltraStats AI](docs/development/roadmap.md)

O roadmap deverá ser utilizado como referência para:

- etapa atual;
- etapas concluídas;
- próximas etapas;
- dependências;
- entregas;
- mudanças de escopo.

---

## 13. Documentação arquitetural

### Modelo canônico

[Modelo Canônico do Domínio](docs/architecture/canonical-domain-model.md)

Define:

- entidades;
- atributos;
- relacionamentos;
- ciclos de vida;
- regras estruturais;
- histórico esportivo.

### Agregados e regras

[Agregados e Regras do Domínio](docs/architecture/domain-aggregates-and-rules.md)

Define:

- Bounded Contexts;
- Aggregate Roots;
- ownership;
- Value Objects;
- invariantes;
- serviços;
- políticas;
- eventos;
- transações;
- concorrência;
- histórico;
- integração;
- processamento analítico.

---

## 14. Desenvolvimento

Antes de implementar uma nova funcionalidade, deverá ser verificado:

1. se a funcionalidade pertence à etapa atual;
2. qual contexto é responsável;
3. qual Aggregate Root controla a alteração;
4. quais regras de domínio devem ser respeitadas;
5. quais documentos precisam ser atualizados;
6. quais testes serão necessários.

Funcionalidades fora da etapa atual deverão ser registradas no roadmap em vez de
serem implementadas sem planejamento.

---

## 15. Testes

O projeto deverá possuir testes para:

- Value Objects;
- entidades;
- Aggregate Roots;
- invariantes;
- Domain Services;
- Domain Policies;
- repositories;
- Unit of Work;
- migrations;
- integrações;
- idempotência;
- concorrência;
- contratos;
- reprocessamento;
- modelos preditivos.

Os comandos definitivos de execução serão documentados quando a estrutura do G5
for criada.

---

## 16. Changelog

O histórico de alterações relevantes está disponível em:

[CHANGELOG.md](CHANGELOG.md)

O changelog deverá registrar:

- novas funcionalidades;
- alterações arquiteturais;
- mudanças incompatíveis;
- correções relevantes;
- remoções;
- mudanças de documentação que alterem o planejamento oficial.

---

## 17. Regra de documentação

Uma etapa não deverá ser considerada totalmente concluída enquanto existirem
alterações obrigatórias de documentação pendentes.

Sempre que necessário, deverão ser atualizados:

- README principal;
- índice da documentação;
- roadmap;
- changelog;
- documentos arquiteturais;
- documentação de banco;
- documentação de providers;
- documentação de API;
- documentação de deployment.