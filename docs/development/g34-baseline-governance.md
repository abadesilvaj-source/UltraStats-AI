# G34 — Baseline e governança

## Responsabilidades

| Papel | Responsabilidade |
|---|---|
| Proprietário do produto | visão, autorização de risco, usuários e publicação |
| Responsável técnico | arquitetura, implementação, testes e dívida técnica |
| Operador local | containers, cotas, backup, incidentes e baseline |
| Revisor científico | datasets, leakage, calibração, promoção e rollback |

Uma pessoa pode acumular papéis no ambiente pessoal, mas cada decisão registra
qual papel foi exercido.

## Cadência semanal

1. Segunda: gerar baseline G34 e revisar saúde/cota/disco.
2. Quarta: revisar qualidade de dados, drift e incidentes.
3. Sexta: revisar paper v2, dívida e decisões; nenhuma regra muda dentro da
   coorte ativa.
4. Mensal: reavaliar prioridades e registrar ADR quando a direção mudar.

## Comando do baseline

Dentro do backend ou container:

```powershell
python -m scripts.g34_baseline --output reports/generated/g34-baseline.json
python -m scripts.g34_baseline --verify reports/generated/g34-baseline.json
```

O JSON contém commit base, checksum exato da árvore executada, versões,
migration aplicada, configurações públicas em allowlist,
contagens, estado das carteiras, recomendações, saúde e checksum. Chaves, tokens,
URLs de banco e segredo de autenticação não são lidos pelo exportador.

## Escopo decisório congelado

Carteira: `automatic-shadow-v2`.

Mercados executáveis:

- `under_2_5_goals`;
- `under_3_5_goals`;
- `both_teams_to_score`.

Os demais mercados permanecem `shadow_observation`. Qualquer mudança cria nova
versão de política e nova coorte; não edita a v2 retroativamente.

## Registro de decisão

Cada reunião/revisão registra data, papel, evidência, decisão, alternativas,
risco, rollback e fase afetada. ADRs ficam em
[`../architecture/architecture-decisions.md`](../architecture/architecture-decisions.md).

## Gate da G34

- manifesto pode ser reproduzido pelo comando documentado;
- checksum independe apenas do horário de captura;
- exportador possui teste contra vazamento de segredo;
- fotografia local é versionada sem credenciais;
- escopo e dívida possuem responsáveis/fase;
- catálogo define fontes únicas para métricas decisórias;
- roadmap e índices apontam para uma fonte vigente.
