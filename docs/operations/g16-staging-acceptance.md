# G16 — Homologação em staging

## Resultado

**Homologação concluída e aprovada para promoção estável.**

O ambiente isolado `ultrastats-g16` foi levantado em Docker com PostgreSQL 17,
migrations, scheduler e dashboard. A evidência estruturada está em
`release/staging-acceptance-v0.1.0-rc.2.json`.

## Evidências aprovadas

| Verificação | Resultado |
|---|---|
| PostgreSQL | saudável |
| Alembic | `b8151a2c9e10 (head)` |
| Scheduler | saudável, heartbeat de 10 segundos |
| Dashboard | HTTP 200 e health check saudável |
| Filesystem do dashboard | read-only |
| Diretório temporário | `/tmp` em tmpfs |
| Carga | 100 requisições, 0 falhas |
| Latência média/máxima | 45,65 ms / 733,53 ms |
| Backup e restore PostgreSQL | aprovado |
| Downgrade e re-upgrade | aprovado no banco restaurado |
| Dependências públicas | conectividade e contrato aprovados |

## Coleta real

- OpenLigaDB: 306 partidas da Bundesliga 2025;
- Football-Data.co.uk: 380 registros da Premier League 2025/26;
- StatsBomb Open Data: 3.940 eventos da partida de validação.
- API-Football: plano Free ativo, 263 fixtures, 10 respostas de odds e
  estatísticas de partida, sem erros de contrato.

## Decisão sobre Football-Data.org

Por decisão do operador em 24/07/2026, Football-Data.org passa a ser uma fonte
complementar opcional até o recebimento do token. A API-Football, homologada
com dados reais de fixtures, odds e estatísticas, satisfaz a capacidade
obrigatória de dados ao vivo e apostas. OpenLigaDB, Football-Data.co.uk e
StatsBomb permanecem como fontes públicas de fallback e treinamento.

Nenhum token deve ser incluído em commits, evidências ou logs.
