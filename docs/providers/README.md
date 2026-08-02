# Providers

## Estado operacional em agosto de 2026

Por decisão do proprietário em 2 de agosto, somente `api_football` permanece
ativo para novas coletas (`ACTIVE_PROVIDERS=api_football`). The Odds API,
Football-Data, SportMonks e fontes públicas ficam desativadas operacionalmente.
Seus dados históricos não são removidos.

O ciclo de odds sempre consulta o dia atual e gira pelos dias futuros da janela
de 14 dias. Com um dia futuro por ciclo de 15 minutos, toda a janela é visitada
em aproximadamente 3h30. Varreduras instantâneas são evitadas porque o endpoint
de odds aplica rate limit próprio e pode responder HTTP 429.

O construtor multifonte aceita `API_FOOTBALL_KEY`. Quando ela não existe,
`SPORTS_API_KEY` é fallback legado; uma `API_FOOTBALL_KEY` explicitamente vazia
continua desativando o conector. O job dedicado atualiza odds e marca snapshots
elegíveis como closing odds. Falta de odd real nunca é preenchida artificialmente.

Resultados e gols podem usar ensembles Poisson/Elo/ML quando o modelo temporal
estiver aprovado; caso contrário, o pipeline mantém o baseline.

## API-Football Ultra

A integração Ultra inclui fixtures, livescore, eventos, estatísticas,
escalações, lesões, estatísticas de jogadores e equipes, previsões do provedor,
odds pré-jogo e odds ao vivo. A política de frequência, franquia e backfill
está documentada em
[`docs/operations/api-football-ultra.md`](../operations/api-football-ultra.md).

## Operação agendada

O scheduler usa `SYNC_PROVIDER=multi_provider` para consultar API-Football,
Football-Data.org, OpenLigaDB e Football-Data.co.uk. Cada execução registra
health checks e payloads brutos idempotentes. Falhas parciais ativam modo
degradado; a execução só falha quando nenhuma fonte responde.

O intervalo local recomendado é de 60 minutos para respeitar a franquia gratuita
da API-Football. StatsBomb Open Data permanece disponível para coletas de
eventos/xG orientadas por partida, pois seu contrato exige um `match_id`.

### Pipeline operacional

A coleta de fixtures é promovida para as tabelas consumidas pela API e pelo
frontend. O processo resolve competição e equipes pelos identificadores
externos, atualiza o ciclo de vida das partidas, garante os mercados principais,
vincula odds disponíveis e produz previsões Poisson idempotentes.

Previsões sem histórico estatístico suficiente são identificadas como
`evidence_level=low`; elas permitem operar e observar o sistema, mas não devem
ser interpretadas como recomendações de alta confiança. O EV só é calculado
quando existe odd real correspondente.

Esta seção reúne documentos relacionados às integrações com provedores externos de dados de futebol.

Documentos previstos:

- framework de providers;
- configuração de credenciais;
- capacidades dos providers;
- coleta e normalização;
- tratamento de falhas;
- limites de requisição;
- provedores reais integrados.

## Football-Data.org

A fundação canônica da G6 utiliza a API v4 e autenticação pelo header
`X-Auth-Token`. Configure `FOOTBALL_DATA_API_TOKEN` apenas no ambiente local;
o token nunca deve ser versionado.

O adapter suporta competições, equipes, partidas e classificação. O cliente
aplica timeout, rate limiting e retries para HTTP 429 e falhas 5xx. O plano
gratuito deve ser configurado para dez requisições por minuto.

Collectors preservam o payload bruto antes de qualquer normalização. A store
SQLAlchemy usa uma representação JSON canônica e fingerprint SHA-256 para
garantir deduplicação. A store em memória permanece disponível para testes.

O health check e `ProviderDashboard.snapshot` oferecem o contrato de dados para
o painel operacional. A página `10_Providers.py` permite executar a verificação
e consultar o último estado persistido.

O adapter somente aceita `FOOTBALL_DATA_API_TOKEN`; a variável genérica legada
`SPORTS_API_KEY` não é reutilizada, evitando o envio de credenciais de outro
provider. A validação live depende de uma chave real configurada localmente.

## Motor multi-provider

A G15.1 adiciona adapters para API-Football, Football-Data.co.uk, StatsBomb
Open Data e OpenLigaDB. A matriz de capacidades, prioridade, continuidade
degradada e validação preditiva estão em
[`multi-provider-model-validation.md`](../architecture/multi-provider-model-validation.md).

Fontes sem API pública ou licença explícita não são coletadas por scraping.
## Integrações gratuitas complementares

Os conectores são ativados somente quando suas chaves estão presentes no
ambiente local. Não se considera uma fonte disponível apenas porque o
endpoint público de saúde responde: a aceitação também exige coleta bruta,
normalização, identidade e fusão.

- **GOAL API:** agenda, placares, eventos, escalações, estatísticas e odds;
  requer `GOAL_API_KEY`.
- **Zafronix Sports APIs:** histórico de seleções e competições, estádios,
  árbitros e clima; requer `ZAFRONIX_API_KEY`.

GOAL API e Zafronix seguem o mesmo peso-base dos demais provedores. A decisão
por campo continua sendo feita por consenso, atualidade e completude; a ordem
da lista de provedores não concede autoridade especial sobre um campo.
