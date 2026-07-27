# UltraStats AI Backend API v1

Base local: `http://localhost:8000/api/v1`

Documentação OpenAPI:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Consultas

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/health` | Saúde, contagens e última sincronização |
| GET | `/matches` | Partidas futuras/em andamento |
| GET | `/matches/{id}` | Partida, estatísticas, mercados e análises |
| GET | `/markets` | Catálogo operacional |
| GET | `/predictions` | Previsões apenas de partidas ativas |
| GET | `/recommendations` | Previsões ativas com EV positivo |
| GET | `/bankrolls` | Bancas e saldos |
| GET | `/bet-slips` | Bilhetes simples e múltiplos |
| GET | `/favorites` | Favoritos do usuário |
| GET | `/live` | Snapshots do motor ao vivo |

O parâmetro `timezone` pode ser enviado nas consultas de partidas. Exemplo:

```http
GET /api/v1/matches?timezone=America/Sao_Paulo
```

`/matches` aceita também `status`, `limit` (entre 1 e 500) e `offset` para filtragem e paginação.

## Registrar bilhete

```http
POST /api/v1/bet-slips
Content-Type: application/json
```

```json
{
  "bankroll_id": 1,
  "bookmaker": "API-Football",
  "stake_amount": 25,
  "legs": [
    {
      "match_id": 100,
      "market_id": 1,
      "selection": "Home"
    },
    {
      "match_id": 101,
      "market_id": 3,
      "selection": "Under 2.5"
    }
  ]
}
```

Uma perna cria uma aposta simples; duas ou mais criam uma múltipla.

## Erros

Erros de validação retornam HTTP 422:

```json
{"error": "Odd atual não encontrada."}
```
