# Resolução de Identidade e Data Fusion

## Fluxo

```text
RawProviderPayload
  -> validação
  -> normalização Unicode
  -> geração e scoring de candidatos
  -> associação automática ou revisão manual
  -> observações por provider
  -> fusão por campo
  -> valores canônicos com proveniência
```

Registros inválidos são enviados à quarentena usando o fingerprint SHA-256 do
payload bruto. Após correção, o mesmo registro pode ser reprocessado e marcado
como resolvido sem perder seu histórico.

## Decisões

Scores acima do threshold automático produzem `MATCHED`. Scores intermediários
produzem `REVIEW`; a decisão exige responsável e justificativa. Scores baixos
permanecem `UNMATCHED`. Rejeições manuais são registradas como `REJECTED`.

## Fusão

A fusão ocorre por campo. A `ProviderPriorityPolicy` seleciona a origem
preferencial, enquanto valores divergentes geram `FusionConflict`. Cada campo
resultante mantém o provider de origem em `provenance`.

## Persistência

A migration `9c7b7e30f003` cria:

- `identity_decisions`;
- `fusion_results`;
- `data_quarantine`.

As constraints garantem uma decisão corrente por identidade externa e um item
de quarentena por fingerprint. Índices atendem a fila de revisão, pendências de
quarentena e histórico de fusões.

## Validação

A conclusão da G7 foi validada com 2.458 testes e 100% de cobertura de linhas e
branches, incluindo idempotência, revisão, conflitos, quarentena,
reprocessamento e upgrade/downgrade da migration.
