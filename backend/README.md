# Backend

Backend Python do UltraStats AI.

## Inteligência operacional atual

- baseline Poisson e Elo;
- regressão logística temporal para 1X2, over/under 2,5 e BTTS;
- split cronológico 70/15/15 e calibração em holdout;
- aprovação somente quando o teste supera o baseline;
- ensemble champion/challenger persistido para resultados e gols;
- fallback determinístico quando a amostra ou o modelo não são aprovados;
- coleta multifonte de odds e marcação de closing odds.

O treino considera no máximo as 5.000 observações temporais mais recentes para
manter custo operacional limitado. O próximo desacoplamento dos jobs está
planejado na G27.

- `api/`: API HTTP FastAPI;
- `app/`: aplicação operacional, modelos, serviços, provedores e scheduler;
- `src/ultrastats_ai/`: domínio canônico e infraestrutura;
- `migrations/`: migrations Alembic;
- `scripts/`: comandos operacionais;
- `tests/`: testes unitários e de integração;
- `data/`: dados locais controlados usados por provedores de desenvolvimento.

Comandos principais devem ser executados a partir desta pasta:

```powershell
python -m alembic upgrade head
python -m pytest
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
python -m scripts.run_scheduler
```
