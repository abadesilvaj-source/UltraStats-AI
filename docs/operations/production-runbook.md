# Runbook de produção

> Uso suspenso em 2 de agosto de 2026. O aplicativo opera localmente; este
> runbook permanece apenas como preparação para uma futura decisão G32.

## Inicialização

1. Injetar credenciais pelo ambiente.
2. Aplicar migrations e confirmar exatamente um Alembic head.
3. Validar banco e provedores.
4. Iniciar backend, scheduler e frontend.
5. Confirmar health checks e ausência de alertas críticos.

## Incidente

1. Identificar serviço, janela e correlação do alerta.
2. Preservar logs e cadeia de auditoria.
3. Suspender recomendações se dados, odds ou feeds estiverem degradados.
4. Isolar o provedor ou circuito com falha.
5. Retomar somente após health checks e validação de consistência.

## Backup e recuperação

Todo backup deve possuir checksum, retenção e teste de restore em ambiente
isolado. Um artefato com checksum divergente nunca deve ser restaurado.

## Segurança

- exigir TLS na borda;
- manter origens permitidas no mínimo necessário;
- monitorar rate limiting e falhas de assinatura;
- revisar dependências antes de cada release.
