# UltraStats AI

> Estado atual: operação exclusivamente local. O roadmap vigente é
> [docs/development/next-steps-roadmap.md](docs/development/next-steps-roadmap.md).
> Hospedagem externa permanece pausada até nova autorização explícita.

Plataforma pessoal de inteligência para futebol, com coleta multiprovedor,
conciliação de dados, estatísticas, previsões, recomendações, gestão de risco e
controle de banca.

## Estrutura

```text
UltraStats AI/
├── backend/                 # Todo o sistema Python
│   ├── api/                 # API FastAPI
│   ├── app/                 # Serviços operacionais, ORM, provedores e scheduler
│   ├── src/ultrastats_ai/   # Domínio canônico e infraestrutura
│   ├── migrations/          # Alembic
│   ├── scripts/             # Rotinas operacionais
│   ├── tests/               # Testes unitários e de integração
│   ├── data/                # Dados locais controlados
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements*.txt
├── frontend/                # Aplicação React + TypeScript
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docs/                    # Arquitetura, operação e decisões
├── ops/                     # Proxy e comandos auxiliares
├── docker-compose.yml       # Ambiente local
├── docker-compose.staging.yml
└── docker-compose.production.yml
```

Detalhes da organização estão em
[docs/architecture/repository-structure.md](docs/architecture/repository-structure.md).

A arquitetura dos motores e do ciclo científico está em
[docs/architecture/intelligence-platform-v2.md](docs/architecture/intelligence-platform-v2.md).

O pipeline atual combina baseline Poisson/Elo com ML temporal aprovado fora da
amostra. Ensembles reais operam em champion/challenger para resultados e gols;
na ausência de modelo aprovado, a inferência usa o baseline determinístico.

## Execução com Docker

Na raiz:

```powershell
docker compose up -d --build
docker compose ps
```

- Aplicação: `http://localhost:8516`
- Aplicação mobile: `http://localhost:8517`
- API: `http://localhost:8000/api/v1/health`

Para encerrar:

```powershell
docker compose down
```

## Desenvolvimento do backend

Execute os comandos dentro de `backend/`:

```powershell
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m pytest
python -m uvicorn api.main:app --reload --port 8000
python -m scripts.run_scheduler
```

O backend mantém dois níveis complementares:

- `app`: aplicação operacional atualmente persistida pelo SQLAlchemy;
- `ultrastats_ai`: domínio canônico, motores e infraestrutura de longo prazo.

## Desenvolvimento do frontend

Execute dentro de `frontend/`:

```powershell
pnpm install
pnpm dev
pnpm build
```

O frontend acessa `/api/v1` e, em Docker, o Nginx encaminha as chamadas ao
serviço `backend`.

## Configuração

Copie `.env.example` para `.env` e preencha somente as credenciais dos
provedores utilizados. Nunca versione chaves reais. Os ambientes de staging e
produção possuem exemplos próprios.

## Qualidade

Arquitetura de confiabilidade: [Recommendation accuracy v3](docs/architecture/recommendation-accuracy-v3.md).

As validações principais são:

```powershell
cd backend
python -m pytest
python -m alembic heads
cd ..\frontend
pnpm build
```

O pipeline do GitHub valida backend e frontend separadamente e publica imagens
independentes em releases.
