# G35 — resiliência, jobs e recuperação

Status: concluída em 03/08/2026.

## Arquitetura operacional

Coleta completa, placares ao vivo, backfill/promoção, odds, paper/liquidação e
treino possuem execuções independentes. Cada ciclo usa tarefa persistente com
chave idempotente, lease, timeout brando, três tentativas, backoff exponencial e
dead-letter. O APScheduler limita uma instância por job e roda separado da API.

A liquidação apenas enfileira `model_training`. O worker de treino gera o novo
artefato fora da inferência; em falha, o champion anterior continua disponível.
Transações volumosas permanecem limitadas pelos lotes configuráveis.

Kill switches: coleta (`JOB_SYNC_ENABLED`, `JOB_LIVE_ENABLED`,
`JOB_BACKFILL_ENABLED`, `JOB_ODDS_ENABLED`), treino (`JOB_TRAINING_ENABLED`),
recomendação (`RECOMMENDATION_GENERATION_ENABLED`) e paper
(`JOB_PAPER_ENABLED`).

## SLO e recuperação

O status da plataforma expõe fila, execução, falhas, dead-letter, maior duração
e violações por job. Lease vencido é retomado no próximo ciclo. Os testes de
interrupção cobrem `sync`, `live`, `backfill`, `odds`, `paper` e `training`.
Timeout é brando e registra a violação; o scheduler separado impede bloqueio da
API e do feed ao vivo.

## Backup validado

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\ops\windows\g35-storage-health.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\ops\windows\g35-backup-restore.ps1
```

Em 03/08/2026: banco com 4.950.013.619 bytes (12,46% de 36,99 GB), saudável.
Alertas: 75%, 85% e 90%. Dump integral com 627.732.487 bytes e SHA-256
`2bf524dd7b21c39283c8d21330fb90cb908b1499b1cb4952cf922566fb733d21`.
Restore temporário confirmou 15.238 partidas, 357.922 previsões, 8.892.328
snapshots de odds, 4.688 apostas fictícias e 1 usuário. RTO observado: 6m07s.
RPO local: último backup; executar diariamente e antes de migrations. Retenção:
14 dias.

Somente o banco temporário prefixado `ultrastats_g35_restore_` e backups antigos
com padrão controlado são removidos. O volume PostgreSQL original nunca é
removido.
