# Roadmap mestre 2026–2027 — UltraStats AI

Atualizado em: 2 de agosto de 2026.

Este é o único plano vigente do produto. O histórico G1–G33 permanece em
[`roadmap.md`](roadmap.md). A visão final está em
[`../product/product-vision.md`](../product/product-vision.md) e a avaliação que
originou este plano em
[`../operations/system-assessment-2026-08-02.md`](../operations/system-assessment-2026-08-02.md).

O aplicativo permanece exclusivamente local. Hospedagem, acesso externo e
automação com dinheiro real não estão autorizados.

## Norte do produto

Construir um assistente de decisão de futebol seletivo e responsável. O sistema
deve provar probabilidades calibradas e risco controlado antes de ampliar
mercados ou usuários. “Sem aposta” é um resultado correto.

## Estado inicial

- fundação G1–G26 e impacto de jogadores G33 implementados;
- API-Football como única fonte ativa de novas coletas;
- web, mobile, API, scheduler e PostgreSQL operacionais localmente;
- política de paper trading v2 ativa, com histórico v1 preservado;
- validação temporal, champion/challenger e fallback presentes;
- evidência prospectiva da nova política ainda insuficiente;
- G27–G30 parcialmente implementadas e consolidadas nas fases abaixo.

## Sequência executiva

| Fase | Prioridade | Horizonte relativo | Saída obrigatória |
|---|---:|---:|---|
| G34 — baseline e congelamento | P0 | semana 1 | fotografia reproduzível e escopo decisório reduzido |
| G35 — operação e armazenamento | P0 | semanas 1–3 | jobs isolados, recuperação e backup demonstrados |
| G36 — contratos de dados | P0 | semanas 2–5 | SLA e qualidade por competição/capacidade |
| G37 — laboratório científico | P0 | semanas 4–8 | datasets/modelos reproduzíveis e calibrados |
| G38 — decisão e risco | P0 | semanas 6–10 | política prospectiva segura e auditável |
| G39 — observação prospectiva | P0 | mínimo 30–90 dias | evidência suficiente para promoção |
| G40 — produto web/mobile | P1 | semanas 8–14 | jornada simples, acessível e testada |
| G41 — piloto multiusuário local | P1 | após G39/G40 | teste controlado sem falhas críticas |
| G42 — prontidão operacional externa | P2 | sob autorização | ambiente privado reversível |
| G43 — v1.0 e evolução | P2 | após todos os gates | release sustentada por evidência |

Horizontes representam ordem e esforço, não datas prometidas. G39 depende do
calendário esportivo e não pode ser acelerada por backfill.

## G34 — Baseline, inventário e congelamento de escopo

Objetivo: criar uma referência única antes de novas otimizações.

- [x] registrar visão final e avaliação integral do sistema;
- [x] iniciar paper trading v2 sem apagar a v1;
- [x] gerar manifesto automático de versões, migrations e configurações não secretas;
- [x] congelar mercados executáveis iniciais e manter os demais em shadow;
- [x] capturar baseline de banco, cobertura, latência, modelos e recomendações;
- [x] reconciliar documentos que ainda tratam G27–G30 como não iniciadas;
- [x] classificar dívida técnica por impacto e remover métricas duplicadas;
- [x] definir responsáveis, cadence semanal e registro de decisões.

Status: **concluída**. Evidências em
[`../baselines/g34-baseline-2026-08-02.json`](../baselines/g34-baseline-2026-08-02.json),
[`g34-baseline-governance.md`](g34-baseline-governance.md),
[`technical-debt-register.md`](technical-debt-register.md) e
[`../architecture/metrics-catalog.md`](../architecture/metrics-catalog.md).

Gate aprovado: baseline reproduzível, sem segredo, com números e consultas
versionadas.

## G35 — Operação resiliente e armazenamento seguro

Objetivo: garantir que coleta, treino e inferência não derrubem o produto nem o
banco.

- [x] separar coleta, promoção, odds, treino, inferência, paper e liquidação em jobs;
- [x] idempotência, lease, timeout, retry/backoff e dead-letter por job;
- [x] treinar fora do processo de inferência e manter o champion disponível;
- [x] limitar transações e commits por lote;
- [x] criar SLO de duração, atraso, fila, erro e recuperação;
- [x] alertar disco em 75%, 85% e 90%;
- [x] automatizar backup lógico com checksum e retenção;
- [x] testar restore em PostgreSQL temporário e comparar contagens críticas;
- [x] executar ensaio de interrupção no meio de cada job;
- [x] criar kill switch de coleta, treino e recomendação independentes.

Gate:

- nenhum job bloqueia API/live por mais de cinco minutos;
- reinício não duplica artefatos;
- restore validado e RPO/RTO documentados;
- volume PostgreSQL nunca é removido por manutenção.

Runbook: [`../operations/docker-storage-maintenance.md`](../operations/docker-storage-maintenance.md).

Conclusão: 03/08/2026. Evidências em
[`../operations/g35-resilience-runbook.md`](../operations/g35-resilience-runbook.md).

## G36 — Contratos de dados, odds e identidade

Objetivo: transformar disponibilidade externa em qualidade mensurável.

- [x] catálogo-alvo de competições com fixtures, resultados, odds, escalações,
  jogadores, eventos e estatísticas;
- [x] denominadores brutos e elegíveis versionados;
- [x] contrato de frescor por capacidade e estado `available/unavailable/stale`;
- [x] reconciliar IDs de competição, temporada, equipe, partida e mercado;
- [x] impedir união de competições homônimas de países diferentes;
- [x] coletar abertura, snapshots e closing line quando disponíveis;
- [x] validar bookmaker, linha, seleção e timestamp antes de associar odds;
- [x] priorizar lacunas pelo impacto nos mercados ativos;
- [x] quarentena e reprocessamento de payloads inconsistentes;
- [x] painel de causa raiz e custo de cota por dado útil.

Gate:

- estatísticas elegíveis ≥ 90% no núcleo;
- odds frescas ≥ 80% das partidas realmente cobertas pelo provedor;
- ≥ 80% das partidas com odds possuem dois snapshots quando a fonte permite;
- erro de identidade amostrado < 0,5%;
- toda ausência relevante possui motivo verificável.

Implementação concluída em 03/08/2026. Contratos e procedimento de aceite:
[`../operations/g36-data-contracts-runbook.md`](../operations/g36-data-contracts-runbook.md).

## G37 — Laboratório estatístico, ML e MLOps

Objetivo: aprovar modelos somente por desempenho temporal futuro.

- [x] registry de dataset com consulta, cutoff, checksum, features e alvos;
- [x] testes automáticos de leakage e contratos de features;
- [x] baselines Poisson/Elo por mercado e regime;
- [x] modelos especializados apenas onde existe amostra;
- [x] walk-forward aninhado por temporada/competição/mercado/horizonte;
- [x] calibração sem usar o conjunto de teste;
- [x] intervalos de confiança e análise de sensibilidade;
- [x] benchmark contra probabilidade implícita sem margem;
- [x] champion/challenger com canário, rollback e validade temporal;
- [x] drift de dados, conceito, calibração e cobertura;
- [x] model card, limitações e segmentos proibidos por versão;
- [x] ablação de escalações, jogadores, odds e contexto.

Gate:

- challenger melhora baseline fora da amostra com incerteza aceitável;
- nenhum segmento ruim é ocultado por média global;
- treino é reproduzível e rollback leva minutos, não horas;
- previsão registra modelo, dataset, cutoff e qualidade das features.

Implementação concluída em 04/08/2026. O canário permanece limitado a 5% e
não substitui automaticamente o campeão. Evidências e rollback:
[`../operations/g37-mlops-runbook.md`](../operations/g37-mlops-runbook.md).

## G38 — Recomendação seletiva, paper trading e risco

Objetivo: converter probabilidades em decisões sem repetir a política v1.

- [x] separar `paper_executed` de `shadow_observation`;
- [x] odds 1,60–2,99, limite inferior ≥ 80% e horizonte ≤ 6h;
- [x] reservar pendências e limitar 3% ao dia/1% por partida;
- [x] bloquear placar exato, linhas extremas e escanteios na execução inicial;
- [x] isolar carteiras, liquidação e métricas por política;
- [x] limite agregado por competição, mercado e correlação;
- [x] circuit breaker por drawdown, drift e perda de cobertura;
- [x] odd mínima válida e expiração visível na recomendação;
- [x] recalibrar rótulos de risco por perda observada, não por nome do mercado;
- [x] painel com hit rate, Brier, CLV, ROI, yield e drawdown por coorte;
- [x] impedir promoção quando ROI, CLV ou calibração degradarem;
- [x] testar estresse, sequência de perdas, void e correções de resultado.

Gate: todas as invariantes de exposição passam em concorrência e nenhuma
recomendação sem preço recente recebe stake.

Implementação concluída em 04/08/2026. Política, limites, circuit breakers,
reconciliação e procedimento de aceite:
[`../operations/g38-selective-risk-runbook.md`](../operations/g38-selective-risk-runbook.md).

## G39 — Validação prospectiva contínua

Objetivo: obter evidência que não foi usada para escolher a política.

- [ ] iniciar coorte v2 com data de corte imutável;
- [ ] revisão semanal automática, sem ajustar regra no meio da coorte;
- [ ] relatório de calibração por decil e segmento;
- [ ] comparar executadas, shadow, baseline e mercado;
- [ ] medir CLV de abertura/execução/fechamento;
- [ ] registrar mudanças como nova versão, nunca sobrescrever a coorte;
- [ ] promover mercado em três etapas: shadow, stake mínimo, política ativa;
- [ ] rebaixar automaticamente em drift ou deterioração;
- [ ] executar análise independente antes de ampliar capital fictício.

Gate mínimo:

- 30–90 dias prospectivos;
- 1.000 decisões liquidadas totais;
- 100 por segmento promovido;
- Brier/ECE dentro do limite definido;
- CLV médio não negativo com intervalo reportado;
- drawdown abaixo do limite aprovado;
- nenhuma falha de integridade aberta.

## G40 — Produto web e mobile centrado na decisão

Objetivo: tornar o sistema compreensível sem expor complexidade operacional.

- [ ] design system compartilhado e tokens responsivos;
- [ ] separar “projeção”, “observação”, “recomendação” e “aposta registrada”;
- [ ] onboarding, glossário e mensagens de risco;
- [ ] recomendação em um cartão: seleção, odd mínima, validade, confiança,
  incerteza, stake máximo e explicação;
- [ ] busca, filtros e estados vazios consistentes;
- [ ] histórico pessoal com evolução da banca e decisões;
- [ ] acessibilidade WCAG 2.2 AA e navegação por teclado;
- [ ] E2E dos fluxos críticos em web e viewport mobile;
- [ ] performance, paginação e virtualização de listas grandes;
- [ ] feedback no produto com consentimento e sem dado sensível.

Gate: usuários de teste concluem busca → compreensão → registro sem ajuda e sem
erros P0/P1.

## G41 — Piloto local multiusuário

Objetivo: validar utilidade e isolamento antes de acesso externo.

- [ ] testes de autorização por objeto em todas as rotas pessoais;
- [ ] cadastro, login, logout, expiração, recuperação e revogação;
- [ ] exportação e exclusão dos dados do usuário;
- [ ] backup imediatamente antes do piloto;
- [ ] telemetria local de erros, sem credenciais ou conteúdo privado;
- [ ] roteiro de teste, formulário e triagem de feedback;
- [ ] piloto de 7–14 dias com grupo pequeno;
- [ ] correção de todos os P0/P1 e decisão formal de continuar.

Gate: zero vazamento entre usuários, restore demonstrado e aceite do piloto.

## G42 — Prontidão para operação externa

Objetivo: preparar publicação privada, sem executá-la automaticamente.

- [ ] decisão explícita do proprietário;
- [ ] threat model, gestão de segredos e revisão de dependências;
- [ ] PostgreSQL gerenciado, backups/PITR e migrations controladas;
- [ ] API e scheduler em runtime persistente; frontend em CDN quando aplicável;
- [ ] TLS, domínio, CORS, CSP, rate limit e proteção contra abuso;
- [ ] observabilidade, alertas, orçamento e limites de cota;
- [ ] staging isolado, teste de carga, desastre e rollback;
- [ ] privacidade, termos e jogo responsável revisados juridicamente;
- [ ] plano de incidentes e encerramento seguro do serviço.

Gate: checklist de produção aprovado e rollback ensaiado. Vercel isoladamente
não substitui backend, scheduler e PostgreSQL.

## G43 — Release v1.0 e evolução controlada

Objetivo: declarar maturidade apenas quando produto e evidência convergirem.

- [ ] cumprir a definição v1.0 da visão de produto;
- [ ] publicar model cards e release notes internas;
- [ ] definir SLO/SLA, suporte e cadence de releases;
- [ ] revisão mensal de dados/modelos e trimestral de risco;
- [ ] experimentos sempre versionados, reversíveis e em shadow primeiro;
- [ ] expansão de mercado/competição somente após os mesmos gates;
- [ ] revisão formal semestral da visão e deste roadmap.

## Painel semanal obrigatório

| Área | Indicadores |
|---|---|
| Operação | disponibilidade, atraso, duração, fila, erro e recuperação |
| Banco | tamanho, crescimento, backup, restore, conexões e queries lentas |
| Dados | cobertura, frescor, identidade, cota e incidentes por causa |
| Modelos | Brier, log loss, ECE, drift, amostra e ganho sobre baseline |
| Decisão | abstinência, executadas/shadow, CLV, ROI, yield e drawdown |
| Risco | exposição pendente, concentração, correlação e circuit breakers |
| Produto | tarefas concluídas, latência, erros, acessibilidade e feedback |
| Segurança | acessos negados, sessões, segredos e testes de isolamento |

## Governança

- uma fase só conclui com código, testes, documentação e evidência;
- implementação não significa validação e validação não significa produção;
- nenhuma regra é ajustada retroativamente dentro da mesma coorte;
- dados pessoais, bancos e segredos nunca entram no Git;
- resultados negativos permanecem visíveis;
- toda expansão exige rollback;
- este documento prevalece sobre roadmaps históricos.
