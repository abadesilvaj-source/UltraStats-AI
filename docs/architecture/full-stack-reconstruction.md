# Arquitetura full-stack

```text
React/Vite :8516
      |
      | /api/v1
      v
FastAPI :8000
      |
      +-- PostgreSQL
      +-- scheduler
              |
              +-- coleta multiprovedor
              +-- fusão e proveniência
              +-- estatísticas e features
              +-- previsões e calibração
              +-- recomendações e liquidação
```

O frontend não acessa o banco nem importa serviços Python. O dashboard
Streamlit legado foi removido; React é a única interface mantida.

## Decisões

1. `backend/src/ultrastats_ai` contém o domínio canônico.
2. `backend/app` contém persistência e casos de uso operacionais.
3. `backend/api` publica os casos de uso.
4. Datas são armazenadas em UTC e exibidas no timezone do usuário.
5. Resultados oficiais, não recomendações, alimentam auditoria e calibração.
6. Cada campo é conciliado de forma neutra entre fontes disponíveis.
7. Correlações e risco geram aviso confirmável; regras técnicas continuam
   protegendo saldo, integridade e estados inválidos.
