# UltraStats AI

Plataforma de análise quantitativa para apostas esportivas.

## Objetivos

- Armazenar jogos e estatísticas.
- Calcular probabilidades.
- Comparar probabilidades com odds.
- Identificar apostas com valor esperado positivo.
- Registrar resultados.
- Auditar previsões.
- Acompanhar ROI, CLV, Yield e Drawdown.

## Tecnologias

- Python
- PostgreSQL
- Docker
- SQLAlchemy
- Pandas
- Streamlit
- Git

## Status

Projeto em desenvolvimento.
## Arquitetura atual

O projeto utiliza uma arquitetura em camadas:

- `models`: representam as tabelas do banco.
- `repositories`: realizam consultas e persistência.
- `services`: concentram regras de negócio.
- `scripts`: executam tarefas manuais.
- `tests`: validam o comportamento do sistema.

## Estrutura principal

```text
app/
├── core/
├── database/
├── models/
├── repositories/
├── schemas/
├── services/
└── utils/

## Gestão de risco

O Dashboard Pro possui um simulador de stake baseado em:

- probabilidade estimada;
- odd decimal;
- valor esperado;
- Kelly Criterion;
- Kelly fracionado;
- limite máximo por aposta;
- exposição diária;
- perfis conservador, moderado e agressivo.

## Operações financeiras

O Dashboard Pro permite:

- criar bancas;
- realizar depósitos;
- realizar retiradas;
- realizar ajustes administrativos;
- ativar ou desativar bancas;
- consultar o histórico financeiro.

## Criação de apostas

O Dashboard Pro permite:

- selecionar uma partida aberta;
- selecionar o mercado;
- informar odd e probabilidade;
- simular Kelly e stake;
- aplicar o perfil de risco;
- registrar uma aposta oficial;
- debitar automaticamente a banca;
- impedir apostas duplicadas ou em partidas encerradas.

## Liquidação administrativa

O Dashboard Pro permite:

- selecionar uma partida aberta;
- informar o placar oficial;
- registrar escanteios, cartões e finalizações;
- registrar posse de bola e xG;
- encerrar a partida;
- liquidar apostas pendentes;
- calcular lucro ou prejuízo;
- atualizar a banca;
- criar auditorias pós-jogo.

## Cliente HTTP esportivo

A camada HTTP do UltraStats AI possui:

- API key em variáveis de ambiente;
- timeout configurável;
- tentativas automáticas;
- tratamento de HTTP 401, 403, 429 e 5xx;
- validação de JSON;
- logs em arquivo;
- modo sandbox;
- testes com `httpx.MockTransport`.

As credenciais reais devem permanecer apenas no arquivo `.env`.

## Monitoramento de sincronizações

Cada execução de collector é registrada em `sync_runs`.

Informações registradas:

- provedor;
- status;
- início e fim;
- duração;
- quantidades criadas;
- quantidades atualizadas;
- quantidades vinculadas;
- partidas ignoradas;
- mensagem de erro;
- origem do acionamento.

### Execução manual

```powershell
python -m scripts.sync_mock_provider

## Scheduler automático

O UltraStats AI pode executar sincronizações automaticamente.

### Configuração

```env
SYNC_ENABLED=true
SYNC_INTERVAL_MINUTES=60
SYNC_PROVIDER=mock_provider
SYNC_MAX_RUNTIME_MINUTES=20

## Heartbeat do scheduler

O scheduler registra seu estado na tabela:

```text
scheduler_heartbeats

## Inicialização no Windows

Os scripts de inicialização estão na pasta:

```text
windows



## Inicialização

### Produção / Desenvolvimento (recomendado)

```powershell
.\windows\docker_start.bat
.\windows\docker_status.bat
.\windows\docker_stop.bat

## Logs do scheduler

O scheduler utiliza a configuração centralizada de logs do UltraStats AI.

Os logs são enviados simultaneamente para:

- terminal do Docker;
- arquivo persistente `logs/scheduler.log`;
- arquivo global `logs/errors.log`, quando o nível é `ERROR` ou superior.

Configurações disponíveis:

```env
LOG_LEVEL=INFO
LOG_DIRECTORY=logs
LOG_MAX_BYTES=5000000
LOG_BACKUP_COUNT=5
LOG_CONSOLE_ENABLED=true
LOG_FILE_ENABLED=true

Para acompanhar os logs pelo Docker:

docker compose logs -f scheduler

Para consultar o arquivo dentro do container:

docker exec ultrastats_scheduler tail -n 100 /app/logs/scheduler.log

## Logs do Dashboard

O Dashboard utiliza a configuração centralizada de logs.

Os eventos são gravados em:

```text
logs/dashboard.log

Erros também são enviados para:

logs/errors.log

## Diagnóstico de logging

A configuração centralizada de logs pode ser inspecionada pela função:

```python
from app.core.logging_config import (
    get_logging_status,
)

## Cliente HTTP para providers

O UltraStats AI possui um cliente HTTP reutilizável para integração com APIs externas.

Recursos:

- timeout configurável;
- retries automáticos;
- backoff progressivo;
- controle de requisições por minuto;
- tratamento padronizado de falhas;
- suporte ao cabeçalho `Retry-After`;
- logs;
- testes com transporte HTTP simulado.

Componentes:

```text
app/providers/http_client.py
app/providers/rate_limiter.py
app/providers/exceptions.py

Configurações:

PROVIDER_HTTP_TIMEOUT_SECONDS=15
PROVIDER_HTTP_MAX_RETRIES=3
PROVIDER_HTTP_RETRY_DELAY_SECONDS=1
PROVIDER_DEFAULT_REQUESTS_PER_MINUTE=10
PROVIDER_USER_AGENT=UltraStats-AI/1.0