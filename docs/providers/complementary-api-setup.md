# Configuração das APIs complementares

## TheSportsDB

O conector v1 é ativado automaticamente com a chave pública `123`:

```env
THESPORTSDB_API_KEY=123
THESPORTSDB_BASE_URL=https://www.thesportsdb.com/api/v1/json/123
```

Ele participa da identidade e da fusão de agenda, placar, estado e estádio.

## Sportmonks

Crie uma conta no plano gratuito, copie o token em MySportmonks e configure:

```env
SPORTMONKS_API_TOKEN=seu_token
SPORTMONKS_BASE_URL=https://api.sportmonks.com/v3/football
```

Sem o token, o conector não é criado. O plano gratuito atual cobre a Superliga
Dinamarquesa e a Premiership Escocesa. Dados indisponíveis na assinatura são
ignorados sem impedir a sincronização das outras fontes.

## The Odds API

Crie uma conta, copie a API key e configure:

```env
THE_ODDS_API_KEY=sua_chave
THE_ODDS_API_BASE_URL=https://api.the-odds-api.com/v4
THE_ODDS_API_SPORT_KEYS=soccer_brazil_campeonato,soccer_epl,soccer_uefa_champs_league
THE_ODDS_API_REGIONS=eu
THE_ODDS_API_MARKETS=h2h,totals
```

Cada combinação região/mercado consome créditos. O padrão consulta uma região
e dois mercados. Ajuste a lista de competições à cobertura desejada.

## Ativação

Depois de alterar o arquivo de ambiente:

```powershell
docker compose -p ultrastats-g16 -f docker-compose.staging.yml `
  --env-file .env.staging.g16.local up -d --build --wait backend scheduler
```

Confirme a ativação em:

- `GET http://localhost:8000/api/v1/health`;
- `GET http://localhost:8000/api/v1/providers/contributions`.

Credenciais nunca devem ser incluídas no Git. Os conectores são independentes:
uma chave ausente, cota esgotada ou indisponibilidade degrada somente a fonte
correspondente.
