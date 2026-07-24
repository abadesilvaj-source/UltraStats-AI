# Providers

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
