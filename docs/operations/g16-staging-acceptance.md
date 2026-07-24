# G16 — Homologação em staging

## Resultado

**Homologação automatizada concluída. Promoção estável bloqueada.**

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

## Bloqueios

1. `FOOTBALL_DATA_API_TOKEN` não está configurado;
2. `API_FOOTBALL_KEY` não está configurada;
3. o aceite humano do operador ainda não foi fornecido.

Esses itens são bloqueantes porque Football-Data.org e API-Football foram
classificadas como fontes requeridas para a operação pretendida. A aplicação
continua funcional em modo degradado com as fontes públicas, mas a ausência de
odds/live da API-Football impede a promoção honesta para produção.

## Retomada

1. preencher localmente `FOOTBALL_DATA_API_TOKEN` e `API_FOOTBALL_KEY`;
2. reiniciar o projeto `ultrastats-g16`;
3. repetir health e coleta dos dois providers;
4. revisar visualmente dashboard, dados, odds e recomendações;
5. registrar o aceite do operador;
6. executar novamente o gate;
7. somente então promover para `v0.1.0`.

Nenhum token deve ser incluído em commits, evidências ou logs.
