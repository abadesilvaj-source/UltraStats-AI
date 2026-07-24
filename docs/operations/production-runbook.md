# Runbook de Produção

O gate de homologação da G16 e o resultado da RC2 estão documentados em
[`g16-staging-acceptance.md`](g16-staging-acceptance.md). Uma release somente
pode ser promovida quando `StagingDecision.approved` for verdadeiro.

## Inicialização

1. Injetar credenciais pelo ambiente; nunca salvar valores no repositório.
2. Aplicar migrations e confirmar exatamente um Alembic head.
3. Validar banco, providers, filas e cache.
4. Iniciar API, workers, scheduler e dashboard.
5. Confirmar métricas, heartbeat e ausência de alertas críticos.

## Incidente

1. Identificar serviço, janela e correlação do alerta.
2. Preservar logs e cadeia de auditoria.
3. Suspender recomendações se dados, odds ou feeds estiverem degradados.
4. Isolar provider ou circuito com falha.
5. Registrar ator, ação e instante de cada intervenção.
6. Retomar somente após health checks e validação de consistência.

## Backup e recuperação

1. Gerar o artefato canônico.
2. Conferir e registrar checksum, tamanho e localização.
3. Copiar para storage com retenção e controle de acesso.
4. Testar restore em ambiente isolado.
5. Comparar checksum antes de abrir o conteúdo.
6. Registrar a verificação no catálogo.

Um artefato com checksum divergente nunca deverá ser restaurado.

## Filas

- mensagens precisam de identidade idempotente;
- falhas transitórias usam nack e retry;
- mensagens acima do limite vão para dead-letter;
- reprocessamento de dead-letter exige investigação e auditoria.

## Segurança

- rotacionar o segredo de tokens por procedimento controlado;
- exigir TLS na borda;
- manter allowlist de origem mínima;
- monitorar rate limiting e falhas de assinatura;
- revisar papéis periodicamente;
- executar revisão de dependências antes de cada release.

## Escala

O número de réplicas deve respeitar capacidade medida, mínimo operacional e
máximo financeiro. Mudanças de capacidade precisam ser validadas pelo teste de
carga e observadas em latência, erros e saturação.

## Retenção

Aplicar retenção por categoria. Auditorias, backups, métricas, notificações e
payloads podem ter períodos distintos. Exclusões precisam ser registradas e não
podem romper obrigações de auditoria ou recuperação.
