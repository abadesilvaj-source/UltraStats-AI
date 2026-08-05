# Baselines operacionais

## G34 — 2 de agosto de 2026

Artefato: [`g34-baseline-2026-08-02.json`](g34-baseline-2026-08-02.json).

- schema: `g34-baseline-v1`;
- commit de referência: `0bd07194d9fe267578a774a86cfde5bc94b116a8`;
- migration aplicada: `b53d8a44e015`;
- checksum do baseline: `522b0665eff703ca4f43933770ee83e58a09549f10fb59cd6749fce242b7bea9`;
- checksum da árvore backend executada: `d811c17497e34ee56a168b731bfebad81834957294535fab03037fb6695da681`;
- banco: PostgreSQL;
- estado da API no instante: saudável;
- carteira v2: ativa, R$ 10.000 e coorte prospectiva sem decisões herdadas;
- escopo executável: under 2.5, under 3.5 e ambas marcam.

A carteira v1 permanece no artefato como evidência histórica. Ela não participa
do saldo, métricas ou decisões da v2.

O JSON não contém chaves, tokens, senha, URL do banco ou segredo de autenticação.
Seu checksum cobre todo o estado, exceto horário de captura e o próprio checksum.

Regeneração e verificação:

```powershell
python -m scripts.g34_baseline --output reports/generated/g34-baseline.json
python -m scripts.g34_baseline --verify reports/generated/g34-baseline.json
```
