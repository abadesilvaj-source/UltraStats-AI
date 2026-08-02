# Roadmap 2026 — próximas etapas

Atualizado em: 2 de agosto de 2026.

Este é o plano vigente após a conclusão da fundação G1–G26 e da primeira
implementação operacional de ML temporal, ensembles reais e closing odds. O
aplicativo permanece local; publicação na internet não faz parte do escopo atual.

## Estado de partida

Decisão operacional de 2 de agosto de 2026: API-Football é a única fonte ativa
para novas coletas. Dados históricos das demais fontes são preservados para
auditoria e reprodutibilidade, mas não recebem novas observações.

- backend FastAPI, scheduler, PostgreSQL e frontends web/mobile saudáveis;
- autenticação e isolamento dos dados por usuário implementados;
- 14.305 partidas e 299.203 previsões na fotografia operacional de 1º de agosto;
- API-Football, The Odds API e fontes complementares configuráveis;
- Poisson e Elo em produção, com ML temporal condicionado à aprovação fora da amostra;
- ensembles champion/challenger reais para resultados e gols;
- 2.729 testes aprovados e 99% de cobertura na última validação integral.

Os números operacionais são fotografias do ambiente, não metas permanentes.

## Ordem de execução

| Fase | Prioridade | Horizonte sugerido | Resultado esperado |
|---|---:|---:|---|
| G27 — estabilização do pipeline | P0 | 1–2 semanas | ciclos curtos, concorrência controlada e observabilidade |
| G28 — qualidade e cobertura | P0 | 2–4 semanas | cobertura elegível ≥ 90% nas competições-alvo |
| G29 — validação científica | P0 | 3–6 semanas | modelos aprovados por evidência, não por cadastro |
| G30 — recomendação e risco | P1 | 5–8 semanas | recomendações seletivas e auditáveis |
| G31 — piloto local multiusuário | P1 | 7–10 semanas | feedback estruturado sem publicação externa |
| G32 — prontidão para hospedagem | P2 | somente sob nova decisão | implantação privada reversível e segura |

Os horizontes indicam sequência e esforço relativo. Não são promessas de data.

## G27 — Estabilização do pipeline operacional

Objetivo: impedir que coleta, treinamento e geração de previsões concorram por
uma única transação longa.

- [ ] separar coleta, promoção, treino e inferência em jobs idempotentes;
- [ ] adotar commits por lote e limites de tempo por etapa;
- [ ] criar trava de exclusão por tipo de job e evitar treinos duplicados;
- [ ] mover treino para fila própria, mantendo inferência com o último champion;
- [ ] registrar duração, filas, itens processados e motivo de degradação;
- [ ] criar retry com backoff para HTTP 429 e circuit breaker para HTTP 402;
- [ ] testar recuperação após encerramento no meio de cada etapa;
- [ ] manter o frontend disponível durante backfills e treinamentos.

### G27.1 — Manutenção segura de armazenamento

Objetivo: impedir esgotamento do disco virtual Docker sem perda ou alteração do
banco.

- [ ] medir semanalmente imagens, containers, cache e volumes separadamente;
- [ ] criar alertas em 75%, 85% e 90% do limite;
- [ ] produzir backup lógico com checksum antes de cada limpeza;
- [ ] validar o restore em banco temporário isolado;
- [ ] limpar somente cache de build e imagens comprovadamente não utilizadas;
- [ ] proibir `docker system prune --volumes`, `docker volume prune`,
  `docker compose down -v` e remoção manual de `PGDATA`;
- [ ] comparar contagens críticas e executar smoke tests depois da manutenção;
- [ ] documentar espaço recuperado e evidências da preservação do banco.

Critérios de aceite:

- volume PostgreSQL ativo permanece com o mesmo identificador;
- nenhuma contagem funcional diminui após a manutenção;
- backup possui checksum e teste de restore aprovado;
- todos os cinco serviços retornam saudáveis após a limpeza;
- cache recuperável é reduzido sem remover imagens em uso.

Runbook obrigatório:
[`../operations/docker-storage-maintenance.md`](../operations/docker-storage-maintenance.md).

Critérios de aceite:

- ciclo ao vivo não é bloqueado por treino ou refresh de odds;
- nenhuma transação operacional permanece aberta por mais de cinco minutos;
- reinício do scheduler não duplica forecasts, odds ou payloads;
- health check diferencia saudável, degradado e indisponível.

## G28 — Cobertura, odds e qualidade dos dados

Objetivo: elevar cobertura útil com dados reais, sem fabricar preenchimentos.

- [ ] definir lista explícita de competições-alvo e SLA por capacidade;
- [ ] medir denominadores de cobertura bruta e elegível por data/competição;
- [ ] ampliar backfill de estatísticas por lotes respeitando cotas;
- [ ] consolidar matching de partidas entre provedores de odds e fixtures;
- [ ] armazenar abertura, snapshots intermediários e closing odds;
- [ ] criar reconciliação para partidas sem estatística, odds ou identidade;
- [ ] priorizar automaticamente lacunas com maior impacto nos modelos;
- [ ] criar painel de erros por provedor, competição e causa.
- [x] restringir novas coletas à API-Football sem excluir histórico anterior;
- [x] rotacionar a janela futura de odds preservando o dia atual em cada ciclo;
- [x] alinhar cobertura elegível de odds à janela operacional de 14 dias;

Critérios de aceite:

- cobertura elegível de estatísticas ≥ 90% nas competições-alvo;
- cobertura bruta cresce de forma mensurável e com denominador documentado;
- ≥ 80% das partidas elegíveis com odds têm ao menos dois snapshots válidos;
- closing odds são marcadas antes da liquidação sempre que a fonte permitir;
- toda ausência relevante possui causa auditável.

## G29 — Validação científica e MLOps

Objetivo: promover modelos somente quando superarem baseline em dados futuros.

- [ ] versionar dataset, features, hiperparâmetros e checksum do conteúdo;
- [ ] executar walk-forward por competição, mercado e horizonte;
- [ ] comparar Poisson, Elo, ML e ensembles com log loss, Brier e calibração;
- [ ] definir amostra mínima e intervalo de confiança por segmento;
- [ ] automatizar champion/challenger e rollback de modelo;
- [ ] monitorar drift de features, probabilidades e resultado;
- [ ] calibrar pesos do ensemble fora da amostra;
- [ ] expandir ML apenas para mercados com dados suficientes;
- [ ] publicar model cards internas com limitações conhecidas.

Critérios de aceite:

- nenhum challenger é promovido sem ganho fora da amostra;
- treino, calibração e teste possuem cortes temporais reproduzíveis;
- inferência tem fallback determinístico para o baseline;
- métricas globais nunca ocultam segmentos com amostra insuficiente;
- cada forecast informa modelo, versão, corte e nível de evidência.

## G30 — Recomendações, banca e risco

Objetivo: transformar probabilidades calibradas em decisões conservadoras.

- [ ] usar odds atuais e closing line apenas quando realmente observadas;
- [ ] recalibrar limiares de EV, incerteza e abstinência por segmento;
- [ ] limitar exposição por partida, competição, mercado e correlação;
- [ ] validar Kelly fracionado com cenários de estresse;
- [ ] medir ROI, yield, drawdown e CLV somente em apostas liquidadas;
- [ ] separar recomendação, simulação e aposta registrada;
- [ ] explicar por que uma oportunidade foi recomendada ou recusada;
- [ ] reforçar limites e mensagens de jogo responsável.

Critérios de aceite:

- ausência de odds recentes sempre produz “Sem aposta”;
- recomendações não usam métricas financeiras sintéticas;
- exposição respeita integralmente o perfil do usuário;
- auditoria reconstrói a decisão com os dados disponíveis naquele instante.

## G31 — Piloto local multiusuário

Objetivo: permitir testes reais com amigos mantendo o sistema na máquina local.

- [ ] revisar isolamento de banca, apostas, favoritos e configurações por usuário;
- [ ] testar cadastro, login, logout, recuperação e expiração de sessão;
- [ ] adicionar consentimento, exclusão de conta e exportação dos próprios dados;
- [ ] criar coleta de feedback dentro do produto, sem dados sensíveis;
- [ ] executar testes de usabilidade web e mobile;
- [ ] definir backup antes do piloto e rotina de restauração;
- [ ] acompanhar erros e feedback por 7–14 dias.

Critérios de aceite:

- zero acesso cruzado entre usuários nos testes automatizados e exploratórios;
- nenhuma credencial ou chave aparece no frontend, logs ou repositório;
- backup e restauração são demonstrados antes do primeiro convidado;
- problemas P0/P1 do piloto são corrigidos antes de ampliar participantes.

Amigos fora da rede local só poderão acessar após uma decisão de hospedagem ou
VPN privada. Essa autorização não está ativa neste roadmap.

## G32 — Prontidão para hospedagem privada

Objetivo: preparar, sem executar, uma futura publicação segura.

- [ ] decidir arquitetura de frontend, API, banco, scheduler e armazenamento;
- [ ] substituir bancos locais por PostgreSQL gerenciado com backups;
- [ ] separar secrets de build e runtime;
- [ ] configurar domínio, TLS, CORS, rate limit e observabilidade;
- [ ] executar migrations e smoke tests em ambiente isolado;
- [ ] elaborar rollback e plano de resposta a incidentes;
- [ ] concluir revisão jurídica e de privacidade aplicável.

Gate de início: somente após autorização explícita do proprietário. Vercel
isoladamente não hospeda o scheduler e o PostgreSQL persistente desta arquitetura.

## G33 — Importância dos jogadores nas previsões ✅

Objetivo: transformar estatísticas individuais, escalações e desfalques em
evidência temporal auditável, preservando o modelo coletivo quando a cobertura
for insuficiente.

- [x] normalizar estatísticas individuais provenientes da API Football;
- [x] criar rating 0–100 sensível à posição, minutos, amostra e forma;
- [x] agregar força da escalação provável ou confirmada;
- [x] ponderar ausências pela importância observada do atleta;
- [x] materializar `player_impact_v1` no feature store temporal;
- [x] aplicar cobertura mínima e teto configurável de ajuste do xG;
- [x] preservar fallback determinístico para o pipeline anterior;
- [x] incluir cobertura individual no nível de evidência e confiança;
- [x] registrar fatores individuais nas explicações dos forecasts;
- [x] automatizar a atualização dentro do ciclo operacional existente;
- [x] adicionar testes de regressão, escalação confirmada e falta de identidade.

Critérios de aceite:

- nenhuma observação posterior ao cutoff participa da previsão;
- cobertura abaixo de 45% não altera o xG;
- ajuste individual absoluto não ultrapassa 0,12 xG por equipe por padrão;
- desligar `PLAYER_IMPACT_ENABLED` restaura o comportamento coletivo;
- competições sem estatísticas individuais continuam operando normalmente;
- cada snapshot informa cutoff, fontes e versão da política;
- novos pesos continuam subordinados ao gate temporal G29.

## Indicadores semanais

| Área | Indicador |
|---|---|
| Operação | duração e taxa de sucesso por job |
| Dados | cobertura bruta/elegível e idade do dado |
| Odds | partidas com snapshots, casas e closing odds |
| Modelos | log loss, Brier, ECE, drift e taxa de aprovação |
| Recomendação | abstinência, EV observado e exposição |
| Produto | usuários ativos, erros e feedback resolvido |
| Segurança | tentativas bloqueadas, sessões e acessos cruzados |

## Regras de governança

- dados ausentes nunca são inventados para atingir uma meta;
- cobertura não representa acurácia;
- acurácia isolada não autoriza recomendação;
- mudanças de modelo exigem validação temporal e caminho de rollback;
- credenciais, bancos e dados pessoais não são enviados ao Git;
- hospedagem permanece pausada até nova autorização explícita;
- cada fase atualiza código, testes, runbook, changelog e este roadmap.
