# Backend

Backend Python do UltraStats AI.

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
