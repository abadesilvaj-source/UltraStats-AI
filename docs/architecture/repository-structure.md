# Estrutura do repositório

## Princípio

A raiz contém apenas projetos executáveis, documentação e orquestração. Código
Python pertence ao `backend`; código React pertence ao `frontend`.

## Backend

| Caminho | Responsabilidade |
|---|---|
| `backend/api` | Rotas HTTP, serialização e consultas de leitura |
| `backend/app` | Configuração, banco operacional, ORM, serviços e provedores |
| `backend/src/ultrastats_ai` | Domínio canônico, motores e infraestrutura |
| `backend/migrations` | Histórico versionado do banco |
| `backend/scripts` | Entradas de scheduler, saúde, seeds e release |
| `backend/tests` | Testes de todo o backend |
| `backend/data` | Fixtures e dados locais explicitamente controlados |

O diretório de trabalho do backend é sempre `backend/`. Isso preserva imports
curtos (`app`, `api`, `ultrastats_ai`, `scripts`) sem adicionar pacotes da raiz
ao runtime.

## Frontend

| Caminho | Responsabilidade |
|---|---|
| `frontend/src/app` | Roteamento e composição das páginas |
| `frontend/src/App.tsx` | Componentes visuais de domínio compartilhados |
| `frontend/src/api.ts` | Contrato de acesso à API e adaptação de DTOs |
| `frontend/src/data.ts` | Tipos usados pela interface |
| `frontend/src/index.css` | Sistema visual |

O antigo aplicativo React duplicado foi removido; `main.tsx` possui apenas um
ponto de entrada, o `AppRouter`.

## Operação

`ops/` contém somente artefatos de operação:

- `ops/deploy/Caddyfile`: proxy de produção;
- `ops/windows`: atalhos locais para Docker e migrations.

Os arquivos Compose permanecem na raiz por convenção e usam contextos de build
independentes para backend e frontend.

## Componentes removidos

- dashboard Streamlit legado;
- scripts Windows do dashboard antigo;
- Dockerfile Python duplicado na raiz;
- dependências exclusivas do Streamlit e de visualização legada;
- implementação React antiga e não utilizada;
- caches, builds e artefatos temporários.
