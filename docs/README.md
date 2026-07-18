# Documentação do UltraStats AI

Esta pasta concentra a documentação técnica, arquitetural e operacional do UltraStats AI.

O objetivo é manter o `README.md` da raiz mais simples, utilizando esta área para conteúdos detalhados.

---

## Navegação

### Arquitetura

Documentos relacionados à arquitetura geral, domínio do futebol e decisões técnicas.

- [`architecture/domain-overview.md`](architecture/domain-overview.md)
- [`architecture/context-map.md`](architecture/context-map.md)
- [`architecture/architecture-decisions.md`](architecture/architecture-decisions.md)
- [`architecture/football-domain.md`](architecture/football-domain.md)
- [`architecture/provider-identity-mappings.md`](architecture/provider-identity-mappings.md)
- [`architecture/match-lifecycle.md`](architecture/match-lifecycle.md)

### Desenvolvimento

Documentação relacionada ao planejamento e ao processo de desenvolvimento.

- [`development/README.md`](development/README.md)
- [`development/roadmap.md`](development/roadmap.md)

Documentos disponíveis:

- Roadmap oficial.

Documentos previstos:

- changelog;
- padrões de código;
- convenções de commits;
- estratégia de testes.

### Implantação

Documentação relacionada à execução e implantação da aplicação.

- [`deployment/README.md`](deployment/README.md)

Documentos previstos:

- Docker;
- Docker Compose;
- configuração de ambiente;
- inicialização no Windows;
- scheduler;
- logs;
- monitoramento.

### Providers

Documentação relacionada às integrações com provedores externos de dados de futebol.

- [`providers/README.md`](providers/README.md)

Documentos previstos:

- framework de providers;
- configuração de credenciais;
- capacidades suportadas;
- coleta;
- normalização;
- tratamento de falhas;
- rate limiting;
- provedores integrados.

### Banco de Dados

Documentação relacionada à persistência dos dados.

- [`database/README.md`](database/README.md)

Documentos previstos:

- PostgreSQL;
- SQLAlchemy;
- Alembic;
- migrations;
- modelos canônicos;
- índices;
- integridade;
- auditoria.

### API

Documentação relacionada à futura API do UltraStats AI.

- [`api/README.md`](api/README.md)

Documentos previstos:

- endpoints;
- autenticação;
- schemas;
- respostas;
- erros;
- versionamento;
- exemplos de integração.

### Imagens

Arquivos visuais utilizados na documentação.

- [`images/README.md`](images/README.md)

Exemplos:

- diagramas;
- fluxos;
- capturas de tela;
- modelos de domínio;
- ilustrações de arquitetura.

---

## Estrutura atual

```text
docs/
├── README.md
├── api/
│   └── README.md
├── architecture/
│   ├── architecture-decisions.md
│   ├── context-map.md
│   ├── domain-overview.md
│   ├── football-domain.md
│   ├── match-lifecycle.md
│   └── provider-identity-mappings.md
├── database/
│   └── README.md
├── deployment/
│   └── README.md
├── development/
│   └── README.md
├── images/
│   └── README.md
└── providers/
    └── README.md
```

---

## Convenções

Os documentos deverão seguir estas orientações:

- utilizar Markdown;
- possuir um título principal;
- apresentar objetivo claro;
- evitar duplicação de conteúdo;
- utilizar links relativos;
- manter exemplos de código em blocos corretamente identificados;
- atualizar os índices sempre que novos documentos forem adicionados;
- preservar decisões arquiteturais relevantes em ADRs.

---

## Evolução

A documentação será ampliada conforme o desenvolvimento do projeto.

As próximas adições previstas são:

- roadmap oficial;
- changelog;
- documentação do Docker;
- documentação do scheduler;
- documentação de logging;
- documentação do framework de providers;
- documentação do modelo canônico;
- documentação da API.