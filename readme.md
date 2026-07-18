# UltraStats AI

Plataforma de análise quantitativa para apostas esportivas focada exclusivamente em futebol.

---

# Objetivos

O UltraStats AI tem como principais objetivos:

- armazenar partidas e estatísticas de futebol;
- consolidar dados provenientes de múltiplos provedores;
- calcular probabilidades utilizando modelos estatísticos;
- comparar probabilidades com odds de casas de apostas;
- identificar apostas com valor esperado positivo (Expected Value);
- registrar previsões;
- auditar resultados;
- acompanhar métricas de desempenho como ROI, Yield e Drawdown;
- fornecer recomendações explicáveis para apostas esportivas.

---

# Tecnologias

- Python
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Docker Compose
- Pandas
- Streamlit
- Git

---

# Status

## Etapa atual

O projeto encontra-se na etapa **G4.A.2 — Entidades Centrais do Futebol**.

Documentos principais:

- `docs/architecture/domain-overview.md`
- `docs/architecture/architecture-decisions.md`
- `docs/architecture/context-map.md`
- `docs/architecture/football-domain.md`
- `docs/architecture/provider-identity-mappings.md`
- `docs/architecture/match-lifecycle.md`

Projeto em desenvolvimento.

---

# Arquitetura atual

O projeto utiliza uma arquitetura em camadas.

- `models` representam as entidades persistidas.
- `repositories` concentram acesso ao banco de dados.
- `services` implementam as regras de negócio.
- `schemas` realizam validação e serialização.
- `core` contém configurações globais.
- `database` concentra infraestrutura de persistência.
- `utils` contém funções auxiliares reutilizáveis.
- `scripts` executam operações administrativas.
- `tests` validam o comportamento da aplicação.

---

# Estrutura principal

```text
app/
├── core/
├── database/
├── models/
├── repositories/
├── schemas/
├── services/
└── utils/
```
---

# Gestão de risco

O Dashboard Pro possui um simulador de stake baseado em:

- probabilidade estimada;
- odd decimal;
- valor esperado;
- Kelly Criterion;
- Kelly fracionado;
- limite máximo por aposta;
- exposição diária;
- perfis conservador, moderado e agressivo.

---

# Operações financeiras

O Dashboard Pro permite:

- criar bancas;
- realizar depósitos;
- realizar retiradas;
- realizar ajustes administrativos;
- ativar ou desativar bancas;
- consultar o histórico financeiro.

---

# Criação de apostas

O Dashboard Pro permite:

- selecionar uma partida aberta;
- selecionar o mercado;
- informar odd e probabilidade;
- simular Kelly e stake;
- aplicar o perfil de risco;
- registrar uma aposta oficial;
- debitar automaticamente a banca;
- impedir apostas duplicadas ou em partidas encerradas.

---

# Liquidação administrativa

O Dashboard Pro permite:

- selecionar uma partida aberta;
- informar o placar oficial;
- registrar escanteios, cartões e finalizações;
- registrar posse de bola;
- registrar xG;
- encerrar a partida;
- liquidar apostas pendentes;
- calcular lucro ou prejuízo;
- atualizar automaticamente a banca;
- criar auditorias pós-jogo.

---

# Cliente HTTP esportivo

A camada HTTP do UltraStats AI possui:

- API Key em variáveis de ambiente;
- timeout configurável;
- tentativas automáticas (retries);
- tratamento para HTTP 401, 403, 429 e erros 5xx;
- validação de JSON;
- logs em arquivo;
- modo sandbox;
- testes utilizando `httpx.MockTransport`.

As credenciais reais devem permanecer exclusivamente no arquivo `.env`.

---

# Monitoramento de sincronizações

Cada execução de um collector é registrada na tabela:

```text
sync_runs
```

As seguintes informações são armazenadas:

- provedor;
- status;
- horário de início;
- horário de término;
- duração;
- quantidade de registros criados;
- quantidade de registros atualizados;
- quantidade de entidades vinculadas;
- partidas ignoradas;
- mensagem de erro;
- origem da execução.

## Execução manual

```powershell
python -m scripts.sync_mock_provider
```
---

# Scheduler automático

O UltraStats AI pode executar sincronizações automaticamente por meio de um scheduler.

## Configuração

```env
SYNC_ENABLED=true
SYNC_INTERVAL_MINUTES=60
SYNC_PROVIDER=mock_provider
SYNC_MAX_RUNTIME_MINUTES=20
```

---

# Heartbeat do scheduler

O scheduler registra periodicamente seu estado na tabela:

```text
scheduler_heartbeats
```

Esse mecanismo permite verificar se o scheduler continua ativo mesmo quando nenhuma sincronização está sendo executada.

---

# Inicialização no Windows

Os scripts auxiliares para execução local encontram-se em:

```text
windows/
```

## Produção / Desenvolvimento

```powershell
.\windows\docker_start.bat
.\windows\docker_status.bat
.\windows\docker_stop.bat
```

---

# Logs do scheduler

O scheduler utiliza a configuração centralizada de logs do UltraStats AI.

Os registros são enviados simultaneamente para:

- terminal do Docker;
- arquivo persistente `logs/scheduler.log`;
- arquivo global `logs/errors.log`, quando o nível for `ERROR` ou superior.

## Configuração

```env
LOG_LEVEL=INFO
LOG_DIRECTORY=logs
LOG_MAX_BYTES=5000000
LOG_BACKUP_COUNT=5
LOG_CONSOLE_ENABLED=true
LOG_FILE_ENABLED=true
```

### Acompanhar logs pelo Docker

```powershell
docker compose logs -f scheduler
```

### Consultar o arquivo dentro do container

```powershell
docker exec ultrastats_scheduler tail -n 100 /app/logs/scheduler.log
```

---

# Logs do Dashboard

O Dashboard utiliza a configuração centralizada de logs.

Os eventos são gravados em:

```text
logs/dashboard.log
```

Erros também são registrados em:

```text
logs/errors.log
```

---

# Diagnóstico de logging

A configuração centralizada pode ser inspecionada utilizando:

```python
from app.core.logging_config import (
    get_logging_status,
)
```

Essa função permite verificar rapidamente a configuração atual do sistema de logging.

---

# Cliente HTTP para providers

O UltraStats AI possui um cliente HTTP reutilizável para integração com APIs esportivas externas.

## Recursos

- timeout configurável;
- tentativas automáticas (retries);
- backoff progressivo;
- controle de requisições por minuto (Rate Limiting);
- tratamento padronizado de falhas;
- suporte ao cabeçalho `Retry-After`;
- logging centralizado;
- testes utilizando transporte HTTP simulado.

## Componentes

```text
app/providers/http_client.py
app/providers/rate_limiter.py
app/providers/exceptions.py
```

## Configurações

```env
PROVIDER_HTTP_TIMEOUT_SECONDS=15
PROVIDER_HTTP_MAX_RETRIES=3
PROVIDER_HTTP_RETRY_DELAY_SECONDS=1
PROVIDER_DEFAULT_REQUESTS_PER_MINUTE=10
PROVIDER_USER_AGENT=UltraStats-AI/1.0
```

---

# Framework de Providers

O UltraStats AI utiliza um framework próprio para integração com múltiplos provedores de dados esportivos.

Todos os providers implementam uma interface comum, permitindo adicionar novos provedores sem alterar a lógica de negócio da aplicação.

## Componentes principais

```text
app/providers/base.py
app/providers/registry.py
app/providers/mock_provider.py
```

Cada provider declara:

- nome interno;
- nome de exibição;
- capacidades suportadas;
- necessidade de API Key;
- disponibilidade da integração;
- verificação de saúde (Health Check).

O registro global permite instanciar um provider pelo seu nome:

```python
from app.providers import provider_registry

provider = provider_registry.create("mock")
```

O provider padrão pode ser definido por variável de ambiente:

```env
PROVIDER_NAME=mock
```

---

# Capacidades previstas para os providers

Os providers poderão fornecer uma ou mais das seguintes capacidades:

```text
competitions
teams
matches
standings
players
coaches
referees
stadiums
lineups
injuries
suspensions
match_events
match_statistics
odds
expected_goals
```

Cada provider informará quais dessas capacidades suporta, permitindo que o sistema adapte automaticamente o fluxo de sincronização.

---

# Visão de longo prazo

A arquitetura do UltraStats AI foi projetada para trabalhar com múltiplos provedores simultaneamente.

O fluxo geral de processamento seguirá a seguinte estrutura:

```text
Providers
      │
      ▼
Collectors
      │
      ▼
Normalização
      │
      ▼
Resolução de Identidade
      │
      ▼
Data Fusion Engine
      │
      ▼
Domínio Canônico
      │
      ▼
Banco PostgreSQL
      │
      ▼
Motor Estatístico
      │
      ▼
Modelos Preditivos
      │
      ▼
Dashboard / API
```

Os dados provenientes dos provedores **nunca serão gravados diretamente nas tabelas principais**.

Todo dado deverá passar pelas etapas de:

- validação;
- normalização;
- resolução de identidade;
- fusão de dados;
- persistência no domínio canônico.

---

# Estado atual do projeto

Atualmente o projeto encontra-se na construção da arquitetura do domínio do futebol.

As próximas etapas incluem:

- modelagem das entidades canônicas;
- implementação do domínio em SQLAlchemy;
- integração com provedores reais;
- resolução automática de identidade;
- Data Fusion Engine;
- modelos estatísticos;
- motor de recomendações;
- dashboard avançado.

---

# Licença

Este projeto encontra-se em desenvolvimento e, até o momento, não possui uma licença pública definida.