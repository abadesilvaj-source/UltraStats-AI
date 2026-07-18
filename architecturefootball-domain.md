[1mdiff --git a/docs/architecture/architecture-decisions.md b/docs/architecture/architecture-decisions.md[m
[1mindex 68b0225..5310a08 100644[m
[1m--- a/docs/architecture/architecture-decisions.md[m
[1m+++ b/docs/architecture/architecture-decisions.md[m
[36m@@ -234,4 +234,143 @@[m [mProbabilidades e recomendações serão apresentadas como estimativas.[m
 Consequência:[m
 [m
 A interface deverá incluir comunicação de risco e recursos de jogo[m
[31m-responsável.[m
\ No newline at end of file[m
[32m+[m[32mresponsável.[m
[32m+[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m## ADR-018 — UUID como identificador canônico[m
[32m+[m
[32m+[m[32m**Status:** Aprovada[m
[32m+[m
[32m+[m[32m### Decisão[m
[32m+[m
[32m+[m[32mTodas as entidades canônicas do UltraStats AI utilizarão identificadores internos[m
[32m+[m[32m(UUID), independentes dos identificadores fornecidos pelos provedores externos.[m
[32m+[m
[32m+[m[32m### Motivação[m
[32m+[m
[32m+[m[32mCada provedor utiliza seus próprios identificadores. Caso esses IDs sejam usados[m
[32m+[m[32mcomo chave principal do sistema, a troca ou inclusão de novos provedores se torna[m
[32m+[m[32mcomplexa.[m
[32m+[m
[32m+[m[32mAo utilizar um UUID interno, a identidade da entidade permanece estável mesmo[m
[32m+[m[32mque um provedor seja removido ou substituído.[m
[32m+[m
[32m+[m[32m### Consequências[m
[32m+[m
[32m+[m[32m- O domínio passa a ser independente dos provedores.[m
[32m+[m[32m- Um mesmo objeto pode possuir vários identificadores externos.[m
[32m+[m[32m- Os identificadores externos serão armazenados em estruturas de mapeamento.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m## ADR-019 — Histórico de vínculos esportivos[m
[32m+[m
[32m+[m[32m**Status:** Aprovada[m
[32m+[m
[32m+[m[32m### Decisão[m
[32m+[m
[32m+[m[32mOs vínculos entre jogadores, treinadores, equipes e estádios deverão preservar[m
[32m+[m[32mo histórico completo.[m
[32m+[m
[32m+[m[32m### Motivação[m
[32m+[m
[32m+[m[32mJogadores mudam de clube.[m
[32m+[m
[32m+[m[32mTreinadores mudam de equipe.[m
[32m+[m
[32m+[m[32mClubes mudam de estádio.[m
[32m+[m
[32m+[m[32mEssas alterações não podem sobrescrever informações antigas.[m
[32m+[m
[32m+[m[32m### Consequências[m
[32m+[m
[32m+[m[32m- Transferências poderão ser analisadas historicamente.[m
[32m+[m[32m- Estatísticas antigas continuarão consistentes.[m
[32m+[m[32m- Modelos preditivos poderão utilizar informações históricas.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m## ADR-020 — Partidas possuem ciclo de vida explícito[m
[32m+[m
[32m+[m[32m**Status:** Aprovada[m
[32m+[m
[32m+[m[32m### Decisão[m
[32m+[m
[32m+[m[32mUma partida deverá possuir estados bem definidos e transições controladas.[m
[32m+[m
[32m+[m[32m### Motivação[m
[32m+[m
[32m+[m[32mNem todas as partidas seguem o fluxo simples:[m
[32m+[m
[32m+[m[32m```text[m
[32m+[m[32mAgendada → Em andamento → Finalizada[m
[32m+[m[32m```[m
[32m+[m
[32m+[m[32mTambém existem situações como:[m
[32m+[m
[32m+[m[32m- adiamento;[m
[32m+[m[32m- atraso;[m
[32m+[m[32m- suspensão;[m
[32m+[m[32m- abandono;[m
[32m+[m[32m- resultado administrativo;[m
[32m+[m[32m- disputa por pênaltis.[m
[32m+[m
[32m+[m[32m### Consequências[m
[32m+[m
[32m+[m[32mO sistema poderá tratar corretamente cada situação sem ambiguidades.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m## ADR-021 — Escalação provável e confirmada são registros diferentes[m
[32m+[m
[32m+[m[32m**Status:** Aprovada[m
[32m+[m
[32m+[m[32m### Decisão[m
[32m+[m
[32m+[m[32mEscalações previstas e escalações confirmadas deverão ser armazenadas como[m
[32m+[m[32mregistros independentes.[m
[32m+[m
[32m+[m[32m### Motivação[m
[32m+[m
[32m+[m[32mUma escalação provável representa uma previsão.[m
[32m+[m
[32m+[m[32mUma escalação confirmada representa um fato observado.[m
[32m+[m
[32m+[m[32mA previsão não deve ser perdida quando a confirmação ocorrer.[m
[32m+[m
[32m+[m[32m### Consequências[m
[32m+[m
[32m+[m[32mSerá possível:[m
[32m+[m
[32m+[m[32m- comparar previsão e realidade;[m
[32m+[m[32m- medir a qualidade das previsões;[m
[32m+[m[32m- analisar o impacto das alterações de última hora.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m## ADR-022 — Dados históricos não serão removidos por inatividade[m
[32m+[m
[32m+[m[32m**Status:** Aprovada[m
[32m+[m
[32m+[m[32m### Decisão[m
[32m+[m
[32m+[m[32mEntidades esportivas históricas utilizarão inativação lógica.[m
[32m+[m
[32m+[m[32m### Motivação[m
[32m+[m
[32m+[m[32mEquipes, jogadores, treinadores e competições antigas continuam sendo[m
[32m+[m[32mreferenciados por partidas e estatísticas.[m
[32m+[m
[32m+[m[32mRemovê-los fisicamente quebraria o histórico.[m
[32m+[m
[32m+[m[32m### Consequências[m
[32m+[m
[32m+[m[32mSerá utilizado, sempre que aplicável:[m
[32m+[m
[32m+[m[32m```text[m
[32m+[m[32mis_active = false[m
[32m+[m[32m```[m
[32m+[m
[32m+[m[32mA exclusão física ficará restrita a registros criados por erro ou duplicidade.[m
[1mdiff --git a/docs/architecture/domain-overview.md b/docs/architecture/domain-overview.md[m
[1mindex 1867bdd..c628589 100644[m
[1m--- a/docs/architecture/domain-overview.md[m
[1m+++ b/docs/architecture/domain-overview.md[m
[36m@@ -229,6 +229,13 @@[m [mNão contém probabilidades de aposta nem recomendações.[m
 [m
 ---[m
 [m
[32m+[m[32mDocumentos detalhados:[m
[32m+[m
[32m+[m[32m- `docs/architecture/football-domain.md`[m
[32m+[m[32m- `docs/architecture/provider-identity-mappings.md`[m
[32m+[m[32m- `docs/architecture/match-lifecycle.md`[m
[32m+[m
[32m+[m
 ## 9. Statistics Context[m
 [m
 Responsável por estatísticas observadas e derivadas.[m
[1mdiff --git a/readme.md b/readme.md[m
[1mindex 10c344b..9877bbc 100644[m
[1m--- a/readme.md[m
[1m+++ b/readme.md[m
[36m@@ -1,41 +1,75 @@[m
 # UltraStats AI[m
 [m
[31m-Plataforma de análise quantitativa para apostas esportivas.[m
[32m+[m[32mPlataforma de análise quantitativa para apostas esportivas focada exclusivamente em futebol.[m
 [m
[31m-## Objetivos[m
[32m+[m[32m---[m
 [m
[31m-- Armazenar jogos e estatísticas.[m
[31m-- Calcular probabilidades.[m
[31m-- Comparar probabilidades com odds.[m
[31m-- Identificar apostas com valor esperado positivo.[m
[31m-- Registrar resultados.[m
[31m-- Auditar previsões.[m
[31m-- Acompanhar ROI, CLV, Yield e Drawdown.[m
[32m+[m[32m# Objetivos[m
 [m
[31m-## Tecnologias[m
[32m+[m[32mO UltraStats AI tem como principais objetivos:[m
[32m+[m
[32m+[m[32m- armazenar partidas e estatísticas de futebol;[m
[32m+[m[32m- consolidar dados provenientes de múltiplos provedores;[m
[32m+[m[32m- calcular probabilidades utilizando modelos estatísticos;[m
[32m+[m[32m- comparar probabilidades com odds de casas de apostas;[m
[32m+[m[32m- identificar apostas com valor esperado positivo (Expected Value);[m
[32m+[m[32m- registrar previsões;[m
[32m+[m[32m- auditar resultados;[m
[32m+[m[32m- acompanhar métricas de desempenho como ROI, Yield e Drawdown;[m
[32m+[m[32m- fornecer recomendações explicáveis para apostas esportivas.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Tecnologias[m
 [m
 - Python[m
 - PostgreSQL[m
[31m-- Docker[m
 - SQLAlchemy[m
[32m+[m[32m- Alembic[m
[32m+[m[32m- Docker[m
[32m+[m[32m- Docker Compose[m
 - Pandas[m
 - Streamlit[m
 - Git[m
 [m
[31m-## Status[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Status[m
[32m+[m
[32m+[m[32m## Etapa atual[m
[32m+[m
[32m+[m[32mO projeto encontra-se na etapa **G4.A.2 — Entidades Centrais do Futebol**.[m
[32m+[m
[32m+[m[32mDocumentos principais:[m
[32m+[m
[32m+[m[32m- `docs/architecture/domain-overview.md`[m
[32m+[m[32m- `docs/architecture/architecture-decisions.md`[m
[32m+[m[32m- `docs/architecture/context-map.md`[m
[32m+[m[32m- `docs/architecture/football-domain.md`[m
[32m+[m[32m- `docs/architecture/provider-identity-mappings.md`[m
[32m+[m[32m- `docs/architecture/match-lifecycle.md`[m
 [m
 Projeto em desenvolvimento.[m
[31m-## Arquitetura atual[m
 [m
[31m-O projeto utiliza uma arquitetura em camadas:[m
[32m+[m[32m---[m
 [m
[31m-- `models`: representam as tabelas do banco.[m
[31m-- `repositories`: realizam consultas e persistência.[m
[31m-- `services`: concentram regras de negócio.[m
[31m-- `scripts`: executam tarefas manuais.[m
[31m-- `tests`: validam o comportamento do sistema.[m
[32m+[m[32m# Arquitetura atual[m
 [m
[31m-## Estrutura principal[m
[32m+[m[32mO projeto utiliza uma arquitetura em camadas.[m
[32m+[m
[32m+[m[32m- `models` representam as entidades persistidas.[m
[32m+[m[32m- `repositories` concentram acesso ao banco de dados.[m
[32m+[m[32m- `services` implementam as regras de negócio.[m
[32m+[m[32m- `schemas` realizam validação e serialização.[m
[32m+[m[32m- `core` contém configurações globais.[m
[32m+[m[32m- `database` concentra infraestrutura de persistência.[m
[32m+[m[32m- `utils` contém funções auxiliares reutilizáveis.[m
[32m+[m[32m- `scripts` executam operações administrativas.[m
[32m+[m[32m- `tests` validam o comportamento da aplicação.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Estrutura principal[m
 [m
 ```text[m
 app/[m
[36m@@ -46,8 +80,10 @@[m [mapp/[m
 ├── schemas/[m
 ├── services/[m
 └── utils/[m
[32m+[m[32m```[m
[32m+[m[32m---[m
 [m
[31m-## Gestão de risco[m
[32m+[m[32m# Gestão de risco[m
 [m
 O Dashboard Pro possui um simulador de stake baseado em:[m
 [m
[36m@@ -60,7 +96,9 @@[m [mO Dashboard Pro possui um simulador de stake baseado em:[m
 - exposição diária;[m
 - perfis conservador, moderado e agressivo.[m
 [m
[31m-## Operações financeiras[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Operações financeiras[m
 [m
 O Dashboard Pro permite:[m
 [m
[36m@@ -71,7 +109,9 @@[m [mO Dashboard Pro permite:[m
 - ativar ou desativar bancas;[m
 - consultar o histórico financeiro.[m
 [m
[31m-## Criação de apostas[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Criação de apostas[m
 [m
 O Dashboard Pro permite:[m
 [m
[36m@@ -84,105 +124,127 @@[m [mO Dashboard Pro permite:[m
 - debitar automaticamente a banca;[m
 - impedir apostas duplicadas ou em partidas encerradas.[m
 [m
[31m-## Liquidação administrativa[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Liquidação administrativa[m
 [m
 O Dashboard Pro permite:[m
 [m
 - selecionar uma partida aberta;[m
 - informar o placar oficial;[m
 - registrar escanteios, cartões e finalizações;[m
[31m-- registrar posse de bola e xG;[m
[32m+[m[32m- registrar posse de bola;[m
[32m+[m[32m- registrar xG;[m
 - encerrar a partida;[m
 - liquidar apostas pendentes;[m
 - calcular lucro ou prejuízo;[m
[31m-- atualizar a banca;[m
[32m+[m[32m- atualizar automaticamente a banca;[m
 - criar auditorias pós-jogo.[m
 [m
[31m-## Cliente HTTP esportivo[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Cliente HTTP esportivo[m
 [m
 A camada HTTP do UltraStats AI possui:[m
 [m
[31m-- API key em variáveis de ambiente;[m
[32m+[m[32m- API Key em variáveis de ambiente;[m
 - timeout configurável;[m
[31m-- tentativas automáticas;[m
[31m-- tratamento de HTTP 401, 403, 429 e 5xx;[m
[32m+[m[32m- tentativas automáticas (retries);[m
[32m+[m[32m- tratamento para HTTP 401, 403, 429 e erros 5xx;[m
 - validação de JSON;[m
 - logs em arquivo;[m
 - modo sandbox;[m
[31m-- testes com `httpx.MockTransport`.[m
[32m+[m[32m- testes utilizando `httpx.MockTransport`.[m
 [m
[31m-As credenciais reais devem permanecer apenas no arquivo `.env`.[m
[32m+[m[32mAs credenciais reais devem permanecer exclusivamente no arquivo `.env`.[m
 [m
[31m-## Monitoramento de sincronizações[m
[32m+[m[32m---[m
 [m
[31m-Cada execução de collector é registrada em `sync_runs`.[m
[32m+[m[32m# Monitoramento de sincronizações[m
 [m
[31m-Informações registradas:[m
[32m+[m[32mCada execução de um collector é registrada na tabela:[m
[32m+[m
[32m+[m[32m```text[m
[32m+[m[32msync_runs[m
[32m+[m[32m```[m
[32m+[m
[32m+[m[32mAs seguintes informações são armazenadas:[m
 [m
 - provedor;[m
 - status;[m
[31m-- início e fim;[m
[32m+[m[32m- horário de início;[m
[32m+[m[32m- horário de término;[m
 - duração;[m
[31m-- quantidades criadas;[m
[31m-- quantidades atualizadas;[m
[31m-- quantidades vinculadas;[m
[32m+[m[32m- quantidade de registros criados;[m
[32m+[m[32m- quantidade de registros atualizados;[m
[32m+[m[32m- quantidade de entidades vinculadas;[m
 - partidas ignoradas;[m
 - mensagem de erro;[m
[31m-- origem do acionamento.[m
[32m+[m[32m- origem da execução.[m
 [m
[31m-### Execução manual[m
[32m+[m[32m## Execução manual[m
 [m
 ```powershell[m
 python -m scripts.sync_mock_provider[m
[32m+[m[32m```[m
[32m+[m[32m---[m
 [m
[31m-## Scheduler automático[m
[32m+[m[32m# Scheduler automático[m
 [m
[31m-O UltraStats AI pode executar sincronizações automaticamente.[m
[32m+[m[32mO UltraStats AI pode executar sincronizações automaticamente por meio de um scheduler.[m
 [m
[31m-### Configuração[m
[32m+[m[32m## Configuração[m
 [m
 ```env[m
 SYNC_ENABLED=true[m
 SYNC_INTERVAL_MINUTES=60[m
 SYNC_PROVIDER=mock_provider[m
 SYNC_MAX_RUNTIME_MINUTES=20[m
[32m+[m[32m```[m
 [m
[31m-## Heartbeat do scheduler[m
[32m+[m[32m---[m
 [m
[31m-O scheduler registra seu estado na tabela:[m
[32m+[m[32m# Heartbeat do scheduler[m
[32m+[m
[32m+[m[32mO scheduler registra periodicamente seu estado na tabela:[m
 [m
 ```text[m
 scheduler_heartbeats[m
[32m+[m[32m```[m
 [m
[31m-## Inicialização no Windows[m
[31m-[m
[31m-Os scripts de inicialização estão na pasta:[m
[32m+[m[32mEsse mecanismo permite verificar se o scheduler continua ativo mesmo quando nenhuma sincronização está sendo executada.[m
 [m
[31m-```text[m
[31m-windows[m
[32m+[m[32m---[m
 [m
[32m+[m[32m# Inicialização no Windows[m
 [m
[32m+[m[32mOs scripts auxiliares para execução local encontram-se em:[m
 [m
[31m-## Inicialização[m
[32m+[m[32m```text[m
[32m+[m[32mwindows/[m
[32m+[m[32m```[m
 [m
[31m-### Produção / Desenvolvimento (recomendado)[m
[32m+[m[32m## Produção / Desenvolvimento[m
 [m
 ```powershell[m
 .\windows\docker_start.bat[m
 .\windows\docker_status.bat[m
 .\windows\docker_stop.bat[m
[32m+[m[32m```[m
 [m
[31m-## Logs do scheduler[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Logs do scheduler[m
 [m
 O scheduler utiliza a configuração centralizada de logs do UltraStats AI.[m
 [m
[31m-Os logs são enviados simultaneamente para:[m
[32m+[m[32mOs registros são enviados simultaneamente para:[m
 [m
 - terminal do Docker;[m
 - arquivo persistente `logs/scheduler.log`;[m
[31m-- arquivo global `logs/errors.log`, quando o nível é `ERROR` ou superior.[m
[32m+[m[32m- arquivo global `logs/errors.log`, quando o nível for `ERROR` ou superior.[m
 [m
[31m-Configurações disponíveis:[m
[32m+[m[32m## Configuração[m
 [m
 ```env[m
 LOG_LEVEL=INFO[m
[36m@@ -191,16 +253,23 @@[m [mLOG_MAX_BYTES=5000000[m
 LOG_BACKUP_COUNT=5[m
 LOG_CONSOLE_ENABLED=true[m
 LOG_FILE_ENABLED=true[m
[32m+[m[32m```[m
 [m
[31m-Para acompanhar os logs pelo Docker:[m
[32m+[m[32m### Acompanhar logs pelo Docker[m
 [m
[32m+[m[32m```powershell[m
 docker compose logs -f scheduler[m
[32m+[m[32m```[m
 [m
[31m-Para consultar o arquivo dentro do container:[m
[32m+[m[32m### Consultar o arquivo dentro do container[m
 [m
[32m+[m[32m```powershell[m
 docker exec ultrastats_scheduler tail -n 100 /app/logs/scheduler.log[m
[32m+[m[32m```[m
 [m
[31m-## Logs do Dashboard[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Logs do Dashboard[m
 [m
 O Dashboard utiliza a configuração centralizada de logs.[m
 [m
[36m@@ -208,56 +277,72 @@[m [mOs eventos são gravados em:[m
 [m
 ```text[m
 logs/dashboard.log[m
[32m+[m[32m```[m
 [m
[31m-Erros também são enviados para:[m
[32m+[m[32mErros também são registrados em:[m
 [m
[32m+[m[32m```text[m
 logs/errors.log[m
[32m+[m[32m```[m
[32m+[m
[32m+[m[32m---[m
 [m
[31m-## Diagnóstico de logging[m
[32m+[m[32m# Diagnóstico de logging[m
 [m
[31m-A configuração centralizada de logs pode ser inspecionada pela função:[m
[32m+[m[32mA configuração centralizada pode ser inspecionada utilizando:[m
 [m
 ```python[m
 from app.core.logging_config import ([m
     get_logging_status,[m
 )[m
[32m+[m[32m```[m
[32m+[m
[32m+[m[32mEssa função permite verificar rapidamente a configuração atual do sistema de logging.[m
 [m
[31m-## Cliente HTTP para providers[m
[32m+[m[32m---[m
 [m
[31m-O UltraStats AI possui um cliente HTTP reutilizável para integração com APIs externas.[m
[32m+[m[32m# Cliente HTTP para providers[m
 [m
[31m-Recursos:[m
[32m+[m[32mO UltraStats AI possui um cliente HTTP reutilizável para integração com APIs esportivas externas.[m
[32m+[m
[32m+[m[32m## Recursos[m
 [m
 - timeout configurável;[m
[31m-- retries automáticos;[m
[32m+[m[32m- tentativas automáticas (retries);[m
 - backoff progressivo;[m
[31m-- controle de requisições por minuto;[m
[32m+[m[32m- controle de requisições por minuto (Rate Limiting);[m
 - tratamento padronizado de falhas;[m
 - suporte ao cabeçalho `Retry-After`;[m
[31m-- logs;[m
[31m-- testes com transporte HTTP simulado.[m
[32m+[m[32m- logging centralizado;[m
[32m+[m[32m- testes utilizando transporte HTTP simulado.[m
 [m
[31m-Componentes:[m
[32m+[m[32m## Componentes[m
 [m
 ```text[m
 app/providers/http_client.py[m
 app/providers/rate_limiter.py[m
 app/providers/exceptions.py[m
[32m+[m[32m```[m
 [m
[31m-Configurações:[m
[32m+[m[32m## Configurações[m
 [m
[32m+[m[32m```env[m
 PROVIDER_HTTP_TIMEOUT_SECONDS=15[m
 PROVIDER_HTTP_MAX_RETRIES=3[m
 PROVIDER_HTTP_RETRY_DELAY_SECONDS=1[m
 PROVIDER_DEFAULT_REQUESTS_PER_MINUTE=10[m
 PROVIDER_USER_AGENT=UltraStats-AI/1.0[m
[32m+[m[32m```[m
[32m+[m
[32m+[m[32m---[m
 [m
[32m+[m[32m# Framework de Providers[m
 [m
[31m-## Framework de providers[m
[32m+[m[32mO UltraStats AI utiliza um framework próprio para integração com múltiplos provedores de dados esportivos.[m
 [m
[31m-O UltraStats AI utiliza um contrato comum para integrar diferentes fontes de dados esportivos.[m
[32m+[m[32mTodos os providers implementam uma interface comum, permitindo adicionar novos provedores sem alterar a lógica de negócio da aplicação.[m
 [m
[31m-Componentes principais:[m
[32m+[m[32m## Componentes principais[m
 [m
 ```text[m
 app/providers/base.py[m
[36m@@ -270,29 +355,29 @@[m [mCada provider declara:[m
 - nome interno;[m
 - nome de exibição;[m
 - capacidades suportadas;[m
[31m-- necessidade de chave de API;[m
[32m+[m[32m- necessidade de API Key;[m
 - disponibilidade da integração;[m
[31m-- verificação de saúde.[m
[32m+[m[32m- verificação de saúde (Health Check).[m
 [m
[31m-O registro global permite selecionar um provider pelo nome:[m
[32m+[m[32mO registro global permite instanciar um provider pelo seu nome:[m
 [m
 ```python[m
[31m-from app.providers import ([m
[31m-    provider_registry,[m
[31m-)[m
[32m+[m[32mfrom app.providers import provider_registry[m
 [m
[31m-provider = provider_registry.create([m
[31m-    "mock"[m
[31m-)[m
[32m+[m[32mprovider = provider_registry.create("mock")[m
 ```[m
 [m
[31m-O provider padrão pode ser configurado no ambiente:[m
[32m+[m[32mO provider padrão pode ser definido por variável de ambiente:[m
 [m
 ```env[m
 PROVIDER_NAME=mock[m
 ```[m
 [m
[31m-Capacidades previstas:[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Capacidades previstas para os providers[m
[32m+[m
[32m+[m[32mOs providers poderão fornecer uma ou mais das seguintes capacidades:[m
 [m
 ```text[m
 competitions[m
[36m@@ -300,10 +385,88 @@[m [mteams[m
 matches[m
 standings[m
 players[m
[32m+[m[32mcoaches[m
[32m+[m[32mreferees[m
[32m+[m[32mstadiums[m
 lineups[m
 injuries[m
[32m+[m[32msuspensions[m
 match_events[m
 match_statistics[m
 odds[m
 expected_goals[m
[31m-```[m
\ No newline at end of file[m
[32m+[m[32m```[m
[32m+[m
[32m+[m[32mCada provider informará quais dessas capacidades suporta, permitindo que o sistema adapte automaticamente o fluxo de sincronização.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Visão de longo prazo[m
[32m+[m
[32m+[m[32mA arquitetura do UltraStats AI foi projetada para trabalhar com múltiplos provedores simultaneamente.[m
[32m+[m
[32m+[m[32mO fluxo geral de processamento seguirá a seguinte estrutura:[m
[32m+[m
[32m+[m[32m```text[m
[32m+[m[32mProviders[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mCollectors[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mNormalização[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mResolução de Identidade[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mData Fusion Engine[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mDomínio Canônico[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mBanco PostgreSQL[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mMotor Estatístico[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mModelos Preditivos[m
[32m+[m[32m      │[m
[32m+[m[32m      ▼[m
[32m+[m[32mDashboard / API[m
[32m+[m[32m```[m
[32m+[m
[32m+[m[32mOs dados provenientes dos provedores **nunca serão gravados diretamente nas tabelas principais**.[m
[32m+[m
[32m+[m[32mTodo dado deverá passar pelas etapas de:[m
[32m+[m
[32m+[m[32m- validação;[m
[32m+[m[32m- normalização;[m
[32m+[m[32m- resolução de identidade;[m
[32m+[m[32m- fusão de dados;[m
[32m+[m[32m- persistência no domínio canônico.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Estado atual do projeto[m
[32m+[m
[32m+[m[32mAtualmente o projeto encontra-se na construção da arquitetura do domínio do futebol.[m
[32m+[m
[32m+[m[32mAs próximas etapas incluem:[m
[32m+[m
[32m+[m[32m- modelagem das entidades canônicas;[m
[32m+[m[32m- implementação do domínio em SQLAlchemy;[m
[32m+[m[32m- integração com provedores reais;[m
[32m+[m[32m- resolução automática de identidade;[m
[32m+[m[32m- Data Fusion Engine;[m
[32m+[m[32m- modelos estatísticos;[m
[32m+[m[32m- motor de recomendações;[m
[32m+[m[32m- dashboard avançado.[m
[32m+[m
[32m+[m[32m---[m
[32m+[m
[32m+[m[32m# Licença[m
[32m+[m
[32m+[m[32mEste projeto encontra-se em desenvolvimento e, até o momento, não possui uma licença pública definida.[m
\ No newline at end of file[m
