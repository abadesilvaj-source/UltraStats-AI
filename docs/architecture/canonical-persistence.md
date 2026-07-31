# Persistência do Domínio Canônico

## Decisão arquitetural

A G5 persiste Aggregate Roots como snapshots JSON versionados em um envelope
relacional. O domínio não importa SQLAlchemy: serializers e deserializers são
injetados no repository, preservando a separação entre domínio e infraestrutura.

O modelo legado em `app` continua operacional e não foi alterado. A nova base
`CanonicalBase`, em `backend/src/ultrastats_ai`, é registrada junto da metadata legada
no Alembic.

## Estrutura

- `canonical_aggregates`: contexto, identidade canônica, snapshot, versão,
  auditoria temporal e soft delete;
- `canonical_outbox`: eventos gravados na mesma transação do agregado;
- `canonical_inbox`: deduplicação por consumidor e identificador da mensagem;
- `canonical_audit_log`: trilha de ações ligada ao snapshot;
- `SqlAlchemyAggregateRepository`: carregamento, inclusão, atualização e
  remoção lógica;
- `SqlAlchemyUnitOfWork`: commit, rollback, lifecycle da sessão e Outbox.

O campo `version` é o token de optimistic locking do SQLAlchemy. Atualizações
concorrentes sobre a mesma versão falham, evitando lost updates.

## Migration

A revision `7a5f5c10d001` sucede `34f16155b3c2`, cria índices, checks,
unicidade e chaves estrangeiras, e possui downgrade completo. O teste de
migration executa upgrade e downgrade em um banco SQLite descartável.

## Validação

A consolidação da G5 foi aprovada com 2.439 testes e 100% de cobertura de
linhas e branches. Os testes incluem services, policies, repositories, Unit of
Work, soft delete, optimistic locking, Outbox, Inbox e reversibilidade da
migration.
