# Registro de dívida técnica

Atualizado em: 2 de agosto de 2026.

Escala: impacto P0 bloqueia confiança/operação; P1 limita produto; P2 melhora
manutenção. Estado inicial da G34:

| ID | Prioridade | Dívida | Consequência | Destino |
|---|---:|---|---|---|
| TD-001 | P0 | resolvido: jobs isolados com lease, retry, SLO e dead-letter | encerrado em 03/08/2026 | G35 |
| TD-002 | P0 | resolvido: backup/checksum/restore integral ensaiado | encerrado em 03/08/2026 | G35 |
| TD-003 | P0 | qualidade desigual de odds/estatísticas | recomendação sem evidência suficiente | G36 |
| TD-004 | P0 | validação global pode ocultar segmentos | sobreconfiança e promoção indevida | G37 |
| TD-005 | P0 | coorte v2 ainda sem amostra prospectiva | desempenho decisório desconhecido | G39 |
| TD-006 | P1 | duas camadas Python (`app` e `ultrastats_ai`) coexistem | duplicação de conceitos e manutenção | G35–G37 |
| TD-007 | P1 | métricas homônimas em contextos diferentes | interpretação incorreta | G34 |
| TD-008 | P1 | frontend principal concentra componentes | regressões e evolução lenta | G40 |
| TD-009 | P1 | mobile ainda replica parte da composição | divergência visual/funcional | G40 |
| TD-010 | P1 | paginação limitada em históricos grandes | latência e memória | G40 |
| TD-011 | P1 | isolamento multiusuário precisa auditoria por objeto | risco de privacidade | G41 |
| TD-012 | P2 | documentação histórica extensa e parcialmente redundante | descoberta difícil | contínuo |

## Política de tratamento

1. Toda dívida possui fase, evidência e critério de encerramento.
2. P0 precede nova funcionalidade.
3. Encerramento exige teste ou medição, não apenas refatoração.
4. Novas dívidas entram neste arquivo; não ficam somente em comentários.
5. Itens de segurança nunca são rebaixados para cumprir prazo.

TD-007 é considerada controlada pelo
[`../architecture/metrics-catalog.md`](../architecture/metrics-catalog.md); a
remoção física de cálculos legados ocorrerá quando cada consumidor migrar para
a fonte oficial, com teste de contrato.
